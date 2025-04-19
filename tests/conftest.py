import pytest
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient
import mongomock
import asyncio
from bson import ObjectId
from datetime import datetime
from typing import Dict, Any, Generator

from app.database.connection import database as app_database
from main import app


# Mock MongoDB client
@pytest.fixture
def mock_mongodb():
    """
    Replace the MongoDB client with a mock for testing.
    """
    # Create a mongomock client
    client = mongomock.MongoClient()
    db = client["test_db"]
    
    # Store original database
    original_db = app_database
    
    # Replace with mock database
    app_database.client = client
    app_database.database = db
    app_database.users_collection = db.users
    app_database.categories_collection = db.categories
    app_database.ratings_collection = db.ratings
    app_database.matches_collection = db.matches
    
    yield db
    
    # Restore original database
    app_database.client = original_db.client
    app_database.database = original_db.database
    app_database.users_collection = original_db.users_collection
    app_database.categories_collection = original_db.categories_collection
    app_database.ratings_collection = original_db.ratings_collection
    app_database.matches_collection = original_db.matches_collection


@pytest.fixture
def test_client(mock_mongodb) -> Generator[TestClient, None, None]:
    """
    Create a FastAPI TestClient for testing endpoints.
    """
    with TestClient(app) as client:
        yield client


# Test data fixtures
@pytest.fixture
def test_user_data() -> Dict[str, Any]:
    """
    Sample user data for testing.
    """
    return {
        "name": "Test User",
        "intra_name": "tuser",
        "email": "test@example.com",
        "password": "password123",
        "user_image": "https://example.com/test.jpg"
    }


@pytest.fixture
def test_category_data() -> Dict[str, Any]:
    """
    Sample category data for testing.
    """
    return {
        "name": "Test Category",
        "description": "A test category",
        "color": "#FF5733",
        "image": "https://example.com/category.jpg"
    }


@pytest.fixture
def test_user_in_db(mock_mongodb, test_user_data) -> Dict[str, Any]:
    """
    Create a test user in the database.
    """
    user_id = ObjectId()
    user_data = test_user_data.copy()
    user_data["_id"] = user_id
    user_data["created_at"] = datetime.utcnow()
    user_data["updated_at"] = datetime.utcnow()
    
    mock_mongodb.users.insert_one(user_data)
    
    user_data["_id"] = str(user_id)  # Convert ObjectId to string for API responses
    return user_data


@pytest.fixture
def test_category_in_db(mock_mongodb, test_category_data) -> Dict[str, Any]:
    """
    Create a test category in the database.
    """
    category_id = ObjectId()
    category_data = test_category_data.copy()
    category_data["_id"] = category_id
    category_data["created_at"] = datetime.utcnow()
    category_data["updated_at"] = datetime.utcnow()
    
    mock_mongodb.categories.insert_one(category_data)
    
    category_data["_id"] = str(category_id)  # Convert ObjectId to string for API responses
    return category_data
