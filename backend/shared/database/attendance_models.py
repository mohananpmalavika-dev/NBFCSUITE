"""
HRMS Attendance & Leave Management Models
Database models for attendance tracking, shift management, and leave management
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Date, Time, Text, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, date, time
import enum
import uuid

from .database import Base


# ============================================================================
# ENUMS
# ============================================================================

class ShiftType(str, enum.Enum):
    """Shift type enum"""
    REGULAR = "REGULAR"
    ROTATING = "ROTATING"
    FLEXIBLE = "FLEXIBLE"
    NIGHT = "NIGHT"
    SPLIT = "SPLIT"


class AttendanceStatus(str, enum.Enum):
    """Attendance status enum"""
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    HALF_DAY = "HALF_DAY"
    LEAVE = "LEAVE"
    HOLIDAY = "HOLIDAY"
    WEEK_OFF = "WEEK_OFF"
    ON_DUTY = "ON_DUTY"


class CheckType(str, enum.Enum):
    """Check-in/out type"""
    CHECK_IN = "CHECK_IN"
    CHECK_OUT = "CHECK_OUT"
    BREAK_START = "BREAK_START"
    BREAK_END = "BREAK_END"


class CheckMethod(str, enum.Enum):
    """Check-in/out method"""
    BIOMETRIC = "BIOMETRIC"
    MOBILE = "MOBILE"
    WEB = "WEB"
    RFID = "RFID"
    MANUAL = "MANUAL"


class LeaveType(str, enum.Enum):
    """Leave type enum"""
    CASUAL_LEAVE = "CASUAL_LEAVE"
    SICK_LEAVE = "SICK_LEAVE"
    EARNED_LEAVE = "EARNED_LEAVE"
    PRIVILEGE_LEAVE = "PRIVILEGE_LEAVE"
    MATERNITY_LEAVE = "MATERNITY_LEAVE"
    PATERNITY_LEAVE = "PATERNITY_LEAVE"
    COMPENSATORY_OFF = "COMPENSATORY_OFF"
    LOSS_OF_PAY = "LOSS_OF_PAY"
    SABBATICAL = "SABBATICAL"
    STUDY_LEAVE = "STUDY_LEAVE"


class LeaveStatus(str, enum.Enum):
    """Leave application status"""
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    WITHDRAWN = "WITHDRAWN"


class LeavePeriod(str, enum.Enum):
    """Leave period - full day or half day"""
    FULL_DAY = "FULL_DAY"
    FIRST_HALF = "FIRST_HALF"
    SECOND_HALF = "SECOND_HALF"


# ============================================================================
# SHIFT MANAGEMENT MODELS
# ============================================================================

class Shift(Base):
    """
    Shift master table
    Defines work shifts for employees
    """
    __tablename__ = "shifts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(50), nullable=False, index=True)
    
    # Shift Details
    shift_code = Column(String(50), nullable=False, unique=True)
    shift_name = Column(String(200), nullable=False)
    shift_type = Column(SQLEnum(ShiftType), nullable=False, default=ShiftType.REGULAR)
    
    # Timing
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    grace_period_minutes = Column(Integer, default=15)  # Grace period for late arrival
    half_day_hours = Column(Float, default=4.0)
    full_day_hours = Column(Float, default=8.0)
    
    # Break Configuration
    break_duration_minutes = Column(Integer, default=60)
    break_start_time = Column(Time)
    break_end_time = Column(Time)
    
    # Week Off Configuration
    week_off_1 = Column(String(20))  # e.g., "SUNDAY"
    week_off_2 = Column(String(20))  # Optional second week off
    
    # Overtime
    allow_overtime = Column(Boolean, default=False)
    overtime_start_after_minutes = Column(Integer, default=30)
    
    # Active Status
    is_active = Column(Boolean, default=True)
    effective_from = Column(Date)
    effective_to = Column(Date)
    
    # Description
    description = Column(Text)
    
    # Audit Fields
    is_deleted = Column(Boolean, default=False)
    created_by = Column(String(255))
    updated_by = Column(String(255))
    deleted_by = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime)
    
    # Relationships
    attendances = relationship("Attendance", back_populates="shift")


class EmployeeShift(Base):
    """
    Employee shift assignment
    Links employees to shifts
    """
    __tablename__ = "employee_shifts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(50), nullable=False, index=True)
    
    # Employee and Shift
    employee_id = Column(String(36), ForeignKey("employees.id"), nullable=False, index=True)
    shift_id = Column(String(36), ForeignKey("shifts.id"), nullable=False, index=True)
    
    # Effective Period
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Audit Fields
    is_deleted = Column(Boolean, default=False)
    created_by = Column(String(255))
    updated_by = Column(String(255))
    deleted_by = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id])
    shift = relationship("Shift")


# ============================================================================
# ATTENDANCE MODELS
# ============================================================================

class Attendance(Base):
    """
    Daily attendance record
    Main attendance tracking table
    """
    __tablename__ = "attendance"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(50), nullable=False, index=True)
    
    # Employee and Date
    employee_id = Column(String(36), ForeignKey("employees.id"), nullable=False, index=True)
    attendance_date = Column(Date, nullable=False, index=True)
    
    # Shift Information
    shift_id = Column(String(36), ForeignKey("shifts.id"), index=True)
    scheduled_start_time = Column(Time)
    scheduled_end_time = Column(Time)
    
    # Check-in/out Times
    actual_check_in = Column(DateTime)
    actual_check_out = Column(DateTime)
    
    # Time Calculations
    late_by_minutes = Column(Integer, default=0)
    early_out_minutes = Column(Integer, default=0)
    total_work_hours = Column(Float, default=0.0)
    overtime_hours = Column(Float, default=0.0)
    break_hours = Column(Float, default=0.0)
    
    # Status
    status = Column(SQLEnum(AttendanceStatus), nullable=False, default=AttendanceStatus.ABSENT)
    
    # Location (for mobile check-in)
    check_in_location = Column(Text)  # JSON: {lat, lng, address}
    check_out_location = Column(Text)  # JSON: {lat, lng, address}
    
    # Device Information
    check_in_device = Column(String(200))
    check_out_device = Column(String(200))
    check_in_method = Column(SQLEnum(CheckMethod))
    check_out_method = Column(SQLEnum(CheckMethod))
    
    # Remarks
    remarks = Column(Text)
    is_manual_entry = Column(Boolean, default=False)
    manual_entry_reason = Column(Text)
    
    # Approval
    is_approved = Column(Boolean, default=False)
    approved_by = Column(String(36))
    approved_at = Column(DateTime)
    
    # Audit Fields
    is_deleted = Column(Boolean, default=False)
    created_by = Column(String(255))
    updated_by = Column(String(255))
    deleted_by = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id])
    shift = relationship("Shift", back_populates="attendances")
    biometric_logs = relationship("BiometricLog", back_populates="attendance")


class BiometricLog(Base):
    """
    Biometric device logs
    Raw data from biometric devices
    """
    __tablename__ = "biometric_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(50), nullable=False, index=True)
    
    # Employee
    employee_id = Column(String(36), ForeignKey("employees.id"), nullable=False, index=True)
    biometric_id = Column(String(50))  # Employee's biometric ID/enrollment number
    
    # Log Details
    log_datetime = Column(DateTime, nullable=False, index=True)
    check_type = Column(SQLEnum(CheckType), nullable=False)
    
    # Device Information
    device_id = Column(String(100))
    device_name = Column(String(200))
    device_location = Column(String(200))
    
    # Biometric Data (optional - for advanced integrations)
    biometric_data = Column(Text)  # JSON: fingerprint template, face data, etc.
    verification_method = Column(String(50))  # FINGERPRINT, FACE, IRIS, CARD
    verification_score = Column(Float)  # Match confidence score
    
    # Linked Attendance
    attendance_id = Column(String(36), ForeignKey("attendance.id"), index=True)
    
    # Processing Status
    is_processed = Column(Boolean, default=False)
    processed_at = Column(DateTime)
    
    # Audit Fields
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id])
    attendance = relationship("Attendance", back_populates="biometric_logs")


class AttendanceRegularization(Base):
    """
    Attendance correction/regularization requests
    For manual attendance corrections
    """
    __tablename__ = "attendance_regularization"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(50), nullable=False, index=True)
    
    # Reference
    attendance_id = Column(String(36), ForeignKey("attendance.id"), nullable=False, index=True)
    employee_id = Column(String(36), ForeignKey("employees.id"), nullable=False, index=True)
    
    # Requested Changes
    requested_check_in = Column(DateTime)
    requested_check_out = Column(DateTime)
    reason = Column(Text, nullable=False)
    supporting_documents = Column(Text)  # JSON array of URLs
    
    # Status
    status = Column(SQLEnum(LeaveStatus), nullable=False, default=LeaveStatus.PENDING)
    
    # Approval
    approved_by = Column(String(36))
    approved_at = Column(DateTime)
    rejection_reason = Column(Text)
    
    # Audit Fields
    is_deleted = Column(Boolean, default=False)
    created_by = Column(String(255))
    updated_by = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    attendance = relationship("Attendance")
    employee = relationship("Employee", foreign_keys=[employee_id])


# ============================================================================
# LEAVE MANAGEMENT MODELS
# ============================================================================

class LeavePolicyMaster(Base):
    """
    Leave policy master
    Defines leave types and entitlements
    """
    __tablename__ = "leave_policies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(50), nullable=False, index=True)
    
    # Policy Details
    policy_code = Column(String(50), nullable=False, unique=True)
    policy_name = Column(String(200), nullable=False)
    leave_type = Column(SQLEnum(LeaveType), nullable=False, index=True)
    
    # Entitlement
    annual_quota = Column(Float, nullable=False)  # Total leaves per year
    max_consecutive_days = Column(Integer)  # Max continuous leave allowed
    min_notice_days = Column(Integer, default=0)  # Minimum notice required
    max_carry_forward = Column(Float, default=0.0)  # Max leaves to carry forward
    
    # Accrual Settings
    is_accrual_based = Column(Boolean, default=False)
    accrual_frequency = Column(String(20))  # MONTHLY, QUARTERLY, YEARLY
    accrual_rate = Column(Float)  # Leaves accrued per period
    
    # Applicability
    applicable_after_days = Column(Integer, default=0)  # Probation period
    applicable_gender = Column(String(20))  # MALE, FEMALE, ALL
    
    # Restrictions
    allow_half_day = Column(Boolean, default=True)
    allow_negative_balance = Column(Boolean, default=False)
    require_document = Column(Boolean, default=False)
    require_document_after_days = Column(Integer)  # Medical certificate after X days
    
    # Weekend/Holiday Treatment
    include_weekends = Column(Boolean, default=False)
    include_holidays = Column(Boolean, default=False)
    
    # Encashment
    is_encashable = Column(Boolean, default=False)
    encashment_min_balance = Column(Float)
    encashment_percentage = Column(Float)  # % of salary per day
    
    # Status
    is_active = Column(Boolean, default=True)
    effective_from = Column(Date)
    effective_to = Column(Date)
    
    # Description
    description = Column(Text)
    rules = Column(Text)  # JSON: Additional rules and conditions
    
    # Audit Fields
    is_deleted = Column(Boolean, default=False)
    created_by = Column(String(255))
    updated_by = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EmployeeLeaveBalance(Base):
    """
    Employee leave balance
    Tracks leave balance for each employee
    """
    __tablename__ = "employee_leave_balance"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(50), nullable=False, index=True)
    
    # Employee and Leave Type
    employee_id = Column(String(36), ForeignKey("employees.id"), nullable=False, index=True)
    leave_policy_id = Column(String(36), ForeignKey("leave_policies.id"), nullable=False, index=True)
    leave_type = Column(SQLEnum(LeaveType), nullable=False, index=True)
    
    # Balance for Financial Year
    financial_year = Column(String(10), nullable=False)  # e.g., "2026-27"
    
    # Balance Details
    opening_balance = Column(Float, default=0.0)
    accrued = Column(Float, default=0.0)
    availed = Column(Float, default=0.0)
    carry_forward = Column(Float, default=0.0)
    encashed = Column(Float, default=0.0)
    lapsed = Column(Float, default=0.0)
    current_balance = Column(Float, default=0.0)
    
    # Pending Applications
    pending_approval = Column(Float, default=0.0)
    
    # Last Updated
    last_accrual_date = Column(Date)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Audit Fields
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id])
    leave_policy = relationship("LeavePolicyMaster")


class LeaveApplication(Base):
    """
    Leave application
    Employee leave requests
    """
    __tablename__ = "leave_applications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(50), nullable=False, index=True)
    
    # Application Details
    application_code = Column(String(50), nullable=False, unique=True)
    employee_id = Column(String(36), ForeignKey("employees.id"), nullable=False, index=True)
    leave_policy_id = Column(String(36), ForeignKey("leave_policies.id"), nullable=False)
    leave_type = Column(SQLEnum(LeaveType), nullable=False, index=True)
    
    # Leave Period
    from_date = Column(Date, nullable=False, index=True)
    to_date = Column(Date, nullable=False, index=True)
    from_period = Column(SQLEnum(LeavePeriod), default=LeavePeriod.FULL_DAY)
    to_period = Column(SQLEnum(LeavePeriod), default=LeavePeriod.FULL_DAY)
    total_days = Column(Float, nullable=False)
    
    # Reason and Documents
    reason = Column(Text, nullable=False)
    contact_during_leave = Column(String(200))
    address_during_leave = Column(Text)
    supporting_documents = Column(Text)  # JSON array of URLs
    
    # Status and Workflow
    status = Column(SQLEnum(LeaveStatus), nullable=False, default=LeaveStatus.DRAFT, index=True)
    applied_date = Column(Date)
    
    # Approval Chain
    reporting_manager_id = Column(String(36))
    reporting_manager_status = Column(String(20))
    reporting_manager_remarks = Column(Text)
    reporting_manager_date = Column(DateTime)
    
    hr_approver_id = Column(String(36))
    hr_approver_status = Column(String(20))
    hr_approver_remarks = Column(Text)
    hr_approver_date = Column(DateTime)
    
    final_approver_id = Column(String(36))
    final_approver_status = Column(String(20))
    final_approver_remarks = Column(Text)
    final_approver_date = Column(DateTime)
    
    # Rejection
    rejection_reason = Column(Text)
    
    # Cancellation
    is_cancelled = Column(Boolean, default=False)
    cancelled_by = Column(String(36))
    cancellation_reason = Column(Text)
    cancelled_at = Column(DateTime)
    
    # Balance Impact
    balance_before = Column(Float)
    balance_after = Column(Float)
    
    # Audit Fields
    is_deleted = Column(Boolean, default=False)
    created_by = Column(String(255))
    updated_by = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id])
    leave_policy = relationship("LeavePolicyMaster")


class LeaveEncashment(Base):
    """
    Leave encashment requests
    Convert leave balance to cash
    """
    __tablename__ = "leave_encashment"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(50), nullable=False, index=True)
    
    # Employee and Leave Type
    employee_id = Column(String(36), ForeignKey("employees.id"), nullable=False, index=True)
    leave_policy_id = Column(String(36), ForeignKey("leave_policies.id"), nullable=False)
    leave_type = Column(SQLEnum(LeaveType), nullable=False)
    
    # Encashment Details
    encashment_code = Column(String(50), nullable=False, unique=True)
    financial_year = Column(String(10), nullable=False)
    days_to_encash = Column(Float, nullable=False)
    per_day_amount = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    
    # Balance Before/After
    balance_before = Column(Float)
    balance_after = Column(Float)
    
    # Status
    status = Column(SQLEnum(LeaveStatus), nullable=False, default=LeaveStatus.PENDING)
    
    # Approval
    approved_by = Column(String(36))
    approved_at = Column(DateTime)
    rejection_reason = Column(Text)
    
    # Payment
    is_paid = Column(Boolean, default=False)
    payment_date = Column(Date)
    payment_reference = Column(String(100))
    
    # Audit Fields
    is_deleted = Column(Boolean, default=False)
    created_by = Column(String(255))
    updated_by = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id])
    leave_policy = relationship("LeavePolicyMaster")


# ============================================================================
# INDEXES
# ============================================================================

# Additional composite indexes for performance
from sqlalchemy import Index

Index('idx_attendance_emp_date', Attendance.employee_id, Attendance.attendance_date)
Index('idx_biometric_emp_datetime', BiometricLog.employee_id, BiometricLog.log_datetime)
Index('idx_leave_app_emp_status', LeaveApplication.employee_id, LeaveApplication.status)
Index('idx_leave_balance_emp_fy', EmployeeLeaveBalance.employee_id, EmployeeLeaveBalance.financial_year)
