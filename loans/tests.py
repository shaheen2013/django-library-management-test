import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.test import APIClient
from .models import Loan
from books.models import Book

User = get_user_model()


@pytest.fixture
def api_client():
    """Fixture for API client"""
    return APIClient()


@pytest.fixture
def admin_user(db):
    """Fixture for admin user"""
    return User.objects.create_user(
        username='admin',
        email='admin@example.com',
        password='AdminPass123!',
        role='admin',
        is_staff=True
    )


@pytest.fixture
def regular_user(db):
    """Fixture for regular user"""
    return User.objects.create_user(
        username='user',
        email='user@example.com',
        password='UserPass123!',
        role='user'
    )


@pytest.fixture
def another_user(db):
    """Fixture for another regular user"""
    return User.objects.create_user(
        username='user2',
        email='user2@example.com',
        password='UserPass123!',
        role='user'
    )


@pytest.fixture
def sample_book(db):
    """Fixture for a sample book"""
    return Book.objects.create(
        title='Sample Book',
        author='Sample Author',
        isbn='9780987654321',
        page_count=250,
        total_copies=3,
        available_copies=3,
        category='Science'
    )


@pytest.fixture
def unavailable_book(db):
    """Fixture for an unavailable book"""
    return Book.objects.create(
        title='Unavailable Book',
        author='Popular Author',
        isbn='9781111111111',
        page_count=400,
        total_copies=2,
        available_copies=0,
        category='Fantasy'
    )


@pytest.fixture
def active_loan(db, regular_user, sample_book):
    """Fixture for an active loan"""
    sample_book.borrow()
    return Loan.objects.create(
        user=regular_user,
        book=sample_book,
        due_date=timezone.now() + timedelta(days=14)
    )


@pytest.fixture
def overdue_loan(db, regular_user):
    """Fixture for an overdue loan"""
    book = Book.objects.create(
        title='Overdue Book',
        author='Test Author',
        isbn='9782222222222',
        page_count=300,
        total_copies=1,
        available_copies=0
    )
    return Loan.objects.create(
        user=regular_user,
        book=book,
        due_date=timezone.now() - timedelta(days=5)
    )


