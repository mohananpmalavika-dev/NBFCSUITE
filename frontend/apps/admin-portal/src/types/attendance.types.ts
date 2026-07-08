/**
 * Attendance & Leave Management Module TypeScript Types
 * Maps to backend attendance and leave models
 */

// ============================================================================
// ENUMS
// ============================================================================

export enum ShiftType {
  REGULAR = 'REGULAR',
  ROTATING = 'ROTATING',
  FLEXIBLE = 'FLEXIBLE',
  NIGHT = 'NIGHT',
  SPLIT = 'SPLIT'
}

export enum AttendanceStatus {
  PRESENT = 'PRESENT',
  ABSENT = 'ABSENT',
  HALF_DAY = 'HALF_DAY',
  LEAVE = 'LEAVE',
  HOLIDAY = 'HOLIDAY',
  WEEK_OFF = 'WEEK_OFF',
  ON_DUTY = 'ON_DUTY'
}

export enum CheckType {
  CHECK_IN = 'CHECK_IN',
  CHECK_OUT = 'CHECK_OUT',
  BREAK_START = 'BREAK_START',
  BREAK_END = 'BREAK_END'
}

export enum CheckMethod {
  BIOMETRIC = 'BIOMETRIC',
  MOBILE = 'MOBILE',
  WEB = 'WEB',
  RFID = 'RFID',
  MANUAL = 'MANUAL'
}

export enum LeaveType {
  CASUAL_LEAVE = 'CASUAL_LEAVE',
  SICK_LEAVE = 'SICK_LEAVE',
  EARNED_LEAVE = 'EARNED_LEAVE',
  PRIVILEGE_LEAVE = 'PRIVILEGE_LEAVE',
  MATERNITY_LEAVE = 'MATERNITY_LEAVE',
  PATERNITY_LEAVE = 'PATERNITY_LEAVE',
  COMPENSATORY_OFF = 'COMPENSATORY_OFF',
  LOSS_OF_PAY = 'LOSS_OF_PAY',
  SABBATICAL = 'SABBATICAL',
  STUDY_LEAVE = 'STUDY_LEAVE'
}

export enum LeaveStatus {
  DRAFT = 'DRAFT',
  PENDING = 'PENDING',
  APPROVED = 'APPROVED',
  REJECTED = 'REJECTED',
  CANCELLED = 'CANCELLED',
  WITHDRAWN = 'WITHDRAWN'
}

export enum LeavePeriod {
  FULL_DAY = 'FULL_DAY',
  FIRST_HALF = 'FIRST_HALF',
  SECOND_HALF = 'SECOND_HALF'
}

// ============================================================================
// SHIFT TYPES
// ============================================================================

export interface Shift {
  id: string;
  tenant_id: string;
  shift_code: string;
  shift_name: string;
  shift_type: ShiftType;
  start_time: string; // HH:mm:ss format
  end_time: string;
  grace_period_minutes: number;
  half_day_hours: number;
  full_day_hours: number;
  break_duration_minutes: number;
  break_start_time?: string;
  break_end_time?: string;
  week_off_1?: string;
  week_off_2?: string;
  allow_overtime: boolean;
  overtime_start_after_minutes: number;
  is_active: boolean;
  effective_from?: string;
  effective_to?: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface ShiftCreate {
  shift_code: string;
  shift_name: string;
  shift_type: ShiftType;
  start_time: string;
  end_time: string;
  grace_period_minutes?: number;
  half_day_hours?: number;
  full_day_hours?: number;
  break_duration_minutes?: number;
  break_start_time?: string;
  break_end_time?: string;
  week_off_1?: string;
  week_off_2?: string;
  allow_overtime?: boolean;
  overtime_start_after_minutes?: number;
  effective_from?: string;
  effective_to?: string;
  description?: string;
}

export interface EmployeeShiftAssignment {
  employee_id: string;
  shift_id: string;
  effective_from: string;
  effective_to?: string;
}

// ============================================================================
// ATTENDANCE TYPES
// ============================================================================

export interface Attendance {
  id: string;
  tenant_id: string;
  employee_id: string;
  attendance_date: string;
  shift_id?: string;
  scheduled_start_time?: string;
  scheduled_end_time?: string;
  actual_check_in?: string;
  actual_check_out?: string;
  late_by_minutes: number;
  early_out_minutes: number;
  total_work_hours: number;
  overtime_hours: number;
  break_hours: number;
  status: AttendanceStatus;
  check_in_location?: string;
  check_out_location?: string;
  check_in_device?: string;
  check_out_device?: string;
  check_in_method?: CheckMethod;
  check_out_method?: CheckMethod;
  remarks?: string;
  is_manual_entry: boolean;
  manual_entry_reason?: string;
  is_approved: boolean;
  approved_by?: string;
  approved_at?: string;
  created_at: string;
  updated_at: string;
  
