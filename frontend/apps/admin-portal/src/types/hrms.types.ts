/**
 * HRMS (Human Resource Management System) TypeScript Types
 * Employee Management, Organization Structure, Department, Designation, Reporting Hierarchy
 */

// ============================================================================
// ENUMS
// ============================================================================

export enum EmploymentType {
  PERMANENT = "permanent",
  CONTRACT = "contract",
  PROBATION = "probation",
  INTERN = "intern",
  CONSULTANT = "consultant",
}

export enum EmploymentStatus {
  ACTIVE = "active",
  INACTIVE = "inactive",
  RESIGNED = "resigned",
  TERMINATED = "terminated",
  ABSCONDED = "absconded",
  RETIRED = "retired",
}

export enum Gender {
  MALE = "male",
  FEMALE = "female",
  OTHER = "other",
}

export enum BloodGroup {
  A_POSITIVE = "A+",
  A_NEGATIVE = "A-",
  B_POSITIVE = "B+",
  B_NEGATIVE = "B-",
  O_POSITIVE = "O+",
  O_NEGATIVE = "O-",
  AB_POSITIVE = "AB+",
  AB_NEGATIVE = "AB-",
}

export enum MaritalStatus {
  SINGLE = "single",
  MARRIED = "married",
  DIVORCED = "divorced",
  WIDOWED = "widowed",
}

export enum DepartmentType {
  OPERATIONS = "operations",
  FINANCE = "finance",
  IT = "it",
  HR = "hr",
  MARKETING = "marketing",
  SALES = "sales",
  ADMIN = "admin",
  LEGAL = "legal",
  COMPLIANCE = "compliance",
  AUDIT = "audit",
  RISK = "risk",
  CREDIT = "credit",
  COLLECTIONS = "collections",
  CUSTOMER_SERVICE = "customer_service",
  OTHER = "other",
}

export enum ReportingType {
  DIRECT = "direct",
  DOTTED = "dotted",
  FUNCTIONAL = "functional",
}

// ============================================================================
// ORGANIZATION TYPES
// ============================================================================

export interface Organization {
  id: number;
  organization_code: string;
  organization_name: string;
  short_name?: string;
  legal_name?: string;
  pan_number?: string;
  tan_number?: string;
  gstin?: string;
  cin_number?: string;
  email?: string;
  phone?: string;
  website?: string;
  registered_address_line1?: string;
  registered_address_line2?: string;
  registered_city?: string;
  registered_state?: string;
  registered_pincode?: string;
  registered_country?: string;
  is_active: boolean;
  established_date?: string;
  created_at: string;
  updated_at?: string;
}

export interface OrganizationCreate {
  organization_name: string;
  short_name?: string;
  legal_name?: string;
  pan_number?: string;
  tan_number?: string;
  gstin?: string;
  cin_number?: string;
  email?: string;
  phone?: string;
  website?: string;
  registered_address_line1?: string;
  registered_address_line2?: string;
  registered_city?: string;
  registered_state?: string;
  registered_pincode?: string;
  established_date?: string;
  is_active?: boolean;
}

export interface OrganizationUpdate {
  organization_name?: string;
  short_name?: string;
  legal_name?: string;
  email?: string;
  phone?: string;
  website?: string;
  is_active?: boolean;
}

export interface OrganizationListItem {
  id: number;
  organization_code: string;
  organization_name: string;
  short_name?: string;
  is_active: boolean;
}

// ============================================================================
// DEPARTMENT TYPES
// ============================================================================

export interface Department {
  id: number;
  department_code: string;
  department_name: string;
  department_type: DepartmentType;
  description?: string;
  organization_id: number;
  parent_department_id?: number;
  hod_employee_id?: number;
  email?: string;
  phone?: string;
  extension?: string;
  location?: string;
  floor?: string;
  cost_center_code?: string;
  is_active: boolean;
  organization_name?: string;
  parent_department_name?: string;
  hod_name?: string;
  employee_count?: number;
  created_at: string;
  updated_at?: string;
}

