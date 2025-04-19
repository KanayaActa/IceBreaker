import pytest
from fastapi.testclient import TestClient
from bson import ObjectId
from datetime import datetime


@pytest.fixture
def test_result_data(test_user_in_db, test_category_in_db):
    """
    Sample match result data for testing.
    """
    # Create another user to be the loser
    loser_id = str(ObjectId())
    
    # Add the loser to the database
    loser_data = {
        "_id": ObjectId(loser_id),
        "name": "Loser User",
        "intra_name": "luser",
        "email": "loser@example.com",
        "password": "password123",
        "user_image": "https://example.com/loser.jpg",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    return {
        "winner_id": test_user_in_db["_id"],
        "loser_id": loser_id,
        "category_id": test_category_in_db["_id"],
        "winner_point": 21,
        "loser_point": 15,
        "date": datetime.utcnow().isoformat()
    }, loser_data


def test_record_match_result(test_client: TestClient, mock_mongodb, test_result_data):
    """
    Test recording a match result and updating ratings.
    """
    result_data, loser_data = test_result_data
    
    # Add the loser to the database
    mock_mongodb.users.insert_one(loser_data)
    
    response = test_client.post("/api/result/", json=result_data)
    
    assert response.status_code == 201
    data = response.json()
    assert "message" in data
    assert "match_id" in data
    assert "winner" in data
    assert "loser" in data
    assert data["winner"]["id"] == result_data["winner_id"]
    assert data["loser"]["id"] == result_data["loser_id"]
    
    # Check that ratings were created/updated
    winner_rating = mock_mongodb.ratings.find_one({
        "user_id": ObjectId(result_data["winner_id"]),
        "category_id": ObjectId(result_data["category_id"])
    })
    assert winner_rating is not None
    assert winner_rating["rate"] > 1500  # Winner's rating should increase
    
    loser_rating = mock_mongodb.ratings.find_one({
        "user_id": ObjectId(result_data["loser_id"]),
        "category_id": ObjectId(result_data["category_id"])
    })
    assert loser_rating is not None
    assert loser_rating["rate"] < 1500  # Loser's rating should decrease
    
    # Check that match was created
    match = mock_mongodb.matches.find_one({
        "winner_id": ObjectId(result_data["winner_id"]),
        "loser_id": ObjectId(result_data["loser_id"]),
        "category_id": ObjectId(result_data["category_id"])
    })
    assert match is not None
    assert match["winner_point"] == result_data["winner_point"]
    assert match["loser_point"] == result_data["loser_point"]
