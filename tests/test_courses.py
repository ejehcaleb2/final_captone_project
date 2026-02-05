import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

import uuid


def _random_email(prefix: str):
    return f"{prefix}_{uuid.uuid4().hex[:8]}@example.com"


def create_admin_user():
    user_data = {
        "name": "Admin User",
        "email": _random_email("admin"),
        "password": "adminpassword",
        "role": "admin"
    }
    response = client.post("/users/register", json=user_data)
    assert response.status_code == 200
    # Login to get access token
    login_data = {"username": user_data["email"], "password": user_data["password"]}
    login_response = client.post("/users/login", data=login_data)
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_create_course():
    # Get admin headers
    headers = create_admin_user()

    # Course data to create
    import uuid
    course_code = f"PY_{uuid.uuid4().hex[:6]}"
    course_data = {
        "title": "Introduction to Python",
        "code": course_code,
        "capacity": 30
    }

    # Make POST request to create course
    response = client.post("/courses/", json=course_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == course_data["title"]
    assert data["code"] == course_data["code"]
    assert data["capacity"] == course_data["capacity"]
    assert data["is_active"] is True

def test_get_all_courses():
    # Make GET request to retrieve all courses
    response = client.get("/courses/")
    assert response.status_code == 200
    data = response.json()
    # Check that at least one course exists (the one we just created)
    assert len(data) >= 1
    # Verify that the first course has the expected keys
    course_keys = {"id", "title", "code", "capacity", "is_active"}
    assert course_keys.issubset(data[0].keys())
def test_get_course_by_id():
    # First, get all courses to find an ID
    all_courses_response = client.get("/courses/")
    assert all_courses_response.status_code == 200
    course_id = all_courses_response.json()[0]["id"]

    # Now, get that course by ID
    response = client.get(f"/courses/{course_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == course_id
    assert "title" in data
    assert "code" in data
    assert "capacity" in data
    assert "is_active" in data
def test_update_course():
    # Get admin headers
    headers = create_admin_user()

    # Get an existing course ID
    all_courses_response = client.get("/courses/")
    course_id = all_courses_response.json()[0]["id"]

    # New data to update
    update_data = {
        "title": "Advanced Python",
        "capacity": 50,
        "is_active": True
    }

    # Make PUT request to update course
    response = client.put(f"/courses/{course_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["capacity"] == update_data["capacity"]
    assert data["is_active"] == update_data["is_active"]
def test_non_admin_cannot_create_course():
    # First, register a normal student
    import uuid
    def _random_email(prefix: str):
        return f"{prefix}_{uuid.uuid4().hex[:8]}@example.com"

    student_data = {
        "name": "Student User",
        "email": _random_email("student"),
        "password": "studentpassword",
        "role": "student"
    }
    response = client.post("/users/register", json=student_data)
    assert response.status_code == 200

    # Login as student to get token
    login_data = {"username": student_data["email"], "password": student_data["password"]}
    login_response = client.post("/users/login", data=login_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Try to create a course
    import uuid
    course_data = {
        "title": "Unauthorized Course",
        "code": f"UC_{uuid.uuid4().hex[:6]}",
        "capacity": 10
    }
    create_response = client.post("/courses/", json=course_data, headers=headers)
    assert create_response.status_code == 403  # Forbidden
    
def test_deactivate_course():
    # Get admin headers
    headers = create_admin_user()

    # Get an existing course ID
    all_courses_response = client.get("/courses/")
    course_id = all_courses_response.json()[0]["id"]

    # Update course to deactivate
    update_data = {"is_active": False}
    response = client.put(f"/courses/{course_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is False

def test_admin_delete_course():
    # Get admin headers
    headers = create_admin_user()

    # Create a new course to delete
    import uuid
    course_code = f"DEL_{uuid.uuid4().hex[:6]}"
    course_data = {
        "title": "Course to Delete",
        "code": course_code,
        "capacity": 10
    }
    create_response = client.post("/courses/", json=course_data, headers=headers)
    assert create_response.status_code == 200
    course_id = create_response.json()["id"]

    # Delete the course
    delete_response = client.delete(f"/courses/{course_id}", headers=headers)
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Course deleted successfully"

    # Verify course is deleted
    get_response = client.get(f"/courses/{course_id}")
    assert get_response.status_code == 404