export interface DepartmentCreate {
  department_name: string;
  department_type: DepartmentType;
  description?: string;
  organization_id: number;
  parent_department_id?: number;
  hod_employee_id?: number;
  email?: string;
  phone?: string;
  extension?: string;
  location?: string;
  floor?: string;
  cost_center_code?: string;
  is_active?: boolean;
}

export interface DepartmentUpdate {
  department_name?: string;
  department_type?: DepartmentType;
  description?: string;
  parent_department_id?: number;
  hod_employee_id?: number;
  email?: string;
  phone?: string;
  location?: string;
  is_active?: boolean;
}

export interface DepartmentListItem {
  id: number;
  department_code: string;
  department_name: string;
  department_type: DepartmentType;
  hod_name?: string;
  employee_count: number;
  is_active: boolean;
}

export interface DepartmentTreeNode {
  id: number;
  department_code: string;
  department_name: string;
  department_type: DepartmentType;
  parent_department_id?: number;
  hod_employee_id?: number;
  hod_name?: string;
  employee_count: number;
  children: DepartmentTreeNode[];
}

export interface DepartmentStats {
  total_departments: number;
  active_departments: number;
  employees_by_department: Array<{ department: string; count: number }>;
}

// ============================================================================
// DESIGNATION TYPES
// ============================================================================

export interface Designation {
  id: number;
  designation_code: string;
  designation_name: string;
  description?: string;
  level?: number;
  grade?: string;
  min_salary?: number;
  max_salary?: number;
  min_experience_years?: number;
  required_qualification?: string;
  is_active: boolean;
  employee_count?: number;
  created_at: string;
  updated_at?: string;
}

export interface DesignationCreate {
  designation_name: string;
  description?: string;
  level?: number;
  grade?: string;
  min_salary?: number;
  max_salary?: number;
  min_experience_years?: number;
  required_qualification?: string;
  is_active?: boolean;
}

export interface DesignationUpdate {
  designation_name?: string;
  description?: string;
  level?: number;
  grade?: string;
  min_salary?: number;
  max_salary?: number;
  is_active?: boolean;
}

export interface DesignationListItem {
  id: number;
  designation_code: string;
  designation_name: string;
  level?: number;
  grade?: string;
  employee_count: number;
  is_active: boolean;
}

export interface DesignationStats {
  total_designations: number;
  active_designations: number;
  employees_by_designation: Array<{ designation: string; count: number }>;
}

// ============================================================================
// EMPLOYEE TYPES
// ============================================================================

export interface Employee {
  id: number;
  employee_code: string;
  full_name: string;
  
  // Employment Information
  organization_id: number;
  department_id?: number;
  designation_id?: number;
  reporting_manager_id?: number;
  employment_type: EmploymentType;
  employment_status: EmploymentStatus;
  date_of_joining: string;
  date_of_confirmation?: string;
  work_location?: string;
  shift_type?: string;
  
  // Personal Information
  first_name: string;
  middle_name?: string;
  last_name: string;
  date_of_birth?: string;
  age?: number;
  gender?: Gender;
  blood_group?: BloodGroup;
  marital_status?: MaritalStatus;
  
  // Family Details
  father_name?: string;
  mother_name?: string;
  spouse_name?: string;
  number_of_children?: number;
  
  // Contact Information
  personal_email?: string;
  official_email?: string;
  mobile: string;
  alternate_mobile?: string;
  emergency_contact_name?: string;
  emergency_contact_number?: string;
  emergency_contact_relation?: string;
  
  // Current Address
  current_address_line1?: string;
  current_address_line2?: string;
  current_city?: string;
  current_state?: string;
  current_pincode?: string;
  
  // Permanent Address
  permanent_address_line1?: string;
  permanent_address_line2?: string;
  permanent_city?: string;
  permanent_state?: string;
  permanent_pincode?: string;
  is_permanent_same_as_current?: boolean;
  
  // Identity Documents
  pan_number?: string;
  aadhaar_number?: string;
  passport_number?: string;
  driving_license_number?: string;
  
  // Bank Details
  salary_bank_name?: string;
  salary_account_number?: string;
  salary_ifsc_code?: string;
  pf_number?: string;
  uan_number?: string;
  esi_number?: string;
  
  // Salary
  current_ctc?: number;
  basic_salary?: number;
  gross_salary?: number;
  net_salary?: number;
  
