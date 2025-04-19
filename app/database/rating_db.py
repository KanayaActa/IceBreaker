from bson import ObjectId
from datetime import datetime
from typing import List, Optional
from app.database.connection import ratings_collection
from app.schemas.rating import RatingCreate, RatingUpdate, RatingInDB


async def create_rating(rating: RatingCreate) -> RatingInDB:
    """
    Create a new rating in the database.
    """
    rating_dict = rating.model_dump()
    rating_dict["created_at"] = datetime.utcnow()
    rating_dict["updated_at"] = datetime.utcnow()
    
    # Convert string IDs to ObjectId for storage
    rating_dict["user_id"] = ObjectId(rating_dict["user_id"])
    rating_dict["category_id"] = ObjectId(rating_dict["category_id"])
    
    result = await ratings_collection.insert_one(rating_dict)
    
    created_rating = await ratings_collection.find_one({"_id": result.inserted_id})
    
    # Convert ObjectId back to string for response
    created_rating["_id"] = str(created_rating["_id"])
    created_rating["user_id"] = str(created_rating["user_id"])
    created_rating["category_id"] = str(created_rating["category_id"])
    
    return RatingInDB(**created_rating)


async def get_rating(rating_id: str) -> Optional[RatingInDB]:
    """
    Get a rating by ID.
    """
    try:
        rating = await ratings_collection.find_one({"_id": ObjectId(rating_id)})
        if rating:
            rating["_id"] = str(rating["_id"])
            rating["user_id"] = str(rating["user_id"])
            rating["category_id"] = str(rating["category_id"])
            return RatingInDB(**rating)
    except Exception:
        return None
    return None


async def get_user_category_rating(user_id: str, category_id: str) -> Optional[RatingInDB]:
    """
    Get a rating by user_id and category_id.
    """
    try:
        rating = await ratings_collection.find_one({
            "user_id": ObjectId(user_id),
            "category_id": ObjectId(category_id)
        })
        if rating:
            rating["_id"] = str(rating["_id"])
            rating["user_id"] = str(rating["user_id"])
            rating["category_id"] = str(rating["category_id"])
            return RatingInDB(**rating)
    except Exception:
        return None
    return None


async def update_rating(rating_id: str, rating_update: RatingUpdate) -> Optional[RatingInDB]:
    """
    Update a rating by ID.
    """
    try:
        rating_dict = rating_update.model_dump(exclude_unset=True)
        rating_dict["updated_at"] = datetime.utcnow()
        
        await ratings_collection.update_one(
            {"_id": ObjectId(rating_id)},
            {"$set": rating_dict}
        )
        
        updated_rating = await ratings_collection.find_one({"_id": ObjectId(rating_id)})
        if updated_rating:
            updated_rating["_id"] = str(updated_rating["_id"])
            updated_rating["user_id"] = str(updated_rating["user_id"])
            updated_rating["category_id"] = str(updated_rating["category_id"])
            return RatingInDB(**updated_rating)
    except Exception:
        return None
    return None


async def get_category_rankings(category_id: str) -> List[RatingInDB]:
    """
    Get all ratings for a category, sorted by rate in descending order.
    """
    try:
        cursor = ratings_collection.find({"category_id": ObjectId(category_id)}).sort("rate", -1)
        
        ratings = []
        async for rating in cursor:
            rating["_id"] = str(rating["_id"])
            rating["user_id"] = str(rating["user_id"])
            rating["category_id"] = str(rating["category_id"])
            ratings.append(RatingInDB(**rating))
        
        return ratings
    except Exception:
        return []
