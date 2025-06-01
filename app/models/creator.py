from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Creator(Base):
    __tablename__ = "creators"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    bio = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    category = Column(String, nullable=False)  # fashion, tech, lifestyle, etc.
    
    # Social media platforms
    instagram_handle = Column(String, nullable=True)
    instagram_followers = Column(Integer, default=0)
    youtube_handle = Column(String, nullable=True)
    youtube_subscribers = Column(Integer, default=0)
    tiktok_handle = Column(String, nullable=True)
    tiktok_followers = Column(Integer, default=0)
    twitter_handle = Column(String, nullable=True)
    twitter_followers = Column(Integer, default=0)
    
    # Pricing and engagement
    base_rate = Column(Float, nullable=True)  # Base rate per post
    engagement_rate = Column(Float, nullable=True)  # Average engagement rate
    media_kit_url = Column(String, nullable=True)
    
    # Profile and verification
    profile_image_url = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Additional metadata
    languages = Column(JSON, nullable=True)  # List of languages
    content_types = Column(JSON, nullable=True)  # post, story, reel, video
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    campaign_creators = relationship("CampaignCreator", back_populates="creator")