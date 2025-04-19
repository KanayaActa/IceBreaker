import matplotlib.pyplot as plt
import io
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict
from pydantic import BaseModel
from datetime import datetime
from app.database import rating_db, match_db, user_db, category_db
from app.schemas.match import MatchCreate
from app.utils.rating_calculator import calculate_elo_rating_change, get_initial_rating
from bson.objectid import ObjectId
from bson.errors import InvalidId
from app.schemas.rating import RatingInDB

router = APIRouter(prefix="/api", tags=["graph"])




@router.get("/rating-history/{user_id}/{category_id}", response_model=List[RatingInDB])
async def get_user_rating_history(user_id: str, category_id: str):
    """
    Get the rating history for a user in a specific category.
    """
    # Validate IDs
    try:
        ObjectId(user_id)
        ObjectId(category_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    # Check if user and category exist
    user = await user_db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
    
    category = await category_db.get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail=f"Category with ID {category_id} not found")
    
    # Get rating history
    rating_history = await rating_db.get_user_rating_history(user_id, category_id)
    return rating_history



@router.get("/rating-history/{user_id}/{category_id}/graph-image")
async def get_user_rating_history_graph_image(user_id: str, category_id: str):
    """
    Get the rating history for a user in a specific category as a graph image.
    Returns a generated image of the rating history graph.
    """
    # Validate IDs
    try:
        ObjectId(user_id)
        ObjectId(category_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    # Check if user and category exist
    user = await user_db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
    
    category = await category_db.get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail=f"Category with ID {category_id} not found")
    
    # Get rating history
    rating_history = await rating_db.get_user_rating_history(user_id, category_id)
    
    # Create graph data
    dates = [rating.date for rating in rating_history]
    rates = [rating.rate for rating in rating_history]

    # Create the graph
    plt.figure(figsize=(10, 6))
    plt.plot(dates, rates, marker='o', linestyle='-', color='b')
    plt.title(f"Rating History for User {user_id} in Category {category_id}")
    plt.xlabel("Date")
    plt.ylabel("Rating")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the plot to a BytesIO object
    img_io = io.BytesIO()
    plt.savefig(img_io, format='png')
    img_io.seek(0)
    plt.close()

    # Return the image as a streaming response
    return StreamingResponse(img_io, media_type="image/png")
