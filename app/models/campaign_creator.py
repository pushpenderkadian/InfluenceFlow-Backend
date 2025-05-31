from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, Enum, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from ..database import Base

class CampaignCreatorStatus(str, enum.Enum):
    INVITED = "invited"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class CampaignCreator(Base):
    __tablename__ = "campaign_creators"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    creator_id = Column(Integer, ForeignKey("creators.id"), nullable=False)
    
    # Negotiation details
    offered_rate = Column(Float, nullable=False)
    negotiated_rate = Column(Float, nullable=True)
    final_rate = Column(Float, nullable=True)
    
    # Status and timeline
    status = Column(Enum(CampaignCreatorStatus), default=CampaignCreatorStatus.INVITED)
    invited_at = Column(DateTime(timezone=True), server_default=func.now())
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Content deliverables
    deliverables_completed = Column(Integer, default=0)
    deliverables_total = Column(Integer, nullable=False)
      # Relationships
    campaign = relationship("Campaign", back_populates="campaign_creators")
    creator = relationship("Creator", back_populates="campaign_creators")