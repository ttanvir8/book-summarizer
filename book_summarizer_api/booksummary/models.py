from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Book(models.Model):
    title = models.CharField(max_length=255)
    pdf_file = models.FileField(upload_to='book_pdfs/') # Store PDF file, adjust storage as needed
    processed_date = models.DateTimeField(default=timezone.now)
    total_pages = models.IntegerField(null=True, blank=True)
    total_chapters = models.IntegerField(null=True, blank=True)
    owner = models.ForeignKey(User, related_name='books', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.title

class Chapter(models.Model):
    book = models.ForeignKey(Book, related_name='chapters', on_delete=models.CASCADE)
    chapter_number = models.CharField(max_length=50)  # Changed from IntegerField to support hierarchical numbers like '1.1', '1.2'
    title = models.CharField(max_length=255)
    text = models.TextField()
    summary = models.TextField(blank=True, null=True) # Legacy field for backward compatibility
    start_page = models.IntegerField()
    end_page = models.IntegerField()
    page_count = models.IntegerField()
    word_count = models.IntegerField()
    compression_ratio = models.FloatField(null=True, blank=True)  # Legacy field for backward compatibility
    active_summary = models.ForeignKey('ChapterSummary', null=True, blank=True, on_delete=models.SET_NULL, related_name='active_for_chapters')
    level = models.IntegerField(default=0)  # Nesting level (0 for top-level chapters)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')  # Parent chapter reference

    def __str__(self):
        return f"Chapter {self.chapter_number}: {self.title} (Book: {self.book.title})"

class ChapterSummary(models.Model):
    chapter = models.ForeignKey(Chapter, related_name='summaries', on_delete=models.CASCADE)
    summary_text = models.TextField()
    prompt_used = models.TextField()
    compression_ratio = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Chapter summaries"
    
    def __str__(self):
        return f"Summary for Chapter {self.chapter.chapter_number} (Created: {self.created_at.strftime('%Y-%m-%d %H:%M')})"
