/**
 * Attendance & Leave Management API Service
 * Handles all API calls for attendance and leave module
 */

import axios from 'axios';
import {
  Shift,
  ShiftCreate,
  EmployeeShiftAssignment,
  Attendance,
  CheckInRequest,
  CheckOutRequest,
  MobileCheckInRequest,
  AttendanceDashboardStats,
  LeavePolicy,
  LeavePolicyCreate,
  LeaveBalance,
  EmployeeLeaveBalanceSummary,
  LeaveApplication,
  LeaveApplicationCreate,
  LeaveDashboardStats,
  PaginatedResponse,
  LeaveType
} from '../types/attendance.types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// ============================================================================
// SHIFT MANAGEMENT API
// ============================================================================

export const shiftApi = {
  // List shifts
  async list(params: {
    page?: number;
    page_size?: number;
    search?: string;
    shift_type?: string;
    is_active?: boolean;
  }): Promise<PaginatedResponse<Shift>> {
    const response = await axios.get(`${API_BASE_URL}/attendance/shifts`, { params });
    return response.data;
  },

  // Get shift by ID
  async get(id: string): Promise<Shift> {
    const response = await axios.get(`${API_BASE_URL}/attendance/shifts/${id}`);
    return response.data;
  },

  // Create shift
  async create(data: ShiftCreate): Promise<Shift> {
    const response = await axios.post(`${API_BASE_URL}/attendance/shifts`, data);
    return response.data;
  },

  // Update shift
  async update(id: string, data: Partial<ShiftCreate>): Promise<Shift> {
    const response = await axios.put(`${API_BASE_URL}/attendance/shifts/${id}`, data);
    return response.data;
  },

  // Delete shift
  async delete(id: string): Promise<void> {
    await axios.delete(`${API_BASE_URL}/attendance/shifts/${id}`);
  },

  // Assign shift to employee
  async assignToEmployee(assignment: EmployeeShiftAssignment): Promise<{ message: string; assignment_id: string }> {
    const response = await axios.post(`${API_BASE_URL}/attendance/shifts/assign-employee`, assignment);
    return response.data;
  }
};

// ============================================================================
// ATTENDANCE API
// ============================================================================

export const attendanceApi = {
  // Check-in
  async checkIn(request: CheckInRequest): Promise<Attendance> {
    const response = await axios.post(`${API_BASE_URL}/attendance/check-in`, request);
    return response.data;
  },

  // Check-out
  async checkOut(request: CheckOutRequest): Promise<Attendance> {
    const response = await axios.post(`${API_BASE_URL}/attendance/check-out`, request);
    return response.data;
  },

  // Mobile check-in
  async mobileCheckIn(request: MobileCheckInRequest): Promise<any> {
    const response = await axios.post(`${API_BASE_URL}/attendance/mobile/check-in`, request);
    return response.data;
  },

  // Mobile check-out
  async mobileCheckOut(request: MobileCheckInRequest): Promise<any> {
    const response = await axios.post(`${API_BASE_URL}/attendance/mobile/check-out`, request);
    return response.data;
  },

  // List attendance records
  async list(params: {
    page?: number;
    page_size?: number;
    employee_id?: string;
    from_date?: string;
    to_date?: string;
    status?: string;
  }): Promise<PaginatedResponse<Attendance>> {
    const response = await axios.get(`${API_BASE_URL}/attendance`, { params });
    return response.data;
  },

  // Get attendance by ID
  async get(id: string): Promise<Attendance> {
    const response = await axios.get(`${API_BASE_URL}/attendance/${id}`);
    return response.data;
  },

  // Get dashboard stats
  async getDashboardStats(): Promise<AttendanceDashboardStats> {
    const response = await axios.get(`${API_BASE_URL}/attendance/dashboard/stats`);
    return response.data;
  },

  // Get stats for a specific date
  async getStats(date: string): Promise<AttendanceDashboardStats> {
    const response = await axios.get(`${API_BASE_URL}/attendance/stats`, {
      params: { date }
    });
    return response.data;
  },

  // Create manual attendance
  async createManual(data: {
    employee_id: string;
    attendance_date: string;
    shift_id?: string;
    actual_check_in?: string;
    actual_check_out?: string;
    status: string;
    remarks?: string;
    is_manual_entry: boolean;
    manual_entry_reason?: string;
  }): Promise<Attendance> {
    const response = await axios.post(`${API_BASE_URL}/attendance/manual`, data);
    return response.data;
  },

  // Update attendance
  async update(id: string, data: Partial<Attendance>): Promise<Attendance> {
    const response = await axios.put(`${API_BASE_URL}/attendance/${id}`, data);
    return response.data;
  }
};

