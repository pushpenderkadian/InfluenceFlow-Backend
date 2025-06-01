from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta
from typing import List

from ..database import get_db
from ..models.user import User
from ..models.creator import Creator
from ..schemas.user import UserCreate, User as UserSchema, UserLogin, Token
from ..schemas.creator import CreatorCreate, Creator as CreatorSchema, CreatorLogin
from ..auth.jwt_handler import create_access_token, get_password_hash, verify_password
from ..dependencies import get_current_user
from ..middlewares.rate_limiter import limiter
from ..config import settings
from ..services.pinecone_service import PineconeService
pinecone_service = PineconeService()

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register/user", response_model=UserSchema)
@limiter.limit("5/minute")
async def register_user(request: Request, user: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new campaign manager user"""
    # Check if user already exists
    result = await db.execute(select(User).filter(User.email == user.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    result = await db.execute(select(User).filter(User.username == user.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    

    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        uid=user.uid,
        username=user.username,
        hashed_password=hashed_password,
        full_name=user.full_name,
        company_name=user.company_name,
        role=user.role
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    return db_user

@router.post("/register/creator", response_model=CreatorSchema)
@limiter.limit("5/minute")
async def register_creator(request: Request, creator: CreatorCreate, db: AsyncSession = Depends(get_db)):
    """Register a new creator/influencer"""
    # Check if creator already exists
    result = await db.execute(select(Creator).filter(Creator.email == creator.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    result = await db.execute(select(Creator).filter(Creator.username == creator.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new creator
    hashed_password = get_password_hash(creator.password)
    db_creator = Creator(
        email=creator.email,
        username=creator.username,
        hashed_password=hashed_password,
        full_name=creator.full_name,
        bio=creator.bio,
        location=creator.location,
        category=creator.category,
        instagram_handle=creator.instagram_handle,
        instagram_followers=creator.instagram_followers,
        youtube_handle=creator.youtube_handle,
        youtube_subscribers=creator.youtube_subscribers,
        tiktok_handle=creator.tiktok_handle,
        tiktok_followers=creator.tiktok_followers,
        twitter_handle=creator.twitter_handle,
        twitter_followers=creator.twitter_followers,
        base_rate=creator.base_rate,
        engagement_rate=creator.engagement_rate,
        languages=creator.languages,
        content_types=creator.content_types
    )
    
    db.add(db_creator)
    await db.commit()
    await db.refresh(db_creator)
    
    # Add creator to Pinecone for search
    creator_data = {
        'full_name': db_creator.full_name,
        'bio': db_creator.bio,
        'location': db_creator.location,
        'category': db_creator.category,
        'languages': db_creator.languages,
        'content_types': db_creator.content_types,
        'instagram_followers': db_creator.instagram_followers,
        'base_rate': db_creator.base_rate,
        'engagement_rate': db_creator.engagement_rate
    }
    await pinecone_service.upsert_creator(db_creator.id, creator_data)
    
    return db_creator

@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
async def login(request: Request, login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login for both users and creators with explicit user type"""
    
    if login_data.user_type == "user":
        # Authenticate as campaign manager/user
        result = await db.execute(select(User).filter(User.username == login_data.username))
        user = result.scalar_one_or_none()
        
        if not user or not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "user_type": "user"},
            expires_delta=access_token_expires
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_type": "user",
            "user_id": user.id
        }
    
    elif login_data.user_type == "creator":
        # Authenticate as creator/influencer
        result = await db.execute(select(Creator).filter(Creator.username == login_data.username))
        creator = result.scalar_one_or_none()
        
        if not creator or not verify_password(login_data.password, creator.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(creator.id), "user_type": "creator"},
            expires_delta=access_token_expires
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_type": "creator",
            "user_id": creator.id
        }
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user_type. Must be 'user' or 'creator'",
        )

@router.get("/me", response_model=UserSchema)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

