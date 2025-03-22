from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from rest_framework.test import APIClient
from rest_framework import status
import os
import shutil
import tempfile
import json

from .models import Book, Chapter, ChapterSummary

class SummarizeAPITests(TestCase):
    """Tests for the Chapter Summarize API endpoint"""
    
    def setUp(self):
        """Set up test data before each test"""
        # Create a temporary media directory for test files
        self.temp_media = tempfile.mkdtemp()
        settings.MEDIA_ROOT = self.temp_media
        
        # Create test users
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpassword'
        )
        
        # Create API client
        self.client = APIClient()
        
        # Create a test book with a chapter
        self.book = Book.objects.create(
            title="Test Book",
            owner=self.user,
            total_pages=100,
            total_chapters=1
        )
        
        # Create a test chapter
        self.chapter = Chapter.objects.create(
            book=self.book,
            chapter_number="1",
            title="Test Chapter",
            text="This is a test chapter content that needs to be summarized. " * 10,  # Repeat text for longer content
            start_page=1,
            end_page=10,
            page_count=10,
            word_count=100
        )
        
        # Base URL for summarize endpoint
        self.summarize_url = f'/api/chapters/book/{self.book.id}/chapter/{self.chapter.chapter_number}/summarize/'
    
    def tearDown(self):
        """Clean up test files after each test"""
        # Remove the temporary media directory
        shutil.rmtree(self.temp_media, ignore_errors=True)
    
    def test_summarize_authenticated_owner(self):
        """Test summarizing a chapter when authenticated as the book owner"""
        # Login the user
        self.client.force_authenticate(user=self.user)
        
        # Make POST request to summarize endpoint
        response = self.client.post(self.summarize_url)
        
        # Check if summarization was successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify response structure
        self.assertIn('summary_text', response.data)
        self.assertIn('compression_ratio', response.data)
        self.assertIn('prompt_used', response.data)
        
        # Verify summary was created in database
        self.assertTrue(ChapterSummary.objects.filter(chapter=self.chapter).exists())
        
        # Verify the chapter's active_summary was set
        self.chapter.refresh_from_db()
        self.assertIsNotNone(self.chapter.active_summary)
    
    def test_summarize_with_custom_prompt(self):
        """Test summarizing a chapter with a custom prompt"""
        self.client.force_authenticate(user=self.user)
        
        custom_prompt = "Create a brief summary of the following text:"
        data = {'custom_prompt': custom_prompt}
        
        response = self.client.post(self.summarize_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(custom_prompt, response.data['prompt_used'])
    
    def test_summarize_unauthenticated(self):
        """Test that unauthenticated users cannot summarize chapters"""
        response = self.client.post(self.summarize_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_summarize_wrong_owner(self):
        """Test that non-owners cannot summarize chapters"""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.post(self.summarize_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_summarize_nonexistent_book(self):
        """Test summarizing a chapter from a nonexistent book"""
        self.client.force_authenticate(user=self.user)
        url = f'/api/chapters/book/99999/chapter/{self.chapter.chapter_number}/summarize/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_summarize_nonexistent_chapter(self):
        """Test summarizing a nonexistent chapter"""
        self.client.force_authenticate(user=self.user)
        url = f'/api/chapters/book/{self.book.id}/chapter/99999/summarize/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_multiple_summaries_same_chapter(self):
        """Test creating multiple summaries for the same chapter"""
        self.client.force_authenticate(user=self.user)
        
        # Create first summary
        response1 = self.client.post(self.summarize_url)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # Create second summary
        response2 = self.client.post(self.summarize_url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        
        # Verify both summaries exist and are different
        summaries = ChapterSummary.objects.filter(chapter=self.chapter)
        self.assertEqual(summaries.count(), 2)
        self.assertNotEqual(summaries[0].summary_text, summaries[1].summary_text)
        
        # Verify the latest summary is set as active
        self.chapter.refresh_from_db()
        self.assertEqual(self.chapter.active_summary, summaries.latest('created_at')) 