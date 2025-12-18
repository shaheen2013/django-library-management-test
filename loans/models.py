from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class Loan(models.Model):
    """
    Loan model to track book borrowing.
    """
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='loans'
    )
    book = models.ForeignKey(
        'books.Book',
        on_delete=models.CASCADE,
        related_name='loans'
    )
    
    # Loan dates
    borrowed_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    returned_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active'
    )
    
    # Notes
    notes = models.TextField(blank=True, null=True)
    
    # Fine for overdue books
    fine_amount = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0.00,
        help_text="Fine amount for overdue returns"
    )
    fine_paid = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'loans'
        ordering = ['-borrowed_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['book', 'status']),
            models.Index(fields=['due_date']),
        ]
        
    def __str__(self):
        return f"{self.user.username} borrowed {self.book.title}"
    
    def save(self, *args, **kwargs):
        """Set due date automatically if not provided (14 days from borrow)"""
        if not self.pk and not self.due_date:
            self.due_date = timezone.now() + timedelta(days=14)
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        """Check if loan is overdue"""
        if self.returned_at or not self.due_date:
            return False
        return timezone.now() > self.due_date
    
    @property
    def days_overdue(self):
        """Calculate number of days overdue"""
        if not self.is_overdue:
            return 0
        return (timezone.now() - self.due_date).days
    
    def calculate_fine(self, daily_rate=0.50):
        """Calculate fine for overdue books"""
        if self.is_overdue:
            self.fine_amount = self.days_overdue * daily_rate
            self.status = 'overdue'
            self.save()
        return self.fine_amount
    
    def return_loan(self):
        """Mark loan as returned"""
        if not self.returned_at:
            self.returned_at = timezone.now()
            if self.is_overdue:
                self.calculate_fine()
                self.status = 'overdue'
            else:
                self.status = 'returned'
            self.save()
            self.book.return_book()
            return True
        return False
