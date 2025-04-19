import pytest
from fastapi.testclient import TestClient
from bson import ObjectId
from datetime import datetime


@pytest.fixture
def test_match_data(test_user_in_db, test_category_in_db):
    """
    Sample match data for testing.
    """
    # Create another user to be the loser
    loser_id = str(ObjectId())
    
    return {
        "winner_id": test_user_in_db["_id"],
        "loser_id": loser_id,
        "category_id": test_category_in_db["_id"],
        "winner_point": 21,
        "loser_point": 15,
        "date": datetime.utcnow().isoformat()
    }


@pytest.fixture
def test_match_in_db(mock_mongodb, test_match_data):
    """
    Create a test match in the database.
    """
    match_id = ObjectId()
    match_data = test_match_data.copy()
    match_data["_id"] = match_id
    match_data["created_at"] = datetime.utcnow()
    match_data["updated_at"] = datetime.utcnow()
    
    # Convert string IDs to ObjectId for storage
    match_data["winner_id"] = ObjectId(match_data["winner_id"])
    match_data["loser_id"] = ObjectId(match_data["loser_id"])
    match_data["category_id"] = ObjectId(match_data["category_id"])
    
    mock_mongodb.matches.insert_one(match_data)
    
    # Convert back to strings for API responses
    result = match_data.copy()
    result["_id"] = str(match_id)
    result["winner_id"] = str(match_data["winner_id"])
    result["loser_id"] = str(match_data["loser_id"])
    result["category_id"] = str(match_data["category_id"])
    return result


def test_create_match(test_client: TestClient, test_match_data):
    """
    Test creating a new match.
    """
    response = test_client.post("/api/match/", json=test_match_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["winner_id"] == test_match_data["winner_id"]
    assert data["loser_id"] == test_match_data["loser_id"]
    assert data["category_id"] == test_match_data["category_id"]
    assert data["winner_point"] == test_match_data["winner_point"]
    assert data["loser_point"] == test_match_data["loser_point"]
    assert "_id" in data


def test_get_match(test_client: TestClient, test_match_in_db):
    """
    Test getting a match by ID.
    """
    match_id = test_match_in_db["_id"]
    
    response = test_client.get(f"/api/match/{match_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["winner_id"] == test_match_in_db["winner_id"]
    assert data["loser_id"] == test_match_in_db["loser_id"]
    assert data["category_id"] == test_match_in_db["category_id"]
    assert data["winner_point"] == test_match_in_db["winner_point"]
    assert data["loser_point"] == test_match_in_db["loser_point"]


def test_get_user_matches(test_client: TestClient, test_match_in_db):
    """
    Test getting all matches for a user.
    """
    user_id = test_match_in_db["winner_id"]
    
    response = test_client.get(f"/api/match/user/{user_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(match["_id"] == test_match_in_db["_id"] for match in data)


def test_get_category_matches(test_client: TestClient, test_match_in_db):
    """
    Test getting all matches for a category.
    """
    category_id = test_match_in_db["category_id"]
    
    response = test_client.get(f"/api/match/category/{category_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(match["_id"] == test_match_in_db["_id"] for match in data)
