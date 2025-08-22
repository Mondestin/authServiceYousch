"""
Users endpoint for managing user accounts
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.user import User
from app.models.school import School
from app.models.school import Campus
from app.models.role import Role
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Create a new user account
    
    Args:
        user: User creation data
        db: Database session
        
    Returns:
        Created user information
        
    Raises:
        HTTPException: If user creation fails
    """
    try:
        # Validate school reference
        school = db.query(School).filter(School.id == user.school_id).first()
        if not school:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"School with ID {user.school_id} not found"
            )
        
        # Validate campus reference if provided
        if user.campus_id is not None:
            campus = db.query(Campus).filter(Campus.id == user.campus_id).first()
            if not campus:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Campus with ID {user.campus_id} not found"
                )
            
            # Campus must belong to the specified school
            if campus.school_id != user.school_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Campus must belong to the specified school"
                )
        
        # Validate role reference
        role = db.query(Role).filter(Role.id == user.role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role with ID {user.role_id} not found"
            )
        
        # Check if email already exists in the school
        existing_user = db.query(User).filter(
            User.school_id == user.school_id,
            User.email == user.email
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with email '{user.email}' already exists in this school"
            )
        
        # Check if username already exists in the school (if provided)
        if user.username:
            existing_user = db.query(User).filter(
                User.school_id == user.school_id,
                User.username == user.username
            ).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User with username '{user.username}' already exists in this school"
                )
        
        # Create new user
        db_user = User(
            school_id=user.school_id,
            campus_id=user.campus_id,
            role_id=user.role_id,
            email=user.email,
            username=user.username,
            phone=user.phone,
            hashed_password=user.hashed_password,
            first_name=user.first_name,
            last_name=user.last_name,
            date_of_birth=user.date_of_birth,
            gender=user.gender,
            profile_picture=user.profile_picture
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"User created successfully: {db_user.email}")
        return UserResponse.model_validate(db_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    school_id: Optional[int] = None,
    campus_id: Optional[int] = None,
    role_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
) -> List[UserResponse]:
    """
    Get list of users
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        school_id: Filter by school ID (optional)
        campus_id: Filter by campus ID (optional)
        role_id: Filter by role ID (optional)
        is_active: Filter by active status (optional)
        db: Database session
        
    Returns:
        List of users
    """
    try:
        query = db.query(User)
        
        if school_id is not None:
            query = query.filter(User.school_id == school_id)
        
        if campus_id is not None:
            query = query.filter(User.campus_id == campus_id)
        
        if role_id is not None:
            query = query.filter(User.role_id == role_id)
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        users = query.offset(skip).limit(limit).all()
        return [UserResponse.model_validate(user) for user in users]
        
    except Exception as e:
        logger.error(f"Failed to retrieve users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Get a specific user by ID
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        User information
        
    Raises:
        HTTPException: If user not found
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        return UserResponse.model_validate(user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user"
        )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Update a user
    
    Args:
        user_id: User ID
        user_update: Updated user data
        db: Database session
        
    Returns:
        Updated user information
        
    Raises:
        HTTPException: If user not found or update fails
    """
    try:
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        # Update fields
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"User {user_id} updated successfully")
        return UserResponse.model_validate(db_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update user {user_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a user
    
    Args:
        user_id: User ID
        db: Database session
        
    Raises:
        HTTPException: If user not found or deletion fails
    """
    try:
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        db.delete(db_user)
        db.commit()
        
        logger.info(f"User {user_id} deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete user {user_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        ) 