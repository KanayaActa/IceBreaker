from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from app.database import rating_db, user_db
from app.schemas.rating import RatingResponse
from bson.objectid import ObjectId
from bson.errors import InvalidId

router = APIRouter(prefix="/api/ranking", tags=["rankings"])


@router.get("/category/{category_id}")
async def get_category_ranking(category_id: str):
    """
    Get ranking for a specific category.
    """
    try:
        ObjectId(category_id)  # Validate ObjectId format
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid category ID format")
    
    # Get all ratings for the category sorted by rate
    ratings = await rating_db.get_category_rankings(category_id)
    
    # Prepare ranking with user details
    ranking = []
    rank = 1
    
    for rating in ratings:
        user = await user_db.get_user(rating.user_id)
        if user:
            ranking.append({
                "rank": rank,
                "user_id": rating.user_id,
                "name": user.name,
                "intra_name": user.intra_name,
                "user_image": user.user_image,
                "rating": rating.rate,
                "last_updated": rating.date
            })
            rank += 1
    
    return ranking
