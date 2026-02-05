<<<<<<< HEAD
# Course Enrollment Platform

A secure, database-backed RESTful API for managing a course enrollment platform using FastAPI.

## Features

- User authentication and authorization with JWT
- Role-based access control (Student/Admin)
- Course management
- Enrollment management with business rules
- SQLite database with migrations
- Comprehensive automated tests

## Setup Instructions

1. **Clone the repository** (if applicable) and navigate to the project directory.

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - On Windows: `venv\Scripts\activate`
   - On macOS/Linux: `source venv/bin/activate`

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables:**
   - Copy `.env` file and update `SECRET_KEY` with a secure random string.

6. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

7. **Run the application:**
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://127.0.0.1:8000`

8. **Access API documentation:**
   - Interactive API docs: `http://127.0.0.1:8000/docs`

## Running Tests

To run the automated test suite:

```bash
pytest
```

All tests should pass, covering authentication, course management, enrollment logic, and API endpoints.

## API Endpoints

### Authentication
- `POST /users/register` - Register a new user
- `POST /users/login` - Login and get JWT token
- `GET /users/me` - Get current user profile (authenticated)

### Courses
- `GET /courses/` - Get all active courses (public)
- `GET /courses/{course_id}` - Get course by ID (public)
- `POST /courses/` - Create a new course (admin only)
- `PUT /courses/{course_id}` - Update course (admin only)

### Enrollments
- `POST /enrollments/` - Enroll in a course (student only)
- `DELETE /enrollments/{course_id}` - Deregister from a course (student only)
- `GET /enrollments/all` - Get all enrollments (admin only)
- `GET /enrollments/course/{course_id}` - Get enrollments for a course (admin only)
- `DELETE /enrollments/{enrollment_id}` - Remove student from course (admin only)

## Business Rules

- Emails must be unique
- Course codes must be unique
- Only active students can authenticate
- Students cannot enroll in the same course twice
- Enrollment fails if course is full or inactive
- Admins can manage courses and view all enrollments

## Database

Uses SQLite with SQLAlchemy ORM. Migrations are handled by Alembic.

## Security

- Passwords are hashed using PBKDF2
- JWT tokens for authentication
- Role-based access control
# Course Enrollment Platform

A secure, database-backed RESTful API for managing a course enrollment platform using FastAPI.

## Features

- User authentication and authorization with JWT
- Role-based access control (Student/Admin)
- Course management
- Enrollment management with business rules
- SQLite database with migrations
- Comprehensive automated tests

## Setup Instructions

1. **Clone the repository** (if applicable) and navigate to the project directory.

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - On Windows: `venv\\Scripts\\activate`
   - On macOS/Linux: `source venv/bin/activate`

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables:**
   - Copy `.env` file and update `SECRET_KEY` with a secure random string.

6. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

7. **Run the application:**
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://127.0.0.1:8000`

8. **Access API documentation:**
   - Interactive API docs: `http://127.0.0.1:8000/docs`

## Running Tests

To run the automated test suite:

```bash
pytest
```

All tests should pass, covering authentication, course management, enrollment logic, and API endpoints.

## API Endpoints

### Authentication
- `POST /users/register` - Register a new user
- `POST /users/login` - Login and get JWT token
- `GET /users/me` - Get current user profile (authenticated)

### Courses
- `GET /courses/` - Get all active courses (public)
- `GET /courses/{course_id}` - Get course by ID (public)
- `POST /courses/` - Create a new course (admin only)
- `PUT /courses/{course_id}` - Update course (admin only)
- `DELETE /courses/{course_id}` - Delete course (admin only, no active enrollments)

### Enrollments
- `POST /enrollments/` - Enroll in a course (student only)
- `DELETE /enrollments/{course_id}` - Deregister from a course (student only)
- `GET /enrollments/all` - Get all enrollments (admin or student's own enrollments)
- `GET /enrollments/course/{course_id}` - Get enrollments for a course (admin only)
- `DELETE /enrollments/admin/{course_id}/user/{user_id}` - Remove student from course (admin only)
- `DELETE /enrollments/admin/{course_id}` - Bulk remove students by `user_ids` (admin only)

## Business Rules

- Emails must be unique
- Course codes must be unique
- Only active students can authenticate
- Students cannot enroll in the same course twice
- Enrollment fails if course is full or inactive
- Admins can manage courses and view all enrollments

## Database

Uses SQLite with SQLAlchemy ORM. Migrations are handled by Alembic.

## Security

- Passwords are hashed using PBKDF2
- JWT tokens for authentication
- Role-based access control

# final_captone_project
