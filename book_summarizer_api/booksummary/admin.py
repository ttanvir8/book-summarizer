from django.contrib import admin
from django.utils.html import format_html
from .models import Book, Chapter, ChapterSummary


class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 0
    fields = ('chapter_number', 'title', 'level', 'parent', 'start_page', 'end_page', 'page_count', 'word_count')
    readonly_fields = ('word_count', 'page_count')
    show_change_link = True
    can_delete = False
    max_num = 0
    
    def get_queryset(self, request):
        # Only show top-level chapters in the book admin view
        qs = super().get_queryset(request)
        return qs.filter(parent__isnull=True)


class ChapterSummaryInline(admin.TabularInline):
    model = ChapterSummary
    extra = 0
    fields = ('summary_text', 'compression_ratio', 'created_at')
    readonly_fields = ('compression_ratio', 'created_at')
    show_change_link = True
    max_num = 0


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'processed_date', 'total_pages', 'total_chapters', 'view_pdf_link')
    list_filter = ('processed_date', 'owner')
    search_fields = ('title', 'owner__username')
    readonly_fields = ('processed_date', 'total_pages', 'total_chapters', 'owner')
    date_hierarchy = 'processed_date'
    inlines = [ChapterInline]
    
    def view_pdf_link(self, obj):
        if obj.pdf_file:
            return format_html('<a href="{}" target="_blank">View PDF</a>', obj.pdf_file.url)
        return "No PDF"
    view_pdf_link.short_description = 'PDF'


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('indented_title', 'book', 'chapter_number', 'level', 'parent', 'start_page', 'end_page', 'page_count', 'word_count', 'has_summary')
    list_filter = ('book', 'level')
    search_fields = ('title', 'book__title')
    readonly_fields = ('book', 'chapter_number', 'page_count', 'word_count')
    inlines = [ChapterSummaryInline]
    actions = ['generate_summary', 'regenerate_summary']
    list_select_related = ('book', 'parent', 'active_summary')
    list_display_links = ('indented_title',)
    
    def indented_title(self, obj):
        """Display indented title to represent hierarchy"""
        indent = '&nbsp;&nbsp;&nbsp;&nbsp;' * obj.level
        return format_html('{}{} {}', indent, obj.chapter_number, obj.title)
    indented_title.short_description = 'Chapter Title'
    indented_title.admin_order_field = 'title'
    
    def has_summary(self, obj):
        return obj.active_summary is not None
    has_summary.boolean = True
    has_summary.short_description = 'Has Summary'
    
    def get_queryset(self, request):
        # Order by book and then by chapter_number
        return super().get_queryset(request).order_by('book', 'chapter_number')
    
    def generate_summary(self, request, queryset):
        """
        Generate summary for selected chapters
        """
        from .views import generate_chapter_summary
        success_count = 0
        error_count = 0
        
        for chapter in queryset:
            try:
                # Generate summary
                summary_text, compression_ratio, prompt_used = generate_chapter_summary(chapter.text)
                
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
                
                success_count += 1
            except Exception as e:
                self.message_user(request, f"Error generating summary for chapter {chapter.title}: {str(e)}", level='ERROR')
                error_count += 1
        
        if success_count > 0:
            self.message_user(request, f"Successfully generated summaries for {success_count} chapters")
        if error_count > 0:
            self.message_user(request, f"Failed to generate summaries for {error_count} chapters", level='WARNING')
    generate_summary.short_description = "Generate summary for selected chapters"
    
    def regenerate_summary(self, request, queryset):
        """
        Regenerate summary with alternative prompt for selected chapters
        """
        from .views import generate_chapter_summary
        success_count = 0
        error_count = 0
        
        # Define an alternative prompt for admin regeneration
        admin_alternative_prompt = "Create a concise executive summary of the following text. Focus on key insights, main arguments, and significant conclusions."
        
        for chapter in queryset:
            try:
                # Generate summary with alternative prompt
                summary_text, compression_ratio, prompt_used = generate_chapter_summary(chapter.text, admin_alternative_prompt)
                
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
                
                success_count += 1
            except Exception as e:
                self.message_user(request, f"Error regenerating summary for chapter {chapter.title}: {str(e)}", level='ERROR')
                error_count += 1
        
        if success_count > 0:
            self.message_user(request, f"Successfully regenerated summaries for {success_count} chapters")
        if error_count > 0:
            self.message_user(request, f"Failed to regenerate summaries for {error_count} chapters", level='WARNING')
    regenerate_summary.short_description = "Regenerate summary with alternative prompt"
    
    # Filtering to show chapters hierarchically
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parent" and request.resolver_match.kwargs.get('object_id'):
            chapter_id = request.resolver_match.kwargs.get('object_id')
            chapter = Chapter.objects.get(id=chapter_id)
            kwargs["queryset"] = Chapter.objects.filter(book=chapter.book).exclude(id=chapter_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(ChapterSummary)
class ChapterSummaryAdmin(admin.ModelAdmin):
    list_display = ('chapter', 'compression_ratio', 'created_at', 'is_active')
    list_filter = ('created_at', 'chapter__book')
    search_fields = ('chapter__title', 'chapter__book__title')
    readonly_fields = ('created_at', 'compression_ratio', 'chapter')
    date_hierarchy = 'created_at'
    fields = ('chapter', 'summary_text', 'prompt_used', 'compression_ratio', 'created_at')
    actions = ['set_as_active_summary']
    
    def is_active(self, obj):
        if obj.chapter.active_summary and obj.chapter.active_summary.id == obj.id:
            return True
        return False
    is_active.boolean = True
    is_active.short_description = 'Active'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('chapter', 'chapter__active_summary')
    
    def set_as_active_summary(self, request, queryset):
        """
        Set selected summaries as active for their respective chapters
        """
        success_count = 0
        error_count = 0
        
        for summary in queryset:
            try:
                # Set as active summary for its chapter
                chapter = summary.chapter
                chapter.active_summary = summary
                chapter.save()
                
                success_count += 1
            except Exception as e:
                self.message_user(request, f"Error setting summary as active: {str(e)}", level='ERROR')
                error_count += 1
        
        if success_count > 0:
            self.message_user(request, f"Successfully set {success_count} summaries as active")
        if error_count > 0:
            self.message_user(request, f"Failed to set {error_count} summaries as active", level='WARNING')
    set_as_active_summary.short_description = "Set selected summaries as active"
