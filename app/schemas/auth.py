from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[str] = None


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class SignUpRequest(BaseModel):
    name: str
    intra_name: str
    email: EmailStr
    password: str
    user_image: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    name: str
    intra_name: str
    email: EmailStr
    user_image: Optional[str] = None
    created_at: datetime
    updated_at: datetime
