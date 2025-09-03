"""
Organization subscription management endpoints for the AuthService
Includes CRUD operations for organization subscriptions
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.logging import get_logger
from app.models.user import User
from app.models.organization_subscription import OrganizationSubscription
from app.schemas.organization_subscription import (
    OrganizationSubscriptionCreate, 
    OrganizationSubscriptionUpdate, 
    OrganizationSubscriptionResponse
)

# Get logger
logger = get_logger(__name__)

# Create router
router = APIRouter()


@router.get("/", response_model=List[OrganizationSubscriptionResponse])
def get_organization_subscriptions(
    org_id: Optional[int] = Query(None, description="Filter by organization ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of organization subscriptions
    Optional org_id filter
    Accessible by org_admin and super_admin
    """
    # TODO: Add org_admin and super_admin role checks
    # For now, allowing any authenticated user
    
    query = db.query(OrganizationSubscription)
    if org_id:
        query = query.filter(OrganizationSubscription.org_id == org_id)
    
    subscriptions = query.all()
    return subscriptions


@router.post("/", response_model=OrganizationSubscriptionResponse, status_code=status.HTTP_201_CREATED)
def create_organization_subscription(
    subscription_data: OrganizationSubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new organization subscription
    Accessible by org_admin and super_admin
    """
    # TODO: Add org_admin and super_admin role checks
    # For now, allowing any authenticated user
    
    # Check if organization already has a subscription for this service
    existing_subscription = db.query(OrganizationSubscription).filter(
        OrganizationSubscription.org_id == subscription_data.org_id,
        OrganizationSubscription.service_id == subscription_data.service_id
    ).first()
    if existing_subscription:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization already has a subscription for this service"
        )
    
    # Create new organization subscription
    subscription = OrganizationSubscription(
        org_id=subscription_data.org_id,
        service_id=subscription_data.service_id,
        tier_id=subscription_data.tier_id,
        start_date=subscription_data.start_date,
        end_date=subscription_data.end_date,
        is_active=subscription_data.is_active if subscription_data.is_active is not None else True
    )
    
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    
    logger.info(f"Organization subscription created: org {subscription.org_id} for service {subscription.service_id} by user {current_user.id}")
    return subscription


@router.get("/{subscription_id}", response_model=OrganizationSubscriptionResponse)
def get_organization_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific organization subscription by ID
    Accessible by org_admin and super_admin
    """
    # TODO: Add org_admin and super_admin role checks
    # For now, allowing any authenticated user
    
    subscription = db.query(OrganizationSubscription).filter(
        OrganizationSubscription.id == subscription_id
    ).first()
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization subscription not found"
        )
    
    return subscription


@router.put("/{subscription_id}", response_model=OrganizationSubscriptionResponse)
def update_organization_subscription(
    subscription_id: int,
    subscription_data: OrganizationSubscriptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an organization subscription
    Accessible by org_admin and super_admin
    """
    # TODO: Add org_admin and super_admin role checks
    # For now, allowing any authenticated user
    
    subscription = db.query(OrganizationSubscription).filter(
        OrganizationSubscription.id == subscription_id
    ).first()
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization subscription not found"
        )
    
    # Update subscription fields
    if subscription_data.tier_id is not None:
        subscription.tier_id = subscription_data.tier_id
    
    if subscription_data.start_date is not None:
        subscription.start_date = subscription_data.start_date
    
    if subscription_data.end_date is not None:
        subscription.end_date = subscription_data.end_date
    
    if subscription_data.is_active is not None:
        subscription.is_active = subscription_data.is_active
    
    db.commit()
    db.refresh(subscription)
    
    logger.info(f"Organization subscription updated: {subscription.id} by user {current_user.id}")
    return subscription


@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_organization_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an organization subscription
    Only accessible by super_admin
    """
    # TODO: Add super_admin role check
    # For now, allowing any authenticated user
    
    subscription = db.query(OrganizationSubscription).filter(
        OrganizationSubscription.id == subscription_id
    ).first()
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization subscription not found"
        )
    
    subscription_id_val = subscription.id
    db.delete(subscription)
    db.commit()
    
    logger.info(f"Organization subscription deleted: {subscription_id_val} by user {current_user.id}")