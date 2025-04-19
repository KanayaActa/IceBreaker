from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.database import category_db
from bson.objectid import ObjectId
from bson.errors import InvalidId

router = APIRouter(prefix="/api/category", tags=["categories"])


@router.post("/", response_model=CategoryResponse)
async def create_category(category: CategoryCreate):
    """
    Create a new category.
    """
    created_category = await category_db.create_category(category)
    return created_category


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: str):
    """
    Get category details by ID.
    """
    try:
        ObjectId(category_id)  # Validate ObjectId format
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid category ID format")
    
    category = await category_db.get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(category_id: str, category_update: CategoryUpdate):
    """
    Update category details.
    """
    try:
        ObjectId(category_id)  # Validate ObjectId format
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid category ID format")
    
    updated_category = await category_db.update_category(category_id, category_update)
    if not updated_category:
        raise HTTPException(status_code=404, detail="Category not found")
    return updated_category


@router.get("/", response_model=List[CategoryResponse])
async def get_all_categories():
    """
    Get all categories.
    """
    categories = await category_db.get_all_categories()
    return categories
