import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def _random_email(prefix: str):
    return f"{prefix}_{uuid.uuid4().hex[:8]}@example.com"


def _register_and_login(role: str):
    email = _random_email(role)
    password = "TestPass123!"
    user_data = {"name": f"{role.title()} User", "email": email, "password": password, "role": role}
    resp = client.post("/users/register", json=user_data)
    assert resp.status_code in (200, 201)
    login_resp = client.post("/users/login", data={"username": email, "password": password})
    assert login_resp.status_code == 200
    token = login_resp.json().get("access_token")
    assert token
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def student_headers():
    return _register_and_login("student")


@pytest.fixture
def admin_headers():
    return _register_and_login("admin")


def _get_active_course_id():
    resp = client.get("/courses/")
    assert resp.status_code == 200
    for course in resp.json():
        if course.get("is_active"):
            return course["id"]
    pytest.skip("No active course available for tests")


def _create_active_course():
    headers = _register_and_login("admin")
    course_code = f"PY_{uuid.uuid4().hex[:6]}"
    course_data = {
        "title": "Test Course",
        "code": course_code,
        "capacity": 30
    }
    response = client.post("/courses/", json=course_data, headers=headers)
    assert response.status_code == 200
    return response.json()["id"]


def test_student_enroll_in_course(student_headers):
    course_id = _create_active_course()
    resp = client.post("/enrollments/", json={"course_id": course_id}, headers=student_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["course_id"] == course_id
    assert "user_id" in data


def test_student_deregister_from_course(student_headers):
    enrollments = client.get("/enrollments/all", headers=student_headers)
    if not enrollments.json():
        course_id = _create_active_course()
        enroll_resp = client.post("/enrollments/", json={"course_id": course_id}, headers=student_headers)
        assert enroll_resp.status_code == 200
        course_id = enroll_resp.json()["course_id"]
    else:
        course_id = enrollments.json()[0]["course_id"]

    resp = client.delete(f"/enrollments/{course_id}", headers=student_headers)
    assert resp.status_code == 200
    msg = resp.json().get("message", "").lower()
    assert "dereg" in msg or "success" in msg or "removed" in msg


def test_admin_view_all_enrollments(admin_headers):
    resp = client.get("/enrollments/all", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    if data:
        assert "user_id" in data[0] and "course_id" in data[0]


def test_admin_view_course_enrollments(admin_headers):
    course_id = _create_active_course()
    resp = client.get(f"/enrollments/course/{course_id}", headers=admin_headers)
    assert resp.status_code == 200
    for enrollment in resp.json():
        assert enrollment["course_id"] == course_id
        assert "user_id" in enrollment


def test_admin_remove_student_from_course(admin_headers, student_headers):
    course_id = _create_active_course()
    enroll_resp = client.post("/enrollments/", json={"course_id": course_id}, headers=student_headers)
    assert enroll_resp.status_code == 200
    student_id = enroll_resp.json()["user_id"]

    resp = client.delete(f"/enrollments/admin/{course_id}/user/{student_id}", headers=admin_headers)
    assert resp.status_code == 200
    msg = resp.json().get("message", "").lower()
    assert "remove" in msg or "removed" in msg or "success" in msg

def test_admin_bulk_remove_students(admin_headers):
    course_id = _create_active_course()
    
    # Create multiple students and enroll them
    student_ids = []
    for _ in range(3):
        student_headers = _register_and_login("student")
        enroll_resp = client.post("/enrollments/", json={"course_id": course_id}, headers=student_headers)
        assert enroll_resp.status_code == 200
        student_ids.append(enroll_resp.json()["user_id"])
    
    # Bulk remove
    import json
    resp = client.request("DELETE", f"/enrollments/admin/{course_id}", content=json.dumps({"user_ids": student_ids}), headers={**admin_headers, "Content-Type": "application/json"})
    assert resp.status_code == 200
    msg = resp.json().get("message", "").lower()
    assert "removed 3 student" in msg or "success" in msg

