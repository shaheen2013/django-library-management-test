"""
URL configuration for library_management project.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger/OpenAPI documentation setup
schema_view = get_schema_view(
    openapi.Info(
        title="Library Management API",
        default_version='v1',
        description="""
        A comprehensive Library Management System API
        
        Features:
        - User authentication and authorization with JWT
        - Book management (CRUD operations)
        - Loan management (borrow and return books)
        - User roles (User and Admin)
        - Filtering and pagination
        - Security measures against common attacks
        """,
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@library.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/auth/', include('accounts.urls')),
    path('api/books/', include('books.urls')),
    path('api/loans/', include('loans.urls')),
    
    # Swagger documentation
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='api-docs'),
]
