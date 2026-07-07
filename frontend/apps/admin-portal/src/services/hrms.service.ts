/**
 * HRMS API Service
 * Complete service layer for HRMS operations
 */

import { apiClient } from "@/lib/api/client";
import type {
  // Organization
  Organization,
  OrganizationCreate,
  OrganizationUpdate,
  OrganizationListItem,
  
  // Department
  Department,
  DepartmentCreate,
  DepartmentUpdate,
  DepartmentListItem,
  PaginatedDepartmentResponse,
  DepartmentTreeNode,
  DepartmentStats,
  DepartmentFilters,
  
  // Designation
  Designation,
  DesignationCreate,
  DesignationUpdate,
  DesignationListItem,
  PaginatedDesignationResponse,
  DesignationStats,
  DesignationFilters,
  
  // Employee
  Employee,
  EmployeeCreate,
  EmployeeUpdate,
  EmployeeListItem,
  PaginatedEmployeeResponse,
  EmployeeDashboardStats,
  EmployeeFilters,
  EmployeeSearchParams,
  EmployeeCardView,
  OrgChartNode,
} from "@/types/hrms.types";

const BASE_URL = "/api/v1";

// ============================================================================
// ORGANIZATION OPERATIONS
// ============================================================================

/**
 * Create new organization
 */
export const createOrganization = async (
  data: OrganizationCreate
): Promise<Organization> => {
  const response = await apiClient.post<Organization>(
    `${BASE_URL}/hrms/organizations`,
    data
  );
  return response.data;
};

/**
 * Get paginated list of organizations
 */
export const getOrganizations = async (
  page: number = 1,
  page_size: number = 20,
  search?: string,
  is_active?: boolean
): Promise<{ items: Organization[]; total: number; page: number; page_size: number; pages: number }> => {
  const params = new URLSearchParams();
  params.append("page", page.toString());
  params.append("page_size", page_size.toString());
  if (search) params.append("search", search);
  if (is_active !== undefined) params.append("is_active", is_active.toString());
  
  const response = await apiClient.get(
    `${BASE_URL}/hrms/organizations?${params.toString()}`
  );
  return response.data;
};

/**
 * Get all active organizations (for dropdowns)
 */
export const getActiveOrganizations = async (): Promise<OrganizationListItem[]> => {
  const response = await apiClient.get<OrganizationListItem[]>(
    `${BASE_URL}/hrms/organizations/active`
  );
  return response.data;
};

/**
 * Get organization by ID
 */
export const getOrganizationById = async (
  organizationId: number
): Promise<Organization> => {
  const response = await apiClient.get<Organization>(
    `${BASE_URL}/hrms/organizations/${organizationId}`
  );
  return response.data;
};

/**
 * Update organization
 */
export const updateOrganization = async (
  organizationId: number,
  data: OrganizationUpdate
): Promise<Organization> => {
  const response = await apiClient.put<Organization>(
    `${BASE_URL}/hrms/organizations/${organizationId}`,
    data
  );
  return response.data;
};

/**
 * Delete organization
 */
export const deleteOrganization = async (organizationId: number): Promise<void> => {
  await apiClient.delete(`${BASE_URL}/hrms/organizations/${organizationId}`);
};

// ============================================================================
// DEPARTMENT OPERATIONS
// ============================================================================

/**
 * Create new department
 */
export const createDepartment = async (
  data: DepartmentCreate
): Promise<Department> => {
  const response = await apiClient.post<Department>(
    `${BASE_URL}/hrms/departments`,
    data
  );
  return response.data;
};

/**
 * Get paginated list of departments with filters
 */
export const getDepartments = async (
  filters?: DepartmentFilters
): Promise<PaginatedDepartmentResponse> => {
  const params = new URLSearchParams();
  
  if (filters?.page) params.append("page", filters.page.toString());
  if (filters?.page_size) params.append("page_size", filters.page_size.toString());
  if (filters?.search) params.append("search", filters.search);
  if (filters?.organization_id) params.append("organization_id", filters.organization_id.toString());
  if (filters?.parent_department_id) params.append("parent_department_id", filters.parent_department_id.toString());
  if (filters?.is_active !== undefined) params.append("is_active", filters.is_active.toString());
  
  const response = await apiClient.get<PaginatedDepartmentResponse>(
    `${BASE_URL}/hrms/departments?${params.toString()}`
  );
  return response.data;
};

