"""
Facility & Administration Management Models
Complete facility management including buildings, housekeeping, cafeteria, transport, and visitor management
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Date, Time, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, date, time
import enum

from backend.shared.database.connection import Base


# ============================================================================
# ENUMS
# ============================================================================

class BuildingTypeEnum(str, enum.Enum):
    """Building types"""
    OFFICE = "office"
    WAREHOUSE = "warehouse"
    FACTORY = "factory"
    RETAIL = "retail"
    RESIDENTIAL = "residential"
    MIXED_USE = "mixed_use"


class BuildingStatusEnum(str, enum.Enum):
    """Building status"""
    ACTIVE = "active"
    UNDER_CONSTRUCTION = "under_construction"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"


class RoomTypeEnum(str, enum.Enum):
    """Room types"""
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


class RoomStatusEnum(str, enum.Enum):
    """Room status"""
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    UNDER_MAINTENANCE = "under_maintenance"
    RESERVED = "reserved"
    OUT_OF_SERVICE = "out_of_service"


class HousekeepingTaskTypeEnum(str, enum.Enum):
    """Housekeeping task types"""
    CLEANING = "cleaning"
    DEEP_CLEANING = "deep_cleaning"
    SANITIZATION = "sanitization"
    WASTE_DISPOSAL = "waste_disposal"
    FLOOR_CLEANING = "floor_cleaning"
    WINDOW_CLEANING = "window_cleaning"
    RESTROOM_CLEANING = "restroom_cleaning"
    CARPET_CLEANING = "carpet_cleaning"
    PEST_CONTROL = "pest_control"
    OTHER = "other"


class TaskStatusEnum(str, enum.Enum):
    """Task status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class TaskPriorityEnum(str, enum.Enum):
    """Task priority"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class MealTypeEnum(str, enum.Enum):
    """Meal types"""
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACKS = "snacks"
    BEVERAGES = "beverages"


class OrderStatusEnum(str, enum.Enum):
    """Order status"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    SERVED = "served"
    CANCELLED = "cancelled"


class VehicleTypeEnum(str, enum.Enum):
    """Vehicle types"""
    CAR = "car"
    SUV = "suv"
    VAN = "van"
    BUS = "bus"
    TRUCK = "truck"
    TWO_WHEELER = "two_wheeler"


class VehicleStatusEnum(str, enum.Enum):
    """Vehicle status"""
    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    OUT_OF_SERVICE = "out_of_service"


