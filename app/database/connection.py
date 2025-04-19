from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.database import Database
from pymongo.collection import Collection
import os
from dotenv import load_dotenv
from decouple import config

# # Load environment variables
# load_dotenv()

# # MongoDB connection string
# MONGO_API_KEY = os.getenv("MONGO_API_KEY", "mongodb://localhost:27017")
# DB_NAME = os.getenv("DB_NAME", "icebreaker_db")
MONGO_API_KEY = config("MONGO_API_KEY")
DB_NAME = config("DB_NAME")

# Database client
client = AsyncIOMotorClient(MONGO_API_KEY)
database = client[DB_NAME]

# Collections
users_collection: Collection = database.users
categories_collection: Collection = database.categories
ratings_collection: Collection = database.ratings
matches_collection: Collection = database.matches

async def get_database() -> Database:
    """
    Get database connection.
    """
    return database
