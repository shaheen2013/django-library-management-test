from rest_framework import serializers
from .models import Loan
from books.serializers import BookListSerializer
from accounts.serializers import UserListSerializer


class LoanSerializer(serializers.ModelSerializer):
    """Full serializer for Loan model"""
    is_overdue = serializers.ReadOnlyField()
    days_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = Loan
        fields = (
            'id', 'user', 'book', 'borrowed_at', 'due_date', 'returned_at',
            'status', 'notes', 'fine_amount', 'fine_paid',
            'is_overdue', 'days_overdue'
        )
        read_only_fields = ('id', 'borrowed_at', 'status', 'fine_amount')
    
    def validate(self, attrs):
        """Validate loan creation"""
        book = attrs.get('book')
        user = attrs.get('user')
        
        # Check if book is available
        if book and not book.is_available:
            raise serializers.ValidationError(
                {"book": "This book is not available for borrowing"}
            )
        
        # Check if user already has this book on loan
        if user and book:
            existing_loan = Loan.objects.filter(
                user=user,
                book=book,
                returned_at__isnull=True
            ).exists()
            
            if existing_loan:
                raise serializers.ValidationError(
                    {"book": "You already have this book on loan"}
                )
        
        return attrs
    
    def create(self, validated_data):
        """Create loan and update book availability"""
        book = validated_data['book']
        loan = super().create(validated_data)
        book.borrow()
        return loan


class LoanDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for loan with nested user and book info"""
    user = UserListSerializer(read_only=True)
    book = BookListSerializer(read_only=True)
    is_overdue = serializers.ReadOnlyField()
    days_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = Loan
        fields = (
            'id', 'user', 'book', 'borrowed_at', 'due_date', 'returned_at',
            'status', 'notes', 'fine_amount', 'fine_paid',
            'is_overdue', 'days_overdue'
        )
        read_only_fields = fields


class LoanCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a loan"""
    
    class Meta:
        model = Loan
        fields = ('book', 'due_date', 'notes')
    
    def validate_book(self, value):
        """Check if book is available"""
        if not value.is_available:
            raise serializers.ValidationError(
                "This book is not available for borrowing"
            )
        return value
    
    def validate(self, attrs):
        """Validate that user doesn't already have this book"""
        user = self.context['request'].user
        book = attrs.get('book')
        
        existing_loan = Loan.objects.filter(
            user=user,
            book=book,
            returned_at__isnull=True
        ).exists()
        
        if existing_loan:
            raise serializers.ValidationError(
                {"book": "You already have this book on loan"}
            )
        
        return attrs
    
    def create(self, validated_data):
        """Create loan with authenticated user and update book availability"""
        validated_data['user'] = self.context['request'].user
        book = validated_data['book']
        loan = super().create(validated_data)
        book.borrow()
        return loan


class LoanReturnSerializer(serializers.Serializer):
    """Serializer for returning a book"""
    notes = serializers.CharField(required=False, allow_blank=True)


