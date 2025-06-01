from fastapi import APIRouter, Depends, HTTPException, status, Request
import requests
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from datetime import datetime, UTC

from helpers.queue_helper import create_queue
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
    CampaignStatusUpdate,
    PaymentRequest
)
from ..dependencies import get_current_user, require_role
from ..middlewares.rate_limiter import limiter
from ..services.email_service import email_service
from sqlalchemy import text
from app.models.outreach_log import OutreachLog
from app.config import settings

import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY
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
    
    outreach_data = await email_service.send_campaign_invitation(
        creator_email=creator.email,
        creator_name=creator.full_name,
        campaign_title=campaign.title,
        brand_name=campaign.brand_name,
        offered_rate=invitation.offered_rate,
        campaign_details=campaign_details
    )

    outreach_log_ingest_data = {
        "campaign_creator_id": current_user.id,
        "outreach_type": outreach_data["outreach_type"],
        "recipient_contact": outreach_data["recipient_contact"],
        "subject": outreach_data["subject"],
        "message": outreach_data["message"],
        "status": outreach_data["status"],
        "sent_at": datetime.now(UTC),
        "delivered_at": datetime.now(UTC)
    }
    print(f"Creating outreach log with data: {outreach_log_ingest_data}")
    db_outreach_log = OutreachLog(**outreach_log_ingest_data)
    
    db.add(db_outreach_log)
    await db.commit()
    await db.refresh(db_outreach_log)

    outreach_id = db_outreach_log.id
    _status = db_outreach_log.status

    payload = {
        "outreach_id": outreach_id,
        "status": _status
    }

    print(f"Sending payload to email queue: {payload}")
    queue = create_queue(
        queue_name=settings.EMAIL_QUEUE_NAME,
        host=settings.RABBITMQ_HOST,
        port=settings.RABBITMQ_PORT,
        user=settings.RABBITMQ_USER,
        password=settings.RABBITMQ_PASSWORD,
        vhost=settings.RABBITMQ_VHOST
    )
    queue.put(payload)

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
    
    assistant_id = None
    try:
        assistant_id_url = f"http://localhost:8001/create-campaign-assistant"
        response = requests.post(url=assistant_id_url, json=campaign)
        response.raise_for_status()
        response = response.json()
        assistant_id = response["assistant_id"]
    except Exception as e:
        print(f"Error getting assitant id")
    

    update_data = campaign_status_update.dict(exclude_unset=True)
    update_data["assistant_id"] = assistant_id
    print(update_data)
    for field, value in update_data.items():
        setattr(campaign, field, value)
    
    await db.commit()
    await db.refresh(campaign)
    
    return {
        "status": True
    }


@router.get("/creator/{creator_id}/campaign/{campaign_id}/chat")
async def get_creator_campaign_chat(creator_id: int, campaign_id: int,db: AsyncSession = Depends(get_db)):
    """
    Fetch chat messages for a specific creator and campaign
    """
    try:
        # Get thread_id from database
        result = await db.execute(
            text("SELECT thread_id FROM campaign_creators WHERE creator_id=:creator_id AND campaign_id=:campaign_id"),
            {"creator_id": creator_id, "campaign_id": campaign_id}
        )
        row = result.mappings().fetchone()
        
        if not row["thread_id"]:
            return {
                "creator_id": creator_id,
                "campaign_id": campaign_id,
                "thread_id": "",
                "messages": "",
                "total_messages": []
            }
        
        thread_id = row.thread_id
        
        # Fetch messages from OpenAI
        messages_response = requests.get(f"https://api.openai.com/v1/threads/{thread_id}/messages",
            headers={
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "OpenAI-Beta": "assistants=v2"
            }
        )
        
        if messages_response.status_code != 200:
            raise HTTPException(
                status_code=messages_response.status_code, 
                detail=f"Failed to fetch messages: {messages_response.text}"
            )
            
        messages = messages_response.json()
        
        # Format messages in chronological order (oldest first)
        formatted_messages = []
        for message in reversed(messages.get("data", [])):
            formatted_message = {
                "id": message.get("id"),
                "role": message.get("role"),
                "content": "",
                "created_at": message.get("created_at"),
                "timestamp": message.get("created_at")
            }
            
            # Extract text content
            content_parts = []
            for content_block in message.get("content", []):
                if content_block.get("type") == "text":
                    content_parts.append(content_block.get("text", {}).get("value", ""))
            
            formatted_message["content"] = " ".join(content_parts)
            formatted_messages.append(formatted_message)
        
        return {
            "creator_id": creator_id,
            "campaign_id": campaign_id,
            "thread_id": thread_id,
            "messages": formatted_messages,
            "total_messages": len(formatted_messages)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching chat: {str(e)}")




@router.post("/payment")
async def process_payment(payment_data: PaymentRequest,db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)):
    # Validate user exists
    try:
        user_row = current_user.dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    if not user_row:
        raise HTTPException(status_code=400, detail="Invalid User")
    
    user_id = user_row['id']
    
    try:
        # Start database transaction
        async with db.acquire() as connection:
            async with connection.transaction():
                # Create Stripe payment intent
                payment_intent = stripe.PaymentIntent.create(
                    amount=payment_data.amount,
                    currency="inr",
                    description="Stripe Payment",
                    payment_method=payment_data.id,
                    confirm=True
                )
                
               
    except stripe.error.StripeError as e:
        print(f"Stripe error: {e}")
        raise HTTPException(status_code=500, detail="Payment Failed")
    except Exception as error:
        print(f"Database error: {error}")
        raise HTTPException(status_code=500, detail="Payment Failed")
    
    return {"message": "Payment Successful"}