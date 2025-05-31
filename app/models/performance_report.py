from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class PerformanceReport(Base):
    __tablename__ = "performance_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_creator_id = Column(Integer, ForeignKey("campaign_creators.id"), nullable=False)
      # Report details
    report_period_start = Column(DateTime(timezone=True), nullable=False)
    report_period_end = Column(DateTime(timezone=True), nullable=False)
    content_url = Column(String, nullable=True)  # Link to the actual content
    
    # Engagement metrics
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    saves = Column(Integer, default=0)
    
    # Performance metrics
    reach = Column(Integer, default=0)
    impressions = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    click_through_rate = Column(Float, default=0.0)
    
    # ROI and conversion
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    conversion_rate = Column(Float, default=0.0)
    revenue_generated = Column(Float, default=0.0)
    roi = Column(Float, default=0.0)
    
    # Additional metrics (platform specific)
    platform_metrics = Column(JSON, nullable=True)  # Custom metrics per platform
    
    # Report metadata
    report_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
      # Relationships
    campaign_creator = relationship("CampaignCreator")