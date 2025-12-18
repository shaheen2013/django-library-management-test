"""
Initial setup script for Library Management System
This script helps automate the initial setup process.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_management.settings')
django.setup()

from django.contrib.auth import get_user_model
from books.models import Book

User = get_user_model()


def create_sample_data():
    """Create sample books and users for testing"""
    print("Creating sample data...")
    
    # Create sample books
    sample_books = [
        {
            'title': 'Python Programming for Beginners',
            'author': 'John Smith',
            'isbn': '9781234567890',
            'publisher': 'Tech Books Publishing',
            'page_count': 500,
            'language': 'English',
            'description': 'A comprehensive guide to Python programming.',
            'total_copies': 5,
            'available_copies': 5,
            'category': 'Programming'
        },
        {
            'title': 'Django for Professionals',
            'author': 'Jane Doe',
            'isbn': '9780987654321',
            'publisher': 'Web Dev Press',
            'page_count': 450,
            'language': 'English',
            'description': 'Build production-ready Django applications.',
            'total_copies': 3,
            'available_copies': 3,
            'category': 'Programming'
        },
        {
            'title': 'Data Science Essentials',
            'author': 'Alice Johnson',
            'isbn': '9781111111111',
            'publisher': 'Data Science Books',
            'page_count': 600,
            'language': 'English',
            'description': 'Learn data science from scratch.',
            'total_copies': 4,
            'available_copies': 4,
            'category': 'Data Science'
        },
        {
            'title': 'Machine Learning Fundamentals',
            'author': 'Bob Wilson',
            'isbn': '9782222222222',
            'publisher': 'AI Publishing',
            'page_count': 550,
            'language': 'English',
            'description': 'Introduction to machine learning concepts.',
            'total_copies': 3,
            'available_copies': 3,
            'category': 'Machine Learning'
        },
        {
            'title': 'Web Design Basics',
            'author': 'Carol Brown',
            'isbn': '9783333333333',
            'publisher': 'Design House',
            'page_count': 400,
            'language': 'English',
            'description': 'Fundamental principles of web design.',
            'total_copies': 6,
            'available_copies': 6,
            'category': 'Design'
        }
    ]
    
    created_books = 0
    for book_data in sample_books:
        book, created = Book.objects.get_or_create(
            isbn=book_data['isbn'],
            defaults=book_data
        )
        if created:
            created_books += 1
            print(f"  [+] Created book: {book.title}")
        else:
            print(f"  [-] Book already exists: {book.title}")
    
    print(f"\nSummary: Created {created_books} new book(s)")
    
    # Create a test user
    try:
        test_user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'testuser@example.com',
                'first_name': 'Test',
                'last_name': 'User',
                'role': 'user'
            }
        )
        if created:
            test_user.set_password('TestPass123!')
            test_user.save()
            print(f"\n[+] Created test user: testuser (password: TestPass123!)")
        else:
            print(f"\n[-] Test user already exists: testuser")
    except Exception as e:
        print(f"\n[!] Error creating test user: {e}")


def check_admin_exists():
    """Check if admin user exists"""
    admin_users = User.objects.filter(is_superuser=True)
    if admin_users.exists():
        print("\n[+] Admin user(s) found:")
        for admin in admin_users:
            print(f"  - {admin.username} ({admin.email})")
        return True
    else:
        print("\n[!] No admin users found.")
        print("  Please create a superuser with: python manage.py createsuperuser")
        return False


def main():
    """Main setup function"""
    print("=" * 60)
    print("Library Management System - Initial Setup")
    print("=" * 60)
    
    # Check for admin
    has_admin = check_admin_exists()
    
    # Ask user if they want to create sample data
    print("\n" + "=" * 60)
    response = input("Do you want to create sample books and test user? (y/n): ")
    
    if response.lower() in ['y', 'yes']:
        create_sample_data()
    else:
        print("Skipping sample data creation.")
    
    print("\n" + "=" * 60)
    print("Setup complete!")
    print("\nNext steps:")
    if not has_admin:
        print("  1. Create an admin user: python manage.py createsuperuser")
    print("  2. Start the server: python manage.py runserver")
    print("  3. Open your browser: http://127.0.0.1:8000/swagger/")
    print("=" * 60)


if __name__ == '__main__':
    main()
