from bson import ObjectId
from datetime import datetime
from typing import List, Optional
from app.database.connection import matches_collection
from app.schemas.match import MatchCreate, MatchUpdate, MatchInDB


async def create_match(match: MatchCreate) -> MatchInDB:
    """
    Create a new match in the database.
    """
    match_dict = match.model_dump()
    match_dict["created_at"] = datetime.utcnow()
    match_dict["updated_at"] = datetime.utcnow()
    
    # Convert string IDs to ObjectId for storage
    match_dict["winner_id"] = ObjectId(match_dict["winner_id"])
    match_dict["loser_id"] = ObjectId(match_dict["loser_id"])
    match_dict["category_id"] = ObjectId(match_dict["category_id"])
    
    result = await matches_collection.insert_one(match_dict)
    
    created_match = await matches_collection.find_one({"_id": result.inserted_id})
    
    # Convert ObjectId back to string for response
    created_match["_id"] = str(created_match["_id"])
    created_match["winner_id"] = str(created_match["winner_id"])
    created_match["loser_id"] = str(created_match["loser_id"])
    created_match["category_id"] = str(created_match["category_id"])
    
    return MatchInDB(**created_match)


async def get_match(match_id: str) -> Optional[MatchInDB]:
    """
    Get a match by ID.
    """
    try:
        match = await matches_collection.find_one({"_id": ObjectId(match_id)})
        if match:
            match["_id"] = str(match["_id"])
            match["winner_id"] = str(match["winner_id"])
            match["loser_id"] = str(match["loser_id"])
            match["category_id"] = str(match["category_id"])
            return MatchInDB(**match)
    except Exception:
        return None
    return None


async def get_user_matches(user_id: str) -> List[MatchInDB]:
    """
    Get all matches for a user (either as winner or loser).
    """
    try:
        cursor = matches_collection.find({
            "$or": [
                {"winner_id": ObjectId(user_id)},
                {"loser_id": ObjectId(user_id)}
            ]
        }).sort("date", -1)
        
        matches = []
        async for match in cursor:
            match["_id"] = str(match["_id"])
            match["winner_id"] = str(match["winner_id"])
            match["loser_id"] = str(match["loser_id"])
            match["category_id"] = str(match["category_id"])
            matches.append(MatchInDB(**match))
        
        return matches
    except Exception:
        return []


async def get_category_matches(category_id: str) -> List[MatchInDB]:
    """
    Get all matches for a category.
    """
    try:
        cursor = matches_collection.find({"category_id": ObjectId(category_id)}).sort("date", -1)
        
        matches = []
        async for match in cursor:
            match["_id"] = str(match["_id"])
            match["winner_id"] = str(match["winner_id"])
            match["loser_id"] = str(match["loser_id"])
            match["category_id"] = str(match["category_id"])
            matches.append(MatchInDB(**match))
        
        return matches
    except Exception:
        return []


async def update_match(match_id: str, match_update: MatchUpdate) -> Optional[MatchInDB]:
    """
    Update a match by ID.
    """
    try:
        match_dict = match_update.model_dump(exclude_unset=True)
        match_dict["updated_at"] = datetime.utcnow()
        
        await matches_collection.update_one(
            {"_id": ObjectId(match_id)},
            {"$set": match_dict}
        )
        
        updated_match = await matches_collection.find_one({"_id": ObjectId(match_id)})
        if updated_match:
            updated_match["_id"] = str(updated_match["_id"])
            updated_match["winner_id"] = str(updated_match["winner_id"])
            updated_match["loser_id"] = str(updated_match["loser_id"])
            updated_match["category_id"] = str(updated_match["category_id"])
            return MatchInDB(**updated_match)
    except Exception:
        return None
    return None
