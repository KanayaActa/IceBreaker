from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.database import user_db
from bson.objectid import ObjectId
from bson.errors import InvalidId

router = APIRouter(prefix="/api/user", tags=["users"])


@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate):
    """
    Create a new user.
    """
    created_user = await user_db.create_user(user)
    return created_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """
    Get user details by ID.
    """
    try:
        ObjectId(user_id)  # Validate ObjectId format
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    user = await user_db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user_update: UserUpdate):
    """
    Update user details.
    """
    try:
        ObjectId(user_id)  # Validate ObjectId format
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    updated_user = await user_db.update_user(user_id, user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@router.get("/", response_model=List[UserResponse])
async def search_users(key: Optional[str] = Query(None)):
    """
    Search users by name or intra_name (partial match).
    """
    if not key:
        raise HTTPException(status_code=400, detail="Search key is required")
    
    users = await user_db.search_users(key)
    return users
