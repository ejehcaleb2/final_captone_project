import uuid
from fastapi.testclient import TestClient
from app.main import app
import json

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


def _create_course():
    """Helper to create course and return course ID"""
    admin_token = _create_admin_token()
    course_data = {"title": "Test Course", "code": f"TST_{uuid.uuid4().hex[:6]}", "capacity": 30}
    create_resp = client.post("/courses/", json=course_data, headers={"Authorization": f"Bearer {admin_token}"})
    return create_resp.json()["id"]


# ========== ENROLLMENT CREATION TESTS ==========

def test_student_enroll_in_course():
    """Test student can enroll in course"""
    student_token = _create_student_token()
    course_id = _create_course()
    
    response = client.post("/enrollments/", json={"course_id": course_id}, headers={"Authorization": f"Bearer {student_token}"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["course_id"] == course_id
    assert "user_id" in data
    assert "id" in data


def test_student_cannot_enroll_twice():
    """Test student cannot enroll in same course twice"""
    student_token = _create_student_token()
    course_id = _create_course()
    
    # First enrollment
    response1 = client.post("/enrollments/", json={"course_id": course_id}, headers={"Authorization": f"Bearer {student_token}"})
    assert response1.status_code == 200
    
    # Second enrollment attempt
    response2 = client.post("/enrollments/", json={"course_id": course_id}, headers={"Authorization": f"Bearer {student_token}"})
    assert response2.status_code == 400
    assert "already enrolled" in response2.json()["detail"].lower()


def test_admin_cannot_enroll_in_course():
    """Test admin cannot enroll in course"""
    admin_token = _create_admin_token()
    course_id = _create_course()
    
    response = client.post("/enrollments/", json={"course_id": course_id}, headers={"Authorization": f"Bearer {admin_token}"})
    
    assert response.status_code == 403


def test_enroll_in_nonexistent_course():
    """Test enrollment in non-existent course fails"""
    student_token = _create_student_token()
    
    response = client.post("/enrollments/", json={"course_id": 99999}, headers={"Authorization": f"Bearer {student_token}"})
    
    assert response.status_code == 400


def test_enroll_in_inactive_course():
    """Test enrollment in inactive course fails"""
    admin_token = _create_admin_token()
    student_token = _create_student_token()
    
    # Create and deactivate course
    course_id = _create_course()
    client.put(f"/courses/{course_id}", json={"is_active": False}, headers={"Authorization": f"Bearer {admin_token}"})
    
    # Try to enroll
    response = client.post("/enrollments/", json={"course_id": course_id}, headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 400


def test_cannot_enroll_when_course_full():
    """Test enrollment fails when course is at capacity"""
    # Create course with capacity 1
    admin_token = _create_admin_token()
    course_data = {"title": "Small Class", "code": f"SML_{uuid.uuid4().hex[:6]}", "capacity": 1}
    create_resp = client.post("/courses/", json=course_data, headers={"Authorization": f"Bearer {admin_token}"})
    course_id = create_resp.json()["id"]
    
    # First student enrolls
    student1_token = _create_student_token()
    response1 = client.post("/enrollments/", json={"course_id": course_id}, headers={"Authorization": f"Bearer {student1_token}"})
    assert response1.status_code == 200
    
    # Second student tries to enroll
    student2_token = _create_student_token()
    response2 = client.post("/enrollments/", json={"course_id": course_id}, headers={"Authorization": f"Bearer {student2_token}"})
    assert response2.status_code == 400
    assert "full" in response2.json()["detail"].lower()


# ========== ENROLLMENT DEREGISTRATION TESTS ==========

def test_student_deregister_from_course():
    """Test student can deregister from course"""
    student_token = _create_student_token()
    course_id = _create_course()
    
    # Enroll
    client.post("/enrollments/", json={"course_id": course_id}, headers={"Authorization": f"Bearer {student_token}"})
    
    # Deregister
    response = client.delete(f"/enrollments/{course_id}", headers={"Authorization": f"Bearer {student_token}"})
    
    assert response.status_code == 200
    assert "dereg" in response.json()["message"].lower() or "success" in response.json()["message"].lower()


def test_admin_cannot_deregister_from_course():
    """Test admin cannot deregister (only students can)"""
    admin_token = _create_admin_token()
    course_id = _create_course()
    
    response = client.delete(f"/enrollments/{course_id}", headers={"Authorization": f"Bearer {admin_token}"})
    
    assert response.status_code == 403


def test_deregister_nonexistent_enrollment():
    """Test deregistering from non-existent enrollment fails"""
    student_token = _create_student_token()
    
    response = client.delete(f"/enrollments/99999", headers={"Authorization": f"Bearer {student_token}"})
    
    assert response.status_code == 404


# ========== ENROLLMENT VIEWING TESTS ==========

def test_student_view_own_enrollments():
    """Test student can view their own enrollments"""
    student_token = _create_student_token()
    course_id = _create_course()
    
    # Enroll
    client.post("/enrollments/", json={"course_id": course_id}, headers={"Authorization": f"Bearer {student_token}"})
    
    # View own enrollments
    response = client.get("/enrollments/my-enrollments", headers={"Authorization": f"Bearer {student_token}"})
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(e["course_id"] == course_id for e in data)


def test_student_view_specific_enrollment():
    """Test student can view specific enrollment by ID"""
    student_token = _create_student_token()
    course_id = _create_course()
    
    # Enroll
    enroll_resp = client.post("/enrollments/", json={"course_id": course_id}, headers={"Authorization": f"Bearer {student_token}"})
    enrollment_id = enroll_resp.json()["id"]
    
    # View specific enrollment
    response = client.get(f"/enrollments/{enrollment_id}", headers={"Authorization": f"Bearer {student_token}"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == enrollment_id


def test_student_cannot_view_other_enrollments():
    """Test student cannot view other student's enrollment"""
    admin_token = _create_admin_token()
    student1_token = _create_student_token()
    student2_token = _create_student_token()
    
    course_id = _create_course()
    
    # Student 1 enrolls
    enroll_resp = client.post("/enrollments/", json={"course_id": course_id}, headers={"Authorization": f"Bearer {student1_token}"})
    enrollment_id = enroll_resp.json()["id"]
    
    # Student 2 tries to view Student 1's enrollment
    response = client.get(f"/enrollments/{enrollment_id}", headers={"Authorization": f"Bearer {student2_token}"})
    
    assert response.status_code == 403


def test_admin_view_enrollment_by_id():
    """Test admin can view any enrollment by ID"""
    student_token = _create_student_token()
    admin_token = _create_admin_token()
    
    course_id = _create_course()
    
    # Student enrolls
    enroll_resp = client.post("/enrollments/", json={"course_id": course_id}, headers={"Authorization": f"Bearer {student_token}"})
    enrollment_id = enroll_resp.json()["id"]
    
    # Admin views enrollment
    response = client.get(f"/enrollments/{enrollment_id}", headers={"Authorization": f"Bearer {admin_token}"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == enrollment_id


def test_admin_view_all_enrollments():
    """Test admin can view all enrollments"""
    admin_token = _create_admin_token()
    
    response = client.get("/enrollments/all", headers={"Authorization": f"Bearer {admin_token}"})
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_student_cannot_view_all_enrollments():
    """Test student cannot view all enrollments"""
    student_token = _create_student_token()
    
    response = client.get("/enrollments/all", headers={"Authorization": f"Bearer {student_token}"})
    
    assert response.status_code == 403


def test_admin_view_course_enrollments():
    """Test admin can view enrollments by course"""
    admin_token = _create_admin_token()
    student_token = _create_student_token()
    
    course_id = _create_course()
    
    # Student enrolls
    client.post("/enrollments/", json={"course_id": course_id}, headers={"Authorization": f"Bearer {student_token}"})
    
    # Admin views course enrollments
    response = client.get(f"/enrollments/course/{course_id}", headers={"Authorization": f"Bearer {admin_token}"})
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert all(e["course_id"] == course_id for e in data)


def test_student_cannot_view_course_enrollments():
    """Test student cannot view all course enrollments"""
    student_token = _create_student_token()
    course_id = _create_course()
    
    response = client.get(f"/enrollments/course/{course_id}", headers={"Authorization": f"Bearer {student_token}"})
    
    assert response.status_code == 403


# ========== ADMIN ENROLLMENT MANAGEMENT TESTS ==========

def test_admin_remove_student_from_course():
    """Test admin can remove student from course"""
    admin_token = _create_admin_token()
    student_token = _create_student_token()
    
    course_id = _create_course()
    
    # Student enrolls
    enroll_resp = client.post("/enrollments/", json={"course_id": course_id}, headers={"Authorization": f"Bearer {student_token}"})
    student_id = enroll_resp.json()["user_id"]
    
    # Admin removes student
    response = client.delete(f"/enrollments/admin/{course_id}/user/{student_id}", headers={"Authorization": f"Bearer {admin_token}"})
    
    assert response.status_code == 200
    assert "removed" in response.json()["message"].lower() or "success" in response.json()["message"].lower()


def test_admin_bulk_remove_students():
    """Test admin can bulk remove students"""
    admin_token = _create_admin_token()
    course_id = _create_course()
    
    # Enroll 3 students
    student_ids = []
    for _ in range(3):
        student_token = _create_student_token()
        enroll_resp = client.post("/enrollments/", json={"course_id": course_id}, headers={"Authorization": f"Bearer {student_token}"})
        student_ids.append(enroll_resp.json()["user_id"])
    
    # Bulk remove
    response = client.request("DELETE", f"/enrollments/admin/{course_id}", json={"user_ids": student_ids}, headers={"Authorization": f"Bearer {admin_token}"})
    
    assert response.status_code == 200
    assert "3" in response.json()["message"]

