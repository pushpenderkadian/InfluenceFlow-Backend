from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional

from ..database import get_db
from ..models.creator import Creator
from ..models.campaign_creator import CampaignCreator
from ..schemas.creator import (
    Creator as CreatorSchema, 
    CreatorUpdate, 
    CreatorSearch, 
    CreatorSearchResult
)
from ..dependencies import get_current_user, get_current_creator
from ..middlewares.rate_limiter import limiter
from ..services.pinecone_service import PineconeService
pinecone_service = PineconeService()
router = APIRouter(prefix="/creators", tags=["creators"])

@router.get("/search", response_model=CreatorSearchResult)
@limiter.limit("30/minute")
async def search_creators(
    request: Request,
    query: str = Query(..., description="Search query for finding creators"),
    category: Optional[str] = Query(None, description="Filter by creator category"),
    min_followers: Optional[int] = Query(None, description="Minimum follower count"),
    max_followers: Optional[int] = Query(None, description="Maximum follower count"),
    location: Optional[str] = Query(None, description="Filter by location"),
    min_engagement_rate: Optional[float] = Query(None, description="Minimum engagement rate"),
    max_rate: Optional[float] = Query(None, description="Maximum rate per post"),
    limit: int = Query(10, description="Number of results to return"),
    db: AsyncSession = Depends(get_db)
):
    """Search creators using vector similarity and filters"""
    
    # Prepare filters for Pinecone
    filters = {}
    if category:
        filters['category'] = category
    if min_followers:
        filters['min_followers'] = min_followers
    if max_rate:
        filters['max_rate'] = max_rate
    
    # Search in Pinecone
    pinecone_results = await pinecone_service.search_creators(
        query=query,
        filters=filters,
        limit=limit * 2  # Get more results to filter in DB
    )
    print(f"Pinecone search results: {len(pinecone_results)} matches for query '{query}'")
    # Extract creator IDs from Pinecone results
    creator_ids = [int(match.metadata.get('creator_id', 0)) for match in pinecone_results]
    similarity_scores = [match.score for match in pinecone_results]
    
    if not creator_ids:
        # Fallback to database search if Pinecone returns no results
        query_filter = Creator.is_active == True
        
        if category:
            query_filter = and_(query_filter, Creator.category.ilike(f"%{category}%"))
        if location:
            query_filter = and_(query_filter, Creator.location.ilike(f"%{location}%"))
        if min_followers:
            query_filter = and_(query_filter, Creator.instagram_followers >= min_followers)
        if max_followers:
            query_filter = and_(query_filter, Creator.instagram_followers <= max_followers)
        if min_engagement_rate:
            query_filter = and_(query_filter, Creator.engagement_rate >= min_engagement_rate)
        if max_rate:
            query_filter = and_(query_filter, Creator.base_rate <= max_rate)
        
        result = await db.execute(
            select(Creator)
            .filter(query_filter)
            .limit(limit)
        )
        creators = result.scalars().all()
        similarity_scores = [0.0] * len(creators)
    else:
        # Get creators from database based on Pinecone results
        result = await db.execute(
            select(Creator)
            .filter(Creator.id.in_(creator_ids), Creator.is_active == True)
        )
        db_creators = result.scalars().all()
        
        # Sort creators based on Pinecone order
        creator_dict = {creator.id: creator for creator in db_creators}
        creators = [creator_dict[creator_id] for creator_id in creator_ids if creator_id in creator_dict]
        
        # Apply additional database filters
        filtered_creators = []
        filtered_scores = []
        
        for i, creator in enumerate(creators):
            if location and location.lower() not in (creator.location or "").lower():
                continue
            if max_followers and creator.instagram_followers > max_followers:
                continue
            if min_engagement_rate and (creator.engagement_rate or 0) < min_engagement_rate:
                continue
            
            filtered_creators.append(creator)
            filtered_scores.append(similarity_scores[i] if i < len(similarity_scores) else 0.0)
            
            if len(filtered_creators) >= limit:
                break
        
        creators = filtered_creators
        similarity_scores = filtered_scores
    
    return CreatorSearchResult(
        creators=creators,
        total_count=len(creators),
        similarity_scores=similarity_scores
    )