// ============================================================================
// BIOMETRIC API
// ============================================================================

export const biometricApi = {
  // Create biometric log
  async createLog(data: {
    employee_id: string;
    biometric_id?: string;
    log_datetime: string;
    check_type: string;
    device_id?: string;
    device_name?: string;
    device_location?: string;
    verification_method?: string;
    verification_score?: number;
  }): Promise<any> {
    const response = await axios.post(`${API_BASE_URL}/attendance/biometric/log`, data);
    return response.data;
  },

  // Bulk sync biometric logs
  async syncLogs(logs: any[]): Promise<{ message: string; processed_ids: string[] }> {
    const response = await axios.post(`${API_BASE_URL}/attendance/biometric/sync`, logs);
    return response.data;
  }
};

// ============================================================================
// LEAVE POLICY API
// ============================================================================

export const leavePolicyApi = {
  // List leave policies
  async list(params: {
    page?: number;
    page_size?: number;
    search?: string;
    leave_type?: string;
    is_active?: boolean;
  }): Promise<PaginatedResponse<LeavePolicy>> {
    const response = await axios.get(`${API_BASE_URL}/leave/policies`, { params });
    return response.data;
  },

  // Get leave policy by ID
  async get(id: string): Promise<LeavePolicy> {
    const response = await axios.get(`${API_BASE_URL}/leave/policies/${id}`);
    return response.data;
  },

  // Create leave policy
  async create(data: LeavePolicyCreate): Promise<LeavePolicy> {
    const response = await axios.post(`${API_BASE_URL}/leave/policies`, data);
    return response.data;
  },

  // Update leave policy
  async update(id: string, data: Partial<LeavePolicyCreate>): Promise<LeavePolicy> {
    const response = await axios.put(`${API_BASE_URL}/leave/policies/${id}`, data);
    return response.data;
  },

  // Delete leave policy
  async delete(id: string): Promise<void> {
    await axios.delete(`${API_BASE_URL}/leave/policies/${id}`);
  }
};

// ============================================================================
// LEAVE BALANCE API
// ============================================================================

export const leaveBalanceApi = {
  // Get employee's leave balance
  async getEmployeeBalance(employee_id: string, financial_year: string): Promise<EmployeeLeaveBalanceSummary> {
    const response = await axios.get(`${API_BASE_URL}/leave/balance/${employee_id}/${financial_year}`);
    return response.data;
  },

  // Initialize leave balance
  async initialize(employee_id: string, policy_id: string, financial_year: string): Promise<any> {
    const response = await axios.post(`${API_BASE_URL}/leave/balance/initialize`, null, {
      params: { employee_id, policy_id, financial_year }
    });
    return response.data;
  },

  // Accrue leave
  async accrue(
    employee_id: string,
    leave_type: LeaveType,
    financial_year: string,
    accrual_amount: number
  ): Promise<any> {
    const response = await axios.post(`${API_BASE_URL}/leave/balance/accrue`, null, {
      params: { employee_id, leave_type, financial_year, accrual_amount }
    });
    return response.data;
  }
};

// ============================================================================
// LEAVE APPLICATION API
// ============================================================================

