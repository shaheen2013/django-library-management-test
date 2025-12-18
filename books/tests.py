import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Book

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
def book_data():
    """Fixture for book data"""
    return {
        'title': 'Test Book',
        'author': 'Test Author',
        'isbn': '9781234567890',
        'publisher': 'Test Publisher',
        'page_count': 300,
        'language': 'English',
        'description': 'A test book description',
        'total_copies': 5,
        'available_copies': 5,
        'category': 'Fiction'
    }


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


@pytest.mark.django_db
class TestBookList:
    """Tests for book listing"""
    
    def test_list_books_anonymous(self, api_client, sample_book):
        """Test listing books as anonymous user"""
        url = reverse('books:book_list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1
    
    def test_list_books_with_search(self, api_client, sample_book):
        """Test book search functionality"""
        url = reverse('books:book_list')
        response = api_client.get(url, {'search': 'Sample'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1
        assert response.data['results'][0]['title'] == 'Sample Book'
    
    def test_list_books_filter_by_category(self, api_client, sample_book):
        """Test filtering books by category"""
        url = reverse('books:book_list')
        response = api_client.get(url, {'category': 'Science'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1
    
    def test_list_books_filter_by_availability(self, api_client, sample_book, unavailable_book):
        """Test filtering books by availability"""
        url = reverse('books:book_list')
        response = api_client.get(url, {'available': 'true'})
        
        assert response.status_code == status.HTTP_200_OK
        # Check that only available books are returned
        for book in response.data['results']:
            assert book['is_available'] is True


@pytest.mark.django_db
class TestBookDetail:
    """Tests for book detail view"""
    
    def test_get_book_detail(self, api_client, sample_book):
        """Test getting book details"""
        url = reverse('books:book_detail', kwargs={'pk': sample_book.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == sample_book.title
        assert response.data['author'] == sample_book.author
        assert response.data['isbn'] == sample_book.isbn
    
    def test_get_nonexistent_book(self, api_client):
        """Test getting details of non-existent book"""
        url = reverse('books:book_detail', kwargs={'pk': 99999})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestBookCreate:
    """Tests for book creation"""
    
    def test_create_book_as_admin(self, api_client, admin_user, book_data):
        """Test creating book as admin"""
        api_client.force_authenticate(user=admin_user)
        url = reverse('books:book_create')
        response = api_client.post(url, book_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Book.objects.filter(isbn=book_data['isbn']).exists()
    
    def test_create_book_as_regular_user(self, api_client, regular_user, book_data):
        """Test creating book as regular user (should fail)"""
        api_client.force_authenticate(user=regular_user)
        url = reverse('books:book_create')
        response = api_client.post(url, book_data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_create_book_anonymous(self, api_client, book_data):
        """Test creating book as anonymous user (should fail)"""
        url = reverse('books:book_create')
        response = api_client.post(url, book_data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_book_duplicate_isbn(self, api_client, admin_user, sample_book, book_data):
        """Test creating book with duplicate ISBN"""
        api_client.force_authenticate(user=admin_user)
        book_data['isbn'] = sample_book.isbn
        url = reverse('books:book_create')
        response = api_client.post(url, book_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_create_book_invalid_isbn(self, api_client, admin_user, book_data):
        """Test creating book with invalid ISBN"""
        api_client.force_authenticate(user=admin_user)
        book_data['isbn'] = '123'  # Too short
        url = reverse('books:book_create')
        response = api_client.post(url, book_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestBookUpdate:
    """Tests for book update"""
    
    def test_update_book_as_admin(self, api_client, admin_user, sample_book):
        """Test updating book as admin"""
        api_client.force_authenticate(user=admin_user)
        url = reverse('books:book_update', kwargs={'pk': sample_book.id})
        data = {'title': 'Updated Title', 'author': 'Updated Author'}
        response = api_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        sample_book.refresh_from_db()
        assert sample_book.title == 'Updated Title'
    
    def test_update_book_as_regular_user(self, api_client, regular_user, sample_book):
        """Test updating book as regular user (should fail)"""
        api_client.force_authenticate(user=regular_user)
        url = reverse('books:book_update', kwargs={'pk': sample_book.id})
        data = {'title': 'Updated Title'}
        response = api_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestBookDelete:
    """Tests for book deletion"""
    
    def test_delete_book_as_admin(self, api_client, admin_user, sample_book):
        """Test deleting book as admin"""
        api_client.force_authenticate(user=admin_user)
        url = reverse('books:book_delete', kwargs={'pk': sample_book.id})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Book.objects.filter(id=sample_book.id).exists()
    
    def test_delete_book_as_regular_user(self, api_client, regular_user, sample_book):
        """Test deleting book as regular user (should fail)"""
        api_client.force_authenticate(user=regular_user)
        url = reverse('books:book_delete', kwargs={'pk': sample_book.id})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestBookStats:
    """Tests for book statistics"""
    
    def test_get_book_stats(self, api_client, sample_book, unavailable_book):
        """Test getting book statistics"""
        url = reverse('books:book_stats')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'total_books' in response.data
        assert 'available_books' in response.data
        assert 'borrowed_books' in response.data
        assert response.data['total_books'] >= 2


@pytest.mark.django_db
class TestBookCategories:
    """Tests for book categories"""
    
    def test_get_book_categories(self, api_client, sample_book):
        """Test getting list of categories"""
        url = reverse('books:book_categories')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'categories' in response.data
        assert 'Science' in response.data['categories']


@pytest.mark.django_db
class TestBookModel:
    """Tests for Book model"""
    
    def test_book_creation(self, sample_book):
        """Test book model creation"""
        assert sample_book.title == 'Sample Book'
        assert sample_book.author == 'Sample Author'
        assert sample_book.isbn == '9780987654321'
    
    def test_book_str_representation(self, sample_book):
        """Test book string representation"""
        assert str(sample_book) == 'Sample Book by Sample Author'
    
    def test_is_available_property(self, sample_book, unavailable_book):
        """Test is_available property"""
        assert sample_book.is_available is True
        assert unavailable_book.is_available is False
    
    def test_borrowed_copies_property(self, sample_book):
        """Test borrowed_copies property"""
        assert sample_book.borrowed_copies == 0
    
    def test_borrow_book(self, sample_book):
        """Test borrowing a book"""
        initial_available = sample_book.available_copies
        result = sample_book.borrow()
        
        assert result is True
        assert sample_book.available_copies == initial_available - 1
    
    def test_borrow_unavailable_book(self, unavailable_book):
        """Test borrowing an unavailable book"""
        result = unavailable_book.borrow()
        
        assert result is False
    
    def test_return_book(self, sample_book):
        """Test returning a book"""
        sample_book.borrow()
        initial_available = sample_book.available_copies
        result = sample_book.return_book()
        
        assert result is True
        assert sample_book.available_copies == initial_available + 1
    
    def test_available_copies_validation(self):
        """Test that available copies can't exceed total copies"""
        from django.core.exceptions import ValidationError
        
        book = Book(
            title='Test Book',
            author='Test Author',
            isbn='9781234567890',
            page_count=100,
            total_copies=5,
            available_copies=10
        )
        
        with pytest.raises(ValidationError):
            book.clean()
