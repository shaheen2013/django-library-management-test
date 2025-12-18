Django Library Management Test

PROJECT TECHNOLOGY STACK (As Required by Client):
--------------------------------------------------
 Framework: Django 4.2.7
 API: Django REST Framework 3.14.0
 Database: PostgreSQL 15 (Alpine)
 Containerization: Docker + Docker Compose
 Web Server: Gunicorn (production-ready WSGI)
 Reverse Proxy: Nginx (Alpine)

RUNNING SERVICES:
----------------
1. PostgreSQL Database (Port 5432)
   - Database: library_db
   - User: library_user
   - Status: Healthy & Running
   - Data persistence: Docker volume (postgres_data)

2. Django Web Application (Port 8000)
   - Framework: Django 4.2.7 + DRF
   - Workers: Gunicorn with 3 worker processes
   - Status: Running
   - Database: Connected to PostgreSQL

3. Nginx Reverse Proxy (Port 80)
   - Static files: Served via Nginx
   - Proxy: Routes to Django backend
   - Status: Running

SAMPLE DATA:
------------------
 5 Sample Books (various categories)
 Test User: testuser / TestPass123!
 Admin User: admin / admin123

AVAILABLE ENDPOINTS:
-------------------
API Root:           http://localhost:8000
Swagger Docs:       http://localhost:8000/swagger/
ReDoc Docs:         http://localhost:8000/redoc/
Admin Panel:        http://localhost:8000/admin/

Books API:          http://localhost:8000/api/books/
Loans API:          http://localhost:8000/api/loans/
Auth API:           http://localhost:8000/api/auth/

DOCKER COMMANDS:
---------------
Start:              docker-compose up -d
Stop:               docker-compose down
View Logs:          docker-compose logs -f
Rebuild:            docker-compose up --build -d
Shell Access:       docker-compose exec web bash
Database Access:    docker-compose exec db psql -U library_user -d library_db

ADMIN CREDENTIALS:
-----------------
Username: admin
Password: admin123

API AUTHENTICATION:
------------------
Method: JWT (JSON Web Tokens)
Login: POST /api/auth/login/
Token Refresh: POST /api/auth/token/refresh/

FEATURES IMPLEMENTED:
--------------------
 User Authentication & Authorization (JWT)
 Role-based Access Control (User/Admin)
 Book Management (CRUD)
 Loan/Borrow System
 Overdue Tracking
 Fine Calculation
 Search & Filtering
 Pagination
 API Documentation (Swagger/ReDoc)
 Admin Dashboard
 Comprehensive Test Suite (pytest)
 Docker Production Setup
 PostgreSQL Integration
 Static File Serving (Nginx + WhiteNoise)
 CORS Configuration
 Rate Limiting
 Input Validation

DATABASE TABLES:
---------------
- users (Custom user model)
- books (Book catalog)
- loans (Loan/borrow records)
- auth_* (Django authentication)
- django_* (Django system tables)

TESTING:
-------
Run Tests: docker-compose exec web pytest
Coverage:  docker-compose exec web pytest --cov=.

PROJECT STRUCTURE:
-----------------
 accounts/     - User management & authentication
 books/        - Book catalog management
 loans/        - Loan/borrow system
 tests/        - Comprehensive test suite
 docker/       - Docker configuration files
 docs/         - API documentation

SECURITY FEATURES:
-----------------
 JWT Token Authentication
 Password Hashing (PBKDF2)
 CORS Protection
 CSRF Protection
 SQL Injection Protection (ORM)
 XSS Headers
 Rate Limiting
 Input Validation