@router.get("/", response_model=List[CreatorSchema])
async def get_creators(
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all creators with optional filtering"""
    query_filter = Creator.is_active == True
    
    if category:
        query_filter = and_(query_filter, Creator.category.ilike(f"%{category}%"))
    
    result = await db.execute(
        select(Creator)
        .filter(query_filter)
        .offset(skip)
        .limit(limit)
        .order_by(Creator.created_at.desc())
    )
    
    return result.scalars().all()

@router.get("/{creator_id}", response_model=CreatorSchema)
async def get_creator(creator_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific creator by ID"""
    result = await db.execute(
        select(Creator)
        .filter(Creator.id == creator_id, Creator.is_active == True)
    )
    creator = result.scalar_one_or_none()
    
    if not creator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creator not found"
        )
    
    return creator

@router.put("/me", response_model=CreatorSchema)
async def update_creator_profile(
    creator_update: CreatorUpdate,
    current_creator: Creator = Depends(get_current_creator),
    db: AsyncSession = Depends(get_db)
):
    """Update current creator's profile"""
    
    # Update creator fields
    update_data = creator_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_creator, field, value)
    
    await db.commit()
    await db.refresh(current_creator)
    
    # Update creator in Pinecone
    creator_data = {
        'full_name': current_creator.full_name,
        'bio': current_creator.bio,
        'location': current_creator.location,
        'category': current_creator.category,
        'languages': current_creator.languages,
        'content_types': current_creator.content_types,
        'instagram_followers': current_creator.instagram_followers,
        'base_rate': current_creator.base_rate,
        'engagement_rate': current_creator.engagement_rate
    }
    await pinecone_service.upsert_creator(current_creator.id, creator_data)
    
    return current_creator

@router.get("/me/campaigns")
async def get_creator_campaigns(
    request: Request,
    current_creator: Creator = Depends(get_current_creator),
    db: AsyncSession = Depends(get_db)
):
    """Get campaigns for current creator"""
    result = await db.execute(
        select(CampaignCreator)
        .filter(CampaignCreator.creator_id == current_creator.id)
        .order_by(CampaignCreator.invited_at.desc())
    )
    
    return result.scalars().all()

@router.post("/me/campaigns/{campaign_creator_id}/accept")
async def accept_campaign_invitation(
    campaign_creator_id: int,
    current_creator: Creator = Depends(get_current_creator),
    db: AsyncSession = Depends(get_db)
):
    """Accept a campaign invitation"""
    result = await db.execute(
        select(CampaignCreator)
        .filter(
            CampaignCreator.id == campaign_creator_id,
            CampaignCreator.creator_id == current_creator.id
        )
    )
    campaign_creator = result.scalar_one_or_none()
    
    if not campaign_creator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign invitation not found"
        )
    
    if campaign_creator.status != "invited":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Campaign invitation cannot be accepted"
        )
    
    # Update status
    from datetime import datetime
    campaign_creator.status = "accepted"
    campaign_creator.accepted_at = datetime.utcnow()
    campaign_creator.final_rate = campaign_creator.offered_rate
    
    await db.commit()
    await db.refresh(campaign_creator)
    
    return {"message": "Campaign invitation accepted successfully"}

@router.post("/me/campaigns/{campaign_creator_id}/decline")
async def decline_campaign_invitation(
    campaign_creator_id: int,
    current_creator: Creator = Depends(get_current_creator),
    db: AsyncSession = Depends(get_db)
):
    """Decline a campaign invitation"""
    result = await db.execute(
        select(CampaignCreator)
        .filter(
            CampaignCreator.id == campaign_creator_id,
            CampaignCreator.creator_id == current_creator.id
        )
    )
    campaign_creator = result.scalar_one_or_none()
    
    if not campaign_creator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign invitation not found"
        )
    
    if campaign_creator.status != "invited":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Campaign invitation cannot be declined"
        )
    
    # Update status
    campaign_creator.status = "declined"
    
    await db.commit()
    
    return {"message": "Campaign invitation declined"}