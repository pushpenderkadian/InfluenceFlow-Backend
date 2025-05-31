from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from .database import get_db
from .auth.jwt_handler import verify_token
from .models.user import User
from .models.creator import Creator

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    token = credentials.credentials
    payload = verify_token(token)
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    result = await db.execute(select(User).filter(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user

async def get_current_creator(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Creator:
    """Get current authenticated creator"""
    token = credentials.credentials
    payload = verify_token(token)
    
    creator_id: str = payload.get("sub")
    user_type: str = payload.get("user_type")
    
    if creator_id is None or user_type != "creator":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    result = await db.execute(select(Creator).filter(Creator.id == int(creator_id)))
    creator = result.scalar_one_or_none()
    
    if creator is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Creator not found",
        )
    
    return creator

def require_role(allowed_roles: list):
    """Decorator to require specific roles"""
    async def role_checker(
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
        token = credentials.credentials
        payload = verify_token(token)
        user_type = payload.get("user_type")
        
        if user_type not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return True
    
    return role_checker