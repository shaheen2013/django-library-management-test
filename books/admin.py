from django.contrib import admin
from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """
    Admin interface for Book model.
    """
    list_display = (
        'title', 'author', 'isbn', 'category', 
        'total_copies', 'available_copies', 'is_available', 'created_at'
    )
    list_filter = ('category', 'language', 'publication_date', 'created_at')
    search_fields = ('title', 'author', 'isbn', 'description')
    ordering = ('title',)
    readonly_fields = ('created_at', 'updated_at', 'is_available', 'borrowed_copies')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'author', 'isbn', 'publisher', 'publication_date')
        }),
        ('Details', {
            'fields': ('page_count', 'language', 'description', 'cover_image')
        }),
        ('Availability', {
            'fields': ('total_copies', 'available_copies', 'is_available', 'borrowed_copies')
        }),
        ('Classification', {
            'fields': ('category', 'shelf_location')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Make certain fields readonly when editing"""
        readonly = list(self.readonly_fields)
        if obj:  # Editing existing object
            readonly.extend(['isbn'])
        return readonly
