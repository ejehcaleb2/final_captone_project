<<<<<<< HEAD
# Course Enrollment Platform(This project humbled me for real)

A secure, database-backed RESTful API for managing a course enrollment platform using FastAPI.

## Features

- User authentication and authorization with JWT
- Role-based access control (Student/Admin)
- Course management
- Enrollment management with business rules
- Comprehensive automated tests

## Setup Instructions

1. **Clone the repository** (if applicable) and navigate to the project directory.

# Course Enrollment Platform

A secure, database-backed RESTful API for managing course enrollments using FastAPI.

**Key features**
- JWT authentication
- Role-based access control (student / admin)
- Course and enrollment management with business rules
- PostgreSQL + SQLAlchemy with Alembic migrations
- Comprehensive automated tests (pytest)

**Quickstart**
1. Create and activate a virtual environment:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Copy environment file and fill secrets:
```bash
cp .env.example .env

```
4. Run migrations:
```bash
alembic upgrade head
```
5. Run the app:
```bash
uvicorn app.main:app --reload
```

Interactive docs: https://final-captone-project.onrender.com/docs
Deployment: Render

**Testing**
Run the automated test suite:
```bash
pytest
```

**Environment**
- Provide a `DATABASE_URL` pointing to a PostgreSQL instance. Example format:
  `postgresql://user:password@host:5432/dbname`
- `SECRET_KEY` must be a securely generated random string. Do not commit `.env` to VCS.

**API Endpoints (overview)**
- Authentication
  - `POST /users/register` — register
  - `POST /users/login` — obtain JWT
  - `GET /users/me` — current user (authenticated)
- Courses
  - `GET /courses/` — list active courses (authenticated)
  - `GET /courses/{course_id}` — get course (authenticated)
  - `POST /courses/` — create course (admin)
  - `PUT /courses/{course_id}` — update course (admin)
  - `DELETE /courses/{course_id}` — delete course (admin, only if no enrollments)
- Enrollments
  - `POST /enrollments/` — enroll (student)
  - `DELETE /enrollments/{course_id}` — deregister (student)
  - `GET /enrollments/my-enrollments` — view own enrollments (student)
  - `GET /enrollments/all` — view all enrollments (admin)
  - `GET /enrollments/course/{course_id}` — view enrollments by course (admin)
  - `DELETE /enrollments/admin/{course_id}/user/{user_id}` — remove student (admin)
  - `DELETE /enrollments/admin/{course_id}` — bulk remove students by `user_ids` (admin)

**Business rules enforced**
- Unique emails for users
- Unique course codes
- Course `capacity` must be > 0
- Only active users may authenticate
- Students cannot enroll twice in the same course
- Enrollment fails if course is full or inactive

**Notes**
- Migrations are handled via Alembic (`alembic/versions` present).
- The repository should not contain secrets. Use `.env.example` for sharing config structure.

If you'd like, I can also add a CI workflow to run migrations and tests automatically.
## Features
