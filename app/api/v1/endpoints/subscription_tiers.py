"""
Subscription tier management endpoints for the AuthService
Includes CRUD operations for subscription tiers
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.logging import get_logger
from app.models.user import User
from app.models.subscription_tier import SubscriptionTier
from app.schemas.subscription_tier import SubscriptionTierCreate, SubscriptionTierUpdate, SubscriptionTierResponse

# Get logger
logger = get_logger(__name__)

# Create router
router = APIRouter()


@router.get("/", response_model=List[SubscriptionTierResponse])
def get_subscription_tiers(
    service_id: Optional[int] = Query(None, description="Filter by service ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of subscription tiers
    Optional service_id filter
    Accessible by service_admin and super_admin
    """
    # TODO: Add service_admin and super_admin role checks
    # For now, allowing any authenticated user
    
    query = db.query(SubscriptionTier)
    if service_id:
        query = query.filter(SubscriptionTier.service_id == service_id)
    
    tiers = query.all()
    return tiers


@router.post("/", response_model=SubscriptionTierResponse, status_code=status.HTTP_201_CREATED)
def create_subscription_tier(
    tier_data: SubscriptionTierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new subscription tier
    Accessible by service_admin and super_admin
    """
    # TODO: Add service_admin and super_admin role checks
    # For now, allowing any authenticated user
    
    # Check if tier with same name already exists for this service
    existing_tier = db.query(SubscriptionTier).filter(
        SubscriptionTier.service_id == tier_data.service_id,
        SubscriptionTier.tier_name == tier_data.tier_name
    ).first()
    if existing_tier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subscription tier with this name already exists for this service"
        )
    
    # Create new subscription tier
    tier = SubscriptionTier(
        service_id=tier_data.service_id,
        tier_name=tier_data.tier_name,
        features=tier_data.features
    )
    
    db.add(tier)
    db.commit()
    db.refresh(tier)
    
    logger.info(f"Subscription tier created: {tier.tier_name} for service {tier.service_id} by user {current_user.id}")
    return tier


@router.get("/{tier_id}", response_model=SubscriptionTierResponse)
def get_subscription_tier(
    tier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific subscription tier by ID
    Accessible by service_admin and super_admin
    """
    # TODO: Add service_admin and super_admin role checks
    # For now, allowing any authenticated user
    
    tier = db.query(SubscriptionTier).filter(SubscriptionTier.id == tier_id).first()
    if not tier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription tier not found"
        )
    
    return tier


@router.put("/{tier_id}", response_model=SubscriptionTierResponse)
def update_subscription_tier(
    tier_id: int,
    tier_data: SubscriptionTierUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a subscription tier
    Accessible by service_admin and super_admin
    """
    # TODO: Add service_admin and super_admin role checks
    # For now, allowing any authenticated user
    
    tier = db.query(SubscriptionTier).filter(SubscriptionTier.id == tier_id).first()
    if not tier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription tier not found"
        )
    
    # Update tier fields
    if tier_data.tier_name is not None:
        # Check if new name conflicts with existing tier for the same service
        existing_tier = db.query(SubscriptionTier).filter(
            SubscriptionTier.service_id == tier.service_id,
            SubscriptionTier.tier_name == tier_data.tier_name,
            SubscriptionTier.id != tier_id
        ).first()
        if existing_tier:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subscription tier with this name already exists for this service"
            )
        tier.tier_name = tier_data.tier_name
    
    if tier_data.features is not None:
        tier.features = tier_data.features
    
    db.commit()
    db.refresh(tier)
    
    logger.info(f"Subscription tier updated: {tier.tier_name} by user {current_user.id}")
    return tier


@router.delete("/{tier_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subscription_tier(
    tier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a subscription tier
    Accessible by service_admin and super_admin
    """
    # TODO: Add service_admin and super_admin role checks
    # For now, allowing any authenticated user
    
    tier = db.query(SubscriptionTier).filter(SubscriptionTier.id == tier_id).first()
    if not tier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription tier not found"
        )
    
    tier_name = tier.tier_name
    db.delete(tier)
    db.commit()
    
    logger.info(f"Subscription tier deleted: {tier_name} by user {current_user.id}")