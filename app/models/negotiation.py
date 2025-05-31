from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from ..database import Base

class NegotiationStatus(str, enum.Enum):
    INITIATED = "initiated"
    COUNTER_OFFERED = "counter_offered"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"

class Negotiation(Base):
    __tablename__ = "negotiations"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_creator_id = Column(Integer, ForeignKey("campaign_creators.id"), nullable=False)
    
    # Negotiation details
    proposed_rate = Column(Float, nullable=False)
    counter_rate = Column(Float, nullable=True)
    final_rate = Column(Float, nullable=True)
    
    # Messages and terms
    initial_message = Column(Text, nullable=True)
    counter_message = Column(Text, nullable=True)
    terms_and_conditions = Column(Text, nullable=True)
    
    # Status and timeline
    status = Column(Enum(NegotiationStatus), default=NegotiationStatus.INITIATED)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
      # Relationships
    campaign_creator = relationship("CampaignCreator")