class TripStatusEnum(str, enum.Enum):
    """Trip status"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class VisitorTypeEnum(str, enum.Enum):
    """Visitor types"""
    CUSTOMER = "customer"
    VENDOR = "vendor"
    CANDIDATE = "candidate"
    CONTRACTOR = "contractor"
    GUEST = "guest"
    OFFICIAL = "official"
    OTHER = "other"


class VisitPurposeEnum(str, enum.Enum):
    """Visit purposes"""
    MEETING = "meeting"
    INTERVIEW = "interview"
    DELIVERY = "delivery"
    MAINTENANCE = "maintenance"
    TRAINING = "training"
    AUDIT = "audit"
    INSPECTION = "inspection"
    OTHER = "other"


class VisitStatusEnum(str, enum.Enum):
    """Visit status"""
    SCHEDULED = "scheduled"
    CHECKED_IN = "checked_in"
    IN_MEETING = "in_meeting"
    CHECKED_OUT = "checked_out"
    CANCELLED = "cancelled"


# ============================================================================
# BUILDING MANAGEMENT MODELS
# ============================================================================

class Building(Base):
    """Building master data"""
    __tablename__ = "facility_buildings"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Basic Information
    building_code = Column(String(50), unique=True, nullable=False, index=True)
    building_name = Column(String(200), nullable=False)
    building_type = Column(SQLEnum(BuildingTypeEnum), nullable=False)
    status = Column(SQLEnum(BuildingStatusEnum), default=BuildingStatusEnum.ACTIVE)
    
    # Location
    address_line1 = Column(String(200))
    address_line2 = Column(String(200))
    city = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(10))
    country = Column(String(100), default="India")
    
    # Building Details
    total_floors = Column(Integer, default=0)
    total_area_sqft = Column(Float)
    built_year = Column(Integer)
    ownership_type = Column(String(50))  # owned, leased, rented
    
    # Facilities
    has_elevator = Column(Boolean, default=False)
    has_parking = Column(Boolean, default=False)
    parking_capacity = Column(Integer, default=0)
    has_generator = Column(Boolean, default=False)
    has_cafeteria = Column(Boolean, default=False)
    has_gym = Column(Boolean, default=False)
    
    # Contact
    facility_manager_id = Column(Integer, ForeignKey("hrms_employees.id"))
    contact_number = Column(String(15))
    emergency_contact = Column(String(15))
    
    # Additional Info
    description = Column(Text)
    remarks = Column(Text)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime)
    deleted_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    floors = relationship("Floor", back_populates="building", cascade="all, delete-orphan")
    rooms = relationship("Room", back_populates="building")


class Floor(Base):
    """Floor information within a building"""
    __tablename__ = "facility_floors"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    building_id = Column(Integer, ForeignKey("facility_buildings.id"), nullable=False)
    
    floor_number = Column(Integer, nullable=False)  # 0 = Ground, -1 = Basement 1
    floor_name = Column(String(100))  # e.g., "Ground Floor", "First Floor"
    floor_area_sqft = Column(Float)
    total_rooms = Column(Integer, default=0)
    
    # Facilities
    has_restroom = Column(Boolean, default=True)
    has_pantry = Column(Boolean, default=False)
    has_fire_exit = Column(Boolean, default=True)
    
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    building = relationship("Building", back_populates="floors")
    rooms = relationship("Room", back_populates="floor", cascade="all, delete-orphan")


class Room(Base):
    """Room/Space within a floor"""
    __tablename__ = "facility_rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    building_id = Column(Integer, ForeignKey("facility_buildings.id"), nullable=False)
    floor_id = Column(Integer, ForeignKey("facility_floors.id"), nullable=False)
    
    room_number = Column(String(50), nullable=False)
    room_name = Column(String(200))
    room_type = Column(SQLEnum(RoomTypeEnum), nullable=False)
    status = Column(SQLEnum(RoomStatusEnum), default=RoomStatusEnum.AVAILABLE)
    
    # Room Details
    area_sqft = Column(Float)
    seating_capacity = Column(Integer)
    
    # Assigned To
    department_id = Column(Integer, ForeignKey("hrms_departments.id"))
    assigned_to_employee_id = Column(Integer, ForeignKey("hrms_employees.id"))
    
    # Amenities
    has_ac = Column(Boolean, default=False)
    has_projector = Column(Boolean, default=False)
    has_whiteboard = Column(Boolean, default=False)
    has_wifi = Column(Boolean, default=True)
    
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    building = relationship("Building", back_populates="rooms")
    floor = relationship("Floor", back_populates="rooms")


# ============================================================================
# HOUSEKEEPING MODELS
# ============================================================================

class HousekeepingTask(Base):
    """Housekeeping tasks and cleaning schedules"""
    __tablename__ = "facility_housekeeping_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    task_code = Column(String(50), unique=True, nullable=False, index=True)
    task_type = Column(SQLEnum(HousekeepingTaskTypeEnum), nullable=False)
    task_name = Column(String(200), nullable=False)
    
    # Location
    building_id = Column(Integer, ForeignKey("facility_buildings.id"), nullable=False)
    floor_id = Column(Integer, ForeignKey("facility_floors.id"))
    room_id = Column(Integer, ForeignKey("facility_rooms.id"))
    specific_location = Column(String(200))
    
    # Schedule
    scheduled_date = Column(Date, nullable=False)
    scheduled_time = Column(Time)
    estimated_duration_minutes = Column(Integer)
    
    # Assignment
    assigned_to_employee_id = Column(Integer, ForeignKey("hrms_employees.id"))
    assigned_at = Column(DateTime)
    
    # Status & Priority
    status = Column(SQLEnum(TaskStatusEnum), default=TaskStatusEnum.PENDING)
    priority = Column(SQLEnum(TaskPriorityEnum), default=TaskPriorityEnum.MEDIUM)
    
    # Completion
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    actual_duration_minutes = Column(Integer)
    
    # Quality Check
    quality_rating = Column(Integer)  # 1-5
    quality_checked_by = Column(Integer, ForeignKey("hrms_employees.id"))
    quality_checked_at = Column(DateTime)
    quality_remarks = Column(Text)
    
    # Additional
    description = Column(Text)
    remarks = Column(Text)
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(String(50))  # daily, weekly, monthly
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False)


class HousekeepingSupply(Base):
    """Housekeeping supplies and inventory"""
    __tablename__ = "facility_housekeeping_supplies"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    item_code = Column(String(50), unique=True, nullable=False, index=True)
    item_name = Column(String(200), nullable=False)
    category = Column(String(100))  # cleaning_agents, tools, equipment
    unit_of_measure = Column(String(20))  # pieces, liters, kg
    
    # Inventory
    current_stock = Column(Float, default=0)
    minimum_stock = Column(Float, default=0)
    reorder_quantity = Column(Float, default=0)
    
    # Cost
    unit_price = Column(Float)
    supplier_name = Column(String(200))
    
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False)


# ============================================================================
# CAFETERIA MANAGEMENT MODELS
# ============================================================================

class CafeteriaMenu(Base):
    """Cafeteria menu items"""
    __tablename__ = "facility_cafeteria_menu"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    item_code = Column(String(50), unique=True, nullable=False, index=True)
    item_name = Column(String(200), nullable=False)
    meal_type = Column(SQLEnum(MealTypeEnum), nullable=False)
    category = Column(String(100))  # veg, non-veg, beverages
    
    # Pricing
    price = Column(Float, nullable=False)
    employee_price = Column(Float)  # subsidized price for employees
    
    # Availability
    is_available = Column(Boolean, default=True)
    available_days = Column(String(100))  # comma-separated: mon,tue,wed
    available_from_time = Column(Time)
    available_to_time = Column(Time)
    
    # Nutrition (optional)
    calories = Column(Integer)
    is_vegetarian = Column(Boolean, default=True)
    contains_allergens = Column(String(200))
    
    description = Column(Text)
    image_url = Column(String(500))
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    order_items = relationship("CafeteriaOrderItem", back_populates="menu_item")


class CafeteriaOrder(Base):
    """Cafeteria orders"""
    __tablename__ = "facility_cafeteria_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    order_date = Column(Date, nullable=False, default=date.today)
    order_time = Column(Time, nullable=False)
    
    # Customer
    employee_id = Column(Integer, ForeignKey("hrms_employees.id"), nullable=False)
    employee_name = Column(String(200))
    department = Column(String(100))
    
    # Order Details
    meal_type = Column(SQLEnum(MealTypeEnum))
    delivery_location = Column(String(200))  # room number, floor
    
    # Status
    status = Column(SQLEnum(OrderStatusEnum), default=OrderStatusEnum.PENDING)
    
    # Timing
    requested_time = Column(Time)  # when customer wants the order
    preparation_started_at = Column(DateTime)
    ready_at = Column(DateTime)
    served_at = Column(DateTime)
    
    # Payment
    total_amount = Column(Float, nullable=False, default=0)
    discount_amount = Column(Float, default=0)
    net_amount = Column(Float, nullable=False, default=0)
    payment_method = Column(String(50))  # cash, card, wallet, account_deduction
    payment_status = Column(String(50), default="pending")
    payment_reference = Column(String(100))
    
    # Feedback
    rating = Column(Integer)  # 1-5
    feedback = Column(Text)
    
    remarks = Column(Text)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    items = relationship("CafeteriaOrderItem", back_populates="order", cascade="all, delete-orphan")



class CafeteriaOrderItem(Base):
    """Individual items in cafeteria order"""
    __tablename__ = "facility_cafeteria_order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("facility_cafeteria_orders.id"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("facility_cafeteria_menu.id"), nullable=False)
    
    item_name = Column(String(200), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    
    special_instructions = Column(Text)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    order = relationship("CafeteriaOrder", back_populates="items")
    menu_item = relationship("CafeteriaMenu", back_populates="order_items")


class CafeteriaInventory(Base):
    """Cafeteria inventory management"""
    __tablename__ = "facility_cafeteria_inventory"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    item_code = Column(String(50), unique=True, nullable=False, index=True)
    item_name = Column(String(200), nullable=False)
    category = Column(String(100))  # groceries, vegetables, dairy, beverages
    unit_of_measure = Column(String(20))  # kg, liters, pieces
    
    # Stock
    current_stock = Column(Float, default=0)
    minimum_stock = Column(Float, default=0)
    maximum_stock = Column(Float, default=0)
    reorder_level = Column(Float, default=0)
    
    # Cost
    unit_cost = Column(Float)
    last_purchase_price = Column(Float)
    
    # Supplier
    preferred_supplier = Column(String(200))
    supplier_contact = Column(String(15))
    
    # Expiry
    has_expiry = Column(Boolean, default=False)
    expiry_alert_days = Column(Integer, default=7)
    
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False)


# ============================================================================
# TRANSPORT MANAGEMENT MODELS
# ============================================================================

class Vehicle(Base):
    """Vehicle master data"""
    __tablename__ = "facility_vehicles"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    vehicle_number = Column(String(50), unique=True, nullable=False, index=True)
    vehicle_type = Column(SQLEnum(VehicleTypeEnum), nullable=False)
    make_model = Column(String(200))
    year_of_manufacture = Column(Integer)
    color = Column(String(50))
    
    # Capacity
    seating_capacity = Column(Integer)
    cargo_capacity_kg = Column(Float)
    
    # Registration
    registration_date = Column(Date)
    registration_expiry = Column(Date)
    registration_state = Column(String(100))
    
    # Insurance
    insurance_company = Column(String(200))
    insurance_policy_number = Column(String(100))
    insurance_expiry = Column(Date)
    insurance_amount = Column(Float)
    
    # Status
    status = Column(SQLEnum(VehicleStatusEnum), default=VehicleStatusEnum.AVAILABLE)
    ownership = Column(String(50))  # owned, leased
    
    # Mileage
    current_mileage_km = Column(Float, default=0)
    last_service_mileage = Column(Float)
    next_service_due_km = Column(Float)
    
    # Fuel
    fuel_type = Column(String(50))  # petrol, diesel, cng, electric
    average_fuel_efficiency = Column(Float)  # km per liter
    
    # Assignment
    assigned_driver_id = Column(Integer, ForeignKey("hrms_employees.id"))
    home_location = Column(String(200))
    
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    trips = relationship("Trip", back_populates="vehicle")
    maintenance_records = relationship("VehicleMaintenance", back_populates="vehicle")


class Trip(Base):
    """Vehicle trip/journey records"""
    __tablename__ = "facility_trips"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    trip_number = Column(String(50), unique=True, nullable=False, index=True)
    vehicle_id = Column(Integer, ForeignKey("facility_vehicles.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("hrms_employees.id"), nullable=False)
    
    # Schedule
    trip_date = Column(Date, nullable=False)
    scheduled_start_time = Column(Time)
    scheduled_end_time = Column(Time)
    
    # Locations
    start_location = Column(String(200), nullable=False)
    end_location = Column(String(200), nullable=False)
    route_details = Column(Text)
    
    # Actual Timings
    actual_start_time = Column(DateTime)
    actual_end_time = Column(DateTime)
    
    # Trip Details
    purpose = Column(String(200))
    requested_by_employee_id = Column(Integer, ForeignKey("hrms_employees.id"))
    passenger_count = Column(Integer, default=0)
    passenger_names = Column(Text)  # comma-separated or JSON
    
    # Mileage & Fuel
    start_mileage_km = Column(Float)
    end_mileage_km = Column(Float)
    distance_km = Column(Float)
    fuel_consumed_liters = Column(Float)
    fuel_cost = Column(Float)
    
    # Status
    status = Column(SQLEnum(TripStatusEnum), default=TripStatusEnum.SCHEDULED)
    
    # Toll & Expenses
    toll_charges = Column(Float, default=0)
    parking_charges = Column(Float, default=0)
    other_expenses = Column(Float, default=0)
    total_expense = Column(Float, default=0)
    
    remarks = Column(Text)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="trips")


class VehicleMaintenance(Base):
    """Vehicle maintenance records"""
    __tablename__ = "facility_vehicle_maintenance"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    vehicle_id = Column(Integer, ForeignKey("facility_vehicles.id"), nullable=False)
    
    maintenance_code = Column(String(50), unique=True, nullable=False, index=True)
    maintenance_type = Column(String(100))  # routine, repair, inspection
    
    # Schedule
    scheduled_date = Column(Date)
    actual_date = Column(Date)
    
    # Service Details
    service_provider = Column(String(200))
    service_location = Column(String(200))
    mileage_at_service = Column(Float)
    
    # Work Done
    work_description = Column(Text)
    parts_replaced = Column(Text)
    
    # Cost
    labor_cost = Column(Float, default=0)
    parts_cost = Column(Float, default=0)
    other_charges = Column(Float, default=0)
    total_cost = Column(Float, default=0)
    
    # Next Service
    next_service_due_date = Column(Date)
    next_service_due_km = Column(Float)
    
    # Documents
    invoice_number = Column(String(100))
    invoice_url = Column(String(500))
    
    remarks = Column(Text)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="maintenance_records")


# ============================================================================
# VISITOR MANAGEMENT MODELS
# ============================================================================

class Visitor(Base):
    """Visitor records and passes"""
    __tablename__ = "facility_visitors"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    visitor_pass_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Visitor Details
    visitor_name = Column(String(200), nullable=False)
    visitor_type = Column(SQLEnum(VisitorTypeEnum), nullable=False)
    company_name = Column(String(200))
    designation = Column(String(100))
    
    # Contact
    mobile_number = Column(String(15), nullable=False)
    email = Column(String(200))
    
    # Identity
    id_proof_type = Column(String(50))  # aadhaar, pan, driving_license, passport
    id_proof_number = Column(String(100))
    
    # Visit Details
    purpose = Column(SQLEnum(VisitPurposeEnum), nullable=False)
    purpose_details = Column(Text)
    
    # Host Employee
    host_employee_id = Column(Integer, ForeignKey("hrms_employees.id"), nullable=False)
    host_employee_name = Column(String(200))
    host_department = Column(String(100))
    
    # Visit Schedule
    visit_date = Column(Date, nullable=False)
    expected_in_time = Column(Time)
    expected_out_time = Column(Time)
    
    # Actual Check-in/out
    check_in_time = Column(DateTime)
    check_out_time = Column(DateTime)
    duration_minutes = Column(Integer)
    
    # Status
    status = Column(SQLEnum(VisitStatusEnum), default=VisitStatusEnum.SCHEDULED)
    
    # Security & Access
    building_id = Column(Integer, ForeignKey("facility_buildings.id"))
    floor_access = Column(String(200))  # comma-separated floor numbers
    meeting_room_id = Column(Integer, ForeignKey("facility_rooms.id"))
    
    # Belongings
    has_laptop = Column(Boolean, default=False)
    laptop_serial = Column(String(100))
    has_mobile = Column(Boolean, default=False)
    has_other_items = Column(Boolean, default=False)
    other_items_description = Column(Text)
    
    # Vehicle
    has_vehicle = Column(Boolean, default=False)
    vehicle_number = Column(String(50))
    parking_slot = Column(String(50))
    
    # Badge/Pass
    badge_number = Column(String(50))
    badge_issued_by = Column(Integer, ForeignKey("hrms_employees.id"))
    badge_returned = Column(Boolean, default=False)
    
    # Photo & Signature
    photo_url = Column(String(500))
    signature_url = Column(String(500))
    
    # Approval
    is_pre_approved = Column(Boolean, default=False)
    approved_by = Column(Integer, ForeignKey("hrms_employees.id"))
    approved_at = Column(DateTime)
    
    # Security Clearance
    security_checked = Column(Boolean, default=False)
    security_checked_by = Column(Integer, ForeignKey("hrms_employees.id"))
    security_remarks = Column(Text)
    
    remarks = Column(Text)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False)


class VisitorGroup(Base):
    """Visitor groups for bulk entries"""
    __tablename__ = "facility_visitor_groups"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    group_code = Column(String(50), unique=True, nullable=False, index=True)
    group_name = Column(String(200), nullable=False)
    
    # Visit Details
    visit_date = Column(Date, nullable=False)
    purpose = Column(String(200))
    company_name = Column(String(200))
    
    # Host
    host_employee_id = Column(Integer, ForeignKey("hrms_employees.id"))
    
    # Group Details
    total_visitors = Column(Integer, default=0)
    
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False)
