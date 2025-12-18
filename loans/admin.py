from django.contrib import admin
from .models import Loan


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    """
    Admin interface for Loan model.
    """
    list_display = (
        'id', 'user', 'book', 'borrowed_at', 'due_date', 
        'returned_at', 'status', 'is_overdue', 'fine_amount', 'fine_paid'
    )
    list_filter = ('status', 'fine_paid', 'borrowed_at', 'due_date', 'returned_at')
    search_fields = ('user__username', 'user__email', 'book__title', 'book__isbn')
    ordering = ('-borrowed_at',)
    readonly_fields = ('borrowed_at', 'is_overdue', 'days_overdue')
    
    fieldsets = (
        ('Loan Information', {
            'fields': ('user', 'book', 'borrowed_at', 'due_date', 'returned_at')
        }),
        ('Status', {
            'fields': ('status', 'is_overdue', 'days_overdue')
        }),
        ('Fines', {
            'fields': ('fine_amount', 'fine_paid')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_returned', 'calculate_fines', 'mark_fines_paid']
    
    def mark_as_returned(self, request, queryset):
        """Mark selected loans as returned"""
        count = 0
        for loan in queryset:
            if loan.return_loan():
                count += 1
        self.message_user(request, f'{count} loan(s) marked as returned.')
    mark_as_returned.short_description = "Mark selected loans as returned"
    
    def calculate_fines(self, request, queryset):
        """Calculate fines for selected overdue loans"""
        count = 0
        for loan in queryset:
            if loan.is_overdue:
                loan.calculate_fine()
                count += 1
        self.message_user(request, f'Calculated fines for {count} overdue loan(s).')
    calculate_fines.short_description = "Calculate fines for overdue loans"
    
    def mark_fines_paid(self, request, queryset):
        """Mark fines as paid for selected loans"""
        count = queryset.update(fine_paid=True)
        self.message_user(request, f'Marked {count} fine(s) as paid.')
    mark_fines_paid.short_description = "Mark fines as paid"