export const leaveApplicationApi = {
  // List leave applications
  async list(params: {
    page?: number;
    page_size?: number;
    employee_id?: string;
    status?: string;
    leave_type?: string;
    from_date?: string;
    to_date?: string;
  }): Promise<PaginatedResponse<LeaveApplication>> {
    const response = await axios.get(`${API_BASE_URL}/leave/applications`, { params });
    return response.data;
  },

  // Alias for list (backward compatibility)
  async listApplications(params: {
    page?: number;
    page_size?: number;
    employee_id?: string;
    status?: string;
    leave_type?: string;
    from_date?: string;
    to_date?: string;
    search?: string;
  }): Promise<PaginatedResponse<LeaveApplication>> {
    const response = await axios.get(`${API_BASE_URL}/leave/applications`, { params });
    return response.data;
  },

  // List leave types
  async listLeaveTypes(params?: {
    page?: number;
    page_size?: number;
    is_active?: boolean;
  }): Promise<PaginatedResponse<any>> {
    const response = await axios.get(`${API_BASE_URL}/leave/types`, { params });
    return response.data;
  },

  // List leave balances
  async listBalances(params?: {
    page?: number;
    page_size?: number;
    employee_id?: string;
  }): Promise<PaginatedResponse<LeaveBalance>> {
    const response = await axios.get(`${API_BASE_URL}/leave/balances`, { params });
    return response.data;
  },

  // Get leave application by ID
  async get(id: string): Promise<LeaveApplication> {
    const response = await axios.get(`${API_BASE_URL}/leave/applications/${id}`);
    return response.data;
  },

  // Get dashboard stats
  async getDashboardStats(): Promise<LeaveDashboardStats> {
    const response = await axios.get(`${API_BASE_URL}/leave/applications/dashboard/stats`);
    return response.data;
  },

  // Create leave application
  async create(data: LeaveApplicationCreate): Promise<LeaveApplication> {
    const response = await axios.post(`${API_BASE_URL}/leave/applications`, data);
    return response.data;
  },

  // Alias for create (backward compatibility)
  async createApplication(data: LeaveApplicationCreate): Promise<LeaveApplication> {
    const response = await axios.post(`${API_BASE_URL}/leave/applications`, data);
    return response.data;
  },

  // Update leave application
  async update(id: string, data: Partial<LeaveApplicationCreate>): Promise<LeaveApplication> {
    const response = await axios.put(`${API_BASE_URL}/leave/applications/${id}`, data);
    return response.data;
  },

  // Submit leave application
  async submit(id: string): Promise<LeaveApplication> {
    const response = await axios.post(`${API_BASE_URL}/leave/applications/${id}/submit`);
    return response.data;
  },

  // Approve/Reject leave application
  async approve(
    id: string,
    approver_level: 'REPORTING_MANAGER' | 'HR' | 'FINAL',
    action: 'APPROVE' | 'REJECT',
    remarks?: string
  ): Promise<LeaveApplication> {
    const response = await axios.post(
      `${API_BASE_URL}/leave/applications/${id}/approve?approver_level=${approver_level}`,
      { action, remarks }
    );
    return response.data;
  },

  // Approve leave application (simplified)
  async approveApplication(id: number, data: { remarks?: string }): Promise<LeaveApplication> {
    const response = await axios.post(
      `${API_BASE_URL}/leave/applications/${id}/approve`,
      { action: 'APPROVE', ...data }
    );
    return response.data;
  },

  // Reject leave application (simplified)
  async rejectApplication(id: number, data: { remarks: string }): Promise<LeaveApplication> {
    const response = await axios.post(
      `${API_BASE_URL}/leave/applications/${id}/approve`,
      { action: 'REJECT', ...data }
    );
    return response.data;
  },

  // Cancel leave application
  async cancel(id: string, cancellation_reason: string): Promise<LeaveApplication> {
    const response = await axios.post(`${API_BASE_URL}/leave/applications/${id}/cancel`, {
      cancellation_reason
    });
    return response.data;
  },

  // Cancel leave application (simplified)
  async cancelApplication(id: number): Promise<LeaveApplication> {
    const response = await axios.post(`${API_BASE_URL}/leave/applications/${id}/cancel`, {
      cancellation_reason: 'Cancelled by user'
    });
    return response.data;
  },

  // Delete leave application
  async delete(id: string): Promise<void> {
    await axios.delete(`${API_BASE_URL}/leave/applications/${id}`);
  }
};

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

