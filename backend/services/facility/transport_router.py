"""
Transport Management API Router
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import date

from backend.shared.database.connection import get_db
from backend.shared.auth.dependencies import get_current_user, get_tenant_id
from backend.shared.schemas import SuccessResponse, PaginatedResponse
from .transport_service import TransportService
from .schemas import (
    VehicleCreate, VehicleResponse,
    TripCreate, TripResponse, TripStartUpdate, TripCompleteUpdate
)

router = APIRouter(prefix="/facility/transport", tags=["Facility - Transport"])


# ============================================================================
# VEHICLE ENDPOINTS
# ============================================================================

@router.post("/vehicles", response_model=SuccessResponse[VehicleResponse])
async def create_vehicle(
    vehicle: VehicleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Create a new vehicle"""
    result = await TransportService.create_vehicle(
        db, tenant_id, vehicle.dict(), current_user["id"]
    )
    return SuccessResponse(data=result)


@router.get("/vehicles", response_model=SuccessResponse[PaginatedResponse[VehicleResponse]])
async def list_vehicles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    vehicle_type: Optional[str] = None,
    status: Optional[str] = None,
    assigned_driver: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """List vehicles with filters"""
    vehicles, total = await TransportService.list_vehicles(
        db, tenant_id, skip, limit, vehicle_type, status, assigned_driver
    )
    return SuccessResponse(
        data=PaginatedResponse(
            items=vehicles,
            total=total,
            skip=skip,
            limit=limit
        )
    )


@router.get("/vehicles/available", response_model=SuccessResponse[List[VehicleResponse]])
async def get_available_vehicles(
    trip_date: date,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get vehicles available for a specific date"""
    vehicles = await TransportService.get_available_vehicles(db, tenant_id, trip_date)
    return SuccessResponse(data=vehicles)


# ============================================================================
# TRIP ENDPOINTS
# ============================================================================

@router.post("/trips", response_model=SuccessResponse[TripResponse])
async def create_trip(
    trip: TripCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Create a new trip"""
    result = await TransportService.create_trip(
        db, tenant_id, trip.dict(), current_user["id"]
    )
    return SuccessResponse(data=result)


@router.get("/trips", response_model=SuccessResponse[PaginatedResponse[TripResponse]])
async def list_trips(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    vehicle_id: Optional[int] = None,
    driver_id: Optional[int] = None,
    status: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """List trips with filters"""
    trips, total = await TransportService.list_trips(
        db, tenant_id, skip, limit, vehicle_id, driver_id,
        status, from_date, to_date
    )
    return SuccessResponse(
        data=PaginatedResponse(
            items=trips,
            total=total,
            skip=skip,
            limit=limit
        )
    )


@router.post("/trips/{trip_id}/start", response_model=SuccessResponse[TripResponse])
async def start_trip(
    trip_id: int,
    trip_start: TripStartUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Start a trip"""
    result = await TransportService.start_trip(
        db, tenant_id, trip_id, trip_start.start_mileage, current_user["id"]
    )
    return SuccessResponse(data=result)


@router.post("/trips/{trip_id}/complete", response_model=SuccessResponse[TripResponse])
async def complete_trip(
    trip_id: int,
    trip_complete: TripCompleteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Complete a trip"""
    expenses = {
        "toll": trip_complete.toll_charges,
        "parking": trip_complete.parking_charges,
        "other": trip_complete.other_expenses
    }
    
    result = await TransportService.complete_trip(
        db, tenant_id, trip_id, trip_complete.end_mileage,
        trip_complete.fuel_consumed, expenses, current_user["id"]
    )
    return SuccessResponse(data=result)


@router.get("/maintenance/upcoming", response_model=SuccessResponse[List[VehicleResponse]])
async def get_upcoming_maintenance(
    days_ahead: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get vehicles with upcoming maintenance"""
    vehicles = await TransportService.get_upcoming_maintenance(
        db, tenant_id, days_ahead
    )
    return SuccessResponse(data=vehicles)
