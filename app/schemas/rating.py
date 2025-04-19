from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RatingBase(BaseModel):
    user_id: str
    category_id: str
    rate: float
    date: Optional[datetime] = Field(default_factory=datetime.utcnow)


class RatingCreate(RatingBase):
    pass


class RatingUpdate(BaseModel):
    rate: Optional[float] = None
    date: Optional[datetime] = None


class RatingInDB(RatingBase):
    id: str = Field(alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "user_id": "507f1f77bcf86cd799439022",
                "category_id": "507f1f77bcf86cd799439033",
                "rate": 1500.0,
                "date": "2023-01-01T00:00:00",
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00"
            }
        }


class RatingResponse(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    category_id: str
    rate: float
    date: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
