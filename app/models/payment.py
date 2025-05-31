from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, Enum, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from ..database import Base

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class PaymentType(str, enum.Enum):
    ADVANCE = "advance"
    MILESTONE = "milestone"
    FINAL = "final"
    BONUS = "bonus"

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    
    # Payment details
    payment_type = Column(Enum(PaymentType), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    description = Column(Text, nullable=True)
      # Status and timeline
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    due_date = Column(DateTime(timezone=True), nullable=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Payment processing
    payment_method = Column(String, nullable=True)  # bank_transfer, paypal, stripe
    transaction_id = Column(String, nullable=True)
    payment_reference = Column(String, nullable=True)
    
    # Invoice
    invoice_number = Column(String, nullable=True)
    invoice_url = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    contract = relationship("Contract", back_populates="payments")