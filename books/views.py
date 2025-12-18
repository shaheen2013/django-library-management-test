from rest_framework import generics, permissions, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Book
from .serializers import BookSerializer, BookListSerializer, BookDetailSerializer
from accounts.permissions import IsAdminUser


class BookListView(generics.ListAPIView):
    """
    API endpoint to list all books.
    Supports filtering, searching, and pagination.
    Anonymous users can view.
    """
    queryset = Book.objects.all()
    serializer_class = BookListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'author', 'language']
    search_fields = ['title', 'author', 'isbn', 'description']
    ordering_fields = ['title', 'author', 'publication_date', 'created_at']
    ordering = ['title']
    
    def get_queryset(self):
        """
        Optionally filter by availability.
        """
        queryset = Book.objects.all()
        
        # Filter by availability if requested
        available = self.request.query_params.get('available', None)
        if available is not None:
            if available.lower() == 'true':
                queryset = queryset.filter(available_copies__gt=0)
            elif available.lower() == 'false':
                queryset = queryset.filter(available_copies=0)
        
        return queryset


class BookDetailView(generics.RetrieveAPIView):
    """
    API endpoint to retrieve a single book's details.
    Anonymous users can view.
    """
    queryset = Book.objects.all()
    serializer_class = BookDetailSerializer
    permission_classes = [permissions.AllowAny]


class BookCreateView(generics.CreateAPIView):
    """
    API endpoint to create a new book.
    Only admins can create books.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]


class BookUpdateView(generics.UpdateAPIView):
    """
    API endpoint to update a book.
    Only admins can update books.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]


class BookDeleteView(generics.DestroyAPIView):
    """
    API endpoint to delete a book.
    Only admins can delete books.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]


class BookManageView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to retrieve, update, or delete a book.
    Only admins can update or delete.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    
    def get_permissions(self):
        """
        Anonymous users can view, but only admins can modify.
        """
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsAdminUser()]


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def book_stats(request):
    """
    Get overall statistics about books in the library.
    """
    stats = {
        'total_books': Book.objects.count(),
        'available_books': Book.objects.filter(available_copies__gt=0).count(),
        'borrowed_books': Book.objects.filter(available_copies=0).count(),
        'total_copies': sum(book.total_copies for book in Book.objects.all()),
        'available_copies': sum(book.available_copies for book in Book.objects.all()),
        'categories': Book.objects.values_list('category', flat=True).distinct().count(),
    }
    
    return Response(stats, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def book_categories(request):
    """
    Get list of all book categories.
    """
    categories = Book.objects.values_list('category', flat=True).distinct()
    categories = [cat for cat in categories if cat]  # Remove None values
    
    return Response({
        'categories': sorted(categories)
    }, status=status.HTTP_200_OK)
