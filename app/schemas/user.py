from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    name: str
    intra_name: str
    email: EmailStr
    password: str
    user_image: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    user_image: Optional[str] = None
    password: Optional[str] = None


class UserInDB(UserBase):
    id: str = Field(alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "name": "John Doe",
                "intra_name": "jdoe",
                "email": "jdoe@example.com",
                "password": "hashed_password",
                "user_image": "https://example.com/image.jpg",
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00"
            }
        }


class UserResponse(BaseModel):
    id: str = Field(alias="_id")
    name: str
    intra_name: str
    email: EmailStr
    user_image: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
