/**
 * Customer 360 / CIF API Service
 * Complete service layer for customer management operations
 */

import { apiClient } from "@/lib/api/client";
import type {
  Customer,
  CustomerCreate,
  CustomerUpdate,
  CustomerListItem,
  PaginatedCustomerResponse,
  CustomerDashboardStats,
  CustomerFilters,
  CustomerSearchParams,
  CustomerDocument,
  CustomerDocumentCreate,
  CustomerFamily,
  CustomerFamilyCreate,
  CustomerFamilyUpdate,
  CustomerBankAccount,
  CustomerBankAccountCreate,
  CustomerBankAccountUpdate,
  CustomerKYC,
  CustomerKYCUpdate,
  TimelineActivity,
  TimelineActivityCreate,
  PaginatedTimelineResponse,
  TimelineSummaryResponse,
  BureauPullRequest,
  BureauPullResponse,
  BureauHistoryResponse,
  CreditScoreResponse,
  AadhaarOTPInitRequest,
  AadhaarOTPInitResponse,
  AadhaarOTPVerifyRequest,
  AadhaarOTPVerifyResponse,
  BiometricVerifyRequest,
  BiometricVerifyResponse,
  DigiLockerAuthInitResponse,
  DigiLockerAuthCompleteRequest,
  DigiLockerAuthCompleteResponse,
  DigiLockerFetchDocumentRequest,
} from "@/types/customer.types";

const BASE_URL = "/api/v1/customers";

// ============================================================================
// CUSTOMER CRUD OPERATIONS
// ============================================================================

/**
 * Create new customer
 */
export const createCustomer = async (
  data: CustomerCreate
): Promise<Customer> => {
  const response = await apiClient.post<Customer>(BASE_URL, data);
  return response.data;
};

/**
 * Get paginated list of customers with filters
 */
export const getCustomers = async (
  filters?: CustomerFilters
): Promise<PaginatedCustomerResponse> => {
  const params = new URLSearchParams();
  
  if (filters?.page) params.append("page", filters.page.toString());
  if (filters?.page_size) params.append("page_size", filters.page_size.toString());
  if (filters?.search) params.append("search", filters.search);
  if (filters?.kyc_status) params.append("kyc_status", filters.kyc_status);
  if (filters?.risk_rating) params.append("risk_rating", filters.risk_rating);
  if (filters?.is_active !== undefined) params.append("is_active", filters.is_active.toString());
  
  const response = await apiClient.get<PaginatedCustomerResponse>(
    `${BASE_URL}?${params.toString()}`
  );
  return response.data;
};

/**
 * Get customer dashboard statistics
 */
export const getCustomerStats = async (): Promise<CustomerDashboardStats> => {
  const response = await apiClient.get<CustomerDashboardStats>(`${BASE_URL}/stats`);
  return response.data;
};

/**
 * Search customers by mobile, PAN, or Aadhaar
 */
export const searchCustomers = async (
  params: CustomerSearchParams
): Promise<Customer[]> => {
  const searchParams = new URLSearchParams();
  
  if (params.mobile) searchParams.append("mobile", params.mobile);
  if (params.pan) searchParams.append("pan", params.pan);
  if (params.aadhaar) searchParams.append("aadhaar", params.aadhaar);
  
  const response = await apiClient.get<Customer[]>(
    `${BASE_URL}/search?${searchParams.toString()}`
  );
  return response.data;
};

/**
 * Get customer by ID
 */
export const getCustomerById = async (customerId: number): Promise<Customer> => {
  const response = await apiClient.get<Customer>(`${BASE_URL}/${customerId}`);
  return response.data;
};

/**
 * Get customer by customer code
 */
export const getCustomerByCode = async (customerCode: string): Promise<Customer> => {
  const response = await apiClient.get<Customer>(`${BASE_URL}/code/${customerCode}`);
  return response.data;
};

/**
 * Update customer details
 */
export const updateCustomer = async (
  customerId: number,
  data: CustomerUpdate
): Promise<Customer> => {
  const response = await apiClient.put<Customer>(`${BASE_URL}/${customerId}`, data);
  return response.data;
};

