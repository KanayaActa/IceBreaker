import pytest
from fastapi.testclient import TestClient
from bson import ObjectId


def test_create_category(test_client: TestClient):
    """
    Test creating a new category.
    """
    category_data = {
        "name": "New Category",
        "description": "A new test category",
        "color": "#00FF00",
        "image": "https://example.com/new-category.jpg"
    }
    
    response = test_client.post("/api/category/", json=category_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == category_data["name"]
    assert data["description"] == category_data["description"]
    assert data["color"] == category_data["color"]
    assert data["image"] == category_data["image"]
    assert "_id" in data  # Should have an ID


def test_get_category(test_client: TestClient, test_category_in_db):
    """
    Test getting a category by ID.
    """
    category_id = test_category_in_db["_id"]
    
    response = test_client.get(f"/api/category/{category_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == test_category_in_db["name"]
    assert data["description"] == test_category_in_db["description"]
    assert data["color"] == test_category_in_db["color"]
    assert data["image"] == test_category_in_db["image"]


def test_get_nonexistent_category(test_client: TestClient):
    """
    Test getting a category that doesn't exist.
    """
    nonexistent_id = str(ObjectId())
    
    response = test_client.get(f"/api/category/{nonexistent_id}")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_update_category(test_client: TestClient, test_category_in_db):
    """
    Test updating a category.
    """
    category_id = test_category_in_db["_id"]
    update_data = {
        "name": "Updated Category",
        "color": "#0000FF"
    }
    
    response = test_client.put(f"/api/category/{category_id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["color"] == update_data["color"]
    assert data["description"] == test_category_in_db["description"]  # Should not change


def test_get_all_categories(test_client: TestClient, test_category_in_db):
    """
    Test getting all categories.
    """
    response = test_client.get("/api/category/")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(category["_id"] == test_category_in_db["_id"] for category in data)
