from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# Base schemas
class CreatorBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    bio: Optional[str] = None
    location: Optional[str] = None
    category: str
    instagram_handle: Optional[str] = None
    instagram_followers: int = 0
    youtube_handle: Optional[str] = None
    youtube_subscribers: int = 0
    tiktok_handle: Optional[str] = None
    tiktok_followers: int = 0
    twitter_handle: Optional[str] = None
    twitter_followers: int = 0
    base_rate: Optional[float] = None
    engagement_rate: Optional[float] = None
    languages: Optional[List[str]] = None
    content_types: Optional[List[str]] = None

class CreatorCreate(CreatorBase):
    password: str

class CreatorUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    category: Optional[str] = None
    instagram_handle: Optional[str] = None
    instagram_followers: Optional[int] = None
    youtube_handle: Optional[str] = None
    youtube_subscribers: Optional[int] = None
    tiktok_handle: Optional[str] = None
    tiktok_followers: Optional[int] = None
    twitter_handle: Optional[str] = None
    twitter_followers: Optional[int] = None
    base_rate: Optional[float] = None
    engagement_rate: Optional[float] = None
    languages: Optional[List[str]] = None
    content_types: Optional[List[str]] = None

class CreatorLogin(BaseModel):
    username: str
    password: str

class Creator(CreatorBase):
    id: int
    is_verified: bool
    is_active: bool
    profile_image_url: Optional[str] = None
    media_kit_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CreatorSearch(BaseModel):
    query: str
    category: Optional[str] = None
    min_followers: Optional[int] = None
    max_followers: Optional[int] = None
    location: Optional[str] = None
    min_engagement_rate: Optional[float] = None
    max_rate: Optional[float] = None
    limit: int = 10

class CreatorSearchResult(BaseModel):
    creators: List[Creator]
    total_count: int
    similarity_scores: Optional[List[float]] = None