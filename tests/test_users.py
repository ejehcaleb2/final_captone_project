from fastapi.testclient import TestClient
import uuid
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.main import app

client = TestClient(app)


def _random_email(prefix: str):
    return f"{prefix}_{uuid.uuid4().hex[:8]}@example.com"


# ========== USER REGISTRATION & LOGIN TESTS ==========

def test_register_student_success():
    """Test successful student registration"""
    user_data = {
        "name": "Test Student",
        "email": _random_email("student"),
        "password": "testpassword123",
        "role": "student"
    }
    response = client.post("/users/register", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["role"] == "student"
    assert data["is_active"] is True
    assert "id" in data


def test_register_admin_success():
    """Test successful admin registration"""
    user_data = {
        "name": "Test Admin",
        "email": _random_email("admin"),
        "password": "adminpassword123",
        "role": "admin"
    }
    response = client.post("/users/register", json=user_data)
    assert response.status_code == 200
    assert response.json()["role"] == "admin"


def test_register_duplicate_email():
    """Test that duplicate email registration fails"""
    email = _random_email("duplicate")
    user_data = {
        "name": "First User",
        "email": email,
        "password": "password123",
        "role": "student"
    }
    
    client.post("/users/register", json=user_data)
    response = client.post("/users/register", json=user_data)
    assert response.status_code == 400


def test_register_invalid_role():
    """Test that invalid role is rejected"""
    user_data = {
        "name": "Invalid User",
        "email": _random_email("invalid"),
        "password": "password123",
        "role": "superuser"
    }
    response = client.post("/users/register", json=user_data)
    assert response.status_code == 400


def test_login_success():
    """Test successful login"""
    email = _random_email("login_test")
    password = "correctpassword123"
    user_data = {
        "name": "Login Test User",
        "email": email,
        "password": password,
        "role": "student"
    }
    
    client.post("/users/register", json=user_data)
    
    response = client.post("/users/login", data={"username": email, "password": password})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password():
    """Test login with wrong password fails"""
    email = _random_email("wrong_pwd")
    user_data = {
        "name": "Wrong Password User",
        "email": email,
        "password": "correctpassword",
        "role": "student"
    }
    
    client.post("/users/register", json=user_data)
    
    response = client.post("/users/login", data={"username": email, "password": "wrongpassword"})
    assert response.status_code == 400


# ========== USER PROFILE TESTS ==========

def test_get_current_user_success():
    """Test getting current user profile"""
    email = _random_email("profile_test")
    user_data = {
        "name": "Profile Test User",
        "email": email,
        "password": "password123",
        "role": "student"
    }
    
    client.post("/users/register", json=user_data)
    login_resp = client.post("/users/login", data={"username": email, "password": "password123"})
    token = login_resp.json()["access_token"]
    
    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email


def test_get_current_user_unauthorized():
    """Test that unauthorized request fails"""
    response = client.get("/users/me")
    assert response.status_code == 401


# ========== ADMIN TESTS ==========

def test_admin_get_all_students():
    """Test admin can get all students"""
    admin_email = _random_email("admin")
    admin_data = {"name": "Admin", "email": admin_email, "password": "pass123", "role": "admin"}
    client.post("/users/register", json=admin_data)
    admin_login = client.post("/users/login", data={"username": admin_email, "password": "pass123"})
    admin_token = admin_login.json()["access_token"]
    
    response = client.get("/users/students", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200


def test_student_cannot_get_all_students():
    """Test that student cannot get all students"""
    student_email = _random_email("student")
    student_data = {"name": "Student", "email": student_email, "password": "pass123", "role": "student"}
    client.post("/users/register", json=student_data)
    student_login = client.post("/users/login", data={"username": student_email, "password": "pass123"})
    student_token = student_login.json()["access_token"]
    
    response = client.get("/users/students", headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 403


def test_admin_delete_student():
    """Test admin can delete student"""
    admin_email = _random_email("admin")
    admin_data = {"name": "Admin", "email": admin_email, "password": "pass123", "role": "admin"}
    client.post("/users/register", json=admin_data)
    admin_login = client.post("/users/login", data={"username": admin_email, "password": "pass123"})
    admin_token = admin_login.json()["access_token"]
    
    student_email = _random_email("student")
    student_data = {"name": "Student", "email": student_email, "password": "pass123", "role": "student"}
    student_resp = client.post("/users/register", json=student_data)
    student_id = student_resp.json()["id"]
    
    delete_resp = client.delete(f"/users/{student_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert delete_resp.status_code == 200
