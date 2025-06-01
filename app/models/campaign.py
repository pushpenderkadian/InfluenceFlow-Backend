from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, Enum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from ..database import Base

class CampaignStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    brand_name = Column(String, nullable=False)
    campaign_type = Column(String, nullable=False)  # product_launch, brand_awareness, etc.
      # Budget and timeline
    budget = Column(Float, nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    
    # Campaign requirements
    target_audience = Column(JSON, nullable=True)  # demographics, interests
    content_requirements = Column(JSON, nullable=True)  # post types, hashtags, etc.
    deliverables = Column(JSON, nullable=True)  # number of posts, stories, etc.
    
    # Campaign manager
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Status and metadata
    status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    assistant_id = Column(String, nullable=True)  # Optional assistant for the campaign
    
    # Relationships
    user = relationship("User", back_populates="campaigns")
    campaign_creators = relationship("CampaignCreator", back_populates="campaign")



