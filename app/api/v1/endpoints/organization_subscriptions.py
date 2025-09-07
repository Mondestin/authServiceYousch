"""
Organization subscription management endpoints for the AuthService
Includes CRUD operations for organization subscriptions
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload

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
    db: Session = Depends(get_db)
):
    """
    Get list of organization subscriptions with full service and tier details
    Optional org_id filter
    Public endpoint - no authentication required
    """
    try:
        # Query with joinedload to include service and tier details
        query = db.query(OrganizationSubscription).options(
            joinedload(OrganizationSubscription.service),
            joinedload(OrganizationSubscription.tier)
        )
        
        if org_id:
            query = query.filter(OrganizationSubscription.org_id == org_id)
        
        subscriptions = query.all()
        
        logger.info("Retrieved organization subscriptions", 
                   count=len(subscriptions),
                   org_id=org_id)
        
        return subscriptions
        
    except Exception as e:
        logger.error("Failed to retrieve organization subscriptions", 
                    error=str(e),
                    org_id=org_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve organization subscriptions"
        )


@router.post("/", response_model=OrganizationSubscriptionResponse, status_code=status.HTTP_201_CREATED)
def create_organization_subscription(
    subscription: OrganizationSubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new organization subscription
    Requires authentication
    """
    try:
        # Check if subscription already exists for this org and service
        existing = db.query(OrganizationSubscription).filter(
            OrganizationSubscription.org_id == subscription.org_id,
            OrganizationSubscription.service_id == subscription.service_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization already has a subscription for this service"
            )
        
        # Create new subscription
        db_subscription = OrganizationSubscription(**subscription.dict())
        db.add(db_subscription)
        db.commit()
        db.refresh(db_subscription)
        
        # Load with service and tier details
        db_subscription = db.query(OrganizationSubscription).options(
            joinedload(OrganizationSubscription.service),
            joinedload(OrganizationSubscription.tier)
        ).filter(OrganizationSubscription.id == db_subscription.id).first()
        
        logger.info("Created organization subscription", 
                   subscription_id=db_subscription.id,
                   org_id=subscription.org_id,
                   service_id=subscription.service_id,
                   tier_id=subscription.tier_id)
        
        return db_subscription
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("Failed to create organization subscription", 
                    error=str(e),
                    org_id=subscription.org_id,
                    service_id=subscription.service_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create organization subscription"
        )


@router.get("/{subscription_id}", response_model=OrganizationSubscriptionResponse)
def get_organization_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific organization subscription by ID
    Requires authentication
    """
    try:
        subscription = db.query(OrganizationSubscription).options(
            joinedload(OrganizationSubscription.service),
            joinedload(OrganizationSubscription.tier)
        ).filter(OrganizationSubscription.id == subscription_id).first()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization subscription not found"
            )
        
        logger.info("Retrieved organization subscription", 
                   subscription_id=subscription_id)
        
        return subscription
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to retrieve organization subscription", 
                    error=str(e),
                    subscription_id=subscription_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve organization subscription"
        )


@router.put("/{subscription_id}", response_model=OrganizationSubscriptionResponse)
def update_organization_subscription(
    subscription_id: int,
    subscription_update: OrganizationSubscriptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an organization subscription
    Requires authentication
    """
    try:
        # Get existing subscription
        db_subscription = db.query(OrganizationSubscription).filter(
            OrganizationSubscription.id == subscription_id
        ).first()
        
        if not db_subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization subscription not found"
            )
        
        # Update fields
        update_data = subscription_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_subscription, field, value)
        
        db.commit()
        db.refresh(db_subscription)
        
        # Load with service and tier details
        db_subscription = db.query(OrganizationSubscription).options(
            joinedload(OrganizationSubscription.service),
            joinedload(OrganizationSubscription.tier)
        ).filter(OrganizationSubscription.id == subscription_id).first()
        
        logger.info("Updated organization subscription", 
                   subscription_id=subscription_id,
                   updates=update_data)
        
        return db_subscription
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("Failed to update organization subscription", 
                    error=str(e),
                    subscription_id=subscription_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update organization subscription"
        )


@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_organization_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an organization subscription
    Requires authentication
    """
    try:
        # Get existing subscription
        db_subscription = db.query(OrganizationSubscription).filter(
            OrganizationSubscription.id == subscription_id
        ).first()
        
        if not db_subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization subscription not found"
            )
        
        db.delete(db_subscription)
        db.commit()
        
        logger.info("Deleted organization subscription", 
                   subscription_id=subscription_id)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("Failed to delete organization subscription", 
                    error=str(e),
                    subscription_id=subscription_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete organization subscription"
        )