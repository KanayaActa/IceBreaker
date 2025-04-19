import pytest
from fastapi.testclient import TestClient
from bson import ObjectId
from datetime import datetime


@pytest.fixture
def setup_rankings(mock_mongodb, test_user_in_db, test_category_in_db):
    """
    Set up multiple users with ratings for testing rankings.
    """
    category_id = ObjectId(test_category_in_db["_id"])
    user1_id = ObjectId(test_user_in_db["_id"])
    
    # Create additional users
    user2_data = {
        "_id": ObjectId(),
        "name": "User Two",
        "intra_name": "user2",
        "email": "user2@example.com",
        "password": "password123",
        "user_image": "https://example.com/user2.jpg",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    user3_data = {
        "_id": ObjectId(),
        "name": "User Three",
        "intra_name": "user3",
        "email": "user3@example.com",
        "password": "password123",
        "user_image": "https://example.com/user3.jpg",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Insert users
    mock_mongodb.users.insert_one(user2_data)
    mock_mongodb.users.insert_one(user3_data)
    
    # Create ratings for each user
    ratings = [
        {
            "_id": ObjectId(),
            "user_id": user1_id,
            "category_id": category_id,
            "rate": 1800.0,
            "date": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "user_id": user2_data["_id"],
            "category_id": category_id,
            "rate": 1600.0,
            "date": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "user_id": user3_data["_id"],
            "category_id": category_id,
            "rate": 1400.0,
            "date": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    # Insert ratings
    mock_mongodb.ratings.insert_many(ratings)
    
    return {
        "category_id": str(category_id),
        "users": [
            {"id": str(user1_id), "name": test_user_in_db["name"], "rate": 1800.0},
            {"id": str(user2_data["_id"]), "name": user2_data["name"], "rate": 1600.0},
            {"id": str(user3_data["_id"]), "name": user3_data["name"], "rate": 1400.0}
        ]
    }


def test_get_category_ranking(test_client: TestClient, setup_rankings):
    """
    Test getting rankings for a category.
    """
    category_id = setup_rankings["category_id"]
    
    response = test_client.get(f"/api/ranking/category/{category_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3
    
    # Check that rankings are in descending order by rating
    assert data[0]["rank"] == 1
    assert data[1]["rank"] == 2
    assert data[2]["rank"] == 3
    
    assert data[0]["rating"] > data[1]["rating"]
    assert data[1]["rating"] > data[2]["rating"]
    
    # Check that the top user is the one with the highest rating
    assert data[0]["user_id"] == setup_rankings["users"][0]["id"]
    assert data[0]["rating"] == setup_rankings["users"][0]["rate"]
    
    # Check that the second user is the one with the second highest rating
    assert data[1]["user_id"] == setup_rankings["users"][1]["id"]
    assert data[1]["rating"] == setup_rankings["users"][1]["rate"]
    
    # Check that the third user is the one with the lowest rating
    assert data[2]["user_id"] == setup_rankings["users"][2]["id"]
    assert data[2]["rating"] == setup_rankings["users"][2]["rate"]