/**
 * Delete customer (soft delete)
 */
export const deleteCustomer = async (customerId: number): Promise<void> => {
  await apiClient.delete(`${BASE_URL}/${customerId}`);
};

// ============================================================================
// CUSTOMER ACTIONS
// ============================================================================

/**
 * Blacklist a customer
 */
export const blacklistCustomer = async (
  customerId: number,
  reason: string
): Promise<Customer> => {
  const response = await apiClient.post<Customer>(
    `${BASE_URL}/${customerId}/blacklist`,
    null,
    { params: { reason } }
  );
  return response.data;
};

/**
 * Remove customer from blacklist
 */
export const unblacklistCustomer = async (customerId: number): Promise<Customer> => {
  const response = await apiClient.post<Customer>(
    `${BASE_URL}/${customerId}/unblacklist`
  );
  return response.data;
};

/**
 * Update customer CIBIL score
 */
export const updateCibilScore = async (
  customerId: number,
  cibilScore: number
): Promise<Customer> => {
  const response = await apiClient.post<Customer>(
    `${BASE_URL}/${customerId}/update-cibil`,
    null,
    { params: { cibil_score: cibilScore } }
  );
  return response.data;
};

// ============================================================================
// CUSTOMER DOCUMENTS
// ============================================================================

/**
 * Get all documents for a customer
 */
export const getCustomerDocuments = async (
  customerId: number
): Promise<CustomerDocument[]> => {
  const response = await apiClient.get<CustomerDocument[]>(
    `${BASE_URL}/${customerId}/documents`
  );
  return response.data;
};

/**
 * Upload customer document
 */
export const uploadCustomerDocument = async (
  data: CustomerDocumentCreate
): Promise<CustomerDocument> => {
  const response = await apiClient.post<CustomerDocument>(
    `${BASE_URL}/${data.customer_id}/documents`,
    data
  );
  return response.data;
};

/**
 * Get document by ID
 */
export const getDocumentById = async (
  customerId: number,
  documentId: number
): Promise<CustomerDocument> => {
  const response = await apiClient.get<CustomerDocument>(
    `${BASE_URL}/${customerId}/documents/${documentId}`
  );
  return response.data;
};

/**
 * Update document
 */
export const updateDocument = async (
  customerId: number,
  documentId: number,
  data: Partial<CustomerDocumentCreate>
): Promise<CustomerDocument> => {
  const response = await apiClient.put<CustomerDocument>(
    `${BASE_URL}/${customerId}/documents/${documentId}`,
    data
  );
  return response.data;
};

/**
 * Delete document
 */
export const deleteDocument = async (
  customerId: number,
  documentId: number
): Promise<void> => {
  await apiClient.delete(`${BASE_URL}/${customerId}/documents/${documentId}`);
};

/**
 * Verify document
 */
export const verifyDocument = async (
  customerId: number,
  documentId: number
): Promise<CustomerDocument> => {
  const response = await apiClient.post<CustomerDocument>(
    `${BASE_URL}/${customerId}/documents/${documentId}/verify`
  );
  return response.data;
};

// ============================================================================
// CUSTOMER FAMILY
// ============================================================================

/**
 * Get all family members for a customer
 */
export const getCustomerFamily = async (
  customerId: number
): Promise<CustomerFamily[]> => {
  const response = await apiClient.get<CustomerFamily[]>(
    `${BASE_URL}/${customerId}/family`
  );
  return response.data;
};

/**
 * Add family member
 */
export const addFamilyMember = async (
  data: CustomerFamilyCreate
): Promise<CustomerFamily> => {
  const response = await apiClient.post<CustomerFamily>(
    `${BASE_URL}/${data.customer_id}/family`,
    data
  );
  return response.data;
};

/**
 * Update family member
 */
export const updateFamilyMember = async (
  customerId: number,
  familyId: number,
  data: CustomerFamilyUpdate
): Promise<CustomerFamily> => {
  const response = await apiClient.put<CustomerFamily>(
    `${BASE_URL}/${customerId}/family/${familyId}`,
    data
  );
  return response.data;
};

