from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Extended User model with additional fields.
    Supports three roles: anonymous (not registered), registered, and admin.
    """
    ROLE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
    )
    
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.username} ({self.email})"
    
    @property
    def is_admin(self):
        """Check if user has admin role"""
        return self.role == 'admin' or self.is_staff or self.is_superuser
    
    @property
    def active_loans_count(self):
        """Get count of active loans for this user"""
        return self.loans.filter(returned_at__isnull=True).count()
