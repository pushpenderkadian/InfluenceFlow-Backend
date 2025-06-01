from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, Enum, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base

class ContractStatus(str, enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    SIGNED = "signed"
    EXECUTED = "executed"
    TERMINATED = "terminated"

class Contract(Base):
    __tablename__ = "contracts"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_creator_id = Column(Integer, ForeignKey("campaign_creators.id"), nullable=False)
    
    # Contract details
    contract_number = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    terms_and_conditions = Column(Text, nullable=False)
    payment_terms = Column(Text, nullable=False)
    deliverables = Column(Text, nullable=False)
    
    # Financial details
    total_amount = Column(Float, nullable=False)
    advance_percentage = Column(Float, default=0.0)
    advance_amount = Column(Float, default=0.0)
    
    # Contract lifecycle
    status = Column(Enum(ContractStatus), default=ContractStatus.DRAFT)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sent_at = Column(DateTime(timezone=True), nullable=True)
    signed_at = Column(DateTime(timezone=True), nullable=True)
    executed_at = Column(DateTime(timezone=True), nullable=True)
    
    # E-signature
    is_e_signed = Column(Boolean, default=False)
    signature_url = Column(String, nullable=True)
    
    # File storage
    contract_file_url = Column(String, nullable=True)
    signed_contract_url = Column(String, nullable=True)
      # Relationships
    campaign_creator = relationship("CampaignCreator")
    payments = relationship("Payment", back_populates="contract")