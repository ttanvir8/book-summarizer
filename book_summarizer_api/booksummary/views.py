from django.shortcuts import render, redirect
from django.conf import settings
import os

# Create your views here.


# book_summarizer_api/booksummary/views.py

from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from .models import Book, Chapter, ChapterSummary
from .serializers import (
    BookSerializer, BookListSerializer, 
    ChapterSerializer, FlatChapterSerializer, 
    ChapterSummarySerializer
)
from rest_framework import viewsets, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

# Import logic functions from run.py (modularize them later)
import pypdf
import re
import json
from datetime import datetime

# book_summarizer_api/booksummary/views.py

# ... (other imports)
import google.generativeai as genai
from .nested_bookmarks import process_pdf_chapters, normalize_text, extract_text_from_page_range

# Initialize Gemini API (replace with your actual API key)
genai.configure(api_key="AIzaSyDKvBScKmEk9Hhac8gnILDFHaRDNes-3UY") # Make sure to replace YOUR_API_KEY
model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp") # Or "gemini-1.5-pro", "gemini-1.5-flash" or other model you prefer

prompt3 = f"""Create a detailed summary of the following chapter that adheres to these principles:

Relevant: Give me all the main arguments, analogies, processes, tools, examples, and supporting evidence from the source. Prioritize ideas central to the author's thesis. And make it detailed engough so that each arguments are discussed in enough comprehensive details.

Concise: Avoid repetition, redundancy, and filler. Present ideas in a densely informative way (e.g., explain an analogy once with clarity, not multiple times). But, Give each argument's main paragraph enough details to get the point across.

Coherent: Structure the summary logically (e.g., mirror the chapter's flow or group related arguments). Use transitions to show connections between ideas. Make it readable and have logical flow of sentence.

Faithful: Do not add, interpret, or omit content. Preserve the author's tone, emphasis, and proportional focus (e.g., if the author spends 30% of the chapter on a process, reflect that weighting).

Avoid:
Paraphrasing that loses nuance (e.g., oversimplifying a multi-step process).
Listing disconnected facts without contextualizing their role in the argument.

Structure:
Make logical sections for each reasonable sections of the summary and use bold and italic formatting of text to emphasis important parts for better understandability and readability.

Text:
"""

# Alternative prompt for a different style of summary
prompt_concise = f"""Create a concise summary of the following chapter that covers only the most essential points:

Focus on:
- The core argument or thesis
- Key supporting evidence
- Main conclusions

Use simple language and short paragraphs.
Limit to about 1/5 the length of the original text.

Text:
"""


def generate_chapter_summary(chapter_text, prompt_template=None):
    """Generates a summary for a given chapter text using Gemini API and calculates compression ratio."""
    try:
        # Use the provided prompt template or default to prompt3
        prompt_to_use = prompt_template or prompt3
        prompt = f'{prompt_to_use} {chapter_text}'
        
        # Count tokens in the original text
        original_tokens = model.count_tokens(chapter_text).total_tokens
        
        # Generate the summary
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.4,
                "top_p": 0.95,
                "top_k": 64,
            }
        )
        summary_text = response.text
        
        # Count tokens in the summary
        summary_tokens = model.count_tokens(summary_text).total_tokens
        
        # Calculate compression ratio (if summary_tokens is 0, default to 0 to avoid division by zero)
        compression_ratio = 0 if summary_tokens == 0 else summary_tokens / original_tokens
        
        return summary_text, compression_ratio, prompt_to_use
    except Exception as e:
        print(f"Error generating summary: {str(e)}")
        return "Error generating summary", None, prompt_to_use # Or handle error as needed



#### text cleaning
def normalize_text(raw_text):
    # Replace tabs and multiple newlines with a single space
    text = re.sub(r'[\t\n]+', ' ', raw_text)

    # Remove extra spaces
    text = ' '.join(text.split())

    # Add line breaks after periods, exclamation marks, and question marks
    text = re.sub(r'(?<=[.!?]) +', '\n', text)

    # Capitalize the first letter of each sentence
    sentences = text.split('\n')
    sentences = [sentence.strip().capitalize() for sentence in sentences]

    # Join sentences back into a single string
    normalized_text = '\n'.join(sentences)

    # Handle common abbreviations and contractions
    normalized_text = re.sub(r"\bi'm\b", "I'm", normalized_text)
    normalized_text = re.sub(r"\bcan't\b", "cannot", normalized_text)
    normalized_text = re.sub(r"\bwon't\b", "will not", normalized_text)
    normalized_text = re.sub(r"\b(\w+)'ll\b", r"\1 will", normalized_text)
    normalized_text = re.sub(r"\b(\w+)'ve\b", r"\1 have", normalized_text)
    normalized_text = re.sub(r"\b(\w+)'re\b", r"\1 are", normalized_text)
    normalized_text = re.sub(r"\b(\w+)'d\b", r"\1 would", normalized_text)
    normalized_text = re.sub(r"\b(\w+)'s\b", r"\1 is", normalized_text)

    return normalized_text


