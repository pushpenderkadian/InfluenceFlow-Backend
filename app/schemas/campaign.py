from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class CampaignStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# Base schemas
class CampaignBase(BaseModel):
    title: str
    description: Optional[str] = None
    brand_name: str
    campaign_type: str
    budget: float
    start_date: datetime
    end_date: datetime
    target_audience: Optional[Dict[str, Any]] = None
    content_requirements: Optional[Dict[str, Any]] = None
    deliverables: Optional[Dict[str, Any]] = None

class CampaignCreate(CampaignBase):
    pass

class CampaignUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    brand_name: Optional[str] = None
    campaign_type: Optional[str] = None
    budget: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    target_audience: Optional[Dict[str, Any]] = None
    content_requirements: Optional[Dict[str, Any]] = None
    deliverables: Optional[Dict[str, Any]] = None
    status: Optional[CampaignStatus] = None

class Campaign(CampaignBase):
    id: int
    user_id: int
    status: CampaignStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Campaign Creator schemas
class CampaignCreatorStatus(str, Enum):
    INVITED = "invited"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class CampaignCreatorBase(BaseModel):
    campaign_id: int
    creator_id: int
    offered_rate: float
    deliverables_total: int

class CampaignCreatorCreate(CampaignCreatorBase):
    pass

class CampaignCreatorUpdate(BaseModel):
    negotiated_rate: Optional[float] = None
    final_rate: Optional[float] = None
    status: Optional[CampaignCreatorStatus] = None
    deliverables_completed: Optional[int] = None

class CampaignCreator(CampaignCreatorBase):
    id: int
    negotiated_rate: Optional[float] = None
    final_rate: Optional[float] = None
    status: CampaignCreatorStatus
    invited_at: datetime
    accepted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    deliverables_completed: int

    class Config:
        from_attributes = True

class CampaignStatusUpdate(BaseModel):
    status: str

class PaymentRequest(BaseModel):
    amount: int
    id: str  # payment_method_id from Stripe
    user: str  # user email
    plan_name: str
    purchase_date: datetime
    expire_date: datetime