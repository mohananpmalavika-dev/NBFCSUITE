"""
HRMS Training & Development API Router
FastAPI routes for training operations
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import date
import math

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user
from .training_service import TrainingService
from .training_schemas import (
    TrainingCourseCreate, TrainingCourseUpdate, TrainingCourseResponse,
    TrainingCourseListItem, PaginatedTrainingCourseResponse,
    TrainingSessionCreate, TrainingSessionUpdate, TrainingSessionResponse,
    TrainingSessionListItem, PaginatedTrainingSessionResponse,
    TrainingParticipantCreate, TrainingParticipantUpdate, TrainingParticipantResponse,
    PaginatedParticipantResponse,
    TrainingCertificationCreate, TrainingCertificationResponse,
    SkillCreate, SkillResponse,
    EmployeeSkillCreate, EmployeeSkillResponse,
    TrainingDashboardStats, TrainingCalendarItem,
    TrainingTypeEnum, TrainingCategoryEnum, TrainingStatusEnum, ParticipantStatusEnum
)

router = APIRouter(prefix="/hrms/training", tags=["HRMS - Training & Development"])


def get_training_service(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
) -> TrainingService:
    """Dependency to get training service"""
    return TrainingService(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id
    )


# ============================================================================
# TRAINING COURSE ENDPOINTS
# ============================================================================

@router.post("/courses", response_model=TrainingCourseResponse, status_code=status.HTTP_201_CREATED)
async def create_training_course(
    data: TrainingCourseCreate,
    service: TrainingService = Depends(get_training_service)
):
    """
    Create new training course
    
    - Auto-generates course code (TRN-YYYYMM-XXXX)
    - Supports internal and external trainers
    - LMS integration ready
    - Certificate configuration
    """
    try:
        course = await service.create_training_course(data)
        return course
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/courses", response_model=PaginatedTrainingCourseResponse)
async def get_training_courses(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name, code"),
    training_type: Optional[TrainingTypeEnum] = Query(None),
    training_category: Optional[TrainingCategoryEnum] = Query(None),
    is_active: Optional[bool] = Query(None),
    is_published: Optional[bool] = Query(None),
    is_mandatory: Optional[bool] = Query(None),
    service: TrainingService = Depends(get_training_service)
):
    """
    Get paginated list of training courses
    
    Filters:
    - Search by name, code, description
    - Training type and category
    - Active status
    - Published status
    - Mandatory/compliance training
    """
    courses, total = await service.get_training_courses(
        page=page,
        page_size=page_size,
        search=search,
        training_type=training_type,
        training_category=training_category,
        is_active=is_active,
        is_published=is_published,
        is_mandatory=is_mandatory
    )
    
    pages = math.ceil(total / page_size) if total > 0 else 0
    
    return PaginatedTrainingCourseResponse(
        items=courses,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )


@router.get("/courses/{course_id}", response_model=TrainingCourseResponse)
async def get_training_course(
    course_id: str,
    service: TrainingService = Depends(get_training_service)
):
    """Get training course details"""
    course = await service.get_training_course(course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training course not found"
        )
    return course


@router.put("/courses/{course_id}", response_model=TrainingCourseResponse)
async def update_training_course(
    course_id: str,
    data: TrainingCourseUpdate,
    service: TrainingService = Depends(get_training_service)
):
    """Update training course"""
    try:
        course = await service.update_training_course(course_id, data)
        return course
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_training_course(
    course_id: str,
    service: TrainingService = Depends(get_training_service)
):
    """Delete training course (soft delete)"""
    try:
        await service.delete_training_course(course_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )



# ============================================================================
# TRAINING SESSION ENDPOINTS
# ============================================================================

@router.post("/sessions", response_model=TrainingSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_training_session(
    data: TrainingSessionCreate,
    service: TrainingService = Depends(get_training_service)
):
    """
    Create new training session
    
    - Schedule training delivery
    - Physical, virtual, or hybrid sessions
    - Capacity management
    - Trainer assignment
    """
    try:
        session = await service.create_training_session(data)
        return session
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/sessions", response_model=PaginatedTrainingSessionResponse)
async def get_training_sessions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    course_id: Optional[str] = Query(None),
    status: Optional[TrainingStatusEnum] = Query(None),
    start_date_from: Optional[date] = Query(None),
    start_date_to: Optional[date] = Query(None),
    service: TrainingService = Depends(get_training_service)
):
    """Get paginated list of training sessions"""
    sessions, total = await service.get_training_sessions(
        page=page,
        page_size=page_size,
        course_id=course_id,
        status=status,
        start_date_from=start_date_from,
        start_date_to=start_date_to
    )
    
    pages = math.ceil(total / page_size) if total > 0 else 0
    
    return PaginatedTrainingSessionResponse(
        items=sessions,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )


@router.get("/sessions/{session_id}", response_model=TrainingSessionResponse)
async def get_training_session(
    session_id: str,
    service: TrainingService = Depends(get_training_service)
):
    """Get training session details"""
    session = await service.get_training_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training session not found"
        )
    return session


@router.put("/sessions/{session_id}", response_model=TrainingSessionResponse)
async def update_training_session(
    session_id: str,
    data: TrainingSessionUpdate,
    service: TrainingService = Depends(get_training_service)
):
    """Update training session"""
    try:
        session = await service.update_training_session(session_id, data)
        return session
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/calendar", response_model=List[TrainingCalendarItem])
async def get_training_calendar(
    start_date: date = Query(..., description="Calendar start date"),
    end_date: date = Query(..., description="Calendar end date"),
    service: TrainingService = Depends(get_training_service)
):
    """
    Get training calendar for date range
    
    Returns all scheduled and ongoing training sessions
    in the specified date range
    """
    calendar_items = await service.get_training_calendar(start_date, end_date)
    return calendar_items


# ============================================================================
# PARTICIPANT ENDPOINTS
# ============================================================================

@router.post("/participants", response_model=TrainingParticipantResponse, status_code=status.HTTP_201_CREATED)
async def create_participant(
    data: TrainingParticipantCreate,
    service: TrainingService = Depends(get_training_service)
):
    """
    Nominate employee for training
    
    - Register employees for sessions
    - Track nomination and attendance
    """
    try:
        participant = await service.create_participant(data)
        return participant
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/sessions/{session_id}/participants", response_model=List[TrainingParticipantResponse])
async def get_session_participants(
    session_id: str,
    status: Optional[ParticipantStatusEnum] = Query(None),
    service: TrainingService = Depends(get_training_service)
):
    """Get all participants for a training session"""
    participants = await service.get_session_participants(session_id, status)
    return participants


@router.put("/participants/{participant_id}", response_model=TrainingParticipantResponse)
async def update_participant(
    participant_id: str,
    data: TrainingParticipantUpdate,
    service: TrainingService = Depends(get_training_service)
):
    """Update participant status and details"""
    try:
        participant = await service.update_participant(participant_id, data)
        return participant
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ============================================================================
# CERTIFICATION ENDPOINTS
# ============================================================================

@router.post("/certifications", response_model=TrainingCertificationResponse, status_code=status.HTTP_201_CREATED)
async def issue_certificate(
    employee_id: str = Query(...),
    course_id: str = Query(...),
    session_id: Optional[str] = Query(None),
    validity_months: Optional[int] = Query(None),
    service: TrainingService = Depends(get_training_service)
):
    """
    Issue training certificate to employee
    
    - Auto-generates certificate number
    - Sets validity period
    - Tracks certificate status
    """
    try:
        certificate = await service.issue_certificate(
            employee_id=employee_id,
            course_id=course_id,
            session_id=session_id,
            validity_months=validity_months
        )
        return certificate
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/employees/{employee_id}/certifications", response_model=List[TrainingCertificationResponse])
async def get_employee_certifications(
    employee_id: str,
    service: TrainingService = Depends(get_training_service)
):
    """Get all certifications for an employee"""
    certifications = await service.get_employee_certifications(employee_id)
    return certifications


# ============================================================================
# SKILL MATRIX ENDPOINTS
# ============================================================================

@router.post("/skills", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
async def create_skill(
    data: SkillCreate,
    service: TrainingService = Depends(get_training_service)
):
    """Create new skill"""
    try:
        skill = await service.create_skill(
            skill_name=data.skill_name,
            skill_category=data.skill_category,
            skill_description=data.skill_description
        )
        return skill
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/employee-skills", response_model=EmployeeSkillResponse, status_code=status.HTTP_201_CREATED)
async def add_employee_skill(
    data: EmployeeSkillCreate,
    service: TrainingService = Depends(get_training_service)
):
    """Add skill to employee skill matrix"""
    try:
        employee_skill = await service.add_employee_skill(
            employee_id=data.employee_id,
            skill_id=data.skill_id,
            proficiency_level=data.proficiency_level,
            proficiency_percentage=data.proficiency_percentage
        )
        return employee_skill
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/employees/{employee_id}/skills", response_model=List[EmployeeSkillResponse])
async def get_employee_skills(
    employee_id: str,
    service: TrainingService = Depends(get_training_service)
):
    """Get all skills for an employee"""
    skills = await service.get_employee_skills(employee_id)
    return skills


# ============================================================================
# DASHBOARD & STATISTICS
# ============================================================================

@router.get("/stats", response_model=TrainingDashboardStats)
async def get_training_stats(
    service: TrainingService = Depends(get_training_service)
):
    """
    Get training dashboard statistics
    
    Returns:
    - Course statistics
    - Session statistics
    - Participant counts
    - Certification counts
    - Compliance metrics
    """
    stats = await service.get_dashboard_stats()
    return stats
