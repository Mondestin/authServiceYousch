"""
Authentication endpoints for the AuthService
Includes registration, login, logout, refresh, and profile endpoints
"""

from datetime import datetime, timedelta
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

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
    Get current user profile with roles and organization info
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        UserProfileResponse: User profile with roles and organization info
    """
    # Get user's organization
    organization = db.query(Organization).filter(Organization.id == current_user.org_id).first()
    
    # Get user's roles
    user_roles = db.query(UserRole).filter(UserRole.user_id == current_user.id).all()
    roles = []
    for user_role in user_roles:
        role = db.query(Role).filter(Role.id == user_role.role_id).first()
        if role:
            roles.append({
                "id": role.id,
                "name": role.name,
                "service_id": role.service_id,
                "permissions": role.permissions
            })
    
    # Get organization subscriptions
    subscriptions = db.query(OrganizationSubscription).filter(
        OrganizationSubscription.org_id == current_user.org_id,
        OrganizationSubscription.is_active == True
    ).all()
    
    subscription_info = []
    for sub in subscriptions:
        subscription_info.append({
            "service_id": sub.service_id,
            "tier_id": sub.tier_id,
            "start_date": sub.start_date,
            "end_date": sub.end_date
        })
    
    return UserProfileResponse(
        user=current_user.to_dict(),
        roles=roles,
        organization=organization.to_dict() if organization else None,
        subscriptions=subscription_info
    )