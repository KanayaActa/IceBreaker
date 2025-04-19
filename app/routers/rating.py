from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas.rating import RatingCreate, RatingUpdate, RatingResponse
from app.database import rating_db
from bson.objectid import ObjectId
from bson.errors import InvalidId

router = APIRouter(prefix="/api/rating", tags=["ratings"])


# @router.post("/", response_model=RatingResponse)
# async def create_rating(rating: RatingCreate):
#     """
#     Create a new rating.
#     """
#     created_rating = await rating_db.create_rating(rating)
#     return created_rating


@router.get("/{rating_id}", response_model=RatingResponse)
async def get_rating(rating_id: str):
    """
    Get rating details by ID.
    """
    try:
        ObjectId(rating_id)  # Validate ObjectId format
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid rating ID format")
    
    rating = await rating_db.get_rating(rating_id)
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    return rating


@router.get("/user/{user_id}/category/{category_id}", response_model=RatingResponse)
async def get_user_category_rating(user_id: str, category_id: str):
    """
    Get rating for a specific user and category.
    """
    try:
        ObjectId(user_id)  # Validate ObjectId format
        ObjectId(category_id)  # Validate ObjectId format
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    rating = await rating_db.get_user_category_rating(user_id, category_id)
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    return rating


# @router.put("/{rating_id}", response_model=RatingResponse)
# async def update_rating(rating_id: str, rating_update: RatingUpdate):
#     """
#     Update rating details.
#     """
#     try:
#         ObjectId(rating_id)  # Validate ObjectId format
#     except InvalidId:
#         raise HTTPException(status_code=400, detail="Invalid rating ID format")
    
#     updated_rating = await rating_db.update_rating(rating_id, rating_update)
#     if not updated_rating:
#         raise HTTPException(status_code=404, detail="Rating not found")
#     return updated_rating
