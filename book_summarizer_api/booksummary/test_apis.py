from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from rest_framework.test import APIClient
from rest_framework import status
import os
import shutil
import tempfile

from .models import Book


class BookAPITests(TestCase):
    """Tests for the Book API endpoints"""
    
    def setUp(self):
        """Set up test data before each test"""
        # Create a temporary media directory for test files
        self.temp_media = tempfile.mkdtemp()
        settings.MEDIA_ROOT = self.temp_media
        
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create API client
        self.client = APIClient()
        
        # URL for book API - using the correct ViewSet name from router
        self.books_url = '/api/books/'  # Use direct URL instead of reverse() to avoid router name issues
        
        # Create a small test PDF file (as SimpleUploadedFile)
        self.test_pdf_content = (
            b'%PDF-1.4\n'
            b'1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n'
            b'2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n'
            b'3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\n'
            b'xref\n0 4\n0000000000 65535 f\n0000000010 00000 n\n0000000053 00000 n\n0000000102 00000 n\n'
            b'trailer<</Size 4/Root 1 0 R>>\n'
            b'startxref\n176\n%%EOF\n'
        )
        self.test_pdf = SimpleUploadedFile(
            name='test_book.pdf',
            content=self.test_pdf_content,
            content_type='application/pdf'
        )
    
    def tearDown(self):
        """Clean up test files after each test"""
        # Remove the temporary media directory
        shutil.rmtree(self.temp_media, ignore_errors=True)
    
    def test_create_book_authenticated(self):
        """Test creating a book when authenticated works"""
        # Login the user
        self.client.force_authenticate(user=self.user)
        
        # Prepare book data
        data = {
            'title': 'Test Book Title',
            'pdf_file': self.test_pdf
        }
        
        # Make POST request
        response = self.client.post(self.books_url, data, format='multipart')
        
        # Print response content if status code is not what we expect
        if response.status_code != status.HTTP_201_CREATED:
            print(f"\nResponse status: {response.status_code}")
            print("Response content:", response.content.decode())
        
        # Check if creation was successful
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check if book was actually created in DB
        books = Book.objects.all()
        self.assertEqual(books.count(), 1)
        
        # Check if book title matches
        self.assertEqual(books.first().title, 'Test Book Title')
        
        # Check if book has owner
        self.assertEqual(books.first().owner, self.user)
        
        # Check if file was saved
        book = books.first()
        self.assertTrue(book.pdf_file)
        self.assertTrue(os.path.exists(book.pdf_file.path))
    
    def test_create_book_unauthenticated(self):
        """Test creating a book fails when not authenticated"""
        # Prepare book data
        data = {
            'title': 'Test Book Title',
            'pdf_file': self.test_pdf
        }
        
        # Make POST request without authentication
        response = self.client.post(self.books_url, data, format='multipart')
        
        # Check that creation fails with 401 Unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Verify no book was created
        self.assertEqual(Book.objects.count(), 0)
    
    def test_list_books(self):
        """Test that authenticated users can list their books"""
        # Login the user
        self.client.force_authenticate(user=self.user)
        
        # Create a test PDF file for the book
        test_pdf = SimpleUploadedFile(
            name='user_book.pdf',
            content=self.test_pdf_content,
            content_type='application/pdf'
        )
        
        # Create a book for this user
        Book.objects.create(
            title="User's Book",
            pdf_file=test_pdf,
            owner=self.user
        )
        
        # Create a book for another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpassword'
        )
        
        other_pdf = SimpleUploadedFile(
            name='other_book.pdf',
            content=self.test_pdf_content,
            content_type='application/pdf'
        )
        
        Book.objects.create(
            title="Other User's Book",
            pdf_file=other_pdf,
            owner=other_user
        )
        
        # Get list of books
        response = self.client.get(self.books_url)
        
        # Check response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that only this user's book is returned
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "User's Book") 