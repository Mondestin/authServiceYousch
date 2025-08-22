"""
Campuses endpoint for managing school campuses
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.school import Campus
from app.models.school import School
from app.schemas.campus import CampusCreate, CampusUpdate, CampusResponse
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/", response_model=CampusResponse, status_code=status.HTTP_201_CREATED)
async def create_campus(
    campus: CampusCreate,
    db: Session = Depends(get_db)
) -> CampusResponse:
    """
    Create a new campus for a school
    
    Args:
        campus: Campus creation data
        db: Database session
        
    Returns:
        Created campus information
        
    Raises:
        HTTPException: If campus creation fails or school not found
    """
    try:
        # Check if school exists
        school = db.query(School).filter(School.id == campus.school_id).first()
        if not school:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"School with ID {campus.school_id} not found"
            )
        
        # Create new campus
        db_campus = Campus(
            school_id=campus.school_id,
            name=campus.name,
            address_street=campus.address_street,
            address_city=campus.address_city,
            address_postal=campus.address_postal,
            address_country=campus.address_country,
            contact_email=campus.contact_email,
            contact_phone=campus.contact_phone
        )
        
        db.add(db_campus)
        db.commit()
        db.refresh(db_campus)
        
        logger.info(f"Campus created successfully: {db_campus.name} for school {campus.school_id}")
        return CampusResponse.model_validate(db_campus)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create campus: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create campus"
        )


@router.get("/", response_model=List[CampusResponse])
async def get_campuses(
    skip: int = 0,
    limit: int = 100,
    school_id: Optional[int] = None,
    db: Session = Depends(get_db)
) -> List[CampusResponse]:
    """
    Get list of campuses
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        school_id: Filter by school ID (optional)
        db: Database session
        
    Returns:
        List of campuses
    """
    try:
        query = db.query(Campus)
        
        if school_id is not None:
            query = query.filter(Campus.school_id == school_id)
        
        campuses = query.offset(skip).limit(limit).all()
        return [CampusResponse.model_validate(campus) for campus in campuses]
        
    except Exception as e:
        logger.error(f"Failed to retrieve campuses: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve campuses"
        )


@router.get("/{campus_id}", response_model=CampusResponse)
async def get_campus(
    campus_id: int,
    db: Session = Depends(get_db)
) -> CampusResponse:
    """
    Get a specific campus by ID
    
    Args:
        campus_id: Campus ID
        db: Database session
        
    Returns:
        Campus information
        
    Raises:
        HTTPException: If campus not found
    """
    try:
        campus = db.query(Campus).filter(Campus.id == campus_id).first()
        if not campus:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Campus with ID {campus_id} not found"
            )
        
        return CampusResponse.model_validate(campus)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve campus {campus_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve campus"
        )


@router.put("/{campus_id}", response_model=CampusResponse)
async def update_campus(
    campus_id: int,
    campus_update: CampusUpdate,
    db: Session = Depends(get_db)
) -> CampusResponse:
    """
    Update a campus
    
    Args:
        campus_id: Campus ID
        campus_update: Updated campus data
        db: Database session
        
    Returns:
        Updated campus information
        
    Raises:
        HTTPException: If campus not found or update fails
    """
    try:
        db_campus = db.query(Campus).filter(Campus.id == campus_id).first()
        if not db_campus:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Campus with ID {campus_id} not found"
            )
        
        # Update fields
        update_data = campus_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_campus, field, value)
        
        db.commit()
        db.refresh(db_campus)
        
        logger.info(f"Campus {campus_id} updated successfully")
        return CampusResponse.model_validate(db_campus)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update campus {campus_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update campus"
        )


@router.delete("/{campus_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campus(
    campus_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a campus
    
    Args:
        campus_id: Campus ID
        db: Database session
        
    Raises:
        HTTPException: If campus not found or deletion fails
    """
    try:
        db_campus = db.query(Campus).filter(Campus.id == campus_id).first()
        if not db_campus:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Campus with ID {campus_id} not found"
            )
        
        db.delete(db_campus)
        db.commit()
        
        logger.info(f"Campus {campus_id} deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete campus {campus_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete campus"
        ) 