/**
 * Get department statistics
 */
export const getDepartmentStats = async (): Promise<DepartmentStats> => {
  const response = await apiClient.get<DepartmentStats>(
    `${BASE_URL}/hrms/departments/stats`
  );
  return response.data;
};

/**
 * Get department hierarchy tree
 */
export const getDepartmentTree = async (
  organizationId?: number
): Promise<DepartmentTreeNode[]> => {
  const params = new URLSearchParams();
  if (organizationId) params.append("organization_id", organizationId.toString());
  
  const response = await apiClient.get<DepartmentTreeNode[]>(
    `${BASE_URL}/hrms/departments/tree?${params.toString()}`
  );
  return response.data;
};

/**
 * Get department by ID
 */
export const getDepartmentById = async (
  departmentId: number
): Promise<Department> => {
  const response = await apiClient.get<Department>(
    `${BASE_URL}/hrms/departments/${departmentId}`
  );
  return response.data;
};

/**
 * Update department
 */
export const updateDepartment = async (
  departmentId: number,
  data: DepartmentUpdate
): Promise<Department> => {
  const response = await apiClient.put<Department>(
    `${BASE_URL}/hrms/departments/${departmentId}`,
    data
  );
  return response.data;
};

/**
 * Delete department
 */
export const deleteDepartment = async (departmentId: number): Promise<void> => {
  await apiClient.delete(`${BASE_URL}/hrms/departments/${departmentId}`);
};

// ============================================================================
// DESIGNATION OPERATIONS
// ============================================================================

/**
 * Create new designation
 */
export const createDesignation = async (
  data: DesignationCreate
): Promise<Designation> => {
  const response = await apiClient.post<Designation>(
    `${BASE_URL}/hrms/designations`,
    data
  );
  return response.data;
};

/**
 * Get paginated list of designations with filters
 */
export const getDesignations = async (
  filters?: DesignationFilters
): Promise<PaginatedDesignationResponse> => {
  const params = new URLSearchParams();
  
  if (filters?.page) params.append("page", filters.page.toString());
  if (filters?.page_size) params.append("page_size", filters.page_size.toString());
  if (filters?.search) params.append("search", filters.search);
  if (filters?.level !== undefined) params.append("level", filters.level.toString());
  if (filters?.grade) params.append("grade", filters.grade);
  if (filters?.is_active !== undefined) params.append("is_active", filters.is_active.toString());
  
  const response = await apiClient.get<PaginatedDesignationResponse>(
    `${BASE_URL}/hrms/designations?${params.toString()}`
  );
  return response.data;
};

/**
 * Get designation statistics
 */
export const getDesignationStats = async (): Promise<DesignationStats> => {
  const response = await apiClient.get<DesignationStats>(
    `${BASE_URL}/hrms/designations/stats`
  );
  return response.data;
};

/**
 * Get designation by ID
 */
export const getDesignationById = async (
  designationId: number
): Promise<Designation> => {
  const response = await apiClient.get<Designation>(
    `${BASE_URL}/hrms/designations/${designationId}`
  );
  return response.data;
};

/**
 * Update designation
 */
export const updateDesignation = async (
  designationId: number,
  data: DesignationUpdate
): Promise<Designation> => {
  const response = await apiClient.put<Designation>(
    `${BASE_URL}/hrms/designations/${designationId}`,
    data
  );
  return response.data;
};

/**
 * Delete designation
 */
export const deleteDesignation = async (designationId: number): Promise<void> => {
  await apiClient.delete(`${BASE_URL}/hrms/designations/${designationId}`);
};

// ============================================================================
// EMPLOYEE OPERATIONS
// ============================================================================

/**
 * Create new employee
 */
export const createEmployee = async (
  data: EmployeeCreate
): Promise<Employee> => {
  const response = await apiClient.post<Employee>(
    `${BASE_URL}/hrms/employees`,
    data
  );
  return response.data;
};

/**
 * Get paginated list of employees with filters
 */
