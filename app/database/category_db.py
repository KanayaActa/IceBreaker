from bson import ObjectId
from datetime import datetime
from typing import List, Optional
from app.database.connection import categories_collection
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryInDB


async def create_category(category: CategoryCreate) -> CategoryInDB:
    """
    Create a new category in the database.
    """
    category_dict = category.model_dump()
    category_dict["created_at"] = datetime.utcnow()
    category_dict["updated_at"] = datetime.utcnow()
    
    result = await categories_collection.insert_one(category_dict)
    
    created_category = await categories_collection.find_one({"_id": result.inserted_id})
    created_category["_id"] = str(created_category["_id"])
    
    return CategoryInDB(**created_category)


async def get_category(category_id: str) -> Optional[CategoryInDB]:
    """
    Get a category by ID.
    """
    try:
        category = await categories_collection.find_one({"_id": ObjectId(category_id)})
        if category:
            category["_id"] = str(category["_id"])
            return CategoryInDB(**category)
    except Exception:
        return None
    return None


async def update_category(category_id: str, category_update: CategoryUpdate) -> Optional[CategoryInDB]:
    """
    Update a category by ID.
    """
    try:
        category_dict = category_update.model_dump(exclude_unset=True)
        category_dict["updated_at"] = datetime.utcnow()
        
        await categories_collection.update_one(
            {"_id": ObjectId(category_id)},
            {"$set": category_dict}
        )
        
        updated_category = await categories_collection.find_one({"_id": ObjectId(category_id)})
        if updated_category:
            updated_category["_id"] = str(updated_category["_id"])
            return CategoryInDB(**updated_category)
    except Exception:
        return None
    return None


async def get_all_categories() -> List[CategoryInDB]:
    """
    Get all categories.
    """
    cursor = categories_collection.find()
    
    categories = []
    async for category in cursor:
        category["_id"] = str(category["_id"])
        categories.append(CategoryInDB(**category))
    
    return categories


async def delete_category(category_id: str) -> bool:
    """
    Delete a category by ID.
    """
    try:
        result = await categories_collection.delete_one({"_id": ObjectId(category_id)})
        return result.deleted_count > 0
    except Exception:
        return False
