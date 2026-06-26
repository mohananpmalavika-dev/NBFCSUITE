
import axios from 'axios';

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  'http://localhost:8000';

const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
});

type JsonObject = Record<string, unknown>;

export interface LoanApplicationPayload {
  customer_id: string;
  product_code: string;
  applied_amount: number;
  tenure_months: number;
}

export interface PaymentPayload {
  amount: number;
  payment_mode: string;
  reference: string;
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

export const apiClient = {
  setToken: (token: string) => {
    axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  },
  clearToken: () => {
    delete axiosInstance.defaults.headers.common['Authorization'];
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
  validateToken: () =>
    axiosInstance.get(`/auth/validate`),

  // Customer Service
  getCustomer: (customerId: string) =>
    axiosInstance.get(`/customers/${customerId}`),
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
  assignCustomerBranch: (customerId: string, branchId: string) =>
    axiosInstance.post(`/customers/${customerId}/assign-branch`, { branch_id: branchId }),
  getCustomerDocuments: (customerId: string) =>
    axiosInstance.get(`/documents`, { params: { subject_type: 'customer', subject_id: customerId } }),
  getExpiringDocuments: (customerId: string, days = 30) =>
    axiosInstance.get(`/documents/expiring`, { params: { subject_type: 'customer', subject_id: customerId, days } }),
  createDocument: (data: DocumentPayload) =>
    axiosInstance.post(`/documents`, data),
  expireDocument: (documentId: string) =>
    axiosInstance.put(`/documents/${documentId}/expire`),

  // LOS Service
  getLoanProducts: () =>
    axiosInstance.get(`/products`),
  applyForLoan: (data: LoanApplicationPayload) =>
    axiosInstance.post(`/applications`, data),
  getLoanApplications: (customerId: string) =>
    axiosInstance.get(`/applications`, { params: { customer_id: customerId } }),

  // LMS Service
  getCustomerLoans: (customerId: string) =>
    axiosInstance.get(`/loans`, { params: { customer_id: customerId } }),
  getLoanPayments: (loanId: string) =>
    axiosInstance.get(`/loans/${loanId}/payments`),
  makePayment: (loanId: string, data: PaymentPayload) =>
    axiosInstance.post(`/loans/${loanId}/payment`, data),

  // Compliance Service
  runComplianceChecks: (customerId: string, data: JsonObject = {}) =>
    axiosInstance.post(`/run-checks/${customerId}`, data),

  // FinDNA Service
  getExecutiveDashboard: () =>
    axiosInstance.get(`/dashboard/executive`),
};