  // Education
  highest_qualification?: string;
  specialization?: string;
  university?: string;
  year_of_passing?: number;
  total_experience_years?: number;
  
  // Related names
  organization_name?: string;
  department_name?: string;
  designation_name?: string;
  reporting_manager_name?: string;
  
  // Status
  is_active: boolean;
  is_on_probation?: boolean;
  probation_end_date?: string;
  notice_period_days?: number;
  
  created_at: string;
  updated_at?: string;
}

export interface EmployeeCreate {
  // Employment Information
  organization_id: number;
  department_id?: number;
  designation_id?: number;
  reporting_manager_id?: number;
  employment_type: EmploymentType;
  employment_status?: EmploymentStatus;
  date_of_joining: string;
  date_of_confirmation?: string;
  work_location?: string;
  shift_type?: string;
  
  // Personal Information
  first_name: string;
  middle_name?: string;
  last_name: string;
  date_of_birth?: string;
  gender?: Gender;
  blood_group?: BloodGroup;
  marital_status?: MaritalStatus;
  
  // Family Details
  father_name?: string;
  mother_name?: string;
  spouse_name?: string;
  number_of_children?: number;
  
  // Contact Information
  personal_email?: string;
  official_email?: string;
  mobile: string;
  alternate_mobile?: string;
  emergency_contact_name?: string;
  emergency_contact_number?: string;
  emergency_contact_relation?: string;
  
  // Current Address
  current_address_line1?: string;
  current_address_line2?: string;
  current_city?: string;
  current_state?: string;
  current_pincode?: string;
  
  // Permanent Address
  permanent_address_line1?: string;
  permanent_address_line2?: string;
  permanent_city?: string;
  permanent_state?: string;
  permanent_pincode?: string;
  is_permanent_same_as_current?: boolean;
  
  // Identity Documents
  pan_number?: string;
  aadhaar_number?: string;
  passport_number?: string;
  driving_license_number?: string;
  
  // Bank Details
  salary_bank_name?: string;
  salary_account_number?: string;
  salary_ifsc_code?: string;
  pf_number?: string;
  uan_number?: string;
  esi_number?: string;
  
  // Salary
  current_ctc?: number;
  basic_salary?: number;
  
  // Education
  highest_qualification?: string;
  specialization?: string;
  university?: string;
  year_of_passing?: number;
  total_experience_years?: number;
  
  // Status
  is_active?: boolean;
  notice_period_days?: number;
}

export interface EmployeeUpdate {
  department_id?: number;
  designation_id?: number;
  reporting_manager_id?: number;
  employment_type?: EmploymentType;
  employment_status?: EmploymentStatus;
  date_of_confirmation?: string;
  mobile?: string;
  personal_email?: string;
  official_email?: string;
  current_address_line1?: string;
  current_city?: string;
  current_state?: string;
  current_ctc?: number;
  is_active?: boolean;
}

export interface EmployeeListItem {
  id: number;
  employee_code: string;
  full_name: string;
  official_email?: string;
  mobile: string;
  department_name?: string;
  designation_name?: string;
  employment_type: EmploymentType;
  employment_status: EmploymentStatus;
  date_of_joining: string;
  is_active: boolean;
}

export interface EmployeeCardView {
  id: number;
  employee_code: string;
  full_name: string;
  designation_name?: string;
  department_name?: string;
  photo_url?: string;
  official_email?: string;
  mobile: string;
  reporting_manager_name?: string;
}

// ============================================================================
// REPORTING HIERARCHY TYPES
// ============================================================================

export interface ReportingHierarchy {
  id: number;
  employee_id: number;
  manager_id: number;
  reporting_type: ReportingType;
  is_primary: boolean;
  effective_from: string;
  effective_to?: string;
  is_current: boolean;
  change_reason?: string;
  employee_name?: string;
  manager_name?: string;
  created_at: string;
}

export interface ReportingHierarchyCreate {
  employee_id: number;
  manager_id: number;
  reporting_type?: ReportingType;
  is_primary?: boolean;
  effective_from: string;
  effective_to?: string;
  is_current?: boolean;
  change_reason?: string;
}