/**
 * Delete family member
 */
export const deleteFamilyMember = async (
  customerId: number,
  familyId: number
): Promise<void> => {
  await apiClient.delete(`${BASE_URL}/${customerId}/family/${familyId}`);
};

// ============================================================================
// CUSTOMER BANK ACCOUNTS
// ============================================================================

/**
 * Get all bank accounts for a customer
 */
export const getCustomerBankAccounts = async (
  customerId: number
): Promise<CustomerBankAccount[]> => {
  const response = await apiClient.get<CustomerBankAccount[]>(
    `${BASE_URL}/${customerId}/bank-accounts`
  );
  return response.data;
};

/**
 * Add bank account
 */
export const addBankAccount = async (
  data: CustomerBankAccountCreate
): Promise<CustomerBankAccount> => {
  const response = await apiClient.post<CustomerBankAccount>(
    `${BASE_URL}/${data.customer_id}/bank-accounts`,
    data
  );
  return response.data;
};

/**
 * Update bank account
 */
export const updateBankAccount = async (
  customerId: number,
  accountId: number,
  data: CustomerBankAccountUpdate
): Promise<CustomerBankAccount> => {
  const response = await apiClient.put<CustomerBankAccount>(
    `${BASE_URL}/${customerId}/bank-accounts/${accountId}`,
    data
  );
  return response.data;
};

/**
 * Delete bank account
 */
export const deleteBankAccount = async (
  customerId: number,
  accountId: number
): Promise<void> => {
  await apiClient.delete(`${BASE_URL}/${customerId}/bank-accounts/${accountId}`);
};

/**
 * Verify bank account
 */
export const verifyBankAccount = async (
  customerId: number,
  accountId: number
): Promise<CustomerBankAccount> => {
  const response = await apiClient.post<CustomerBankAccount>(
    `${BASE_URL}/${customerId}/bank-accounts/${accountId}/verify`
  );
  return response.data;
};

/**
 * Set primary bank account
 */
export const setPrimaryBankAccount = async (
  customerId: number,
  accountId: number
): Promise<CustomerBankAccount> => {
  const response = await apiClient.post<CustomerBankAccount>(
    `${BASE_URL}/${customerId}/bank-accounts/${accountId}/set-primary`
  );
  return response.data;
};

// ============================================================================
// CUSTOMER KYC
// ============================================================================

/**
 * Get KYC details for a customer
 */
export const getCustomerKYC = async (customerId: number): Promise<CustomerKYC> => {
  const response = await apiClient.get<CustomerKYC>(`${BASE_URL}/${customerId}/kyc`);
  return response.data;
};

/**
 * Update KYC details
 */
export const updateCustomerKYC = async (
  customerId: number,
  data: CustomerKYCUpdate
): Promise<CustomerKYC> => {
  const response = await apiClient.put<CustomerKYC>(
    `${BASE_URL}/${customerId}/kyc`,
    data
  );
  return response.data;
};

// ============================================================================
// CUSTOMER TIMELINE
// ============================================================================

/**
 * Get customer timeline activities
 */
export const getCustomerTimeline = async (
  customerId: number,
  page: number = 1,
  pageSize: number = 20,
  activityType?: string,
  eventCategory?: string
): Promise<PaginatedTimelineResponse> => {
  const params = new URLSearchParams();
  params.append("page", page.toString());
  params.append("page_size", pageSize.toString());
  if (activityType) params.append("activity_type", activityType);
  if (eventCategory) params.append("event_category", eventCategory);
  
  const response = await apiClient.get<PaginatedTimelineResponse>(
    `${BASE_URL}/${customerId}/timeline?${params.toString()}`
  );
  return response.data;
};

/**
 * Add timeline activity
 */
export const addTimelineActivity = async (
  customerId: number,
  data: TimelineActivityCreate
): Promise<TimelineActivity> => {
  const response = await apiClient.post<TimelineActivity>(
    `${BASE_URL}/${customerId}/timeline`,
    data
  );
  return response.data;
};

