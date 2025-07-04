# Expense Tracker API

A Django REST API for tracking expenses and income with JWT authentication.

## Features

- User registration and login
- CRUD operations for expenses/income
- Tax calculation (flat or percentage)
- Paginated responses
- User-specific data access

## Setup

1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate venv: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
4. Install requirements: `pip install -r requirements.txt`
5. Run migrations: `python manage.py migrate`
6. Start server: `python manage.py runserver`

## API Endpoints

### Authentication

- POST `/api/auth/register/` - Register new user
- POST `/api/auth/login/` - Login (get JWT tokens)
- POST `/api/auth/refresh/` - Refresh JWT token

### Expenses/Income

- GET `/api/expenses/` - List all records (paginated)
- POST `/api/expenses/` - Create new record
- GET `/api/expenses/{id}/` - Get specific record
- PUT `/api/expenses/{id}/` - Update record
- DELETE `/api/expenses/{id}/` - Delete record

## API Sample Request/Response

- They are in api.rest file. You can user REST Client by Huachao Mao(vs code extension) to directly check/play with the endpoints.
