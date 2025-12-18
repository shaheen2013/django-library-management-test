from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Book(models.Model):
    """
    Book model containing all book information.
    """
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True, help_text="13 Character ISBN")
    publisher = models.CharField(max_length=255, blank=True, null=True)
    publication_date = models.DateField(blank=True, null=True)
    page_count = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Number of pages in the book"
    )
    language = models.CharField(max_length=50, default='English')
    description = models.TextField(blank=True, null=True)
    cover_image = models.URLField(blank=True, null=True)
    
    # Availability tracking
    total_copies = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Total number of copies in library"
    )
    available_copies = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(0)],
        help_text="Number of copies available for borrowing"
    )
    
    # Categories and classification
    category = models.CharField(max_length=100, blank=True, null=True)
    shelf_location = models.CharField(max_length=50, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'books'
        ordering = ['title']
        indexes = [
            models.Index(fields=['isbn']),
            models.Index(fields=['title']),
            models.Index(fields=['author']),
            models.Index(fields=['category']),
        ]
        
    def __str__(self):
        return f"{self.title} by {self.author}"
    
    @property
    def is_available(self):
        """Check if book is available for borrowing"""
        return self.available_copies > 0
    
    @property
    def borrowed_copies(self):
        """Calculate number of currently borrowed copies"""
        return self.total_copies - self.available_copies
    
    def borrow(self):
        """Decrease available copies when book is borrowed"""
        if self.available_copies > 0:
            self.available_copies -= 1
            self.save()
            return True
        return False
    
    def return_book(self):
        """Increase available copies when book is returned"""
        if self.available_copies < self.total_copies:
            self.available_copies += 1
            self.save()
            return True
        return False
    
    def clean(self):
        """Validate that available_copies doesn't exceed total_copies"""
        from django.core.exceptions import ValidationError
        if self.available_copies > self.total_copies:
            raise ValidationError('Available copies cannot exceed total copies')
