from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas.match import MatchCreate, MatchUpdate, MatchResponse
from app.database import match_db
from bson.objectid import ObjectId
from bson.errors import InvalidId

router = APIRouter(prefix="/api/match", tags=["matches"])


@router.post("/", response_model=MatchResponse)
async def create_match(match: MatchCreate):
    """
    Create a new match.
    """
    created_match = await match_db.create_match(match)
    return created_match


@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(match_id: str):
    """
    Get match details by ID.
    """
    try:
        ObjectId(match_id)  # Validate ObjectId format
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid match ID format")
    
    match = await match_db.get_match(match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match


@router.get("/user/{user_id}", response_model=List[MatchResponse])
async def get_user_matches(user_id: str):
    """
    Get all matches for a user (either as winner or loser).
    """
    try:
        ObjectId(user_id)  # Validate ObjectId format
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    matches = await match_db.get_user_matches(user_id)
    return matches


@router.get("/category/{category_id}", response_model=List[MatchResponse])
async def get_category_matches(category_id: str):
    """
    Get all matches for a category.
    """
    try:
        ObjectId(category_id)  # Validate ObjectId format
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid category ID format")
    
    matches = await match_db.get_category_matches(category_id)
    return matches
