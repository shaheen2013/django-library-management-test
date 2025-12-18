from django.urls import path
from .views import (
    BookListView, BookDetailView, BookCreateView,
    BookUpdateView, BookDeleteView, BookManageView,
    book_stats, book_categories
)

app_name = 'books'

urlpatterns = [
    # Public endpoints
    path('', BookListView.as_view(), name='book_list'),
    path('<int:pk>/', BookDetailView.as_view(), name='book_detail'),
    path('stats/', book_stats, name='book_stats'),
    path('categories/', book_categories, name='book_categories'),
    
    # Admin endpoints
    path('create/', BookCreateView.as_view(), name='book_create'),
    path('<int:pk>/update/', BookUpdateView.as_view(), name='book_update'),
    path('<int:pk>/delete/', BookDeleteView.as_view(), name='book_delete'),
    path('<int:pk>/manage/', BookManageView.as_view(), name='book_manage'),
]


