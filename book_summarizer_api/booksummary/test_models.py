from django.test import TestCase
from django.contrib.auth.models import User
from .models import Book

class BookModelTest(TestCase):
    """Test the Book model"""
    
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
    
    def test_book_creation(self):
        """Test creating a book"""
        book = Book.objects.create(
            title="Test Book",
            pdf_file="path/to/test.pdf",
            owner=self.user
        )
        
        self.assertEqual(book.title, "Test Book")
        self.assertEqual(book.owner, self.user) 