  // Related data
  employee?: any;
  shift?: Shift;
}

export interface CheckInRequest {
  employee_id: string;
  check_in_time?: string;
  location?: {
    lat: number;
    lng: number;
    address?: string;
  };
  device_info?: string;
  method?: CheckMethod;
}

export interface CheckOutRequest {
  employee_id: string;
  check_out_time?: string;
  location?: {
    lat: number;
    lng: number;
    address?: string;
  };
  device_info?: string;
  method?: CheckMethod;
}

export interface MobileCheckInRequest {
  employee_id: string;
  latitude: number;
  longitude: number;
  address?: string;
  device_info?: string;
}

export interface AttendanceDashboardStats {
  total_employees: number;
  present_today: number;
  absent_today: number;
  on_leave_today: number;
  late_arrivals: number;
  early_departures: number;
  avg_work_hours: number;
  attendance_percentage: number;
}

export interface BiometricLog {
  id: string;
  tenant_id: string;
  employee_id: string;
  biometric_id?: string;
  log_datetime: string;
  check_type: CheckType;
  device_id?: string;
  device_name?: string;
  device_location?: string;
  verification_method?: string;
  verification_score?: number;
  attendance_id?: string;
  is_processed: boolean;
  processed_at?: string;
  created_at: string;
  
  employee?: any;
}

// ============================================================================
// LEAVE POLICY TYPES
// ============================================================================

export interface LeavePolicy {
  id: string;
  tenant_id: string;
  policy_code: string;
  policy_name: string;
  leave_type: LeaveType;
  annual_quota: number;
  max_consecutive_days?: number;
  min_notice_days: number;
  max_carry_forward: number;
  is_accrual_based: boolean;
  accrual_frequency?: string;
  accrual_rate?: number;
  applicable_after_days: number;
  applicable_gender?: string;
  allow_half_day: boolean;
  allow_negative_balance: boolean;
  require_document: boolean;
  require_document_after_days?: number;
  include_weekends: boolean;
  include_holidays: boolean;
  is_encashable: boolean;
  encashment_min_balance?: number;
  encashment_percentage?: number;
  is_active: boolean;
  effective_from?: string;
  effective_to?: string;
  description?: string;
  rules?: string;
  created_at: string;
}

export interface LeavePolicyCreate {
  policy_code: string;
  policy_name: string;
  leave_type: LeaveType;
  annual_quota: number;
  max_consecutive_days?: number;
  min_notice_days?: number;
  max_carry_forward?: number;
  is_accrual_based?: boolean;
  accrual_frequency?: string;
  accrual_rate?: number;
  applicable_after_days?: number;
  applicable_gender?: string;
  allow_half_day?: boolean;
  allow_negative_balance?: boolean;
  require_document?: boolean;
  require_document_after_days?: number;
  include_weekends?: boolean;
  include_holidays?: boolean;
  is_encashable?: boolean;
  encashment_min_balance?: number;
  encashment_percentage?: number;
  effective_from?: string;
  effective_to?: string;
  description?: string;
  rules?: Record<string, any>;
}

// ============================================================================
// LEAVE BALANCE TYPES
// ============================================================================

export interface LeaveBalance {
  id: string;
  tenant_id: string;
  employee_id: string;
  leave_policy_id: string;
  leave_type: LeaveType;
  financial_year: string;
  opening_balance: number;
  accrued: number;
  availed: number;
  carry_forward: number;
  encashed: number;
  lapsed: number;
  current_balance: number;
  pending_approval: number;
  last_accrual_date?: string;
  last_updated: string;
  
