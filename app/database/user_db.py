from bson import ObjectId
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from app.database.connection import users_collection
from app.schemas.user import UserCreate, UserUpdate, UserInDB
from passlib.context import CryptContext
import jwt
import os
from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-for-jwt")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def hash_password(password: str) -> str:
    """
    Hash a password for storing.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


async def create_user(user: UserCreate) -> UserInDB:
    """
    Create a new user in the database.
    Ensures email uniqueness.
    """
    # Check if email already exists
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if intra_name already exists
    existing_user = await users_collection.find_one({"intra_name": user.intra_name})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Intra name already registered"
        )
    
    user_dict = user.model_dump()
    user_dict["password"] = hash_password(user_dict["password"])
    user_dict["created_at"] = datetime.utcnow()
    user_dict["updated_at"] = datetime.utcnow()
    
    try:
        result = await users_collection.insert_one(user_dict)
        
        created_user = await users_collection.find_one({"_id": result.inserted_id})
        created_user["_id"] = str(created_user["_id"])
        
        return UserInDB(**created_user)
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or intra_name already exists"
        )


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
    Ensures email uniqueness if email is being updated.
    """
    try:
        user_dict = user_update.model_dump(exclude_unset=True)
        
        # Check email uniqueness if email is being updated
        if "email" in user_dict:
            existing_user = await users_collection.find_one({"email": user_dict["email"]})
            if existing_user and str(existing_user["_id"]) != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered by another user"
                )
        
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
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        return None
    return None


async def search_users(search_key: str) -> List[UserInDB]:
    """
    Search users by name, intra_name, or email (partial match).
    """
    cursor = users_collection.find({
        "$or": [
            {"name": {"$regex": search_key, "$options": "i"}},
            {"intra_name": {"$regex": search_key, "$options": "i"}},
            {"email": {"$regex": search_key, "$options": "i"}}
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


async def get_user_by_email(email: str) -> Optional[UserInDB]:
    """
    Get a user by email.
    """
    user = await users_collection.find_one({"email": email})
    if user:
        user["_id"] = str(user["_id"])
        return UserInDB(**user)
    return None


async def authenticate_user(email: str, password: str) -> Optional[UserInDB]:
    """
    Authenticate a user by email and password.
    """
    user = await get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user
