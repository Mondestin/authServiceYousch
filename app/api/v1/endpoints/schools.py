"""
Schools endpoint for managing multi-tenant schools
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.school import School
from app.schemas.school import SchoolCreate, SchoolUpdate, SchoolResponse
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/", response_model=SchoolResponse, status_code=status.HTTP_201_CREATED)
async def create_school(
    school: SchoolCreate,
    db: Session = Depends(get_db)
) -> SchoolResponse:
    """
    Create a new school (tenant)
    
    Args:
        school: School creation data
        db: Database session
        
    Returns:
        Created school information
        
    Raises:
        HTTPException: If school creation fails
    """
    try:
        # Check if school with same code already exists
        existing_school = db.query(School).filter(School.code == school.code).first()
        if existing_school:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"School with code '{school.code}' already exists"
            )
        
        # Create new school
        db_school = School(
            name=school.name,
            code=school.code,
            domain=school.domain
        )
        
        db.add(db_school)
        db.commit()
        db.refresh(db_school)
        
        logger.info(f"School created successfully: {db_school.code}")
        return SchoolResponse.model_validate(db_school)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create school: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create school"
        )


@router.get("/", response_model=List[SchoolResponse])
async def get_schools(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> List[SchoolResponse]:
    """
    Get list of all schools
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of schools
    """
    try:
        schools = db.query(School).offset(skip).limit(limit).all()
        return [SchoolResponse.model_validate(school) for school in schools]
        
    except Exception as e:
        logger.error(f"Failed to retrieve schools: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve schools"
        )


@router.get("/{school_id}", response_model=SchoolResponse)
async def get_school(
    school_id: int,
    db: Session = Depends(get_db)
) -> SchoolResponse:
    """
    Get a specific school by ID
    
    Args:
        school_id: School ID
        db: Database session
        
    Returns:
        School information
        
    Raises:
        HTTPException: If school not found
    """
    try:
        school = db.query(School).filter(School.id == school_id).first()
        if not school:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"School with ID {school_id} not found"
            )
        
        return SchoolResponse.model_validate(school)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve school {school_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve school"
        )


@router.put("/{school_id}", response_model=SchoolResponse)
async def update_school(
    school_id: int,
    school_update: SchoolUpdate,
    db: Session = Depends(get_db)
) -> SchoolResponse:
    """
    Update a school
    
    Args:
        school_id: School ID
        school_update: Updated school data
        db: Database session
        
    Returns:
        Updated school information
        
    Raises:
        HTTPException: If school not found or update fails
    """
    try:
        db_school = db.query(School).filter(School.id == school_id).first()
        if not db_school:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"School with ID {school_id} not found"
            )
        
        # Update fields
        update_data = school_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_school, field, value)
        
        db.commit()
        db.refresh(db_school)
        
        logger.info(f"School {school_id} updated successfully")
        return SchoolResponse.model_validate(db_school)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update school {school_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update school"
        )


@router.delete("/{school_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_school(
    school_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a school
    
    Args:
        school_id: School ID
        db: Database session
        
    Raises:
        HTTPException: If school not found or deletion fails
    """
    try:
        db_school = db.query(School).filter(School.id == school_id).first()
        if not db_school:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"School with ID {school_id} not found"
            )
        
        db.delete(db_school)
        db.commit()
        
        logger.info(f"School {school_id} deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete school {school_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete school"
        ) 