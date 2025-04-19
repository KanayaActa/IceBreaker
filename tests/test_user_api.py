import pytest
from fastapi.testclient import TestClient
from bson import ObjectId


def test_create_user(test_client: TestClient):
    """
    Test creating a new user.
    """
    user_data = {
        "name": "New User",
        "intra_name": "nuser",
        "email": "new@example.com",
        "password": "securepass123",
        "user_image": "https://example.com/new.jpg"
    }
    
    response = test_client.post("/api/user/", json=user_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == user_data["name"]
    assert data["intra_name"] == user_data["intra_name"]
    assert data["email"] == user_data["email"]
    assert "password" not in data  # Password should not be returned
    assert "_id" in data  # Should have an ID


def test_get_user(test_client: TestClient, test_user_in_db):
    """
    Test getting a user by ID.
    """
    user_id = test_user_in_db["_id"]
    
    response = test_client.get(f"/api/user/{user_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == test_user_in_db["name"]
    assert data["intra_name"] == test_user_in_db["intra_name"]
    assert data["email"] == test_user_in_db["email"]
    assert "password" not in data  # Password should not be returned


def test_get_nonexistent_user(test_client: TestClient):
    """
    Test getting a user that doesn't exist.
    """
    nonexistent_id = str(ObjectId())
    
    response = test_client.get(f"/api/user/{nonexistent_id}")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_update_user(test_client: TestClient, test_user_in_db):
    """
    Test updating a user.
    """
    user_id = test_user_in_db["_id"]
    update_data = {
        "name": "Updated Name",
        "email": "updated@example.com"
    }
    
    response = test_client.put(f"/api/user/{user_id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["email"] == update_data["email"]
    assert data["intra_name"] == test_user_in_db["intra_name"]  # Should not change


def test_search_users(test_client: TestClient, test_user_in_db):
    """
    Test searching for users.
    """
    # Search by partial name
    search_term = test_user_in_db["name"][:3]
    
    response = test_client.get(f"/api/user/?key={search_term}")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any(user["_id"] == test_user_in_db["_id"] for user in data)
    
    # Search by partial intra_name
    search_term = test_user_in_db["intra_name"][:3]
    
    response = test_client.get(f"/api/user/?key={search_term}")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any(user["_id"] == test_user_in_db["_id"] for user in data)
