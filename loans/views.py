from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import Loan
from .serializers import (
    LoanSerializer, LoanDetailSerializer, LoanCreateSerializer, LoanReturnSerializer
)
from accounts.permissions import IsAdminUser


class LoanListView(generics.ListAPIView):
    """
    API endpoint to list loans.
    Users can see their own loans, admins can see all.
    """
    serializer_class = LoanDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'book', 'user']
    ordering_fields = ['borrowed_at', 'due_date', 'returned_at']
    ordering = ['-borrowed_at']
    
    def get_queryset(self):
        """
        Users see their own loans, admins see all.
        """
        user = self.request.user
        if user.is_staff or user.role == 'admin':
            return Loan.objects.all()
        return Loan.objects.filter(user=user)


class LoanDetailView(generics.RetrieveAPIView):
    """
    API endpoint to retrieve a single loan's details.
    Users can only see their own loans.
    """
    serializer_class = LoanDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Users see their own loans, admins see all.
        """
        user = self.request.user
        if user.is_staff or user.role == 'admin':
            return Loan.objects.all()
        return Loan.objects.filter(user=user)


class LoanCreateView(generics.CreateAPIView):
    """
    API endpoint to create a loan (borrow a book).
    Only authenticated users can borrow books.
    """
    queryset = Loan.objects.all()
    serializer_class = LoanCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        loan = serializer.save()
        
        return Response({
            'loan': LoanDetailSerializer(loan).data,
            'message': 'Book borrowed successfully'
        }, status=status.HTTP_201_CREATED)


class LoanReturnView(APIView):
    """
    API endpoint to return a borrowed book.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        loan = get_object_or_404(Loan, pk=pk)
        
        # Check permissions
        if not (request.user == loan.user or request.user.is_staff or request.user.role == 'admin'):
            return Response({
                'error': 'You do not have permission to return this loan'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Check if already returned
        if loan.returned_at:
            return Response({
                'error': 'This book has already been returned'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Return the loan
        serializer = LoanReturnSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if serializer.validated_data.get('notes'):
            loan.notes = serializer.validated_data['notes']
        
        loan.return_loan()
        
        return Response({
            'loan': LoanDetailSerializer(loan).data,
            'message': 'Book returned successfully',
            'fine': float(loan.fine_amount) if loan.fine_amount > 0 else 0
        }, status=status.HTTP_200_OK)


class LoanUpdateView(generics.UpdateAPIView):
    """
    API endpoint to update a loan.
    Only admins can update loans (e.g., mark fines as paid).
    """
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]


class LoanDeleteView(generics.DestroyAPIView):
    """
    API endpoint to delete a loan.
    Only admins can delete loans.
    """
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_loans(request):
    """
    Get all loans for the authenticated user.
    """
    user = request.user
    loans = Loan.objects.filter(user=user)
    
    active_loans = loans.filter(returned_at__isnull=True)
    returned_loans = loans.filter(returned_at__isnull=False)
    
    return Response({
        'active_loans': LoanDetailSerializer(active_loans, many=True).data,
        'returned_loans': LoanDetailSerializer(returned_loans, many=True).data,
        'total_loans': loans.count(),
        'active_count': active_loans.count(),
        'returned_count': returned_loans.count(),
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsAdminUser])
def loan_stats(request):
    """
    Get overall statistics about loans.
    Only admins can access.
    """
    stats = {
        'total_loans': Loan.objects.count(),
        'active_loans': Loan.objects.filter(returned_at__isnull=True, status='active').count(),
        'returned_loans': Loan.objects.filter(status='returned').count(),
        'overdue_loans': Loan.objects.filter(status='overdue').count(),
        'total_fines': sum(loan.fine_amount for loan in Loan.objects.filter(fine_amount__gt=0)),
        'unpaid_fines': sum(loan.fine_amount for loan in Loan.objects.filter(fine_paid=False, fine_amount__gt=0)),
    }
    
    return Response(stats, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsAdminUser])
def calculate_overdue_fines(request):
    """
    Calculate fines for all overdue loans.
    Only admins can access.
    """
    overdue_loans = Loan.objects.filter(returned_at__isnull=True)
    updated_count = 0
    
    for loan in overdue_loans:
        if loan.is_overdue:
            loan.calculate_fine()
            updated_count += 1
    
    return Response({
        'message': f'Calculated fines for {updated_count} overdue loans',
        'updated_count': updated_count
    }, status=status.HTTP_200_OK)