export const attendanceUtils = {
  // Format time for display
  formatTime(time?: string): string {
    if (!time) return '-';
    return new Date(time).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  },

  // Format duration in hours
  formatHours(hours: number): string {
    const h = Math.floor(hours);
    const m = Math.round((hours - h) * 60);
    return m > 0 ? `${h}h ${m}m` : `${h}h`;
  },

  // Calculate work duration
  calculateDuration(checkIn?: string, checkOut?: string): number {
    if (!checkIn || !checkOut) return 0;
    const diff = new Date(checkOut).getTime() - new Date(checkIn).getTime();
    return diff / (1000 * 60 * 60); // Convert to hours
  },

  // Get status color class
  getStatusColor(status: string): string {
    const colors: Record<string, string> = {
      PRESENT: 'text-green-600 bg-green-100',
      ABSENT: 'text-red-600 bg-red-100',
      HALF_DAY: 'text-yellow-600 bg-yellow-100',
      LEAVE: 'text-blue-600 bg-blue-100',
      HOLIDAY: 'text-purple-600 bg-purple-100',
      WEEK_OFF: 'text-gray-600 bg-gray-100',
      ON_DUTY: 'text-indigo-600 bg-indigo-100'
    };
    return colors[status] || 'text-gray-600 bg-gray-100';
  }
};

export const leaveUtils = {
  // Calculate leave days
  calculateLeaveDays(
    fromDate: string,
    toDate: string,
    fromPeriod: string = 'FULL_DAY',
    toPeriod: string = 'FULL_DAY'
  ): number {
    const start = new Date(fromDate);
    const end = new Date(toDate);
    const diffTime = Math.abs(end.getTime() - start.getTime());
    let days = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;

    // Adjust for half days
    if (fromPeriod !== 'FULL_DAY') days -= 0.5;
    if (toPeriod !== 'FULL_DAY') days -= 0.5;

    return days;
  },

  // Get leave status color
  getStatusColor(status: string): string {
    const colors: Record<string, string> = {
      DRAFT: 'text-gray-600 bg-gray-100',
      PENDING: 'text-yellow-600 bg-yellow-100',
      APPROVED: 'text-green-600 bg-green-100',
      REJECTED: 'text-red-600 bg-red-100',
      CANCELLED: 'text-orange-600 bg-orange-100',
      WITHDRAWN: 'text-gray-600 bg-gray-100'
    };
    return colors[status] || 'text-gray-600 bg-gray-100';
  },

  // Get leave type color
  getTypeColor(leaveType: string): string {
    const colors: Record<string, string> = {
      CASUAL_LEAVE: 'text-blue-600 bg-blue-50',
      SICK_LEAVE: 'text-red-600 bg-red-50',
      EARNED_LEAVE: 'text-green-600 bg-green-50',
      PRIVILEGE_LEAVE: 'text-purple-600 bg-purple-50',
      MATERNITY_LEAVE: 'text-pink-600 bg-pink-50',
      PATERNITY_LEAVE: 'text-indigo-600 bg-indigo-50',
      COMPENSATORY_OFF: 'text-orange-600 bg-orange-50',
      LOSS_OF_PAY: 'text-red-600 bg-red-50',
      SABBATICAL: 'text-teal-600 bg-teal-50',
      STUDY_LEAVE: 'text-cyan-600 bg-cyan-50'
    };
    return colors[leaveType] || 'text-gray-600 bg-gray-50';
  },

  // Get current financial year
  getCurrentFinancialYear(): string {
    const today = new Date();
    const year = today.getFullYear();
    const month = today.getMonth();
    
    if (month >= 3) { // April onwards
      return `${year}-${String(year + 1).slice(2)}`;
    } else {
      return `${year - 1}-${String(year).slice(2)}`;
    }
  }
};

// Export all APIs
export const attendanceService = {
  shift: shiftApi,
  attendance: attendanceApi,
  biometric: biometricApi,
  leavePolicy: leavePolicyApi,
  leaveBalance: leaveBalanceApi,
  leaveApplication: leaveApplicationApi,
  leave: leaveApplicationApi, // Alias for backward compatibility
  attendanceUtils,
  leaveUtils
};

export default attendanceService;
