from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Base schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    company_name: Optional[str] = None
    role: str = "campaign_manager"

class UserCreate(UserBase):
    password: str
    uid: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    company_name: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str
    user_type: str = "user"  # "user" or "creator"

class User(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserInDB(User):
    hashed_password: str

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    user_type: str
    user_id: int

class TokenData(BaseModel):
    username: Optional[str] = None