export const getEmployees = async (
  filters?: EmployeeFilters
): Promise<PaginatedEmployeeResponse> => {
  const params = new URLSearchParams();
  
  if (filters?.page) params.append("page", filters.page.toString());
  if (filters?.page_size) params.append("page_size", filters.page_size.toString());
  if (filters?.search) params.append("search", filters.search);
  if (filters?.department_id) params.append("department_id", filters.department_id.toString());
  if (filters?.designation_id) params.append("designation_id", filters.designation_id.toString());
  if (filters?.employment_type) params.append("employment_type", filters.employment_type);
  if (filters?.employment_status) params.append("employment_status", filters.employment_status);
  if (filters?.reporting_manager_id) params.append("reporting_manager_id", filters.reporting_manager_id.toString());
  if (filters?.is_active !== undefined) params.append("is_active", filters.is_active.toString());
  
  const response = await apiClient.get<PaginatedEmployeeResponse>(
    `${BASE_URL}/hrms/employees?${params.toString()}`
  );
  return response.data;
};

/**
 * Get employee dashboard statistics
 */
export const getEmployeeStats = async (): Promise<EmployeeDashboardStats> => {
  const response = await apiClient.get<EmployeeDashboardStats>(
    `${BASE_URL}/hrms/employees/stats`
  );
  return response.data;
};

/**
 * Search employees by specific fields
 */
export const searchEmployees = async (
  params: EmployeeSearchParams
): Promise<Employee[]> => {
  const searchParams = new URLSearchParams();
  
  if (params.employee_code) searchParams.append("employee_code", params.employee_code);
  if (params.mobile) searchParams.append("mobile", params.mobile);
  if (params.email) searchParams.append("email", params.email);
  if (params.pan_number) searchParams.append("pan_number", params.pan_number);
  
  const response = await apiClient.get<Employee[]>(
    `${BASE_URL}/hrms/employees/search?${searchParams.toString()}`
  );
  return response.data;
};

/**
 * Get employee by ID
 */
export const getEmployeeById = async (employeeId: number): Promise<Employee> => {
  const response = await apiClient.get<Employee>(
    `${BASE_URL}/hrms/employees/${employeeId}`
  );
  return response.data;
};

/**
 * Get employee by employee code
 */
export const getEmployeeByCode = async (
  employeeCode: string
): Promise<Employee> => {
  const response = await apiClient.get<Employee>(
    `${BASE_URL}/hrms/employees/code/${employeeCode}`
  );
  return response.data;
};

/**
 * Update employee details
 */
export const updateEmployee = async (
  employeeId: number,
  data: EmployeeUpdate
): Promise<Employee> => {
  const response = await apiClient.put<Employee>(
    `${BASE_URL}/hrms/employees/${employeeId}`,
    data
  );
  return response.data;
};

/**
 * Delete employee (soft delete)
 */
export const deleteEmployee = async (employeeId: number): Promise<void> => {
  await apiClient.delete(`${BASE_URL}/hrms/employees/${employeeId}`);
};

/**
 * Get employee subordinates
 */
export const getEmployeeSubordinates = async (
  employeeId: number
): Promise<EmployeeCardView[]> => {
  const response = await apiClient.get<EmployeeCardView[]>(
    `${BASE_URL}/hrms/employees/${employeeId}/subordinates`
  );
  return response.data;
};

/**
 * Get organization chart tree
 */
export const getOrgChart = async (
  rootEmployeeId?: number
): Promise<OrgChartNode> => {
  const params = new URLSearchParams();
  if (rootEmployeeId) params.append("root_employee_id", rootEmployeeId.toString());
  
  const response = await apiClient.get<OrgChartNode>(
    `${BASE_URL}/hrms/employees/org-chart/tree?${params.toString()}`
  );
  return response.data;
};

/**
 * Get employees by department
 */
export const getEmployeesByDepartment = async (
  departmentId: number
): Promise<EmployeeListItem[]> => {
  const response = await apiClient.get<EmployeeListItem[]>(
    `${BASE_URL}/hrms/employees/department/${departmentId}/employees`
  );
  return response.data;
};

/**
 * Get employees by designation
 */
export const getEmployeesByDesignation = async (
  designationId: number
): Promise<EmployeeListItem[]> => {
  const response = await apiClient.get<EmployeeListItem[]>(
    `${BASE_URL}/hrms/employees/designation/${designationId}/employees`
  );
  return response.data;
};
