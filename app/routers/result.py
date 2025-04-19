from fastapi import APIRouter, HTTPException, Depends
from typing import List
from pydantic import BaseModel
from datetime import datetime
from app.database import rating_db, match_db, user_db, category_db
from app.schemas.match import MatchCreate
from app.utils.rating_calculator import calculate_elo_rating_change, get_initial_rating
from bson.objectid import ObjectId
from bson.errors import InvalidId

router = APIRouter(prefix="/api/result", tags=["results"])


class MatchResultCreate(BaseModel):
    winner_id: str
    loser_id: str
    category_id: str
    winner_point: int
    loser_point: int
    date: datetime = datetime.utcnow()


@router.post("/", status_code=201)
async def record_match_result(result: MatchResultCreate):
    """
    Record a match result and update ratings.
    """
    # Validate IDs
    try:
        ObjectId(result.winner_id)
        ObjectId(result.loser_id)
        ObjectId(result.category_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    # Check if users and category exist
    winner = await user_db.get_user(result.winner_id)
    if not winner:
        raise HTTPException(status_code=404, detail=f"Winner with ID {result.winner_id} not found")
    
    loser = await user_db.get_user(result.loser_id)
    if not loser:
        raise HTTPException(status_code=404, detail=f"Loser with ID {result.loser_id} not found")
    
    category = await category_db.get_category(result.category_id)
    if not category:
        raise HTTPException(status_code=404, detail=f"Category with ID {result.category_id} not found")
    
    # Create match record
    match_data = MatchCreate(
        winner_id=result.winner_id,
        loser_id=result.loser_id,
        category_id=result.category_id,
        winner_point=result.winner_point,
        loser_point=result.loser_point,
        date=result.date
    )
    
    match = await match_db.create_match(match_data)
    
    # Get current ratings or create initial ratings if they don't exist
    winner_rating = await rating_db.get_user_category_rating(result.winner_id, result.category_id)
    loser_rating = await rating_db.get_user_category_rating(result.loser_id, result.category_id)
    
    winner_current_rate = winner_rating.rate if winner_rating else get_initial_rating()
    loser_current_rate = loser_rating.rate if loser_rating else get_initial_rating()
    
    # Calculate new ratings
    new_winner_rate, new_loser_rate = calculate_elo_rating_change(winner_current_rate, loser_current_rate)
    
    # Update or create ratings
    if winner_rating:
        from app.schemas.rating import RatingUpdate
        await rating_db.update_rating(
            str(winner_rating.id), 
            RatingUpdate(rate=new_winner_rate, date=result.date)
        )
    else:
        from app.schemas.rating import RatingCreate
        await rating_db.create_rating(
            RatingCreate(
                user_id=result.winner_id,
                category_id=result.category_id,
                rate=new_winner_rate,
                date=result.date
            )
        )
    
    if loser_rating:
        from app.schemas.rating import RatingUpdate
        await rating_db.update_rating(
            str(loser_rating.id), 
            RatingUpdate(rate=new_loser_rate, date=result.date)
        )
    else:
        from app.schemas.rating import RatingCreate
        await rating_db.create_rating(
            RatingCreate(
                user_id=result.loser_id,
                category_id=result.category_id,
                rate=new_loser_rate,
                date=result.date
            )
        )
    
    return {
        "message": "Match result recorded and ratings updated",
        "match_id": match.id,
        "winner": {
            "id": result.winner_id,
            "old_rating": winner_current_rate,
            "new_rating": new_winner_rate
        },
        "loser": {
            "id": result.loser_id,
            "old_rating": loser_current_rate,
            "new_rating": new_loser_rate
        }
    }
