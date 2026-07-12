"""
Facility Management Pydantic Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date, time
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class BuildingTypeEnum(str, Enum):
    OFFICE = "office"
    WAREHOUSE = "warehouse"
    FACTORY = "factory"
    RETAIL = "retail"
    RESIDENTIAL = "residential"
    MIXED_USE = "mixed_use"


class BuildingStatusEnum(str, Enum):
    ACTIVE = "active"
    UNDER_CONSTRUCTION = "under_construction"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"


class RoomTypeEnum(str, Enum):
    OFFICE = "office"
    CONFERENCE_ROOM = "conference_room"
    CABIN = "cabin"
    CUBICLE = "cubicle"
    MEETING_ROOM = "meeting_room"
    CAFETERIA = "cafeteria"
    RESTROOM = "restroom"
    STORAGE = "storage"
    SERVER_ROOM = "server_room"
    RECEPTION = "reception"
    LOBBY = "lobby"
    PANTRY = "pantry"
    OTHER = "other"


class RoomStatusEnum(str, Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    UNDER_MAINTENANCE = "under_maintenance"
    RESERVED = "reserved"
    OUT_OF_SERVICE = "out_of_service"


class TaskStatusEnum(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class TaskPriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class OrderStatusEnum(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    SERVED = "served"
    CANCELLED = "cancelled"


class VehicleStatusEnum(str, Enum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    OUT_OF_SERVICE = "out_of_service"


class TripStatusEnum(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class VisitStatusEnum(str, Enum):
    SCHEDULED = "scheduled"
    CHECKED_IN = "checked_in"
    IN_MEETING = "in_meeting"
    CHECKED_OUT = "checked_out"
    CANCELLED = "cancelled"


# ============================================================================
# BUILDING SCHEMAS
# ============================================================================

class BuildingBase(BaseModel):
    building_code: str
    building_name: str
    building_type: BuildingTypeEnum
    status: Optional[BuildingStatusEnum] = BuildingStatusEnum.ACTIVE
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    total_area_sqft: Optional[float] = None
    built_year: Optional[int] = None
    has_elevator: Optional[bool] = False
    has_parking: Optional[bool] = False
    parking_capacity: Optional[int] = 0
    contact_number: Optional[str] = None


class BuildingCreate(BuildingBase):
    pass


class BuildingUpdate(BaseModel):
    building_name: Optional[str] = None
    status: Optional[BuildingStatusEnum] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    contact_number: Optional[str] = None


class BuildingResponse(BuildingBase):
    id: int
    tenant_id: str
    total_floors: int = 0
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# FLOOR SCHEMAS
# ============================================================================

class FloorBase(BaseModel):
    floor_number: int
    floor_name: Optional[str] = None
    floor_area_sqft: Optional[float] = None
    has_restroom: Optional[bool] = True
    has_pantry: Optional[bool] = False


class FloorCreate(FloorBase):
    pass


class FloorResponse(FloorBase):
    id: int
    building_id: int
    total_rooms: int = 0
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# ROOM SCHEMAS
# ============================================================================

class RoomBase(BaseModel):
    room_number: str
    room_name: Optional[str] = None
    room_type: RoomTypeEnum
    status: Optional[RoomStatusEnum] = RoomStatusEnum.AVAILABLE
    area_sqft: Optional[float] = None
    seating_capacity: Optional[int] = None
    has_ac: Optional[bool] = False
    has_projector: Optional[bool] = False


class RoomCreate(RoomBase):
    pass


class RoomStatusUpdate(BaseModel):
    status: RoomStatusEnum


class RoomResponse(RoomBase):
    id: int
    building_id: int
    floor_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# HOUSEKEEPING SCHEMAS
# ============================================================================

class HousekeepingTaskBase(BaseModel):
    task_type: str
    task_name: str
    building_id: int
    floor_id: Optional[int] = None
    room_id: Optional[int] = None
    scheduled_date: date
    scheduled_time: Optional[time] = None
    priority: Optional[TaskPriorityEnum] = TaskPriorityEnum.MEDIUM
    description: Optional[str] = None


class HousekeepingTaskCreate(HousekeepingTaskBase):
    pass


class TaskAssignment(BaseModel):
    employee_id: int


class TaskStatusUpdate(BaseModel):
    status: TaskStatusEnum
    remarks: Optional[str] = None


class HousekeepingTaskResponse(HousekeepingTaskBase):
    id: int
    task_code: str
    status: TaskStatusEnum
    assigned_to_employee_id: Optional[int] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# CAFETERIA SCHEMAS
# ============================================================================

class MenuItemBase(BaseModel):
    item_code: str
    item_name: str
    meal_type: str
    category: Optional[str] = None
    price: float
    employee_price: Optional[float] = None
    is_vegetarian: Optional[bool] = True


class MenuItemCreate(MenuItemBase):
    pass


class MenuItemResponse(MenuItemBase):
    id: int
    is_available: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class OrderItemCreate(BaseModel):
    menu_item_id: int
    quantity: int = 1
    special_instructions: Optional[str] = None


class CafeteriaOrderCreate(BaseModel):
    employee_id: int
    meal_type: str
    delivery_location: Optional[str] = None
    items: List[OrderItemCreate]


class OrderStatusUpdate(BaseModel):
    status: OrderStatusEnum


class CafeteriaOrderResponse(BaseModel):
    id: int
    order_number: str
    order_date: date
    employee_id: int
    status: OrderStatusEnum
    total_amount: float
    net_amount: float
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# TRANSPORT SCHEMAS
# ============================================================================

class VehicleBase(BaseModel):
    vehicle_number: str
    vehicle_type: str
    make_model: Optional[str] = None
    seating_capacity: Optional[int] = None
    fuel_type: Optional[str] = None
    ownership: Optional[str] = "owned"


class VehicleCreate(VehicleBase):
    pass


class VehicleResponse(VehicleBase):
    id: int
    status: VehicleStatusEnum
    current_mileage_km: float = 0
    created_at: datetime
    
    class Config:
        from_attributes = True


class TripBase(BaseModel):
    vehicle_id: int
    driver_id: int
    trip_date: date
    start_location: str
    end_location: str
    purpose: Optional[str] = None
    passenger_count: Optional[int] = 0


class TripCreate(TripBase):
    pass


class TripStartUpdate(BaseModel):
    start_mileage: float


class TripCompleteUpdate(BaseModel):
    end_mileage: float
    fuel_consumed: Optional[float] = None
    toll_charges: Optional[float] = 0
    parking_charges: Optional[float] = 0
    other_expenses: Optional[float] = 0


class TripResponse(TripBase):
    id: int
    trip_number: str
    status: TripStatusEnum
    distance_km: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# VISITOR SCHEMAS
# ============================================================================

class VisitorBase(BaseModel):
    visitor_name: str
    visitor_type: str
    company_name: Optional[str] = None
    mobile_number: str
    purpose: str
    host_employee_id: int
    visit_date: date
    expected_in_time: Optional[time] = None
    id_proof_type: Optional[str] = None
    id_proof_number: Optional[str] = None


class VisitorCreate(VisitorBase):
    pass


class VisitorCheckIn(BaseModel):
    badge_number: Optional[str] = None


class VisitorResponse(VisitorBase):
    id: int
    visitor_pass_number: str
    status: VisitStatusEnum
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
