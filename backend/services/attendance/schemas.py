"""
Attendance & Leave Management - Pydantic Schemas
Request and response models for attendance and leave APIs
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date, time
from enum import Enum


# ============================================================================
# ENUMS (matching database enums)
# ============================================================================

class ShiftTypeEnum(str, Enum):
    REGULAR = "REGULAR"
    ROTATING = "ROTATING"
    FLEXIBLE = "FLEXIBLE"
    NIGHT = "NIGHT"
    SPLIT = "SPLIT"


class AttendanceStatusEnum(str, Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    HALF_DAY = "HALF_DAY"
    LEAVE = "LEAVE"
    HOLIDAY = "HOLIDAY"
    WEEK_OFF = "WEEK_OFF"
    ON_DUTY = "ON_DUTY"


class CheckTypeEnum(str, Enum):
    CHECK_IN = "CHECK_IN"
    CHECK_OUT = "CHECK_OUT"
    BREAK_START = "BREAK_START"
    BREAK_END = "BREAK_END"


class CheckMethodEnum(str, Enum):
    BIOMETRIC = "BIOMETRIC"
    MOBILE = "MOBILE"
    WEB = "WEB"
    RFID = "RFID"
    MANUAL = "MANUAL"


class LeaveTypeEnum(str, Enum):
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


class LeaveStatusEnum(str, Enum):
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    WITHDRAWN = "WITHDRAWN"


class LeavePeriodEnum(str, Enum):
    FULL_DAY = "FULL_DAY"
    FIRST_HALF = "FIRST_HALF"
    SECOND_HALF = "SECOND_HALF"


# ============================================================================
# SHIFT SCHEMAS
# ============================================================================

class ShiftCreate(BaseModel):
    shift_code: str = Field(..., max_length=50)
    shift_name: str = Field(..., max_length=200)
    shift_type: ShiftTypeEnum
    start_time: time
    end_time: time
    grace_period_minutes: int = 15
    half_day_hours: float = 4.0
    full_day_hours: float = 8.0
    break_duration_minutes: int = 60
    break_start_time: Optional[time] = None
    break_end_time: Optional[time] = None
    week_off_1: Optional[str] = None
    week_off_2: Optional[str] = None
    allow_overtime: bool = False
    overtime_start_after_minutes: int = 30
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    description: Optional[str] = None


class ShiftUpdate(BaseModel):
    shift_name: Optional[str] = None
    shift_type: Optional[ShiftTypeEnum] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    grace_period_minutes: Optional[int] = None
    half_day_hours: Optional[float] = None
    full_day_hours: Optional[float] = None
    break_duration_minutes: Optional[int] = None
    break_start_time: Optional[time] = None
    break_end_time: Optional[time] = None
    week_off_1: Optional[str] = None
    week_off_2: Optional[str] = None
    allow_overtime: Optional[bool] = None
    overtime_start_after_minutes: Optional[int] = None
    is_active: Optional[bool] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    description: Optional[str] = None


class ShiftResponse(BaseModel):
    id: str
    tenant_id: str
    shift_code: str
    shift_name: str
    shift_type: ShiftTypeEnum
    start_time: time
    end_time: time
    grace_period_minutes: int
    half_day_hours: float
    full_day_hours: float
    break_duration_minutes: int
    break_start_time: Optional[time]
    break_end_time: Optional[time]
    week_off_1: Optional[str]
    week_off_2: Optional[str]
    allow_overtime: bool
    overtime_start_after_minutes: int
    is_active: bool
    effective_from: Optional[date]
    effective_to: Optional[date]
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ShiftListResponse(BaseModel):
    items: List[ShiftResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class EmployeeShiftAssignment(BaseModel):
    employee_id: str
    shift_id: str
    effective_from: date
    effective_to: Optional[date] = None


# ============================================================================
# ATTENDANCE SCHEMAS
# ============================================================================

class CheckInRequest(BaseModel):
    employee_id: str
    check_in_time: Optional[datetime] = None  # If not provided, use current time
    location: Optional[Dict[str, Any]] = None  # {lat, lng, address}
    device_info: Optional[str] = None
    method: CheckMethodEnum = CheckMethodEnum.WEB


class CheckOutRequest(BaseModel):
    employee_id: str
    check_out_time: Optional[datetime] = None
    location: Optional[Dict[str, Any]] = None
    device_info: Optional[str] = None
    method: CheckMethodEnum = CheckMethodEnum.WEB


class AttendanceCreate(BaseModel):
    employee_id: str
    attendance_date: date
    shift_id: Optional[str] = None
    actual_check_in: Optional[datetime] = None
    actual_check_out: Optional[datetime] = None
    status: AttendanceStatusEnum = AttendanceStatusEnum.ABSENT
    remarks: Optional[str] = None
    is_manual_entry: bool = False
    manual_entry_reason: Optional[str] = None


class AttendanceUpdate(BaseModel):
    shift_id: Optional[str] = None
    actual_check_in: Optional[datetime] = None
    actual_check_out: Optional[datetime] = None
    status: Optional[AttendanceStatusEnum] = None
    remarks: Optional[str] = None


class AttendanceResponse(BaseModel):
    id: str
    tenant_id: str
    employee_id: str
    attendance_date: date
    shift_id: Optional[str]
    scheduled_start_time: Optional[time]
    scheduled_end_time: Optional[time]
    actual_check_in: Optional[datetime]
    actual_check_out: Optional[datetime]
    late_by_minutes: int
    early_out_minutes: int
    total_work_hours: float
    overtime_hours: float
    break_hours: float
    status: AttendanceStatusEnum
    check_in_location: Optional[str]
    check_out_location: Optional[str]
    check_in_device: Optional[str]
    check_out_device: Optional[str]
    check_in_method: Optional[CheckMethodEnum]
    check_out_method: Optional[CheckMethodEnum]
    remarks: Optional[str]
    is_manual_entry: bool
    manual_entry_reason: Optional[str]
    is_approved: bool
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    # Related data
    employee: Optional[Any] = None
    shift: Optional[Any] = None

    class Config:
        from_attributes = True


class AttendanceListResponse(BaseModel):
    items: List[AttendanceResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class BiometricLogCreate(BaseModel):
    employee_id: str
    biometric_id: Optional[str] = None
    log_datetime: datetime
    check_type: CheckTypeEnum
    device_id: Optional[str] = None
    device_name: Optional[str] = None
    device_location: Optional[str] = None
    verification_method: Optional[str] = None
    verification_score: Optional[float] = None


class BiometricLogResponse(BaseModel):
    id: str
    tenant_id: str
    employee_id: str
    biometric_id: Optional[str]
    log_datetime: datetime
    check_type: CheckTypeEnum
    device_id: Optional[str]
    device_name: Optional[str]
    device_location: Optional[str]
    verification_method: Optional[str]
    verification_score: Optional[float]
    attendance_id: Optional[str]
    is_processed: bool
    processed_at: Optional[datetime]
    created_at: datetime
    
    employee: Optional[Any] = None

    class Config:
        from_attributes = True


class AttendanceRegularizationRequest(BaseModel):
    attendance_id: str
    employee_id: str
    requested_check_in: Optional[datetime] = None
    requested_check_out: Optional[datetime] = None
    reason: str
    supporting_documents: Optional[List[str]] = None


class AttendanceRegularizationResponse(BaseModel):
    id: str
    tenant_id: str
    attendance_id: str
    employee_id: str
    requested_check_in: Optional[datetime]
    requested_check_out: Optional[datetime]
    reason: str
    supporting_documents: Optional[str]
    status: LeaveStatusEnum
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    rejection_reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AttendanceDashboardStats(BaseModel):
    total_employees: int
    present_today: int
    absent_today: int
    on_leave_today: int
    late_arrivals: int
    early_departures: int
    avg_work_hours: float
    attendance_percentage: float


class EmployeeAttendanceSummary(BaseModel):
    employee_id: str
    employee_name: str
    month: str
    year: int
    total_working_days: int
    present_days: int
    absent_days: int
    leave_days: int
    half_days: int
    late_days: int
    total_work_hours: float
    avg_work_hours: float
    overtime_hours: float


# ============================================================================
# LEAVE POLICY SCHEMAS
# ============================================================================

class LeavePolicyCreate(BaseModel):
    policy_code: str = Field(..., max_length=50)
    policy_name: str = Field(..., max_length=200)
    leave_type: LeaveTypeEnum
    annual_quota: float
    max_consecutive_days: Optional[int] = None
    min_notice_days: int = 0
    max_carry_forward: float = 0.0
    is_accrual_based: bool = False
    accrual_frequency: Optional[str] = None
    accrual_rate: Optional[float] = None
    applicable_after_days: int = 0
    applicable_gender: Optional[str] = None
    allow_half_day: bool = True
    allow_negative_balance: bool = False
    require_document: bool = False
    require_document_after_days: Optional[int] = None
    include_weekends: bool = False
    include_holidays: bool = False
    is_encashable: bool = False
    encashment_min_balance: Optional[float] = None
    encashment_percentage: Optional[float] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    description: Optional[str] = None
    rules: Optional[Dict[str, Any]] = None


class LeavePolicyUpdate(BaseModel):
    policy_name: Optional[str] = None
    annual_quota: Optional[float] = None
    max_consecutive_days: Optional[int] = None
    min_notice_days: Optional[int] = None
    max_carry_forward: Optional[float] = None
    is_accrual_based: Optional[bool] = None
    accrual_frequency: Optional[str] = None
    accrual_rate: Optional[float] = None
    applicable_after_days: Optional[int] = None
    applicable_gender: Optional[str] = None
    allow_half_day: Optional[bool] = None
    allow_negative_balance: Optional[bool] = None
    require_document: Optional[bool] = None
    require_document_after_days: Optional[int] = None
    include_weekends: Optional[bool] = None
    include_holidays: Optional[bool] = None
    is_encashable: Optional[bool] = None
    encashment_min_balance: Optional[float] = None
    encashment_percentage: Optional[float] = None
    is_active: Optional[bool] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    description: Optional[str] = None
    rules: Optional[Dict[str, Any]] = None


class LeavePolicyResponse(BaseModel):
    id: str
    tenant_id: str
    policy_code: str
    policy_name: str
    leave_type: LeaveTypeEnum
    annual_quota: float
    max_consecutive_days: Optional[int]
    min_notice_days: int
    max_carry_forward: float
    is_accrual_based: bool
    accrual_frequency: Optional[str]
    accrual_rate: Optional[float]
    applicable_after_days: int
    applicable_gender: Optional[str]
    allow_half_day: bool
    allow_negative_balance: bool
    require_document: bool
    require_document_after_days: Optional[int]
    include_weekends: bool
    include_holidays: bool
    is_encashable: bool
    encashment_min_balance: Optional[float]
    encashment_percentage: Optional[float]
    is_active: bool
    effective_from: Optional[date]
    effective_to: Optional[date]
    description: Optional[str]
    rules: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class LeavePolicyListResponse(BaseModel):
    items: List[LeavePolicyResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# LEAVE BALANCE SCHEMAS
# ============================================================================

class LeaveBalanceResponse(BaseModel):
    id: str
    tenant_id: str
    employee_id: str
    leave_policy_id: str
    leave_type: LeaveTypeEnum
    financial_year: str
    opening_balance: float
    accrued: float
    availed: float
    carry_forward: float
    encashed: float
    lapsed: float
    current_balance: float
    pending_approval: float
    last_accrual_date: Optional[date]
    last_updated: datetime
    
    leave_policy: Optional[Any] = None

    class Config:
        from_attributes = True


class EmployeeLeaveBalanceSummary(BaseModel):
    employee_id: str
    financial_year: str
    balances: List[LeaveBalanceResponse]


# ============================================================================
# LEAVE APPLICATION SCHEMAS
# ============================================================================

class LeaveApplicationCreate(BaseModel):
    employee_id: str
    leave_policy_id: str
    leave_type: LeaveTypeEnum
    from_date: date
    to_date: date
    from_period: LeavePeriodEnum = LeavePeriodEnum.FULL_DAY
    to_period: LeavePeriodEnum = LeavePeriodEnum.FULL_DAY
    reason: str
    contact_during_leave: Optional[str] = None
    address_during_leave: Optional[str] = None
    supporting_documents: Optional[List[str]] = None


class LeaveApplicationUpdate(BaseModel):
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    from_period: Optional[LeavePeriodEnum] = None
    to_period: Optional[LeavePeriodEnum] = None
    reason: Optional[str] = None
    contact_during_leave: Optional[str] = None
    address_during_leave: Optional[str] = None
    supporting_documents: Optional[List[str]] = None


class LeaveApplicationResponse(BaseModel):
    id: str
    tenant_id: str
    application_code: str
    employee_id: str
    leave_policy_id: str
    leave_type: LeaveTypeEnum
    from_date: date
    to_date: date
    from_period: LeavePeriodEnum
    to_period: LeavePeriodEnum
    total_days: float
    reason: str
    contact_during_leave: Optional[str]
    address_during_leave: Optional[str]
    supporting_documents: Optional[str]
    status: LeaveStatusEnum
    applied_date: Optional[date]
    reporting_manager_id: Optional[str]
    reporting_manager_status: Optional[str]
    reporting_manager_remarks: Optional[str]
    reporting_manager_date: Optional[datetime]
    hr_approver_id: Optional[str]
    hr_approver_status: Optional[str]
    hr_approver_remarks: Optional[str]
    hr_approver_date: Optional[datetime]
    final_approver_id: Optional[str]
    final_approver_status: Optional[str]
    final_approver_remarks: Optional[str]
    final_approver_date: Optional[datetime]
    rejection_reason: Optional[str]
    is_cancelled: bool
    cancelled_by: Optional[str]
    cancellation_reason: Optional[str]
    cancelled_at: Optional[datetime]
    balance_before: Optional[float]
    balance_after: Optional[float]
    created_at: datetime
    updated_at: datetime
    
    employee: Optional[Any] = None
    leave_policy: Optional[Any] = None

    class Config:
        from_attributes = True


class LeaveApplicationListResponse(BaseModel):
    items: List[LeaveApplicationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class LeaveApprovalAction(BaseModel):
    action: str  # APPROVE, REJECT
    remarks: Optional[str] = None


class LeaveCancellationRequest(BaseModel):
    cancellation_reason: str


class LeaveDashboardStats(BaseModel):
    total_applications: int
    pending_approval: int
    approved: int
    rejected: int
    on_leave_today: int
    upcoming_leaves: int


# ============================================================================
# LEAVE ENCASHMENT SCHEMAS
# ============================================================================

class LeaveEncashmentRequest(BaseModel):
    employee_id: str
    leave_policy_id: str
    leave_type: LeaveTypeEnum
    financial_year: str
    days_to_encash: float


class LeaveEncashmentResponse(BaseModel):
    id: str
    tenant_id: str
    encashment_code: str
    employee_id: str
    leave_policy_id: str
    leave_type: LeaveTypeEnum
    financial_year: str
    days_to_encash: float
    per_day_amount: float
    total_amount: float
    balance_before: Optional[float]
    balance_after: Optional[float]
    status: LeaveStatusEnum
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    rejection_reason: Optional[str]
    is_paid: bool
    payment_date: Optional[date]
    payment_reference: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# MOBILE CHECK-IN SCHEMAS
# ============================================================================

class MobileCheckInRequest(BaseModel):
    employee_id: str
    latitude: float
    longitude: float
    address: Optional[str] = None
    device_info: Optional[str] = None


class MobileCheckOutRequest(BaseModel):
    employee_id: str
    latitude: float
    longitude: float
    address: Optional[str] = None
    device_info: Optional[str] = None


class MobileCheckInResponse(BaseModel):
    success: bool
    message: str
    attendance_id: str
    check_in_time: datetime
    shift_info: Optional[Dict[str, Any]] = None
