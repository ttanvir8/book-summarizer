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
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Chapter
        fields = (
            'id', 'title', 'chapter_number', 'text', 'start_page', 'end_page', 
            'page_count', 'word_count', 'level', 'parent', 'summaries', 
            'active_summary', 'children'
        )
        read_only_fields = (
            'book', 'summary', 'page_count', 'word_count', 'compression_ratio', 
            'summaries', 'active_summary', 'children'
        )
    
    def get_children(self, obj):
        # Get direct children of this chapter
        children = Chapter.objects.filter(parent=obj).order_by('chapter_number')
        
        # Use self serializer for nested children
        serializer = ChapterSerializer(children, many=True, context=self.context)
        return serializer.data

# Flat chapter serializer for list views that doesn't include nested children
class FlatChapterSerializer(serializers.ModelSerializer):
    active_summary = ChapterSummarySerializer(read_only=True)
    parent_title = serializers.SerializerMethodField()
    
    class Meta:
        model = Chapter
        fields = (
            'id', 'title', 'chapter_number', 'start_page', 'end_page', 
            'page_count', 'word_count', 'level', 'parent', 'parent_title',
            'active_summary'
        )
    
    def get_parent_title(self, obj):
        if obj.parent:
            return obj.parent.title
        return None

class BookSerializer(serializers.ModelSerializer):
    chapters = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = '__all__' # or specify fields like ('id', 'title', 'pdf_file', ...)
        read_only_fields = ('processed_date', 'total_pages', 'total_chapters', 'chapters') # Fields generated automatically
    
    def get_chapters(self, obj):
        # Only get top-level chapters (those without a parent)
        if not obj.pk:  # If the Book doesn't have a primary key yet, return empty list
            return []
            
        top_level_chapters = obj.chapters.filter(parent__isnull=True).order_by('chapter_number')
        serializer = ChapterSerializer(top_level_chapters, many=True, context=self.context)
        return serializer.data

# Serializer for flat book representation (without nested chapters)
class BookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ('id', 'title', 'processed_date', 'total_pages', 'total_chapters', 'owner')
        read_only_fields = ('processed_date', 'total_pages', 'total_chapters')