def get_text_from_bookmark_to_bookmark(reader, pages, bookmark1, bookmark2):
    page_number1 = reader.get_destination_page_number(bookmark1)
    page_number2 = reader.get_destination_page_number(bookmark2)

    start = min(page_number1, page_number2)
    end = max(page_number1, page_number2)

    text = ""
    start_page_number = min(page_number1, page_number2)
    for page in pages[start:end]:
        # Add page number with clear formatting
        text += f"\n( Page {start_page_number + 1} )\n\n"
        # Extract text from the current page
        text += normalize_text(page.extract_text())
        # Add spacing after page
        text += "\n\n"
        start_page_number += 1
    return text


def process_pdf_chapters_logic(pdf_file):
    """Processes PDF chapters and returns structured data with nested bookmarks."""
    try:
        reader = pypdf.PdfReader(pdf_file)
        # Use lower memory settings for PdfReader if available
        if hasattr(reader, 'strict'):
            reader.strict = False

        # Use the nested_bookmarks processing function
        document_metadata = process_pdf_chapters(reader)
        
        if not document_metadata:
            # Fallback to non-nested processing if nested processing fails
            print("Nested bookmark processing failed, falling back to flat processing")
            return process_pdf_chapters_flat(pdf_file)
            
        return document_metadata
    except MemoryError:
        print("Memory error encountered - try processing a smaller PDF file")
        raise
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        raise


def process_pdf_chapters_flat(pdf_file):
    """Legacy function for processing PDF chapters without nested structure."""
    reader = pypdf.PdfReader(pdf_file)
    pages = reader.pages
    bookmarks = reader.outline

    document_metadata = {
        "document_info": {
            "total_chapters": len(bookmarks) - 1 if bookmarks else 0,
            "total_pages": len(pages),
            "processed_date": datetime.now().isoformat(),
        },
        "chapters": []
    }

    if bookmarks:
        for i in range(len(bookmarks) - 1):
            try:
                start_page = reader.get_destination_page_number(bookmarks[i])
                end_page = reader.get_destination_page_number(bookmarks[i+1])

                chapter_text = get_text_from_bookmark_to_bookmark(reader, pages, bookmarks[i], bookmarks[i+1])

                chapter_data = {
                    "chapter_number": i + 1,
                    "title": bookmarks[i].title,
                    "text": chapter_text,
                    "metadata": {
                        "start_page": start_page + 1,
                        "end_page": end_page,
                        "page_count": end_page - start_page,
                        "word_count": len(chapter_text.split())
                    }
                }
                document_metadata["chapters"].append(chapter_data)

            except Exception as e:
                print(f"Error processing chapter {i + 1}: {str(e)}")

    return document_metadata


# Define permission classes
class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request, so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the book
        if hasattr(obj, 'owner'):  # For Book model
            return obj.owner == request.user
        elif hasattr(obj, 'book'):  # For Chapter model
            return obj.book.owner == request.user
        return False

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

class IsBookOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a book to access its chapters and summaries.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Check if book_pk is in the URL kwargs
        book_pk = view.kwargs.get('book_pk')
        if book_pk:
            try:
                book = Book.objects.get(pk=book_pk)
                return book.owner == request.user
            except Book.DoesNotExist:
                # Return True to let the view handle the 404
                return True
        
        # For chapter-specific actions
        chapter_id = view.kwargs.get('chapter_id')
        if chapter_id:
            try:
                chapter = Chapter.objects.get(pk=chapter_id)
                return chapter.book.owner == request.user
            except Chapter.DoesNotExist:
                # Return True to let the view handle the 404
                return True
                
        return True  # Default to allowing permission if no specific book/chapter is being accessed

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    permission_classes = [IsOwnerOrReadOnly]
    parser_classes = (MultiPartParser, FormParser) # To handle file uploads
    
    def get_serializer_class(self):
        """Return different serializers for list and detail views"""
        if self.action == 'list':
            return BookListSerializer
        return BookSerializer
    
    def get_queryset(self):
        """
        This view should return a list of all books
        for the currently authenticated user.
        """
        user = self.request.user
        if user.is_authenticated:
            return Book.objects.filter(owner=user)
        return Book.objects.none()
    
    def create(self, request, *args, **kwargs):
        # Check file size before processing
        max_size = getattr(settings, 'MAX_FILE_SIZE', 20 * 1024 * 1024)  # Default 20MB
        
        pdf_file = request.FILES.get('pdf_file')
        if pdf_file and pdf_file.size > max_size:
            return Response(
                {"error": f"File too large. Maximum size is {max_size/1024/1024:.1f}MB"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def perform_create(self, serializer):
        """Override perform_create to process uploaded PDF file and extract chapters."""
        # Create the book instance with owner = current user
        book_instance = serializer.save(owner=self.request.user)
        
        # Process the PDF and create chapters
        try:
            # Extract PDF file path
            pdf_file = book_instance.pdf_file.path
            
            # Process PDF to extract chapters with nested structure
            processed_data = process_pdf_chapters_logic(pdf_file)
            
            # Update book with metadata
            book_instance.total_pages = processed_data.get('document_info', {}).get('total_pages', 0)
            total_chapters = 0
            
            # Create chapter instances with recursion for nested chapters
            if 'chapters' in processed_data:
                chapter_number = 1
                for chapter_data in processed_data['chapters']:
                    self._create_chapter_recursive(book_instance, chapter_data, None, str(chapter_number))
                    chapter_number += 1
                    total_chapters += 1
                    # Count child chapters recursively
                    if 'children' in chapter_data:
                        total_chapters += self._count_children(chapter_data['children'])
            
            book_instance.total_chapters = total_chapters
            book_instance.save()
        except Exception as e:
            # On error, delete the book and return error
            book_instance.delete()
            raise Exception(f"Error processing PDF: {str(e)}")
            
    def _count_children(self, children):
        """Count the number of child chapters recursively"""
        count = len(children)
        for child in children:
            if 'children' in child:
                count += self._count_children(child['children'])
        return count
    
    def _create_chapter_recursive(self, book_instance, chapter_data, parent_chapter, chapter_number):
        """Recursively create chapter and its children"""
        # Create the chapter
        chapter = Chapter.objects.create(
            book=book_instance,
            chapter_number=chapter_number,  # Ensure chapter_number is stored as a string
            title=chapter_data.get('title', 'Untitled Chapter'),
            text=chapter_data.get('text', ''),
            start_page=chapter_data.get('start_page', 0),
            end_page=chapter_data.get('end_page', 0),
            page_count=chapter_data.get('page_count', 0),
            word_count=chapter_data.get('word_count', 0),
            level=chapter_data.get('level', 0),
            parent=parent_chapter
        )
        
        # Process children recursively
        if 'children' in chapter_data and chapter_data['children']:
            child_number = 1
            for child_data in chapter_data['children']:
                # Create hierarchical chapter number (e.g., 1.1, 1.2)
                child_chapter_number = f"{chapter_number}.{child_number}"
                self._create_chapter_recursive(book_instance, child_data, chapter, child_chapter_number)
                child_number += 1
        
        return chapter

class ChapterViewSet(viewsets.ModelViewSet):
    queryset = Chapter.objects.all()
    permission_classes = [IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'list':
            return FlatChapterSerializer
        return ChapterSerializer

    def get_queryset(self):
        queryset = Chapter.objects.all()
        
        # Filter by book if book parameter is provided
        book_id = self.request.query_params.get('book', None)
        if book_id is not None:
            queryset = queryset.filter(book_id=book_id)
        
        # Filter by owner
        if self.request.user.is_authenticated:
            queryset = queryset.filter(book__owner=self.request.user)
        
        return queryset.select_related('book', 'active_summary').prefetch_related('summaries')
    
    @action(detail=True, methods=['get'])
    def children(self, request, pk=None):
        """API endpoint to get direct children of a chapter"""
        chapter = self.get_object()
        children = Chapter.objects.filter(parent=chapter).order_by('chapter_number')
        serializer = ChapterSerializer(children, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path=r'book/(?P<book_pk>[0-9]+)/chapter/(?P<chapter_number>[\w.]+)/summarize',
            permission_classes=[IsBookOwner])
    def summarize(self, request, book_pk=None, chapter_number=None):
        """
        Generate a summary for a specific chapter of a book.
        """
        try:
            # Get the book first
            book = Book.objects.get(pk=book_pk)
            
            # After finding the book, check ownership
            if book.owner != request.user:
                return Response({"error": "You don't have permission to access this book"}, 
                              status=status.HTTP_403_FORBIDDEN)
                
            chapter = Chapter.objects.get(book=book, chapter_number=chapter_number)
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
        except Chapter.DoesNotExist:
            return Response({"error": "Chapter not found"}, status=status.HTTP_404_NOT_FOUND)
            
        try:
            # Get custom prompt if provided
            custom_prompt = request.data.get('custom_prompt', None)
            
            # Generate the summary
            summary_text, compression_ratio, prompt_used = generate_chapter_summary(chapter.text, custom_prompt)
            
            # Create a new ChapterSummary
            summary = ChapterSummary.objects.create(
                chapter=chapter,
                summary_text=summary_text,
                prompt_used=prompt_used,
                compression_ratio=compression_ratio
            )
            
            # Set this as the active summary
            chapter.active_summary = summary
            chapter.save()
            
            # Return the summary data
            serializer = ChapterSummarySerializer(summary)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {"error": f"Failed to generate summary: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path=r'book/(?P<book_pk>\d+)/chapter/(?P<chapter_number>[\w.]+)/regenerate-summary',
            permission_classes=[IsBookOwner])
    def regenerate_summary(self, request, book_pk=None, chapter_number=None):
        """
        Generate a new summary for a specific chapter using an alternative prompt.
        """
        try:
            # Get the book and verify ownership
            book = Book.objects.get(pk=book_pk)
            if book.owner != request.user:
                return Response({"error": "You don't have permission to access this book"}, 
                              status=status.HTTP_403_FORBIDDEN)
                
            chapter = Chapter.objects.get(book=book, chapter_number=chapter_number)
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
        except Chapter.DoesNotExist:
            return Response({"error": "Chapter not found"}, status=status.HTTP_404_NOT_FOUND)
            
        # Get custom prompt if provided
        custom_prompt = request.data.get('custom_prompt', None)
        
        # If no custom prompt, alternate between different prompt styles
        if not custom_prompt:
            # Check if the last summary used prompt3
            last_summary = chapter.summaries.first()
            if last_summary and prompt3 in last_summary.prompt_used:
                custom_prompt = prompt_concise
            else:
                custom_prompt = prompt3
        
        # Generate the summary
        summary_text, compression_ratio, prompt_used = generate_chapter_summary(chapter.text, custom_prompt)
        
        # Create a new ChapterSummary
        summary = ChapterSummary.objects.create(
            chapter=chapter,
            summary_text=summary_text,
            prompt_used=prompt_used,
            compression_ratio=compression_ratio
        )
        
        # Set this as the active summary
        chapter.active_summary = summary
        chapter.save()
        
        # Return the summary data
        serializer = ChapterSummarySerializer(summary)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path=r'(?P<chapter_id>[^/]+)/set-active-summary/(?P<summary_id>[^/]+)',
            permission_classes=[IsBookOwner])
    def set_active_summary(self, request, chapter_id=None, summary_id=None):
        """
        Set a specific summary as the active one for a chapter.
        """
        try:
            # Get the chapter and verify it's from a book owned by the user
            chapter = Chapter.objects.get(pk=chapter_id, book__owner=request.user)
            
            # Get the summary and verify it belongs to this chapter
            summary = ChapterSummary.objects.get(pk=summary_id, chapter=chapter)
            
            # Set as active summary
            chapter.active_summary = summary
            chapter.save()
            
            return Response({"status": "success", "message": "Active summary updated"}, 
                            status=status.HTTP_200_OK)
        except Chapter.DoesNotExist:
            return Response({"error": "Chapter not found or you don't have permission to access it"}, 
                           status=status.HTTP_404_NOT_FOUND)
        except ChapterSummary.DoesNotExist:
            return Response({"error": "Summary not found or doesn't belong to the specified chapter"}, 
                           status=status.HTTP_404_NOT_FOUND)

class ChapterSummaryViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing chapter summaries. No create/update/delete operations allowed."""
    serializer_class = ChapterSummarySerializer
    permission_classes = [IsOwnerOrReadOnly]
    
    def get_queryset(self):
        """
        Filter summaries to only show those belonging to chapters of books owned by the current user
        """
        user = self.request.user
        return ChapterSummary.objects.filter(chapter__book__owner=user)
    
    @action(detail=False, methods=['get'], url_path=r'chapter/(?P<chapter_id>[^/]+)',
            permission_classes=[IsBookOwner])
    def for_chapter(self, request, chapter_id=None):
        """
        Get all summaries for a specific chapter.
        """
        try:
            # Get the chapter and verify ownership
            chapter = Chapter.objects.get(pk=chapter_id)
            if chapter.book.owner != request.user:
                return Response({"error": "You don't have permission to access this chapter"}, 
                               status=status.HTTP_403_FORBIDDEN)
                
            # Get all summaries for this chapter, ordered by most recent first
            summaries = ChapterSummary.objects.filter(chapter=chapter).order_by('-created_at')
            
            serializer = ChapterSummarySerializer(summaries, many=True)
            return Response(serializer.data)
        except Chapter.DoesNotExist:
            return Response({"error": "Chapter not found"}, status=status.HTTP_404_NOT_FOUND)

def auth_callback(request):
    # Redirect to your frontend with the session token
    frontend_url = os.environ.get('FRONTEND_URL', 'https://knowledgeq-git-main-tanvirkkhans-projects.vercel.app/auth/callback')
    return redirect(frontend_url)