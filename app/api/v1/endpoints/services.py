"""
Service management endpoints for the AuthService
Includes CRUD operations for services
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.logging import get_logger
from app.models.user import User
from app.models.service import Service
from app.schemas.service import ServiceCreate, ServiceUpdate, ServiceResponse

# Get logger
logger = get_logger(__name__)

# Create router
router = APIRouter()


@router.get("/", response_model=List[ServiceResponse])
def get_services(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of all services
    Accessible by any authenticated user
    """
    services = db.query(Service).all()
    return services


@router.post("/", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
def create_service(
    service_data: ServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new service
    Only accessible by super_admin
    """
    # TODO: Add super_admin role check
    # For now, allowing any authenticated user
    
    # Check if service with same name already exists
    existing_service = db.query(Service).filter(Service.name == service_data.name).first()
    if existing_service:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Service with this name already exists"
        )
    
    # Create new service
    service = Service(
        name=service_data.name,
        description=service_data.description,
        status=service_data.status
    )
    
    db.add(service)
    db.commit()
    db.refresh(service)
    
    logger.info(f"Service created: {service.name} by user {current_user.id}")
    return service


@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific service by ID
    Accessible by any authenticated user
    """
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    return service


@router.put("/{service_id}", response_model=ServiceResponse)
def update_service(
    service_id: int,
    service_data: ServiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a service
    Only accessible by super_admin
    """
    # TODO: Add super_admin role check
    # For now, allowing any authenticated user
    
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    # Update service fields
    if service_data.name is not None:
        # Check if new name conflicts with existing service
        existing_service = db.query(Service).filter(
            Service.name == service_data.name,
            Service.id != service_id
        ).first()
        if existing_service:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Service with this name already exists"
            )
        service.name = service_data.name
    
    if service_data.description is not None:
        service.description = service_data.description
    
    if service_data.status is not None:
        service.status = service_data.status
    
    db.commit()
    db.refresh(service)
    
    logger.info(f"Service updated: {service.name} by user {current_user.id}")
    return service


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a service
    Only accessible by super_admin
    """
    # TODO: Add super_admin role check
    # For now, allowing any authenticated user
    
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    service_name = service.name
    db.delete(service)
    db.commit()
    
    logger.info(f"Service deleted: {service_name} by user {current_user.id}")