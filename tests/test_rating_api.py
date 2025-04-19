import pytest
from fastapi.testclient import TestClient
from bson import ObjectId
from datetime import datetime


@pytest.fixture
def test_rating_data(test_user_in_db, test_category_in_db):
    """
    Sample rating data for testing.
    """
    return {
        "user_id": test_user_in_db["_id"],
        "category_id": test_category_in_db["_id"],
        "rate": 1500.0,
        "date": datetime.utcnow().isoformat()
    }


@pytest.fixture
def test_rating_in_db(mock_mongodb, test_rating_data):
    """
    Create a test rating in the database.
    """
    rating_id = ObjectId()
    rating_data = test_rating_data.copy()
    rating_data["_id"] = rating_id
    rating_data["created_at"] = datetime.utcnow()
    rating_data["updated_at"] = datetime.utcnow()
    
    # Convert string IDs to ObjectId for storage
    rating_data["user_id"] = ObjectId(rating_data["user_id"])
    rating_data["category_id"] = ObjectId(rating_data["category_id"])
    
    mock_mongodb.ratings.insert_one(rating_data)
    
    # Convert back to strings for API responses
    result = rating_data.copy()
    result["_id"] = str(rating_id)
    result["user_id"] = str(rating_data["user_id"])
    result["category_id"] = str(rating_data["category_id"])
    return result


def test_create_rating(test_client: TestClient, test_rating_data):
    """
    Test creating a new rating.
    """
    response = test_client.post("/api/rating/", json=test_rating_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == test_rating_data["user_id"]
    assert data["category_id"] == test_rating_data["category_id"]
    assert data["rate"] == test_rating_data["rate"]
    assert "_id" in data


def test_get_rating(test_client: TestClient, test_rating_in_db):
    """
    Test getting a rating by ID.
    """
    rating_id = test_rating_in_db["_id"]
    
    response = test_client.get(f"/api/rating/{rating_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == test_rating_in_db["user_id"]
    assert data["category_id"] == test_rating_in_db["category_id"]
    assert data["rate"] == test_rating_in_db["rate"]


def test_get_user_category_rating(test_client: TestClient, test_rating_in_db):
    """
    Test getting a rating for a specific user and category.
    """
    user_id = test_rating_in_db["user_id"]
    category_id = test_rating_in_db["category_id"]
    
    response = test_client.get(f"/api/rating/user/{user_id}/category/{category_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_id
    assert data["category_id"] == category_id
    assert data["rate"] == test_rating_in_db["rate"]


def test_update_rating(test_client: TestClient, test_rating_in_db):
    """
    Test updating a rating.
    """
    rating_id = test_rating_in_db["_id"]
    update_data = {
        "rate": 1600.0
    }
    
    response = test_client.put(f"/api/rating/{rating_id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["rate"] == update_data["rate"]
    assert data["user_id"] == test_rating_in_db["user_id"]
    assert data["category_id"] == test_rating_in_db["category_id"]
