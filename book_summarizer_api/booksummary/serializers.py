# book_summarizer_api/booksummary/serializers.py

from rest_framework import serializers
from .models import Book, Chapter, ChapterSummary

class ChapterSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChapterSummary
        fields = ('id', 'summary_text', 'prompt_used', 'compression_ratio', 'created_at')
        read_only_fields = ('id', 'created_at')

class ChapterSerializer(serializers.ModelSerializer):
    summaries = ChapterSummarySerializer(many=True, read_only=True)
    active_summary = ChapterSummarySerializer(read_only=True)
    
    class Meta:
        model = Chapter
        fields = '__all__'  # Include all fields
        read_only_fields = ('book', 'summary', 'page_count', 'word_count', 'compression_ratio', 'summaries', 'active_summary')

class BookSerializer(serializers.ModelSerializer):
    chapters = ChapterSerializer(many=True, read_only=True) # Nested serializer for chapters

    class Meta:
        model = Book
        fields = '__all__' # or specify fields like ('id', 'title', 'pdf_file', ...)
        read_only_fields = ('processed_date', 'total_pages', 'total_chapters', 'chapters') # Fields generated automatically