/**
 * Get timeline summary
 */
export const getTimelineSummary = async (
  customerId: number,
  days: number = 30
): Promise<TimelineSummaryResponse> => {
  const response = await apiClient.get<TimelineSummaryResponse>(
    `${BASE_URL}/${customerId}/timeline/summary?days=${days}`
  );
  return response.data;
};

// ============================================================================
// CREDIT BUREAU
// ============================================================================

/**
 * Pull credit report from bureau
 */
export const pullCreditReport = async (
  customerId: number,
  data: BureauPullRequest
): Promise<BureauPullResponse> => {
  const response = await apiClient.post<BureauPullResponse>(
    `${BASE_URL}/${customerId}/bureau/pull`,
    data
  );
  return response.data;
};

/**
 * Get bureau pull history
 */
export const getBureauHistory = async (
  customerId: number
): Promise<BureauHistoryResponse[]> => {
  const response = await apiClient.get<BureauHistoryResponse[]>(
    `${BASE_URL}/${customerId}/bureau/history`
  );
  return response.data;
};

/**
 * Get latest credit score
 */
export const getLatestCreditScore = async (
  customerId: number
): Promise<CreditScoreResponse> => {
  const response = await apiClient.get<CreditScoreResponse>(
    `${BASE_URL}/${customerId}/bureau/latest-score`
  );
  return response.data;
};

// ============================================================================
// eKYC / AADHAAR VERIFICATION
// ============================================================================

/**
 * Initiate Aadhaar OTP verification
 */
export const initiateAadhaarOTP = async (
  customerId: number,
  data: AadhaarOTPInitRequest
): Promise<AadhaarOTPInitResponse> => {
  const response = await apiClient.post<AadhaarOTPInitResponse>(
    `${BASE_URL}/${customerId}/ekyc/aadhaar/otp/init`,
    data
  );
  return response.data;
};

/**
 * Verify Aadhaar OTP
 */
export const verifyAadhaarOTP = async (
  customerId: number,
  data: AadhaarOTPVerifyRequest
): Promise<AadhaarOTPVerifyResponse> => {
  const response = await apiClient.post<AadhaarOTPVerifyResponse>(
    `${BASE_URL}/${customerId}/ekyc/aadhaar/otp/verify`,
    data
  );
  return response.data;
};

/**
 * Verify Aadhaar using biometric
 */
export const verifyAadhaarBiometric = async (
  customerId: number,
  data: BiometricVerifyRequest
): Promise<BiometricVerifyResponse> => {
  const response = await apiClient.post<BiometricVerifyResponse>(
    `${BASE_URL}/${customerId}/ekyc/aadhaar/biometric`,
    data
  );
  return response.data;
};

/**
 * Verify PAN
 */
export const verifyPAN = async (
  customerId: number,
  panNumber: string
): Promise<{ verified: boolean; message: string; pan_data?: any }> => {
  const response = await apiClient.post(
    `${BASE_URL}/${customerId}/ekyc/pan/verify`,
    { pan_number: panNumber }
  );
  return response.data;
};

// ============================================================================
// DIGILOCKER
// ============================================================================

/**
 * Initialize DigiLocker authorization
 */
export const initializeDigiLockerAuth = async (
  customerId: number,
  redirectUri: string
): Promise<DigiLockerAuthInitResponse> => {
  const response = await apiClient.post<DigiLockerAuthInitResponse>(
    `${BASE_URL}/${customerId}/digilocker/authorize`,
    { redirect_uri: redirectUri }
  );
  return response.data;
};

/**
 * Complete DigiLocker authorization
 */
export const completeDigiLockerAuth = async (
  customerId: number,
  data: DigiLockerAuthCompleteRequest
): Promise<DigiLockerAuthCompleteResponse> => {
  const response = await apiClient.post<DigiLockerAuthCompleteResponse>(
    `${BASE_URL}/${customerId}/digilocker/complete`,
    data
  );
  return response.data;
};

