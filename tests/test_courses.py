import pytest
from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)


def _random_email(prefix: str):
    return f"{prefix}_{uuid.uuid4().hex[:8]}@example.com"


def _create_admin_token():
    """Helper to create admin and return token"""
    email = _random_email("admin")
    user_data = {"name": "Admin", "email": email, "password": "pass123", "role": "admin"}
    client.post("/users/register", json=user_data)
    login_resp = client.post("/users/login", data={"username": email, "password": "pass123"})
    return login_resp.json()["access_token"]


def _create_student_token():
    """Helper to create student and return token"""
    email = _random_email("student")
    user_data = {"name": "Student", "email": email, "password": "pass123", "role": "student"}
    client.post("/users/register", json=user_data)
    login_resp = client.post("/users/login", data={"username": email, "password": "pass123"})
    return login_resp.json()["access_token"]


# ========== COURSE VIEWING TESTS (Both student & admin) ==========

def test_authenticated_user_view_all_courses():
    """Test that authenticated users can view all courses"""
    token = _create_student_token()
    response = client.get("/courses/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_authenticated_user_view_course_by_id():
    """Test that authenticated users can view course by ID"""
    admin_token = _create_admin_token()
    
    # Create a course
    course_data = {"title": "Test Course", "code": f"TC_{uuid.uuid4().hex[:6]}", "capacity": 30}
    create_resp = client.post("/courses/", json=course_data, headers={"Authorization": f"Bearer {admin_token}"})
    course_id = create_resp.json()["id"]
    
    # View as student
    student_token = _create_student_token()
    response = client.get(f"/courses/{course_id}", headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 200
    assert response.json()["id"] == course_id


def test_unauthenticated_user_cannot_view_courses():
    """Test that unauthenticated users cannot view courses"""
    response = client.get("/courses/")
    assert response.status_code == 401


# ========== COURSE CREATION TESTS (Admin only) ==========

def test_admin_create_course():
    """Test admin can create course"""
    admin_token = _create_admin_token()
    
    course_data = {"title": "Python 101", "code": f"PY_{uuid.uuid4().hex[:6]}", "capacity": 30}
    response = client.post("/courses/", json=course_data, headers={"Authorization": f"Bearer {admin_token}"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == course_data["title"]
    assert data["code"] == course_data["code"]
    assert data["capacity"] == course_data["capacity"]
    assert data["is_active"] is True


def test_student_cannot_create_course():
    """Test student cannot create course"""
    student_token = _create_student_token()
    
    course_data = {"title": "Python 101", "code": f"PY_{uuid.uuid4().hex[:6]}", "capacity": 30}
    response = client.post("/courses/", json=course_data, headers={"Authorization": f"Bearer {student_token}"})
    
    assert response.status_code == 403


def test_duplicate_course_code_rejected():
    """Test that duplicate course code is rejected"""
    admin_token = _create_admin_token()
    code = f"DUP_{uuid.uuid4().hex[:6]}"
    
    course_data = {"title": "Course 1", "code": code, "capacity": 30}
    client.post("/courses/", json=course_data, headers={"Authorization": f"Bearer {admin_token}"})
    
    course_data["title"] = "Course 2"
    response = client.post("/courses/", json=course_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 400


# ========== COURSE UPDATE TESTS (Admin only) ==========

def test_admin_update_course():
    """Test admin can update course"""
    admin_token = _create_admin_token()
    
    # Create course
    course_data = {"title": "Original Title", "code": f"UPD_{uuid.uuid4().hex[:6]}", "capacity": 30}
    create_resp = client.post("/courses/", json=course_data, headers={"Authorization": f"Bearer {admin_token}"})
    course_id = create_resp.json()["id"]
    
    # Update course
    update_data = {"title": "Updated Title", "capacity": 50, "is_active": True}
    response = client.put(f"/courses/{course_id}", json=update_data, headers={"Authorization": f"Bearer {admin_token}"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["capacity"] == update_data["capacity"]


def test_student_cannot_update_course():
    """Test student cannot update course"""
    admin_token = _create_admin_token()
    
    # Create course
    course_data = {"title": "Test", "code": f"TST_{uuid.uuid4().hex[:6]}", "capacity": 30}
    create_resp = client.post("/courses/", json=course_data, headers={"Authorization": f"Bearer {admin_token}"})
    course_id = create_resp.json()["id"]
    
    # Try to update as student
    student_token = _create_student_token()
    update_data = {"title": "Hacked", "capacity": 999, "is_active": True}
    response = client.put(f"/courses/{course_id}", json=update_data, headers={"Authorization": f"Bearer {student_token}"})
    
    assert response.status_code == 403


# ========== COURSE DELETION TESTS (Admin only) ==========

def test_admin_delete_empty_course():
    """Test admin can delete course with no enrollments"""
    admin_token = _create_admin_token()
    
    # Create course
    course_data = {"title": "To Delete", "code": f"DEL_{uuid.uuid4().hex[:6]}", "capacity": 30}
    create_resp = client.post("/courses/", json=course_data, headers={"Authorization": f"Bearer {admin_token}"})
    course_id = create_resp.json()["id"]
    
    # Delete
    response = client.delete(f"/courses/{course_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    
    # Verify deleted
    get_resp = client.get(f"/courses/{course_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert get_resp.status_code == 404


def test_student_cannot_delete_course():
    """Test student cannot delete course"""
    admin_token = _create_admin_token()
    
    # Create course
    course_data = {"title": "Protected", "code": f"PRO_{uuid.uuid4().hex[:6]}", "capacity": 30}
    create_resp = client.post("/courses/", json=course_data, headers={"Authorization": f"Bearer {admin_token}"})
    course_id = create_resp.json()["id"]
    
    # Try to delete as student
    student_token = _create_student_token()
    response = client.delete(f"/courses/{course_id}", headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 403


def test_cannot_delete_course_with_enrollments():
    """Test that courses with enrollments cannot be deleted"""
    admin_token = _create_admin_token()
    student_token = _create_student_token()
    
    # Create course
    course_data = {"title": "Enrolled", "code": f"ENR_{uuid.uuid4().hex[:6]}", "capacity": 30}
    create_resp = client.post("/courses/", json=course_data, headers={"Authorization": f"Bearer {admin_token}"})
    course_id = create_resp.json()["id"]
    
    # Enroll student
    client.post("/enrollments/", json={"course_id": course_id}, headers={"Authorization": f"Bearer {student_token}"})
    
    # Try to delete
    response = client.delete(f"/courses/{course_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 400
    assert "active enrollments" in response.json()["detail"].lower()


# ========== COURSE STUDENTS VIEW TEST (Admin only) ==========

def test_admin_view_course_students():
    """Test admin can view students in course"""
    admin_token = _create_admin_token()
    
    # Create course
    course_data = {"title": "Course", "code": f"STU_{uuid.uuid4().hex[:6]}", "capacity": 30}
    create_resp = client.post("/courses/", json=course_data, headers={"Authorization": f"Bearer {admin_token}"})
    course_id = create_resp.json()["id"]
    
    # Enroll students
    for _ in range(2):
        student_token = _create_student_token()
        client.post("/enrollments/", json={"course_id": course_id}, headers={"Authorization": f"Bearer {student_token}"})
    
    # View students
    response = client.get(f"/courses/{course_id}/students", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == course_id
    assert len(data["students"]) >= 2

