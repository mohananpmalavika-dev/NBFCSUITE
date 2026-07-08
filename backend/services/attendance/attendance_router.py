"""
Attendance Management Router
FastAPI endpoints for attendance and check-in/out operations
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user, get_tenant_id
from .attendance_service import AttendanceService, BiometricService
from .schemas import (
    CheckInRequest, CheckOutRequest, AttendanceCreate, AttendanceUpdate,
    AttendanceResponse, AttendanceListResponse, AttendanceDashboardStats,
    BiometricLogCreate, BiometricLogResponse, MobileCheckInRequest,
    MobileCheckOutRequest, MobileCheckInResponse
)


router = APIRouter()


def get_attendance_service(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_current_user)
):
    """Dependency to get attendance service instance"""
    return AttendanceService(db, tenant_id, user_id)


def get_biometric_service(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_current_user)
):
    """Dependency to get biometric service instance"""
    return BiometricService(db, tenant_id, user_id)


# ============================================================================
# ATTENDANCE ENDPOINTS
# ============================================================================

@router.post("/check-in", response_model=AttendanceResponse, status_code=201)
async def check_in(
    request: CheckInRequest,
    service: AttendanceService = Depends(get_attendance_service)
):
    """Employee check-in"""
    try:
        attendance = await service.check_in(request)
        return attendance
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check-out", response_model=AttendanceResponse)
async def check_out(
    request: CheckOutRequest,
    service: AttendanceService = Depends(get_attendance_service)
):
    """Employee check-out"""
    try:
        attendance = await service.check_out(request)
        return attendance
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mobile/check-in", response_model=MobileCheckInResponse, status_code=201)
async def mobile_check_in(
    request: MobileCheckInRequest,
    service: AttendanceService = Depends(get_attendance_service)
):
    """Mobile app check-in with GPS location"""
    try:
        result = await service.mobile_check_in(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mobile/check-out")
async def mobile_check_out(
    request: MobileCheckOutRequest,
    service: AttendanceService = Depends(get_attendance_service)
):
    """Mobile app check-out with GPS location"""
    try:
        result = await service.mobile_check_out(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/manual", response_model=AttendanceResponse, status_code=201)
async def create_manual_attendance(
    data: AttendanceCreate,
    service: AttendanceService = Depends(get_attendance_service)
):
    """Create manual attendance entry"""
    try:
        attendance = await service.create_manual_attendance(data)
        return attendance
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=AttendanceListResponse)
async def get_attendances(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    employee_id: Optional[str] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    status: Optional[str] = Query(None),
    service: AttendanceService = Depends(get_attendance_service)
):
    """Get paginated list of attendance records"""
    try:
        attendances, total = await service.get_attendances(
            page=page,
            page_size=page_size,
            employee_id=employee_id,
            from_date=from_date,
            to_date=to_date,
            status=status
        )
        
        return {
            "items": attendances,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/dashboard/stats", response_model=AttendanceDashboardStats)
async def get_dashboard_stats(
    service: AttendanceService = Depends(get_attendance_service)
):
    """Get attendance dashboard statistics"""
    try:
        stats = await service.get_dashboard_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{attendance_id}", response_model=AttendanceResponse)
async def get_attendance(
    attendance_id: str,
    service: AttendanceService = Depends(get_attendance_service)
):
    """Get attendance by ID"""
    attendance = await service.get_attendance(attendance_id)
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance not found")
    return attendance


@router.put("/{attendance_id}", response_model=AttendanceResponse)
async def update_attendance(
    attendance_id: str,
    data: AttendanceUpdate,
    service: AttendanceService = Depends(get_attendance_service)
):
    """Update attendance (for corrections)"""
    try:
        attendance = await service.get_attendance(attendance_id)
        if not attendance:
            raise ValueError("Attendance not found")
        
        # Update fields
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(attendance, field, value)
        
        await service.db.commit()
        await service.db.refresh(attendance)
        return attendance
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# BIOMETRIC LOG ENDPOINTS
# ============================================================================

@router.post("/biometric/log", response_model=BiometricLogResponse, status_code=201)
async def create_biometric_log(
    data: BiometricLogCreate,
    service: BiometricService = Depends(get_biometric_service)
):
    """Create biometric log from device"""
    try:
        log = await service.create_biometric_log(data)
        return log
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/biometric/sync")
async def sync_biometric_logs(
    logs: list[BiometricLogCreate],
    service: BiometricService = Depends(get_biometric_service)
):
    """Bulk sync biometric logs from device"""
    try:
        processed = []
        for log_data in logs:
            log = await service.create_biometric_log(log_data)
            processed.append(log.id)
        
        return {
            "message": f"Successfully synced {len(processed)} biometric logs",
            "processed_ids": processed
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
