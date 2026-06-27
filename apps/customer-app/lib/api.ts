
import axios from 'axios';

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  'http://localhost:8000';

const HRMS_API_BASE_URL =
  process.env.NEXT_PUBLIC_HRMS_API_URL ||
  'http://localhost:8012';

const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
});

const hrmsAxiosInstance = axios.create({
  baseURL: HRMS_API_BASE_URL,
});

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
  brand_code: string;
  brand_name: string;
  legal_name?: string;
  short_name?: string;
  email?: string;
  phone?: string;
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

export interface EomZonePayload {
  tenant_id: string;
  business_unit_id: string;
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

export interface HrmsEmployeePayload {
  tenant_id: string;
  employee_number: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  designation: string;
  department: string;
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
  branch_id?: string;
  user_id?: string;
  employment_type?: string;
  status?: string;
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
  getEomBrands: () => axiosInstance.get(`/eom/brands`),
  createEomBrand: (data: EomBrandPayload) => axiosInstance.post(`/eom/brands`, data),
  getEomLegalEntities: () => axiosInstance.get(`/eom/legal-entities`),
  createEomLegalEntity: (data: EomLegalEntityPayload) => axiosInstance.post(`/eom/legal-entities`, data),
  getEomBusinessUnits: () => axiosInstance.get(`/eom/business-units`),
  createEomBusinessUnit: (data: EomBusinessUnitPayload) => axiosInstance.post(`/eom/business-units`, data),
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
  expireDocument: (documentId: string) =>
    axiosInstance.put(`/documents/${documentId}/expire`),

  // HRMS Service
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

  // Compliance Service
  runComplianceChecks: (customerId: string, data: JsonObject = {}) =>
    axiosInstance.post(`/run-checks/${customerId}`, data),

  // FinDNA Service
  getExecutiveDashboard: () =>
    axiosInstance.get(`/dashboard/executive`),
};
