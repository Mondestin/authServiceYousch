"""
Roles endpoint for managing service-specific roles
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.role import Role
from app.models.service import Service
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/", response_model=List[RoleResponse])
def get_roles(
    service_id: Optional[int] = Query(None, description="Filter by service ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[RoleResponse]:
    """
    Get list of roles
    Optional service_id filter
    Accessible by service_admin and super_admin
    """
    # TODO: Add service_admin and super_admin role checks
    # For now, allowing any authenticated user
    
    query = db.query(Role)
    if service_id:
        query = query.filter(Role.service_id == service_id)
    
    roles = query.all()
    return roles


@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(
    role_data: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> RoleResponse:
    """
    Create a new role
    Accessible by service_admin and super_admin
    """
    # TODO: Add service_admin and super_admin role checks
    # For now, allowing any authenticated user
    
    # Validate service exists
    service = db.query(Service).filter(Service.id == role_data.service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    # Check if role with same name already exists for this service
    existing_role = db.query(Role).filter(
        Role.service_id == role_data.service_id,
        Role.name == role_data.name
    ).first()
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role with this name already exists for this service"
        )
    
    # Create new role
    role = Role(
        name=role_data.name,
        service_id=role_data.service_id,
        permissions=role_data.permissions
    )
    
    db.add(role)
    db.commit()
    db.refresh(role)
    
    logger.info(f"Role created: {role.name} for service {role.service_id} by user {current_user.id}")
    return role


@router.get("/{role_id}", response_model=RoleResponse)
def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> RoleResponse:
    """
    Get a specific role by ID
    Accessible by service_admin and super_admin
    """
    # TODO: Add service_admin and super_admin role checks
    # For now, allowing any authenticated user
    
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    return role


@router.put("/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: int,
    role_data: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> RoleResponse:
    """
    Update a role
    Accessible by service_admin and super_admin
    """
    # TODO: Add service_admin and super_admin role checks
    # For now, allowing any authenticated user
    
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Update role fields
    if role_data.name is not None:
        # Check if new name conflicts with existing role for the same service
        existing_role = db.query(Role).filter(
            Role.service_id == role.service_id,
            Role.name == role_data.name,
            Role.id != role_id
        ).first()
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role with this name already exists for this service"
            )
        role.name = role_data.name
    
    if role_data.permissions is not None:
        role.permissions = role_data.permissions
    
    db.commit()
    db.refresh(role)
    
    logger.info(f"Role updated: {role.name} by user {current_user.id}")
    return role


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Delete a role
    Accessible by service_admin and super_admin
    """
    # TODO: Add service_admin and super_admin role checks
    # For now, allowing any authenticated user
    
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    role_name = role.name
    db.delete(role)
    db.commit()
    
    logger.info(f"Role deleted: {role_name} by user {current_user.id}")