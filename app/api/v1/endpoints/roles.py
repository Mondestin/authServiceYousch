"""
Roles and Permissions endpoint for managing RBAC
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.role import Role, Permission, RolePermission
from app.models.school import School
from app.models.school import Campus
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse, PermissionResponse
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role: RoleCreate,
    db: Session = Depends(get_db)
) -> RoleResponse:
    """
    Create a new role
    
    Args:
        role: Role creation data
        db: Database session
        
    Returns:
        Created role information
        
    Raises:
        HTTPException: If role creation fails
    """
    try:
        # Validate school and campus references
        if role.school_id is not None:
            school = db.query(School).filter(School.id == role.school_id).first()
            if not school:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"School with ID {role.school_id} not found"
                )
        
        if role.campus_id is not None:
            campus = db.query(Campus).filter(Campus.id == role.campus_id).first()
            if not campus:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Campus with ID {role.campus_id} not found"
                )
            
            # If campus is specified, school_id must match
            if role.school_id is None or role.school_id != campus.school_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Campus must belong to the specified school"
                )
        
        # Create new role
        db_role = Role(
            school_id=role.school_id,
            campus_id=role.campus_id,
            name=role.name,
            description=role.description,
            is_default=role.is_default
        )
        
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
        
        logger.info(f"Role created successfully: {db_role.name}")
        return RoleResponse.model_validate(db_role)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create role: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create role"
        )


@router.get("/", response_model=List[RoleResponse])
async def get_roles(
    skip: int = 0,
    limit: int = 100,
    school_id: Optional[int] = None,
    campus_id: Optional[int] = None,
    db: Session = Depends(get_db)
) -> List[RoleResponse]:
    """
    Get list of roles
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        school_id: Filter by school ID (optional)
        campus_id: Filter by campus ID (optional)
        db: Database session
        
    Returns:
        List of roles
    """
    try:
        query = db.query(Role)
        
        if school_id is not None:
            query = query.filter(Role.school_id == school_id)
        
        if campus_id is not None:
            query = query.filter(Role.campus_id == campus_id)
        
        roles = query.offset(skip).limit(limit).all()
        return [RoleResponse.model_validate(role) for role in roles]
        
    except Exception as e:
        logger.error(f"Failed to retrieve roles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve roles"
        )


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    db: Session = Depends(get_db)
) -> RoleResponse:
    """
    Get a specific role by ID
    
    Args:
        role_id: Role ID
        db: Database session
        
    Returns:
        Role information
        
    Raises:
        HTTPException: If role not found
    """
    try:
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role with ID {role_id} not found"
            )
        
        return RoleResponse.model_validate(role)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve role {role_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve role"
        )


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_update: RoleUpdate,
    db: Session = Depends(get_db)
) -> RoleResponse:
    """
    Update a role
    
    Args:
        role_id: Role ID
        role_update: Updated role data
        db: Database session
        
    Returns:
        Updated role information
        
    Raises:
        HTTPException: If role not found or update fails
    """
    try:
        db_role = db.query(Role).filter(Role.id == role_id).first()
        if not db_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role with ID {role_id} not found"
            )
        
        # Update fields
        update_data = role_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_role, field, value)
        
        db.commit()
        db.refresh(db_role)
        
        logger.info(f"Role {role_id} updated successfully")
        return RoleResponse.model_validate(db_role)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update role {role_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update role"
        )


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a role
    
    Args:
        role_id: Role ID
        db: Database session
        
    Raises:
        HTTPException: If role not found or deletion fails
    """
    try:
        db_role = db.query(Role).filter(Role.id == role_id).first()
        if not db_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role with ID {role_id} not found"
            )
        
        db.delete(db_role)
        db.commit()
        
        logger.info(f"Role {role_id} deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete role {role_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete role"
        )


@router.get("/permissions/", response_model=List[PermissionResponse])
async def get_permissions(
    db: Session = Depends(get_db)
) -> List[PermissionResponse]:
    """
    Get list of all permissions
    
    Args:
        db: Database session
        
    Returns:
        List of permissions
    """
    try:
        permissions = db.query(Permission).all()
        return [PermissionResponse.model_validate(permission) for permission in permissions]
        
    except Exception as e:
        logger.error(f"Failed to retrieve permissions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve permissions"
        ) 