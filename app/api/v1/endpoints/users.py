"""
Users endpoint for managing user accounts
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.organization import Organization
from app.models.user_role import UserRole
from app.models.role import Role
from app.schemas.user import UserUpdate, UserResponse
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/", response_model=List[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[UserResponse]:
    """
    Get list of users
    Accessible by org_admin and super_admin
    """
    # TODO: Add org_admin and super_admin role checks
    # For now, allowing any authenticated user
    
    users = db.query(User).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Get a specific user by ID
    Accessible by org_admin and super_admin
    """
    # TODO: Add org_admin and super_admin role checks
    # For now, allowing any authenticated user
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Update a user
    Accessible by org_admin and super_admin
    """
    # TODO: Add org_admin and super_admin role checks
    # For now, allowing any authenticated user
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user fields
    if user_data.email is not None:
        # Check if new email conflicts with existing user
        existing_user = db.query(User).filter(
            User.email == user_data.email,
            User.id != user_id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
        user.email = user_data.email
    
    if user_data.first_name is not None:
        user.first_name = user_data.first_name
    
    if user_data.last_name is not None:
        user.last_name = user_data.last_name
    
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    
    # Update roles if provided
    if user_data.roles is not None:
        # Remove existing user roles
        db.query(UserRole).filter(UserRole.user_id == user_id).delete()
        
        # Add new user roles
        for role_id in user_data.roles:
            user_role = UserRole(user_id=user_id, role_id=role_id)
            db.add(user_role)
    
    db.commit()
    db.refresh(user)
    
    logger.info(f"User updated: {user.email} by user {current_user.id}")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Delete a user
    Accessible by org_admin and super_admin
    """
    # TODO: Add org_admin and super_admin role checks
    # For now, allowing any authenticated user
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_email = user.email
    db.delete(user)
    db.commit()
    
    logger.info(f"User deleted: {user_email} by user {current_user.id}")