from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from ..database import Base

class OutreachType(str, enum.Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    INSTAGRAM_DM = "instagram_dm"

class OutreachStatus(str, enum.Enum):
    INITIATED = "initiated"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    REPLIED = "replied"
    FAILED = "failed"

class OutreachLog(Base):
    __tablename__ = "outreach_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_creator_id = Column(Integer, ForeignKey("campaign_creators.id"), nullable=False)
    
    # Outreach details
    outreach_type = Column(Enum(OutreachType), nullable=False)
    recipient_contact = Column(String, nullable=False)  # email, phone, username
    subject = Column(String, nullable=True)
    message = Column(Text, nullable=False)
    
    # Status and tracking
    status = Column(Enum(OutreachStatus), default=OutreachStatus.SENT)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    replied_at = Column(DateTime(timezone=True), nullable=True)
    
    # Response tracking
    response_message = Column(Text, nullable=True)
    is_positive_response = Column(Boolean, nullable=True)
      # Relationships
    campaign_creator = relationship("CampaignCreator")