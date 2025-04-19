from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Optional
from jose import JWTError, jwt

from app.schemas.auth import Token, TokenData, SignInRequest, SignUpRequest, UserResponse
from app.schemas.user import UserCreate
from app.database import user_db

router = APIRouter(prefix="/api/auth", tags=["authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/signin")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Get the current user from the JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, user_db.SECRET_KEY, algorithms=[user_db.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception
        
    user = await user_db.get_user(token_data.user_id)
    if user is None:
        raise credentials_exception
        
    return user


@router.post("/signup", response_model=UserResponse)
async def signup(user_data: SignUpRequest):
    """
    Register a new user.
    """
    # Convert SignUpRequest to UserCreate
    user_create = UserCreate(
        name=user_data.name,
        intra_name=user_data.intra_name,
        email=user_data.email,
        password=user_data.password,
        user_image=user_data.user_image
    )
    
    # Create user
    user = await user_db.create_user(user_create)
    
    # Return user data without password
    return UserResponse(
        id=user.id,
        name=user.name,
        intra_name=user.intra_name,
        email=user.email,
        user_image=user.user_image,
        created_at=user.created_at,
        updated_at=user.updated_at
    )


@router.post("/signin", response_model=Token)
async def signin(form_data: SignInRequest):
    """
    Authenticate a user and return a JWT token.
    """
    user = await user_db.authenticate_user(form_data.email, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Create access token
    access_token_expires = timedelta(minutes=user_db.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = user_db.create_access_token(
        data={"sub": user.id},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
