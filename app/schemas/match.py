from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MatchBase(BaseModel):
    winner_id: str
    loser_id: str
    category_id: str
    winner_point: int
    loser_point: int
    date: Optional[datetime] = Field(default_factory=datetime.utcnow)


class MatchCreate(MatchBase):
    pass


class MatchUpdate(BaseModel):
    winner_point: Optional[int] = None
    loser_point: Optional[int] = None
    date: Optional[datetime] = None


class MatchInDB(MatchBase):
    id: str = Field(alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "winner_id": "507f1f77bcf86cd799439022",
                "loser_id": "507f1f77bcf86cd799439033",
                "category_id": "507f1f77bcf86cd799439044",
                "winner_point": 21,
                "loser_point": 15,
                "date": "2023-01-01T00:00:00",
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00"
            }
        }


class MatchResponse(BaseModel):
    id: str = Field(alias="_id")
    winner_id: str
    loser_id: str
    category_id: str
    winner_point: int
    loser_point: int
    date: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
