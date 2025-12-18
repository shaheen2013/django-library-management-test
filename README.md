# Django Library Management System

This project is a production-ready **Library Management System** built as part of a Django/Python technical test (Stefaniia Popovych). The application allows users to browse and borrow books, while administrators can manage books, users, and loan records. The system is fully containerized using Docker.

---

## Technology Stack

The project uses the following technologies, as required:

* Framework: Django 4.2.7
* API Layer: Django REST Framework 3.14.0
* Database: PostgreSQL 15 (Alpine)
* Containerization: Docker & Docker Compose
* Application Server: Gunicorn (production-ready WSGI server)
* Reverse Proxy: Nginx (Alpine)

---

## Running Services

1. PostgreSQL Database (Port 5432)

   * Database Name: library_db
   * User: library_user
   * Persistent storage using Docker volumes
   * Health checks enabled

2. Django Web Application (Port 8000)

   * Django 4.2.7 with Django REST Framework
   * Gunicorn with 3 worker processes
   * Connected to PostgreSQL

3. Nginx Reverse Proxy (Port 80)

   * Serves static files
   * Proxies requests to the Django backend

All services are managed via Docker Compose.

---

## Sample Data

* 5 sample books across different categories

* Test User:

  * Username: testuser
  * Password: TestPass123!

* Admin User:

  * Username: admin
  * Password: admin123

---

## Available Endpoints

* API Root:        [http://localhost:8000/](http://localhost:8000/)
* Swagger Docs:   [http://localhost:8000/swagger/](http://localhost:8000/swagger/)
* ReDoc Docs:     [http://localhost:8000/redoc/](http://localhost:8000/redoc/)
* Admin Panel:    [http://localhost:8000/admin/](http://localhost:8000/admin/)

API Resources:

* Books API:      [http://localhost:8000/api/books/](http://localhost:8000/api/books/)
* Loans API:      [http://localhost:8000/api/loans/](http://localhost:8000/api/loans/)
* Auth API:       [http://localhost:8000/api/auth/](http://localhost:8000/api/auth/)

---

## Authentication

Authentication is handled using **JWT (JSON Web Tokens)**.

* Login:          POST /api/auth/login/
* Token Refresh:  POST /api/auth/token/refresh/

Role-based access control is enforced for users and administrators.

---

## Features

* User registration, login, and JWT authentication
* Role-based access control (User / Admin)
* Book catalog management (CRUD)
* Borrow and return system
* Overdue tracking with fine calculation
* Search, filtering, and pagination
* Admin dashboard
* API documentation (Swagger & ReDoc)
* Comprehensive test suite (pytest)
* PostgreSQL integration
* Dockerized production setup
* Static file serving with Nginx and WhiteNoise
* CORS configuration
* Rate limiting
* Strong input validation

---

## Docker Commands

* Start services:
  docker-compose up -d

* Stop services:
  docker-compose down

* View logs:
  docker-compose logs -f

* Rebuild images:
  docker-compose up --build -d

* Access Django shell:
  docker-compose exec web bash

* Access PostgreSQL:
  docker-compose exec db psql -U library_user -d library_db

---

## Database Structure

Main tables used in the system:

* users        – Custom user model
* books        – Book catalog
* loans        – Borrow and loan records
* auth_*       – Django authentication tables
* django_*     – Django system tables

---

## Testing

Tests are written using pytest.

* Run tests:
  docker-compose exec web pytest

* Run tests with coverage:
  docker-compose exec web pytest --cov=.

---

## Project Structure

* accounts/   – User management and authentication
* books/      – Book catalog and related logic
* loans/      – Loan and borrow system
* tests/      – Automated test suite
* docker/     – Docker and Nginx configuration
* docs/       – API and project documentation

---

## Security

The application follows standard security best practices:

* JWT-based authentication
* Secure password hashing (PBKDF2)
* CSRF protection
* CORS protection
* ORM-based SQL injection protection
* XSS protection headers
* Rate limiting
* Strict input validation

---

## Assets

The `assets/` folder contains screenshots of the application, including:

* Admin panel screens
* Book listing and loan management views

These screenshots are provided to give a quick visual overview of the application without running it.

---
