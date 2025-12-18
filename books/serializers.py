from rest_framework import serializers
from .models import Book


class BookSerializer(serializers.ModelSerializer):
    """Full serializer for Book model"""
    is_available = serializers.ReadOnlyField()
    borrowed_copies = serializers.ReadOnlyField()
    
    class Meta:
        model = Book
        fields = (
            'id', 'title', 'author', 'isbn', 'publisher', 'publication_date',
            'page_count', 'language', 'description', 'cover_image',
            'total_copies', 'available_copies', 'is_available', 'borrowed_copies',
            'category', 'shelf_location', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def validate_isbn(self, value):
        """Validate ISBN format"""
        # Remove any spaces or hyphens
        isbn = value.replace('-', '').replace(' ', '')
        
        if len(isbn) not in [10, 13]:
            raise serializers.ValidationError(
                "ISBN must be 10 or 13 characters long"
            )
        
        if not isbn.isdigit():
            raise serializers.ValidationError(
                "ISBN must contain only digits"
            )
        
        return isbn
    
    def validate(self, attrs):
        """Validate that available_copies doesn't exceed total_copies"""
        total = attrs.get('total_copies', self.instance.total_copies if self.instance else None)
        available = attrs.get('available_copies', self.instance.available_copies if self.instance else None)
        
        if total is not None and available is not None:
            if available > total:
                raise serializers.ValidationError(
                    "Available copies cannot exceed total copies"
                )
        
        return attrs


class BookListSerializer(serializers.ModelSerializer):
    """Minimal serializer for listing books"""
    is_available = serializers.ReadOnlyField()
    
    class Meta:
        model = Book
        fields = (
            'id', 'title', 'author', 'isbn', 'category',
            'available_copies', 'is_available'
        )
        read_only_fields = fields


class BookDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for book with loan information"""
    is_available = serializers.ReadOnlyField()
    borrowed_copies = serializers.ReadOnlyField()
    active_loans_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = (
            'id', 'title', 'author', 'isbn', 'publisher', 'publication_date',
            'page_count', 'language', 'description', 'cover_image',
            'total_copies', 'available_copies', 'is_available', 'borrowed_copies',
            'category', 'shelf_location', 'active_loans_count',
            'created_at', 'updated_at'
        )
        read_only_fields = fields
    
    def get_active_loans_count(self, obj):
        """Get count of active loans for this book"""
        return obj.loans.filter(returned_at__isnull=True).count()


