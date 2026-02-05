from fastapi.testclient import TestClient
import uuid
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.main import app  # Adjust import based on your app structure

client = TestClient(app)

def _random_email(prefix: str):
    return f"{prefix}_{uuid.uuid4().hex[:8]}@example.com"


def test_user_registration_and_login():
    # 1️⃣ Register a new user
    user_data = {
        "name": "Test User",
        "email": _random_email("testuser"),
        "password": "testpassword",
        "role": "student"
    }
    response = client.post("/users/register", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert "id" in data

    # 2️⃣ Attempt login with correct credentials
    login_data = {
        "username": user_data["email"],  # OAuth2PasswordRequestForm uses 'username'
        "password": user_data["password"]
    }
    response = client.post("/users/login", data=login_data)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    # 3️⃣ Attempt login with wrong password
    wrong_login = {
        "username": user_data["email"],
        "password": "wrongpassword"
    }
    response = client.post("/users/login", data=wrong_login)
    assert response.status_code == 400

def test_admin_delete_student():
    # Create admin
    admin_data = {
        "name": "Admin User",
        "email": _random_email("admin"),
        "password": "adminpass",
        "role": "admin"
    }
    client.post("/users/register", json=admin_data)
    login_resp = client.post("/users/login", data={"username": admin_data["email"], "password": admin_data["password"]})
    admin_token = login_resp.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Create student
    student_data = {
        "name": "Student User",
        "email": _random_email("student"),
        "password": "studentpass",
        "role": "student"
    }
    register_resp = client.post("/users/register", json=student_data)
    student_id = register_resp.json()["id"]

    # Delete student
    delete_resp = client.delete(f"/users/{student_id}", headers=admin_headers)
    assert delete_resp.status_code == 200
    assert delete_resp.json()["message"] == "Student deleted successfully"

    # Verify student is deleted
    get_resp = client.get("/users/me", headers={"Authorization": f"Bearer {admin_token}"})  # This should fail or something, but anyway
    # Actually, to check, perhaps try to login or get students
    students_resp = client.get("/users/students", headers=admin_headers)
    student_ids = [s["id"] for s in students_resp.json()]
    assert student_id not in student_ids