export interface OrgChartNode {
  id: number;
  employee_code: string;
  full_name: string;
  designation_name?: string;
  department_name?: string;
  photo_url?: string;
  reporting_manager_id?: number;
  subordinates: OrgChartNode[];
}

// ============================================================================
// PAGINATION & FILTERS
// ============================================================================

export interface PaginatedEmployeeResponse {
  items: EmployeeListItem[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface PaginatedDepartmentResponse {
  items: DepartmentListItem[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface PaginatedDesignationResponse {
  items: DesignationListItem[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface EmployeeFilters {
  page?: number;
  page_size?: number;
  search?: string;
  department_id?: number;
  designation_id?: number;
  employment_type?: EmploymentType;
  employment_status?: EmploymentStatus;
  reporting_manager_id?: number;
  is_active?: boolean;
}

export interface DepartmentFilters {
  page?: number;
  page_size?: number;
  search?: string;
  organization_id?: number;
  parent_department_id?: number;
  is_active?: boolean;
}

export interface DesignationFilters {
  page?: number;
  page_size?: number;
  search?: string;
  level?: number;
  grade?: string;
  is_active?: boolean;
}

export interface EmployeeSearchParams {
  employee_code?: string;
  mobile?: string;
  email?: string;
  pan_number?: string;
}

// ============================================================================
// DASHBOARD & STATISTICS
// ============================================================================

export interface EmployeeDashboardStats {
  total_employees: number;
  active_employees: number;
  inactive_employees: number;
  on_probation: number;
  permanent_employees: number;
  contract_employees: number;
  new_joiners_this_month: number;
  resignations_this_month: number;
  by_department: Array<{ department: string; count: number }>;
  by_designation: Array<{ designation: string; count: number }>;
  by_employment_type: Record<string, number>;
  by_gender: Record<string, number>;
}

// ============================================================================
// LABEL/DISPLAY HELPERS
// ============================================================================

export const EmploymentTypeLabels: Record<EmploymentType, string> = {
  [EmploymentType.PERMANENT]: "Permanent",
  [EmploymentType.CONTRACT]: "Contract",
  [EmploymentType.PROBATION]: "Probation",
  [EmploymentType.INTERN]: "Intern",
  [EmploymentType.CONSULTANT]: "Consultant",
};

export const EmploymentStatusLabels: Record<EmploymentStatus, string> = {
  [EmploymentStatus.ACTIVE]: "Active",
  [EmploymentStatus.INACTIVE]: "Inactive",
  [EmploymentStatus.RESIGNED]: "Resigned",
  [EmploymentStatus.TERMINATED]: "Terminated",
  [EmploymentStatus.ABSCONDED]: "Absconded",
  [EmploymentStatus.RETIRED]: "Retired",
};

export const DepartmentTypeLabels: Record<DepartmentType, string> = {
  [DepartmentType.OPERATIONS]: "Operations",
  [DepartmentType.FINANCE]: "Finance",
  [DepartmentType.IT]: "IT",
  [DepartmentType.HR]: "HR",
  [DepartmentType.MARKETING]: "Marketing",
  [DepartmentType.SALES]: "Sales",
  [DepartmentType.ADMIN]: "Admin",
  [DepartmentType.LEGAL]: "Legal",
  [DepartmentType.COMPLIANCE]: "Compliance",
  [DepartmentType.AUDIT]: "Audit",
  [DepartmentType.RISK]: "Risk",
  [DepartmentType.CREDIT]: "Credit",
  [DepartmentType.COLLECTIONS]: "Collections",
  [DepartmentType.CUSTOMER_SERVICE]: "Customer Service",
  [DepartmentType.OTHER]: "Other",
};

export const GenderLabels: Record<Gender, string> = {
  [Gender.MALE]: "Male",
  [Gender.FEMALE]: "Female",
  [Gender.OTHER]: "Other",
};

export const MaritalStatusLabels: Record<MaritalStatus, string> = {
  [MaritalStatus.SINGLE]: "Single",
  [MaritalStatus.MARRIED]: "Married",
  [MaritalStatus.DIVORCED]: "Divorced",
  [MaritalStatus.WIDOWED]: "Widowed",
};
