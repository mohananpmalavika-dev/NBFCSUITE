"""
Transport Management Service
Handles vehicle, trip, and maintenance management
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from datetime import datetime, date, timedelta

from backend.shared.database.facility_models import (
    Vehicle, Trip, VehicleMaintenance,
    VehicleTypeEnum, VehicleStatusEnum, TripStatusEnum
)
from backend.shared.exceptions import NotFoundError, ValidationError


class TransportService:
    """Service for transport operations"""
    
    # ============================================================================
    # VEHICLE MANAGEMENT
    # ============================================================================
    
    @staticmethod
    async def create_vehicle(
        db: AsyncSession,
        tenant_id: str,
        vehicle_data: Dict[str, Any],
        user_id: int
    ) -> Vehicle:
        """Create a new vehicle"""
        
        # Check if vehicle number already exists
        stmt = select(Vehicle).where(
            and_(
                Vehicle.tenant_id == tenant_id,
                Vehicle.vehicle_number == vehicle_data.get("vehicle_number"),
                Vehicle.is_deleted == False
            )
        )
        existing = await db.execute(stmt)
        if existing.scalar_one_or_none():
            raise ValidationError("Vehicle number already exists")
        
        vehicle = Vehicle(
            tenant_id=tenant_id,
            created_by=user_id,
            **vehicle_data
        )
        
        db.add(vehicle)
        await db.commit()
        await db.refresh(vehicle)
        
        return vehicle
    
    @staticmethod
    async def list_vehicles(
        db: AsyncSession,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        vehicle_type: Optional[str] = None,
        status: Optional[str] = None,
        assigned_driver: Optional[int] = None
    ) -> tuple[List[Vehicle], int]:
        """List vehicles with filters"""
        
        query = select(Vehicle).where(
            and_(
                Vehicle.tenant_id == tenant_id,
                Vehicle.is_deleted == False
            )
        )
        
        if vehicle_type:
            query = query.where(Vehicle.vehicle_type == vehicle_type)
        
        if status:
            query = query.where(Vehicle.status == status)
        
        if assigned_driver:
            query = query.where(Vehicle.assigned_driver_id == assigned_driver)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()
        
        # Apply pagination
        query = query.offset(skip).limit(limit).order_by(Vehicle.vehicle_number)
        
        result = await db.execute(query)
        vehicles = result.scalars().all()
        
        return vehicles, total_count
    
    @staticmethod
    async def get_available_vehicles(
        db: AsyncSession,
        tenant_id: str,
        trip_date: date
    ) -> List[Vehicle]:
        """Get vehicles available for a specific date"""
        
        # Get vehicles not in use on the specified date
        stmt = select(Vehicle).where(
            and_(
                Vehicle.tenant_id == tenant_id,
                Vehicle.status == VehicleStatusEnum.AVAILABLE,
                Vehicle.is_active == True,
                Vehicle.is_deleted == False
            )
        )
        
        result = await db.execute(stmt)
        return result.scalars().all()
    
    # ============================================================================
    # TRIP MANAGEMENT
    # ============================================================================
    
    @staticmethod
    async def create_trip(
        db: AsyncSession,
        tenant_id: str,
        trip_data: Dict[str, Any],
        user_id: int
    ) -> Trip:
        """Create a new trip"""
        
        # Generate trip number
        date_str = datetime.now().strftime("%Y%m%d")
        stmt = select(func.count()).select_from(Trip).where(
            Trip.tenant_id == tenant_id
        )
        result = await db.execute(stmt)
        count = result.scalar() + 1
        trip_number = f"TRP{date_str}{count:04d}"
        
        trip = Trip(
            tenant_id=tenant_id,
            trip_number=trip_number,
            created_by=user_id,
            **trip_data
        )
        
        db.add(trip)
        await db.commit()
        await db.refresh(trip)
        
        return trip
    
    @staticmethod
    async def list_trips(
        db: AsyncSession,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        vehicle_id: Optional[int] = None,
        driver_id: Optional[int] = None,
        status: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> tuple[List[Trip], int]:
        """List trips with filters"""
        
        query = select(Trip).where(
            and_(
                Trip.tenant_id == tenant_id,
                Trip.is_deleted == False
            )
        )
        
        if vehicle_id:
            query = query.where(Trip.vehicle_id == vehicle_id)
        
        if driver_id:
            query = query.where(Trip.driver_id == driver_id)
        
        if status:
            query = query.where(Trip.status == status)
        
        if from_date:
            query = query.where(Trip.trip_date >= from_date)
        
        if to_date:
            query = query.where(Trip.trip_date <= to_date)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()
        
        # Apply pagination
        query = query.offset(skip).limit(limit).order_by(Trip.trip_date.desc())
        
        result = await db.execute(query)
        trips = result.scalars().all()
        
        return trips, total_count
    
    @staticmethod
    async def start_trip(
        db: AsyncSession,
        tenant_id: str,
        trip_id: int,
        start_mileage: float,
        user_id: int
    ) -> Trip:
        """Start a trip"""
        
        stmt = select(Trip).where(
            and_(
                Trip.tenant_id == tenant_id,
                Trip.id == trip_id,
                Trip.is_deleted == False
            )
        )
        result = await db.execute(stmt)
        trip = result.scalar_one_or_none()
        
        if not trip:
            raise NotFoundError(f"Trip with ID {trip_id} not found")
        
        trip.status = TripStatusEnum.IN_PROGRESS
        trip.actual_start_time = datetime.utcnow()
        trip.start_mileage_km = start_mileage
        trip.updated_by = user_id
        trip.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(trip)
        
        return trip
    
    @staticmethod
    async def complete_trip(
        db: AsyncSession,
        tenant_id: str,
        trip_id: int,
        end_mileage: float,
        fuel_consumed: Optional[float] = None,
        expenses: Optional[Dict[str, float]] = None,
        user_id: int = None
    ) -> Trip:
        """Complete a trip"""
        
        stmt = select(Trip).where(
            and_(
                Trip.tenant_id == tenant_id,
                Trip.id == trip_id,
                Trip.is_deleted == False
            )
        )
        result = await db.execute(stmt)
        trip = result.scalar_one_or_none()
        
        if not trip:
            raise NotFoundError(f"Trip with ID {trip_id} not found")
        
        trip.status = TripStatusEnum.COMPLETED
        trip.actual_end_time = datetime.utcnow()
        trip.end_mileage_km = end_mileage
        trip.distance_km = end_mileage - trip.start_mileage_km
        
        if fuel_consumed:
            trip.fuel_consumed_liters = fuel_consumed
        
        if expenses:
            trip.toll_charges = expenses.get("toll", 0)
            trip.parking_charges = expenses.get("parking", 0)
            trip.other_expenses = expenses.get("other", 0)
            trip.total_expense = (
                trip.toll_charges + 
                trip.parking_charges + 
                trip.other_expenses +
                (trip.fuel_cost or 0)
            )
        
        trip.updated_by = user_id
        trip.updated_at = datetime.utcnow()
        
        # Update vehicle mileage
        vehicle_stmt = select(Vehicle).where(Vehicle.id == trip.vehicle_id)
        vehicle_result = await db.execute(vehicle_stmt)
        vehicle = vehicle_result.scalar_one_or_none()
        
        if vehicle:
            vehicle.current_mileage_km = end_mileage
        
        await db.commit()
        await db.refresh(trip)
        
        return trip
    
    # ============================================================================
    # MAINTENANCE MANAGEMENT
    # ============================================================================
    
    @staticmethod
    async def create_maintenance_record(
        db: AsyncSession,
        tenant_id: str,
        maintenance_data: Dict[str, Any],
        user_id: int
    ) -> VehicleMaintenance:
        """Create a maintenance record"""
        
        # Generate maintenance code
        date_str = datetime.now().strftime("%Y%m%d")
        stmt = select(func.count()).select_from(VehicleMaintenance).where(
            VehicleMaintenance.tenant_id == tenant_id
        )
        result = await db.execute(stmt)
        count = result.scalar() + 1
        maintenance_code = f"MNT{date_str}{count:04d}"
        
        maintenance = VehicleMaintenance(
            tenant_id=tenant_id,
            maintenance_code=maintenance_code,
            created_by=user_id,
            **maintenance_data
        )
        
        db.add(maintenance)
        await db.commit()
        await db.refresh(maintenance)
        
        return maintenance
    
    @staticmethod
    async def get_upcoming_maintenance(
        db: AsyncSession,
        tenant_id: str,
        days_ahead: int = 30
    ) -> List[Vehicle]:
        """Get vehicles with upcoming maintenance"""
        
        target_date = date.today() + timedelta(days=days_ahead)
        
        stmt = select(Vehicle).where(
            and_(
                Vehicle.tenant_id == tenant_id,
                Vehicle.is_active == True,
                Vehicle.is_deleted == False,
                or_(
                    Vehicle.insurance_expiry <= target_date,
                    Vehicle.registration_expiry <= target_date
                )
            )
        )
        
        result = await db.execute(stmt)
        return result.scalars().all()
