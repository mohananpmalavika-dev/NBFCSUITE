
import axios from 'axios';

// Service URL Configuration
// Prioritizes: API Gateway (if available) → Individual service URLs → Fallback defaults
const getServiceURL = (serviceName: string): string => {
  const apiGateway = process.env.NEXT_PUBLIC_API_GATEWAY_URL;
  const isDummyApiGateway = apiGateway === 'https://api-gateway-yourapp.onrender.com' || apiGateway === 'http://api-gateway-yourapp.onrender.com';

  if (apiGateway && !isDummyApiGateway) {
    // Use API Gateway with path-based routing
    // Client paths already include the service prefix, e.g. /auth/login
    return apiGateway;
  }
  
  // Fall back to individual service URLs
  const serviceUrls: Record<string, string> = {
    auth: process.env.NEXT_PUBLIC_AUTH_API_URL || 'http://localhost:8001',
    los: process.env.NEXT_PUBLIC_LOS_API_URL || 'http://localhost:8002',
    lms: process.env.NEXT_PUBLIC_LMS_API_URL || 'http://localhost:8003',
    collections: process.env.NEXT_PUBLIC_COLLECTIONS_API_URL || 'http://localhost:8004',
    customer: process.env.NEXT_PUBLIC_CUSTOMER_API_URL || 'http://localhost:8005',
    findna: process.env.NEXT_PUBLIC_FINDNA_API_URL || 'http://localhost:8006',
    deposits: process.env.NEXT_PUBLIC_DEPOSITS_API_URL || 'http://localhost:8007',
    accounting: process.env.NEXT_PUBLIC_ACCOUNTING_API_URL || 'http://localhost:8008',
    crm: process.env.NEXT_PUBLIC_CRM_API_URL || 'http://localhost:8009',
    document: process.env.NEXT_PUBLIC_DOCUMENT_API_URL || 'http://localhost:8010',
    compliance: process.env.NEXT_PUBLIC_COMPLIANCE_API_URL || 'http://localhost:8011',
    hrms: process.env.NEXT_PUBLIC_HRMS_API_URL || 'http://localhost:8012',
    gold: process.env.NEXT_PUBLIC_GOLD_API_URL || 'http://localhost:8013',
    treasury: process.env.NEXT_PUBLIC_TREASURY_API_URL || 'http://localhost:8014',
    wealth: process.env.NEXT_PUBLIC_WEALTH_API_URL || 'http://localhost:8015',
    insurance: process.env.NEXT_PUBLIC_INSURANCE_API_URL || 'http://localhost:8016',
    procurement: process.env.NEXT_PUBLIC_PROCUREMENT_API_URL || 'http://localhost:8017',
    platform: process.env.NEXT_PUBLIC_PLATFORM_API_URL || 'http://localhost:8018',
    notifications: process.env.NEXT_PUBLIC_NOTIFICATIONS_API_URL || 'http://localhost:8019',
  };
  
  return serviceUrls[serviceName] || (process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000');
};

// Create axios instances for each service
const authAxiosInstance = axios.create({
  baseURL: getServiceURL('auth'),
});

const hrmsAxiosInstance = axios.create({
  baseURL: getServiceURL('hrms'),
});

// Legacy aliases for backward compatibility
const axiosInstance = authAxiosInstance;

type JsonObject = Record<string, unknown>;

export interface LoanApplicationPayload {
  customer_id: string;
  branch_id?: string;
  product_code: string;
  applied_amount: number;
  tenure_months: number;
}

export interface PaymentPayload {
  amount: number;
  payment_mode: string;
  reference: string;
}

export interface DepositTransactionPayload {
  transaction_type: 'credit' | 'debit' | 'interest' | 'fee';
  amount: number;
  description: string;
  reference?: string;
  transaction_date?: string;
  metadata?: JsonObject;
}

export interface DocumentPayload {
  subject_type: string;
  subject_id: string;
  document_category?: string;
  document_type: string;
  document_name: string;
  document_url: string;
  expiry_date?: string | null;
  metadata?: JsonObject;
}

export interface OfficePayload {
  name: string;
  code: string;
  address?: string;
  city?: string;
  state?: string;
  country?: string;
  contact_email?: string;
  contact_phone?: string;
  is_active?: boolean;
}

export interface ZonePayload extends OfficePayload {
  organization_id: string;
}

export interface RegionPayload extends OfficePayload {
  zone_id: string;
}

export interface AreaPayload extends OfficePayload {
  region_id: string;
}

export interface BranchPayload extends OfficePayload {
  area_id: string;
  branch_type?: string;
  postal_code?: string;
}

export interface EomBrandPayload {
  tenant_id: string;
  enterprise_id?: string;
  brand_code: string;
  brand_name: string;
  legal_name?: string;
  short_name?: string;
  email?: string;
  phone?: string;
}

export interface EomEnterprisePayload {
  tenant_id: string;
  enterprise_code: string;
  enterprise_name: string;
  logo_url?: string;
  vision?: string;
  mission?: string;
  corporate_address?: string;
  corporate_office?: string;
  country?: string;
  currency?: string;
  timezone?: string;
  financial_year_start?: string;
  financial_year_end?: string;
}

export interface EomLegalEntityPayload {
  tenant_id: string;
  brand_id: string;
  entity_code: string;
  entity_name: string;
  entity_type?: string;
  registered_address?: string;
  state?: string;
  country?: string;
}

export interface EomBusinessUnitPayload {
  tenant_id: string;
  legal_entity_id: string;
  business_unit_code: string;
  business_unit_name: string;
  head?: string;
}

export interface EomDivisionPayload {
  tenant_id: string;
  business_unit_id: string;
  division_code: string;
  division_name: string;
  division_head?: string;
}

export interface EomZonePayload {
  tenant_id: string;
  business_unit_id: string;
  division_id?: string;
  zone_code: string;
  zone_name: string;
  zone_head?: string;
}

export interface EomRegionPayload {
  tenant_id: string;
  zone_id: string;
  region_code: string;
  region_name: string;
  regional_manager?: string;
  office_address?: string;
}

export interface EomAreaPayload {
  tenant_id: string;
  region_id: string;
  area_code: string;
  area_name: string;
  area_manager?: string;
  office_address?: string;
}

export interface EomClusterPayload {
  tenant_id: string;
  area_id: string;
  cluster_code: string;
  cluster_name: string;
  cluster_manager?: string;
}

export interface EomBranchPayload {
  tenant_id: string;
  area_id: string;
  branch_name: string;
  branch_code?: string;
  short_name?: string;
  zone_id?: string;
  region_id?: string;
  cluster_id?: string;
}

export interface EomDepartmentPayload {
  tenant_id: string;
  branch_id: string;
  department_code: string;
  department_name: string;
}

export interface EomTeamPayload {
  tenant_id: string;
  department_id: string;
  team_code: string;
  team_name: string;
  team_lead_employee_id?: string;
}

export interface EomPositionPayload {
  tenant_id: string;
  position_code: string;
  position_title: string;
  department_id?: string;
  team_id?: string;
  reports_to_position_id?: string;
  grade?: string;
  employment_type?: string;
}

export interface EomVendorPayload {
  tenant_id: string;
  vendor_code: string;
  vendor_name: string;
  vendor_type?: string;
  contact_person?: string;
  email?: string;
  phone?: string;
  gst?: string;
  pan?: string;
}

export interface EomAssetPayload {
  tenant_id: string;
  asset_code: string;
  asset_name: string;
  asset_type?: string;
  branch_id?: string;
  department_id?: string;
  assigned_employee_id?: string;
  vendor_id?: string;
  purchase_value?: number;
}

export interface HrmsEmployeePayload {
  tenant_id: string;
  employee_number: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  designation: string;
  department: string;
  department_id?: string;
  designation_id?: string;
  grade_id?: string;
  position_id?: string;
  manager_employee_id?: string;
  official_email?: string;
  branch_id?: string;
  user_id?: string;
  employment_type?: string;
  joining_date?: string;
}

export interface HrmsEmployeeUpdatePayload {
  first_name?: string;
  last_name?: string;
  phone?: string;
  designation?: string;
  department?: string;
  department_id?: string;
  designation_id?: string;
  grade_id?: string;
  position_id?: string;
  manager_employee_id?: string;
  official_email?: string;
  branch_id?: string;
  user_id?: string;
  employment_type?: string;
  status?: string;
}

export interface HrmsDepartmentPayload {
  tenant_id: string;
  department_code: string;
  department_name: string;
  parent_department_id?: string;
  department_head_employee_id?: string;
  cost_center_code?: string;
  profit_center_code?: string;
  budget_owner_employee_id?: string;
  annual_budget?: number;
}

export interface OrganizationUnitPayload {
  tenant_id?: string;
  parent_id?: string;
  unit_code: string;
  unit_name: string;
  unit_type: string;
  display_order?: number;
  status?: string;
  effective_from?: string;
  effective_to?: string;
  manager_position_id?: string;
  cost_center_id?: string;
  profit_center_id?: string;
  address_id?: string;
}

export interface HrmsDepartmentBudgetResponse {
  department_id: string;
  department_name: string;
  tenant_id: string;
  annual_budget: number;
  cost_center_code?: string;
  profit_center_code?: string;
  budget_owner_employee_id?: string;
  department_head_employee_id?: string;
  department_head_name?: string;
  total_positions: number;
  open_positions: number;
  occupied_positions: number;
  total_employees: number;
}

export interface HrmsDepartmentAnalyticsResponse extends HrmsDepartmentBudgetResponse {
  active_employees: number;
  status: string;
}

export interface HrmsGradePayload {
  tenant_id: string;
  grade_code: string;
  grade_name: string;
  salary_band_min?: number;
  salary_band_max?: number;
  leave_entitlement_days?: number;
  benefits?: Record<string, unknown>;
  approval_limit?: number;
  travel_class?: string;
}

export interface HrmsDesignationPayload {
  tenant_id: string;
  designation_code: string;
  designation_name: string;
  grade_id?: string;
  salary_band_min?: number;
  salary_band_max?: number;
  approval_limit?: number;
  reporting_level?: number;
}

export interface HrmsPositionPayload {
  tenant_id: string;
  position_code: string;
  position_title: string;
  department_id?: string;
  designation_id?: string;
  grade_id?: string;
  branch_id?: string;
  reports_to_position_id?: string;
  approval_limit?: number;
}

export interface PayrollRunPayload {
  tenant_id: string;
  run_name?: string;
  period_start: string;
  period_end: string;
}

export interface PayrollSlipPayload {
  tenant_id: string;
  employee_id: string;
  basic_pay: number;
  allowances?: Record<string, number>;
  deductions?: Record<string, number>;
  tax_amount: number;
}

export interface GlAccountPayload {
  tenant_id: string;
  account_code: string;
  account_name: string;
  account_type: string;
  parent_account_id?: string;
  category?: string;
  currency?: string;
  branch_id?: string;
  branch_specific?: string;
  posting_allowed?: string;
  status?: string;
  opening_balance?: number;
  financial_year?: string;
}

export interface CoaSeedPayload {
  tenant_id: string;
  currency?: string;
  financial_year?: string;
}

export interface PostingRuleLinePayload {
  account_code: string;
  direction: 'debit' | 'credit';
  description?: string;
}

export interface PostingRulePayload {
  tenant_id: string;
  source_module: string;
  source_event: string;
  debit_account_code?: string;
  credit_account_code?: string;
  description?: string;
  lines?: PostingRuleLinePayload[];
}

export type PaymentMode = 'cash' | 'cheque' | 'upi' | 'rtgs' | 'neft' | 'imps';

export interface AccountingPostingLine {
  gl_account_id?: string;
  account_code?: string;
  debit: number;
  credit: number;
  description?: string;
  branch_id?: string;
  currency?: string;
  cost_center?: string;
  profit_center?: string;
}

export interface PostingEnginePayload {
  tenant_id: string;
  source_module: string;
  source_event: string;
  source_reference: string;
  description?: string;
  idempotency_key?: string;
  branch_id?: string;
  business_date?: string;
  financial_year?: string;
  currency?: string;
  metadata?: JsonObject;
  lines: AccountingPostingLine[];
}

export interface VoucherPayload {
  tenant_id: string;
  voucher_type: string;
  voucher_date?: string;
  description: string;
  reference?: string;
  branch_id?: string;
  currency?: string;
  payment_mode?: PaymentMode;
  payment_reference?: string;
  payment_details?: JsonObject;
  created_by?: string;
  metadata?: JsonObject;
  lines: AccountingPostingLine[];
}

export type PaymentVoucherCategory = 'vendor_payments' | 'salary' | 'rent' | 'electricity' | 'tax' | 'insurance';

export interface PaymentVoucherPayload {
  tenant_id: string;
  payment_category: PaymentVoucherCategory;
  amount: number;
  payee_name: string;
  voucher_date?: string;
  description?: string;
  reference?: string;
  branch_id?: string;
  currency?: string;
  payment_mode: PaymentMode;
  payment_reference?: string;
  payment_details?: JsonObject;
  created_by?: string;
  debit_account_id?: string;
  debit_account_code?: string;
  credit_account_id?: string;
  credit_account_code?: string;
  cost_center?: string;
  profit_center?: string;
  metadata?: JsonObject;
}

export type ReceiptVoucherCategory = 'customer_payments';

export interface ReceiptVoucherPayload {
  tenant_id: string;
  receipt_category: ReceiptVoucherCategory;
  amount: number;
  payer_name: string;
  customer_id?: string;
  voucher_date?: string;
  description?: string;
  reference?: string;
  branch_id?: string;
  currency?: string;
  payment_mode: PaymentMode;
  payment_reference?: string;
  payment_details?: JsonObject;
  created_by?: string;
  debit_account_id?: string;
  debit_account_code?: string;
  credit_account_id?: string;
  credit_account_code?: string;
  cost_center?: string;
  profit_center?: string;
  metadata?: JsonObject;
}

export type ContraTransferType = 'cash_to_bank' | 'bank_to_cash' | 'vault_to_branch' | 'branch_to_treasury';

export interface ContraVoucherPayload {
  tenant_id: string;
  transfer_type: ContraTransferType;
  amount: number;
  voucher_date?: string;
  description?: string;
  reference?: string;
  transfer_reference?: string;
  branch_id?: string;
  currency?: string;
  transfer_details?: JsonObject;
  created_by?: string;
  debit_account_id?: string;
  debit_account_code?: string;
  credit_account_id?: string;
  credit_account_code?: string;
  source_location?: string;
  destination_location?: string;
  cost_center?: string;
  profit_center?: string;
  metadata?: JsonObject;
}

export type CreditNoteType = 'interest_reversal' | 'refund' | 'adjustment' | 'discount';

export interface CreditNotePayload {
  tenant_id: string;
  credit_note_type: CreditNoteType;
  amount: number;
  customer_name: string;
  customer_id?: string;
  voucher_date?: string;
  description?: string;
  reference?: string;
  credit_note_reference?: string;
  branch_id?: string;
  currency?: string;
  credit_note_details?: JsonObject;
  created_by?: string;
  debit_account_id?: string;
  debit_account_code?: string;
  credit_account_id?: string;
  credit_account_code?: string;
  cost_center?: string;
  profit_center?: string;
  metadata?: JsonObject;
}

export type DebitNoteType = 'penalty' | 'charges' | 'recovery' | 'tax_adjustment';

export interface DebitNotePayload {
  tenant_id: string;
  debit_note_type: DebitNoteType;
  amount: number;
  customer_name: string;
  customer_id?: string;
  voucher_date?: string;
  description?: string;
  reference?: string;
  debit_note_reference?: string;
  branch_id?: string;
  currency?: string;
  debit_note_details?: JsonObject;
  created_by?: string;
  debit_account_id?: string;
  debit_account_code?: string;
  credit_account_id?: string;
  credit_account_code?: string;
  cost_center?: string;
  profit_center?: string;
  metadata?: JsonObject;
}

export interface DayEndClosePayload {
  tenant_id: string;
  business_date: string;
  branch_id?: string;
  closed_by?: string;
}

export interface AccountingQuickActionPayload {
  tenant_id: string;
  action_type: string;
  amount: number;
  description?: string;
  party_name?: string;
  source_reference?: string;
  branch_id?: string;
  business_date?: string;
  currency?: string;
  performed_by?: string;
  metadata?: JsonObject;
}

export const apiClient = {
  setToken: (token: string) => {
    axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    hrmsAxiosInstance.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  },
  setScope: (scope: {
    tenant_id?: string | null;
    user_id?: string | null;
    organization_id?: string | null;
    zone_id?: string | null;
    region_id?: string | null;
    area_id?: string | null;
    branch_id?: string | null;
  }) => {
    const headers = axiosInstance.defaults.headers.common;
    const hrmsHeaders = hrmsAxiosInstance.defaults.headers.common;
    delete headers['X-Tenant-Id'];
    delete headers['X-User-Id'];
    delete headers['X-Scope-Organization-Id'];
    delete headers['X-Scope-Zone-Id'];
    delete headers['X-Scope-Region-Id'];
    delete headers['X-Scope-Area-Id'];
    delete headers['X-Scope-Branch-Id'];
    delete hrmsHeaders['X-Tenant-Id'];
    delete hrmsHeaders['X-User-Id'];
    delete hrmsHeaders['X-Scope-Organization-Id'];
    delete hrmsHeaders['X-Scope-Zone-Id'];
    delete hrmsHeaders['X-Scope-Region-Id'];
    delete hrmsHeaders['X-Scope-Area-Id'];
    delete hrmsHeaders['X-Scope-Branch-Id'];
    if (scope.tenant_id) {
      headers['X-Tenant-Id'] = scope.tenant_id;
      hrmsHeaders['X-Tenant-Id'] = scope.tenant_id;
    }
    if (scope.user_id) {
      headers['X-User-Id'] = scope.user_id;
      hrmsHeaders['X-User-Id'] = scope.user_id;
    }
    if (scope.organization_id) {
      headers['X-Scope-Organization-Id'] = scope.organization_id;
      hrmsHeaders['X-Scope-Organization-Id'] = scope.organization_id;
    }
    if (scope.zone_id) {
      headers['X-Scope-Zone-Id'] = scope.zone_id;
      hrmsHeaders['X-Scope-Zone-Id'] = scope.zone_id;
    }
    if (scope.region_id) {
      headers['X-Scope-Region-Id'] = scope.region_id;
      hrmsHeaders['X-Scope-Region-Id'] = scope.region_id;
    }
    if (scope.area_id) {
      headers['X-Scope-Area-Id'] = scope.area_id;
      hrmsHeaders['X-Scope-Area-Id'] = scope.area_id;
    }
    if (scope.branch_id) {
      headers['X-Scope-Branch-Id'] = scope.branch_id;
      hrmsHeaders['X-Scope-Branch-Id'] = scope.branch_id;
    }
  },
  clearToken: () => {
    delete axiosInstance.defaults.headers.common['Authorization'];
    delete hrmsAxiosInstance.defaults.headers.common['Authorization'];
    apiClient.setScope({});
  },

  // Auth Service
  login: (username: string, password: string) =>
    axiosInstance.post(`/auth/login`, { username, password }),
  refreshToken: (refreshToken: string) =>
    axiosInstance.post(`/auth/refresh`, { refresh_token: refreshToken }),
  getMe: () =>
    axiosInstance.get(`/auth/users/me`),
  getUser: (userId: string) =>
    axiosInstance.get(`/auth/users/${userId}`),
  listUsers: () =>
    axiosInstance.get(`/auth/users`),
  validateToken: () =>
    axiosInstance.get(`/auth/validate`),
  createRole: (data: { name: string; description?: string; permissions?: string[] }) =>
    axiosInstance.post(`/auth/roles`, data),
  listRoles: () =>
    axiosInstance.get(`/auth/roles`),
  createPermission: (data: { name: string; description?: string }) =>
    axiosInstance.post(`/auth/permissions`, data),
  listPermissions: () =>
    axiosInstance.get(`/auth/permissions`),
  createApiKey: (data: { name?: string; description?: string; tenant_id?: string; expires_at?: string }) =>
    axiosInstance.post(`/auth/keys`, data),
  listApiKeys: () =>
    axiosInstance.get(`/auth/keys`),
  revokeApiKey: (keyId: string) =>
    axiosInstance.delete(`/auth/keys/${keyId}`),
  createOAuthClient: (data: { name: string; redirect_uris?: string[]; scopes?: string[]; client_id?: string; client_secret?: string }) =>
    axiosInstance.post(`/auth/oauth/clients`, data),
  listOAuthClients: () =>
    axiosInstance.get(`/auth/oauth/clients`),
  createExternalProvider: (data: { provider_type: string; display_name: string; configuration?: Record<string, unknown> }) =>
    axiosInstance.post(`/auth/external-providers`, data),
  listExternalProviders: () =>
    axiosInstance.get(`/auth/external-providers`),
  createApprovalRule: (data: { tenant_id?: string; action: string; required_roles?: string[]; threshold?: string; enabled?: boolean }) =>
    axiosInstance.post(`/auth/approval-rules`, data),
  listApprovalRules: () =>
    axiosInstance.get(`/auth/approval-rules`),
  createGroup: (data: { name: string; description?: string }) =>
    axiosInstance.post(`/auth/groups`, data),
  listGroups: () =>
    axiosInstance.get(`/auth/groups`),
  addUserToGroup: (groupId: string, userId: string) =>
    axiosInstance.post(`/auth/groups/${groupId}/users/${userId}`),
  removeUserFromGroup: (groupId: string, userId: string) =>
    axiosInstance.delete(`/auth/groups/${groupId}/users/${userId}`),
  listUserGroups: (userId: string) =>
    axiosInstance.get(`/auth/users/${userId}/groups`),
  listLoginHistory: (userId: string) =>
    axiosInstance.get(`/auth/users/${userId}/login-history`),
  listAuditLogs: () =>
    axiosInstance.get(`/auth/audit-logs`),
  requestOtp: (data: { user_id: string; purpose: string }) =>
    axiosInstance.post(`/auth/otp/request`, data),
  verifyOtp: (data: { user_id: string; code: string; purpose: string }) =>
    axiosInstance.post(`/auth/otp/verify`, data),
  createAttributePolicy: (data: { resource_type: string; action: string; conditions?: Record<string, unknown>; effect?: string }) =>
    axiosInstance.post(`/auth/policies`, data),
  listAttributePolicies: () =>
    axiosInstance.get(`/auth/policies`),

  // Customer Service
  getCustomer: (customerId: string) =>
    axiosInstance.get(`/customers/${customerId}`),
  getCustomers: (params?: { branch_id?: string; q?: string; kyc_status?: string; skip?: number; limit?: number }) =>
    axiosInstance.get(`/customers`, { params }),
  updateCustomer: (customerId: string, data: JsonObject) =>
    axiosInstance.put(`/customers/${customerId}`, data),
  getFinancialProfile: (customerId: string) =>
    axiosInstance.get(`/customers/${customerId}/financial-profile`),
  updateFinancialProfile: (customerId: string, data: JsonObject) =>
    axiosInstance.post(`/customers/${customerId}/financial-profile`, data),
  updateRiskProfile: (customerId: string, data: JsonObject) =>
    axiosInstance.put(`/customers/${customerId}/risk-profile`, data),
  createOrganization: (data: OfficePayload) =>
    axiosInstance.post(`/organizations`, data),
  getOrganizations: () =>
    axiosInstance.get(`/organizations`),
  getOrganizationHierarchy: () =>
    axiosInstance.get(`/organizations/hierarchy`),
  createZone: (data: ZonePayload) =>
    axiosInstance.post(`/zones`, data),
  getZones: (organizationId?: string) =>
    axiosInstance.get(`/zones`, { params: organizationId ? { organization_id: organizationId } : undefined }),
  createRegion: (data: RegionPayload) =>
    axiosInstance.post(`/regions`, data),
  getRegions: (zoneId?: string) =>
    axiosInstance.get(`/regions`, { params: zoneId ? { zone_id: zoneId } : undefined }),
  createArea: (data: AreaPayload) =>
    axiosInstance.post(`/areas`, data),
  getAreas: (regionId?: string) =>
    axiosInstance.get(`/areas`, { params: regionId ? { region_id: regionId } : undefined }),
  createBranch: (data: BranchPayload) =>
    axiosInstance.post(`/branches`, data),
  getBranches: (areaId?: string) =>
    axiosInstance.get(`/branches`, { params: areaId ? { area_id: areaId } : undefined }),
  getBranchScope: (branchId: string) =>
    axiosInstance.get(`/branches/${branchId}/scope`),
  getEomSummary: () => axiosInstance.get(`/eom/summary`),
  getEomHierarchyTree: () => axiosInstance.get(`/eom/hierarchy/tree`),
  getEomEnterprises: () => axiosInstance.get(`/eom/enterprises`),
  createEomEnterprise: (data: EomEnterprisePayload) => axiosInstance.post(`/eom/enterprises`, data),
  getEomBrands: () => axiosInstance.get(`/eom/brands`),
  createEomBrand: (data: EomBrandPayload) => axiosInstance.post(`/eom/brands`, data),
  getEomLegalEntities: () => axiosInstance.get(`/eom/legal-entities`),
  createEomLegalEntity: (data: EomLegalEntityPayload) => axiosInstance.post(`/eom/legal-entities`, data),
  getEomBusinessUnits: () => axiosInstance.get(`/eom/business-units`),
  createEomBusinessUnit: (data: EomBusinessUnitPayload) => axiosInstance.post(`/eom/business-units`, data),
  getEomDivisions: () => axiosInstance.get(`/eom/divisions`),
  createEomDivision: (data: EomDivisionPayload) => axiosInstance.post(`/eom/divisions`, data),
  getEomZones: () => axiosInstance.get(`/eom/zones`),
  createEomZone: (data: EomZonePayload) => axiosInstance.post(`/eom/zones`, data),
  getEomRegions: () => axiosInstance.get(`/eom/regions`),
  createEomRegion: (data: EomRegionPayload) => axiosInstance.post(`/eom/regions`, data),
  getEomAreas: () => axiosInstance.get(`/eom/areas`),
  createEomArea: (data: EomAreaPayload) => axiosInstance.post(`/eom/areas`, data),
  getEomClusters: () => axiosInstance.get(`/eom/clusters`),
  createEomCluster: (data: EomClusterPayload) => axiosInstance.post(`/eom/clusters`, data),
  getEomBranches: () => axiosInstance.get(`/eom/branches`),
  createEomBranch: (data: EomBranchPayload) => axiosInstance.post(`/eom/branches`, data),
  getEomDepartments: () => axiosInstance.get(`/eom/departments`),
  createEomDepartment: (data: EomDepartmentPayload) => axiosInstance.post(`/eom/departments`, data),
  getEomTeams: () => axiosInstance.get(`/eom/teams`),
  createEomTeam: (data: EomTeamPayload) => axiosInstance.post(`/eom/teams`, data),
  getEomPositions: () => axiosInstance.get(`/eom/positions`),
  createEomPosition: (data: EomPositionPayload) => axiosInstance.post(`/eom/positions`, data),
  getEomVendors: () => axiosInstance.get(`/eom/vendors`),
  createEomVendor: (data: EomVendorPayload) => axiosInstance.post(`/eom/vendors`, data),
  getEomAssets: () => axiosInstance.get(`/eom/assets`),
  createEomAsset: (data: EomAssetPayload) => axiosInstance.post(`/eom/assets`, data),
  getCustomerBranchMapping: (customerId: string) =>
    axiosInstance.get(`/eom/customer-branch-mapping/${customerId}`),
  assignCustomerBranch: (
    customerId: string,
    branchId: string,
    transferredBy?: string,
    tenantId: string = 'default',
  ) =>
    axiosInstance.post(`/eom/customer-branch-mapping`, {
      tenant_id: tenantId,
      customer_id: customerId,
      branch_id: branchId,
      transferred_by: transferredBy,
    }),
  getCustomerDocuments: (customerId: string) =>
    axiosInstance.get(`/documents`, { params: { subject_type: 'customer', subject_id: customerId } }),
  getExpiringDocuments: (customerId: string, days = 30) =>
    axiosInstance.get(`/documents/expiring`, { params: { subject_type: 'customer', subject_id: customerId, days } }),
  createDocument: (data: DocumentPayload) =>
    axiosInstance.post(`/documents`, data),
  uploadDocumentFile: (data: FormData) =>
    axiosInstance.post(`/documents/upload`, data),
  expireDocument: (documentId: string) =>
    axiosInstance.put(`/documents/${documentId}/expire`),

  // HRMS Service
  getHrmsDepartments: (params?: { tenant_id?: string; status?: string }) =>
    hrmsAxiosInstance.get(`/departments`, { params }),
  getOrganizationUnits: (params?: { tenant_id?: string }) =>
    hrmsAxiosInstance.get(`/organization/tree`, { params }),
  createOrganizationUnit: (data: OrganizationUnitPayload) =>
    hrmsAxiosInstance.post(`/organization/unit`, data),
  updateOrganizationUnit: (unitId: string, data: Partial<OrganizationUnitPayload>) =>
    hrmsAxiosInstance.put(`/organization/unit/${unitId}`, data),
  deleteOrganizationUnit: (unitId: string) =>
    hrmsAxiosInstance.delete(`/organization/unit/${unitId}`),
  getOrganizationAnalytics: (params?: { tenant_id?: string }) =>
    hrmsAxiosInstance.get(`/organization/analytics`, { params }),
  createHrmsDepartment: (data: HrmsDepartmentPayload) =>
    hrmsAxiosInstance.post(`/departments`, data),
  updateHrmsDepartment: (departmentId: string, data: Partial<Omit<HrmsDepartmentPayload, 'tenant_id' | 'department_code'>>) =>
    hrmsAxiosInstance.put(`/departments/${departmentId}`, data),
  getHrmsDepartmentTree: (params?: { tenant_id?: string; status?: string }) =>
    hrmsAxiosInstance.get(`/departments/tree`, { params }),
  getHrmsDepartment: (departmentId: string) =>
    hrmsAxiosInstance.get(`/departments/${departmentId}`),
  getHrmsDepartmentEmployees: (departmentId: string, params?: { status?: string; skip?: number; limit?: number }) =>
    hrmsAxiosInstance.get(`/departments/${departmentId}/employees`, { params }),
  getHrmsDepartmentPositions: (departmentId: string, params?: { status?: string }) =>
    hrmsAxiosInstance.get(`/departments/${departmentId}/positions`, { params }),
  getHrmsDepartmentBudget: (departmentId: string) =>
    hrmsAxiosInstance.get(`/departments/${departmentId}/budget`),
  getHrmsDepartmentAnalytics: (departmentId: string) =>
    hrmsAxiosInstance.get(`/departments/${departmentId}/analytics`),
  getHrmsGrades: (params?: { tenant_id?: string; status?: string }) =>
    hrmsAxiosInstance.get(`/grades`, { params }),
  createHrmsGrade: (data: HrmsGradePayload) =>
    hrmsAxiosInstance.post(`/grades`, data),
  updateHrmsGrade: (gradeId: string, data: Partial<Omit<HrmsGradePayload, 'tenant_id' | 'grade_code'>>) =>
    hrmsAxiosInstance.put(`/grades/${gradeId}`, data),
  getHrmsDesignations: (params?: { tenant_id?: string; status?: string }) =>
    hrmsAxiosInstance.get(`/designations`, { params }),
  createHrmsDesignation: (data: HrmsDesignationPayload) =>
    hrmsAxiosInstance.post(`/designations`, data),
  updateHrmsDesignation: (designationId: string, data: Partial<Omit<HrmsDesignationPayload, 'tenant_id' | 'designation_code'>>) =>
    hrmsAxiosInstance.put(`/designations/${designationId}`, data),
  getHrmsPositions: (params?: { tenant_id?: string; branch_id?: string; department_id?: string; status?: string }) =>
    hrmsAxiosInstance.get(`/positions`, { params }),
  createHrmsPosition: (data: HrmsPositionPayload) =>
    hrmsAxiosInstance.post(`/positions`, data),
  updateHrmsPosition: (positionId: string, data: Partial<Omit<HrmsPositionPayload, 'tenant_id' | 'position_code'>> & { occupied_by_employee_id?: string; status?: string }) =>
    hrmsAxiosInstance.put(`/positions/${positionId}`, data),
  vacateHrmsPosition: (positionId: string) =>
    hrmsAxiosInstance.post(`/positions/${positionId}/vacate`),
  getEmployees: (params?: { tenant_id?: string; branch_id?: string; department?: string; status?: string; skip?: number; limit?: number }) =>
    hrmsAxiosInstance.get(`/employees`, { params }),
  createEmployee: (data: HrmsEmployeePayload) =>
    hrmsAxiosInstance.post(`/employees`, data),
  updateEmployee: (employeeId: string, data: HrmsEmployeeUpdatePayload) =>
    hrmsAxiosInstance.put(`/employees/${employeeId}`, data),
  assignEmployeeBranch: (employeeId: string, branchId: string) =>
    hrmsAxiosInstance.post(`/employees/${employeeId}/assign-branch`, null, { params: { branch_id: branchId } }),
  getPayrollRuns: (params?: { tenant_id?: string; status?: string; skip?: number; limit?: number }) =>
    hrmsAxiosInstance.get(`/payroll/runs`, { params }),
  createPayrollRun: (data: PayrollRunPayload) =>
    hrmsAxiosInstance.post(`/payroll/runs`, data),
  getPayrollSlips: (runId: string, tenantId: string) =>
    hrmsAxiosInstance.get(`/payroll/runs/${runId}/slips`, { params: { tenant_id: tenantId } }),
  addPayrollSlip: (runId: string, data: PayrollSlipPayload) =>
    hrmsAxiosInstance.post(`/payroll/runs/${runId}/slips`, data),
  finalizePayrollRun: (runId: string, tenantId: string) =>
    hrmsAxiosInstance.post(`/payroll/runs/${runId}/finalize`, null, { params: { tenant_id: tenantId } }),
  getPayrollSummary: (params: { tenant_id: string; period_start?: string; period_end?: string }) =>
    hrmsAxiosInstance.get(`/payroll/summary`, { params }),

  // LOS Service
  getLoanProducts: () =>
    axiosInstance.get(`/products`),
  applyForLoan: (data: LoanApplicationPayload) =>
    axiosInstance.post(`/applications`, data),
  getLoanApplications: (customerIdOrParams?: string | { customer_id?: string; branch_id?: string; status?: string; skip?: number; limit?: number }) => {
    const params = typeof customerIdOrParams === 'string' ? { customer_id: customerIdOrParams } : customerIdOrParams;
    return axiosInstance.get(`/applications`, { params });
  },
  submitLoanApplication: (applicationId: string) =>
    axiosInstance.post(`/applications/${applicationId}/submit`),
  underwriteLoanApplication: (applicationId: string) =>
    axiosInstance.post(`/applications/${applicationId}/underwrite`),
  decideLoanApplication: (
    applicationId: string,
    data: {
      decision: 'approved' | 'rejected';
      approved_amount?: number;
      approved_tenure_months?: number;
      approved_interest_rate?: number;
      rejection_reason?: string;
    },
  ) => axiosInstance.post(`/applications/${applicationId}/decision`, data),

  // LMS Service
  getCustomerLoans: (customerId: string) =>
    axiosInstance.get(`/loans`, { params: { customer_id: customerId } }),
  getLoans: (params?: { customer_id?: string; branch_id?: string; status?: string; skip?: number; limit?: number }) =>
    axiosInstance.get(`/loans`, { params }),
  getEmiSchedule: (loanId: string) =>
    axiosInstance.get(`/loans/${loanId}/emi-schedule`),
  disburseLoan: (loanId: string, data: { amount?: number; reference?: string }) =>
    axiosInstance.post(`/loans/${loanId}/disburse`, data),
  computeLoanOverdue: (loanId: string) =>
    axiosInstance.post(`/loans/${loanId}/compute-overdue`),
  getLoanPayments: (loanId: string) =>
    axiosInstance.get(`/loans/${loanId}/payments`),
  makePayment: (loanId: string, data: PaymentPayload) =>
    axiosInstance.post(`/loans/${loanId}/payment`, data),

  // Deposits Service
  getDepositTypes: () =>
    axiosInstance.get(`/deposit-types`),
  getCustomerDepositAccounts: (customerId: string) =>
    axiosInstance.get(`/deposit-accounts`, { params: { customer_id: customerId } }),
  getDepositAccount: (accountId: string) =>
    axiosInstance.get(`/deposit-accounts/${accountId}`),
  getDepositInterestSchedule: (accountId: string) =>
    axiosInstance.get(`/deposit-accounts/${accountId}/interest-schedule`),
  getDepositTransactions: (accountId: string) =>
    axiosInstance.get(`/deposit-accounts/${accountId}/transactions`),
  getDepositStatement: (accountId: string, fromDate: string, toDate: string) =>
    axiosInstance.get(`/deposit-accounts/${accountId}/statement`, {
      params: { from_date: fromDate, to_date: toDate },
    }),
  createDepositTransaction: (accountId: string, data: DepositTransactionPayload) =>
    axiosInstance.post(`/deposit-accounts/${accountId}/transactions`, data),

  // Accounting Service
  getAccountingDashboard: (tenantId: string) =>
    axiosInstance.get(`/dashboard`, { params: { tenant_id: tenantId } }),
  getAccounting360Dashboard: (tenantId: string) =>
    axiosInstance.get(`/accounting-360/dashboard`, { params: { tenant_id: tenantId } }),
  searchAccounting360: (tenantId: string, query: string) =>
    axiosInstance.get(`/accounting-360/search`, { params: { tenant_id: tenantId, q: query } }),
  getAccounting360Gl: (tenantId: string, accountId: string) =>
    axiosInstance.get(`/accounting-360/gl/${accountId}`, { params: { tenant_id: tenantId } }),
  postAccounting360QuickAction: (data: AccountingQuickActionPayload) =>
    axiosInstance.post(`/accounting-360/quick-action`, data),
  getGlAccounts: (tenantId: string) =>
    axiosInstance.get(`/gl-accounts`, { params: { tenant_id: tenantId } }),
  getGlAccountSummary: (tenantId: string) =>
    axiosInstance.get(`/gl-accounts/summary`, { params: { tenant_id: tenantId } }),
  getGlAccountHierarchy: (tenantId: string) =>
    axiosInstance.get(`/gl-accounts/hierarchy`, { params: { tenant_id: tenantId } }),
  seedDefaultGlAccounts: (data: CoaSeedPayload) =>
    axiosInstance.post(`/gl-accounts/seed-defaults`, data),
  createGlAccount: (data: GlAccountPayload) =>
    axiosInstance.post(`/gl-accounts`, data),
  updateGlAccount: (accountId: string, tenantId: string, data: Partial<Omit<GlAccountPayload, 'tenant_id' | 'account_code'>>) =>
    axiosInstance.put(`/gl-accounts/${accountId}`, data, { params: { tenant_id: tenantId } }),
  getGlBalances: (tenantId: string) =>
    axiosInstance.get(`/gl-balances`, { params: { tenant_id: tenantId } }),
  getGlLedger: (tenantId: string, params?: { financial_year?: string; branch_id?: string }) =>
    axiosInstance.get(`/gl-ledger`, { params: { tenant_id: tenantId, ...params } }),
  getSubLedgerSummary: (tenantId: string) =>
    axiosInstance.get(`/sub-ledger-summary`, { params: { tenant_id: tenantId } }),
  getPostingRules: (tenantId: string) =>
    axiosInstance.get(`/posting-rules`, { params: { tenant_id: tenantId } }),
  createPostingRule: (data: PostingRulePayload) =>
    axiosInstance.post(`/posting-rules`, data),
  getJournalEntries: (tenantId: string) =>
    axiosInstance.get(`/journal-entries`, { params: { tenant_id: tenantId } }),
  validateAccountingPosting: (
    tenantId: string,
    lines: AccountingPostingLine[],
    context?: { source_module?: string; source_event?: string; source_reference?: string },
  ) =>
    axiosInstance.post(`/posting-engine/validate`, { tenant_id: tenantId, ...context, lines }),
  postAccountingEngine: (data: PostingEnginePayload) =>
    axiosInstance.post(`/posting-engine/post`, data),
  createVoucher: (data: VoucherPayload) =>
    axiosInstance.post(`/vouchers`, data),
  getVouchers: (tenantId: string, params?: {
    status?: string;
    voucher_type?: string;
    payment_category?: PaymentVoucherCategory;
    receipt_category?: ReceiptVoucherCategory;
    contra_transfer_type?: ContraTransferType;
    credit_note_type?: CreditNoteType;
    debit_note_type?: DebitNoteType;
  }) =>
    axiosInstance.get(`/vouchers`, { params: { tenant_id: tenantId, ...params } }),
  getPaymentVoucherCategories: () =>
    axiosInstance.get(`/payment-vouchers/categories`),
  createPaymentVoucher: (data: PaymentVoucherPayload) =>
    axiosInstance.post(`/payment-vouchers`, data),
  getReceiptVoucherOptions: () =>
    axiosInstance.get(`/receipt-vouchers/options`),
  createReceiptVoucher: (data: ReceiptVoucherPayload) =>
    axiosInstance.post(`/receipt-vouchers`, data),
  getContraVoucherOptions: () =>
    axiosInstance.get(`/contra-vouchers/options`),
  createContraVoucher: (data: ContraVoucherPayload) =>
    axiosInstance.post(`/contra-vouchers`, data),
  getCreditNoteOptions: () =>
    axiosInstance.get(`/credit-notes/options`),
  createCreditNote: (data: CreditNotePayload) =>
    axiosInstance.post(`/credit-notes`, data),
  getDebitNoteOptions: () =>
    axiosInstance.get(`/debit-notes/options`),
  createDebitNote: (data: DebitNotePayload) =>
    axiosInstance.post(`/debit-notes`, data),
  verifyVoucher: (voucherId: string, tenantId: string, performedBy?: string) =>
    axiosInstance.post(`/vouchers/${voucherId}/verify`, { tenant_id: tenantId, performed_by: performedBy }),
  approveVoucher: (voucherId: string, tenantId: string, performedBy?: string) =>
    axiosInstance.post(`/vouchers/${voucherId}/approve`, { tenant_id: tenantId, performed_by: performedBy }),
  postVoucher: (voucherId: string, tenantId: string, performedBy?: string) =>
    axiosInstance.post(`/vouchers/${voucherId}/post`, { tenant_id: tenantId, performed_by: performedBy }),
  reverseVoucher: (voucherId: string, tenantId: string, performedBy?: string) =>
    axiosInstance.post(`/vouchers/${voucherId}/reverse`, { tenant_id: tenantId, performed_by: performedBy }),
  getTrialBalance: (tenantId: string, startDate?: string, endDate?: string) =>
    axiosInstance.get(`/reports/trial-balance`, {
      params: { tenant_id: tenantId, start_date: startDate, end_date: endDate },
    }),
  getProfitLoss: (tenantId: string, startDate?: string, endDate?: string) =>
    axiosInstance.get(`/reports/profit-loss`, {
      params: { tenant_id: tenantId, start_date: startDate, end_date: endDate },
    }),
  getBalanceSheet: (tenantId: string, asOf?: string) =>
    axiosInstance.get(`/reports/balance-sheet`, {
      params: { tenant_id: tenantId, as_of: asOf },
    }),
  closeDayEnd: (data: DayEndClosePayload) =>
    axiosInstance.post(`/day-end/close`, data),
  getDayEndCloses: (tenantId: string) =>
    axiosInstance.get(`/day-end/closes`, { params: { tenant_id: tenantId } }),

  // Compliance Service
  runComplianceChecks: (customerId: string, data: JsonObject = {}) =>
    axiosInstance.post(`/run-checks/${customerId}`, data),

  // FinDNA Service
  getExecutiveDashboard: () =>
    axiosInstance.get(`/dashboard/executive`),
};
