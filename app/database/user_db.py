from bson import ObjectId
from datetime import datetime
from typing import List, Optional
from app.database.connection import users_collection
from app.schemas.user import UserCreate, UserUpdate, UserInDB
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a password for storing.
    """
    return pwd_context.hash(password)


async def create_user(user: UserCreate) -> UserInDB:
    """
    Create a new user in the database.
    """
    user_dict = user.model_dump()
    user_dict["password"] = hash_password(user_dict["password"])
    user_dict["created_at"] = datetime.utcnow()
    user_dict["updated_at"] = datetime.utcnow()
    
    result = await users_collection.insert_one(user_dict)
    
    created_user = await users_collection.find_one({"_id": result.inserted_id})
    created_user["_id"] = str(created_user["_id"])
    
    return UserInDB(**created_user)


async def get_user(user_id: str) -> Optional[UserInDB]:
    """
    Get a user by ID.
    """
    try:
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if user:
            user["_id"] = str(user["_id"])
            return UserInDB(**user)
    except Exception:
        return None
    return None


async def update_user(user_id: str, user_update: UserUpdate) -> Optional[UserInDB]:
    """
    Update a user by ID.
    """
    try:
        user_dict = user_update.model_dump(exclude_unset=True)
        
        if "password" in user_dict and user_dict["password"]:
            user_dict["password"] = hash_password(user_dict["password"])
            
        user_dict["updated_at"] = datetime.utcnow()
        
        await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": user_dict}
        )
        
        updated_user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if updated_user:
            updated_user["_id"] = str(updated_user["_id"])
            return UserInDB(**updated_user)
    except Exception:
        return None
    return None


async def search_users(search_key: str) -> List[UserInDB]:
    """
    Search users by name or intra_name (partial match).
    """
    cursor = users_collection.find({
        "$or": [
            {"name": {"$regex": search_key, "$options": "i"}},
            {"intra_name": {"$regex": search_key, "$options": "i"}}
        ]
    })
    
    users = []
    async for user in cursor:
        user["_id"] = str(user["_id"])
        users.append(UserInDB(**user))
    
    return users


async def delete_user(user_id: str) -> bool:
    """
    Delete a user by ID.
    """
    try:
        result = await users_collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0
    except Exception:
        return False
