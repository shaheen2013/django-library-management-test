import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    """Fixture for API client"""
    return APIClient()


@pytest.fixture
def user_data():
    """Fixture for user registration data"""
    return {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'TestPass123!',
        'password_confirm': 'TestPass123!',
        'first_name': 'Test',
        'last_name': 'User'
    }


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


@pytest.mark.django_db
class TestUserRegistration:
    """Tests for user registration"""
    
    def test_user_registration_success(self, api_client, user_data):
        """Test successful user registration"""
        url = reverse('accounts:register')
        response = api_client.post(url, user_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'user' in response.data
        assert 'tokens' in response.data
        assert response.data['user']['username'] == user_data['username']
        assert response.data['user']['email'] == user_data['email']
        assert User.objects.filter(username=user_data['username']).exists()
    
    def test_user_registration_password_mismatch(self, api_client, user_data):
        """Test registration with password mismatch"""
        user_data['password_confirm'] = 'DifferentPass123!'
        url = reverse('accounts:register')
        response = api_client.post(url, user_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_user_registration_duplicate_username(self, api_client, user_data, regular_user):
        """Test registration with duplicate username"""
        user_data['username'] = regular_user.username
        url = reverse('accounts:register')
        response = api_client.post(url, user_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_user_registration_invalid_email(self, api_client, user_data):
        """Test registration with invalid email"""
        user_data['email'] = 'invalid-email'
        url = reverse('accounts:register')
        response = api_client.post(url, user_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserLogin:
    """Tests for user login"""
    
    def test_login_success(self, api_client, regular_user):
        """Test successful login"""
        url = reverse('accounts:login')
        data = {
            'username': 'user',
            'password': 'UserPass123!'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'user' in response.data
        assert 'tokens' in response.data
        assert 'access' in response.data['tokens']
        assert 'refresh' in response.data['tokens']
    
    def test_login_invalid_credentials(self, api_client, regular_user):
        """Test login with invalid credentials"""
        url = reverse('accounts:login')
        data = {
            'username': 'user',
            'password': 'WrongPassword'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_nonexistent_user(self, api_client):
        """Test login with non-existent user"""
        url = reverse('accounts:login')
        data = {
            'username': 'nonexistent',
            'password': 'SomePassword123!'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUserProfile:
    """Tests for user profile"""
    
    def test_get_profile_authenticated(self, api_client, regular_user):
        """Test getting profile when authenticated"""
        api_client.force_authenticate(user=regular_user)
        url = reverse('accounts:user_profile')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == regular_user.username
        assert response.data['email'] == regular_user.email
    
    def test_get_profile_unauthenticated(self, api_client):
        """Test getting profile when not authenticated"""
        url = reverse('accounts:user_profile')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_profile(self, api_client, regular_user):
        """Test updating user profile"""
        api_client.force_authenticate(user=regular_user)
        url = reverse('accounts:user_profile')
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone': '1234567890'
        }
        response = api_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'Updated'
        assert response.data['last_name'] == 'Name'


@pytest.mark.django_db
class TestChangePassword:
    """Tests for password change"""
    
    def test_change_password_success(self, api_client, regular_user):
        """Test successful password change"""
        api_client.force_authenticate(user=regular_user)
        url = reverse('accounts:change_password')
        data = {
            'old_password': 'UserPass123!',
            'new_password': 'NewPassword123!',
            'new_password_confirm': 'NewPassword123!'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify new password works
        regular_user.refresh_from_db()
        assert regular_user.check_password('NewPassword123!')
    
    def test_change_password_wrong_old_password(self, api_client, regular_user):
        """Test password change with wrong old password"""
        api_client.force_authenticate(user=regular_user)
        url = reverse('accounts:change_password')
        data = {
            'old_password': 'WrongPassword',
            'new_password': 'NewPassword123!',
            'new_password_confirm': 'NewPassword123!'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserStats:
    """Tests for user statistics"""
    
    def test_get_user_stats(self, api_client, regular_user):
        """Test getting user statistics"""
        api_client.force_authenticate(user=regular_user)
        url = reverse('accounts:user_stats')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'total_loans' in response.data
        assert 'active_loans' in response.data
        assert 'returned_loans' in response.data
        assert 'overdue_loans' in response.data


@pytest.mark.django_db
class TestUserList:
    """Tests for user list (admin only)"""
    
    def test_list_users_as_admin(self, api_client, admin_user, regular_user):
        """Test listing users as admin"""
        api_client.force_authenticate(user=admin_user)
        url = reverse('accounts:user_list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 2
    
    def test_list_users_as_regular_user(self, api_client, regular_user):
        """Test listing users as regular user (should fail)"""
        api_client.force_authenticate(user=regular_user)
        url = reverse('accounts:user_list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestUserModel:
    """Tests for User model"""
    
    def test_user_creation(self, regular_user):
        """Test user model creation"""
        assert regular_user.username == 'user'
        assert regular_user.email == 'user@example.com'
        assert regular_user.role == 'user'
    
    def test_user_str_representation(self, regular_user):
        """Test user string representation"""
        assert str(regular_user) == 'user (user@example.com)'
    
    def test_is_admin_property(self, admin_user, regular_user):
        """Test is_admin property"""
        assert admin_user.is_admin is True
        assert regular_user.is_admin is False
    
    def test_active_loans_count_property(self, regular_user):
        """Test active_loans_count property"""
        assert regular_user.active_loans_count == 0
