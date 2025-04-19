import pytest
from fastapi.testclient import TestClient
from app.database import user_db


def test_signup(test_client: TestClient):
    """
    Test user registration.
    """
    user_data = {
        "name": "Auth Test User",
        "intra_name": "authuser",
        "email": "auth@example.com",
        "password": "securepass123",
        "user_image": "https://example.com/auth.jpg"
    }
    
    response = test_client.post("/api/auth/signup", json=user_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == user_data["name"]
    assert data["intra_name"] == user_data["intra_name"]
    assert data["email"] == user_data["email"]
    assert "password" not in data  # Password should not be returned
    assert "id" in data  # Should have an ID


def test_signup_duplicate_email(test_client: TestClient, test_user_in_db):
    """
    Test user registration with duplicate email.
    """
    user_data = {
        "name": "Duplicate Email User",
        "intra_name": "dupuser",
        "email": test_user_in_db["email"],  # Using existing email
        "password": "securepass123",
        "user_image": "https://example.com/dup.jpg"
    }
    
    response = test_client.post("/api/auth/signup", json=user_data)
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_signin_success(test_client: TestClient, test_user_in_db, monkeypatch):
    """
    Test successful user authentication.
    """
    # Monkeypatch the verify_password function to always return True for testing
    monkeypatch.setattr(user_db, "verify_password", lambda plain_password, hashed_password: True)
    
    signin_data = {
        "email": test_user_in_db["email"],
        "password": "password123"
    }
    
    response = test_client.post("/api/auth/signin", json=signin_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_signin_invalid_credentials(test_client: TestClient, test_user_in_db):
    """
    Test authentication with invalid credentials.
    """
    signin_data = {
        "email": test_user_in_db["email"],
        "password": "wrongpassword"
    }
    
    response = test_client.post("/api/auth/signin", json=signin_data)
    
    assert response.status_code == 401
    assert "incorrect email or password" in response.json()["detail"].lower()


def test_signin_nonexistent_user(test_client: TestClient):
    """
    Test authentication with non-existent user.
    """
    signin_data = {
        "email": "nonexistent@example.com",
        "password": "password123"
    }
    
    response = test_client.post("/api/auth/signin", json=signin_data)
    
    assert response.status_code == 401
    assert "incorrect email or password" in response.json()["detail"].lower()