/**
 * Fetch and store document from DigiLocker
 */
export const fetchDigiLockerDocument = async (
  customerId: number,
  data: DigiLockerFetchDocumentRequest
): Promise<CustomerDocument> => {
  const response = await apiClient.post<CustomerDocument>(
    `${BASE_URL}/${customerId}/digilocker/fetch-document`,
    data
  );
  return response.data;
};

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Export customers to Excel
 */
export const exportCustomers = async (filters?: CustomerFilters): Promise<Blob> => {
  const params = new URLSearchParams();
  if (filters?.search) params.append("search", filters.search);
  if (filters?.kyc_status) params.append("kyc_status", filters.kyc_status);
  if (filters?.risk_rating) params.append("risk_rating", filters.risk_rating);
  
  const response = await apiClient.get(`${BASE_URL}/export?${params.toString()}`, {
    responseType: "blob",
  });
  return response.data;
};

/**
 * Get customer 360 view (all related data)
 */
export const getCustomer360View = async (customerId: number) => {
  const [
    customer,
    documents,
    family,
    bankAccounts,
    kyc,
    timeline,
    bureauHistory,
  ] = await Promise.all([
    getCustomerById(customerId),
    getCustomerDocuments(customerId).catch(() => []),
    getCustomerFamily(customerId).catch(() => []),
    getCustomerBankAccounts(customerId).catch(() => []),
    getCustomerKYC(customerId).catch(() => null),
    getCustomerTimeline(customerId, 1, 10).catch(() => ({ items: [], total: 0, page: 1, page_size: 10, pages: 0 })),
    getBureauHistory(customerId).catch(() => []),
  ]);
  
  return {
    customer,
    documents,
    family,
    bankAccounts,
    kyc,
    timeline,
    bureauHistory,
  };
};

/**
 * Validate if customer can be deleted
 */
export const canDeleteCustomer = async (customerId: number): Promise<boolean> => {
  try {
    const response = await apiClient.get<{ can_delete: boolean; reason?: string }>(
      `${BASE_URL}/${customerId}/can-delete`
    );
    return response.data.can_delete;
  } catch {
    return false;
  }
};

/**
 * Get customer's active loans count
 */
export const getCustomerLoansCount = async (customerId: number): Promise<number> => {
  try {
    const response = await apiClient.get<{ count: number }>(
      `${BASE_URL}/${customerId}/loans/count`
    );
    return response.data.count;
  } catch {
    return 0;
  }
};

// Export all functions as default object
const customerService = {
  // CRUD
  createCustomer,
  getCustomers,
  getCustomerStats,
  searchCustomers,
  getCustomerById,
  getCustomerByCode,
  updateCustomer,
  deleteCustomer,
  
  // Actions
  blacklistCustomer,
  unblacklistCustomer,
  updateCibilScore,
  
  // Documents
  getCustomerDocuments,
  uploadCustomerDocument,
  getDocumentById,
  updateDocument,
  deleteDocument,
  verifyDocument,
  
  // Family
  getCustomerFamily,
  addFamilyMember,
  updateFamilyMember,
  deleteFamilyMember,
  
  // Bank Accounts
  getCustomerBankAccounts,
  addBankAccount,
  updateBankAccount,
  deleteBankAccount,
  verifyBankAccount,
  setPrimaryBankAccount,
  
  // KYC
  getCustomerKYC,
  updateCustomerKYC,
  
  // Timeline
  getCustomerTimeline,
  addTimelineActivity,
  getTimelineSummary,
  
  // Bureau
  pullCreditReport,
  getBureauHistory,
  getLatestCreditScore,
  
  // eKYC
  initiateAadhaarOTP,
  verifyAadhaarOTP,
  verifyAadhaarBiometric,
  verifyPAN,
  
  // DigiLocker
  initializeDigiLockerAuth,
  completeDigiLockerAuth,
  fetchDigiLockerDocument,
  
  // Utilities
  exportCustomers,
  getCustomer360View,
  canDeleteCustomer,
  getCustomerLoansCount,
};

export default customerService;