@pytest.mark.django_db
class TestLoanList:
    """Tests for loan listing"""
    
    def test_list_loans_as_regular_user(self, api_client, regular_user, active_loan):
        """Test listing loans as regular user (should see own loans)"""
        api_client.force_authenticate(user=regular_user)
        url = reverse('loans:loan_list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1
    
    def test_list_loans_as_admin(self, api_client, admin_user, active_loan):
        """Test listing loans as admin (should see all loans)"""
        api_client.force_authenticate(user=admin_user)
        url = reverse('loans:loan_list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1
    
    def test_list_loans_unauthenticated(self, api_client):
        """Test listing loans without authentication"""
        url = reverse('loans:loan_list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_user_sees_only_own_loans(self, api_client, regular_user, another_user, active_loan):
        """Test that users only see their own loans"""
        api_client.force_authenticate(user=another_user)
        url = reverse('loans:loan_list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        # Another user should not see regular_user's loans
        for loan in response.data['results']:
            assert loan['user']['id'] == another_user.id


@pytest.mark.django_db
class TestLoanDetail:
    """Tests for loan detail view"""
    
    def test_get_own_loan_detail(self, api_client, regular_user, active_loan):
        """Test getting own loan details"""
        api_client.force_authenticate(user=regular_user)
        url = reverse('loans:loan_detail', kwargs={'pk': active_loan.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == active_loan.id
    
    def test_get_other_user_loan_detail(self, api_client, another_user, active_loan):
        """Test getting another user's loan details (should fail)"""
        api_client.force_authenticate(user=another_user)
        url = reverse('loans:loan_detail', kwargs={'pk': active_loan.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_loan_detail_as_admin(self, api_client, admin_user, active_loan):
        """Test getting loan details as admin"""
        api_client.force_authenticate(user=admin_user)
        url = reverse('loans:loan_detail', kwargs={'pk': active_loan.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestLoanCreate:
    """Tests for loan creation (borrowing books)"""
    
    def test_borrow_book_success(self, api_client, regular_user, sample_book):
        """Test successfully borrowing a book"""
        api_client.force_authenticate(user=regular_user)
        url = reverse('loans:loan_create')
        data = {
            'book': sample_book.id,
            'due_date': (timezone.now() + timedelta(days=14)).isoformat()
        }
        initial_available = sample_book.available_copies
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'loan' in response.data
        sample_book.refresh_from_db()
        assert sample_book.available_copies == initial_available - 1
    
    def test_borrow_unavailable_book(self, api_client, regular_user, unavailable_book):
        """Test borrowing an unavailable book (should fail)"""
        api_client.force_authenticate(user=regular_user)
        url = reverse('loans:loan_create')
        data = {
            'book': unavailable_book.id,
            'due_date': (timezone.now() + timedelta(days=14)).isoformat()
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_borrow_already_borrowed_book(self, api_client, regular_user, active_loan):
        """Test borrowing a book that user already has (should fail)"""
        api_client.force_authenticate(user=regular_user)
        url = reverse('loans:loan_create')
        data = {
            'book': active_loan.book.id,
            'due_date': (timezone.now() + timedelta(days=14)).isoformat()
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_borrow_book_unauthenticated(self, api_client, sample_book):
        """Test borrowing without authentication (should fail)"""
        url = reverse('loans:loan_create')
        data = {
            'book': sample_book.id,
            'due_date': (timezone.now() + timedelta(days=14)).isoformat()
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestLoanReturn:
    """Tests for loan return"""
    
    def test_return_own_loan(self, api_client, regular_user, active_loan):
        """Test returning own loan"""
        api_client.force_authenticate(user=regular_user)
        url = reverse('loans:loan_return', kwargs={'pk': active_loan.id})
        initial_available = active_loan.book.available_copies
        response = api_client.post(url, {}, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        active_loan.refresh_from_db()
        assert active_loan.returned_at is not None
        assert active_loan.book.available_copies == initial_available + 1
    
    def test_return_already_returned_loan(self, api_client, regular_user, active_loan):
        """Test returning an already returned loan (should fail)"""
        api_client.force_authenticate(user=regular_user)
        active_loan.return_loan()
        url = reverse('loans:loan_return', kwargs={'pk': active_loan.id})
        response = api_client.post(url, {}, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_return_other_user_loan(self, api_client, another_user, active_loan):
        """Test returning another user's loan (should fail)"""
        api_client.force_authenticate(user=another_user)
        url = reverse('loans:loan_return', kwargs={'pk': active_loan.id})
        response = api_client.post(url, {}, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_return_overdue_loan_calculates_fine(self, api_client, regular_user, overdue_loan):
        """Test that returning overdue loan calculates fine"""
        api_client.force_authenticate(user=regular_user)
        url = reverse('loans:loan_return', kwargs={'pk': overdue_loan.id})
        response = api_client.post(url, {}, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['fine'] > 0
        overdue_loan.refresh_from_db()
        assert overdue_loan.fine_amount > 0


@pytest.mark.django_db
class TestLoanUpdate:
    """Tests for loan update (admin only)"""
    
    def test_update_loan_as_admin(self, api_client, admin_user, active_loan):
        """Test updating loan as admin"""
        api_client.force_authenticate(user=admin_user)
        url = reverse('loans:loan_update', kwargs={'pk': active_loan.id})
        data = {'notes': 'Updated notes'}
        response = api_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_update_loan_as_regular_user(self, api_client, regular_user, active_loan):
        """Test updating loan as regular user (should fail)"""
        api_client.force_authenticate(user=regular_user)
        url = reverse('loans:loan_update', kwargs={'pk': active_loan.id})
        data = {'notes': 'Updated notes'}
        response = api_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestUserLoans:
    """Tests for user loans endpoint"""
    
    def test_get_user_loans(self, api_client, regular_user, active_loan):
        """Test getting user's loans"""
        api_client.force_authenticate(user=regular_user)
        url = reverse('loans:user_loans')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'active_loans' in response.data
        assert 'returned_loans' in response.data
        assert len(response.data['active_loans']) >= 1


@pytest.mark.django_db
class TestLoanStats:
    """Tests for loan statistics (admin only)"""
    
    def test_get_loan_stats_as_admin(self, api_client, admin_user, active_loan):
        """Test getting loan statistics as admin"""
        api_client.force_authenticate(user=admin_user)
        url = reverse('loans:loan_stats')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'total_loans' in response.data
        assert 'active_loans' in response.data
        assert 'overdue_loans' in response.data
    
    def test_get_loan_stats_as_regular_user(self, api_client, regular_user):
        """Test getting loan statistics as regular user (should fail)"""
        api_client.force_authenticate(user=regular_user)
        url = reverse('loans:loan_stats')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestCalculateOverdueFines:
    """Tests for calculate overdue fines endpoint"""
    
    def test_calculate_fines_as_admin(self, api_client, admin_user, overdue_loan):
        """Test calculating fines as admin"""
        api_client.force_authenticate(user=admin_user)
        url = reverse('loans:calculate_fines')
        response = api_client.post(url, {}, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'updated_count' in response.data
        overdue_loan.refresh_from_db()
        assert overdue_loan.fine_amount > 0
    
    def test_calculate_fines_as_regular_user(self, api_client, regular_user):
        """Test calculating fines as regular user (should fail)"""
        api_client.force_authenticate(user=regular_user)
        url = reverse('loans:calculate_fines')
        response = api_client.post(url, {}, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestLoanModel:
    """Tests for Loan model"""
    
    def test_loan_creation(self, active_loan):
        """Test loan model creation"""
        assert active_loan.user is not None
        assert active_loan.book is not None
        assert active_loan.status == 'active'
    
    def test_loan_str_representation(self, active_loan):
        """Test loan string representation"""
        expected = f"{active_loan.user.username} borrowed {active_loan.book.title}"
        assert str(active_loan) == expected
    
    def test_is_overdue_property(self, active_loan, overdue_loan):
        """Test is_overdue property"""
        assert active_loan.is_overdue is False
        assert overdue_loan.is_overdue is True
    
    def test_days_overdue_property(self, active_loan, overdue_loan):
        """Test days_overdue property"""
        assert active_loan.days_overdue == 0
        assert overdue_loan.days_overdue >= 5
    
    def test_calculate_fine(self, overdue_loan):
        """Test fine calculation"""
        fine = overdue_loan.calculate_fine(daily_rate=0.50)
        expected_fine = overdue_loan.days_overdue * 0.50
        assert fine == expected_fine
        assert overdue_loan.status == 'overdue'
    
    def test_return_loan(self, active_loan):
        """Test returning a loan"""
        result = active_loan.return_loan()
        assert result is True
        assert active_loan.returned_at is not None
        assert active_loan.status in ['returned', 'overdue']
    
    def test_auto_due_date(self, regular_user, sample_book):
        """Test that due date is automatically set if not provided"""
        loan = Loan.objects.create(
            user=regular_user,
            book=sample_book
        )
        assert loan.due_date is not None
        assert loan.due_date > timezone.now()
