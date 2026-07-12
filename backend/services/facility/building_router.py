"""
Building Management API Router
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user, get_tenant_id
from backend.shared.schemas import SuccessResponse, PaginatedResponse
from .building_service import BuildingService
from .schemas import (
    BuildingCreate, BuildingUpdate, BuildingResponse,
    FloorCreate, FloorResponse,
    RoomCreate, RoomResponse, RoomStatusUpdate
)

router = APIRouter(prefix="/facility/buildings", tags=["Facility - Building Management"])


# ============================================================================
# BUILDING ENDPOINTS
# ============================================================================

@router.post("", response_model=SuccessResponse[BuildingResponse])
async def create_building(
    building: BuildingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Create a new building"""
    result = await BuildingService.create_building(
        db, tenant_id, building.dict(), current_user["id"]
    )
    return SuccessResponse(data=result)


@router.get("", response_model=SuccessResponse[PaginatedResponse[BuildingResponse]])
async def list_buildings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    building_type: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """List all buildings with filters"""
    buildings, total = await BuildingService.list_buildings(
        db, tenant_id, skip, limit, building_type, status, search
    )
    return SuccessResponse(
        data=PaginatedResponse(
            items=buildings,
            total=total,
            skip=skip,
            limit=limit
        )
    )


@router.get("/{building_id}", response_model=SuccessResponse[BuildingResponse])
async def get_building(
    building_id: int,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get building by ID"""
    building = await BuildingService.get_building(db, tenant_id, building_id)
    return SuccessResponse(data=building)


@router.put("/{building_id}", response_model=SuccessResponse[BuildingResponse])
async def update_building(
    building_id: int,
    building: BuildingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Update building information"""
    result = await BuildingService.update_building(
        db, tenant_id, building_id, building.dict(exclude_unset=True), current_user["id"]
    )
    return SuccessResponse(data=result)


@router.delete("/{building_id}", response_model=SuccessResponse[dict])
async def delete_building(
    building_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Delete a building"""
    await BuildingService.delete_building(db, tenant_id, building_id, current_user["id"])
    return SuccessResponse(data={"message": "Building deleted successfully"})


# ============================================================================
# FLOOR ENDPOINTS
# ============================================================================

@router.post("/{building_id}/floors", response_model=SuccessResponse[FloorResponse])
async def create_floor(
    building_id: int,
    floor: FloorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Create a new floor in a building"""
    result = await BuildingService.create_floor(
        db, tenant_id, building_id, floor.dict(), current_user["id"]
    )
    return SuccessResponse(data=result)


@router.get("/{building_id}/floors", response_model=SuccessResponse[List[FloorResponse]])
async def list_floors(
    building_id: int,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """List all floors in a building"""
    floors = await BuildingService.list_floors(db, tenant_id, building_id)
    return SuccessResponse(data=floors)


# ============================================================================
# ROOM ENDPOINTS
# ============================================================================

@router.post("/{building_id}/floors/{floor_id}/rooms", response_model=SuccessResponse[RoomResponse])
async def create_room(
    building_id: int,
    floor_id: int,
    room: RoomCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Create a new room"""
    result = await BuildingService.create_room(
        db, tenant_id, building_id, floor_id, room.dict(), current_user["id"]
    )
    return SuccessResponse(data=result)


@router.get("/rooms", response_model=SuccessResponse[PaginatedResponse[RoomResponse]])
async def list_rooms(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    building_id: Optional[int] = None,
    floor_id: Optional[int] = None,
    room_type: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """List rooms with filters"""
    rooms, total = await BuildingService.list_rooms(
        db, tenant_id, building_id, floor_id, room_type, status, skip, limit
    )
    return SuccessResponse(
        data=PaginatedResponse(
            items=rooms,
            total=total,
            skip=skip,
            limit=limit
        )
    )


@router.patch("/rooms/{room_id}/status", response_model=SuccessResponse[RoomResponse])
async def update_room_status(
    room_id: int,
    status_update: RoomStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Update room status"""
    result = await BuildingService.update_room_status(
        db, tenant_id, room_id, status_update.status, current_user["id"]
    )
    return SuccessResponse(data=result)
