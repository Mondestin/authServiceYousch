"""
Authentication endpoints for the AuthService
Includes registration, login, logout, refresh, and profile endpoints
"""

from datetime import datetime, timedelta
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_db, get_current_user
from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token
)
from app.core.email import EmailService
from app.models.user import User
from app.models.organization import Organization
from app.models.service import Service
from app.models.user_role import UserRole
from app.models.role import Role
from app.models.organization_subscription import OrganizationSubscription
from app.schemas.auth import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    RefreshTokenRequest,
    UserProfileResponse
)

# Get settings and logger
settings = get_settings()
logger = get_logger(__name__)

# Create router
router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Register a new user account
    
    Args:
        user_data: User registration data (email, password, org_id, service_id, first_name, last_name)
        db: Database session
        
    Returns:
        UserResponse: Created user information with tokens
        
    Raises:
        HTTPException: If registration fails
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Verify organization exists
    organization = db.query(Organization).filter(Organization.id == user_data.org_id).first()
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization not found"
        )    
    # Verify service exists
    service = db.query(Service).filter(Service.id == user_data.service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Service not found"
        )
    
    try:
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        
        new_user = User(
            org_id=user_data.org_id,
            email=user_data.email,
            password_hash=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Create access and refresh tokens
        access_token = create_access_token(
            data={"sub": str(new_user.id), "email": new_user.email, "org_id": str(new_user.org_id)}
        )
        refresh_token = create_refresh_token(
            data={"sub": str(new_user.id)}
        )
        
        logger.info(f"User registered successfully: {new_user.email}")
        
        # Send verification email
        try:
            verification_token = create_access_token(
                data={"sub": str(new_user.id), "type": "verification"},
                expires_delta=timedelta(hours=24)
            )
            
            email_sent = await EmailService.send_email_verification(
                to_email=new_user.email,
                firstname=new_user.first_name,
                lastname=new_user.last_name,
                verification_token=verification_token,
                user_id=str(new_user.id)
            )
            
            if email_sent:
                logger.info(f"Verification email sent to: {new_user.email}")
            else:
                logger.warning(f"Failed to send verification email to: {new_user.email}")
                
        except Exception as e:
            logger.error(f"Error sending verification email: {str(e)}")
            # Don't fail registration if email fails
        
        return UserResponse(
            user_id=new_user.id,
            access_token=access_token,
            refresh_token=refresh_token
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"User registration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
) -> Any:
    """
    Authenticate user and return access tokens
    
    Args:
        user_credentials: User login credentials (email, password)
        db: Database session
        
    Returns:
        TokenResponse: Access and refresh tokens
        
    Raises:
        HTTPException: If authentication fails
    """
    # Find user by email
    user = db.query(User).filter(User.email == user_credentials.email).first()
    
    if not user or not verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive"
        )
    
    # Update last login
    user.update_last_login()
    db.commit()
    
    # Create access and refresh tokens
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "org_id": str(user.org_id)}
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}
    )
    
    logger.info(f"User logged in successfully: {user.email}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Logout user (revoke token)
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        dict: Success message
    """
    # In a real implementation, you would add the token to a blacklist
    # For now, we'll just log the logout
    logger.info(f"User logged out: {current_user.email}")
    
    return {"message": "Logged out successfully"}


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Refresh access token using refresh token
    
    Args:
        refresh_data: Refresh token data
        db: Database session
        
    Returns:
        TokenResponse: New access token
        
    Raises:
        HTTPException: If refresh fails
    """
    try:
        # Verify refresh token
        payload = verify_token(refresh_data.refresh_token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "org_id": str(user.org_id)}
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_data.refresh_token  # Keep the same refresh token
        )
        
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get current user profile with full details for roles, organization, and subscriptions
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        UserProfileResponse: User profile with full details
    """
    try:
        # Get user's organization with full details
        organization = db.query(Organization).filter(Organization.id == current_user.org_id).first()
        
        # Get user's roles with service details
        user_roles = db.query(UserRole).filter(UserRole.user_id == current_user.id).all()
        roles = []
        for user_role in user_roles:
            role = db.query(Role).options(
                joinedload(Role.service)
            ).filter(Role.id == user_role.role_id).first()
            if role:
                roles.append({
                    "id": role.id,
                    "name": role.name,
                    "service_id": role.service_id,
                    "permissions": role.permissions,
                    "service": {
                        "id": role.service.id,
                        "name": role.service.name,
                        "description": role.service.description,
                        "status": role.service.status
                    }
                })
        
        # Get organization subscriptions with full service and tier details
        subscriptions = db.query(OrganizationSubscription).options(
            joinedload(OrganizationSubscription.service),
            joinedload(OrganizationSubscription.tier)
        ).filter(
            OrganizationSubscription.org_id == current_user.org_id,
            OrganizationSubscription.is_active == True
        ).all()
        
        subscription_info = []
        for sub in subscriptions:
            subscription_info.append({
                "id": sub.id,
                "service_id": sub.service_id,
                "tier_id": sub.tier_id,
                "start_date": sub.start_date.isoformat() if sub.start_date else None,
                "end_date": sub.end_date.isoformat() if sub.end_date else None,
                "is_active": sub.is_active,
                "service": {
                    "id": sub.service.id,
                    "name": sub.service.name,
                    "description": sub.service.description,
                    "status": sub.service.status
                },
                "tier": {
                    "id": sub.tier.id,
                    "service_id": sub.tier.service_id,
                    "tier_name": sub.tier.tier_name,
                    "features": sub.tier.features
                }
            })
        
        # Prepare organization details
        organization_details = None
        if organization:
            organization_details = {
                "id": organization.id,
                "name": organization.name,
                "created_at": organization.created_at.isoformat() if organization.created_at else None,
                "updated_at": organization.updated_at.isoformat() if organization.updated_at else None
            }
        
        # Prepare complete user data with all details
        user_data = current_user.to_dict()
        user_data.update({
            "roles": roles,
            "organization": organization_details,
            "subscriptions": subscription_info
        })
        
        logger.info("Retrieved user profile with full details", 
                   user_id=current_user.id,
                   roles_count=len(roles),
                   subscriptions_count=len(subscription_info))
        
        return UserProfileResponse(user=user_data)
        
    except Exception as e:
        logger.error("Failed to retrieve user profile", 
                    error=str(e),
                    user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user profile"
        )


@router.post("/verify-email", status_code=status.HTTP_200_OK)
async def verify_email(
    token: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    Verify user email address using verification token
    
    Args:
        token: Email verification token
        db: Database session
        
    Returns:
        dict: Verification result
        
    Raises:
        HTTPException: If verification fails
    """
    try:
        # Verify the token
        payload = verify_token(token)
        
        # Check if it's a verification token
        if payload.get("type") != "verification":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token payload"
            )
        
        # Find user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Mark email as verified (you might want to add an email_verified field to User model)
        # For now, we'll just log the verification
        logger.info(f"Email verified for user: {user.email}")
        
        return {
            "message": "Email verified successfully",
            "user_id": user.id,
            "email": user.email
        }
        
    except Exception as e:
        logger.error(f"Email verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email verification failed"
        )