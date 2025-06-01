from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from ..database import get_db
from ..models.user import User
from ..models.campaign import Campaign
from ..models.campaign_creator import CampaignCreator
from ..models.creator import Creator
from ..schemas.campaign import (
    CampaignCreate, 
    Campaign as CampaignSchema, 
    CampaignUpdate,
    CampaignCreatorCreate,
    CampaignCreator as CampaignCreatorSchema,
    CampaignStatusUpdate
)
from ..dependencies import get_current_user, require_role
from ..middlewares.rate_limiter import limiter
from ..services.email_service import email_service
from sqlalchemy import text

router = APIRouter(prefix="/campaigns", tags=["campaigns"])

@router.post("/", response_model=CampaignSchema)
@limiter.limit("10/minute")
async def create_campaign(
    request: Request,
    campaign: CampaignCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new campaign"""
    db_campaign = Campaign(
        **campaign.dict(),
        user_id=current_user.id
    )
    
    db.add(db_campaign)
    await db.commit()
    await db.refresh(db_campaign)
    
    return db_campaign

@router.get("/", response_model=List[CampaignSchema])
async def get_campaigns(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get campaigns for current user"""
    result = await db.execute(
        select(Campaign)
        .filter(Campaign.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .order_by(Campaign.created_at.desc())
    )
    return result.scalars().all()

@router.get("/{campaign_id}", response_model=CampaignSchema)
async def get_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific campaign"""
    result = await db.execute(
        select(Campaign)
        .filter(Campaign.id == campaign_id, Campaign.user_id == current_user.id)
    )
    campaign = result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    return campaign

@router.put("/{campaign_id}", response_model=CampaignSchema)
async def update_campaign(
    campaign_id: int,
    campaign_update: CampaignUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a campaign"""
    result = await db.execute(
        select(Campaign)
        .filter(Campaign.id == campaign_id, Campaign.user_id == current_user.id)
    )
    campaign = result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Update campaign fields
    update_data = campaign_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(campaign, field, value)
    
    await db.commit()
    await db.refresh(campaign)
    
    return campaign

@router.delete("/{campaign_id}")
async def delete_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a campaign"""
    result = await db.execute(
        select(Campaign)
        .filter(Campaign.id == campaign_id, Campaign.user_id == current_user.id)
    )
    campaign = result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    await db.delete(campaign)
    await db.commit()
    
    return {"message": "Campaign deleted successfully"}

@router.post("/{campaign_id}/invite", response_model=CampaignCreatorSchema)
@limiter.limit("20/minute")
async def invite_creator_to_campaign(
    campaign_id: int,
    request: Request,
    invitation: CampaignCreatorCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Invite a creator to a campaign"""
    # Verify campaign ownership
    result = await db.execute(
        select(Campaign)
        .filter(Campaign.id == campaign_id, Campaign.user_id == current_user.id)
    )
    campaign = result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Check if creator exists
    result = await db.execute(
        select(Creator)
        .filter(Creator.id == invitation.creator_id)
    )
    creator = result.scalar_one_or_none()
    
    if not creator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creator not found"
        )
    
    # Check if invitation already exists
    result = await db.execute(
        select(CampaignCreator)
        .filter(
            CampaignCreator.campaign_id == campaign_id,
            CampaignCreator.creator_id == invitation.creator_id
        )
    )
    existing_invitation = result.scalar_one_or_none()
    
    if existing_invitation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Creator already invited to this campaign"
        )
    
    # Create invitation
    db_campaign_creator = CampaignCreator(
        campaign_id=campaign_id,
        creator_id=invitation.creator_id,
        offered_rate=invitation.offered_rate,
        deliverables_total=invitation.deliverables_total
    )
    
    db.add(db_campaign_creator)
    await db.commit()
    await db.refresh(db_campaign_creator)
    
    # Send invitation email
    campaign_details = {
        'description': campaign.description,
        'start_date': campaign.start_date,
        'end_date': campaign.end_date
    }
    
    await email_service.send_campaign_invitation(
        creator_email=creator.email,
        creator_name=creator.full_name,
        campaign_title=campaign.title,
        brand_name=campaign.brand_name,
        offered_rate=invitation.offered_rate,
        campaign_details=campaign_details
    )
    
    return db_campaign_creator

@router.get("/{campaign_id}/creators", response_model=List[CampaignCreatorSchema])
async def get_campaign_creators(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all creators for a campaign"""
    # Verify campaign ownership
    result = await db.execute(
        select(Campaign)
        .filter(Campaign.id == campaign_id, Campaign.user_id == current_user.id)
    )
    campaign = result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    result = await db.execute(
        select(CampaignCreator)
        .filter(CampaignCreator.campaign_id == campaign_id)
        .options(selectinload(CampaignCreator.creator))
    )
    
    return result.scalars().all()


@router.post("/{campaign_id}/status-update")
@limiter.limit("20/minute")
async def edit_campaign(
        campaign_id: int,
        campaign_status_update: CampaignStatusUpdate,
        request: Request,
        db: AsyncSession = Depends(get_db)
    ):

    """Update a campaign"""
    result = await db.execute(
        select(Campaign)
        .filter(Campaign.id == campaign_id)
    )
    campaign = result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Update campaign fields
    update_data = campaign_status_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(campaign, field, value)
    
    await db.commit()
    await db.refresh(campaign)
    
    return {
        "status": True
    }