  leave_policy?: LeavePolicy;
}

export interface EmployeeLeaveBalanceSummary {
  employee_id: string;
  financial_year: string;
  balances: LeaveBalance[];
}

// ============================================================================
// LEAVE APPLICATION TYPES
// ============================================================================

export interface LeaveApplication {
  id: string;
  tenant_id: string;
  application_code: string;
  employee_id: string;
  leave_policy_id: string;
  leave_type: LeaveType;
  from_date: string;
  to_date: string;
  from_period: LeavePeriod;
  to_period: LeavePeriod;
  total_days: number;
  reason: string;
  contact_during_leave?: string;
  address_during_leave?: string;
  supporting_documents?: string;
  status: LeaveStatus;
  applied_date?: string;
  reporting_manager_id?: string;
  reporting_manager_status?: string;
  reporting_manager_remarks?: string;
  reporting_manager_date?: string;
  hr_approver_id?: string;
  hr_approver_status?: string;
  hr_approver_remarks?: string;
  hr_approver_date?: string;
  final_approver_id?: string;
  final_approver_status?: string;
  final_approver_remarks?: string;
  final_approver_date?: string;
  rejection_reason?: string;
  is_cancelled: boolean;
  cancelled_by?: string;
  cancellation_reason?: string;
  cancelled_at?: string;
  balance_before?: number;
  balance_after?: number;
  created_at: string;
  updated_at: string;
  
  employee?: any;
  leave_policy?: LeavePolicy;
}

export interface LeaveApplicationCreate {
  employee_id: string;
  leave_policy_id: string;
  leave_type: LeaveType;
  from_date: string;
  to_date: string;
  from_period?: LeavePeriod;
  to_period?: LeavePeriod;
  reason: string;
  contact_during_leave?: string;
  address_during_leave?: string;
  supporting_documents?: string[];
}

export interface LeaveDashboardStats {
  total_applications: number;
  pending_approval: number;
  approved: number;
  rejected: number;
  on_leave_today: number;
  upcoming_leaves: number;
}

// ============================================================================
// API RESPONSE TYPES
// ============================================================================

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

export interface DateRange {
  from_date: string;
  to_date: string;
}

export interface LocationInfo {
  lat: number;
  lng: number;
  address?: string;
}

// ============================================================================
// LEAVE TYPE DISPLAY HELPERS
// ============================================================================

export const LEAVE_TYPE_LABELS: Record<LeaveType, string> = {
  [LeaveType.CASUAL_LEAVE]: 'Casual Leave',
  [LeaveType.SICK_LEAVE]: 'Sick Leave',
  [LeaveType.EARNED_LEAVE]: 'Earned Leave',
  [LeaveType.PRIVILEGE_LEAVE]: 'Privilege Leave',
  [LeaveType.MATERNITY_LEAVE]: 'Maternity Leave',
  [LeaveType.PATERNITY_LEAVE]: 'Paternity Leave',
  [LeaveType.COMPENSATORY_OFF]: 'Compensatory Off',
  [LeaveType.LOSS_OF_PAY]: 'Loss of Pay',
  [LeaveType.SABBATICAL]: 'Sabbatical',
  [LeaveType.STUDY_LEAVE]: 'Study Leave'
};

export const LEAVE_STATUS_LABELS: Record<LeaveStatus, string> = {
  [LeaveStatus.DRAFT]: 'Draft',
  [LeaveStatus.PENDING]: 'Pending Approval',
  [LeaveStatus.APPROVED]: 'Approved',
  [LeaveStatus.REJECTED]: 'Rejected',
  [LeaveStatus.CANCELLED]: 'Cancelled',
  [LeaveStatus.WITHDRAWN]: 'Withdrawn'
};

export const ATTENDANCE_STATUS_LABELS: Record<AttendanceStatus, string> = {
  [AttendanceStatus.PRESENT]: 'Present',
  [AttendanceStatus.ABSENT]: 'Absent',
  [AttendanceStatus.HALF_DAY]: 'Half Day',
  [AttendanceStatus.LEAVE]: 'On Leave',
  [AttendanceStatus.HOLIDAY]: 'Holiday',
  [AttendanceStatus.WEEK_OFF]: 'Week Off',
  [AttendanceStatus.ON_DUTY]: 'On Duty'
};
