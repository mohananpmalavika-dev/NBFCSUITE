"""
Building Management Service
Handles building, floor, and room management operations
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from datetime import datetime, date

from backend.shared.database.facility_models import (
    Building, Floor, Room,
    BuildingTypeEnum, BuildingStatusEnum, RoomTypeEnum, RoomStatusEnum
)
from backend.shared.exceptions import NotFoundError, ValidationError


class BuildingService:
    """Service for building management operations"""
    
    @staticmethod
    async def create_building(
        db: AsyncSession,
        tenant_id: str,
        building_data: Dict[str, Any],
        user_id: int
    ) -> Building:
        """Create a new building"""
        
        # Check if building code already exists
        stmt = select(Building).where(
            and_(
                Building.tenant_id == tenant_id,
                Building.building_code == building_data.get("building_code"),
                Building.is_deleted == False
            )
        )
        existing = await db.execute(stmt)
        if existing.scalar_one_or_none():
            raise ValidationError("Building code already exists")
        
        building = Building(
            tenant_id=tenant_id,
            created_by=user_id,
            **building_data
        )
        
        db.add(building)
        await db.commit()
        await db.refresh(building)
        
        return building
    
    @staticmethod
    async def get_building(
        db: AsyncSession,
        tenant_id: str,
        building_id: int
    ) -> Building:
        """Get building by ID"""
        stmt = select(Building).where(
            and_(
                Building.tenant_id == tenant_id,
                Building.id == building_id,
                Building.is_deleted == False
            )
        )
        result = await db.execute(stmt)
        building = result.scalar_one_or_none()
        
        if not building:
            raise NotFoundError(f"Building with ID {building_id} not found")
        
        return building
    
    @staticmethod
    async def list_buildings(
        db: AsyncSession,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        building_type: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[List[Building], int]:
        """List all buildings with filters"""
        
        query = select(Building).where(
            and_(
                Building.tenant_id == tenant_id,
                Building.is_deleted == False
            )
        )
        
        # Apply filters
        if building_type:
            query = query.where(Building.building_type == building_type)
        
        if status:
            query = query.where(Building.status == status)
        
        if search:
            query = query.where(
                or_(
                    Building.building_name.ilike(f"%{search}%"),
                    Building.building_code.ilike(f"%{search}%"),
                    Building.city.ilike(f"%{search}%")
                )
            )
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()
        
        # Apply pagination
        query = query.offset(skip).limit(limit).order_by(Building.building_name)
        
        result = await db.execute(query)
        buildings = result.scalars().all()
        
        return buildings, total_count
    
    @staticmethod
    async def update_building(
        db: AsyncSession,
        tenant_id: str,
        building_id: int,
        building_data: Dict[str, Any],
        user_id: int
    ) -> Building:
        """Update building information"""
        
        building = await BuildingService.get_building(db, tenant_id, building_id)
        
        # Update fields
        for key, value in building_data.items():
            if hasattr(building, key) and key not in ['id', 'tenant_id', 'created_by', 'created_at']:
                setattr(building, key, value)
        
        building.updated_by = user_id
        building.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(building)
        
        return building
    
    @staticmethod
    async def delete_building(
        db: AsyncSession,
        tenant_id: str,
        building_id: int,
        user_id: int
    ) -> bool:
        """Soft delete a building"""
        
        building = await BuildingService.get_building(db, tenant_id, building_id)
        
        building.is_deleted = True
        building.deleted_at = datetime.utcnow()
        building.deleted_by = user_id
        
        await db.commit()
        
        return True
    
    # ============================================================================
    # FLOOR MANAGEMENT
    # ============================================================================
    
    @staticmethod
    async def create_floor(
        db: AsyncSession,
        tenant_id: str,
        building_id: int,
        floor_data: Dict[str, Any],
        user_id: int
    ) -> Floor:
        """Create a new floor in a building"""
        
        # Verify building exists
        await BuildingService.get_building(db, tenant_id, building_id)
        
        floor = Floor(
            tenant_id=tenant_id,
            building_id=building_id,
            created_by=user_id,
            **floor_data
        )
        
        db.add(floor)
        await db.commit()
        await db.refresh(floor)
        
        # Update building total floors count
        stmt = select(func.count()).select_from(Floor).where(
            and_(
                Floor.building_id == building_id,
                Floor.is_deleted == False
            )
        )
        result = await db.execute(stmt)
        floor_count = result.scalar()
        
        building = await BuildingService.get_building(db, tenant_id, building_id)
        building.total_floors = floor_count
        await db.commit()
        
        return floor
    
    @staticmethod
    async def list_floors(
        db: AsyncSession,
        tenant_id: str,
        building_id: int
    ) -> List[Floor]:
        """List all floors in a building"""
        
        stmt = select(Floor).where(
            and_(
                Floor.tenant_id == tenant_id,
                Floor.building_id == building_id,
                Floor.is_deleted == False
            )
        ).order_by(Floor.floor_number)
        
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def get_floor(
        db: AsyncSession,
        tenant_id: str,
        floor_id: int
    ) -> Floor:
        """Get floor by ID"""
        stmt = select(Floor).where(
            and_(
                Floor.tenant_id == tenant_id,
                Floor.id == floor_id,
                Floor.is_deleted == False
            )
        )
        result = await db.execute(stmt)
        floor = result.scalar_one_or_none()
        
        if not floor:
            raise NotFoundError(f"Floor with ID {floor_id} not found")
        
        return floor
    
    # ============================================================================
    # ROOM MANAGEMENT
    # ============================================================================
    
    @staticmethod
    async def create_room(
        db: AsyncSession,
        tenant_id: str,
        building_id: int,
        floor_id: int,
        room_data: Dict[str, Any],
        user_id: int
    ) -> Room:
        """Create a new room"""
        
        # Verify building and floor exist
        await BuildingService.get_building(db, tenant_id, building_id)
        await BuildingService.get_floor(db, tenant_id, floor_id)
        
        room = Room(
            tenant_id=tenant_id,
            building_id=building_id,
            floor_id=floor_id,
            created_by=user_id,
            **room_data
        )
        
        db.add(room)
        await db.commit()
        await db.refresh(room)
        
        return room
    
    @staticmethod
    async def list_rooms(
        db: AsyncSession,
        tenant_id: str,
        building_id: Optional[int] = None,
        floor_id: Optional[int] = None,
        room_type: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Room], int]:
        """List rooms with filters"""
        
        query = select(Room).where(
            and_(
                Room.tenant_id == tenant_id,
                Room.is_deleted == False
            )
        )
        
        if building_id:
            query = query.where(Room.building_id == building_id)
        
        if floor_id:
            query = query.where(Room.floor_id == floor_id)
        
        if room_type:
            query = query.where(Room.room_type == room_type)
        
        if status:
            query = query.where(Room.status == status)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()
        
        # Apply pagination
        query = query.offset(skip).limit(limit).order_by(Room.room_number)
        
        result = await db.execute(query)
        rooms = result.scalars().all()
        
        return rooms, total_count
    
    @staticmethod
    async def update_room_status(
        db: AsyncSession,
        tenant_id: str,
        room_id: int,
        status: RoomStatusEnum,
        user_id: int
    ) -> Room:
        """Update room status"""
        
        stmt = select(Room).where(
            and_(
                Room.tenant_id == tenant_id,
                Room.id == room_id,
                Room.is_deleted == False
            )
        )
        result = await db.execute(stmt)
        room = result.scalar_one_or_none()
        
        if not room:
            raise NotFoundError(f"Room with ID {room_id} not found")
        
        room.status = status
        room.updated_by = user_id
        room.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(room)
        
        return room
