/**
 * Locker Management Service
 * API calls for locker management operations
 */

import { apiClient } from '@/lib/api-client'
import type { PaginatedResponse, PaginationParams } from '@/types'

// ============================================
// Type Definitions
// ============================================

export enum LockerSize {
  SMALL = 'small',
  MEDIUM = 'medium',
  LARGE = 'large',
  EXTRA_LARGE = 'extra_large'
}

export enum LockerStatus {
  AVAILABLE = 'available',
  ALLOCATED = 'allocated',
  UNDER_MAINTENANCE = 'under_maintenance',
  BLOCKED = 'blocked',
  DAMAGED = 'damaged',
  RETIRED = 'retired'
}

export enum AllocationStatus {
  ACTIVE = 'active',
  EXPIRED = 'expired',
  CLOSED = 'closed',
  SURRENDERED = 'surrendered',
  TRANSFERRED = 'transferred'
}

export enum PaymentType {
  RENT = 'rent',
  SECURITY_DEPOSIT = 'security_deposit',
  PENALTY = 'penalty',
  LATE_FEE = 'late_fee',
  DUPLICATE_KEY_CHARGE = 'duplicate_key_charge',
  MISCELLANEOUS = 'miscellaneous'
}

export enum PaymentMode {
  CASH = 'cash',
  CHEQUE = 'cheque',
  NEFT = 'neft',
  RTGS = 'rtgs',
  IMPS = 'imps',
  UPI = 'upi',
  CARD = 'card',
  ONLINE = 'online'
}

export interface LockerMaster {
  id: string
  locker_number: string
  locker_id: string
  locker_size: LockerSize
  branch_id: string
  branch_name?: string
  vault_room: string
  floor?: string
  rack_number?: string
  position?: string
  locker_type: string
  lock_type?: string
  annual_rent: number
  security_deposit: number
  status: LockerStatus
  is_available: boolean
  installation_date?: string
  last_maintenance_date?: string
  next_maintenance_date?: string
  created_at: string
  updated_at: string
}

export interface LockerAllocation {
  id: string
  allocation_number: string
  agreement_number: string
  locker_id: string
  customer_id: string
  allocation_date: string
  agreement_start_date: string
  agreement_end_date: string
  annual_rent: number
  security_deposit: number
  rent_frequency: string
  status: AllocationStatus
  security_deposit_paid: boolean
  rent_paid_upto_date?: string
  next_rent_due_date?: string
  outstanding_rent: number
  total_rent_paid: number
  nominee_name?: string
  nominee_relationship?: string
  auto_renewal: boolean
  created_at: string
  updated_at: string
}

export interface LockerRentPayment {
  id: string
  receipt_number: string
  allocation_id: string
  customer_id: string
  payment_date: string
  payment_type: PaymentType
  payment_mode: PaymentMode
  total_amount: number
  rent_amount: number
  gst_amount: number
  penalty_amount: number
  late_fee_amount: number
  payment_status: string
  period_from?: string
  period_to?: string
  created_at: string
}

export interface OccupancyStats {
  total_lockers: number
  available_lockers: number
  allocated_lockers: number
  under_maintenance: number
  blocked: number
  occupancy_rate: number
  by_size: Record<string, number>
  by_branch: Record<string, number>
}

export interface RevenueStats {
  total_revenue: number
  rent_revenue: number
  deposit_revenue: number
  penalty_revenue: number
  other_revenue: number
  outstanding_rent: number
  expected_annual_revenue: number
  revenue_by_month: Array<{ month: string; revenue: number }>
  revenue_by_branch: Array<{ branch: string; revenue: number }>
}

export interface LockerDashboard {
  occupancy: OccupancyStats
  revenue: RevenueStats
  expiring_allocations: Array<any>
  maintenance_due: Array<any>
  collection_efficiency: any
  recent_allocations: number
  recent_payments: number
}

// ============================================
// Locker Service
// ============================================

export const lockerService = {
  // ============================================
  // Locker Master Management
  // ============================================

  async getLockers(params?: PaginationParams & {
    locker_size?: LockerSize
    branch_id?: string
    vault_room?: string
    status?: LockerStatus
    is_available?: boolean
  }) {
    return apiClient.get<PaginatedResponse<LockerMaster>>('/lockers/master', { params })
  },

  async getLocker(id: string) {
    return apiClient.get<LockerMaster>(`/lockers/master/${id}`)
  },

  async createLocker(data: Partial<LockerMaster>) {
    return apiClient.post<LockerMaster>('/lockers/master', data)
  },

  async updateLocker(id: string, data: Partial<LockerMaster>) {
    return apiClient.put<LockerMaster>(`/lockers/master/${id}`, data)
  },

  async deleteLocker(id: string) {
    return apiClient.delete(`/lockers/master/${id}`)
  },

  async checkAvailability(params?: {
    branch_id?: string
    locker_size?: LockerSize
    vault_room?: string
  }) {
    return apiClient.get('/lockers/availability', { params })
  },

  async getFloorPlan(branch_id: string, vault_room: string) {
    return apiClient.get('/lockers/floor-plan', { 
      params: { branch_id, vault_room } 
    })
  },

  async getOccupancyStats(branch_id?: string) {
    return apiClient.get<OccupancyStats>('/lockers/occupancy-stats', { 
      params: { branch_id } 
    })
  },

  // ============================================
  // Allocation Management
  // ============================================

  async getAllocations(params?: PaginationParams & {
    customer_id?: string
    locker_id?: string
    status?: AllocationStatus
    branch_id?: string
    expiring_within_days?: number
  }) {
    return apiClient.get<PaginatedResponse<LockerAllocation>>('/lockers/allocations', { params })
  },

  async getAllocation(id: string) {
    return apiClient.get<LockerAllocation>(`/lockers/allocations/${id}`)
  },

  async createAllocation(data: any) {
    return apiClient.post<LockerAllocation>('/lockers/allocations', data)
  },

  async updateAllocation(id: string, data: Partial<LockerAllocation>) {
    return apiClient.put<LockerAllocation>(`/lockers/allocations/${id}`, data)
  },

  async calculateRent(allocationId: string, data: {
    allocation_id: string
    period_from: string
    period_to: string
    include_gst?: boolean
    include_penalty?: boolean
  }) {
    return apiClient.post(`/lockers/allocations/${allocationId}/calculate-rent`, data)
  },

  async renewAllocation(id: string, data: {
    new_end_date: string
    annual_rent: number
    adjust_security_deposit?: boolean
    additional_deposit?: number
    remarks?: string
  }) {
    return apiClient.post(`/lockers/allocations/${id}/renew`, data)
  },

  async closeAllocation(id: string, data: {
    closure_date: string
    closure_reason: string
    refund_security_deposit?: boolean
    closure_charges?: number
    final_settlement_amount?: number
    remarks?: string
  }) {
    return apiClient.post(`/lockers/allocations/${id}/close`, data)
  },

  async getExpiringAllocations(days_threshold: number = 30, branch_id?: string) {
    return apiClient.get('/lockers/allocations/expiring/alerts', {
      params: { days_threshold, branch_id }
    })
  },

  async getOverdueRents(branch_id?: string) {
    return apiClient.get('/lockers/allocations/overdue/alerts', {
      params: { branch_id }
    })
  },

  // ============================================
  // Payment Management
  // ============================================

  async getPayments(params?: PaginationParams & {
    allocation_id?: string
    customer_id?: string
    payment_type?: PaymentType
    payment_mode?: PaymentMode
    payment_status?: string
  }) {
    return apiClient.get<PaginatedResponse<LockerRentPayment>>('/lockers/payments', { params })
  },

  async getPayment(id: string) {
    return apiClient.get<LockerRentPayment>(`/lockers/payments/${id}`)
  },

  async recordPayment(data: any) {
    return apiClient.post<LockerRentPayment>('/lockers/payments', data)
  },

  async updatePayment(id: string, data: Partial<LockerRentPayment>) {
    return apiClient.put<LockerRentPayment>(`/lockers/payments/${id}`, data)
  },

  async cancelPayment(id: string, reason: string) {
    return apiClient.post(`/lockers/payments/${id}/cancel`, null, {
      params: { reason }
    })
  },

  async getPaymentHistory(allocationId: string) {
    return apiClient.get(`/lockers/payments/allocation/${allocationId}/history`)
  },

  async getRevenueStats(params?: {
    start_date?: string
    end_date?: string
    branch_id?: string
  }) {
    return apiClient.get<RevenueStats>('/lockers/payments/revenue/stats', { params })
  },

  async getCollectionEfficiency(branch_id?: string) {
    return apiClient.get('/lockers/payments/collection/efficiency', {
      params: { branch_id }
    })
  },

  // ============================================
  // Dashboard & Analytics
  // ============================================

  async getDashboard(branch_id?: string) {
    return apiClient.get<LockerDashboard>('/lockers/dashboard', {
      params: { branch_id }
    })
  },

  async getInventoryReport(branch_id?: string) {
    return apiClient.get('/lockers/reports/inventory', {
      params: { branch_id }
    })
  },

  async getMaintenanceDueReport(days_threshold: number = 30, branch_id?: string) {
    return apiClient.get('/lockers/reports/maintenance-due', {
      params: { days_threshold, branch_id }
    })
  },

  async getHealthCheck() {
    return apiClient.get('/lockers/health')
  }
}


// ============================================
// Customer Management Type Definitions
// ============================================

export enum CustomerType {
  PRIMARY = 'primary',
  JOINT_HOLDER = 'joint_holder',
  NOMINEE = 'nominee',
  AUTHORIZED_SIGNATORY = 'authorized_signatory'
}

export enum CustomerCategory {
  REGULAR = 'regular',
  PREMIUM = 'premium',
  SENIOR_CITIZEN = 'senior_citizen',
  STAFF = 'staff',
  VIP = 'vip'
}

export enum OperationMode {
  EITHER_OR_SURVIVOR = 'either_or_survivor',
  FORMER_OR_SURVIVOR = 'former_or_survivor',
  LATTER_OR_SURVIVOR = 'latter_or_survivor',
  JOINT = 'joint',
  ANYONE = 'anyone'
}

export enum HolderType {
  PRIMARY = 'primary',
  SECONDARY = 'secondary',
  TERTIARY = 'tertiary'
}

export enum KYCDocumentType {
  PAN_CARD = 'pan_card',
  AADHAR_CARD = 'aadhar_card',
  PASSPORT = 'passport',
  VOTER_ID = 'voter_id',
  DRIVING_LICENSE = 'driving_license',
  BANK_STATEMENT = 'bank_statement',
  UTILITY_BILL = 'utility_bill',
  RENT_AGREEMENT = 'rent_agreement',
  SALARY_SLIP = 'salary_slip',
  INCOME_TAX_RETURN = 'income_tax_return',
  PHOTO = 'photo',
  SIGNATURE = 'signature',
  ADDRESS_PROOF = 'address_proof',
  IDENTITY_PROOF = 'identity_proof',
  OTHER = 'other'
}

export enum KYCDocumentCategory {
  IDENTITY_PROOF = 'identity_proof',
  ADDRESS_PROOF = 'address_proof',
  INCOME_PROOF = 'income_proof',
  PHOTO = 'photo',
  SIGNATURE = 'signature',
  OTHER = 'other'
}

export enum VerificationStatus {
  PENDING = 'pending',
  VERIFIED = 'verified',
  REJECTED = 'rejected',
  EXPIRED = 'expired',
  RESUBMISSION_REQUIRED = 'resubmission_required'
}

export enum AuthorizationType {
  FULL_ACCESS = 'full_access',
  LIMITED_ACCESS = 'limited_access',
  EMERGENCY_ACCESS = 'emergency_access',
  TEMPORARY_ACCESS = 'temporary_access'
}

export enum ApprovalStatus {
  PENDING = 'pending',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  REVOKED = 'revoked',
  EXPIRED = 'expired'
}

export interface LockerCustomer {
  id: string
  locker_customer_id: string
  customer_id: string
  allocation_id?: string
  customer_type: CustomerType
  
  // Personal details
  title?: string
  full_name: string
  date_of_birth?: string
  age?: number
  gender?: string
  
  // Contact
  mobile_number: string
  alternate_mobile?: string
  email?: string
  
  // Address
  current_address_line1?: string
  current_address_line2?: string
  current_city?: string
  current_state?: string
  current_pincode?: string
  current_country: string
  
  permanent_address_line1?: string
  permanent_address_line2?: string
  permanent_city?: string
  permanent_state?: string
  permanent_pincode?: string
  permanent_country: string
  address_same_as_current: boolean
  
  // Identification
  pan_number?: string
  aadhar_number?: string
  passport_number?: string
  driving_license_number?: string
  voter_id_number?: string
  
  // Employment
  occupation?: string
  employer_name?: string
  employer_address?: string
  annual_income?: number
  income_source?: string
  
  // Banking
  bank_account_number?: string
  bank_name?: string
  bank_branch?: string
  bank_ifsc?: string
  
  // Purpose
  locker_purpose?: string
  locker_purpose_details?: string
  estimated_value_of_contents?: number
  insurance_required: boolean
  insurance_amount?: number
  
  // Category
  customer_category: CustomerCategory
  is_senior_citizen: boolean
  is_staff_member: boolean
  is_premium_customer: boolean
  
  // Status
  status: string
  verification_status: VerificationStatus
  verification_date?: string
  
  // Metadata
  photo_path?: string
  signature_path?: string
  preferred_language: string
  sms_alerts: boolean
  email_alerts: boolean
  whatsapp_alerts: boolean
  special_instructions?: string
  remarks?: string
  created_at: string
  updated_at: string
}

export interface LockerJointHolder {
  id: string
  joint_holder_id: string
  allocation_id: string
  locker_customer_id: string
  customer_id: string
  
  holder_type: HolderType
  holder_sequence: number
  operation_mode: OperationMode
  
  // Authority
  can_operate_alone: boolean
  requires_joint_operation: boolean
  
  // Permissions
  can_deposit: boolean
  can_retrieve: boolean
  can_make_payments: boolean
  can_surrender: boolean
  can_add_nominee: boolean
  
  // Agreement
  agreement_accepted: boolean
  agreement_accepted_date?: string
  
  // Survivorship
  survivorship_rights: boolean
  inheritance_percentage: number
  
  // Status
  status: string
  activation_date?: string
  deactivation_date?: string
  deactivation_reason?: string
  
  signature_path?: string
  photo_path?: string
  specimen_signature_verified: boolean
  special_instructions?: string
  remarks?: string
  created_at: string
  updated_at: string
}

export interface LockerKYC {
  id: string
  kyc_id: string
  locker_customer_id: string
  allocation_id?: string
  
  document_type: KYCDocumentType
  document_category: KYCDocumentCategory
  document_number?: string
  document_name?: string
  
  issuing_authority?: string
  issue_date?: string
  expiry_date?: string
  is_expired: boolean
  
  document_file_path: string
  document_file_type?: string
  document_file_size?: number
  original_filename?: string
  
  verification_status: VerificationStatus
  verified_by?: string
  verification_date?: string
  verification_remarks?: string
  rejection_reason?: string
  
  kyc_compliance: boolean
  aml_checked: boolean
  aml_status?: string
  
  version_number: number
  is_latest_version: boolean
  is_mandatory: boolean
  
  upload_date: string
  remarks?: string
  created_at: string
  updated_at: string
}

export interface LockerNominee {
  id: string
  nominee_id: string
  locker_customer_id: string
  allocation_id: string
  
  nominee_sequence: number
  is_primary_nominee: boolean
  
  // Personal details
  title?: string
  full_name: string
  date_of_birth: string
  age?: number
  gender?: string
  relationship_with_customer: string
  
  // Contact
  mobile_number?: string
  email?: string
  
  // Address
  address_line1: string
  address_line2?: string
  city: string
  state: string
  pincode: string
  country: string
  
  // Identification
  id_proof_type: string
  id_proof_number: string
  id_proof_document_path?: string
  photo_path?: string
  
  // Share
  nominee_percentage: number
  
  // Minor details
  is_minor: boolean
  guardian_name?: string
  guardian_relationship?: string
  guardian_id_proof_type?: string
  guardian_id_proof_number?: string
  guardian_address?: string
  guardian_mobile?: string
  guardian_document_path?: string
  
  // Status
  status: string
  verification_status: VerificationStatus
  verified_by?: string
  verification_date?: string
  
  nomination_date: string
  nomination_form_path?: string
  nomination_accepted: boolean
  nomination_accepted_date?: string
  
  special_instructions?: string
  remarks?: string
  created_at: string
  updated_at: string
}

export interface LockerAuthorization {
  id: string
  authorization_id: string
  locker_customer_id: string
  allocation_id: string
  
  authorized_person_type: string
  authorized_person_name: string
  authorized_person_customer_id?: string
  
  // Contact
  mobile_number: string
  email?: string
  
  // Identification
  id_proof_type: string
  id_proof_number: string
  id_proof_document_path?: string
  
  // Address
  address: string
  city?: string
  state?: string
  pincode?: string
  
  // Authorization details
  authorization_type: AuthorizationType
  
  // Permissions
  can_deposit_items: boolean
  can_retrieve_items: boolean
  can_view_contents: boolean
  can_make_rent_payments: boolean
  can_renew_locker: boolean
  can_surrender_locker: boolean
  can_add_joint_holder: boolean
  can_change_nominee: boolean
  
  // Time restrictions
  authorization_valid_from: string
  authorization_valid_to?: string
  is_permanent: boolean
  access_days_allowed?: string
  access_time_from?: string
  access_time_to?: string
  
  // Legal documents
  authorization_document_type?: string
  authorization_document_path: string
  authorization_document_number?: string
  authorization_document_date?: string
  
  // Approval
  approval_status: ApprovalStatus
  approved_by?: string
  approval_date?: string
  approval_remarks?: string
  rejection_reason?: string
  
  // Status
  status: string
  signature_specimen_path?: string
  photo_path?: string
  signature_verified: boolean
  last_used_date?: string
  total_access_count: number
  
  special_conditions?: string
  remarks?: string
  created_at: string
  updated_at: string
}

export interface LockerRentStructure {
  id: string
  rent_structure_id: string
  branch_id?: string
  branch_name?: string
  locker_size: LockerSize
  location_type: string
  customer_category: CustomerCategory
  
  // Rent components
  base_rent_annual: number
  base_rent_semi_annual?: number
  base_rent_quarterly?: number
  base_rent_monthly?: number
  
  // Location premium
  location_premium_percentage: number
  location_premium_amount: number
  
  // Security deposit
  security_deposit_amount: number
  security_deposit_refundable: boolean
  
  // GST
  gst_applicable: boolean
  gst_rate: number
  gst_on_rent: boolean
  gst_on_deposit: boolean
  
  // Discounts
  discount_percentage: number
  discount_amount: number
  discount_reason?: string
  advance_payment_discount: number
  
  // Penalties
  late_payment_penalty_applicable: boolean
  late_payment_grace_days: number
  late_payment_penalty_percentage: number
  late_payment_penalty_flat_amount: number
  penalty_calculation_method: string
  
  // Other charges
  duplicate_key_charges: number
  locker_breaking_charges: number
  transfer_charges: number
  closure_charges: number
  
  // Limits
  minimum_rent_period_months: number
  maximum_rent_advance_years: number
  
  // Validity
  effective_from: string
  effective_to?: string
  is_active: boolean
  
  // Special rules
  rent_waiver_applicable: boolean
  rent_waiver_conditions?: string
  
  approved_by?: string
  approval_date?: string
  approval_remarks?: string
  version_number: number
  remarks?: string
  created_at: string
  updated_at: string
}

export interface RentCalculation {
  base_rent: number
  location_premium: number
  discount_amount: number
  subtotal: number
  gst_amount: number
  total_amount: number
  security_deposit: number
  total_payable: number
  rent_frequency: string
  period_months: number
  gst_rate: number
  discount_percentage: number
}

export interface CustomerAnalytics {
  total_customers: number
  by_category: Record<string, number>
  by_verification_status: Record<string, number>
  senior_citizens: number
  premium_customers: number
  kyc_pending: number
  kyc_completed: number
}

export interface JointHolderAnalytics {
  total_joint_accounts: number
  by_operation_mode: Record<string, number>
  active_joint_holders: number
  inactive_joint_holders: number
}

export interface NomineeAnalytics {
  total_nominees: number
  allocations_with_nominees: number
  allocations_without_nominees: number
  minor_nominees: number
  verified_nominees: number
  pending_verification: number
}


// ============================================
// Customer Management Service Methods
// ============================================

export const lockerCustomerService = {
  // Customer CRUD
  createCustomer: (data: Partial<LockerCustomer>) =>
    apiClient.post('/api/lockers/customers', data),
  
  getCustomer: (customerId: string) =>
    apiClient.get<LockerCustomer>(`/api/lockers/customers/${customerId}`),
  
  getCustomerCompleteProfile: (customerId: string) =>
    apiClient.get(`/api/lockers/customers/${customerId}/complete-profile`),
  
  updateCustomer: (customerId: string, data: Partial<LockerCustomer>) =>
    apiClient.put(`/api/lockers/customers/${customerId}`, data),
  
  verifyCustomer: (customerId: string, verificationStatus: VerificationStatus, remarks?: string) =>
    apiClient.post(`/api/lockers/customers/${customerId}/verify`, {
      verification_status: verificationStatus,
      remarks
    }),
  
  searchCustomers: (params: {
    search_query?: string
    customer_category?: CustomerCategory
    verification_status?: VerificationStatus
    status?: string
    is_senior_citizen?: boolean
    is_premium_customer?: boolean
    page?: number
    page_size?: number
  }) =>
    apiClient.post('/api/lockers/customers/search', params),
  
  // Joint Holder Management
  addJointHolder: (data: Partial<LockerJointHolder>) =>
    apiClient.post('/api/lockers/joint-holders', data),
  
  getJointHolder: (jointHolderId: string) =>
    apiClient.get<LockerJointHolder>(`/api/lockers/joint-holders/${jointHolderId}`),
  
  getAllocationJointHolders: (allocationId: string) =>
    apiClient.get<LockerJointHolder[]>(`/api/lockers/allocations/${allocationId}/joint-holders`),
  
  updateJointHolder: (jointHolderId: string, data: Partial<LockerJointHolder>) =>
    apiClient.put(`/api/lockers/joint-holders/${jointHolderId}`, data),
  
  deactivateJointHolder: (jointHolderId: string, reason: string) =>
    apiClient.post(`/api/lockers/joint-holders/${jointHolderId}/deactivate`, { reason }),
  
  // KYC Document Management
  uploadKYC: (data: Partial<LockerKYC>) =>
    apiClient.post('/api/lockers/kyc/upload', data),
  
  bulkUploadKYC: (lockerCustomerId: string, documents: Partial<LockerKYC>[]) =>
    apiClient.post('/api/lockers/kyc/bulk-upload', {
      locker_customer_id: lockerCustomerId,
      documents
    }),
  
  getKYCDocument: (kycId: string) =>
    apiClient.get<LockerKYC>(`/api/lockers/kyc/${kycId}`),
  
  getCustomerKYCDocuments: (lockerCustomerId: string) =>
    apiClient.get<LockerKYC[]>(`/api/lockers/customers/${lockerCustomerId}/kyc`),
  
  verifyKYCDocument: (
    kycId: string,
    verificationStatus: VerificationStatus,
    verificationRemarks?: string,
    rejectionReason?: string
  ) =>
    apiClient.post(`/api/lockers/kyc/${kycId}/verify`, {
      verification_status: verificationStatus,
      verification_remarks: verificationRemarks,
      rejection_reason: rejectionReason
    }),
  
  checkKYCCompliance: (lockerCustomerId: string) =>
    apiClient.get(`/api/lockers/customers/${lockerCustomerId}/kyc-compliance`),
  
  // Nominee Management
  addNominee: (data: Partial<LockerNominee>) =>
    apiClient.post('/api/lockers/nominees', data),
  
  getNominee: (nomineeId: string) =>
    apiClient.get<LockerNominee>(`/api/lockers/nominees/${nomineeId}`),
  
  getAllocationNominees: (allocationId: string) =>
    apiClient.get<LockerNominee[]>(`/api/lockers/allocations/${allocationId}/nominees`),
  
  updateNominee: (nomineeId: string, data: Partial<LockerNominee>) =>
    apiClient.put(`/api/lockers/nominees/${nomineeId}`, data),
  
  verifyNominee: (nomineeId: string, verificationStatus: VerificationStatus) =>
    apiClient.post(`/api/lockers/nominees/${nomineeId}/verify`, {
      verification_status: verificationStatus
    }),
  
  validateNomineePercentages: (allocationId: string) =>
    apiClient.get(`/api/lockers/allocations/${allocationId}/nominees/validate-percentages`),
  
  // Authorization Management
  createAuthorization: (data: Partial<LockerAuthorization>) =>
    apiClient.post('/api/lockers/authorizations', data),
  
  getAuthorization: (authId: string) =>
    apiClient.get<LockerAuthorization>(`/api/lockers/authorizations/${authId}`),
  
  getAllocationAuthorizations: (allocationId: string) =>
    apiClient.get<LockerAuthorization[]>(`/api/lockers/allocations/${allocationId}/authorizations`),
  
  updateAuthorization: (authId: string, data: Partial<LockerAuthorization>) =>
    apiClient.put(`/api/lockers/authorizations/${authId}`, data),
  
  approveAuthorization: (
    authId: string,
    approvalStatus: ApprovalStatus,
    approvalRemarks?: string,
    rejectionReason?: string
  ) =>
    apiClient.post(`/api/lockers/authorizations/${authId}/approve`, {
      approval_status: approvalStatus,
      approval_remarks: approvalRemarks,
      rejection_reason: rejectionReason
    }),
  
  revokeAuthorization: (authId: string, revocationReason: string, revocationDocumentPath?: string) =>
    apiClient.post(`/api/lockers/authorizations/${authId}/revoke`, {
      revocation_reason: revocationReason,
      revocation_document_path: revocationDocumentPath
    }),
  
  checkAuthorizationValidity: (authId: string) =>
    apiClient.get(`/api/lockers/authorizations/${authId}/check-validity`),
  
  // Rent Structure Management
  createRentStructure: (data: Partial<LockerRentStructure>) =>
    apiClient.post('/api/lockers/rent-structures', data),
  
  getRentStructure: (structureId: string) =>
    apiClient.get<LockerRentStructure>(`/api/lockers/rent-structures/${structureId}`),
  
  listRentStructures: (params?: {
    locker_size?: LockerSize
    customer_category?: CustomerCategory
    branch_id?: string
    is_active?: boolean
    page?: number
    page_size?: number
  }) =>
    apiClient.get('/api/lockers/rent-structures', { params }),
  
  updateRentStructure: (structureId: string, data: Partial<LockerRentStructure>) =>
    apiClient.put(`/api/lockers/rent-structures/${structureId}`, data),
  
  deactivateRentStructure: (structureId: string) =>
    apiClient.post(`/api/lockers/rent-structures/${structureId}/deactivate`),
  
  calculateRent: (params: {
    locker_size: LockerSize
    branch_id?: string
    customer_category?: CustomerCategory
    rent_frequency: string
    advance_payment?: boolean
    period_from: string
    period_to: string
  }) =>
    apiClient.post<RentCalculation>('/api/lockers/rent-structures/calculate-rent', params),
  
  getRentStructureComparison: (lockerSize: LockerSize) =>
    apiClient.get(`/api/lockers/rent-structures/comparison/${lockerSize}`),
  
  getPricingSummary: () =>
    apiClient.get('/api/lockers/rent-structures/pricing-summary'),
  
  // Analytics
  getCustomerAnalytics: () =>
    apiClient.get<CustomerAnalytics>('/api/lockers/analytics/customers'),
  
  getJointHolderAnalytics: () =>
    apiClient.get<JointHolderAnalytics>('/api/lockers/analytics/joint-holders'),
  
  getNomineeAnalytics: () =>
    apiClient.get<NomineeAnalytics>('/api/lockers/analytics/nominees'),
}

// Export everything together
export const lockerService = {
  ...lockerCustomerService,
  // ... existing locker service methods will be here
}


// ============================================
// Allocation Process Type Definitions
// ============================================

export enum ApplicationType {
  NEW = 'new',
  RENEWAL = 'renewal',
  TRANSFER = 'transfer',
  ADDITIONAL = 'additional'
}

export enum ApplicationStatus {
  SUBMITTED = 'submitted',
  UNDER_REVIEW = 'under_review',
  PENDING_DOCUMENTS = 'pending_documents',
  PENDING_APPROVAL = 'pending_approval',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  WAITING_LIST = 'waiting_list',
  ALLOCATED = 'allocated',
  CANCELLED = 'cancelled',
  EXPIRED = 'expired'
}

export enum ApplicationStage {
  DOCUMENT_VERIFICATION = 'document_verification',
  CREDIT_CHECK = 'credit_check',
  MANAGER_REVIEW = 'manager_review',
  FINAL_APPROVAL = 'final_approval',
  ALLOCATION = 'allocation'
}

export enum WaitingListStatus {
  ACTIVE = 'active',
  NOTIFIED = 'notified',
  ACCEPTED = 'accepted',
  DECLINED = 'declined',
  EXPIRED = 'expired',
  ALLOCATED = 'allocated',
  CANCELLED = 'cancelled'
}

export enum HandoverType {
  INITIAL_ISSUE = 'initial_issue',
  REPLACEMENT = 'replacement',
  DUPLICATE = 'duplicate',
  RETURN = 'return',
  SURRENDER = 'surrender'
}

export enum KeyType {
  PHYSICAL = 'physical',
  DIGITAL = 'digital'
}

export enum KeyStatus {
  ACTIVE = 'active',
  RETURNED = 'returned',
  LOST = 'lost',
  REPLACED = 'replaced',
  CANCELLED = 'cancelled'
}

export enum AgreementType {
  NEW = 'new',
  RENEWAL = 'renewal',
  MODIFICATION = 'modification',
  TRANSFER = 'transfer'
}

export enum AgreementStatus {
  DRAFT = 'draft',
  PENDING_SIGNATURE = 'pending_signature',
  PARTIALLY_SIGNED = 'partially_signed',
  EXECUTED = 'executed',
  ACTIVE = 'active',
  EXPIRED = 'expired',
  TERMINATED = 'terminated',
  RENEWED = 'renewed'
}

export enum SignatureType {
  PHYSICAL = 'physical',
  DIGITAL = 'digital',
  E_SIGN = 'e_sign'
}

export interface LockerApplication {
  id: string
  application_number: string
  customer_id: string
  locker_customer_id?: string
  branch_id: string
  application_date: string
  application_type: ApplicationType
  
  // Locker preferences
  preferred_locker_size: LockerSize
  alternate_size_1?: LockerSize
  alternate_size_2?: LockerSize
  preferred_location?: string
  preferred_locker_id?: string
  
  // Purpose
  purpose_of_locker: string
  purpose_details?: string
  estimated_value_of_contents?: number
  insurance_required: boolean
  insurance_coverage_amount?: number
  
  // Financial
  proposed_rent_frequency: string
  willing_to_pay_advance: boolean
  advance_payment_months: number
  
  // Priority factors
  is_existing_customer: boolean
  existing_customer_since?: string
  customer_category: CustomerCategory
  deposit_with_bank: number
  loan_accounts: number
  credit_score?: number
  priority_score: number
  priority_reason?: string
  
  // Status
  status: ApplicationStatus
  current_stage: ApplicationStage
  
  // Workflow tracking
  submitted_by?: string
  reviewed_by?: string
  review_date?: string
  review_remarks?: string
  approved_by?: string
  approval_date?: string
  approval_remarks?: string
  approval_level: number
  rejected_by?: string
  rejection_date?: string
  rejection_reason?: string
  
  // Waiting list
  added_to_waiting_list: boolean
  waiting_list_date?: string
  waiting_list_position?: number
  expected_availability_date?: string
  
  // Allocation
  allocated_locker_id?: string
  allocation_id?: string
  allocation_date?: string
  
  // Documents
  application_form_path?: string
  supporting_documents_path?: string
  kyc_verified: boolean
  kyc_verification_date?: string
  
  // Communication
  notification_sent: boolean
  last_notification_date?: string
  follow_up_required: boolean
  follow_up_date?: string
  
  // Validity
  application_valid_till?: string
  is_expired: boolean
  
  special_requirements?: string
  internal_notes?: string
  remarks?: string
  created_at: string
  updated_at: string
}

export interface LockerWaitingList {
  id: string
  waiting_list_id: string
  application_id: string
  customer_id: string
  branch_id: string
  
  added_date: string
  locker_size_requested: LockerSize
  position_in_queue: number
  
  // Priority
  priority_score: number
  priority_factors?: string
  base_priority: number
  existing_customer_bonus: number
  deposit_size_bonus: number
  senior_citizen_bonus: number
  staff_bonus: number
  waiting_time_bonus: number
  
  // Status
  status: WaitingListStatus
  
  // Notification
  notification_sent: boolean
  notification_sent_date?: string
  notification_method?: string
  response_deadline?: string
  customer_response?: string
  customer_response_date?: string
  
  // Offer details
  locker_offered_id?: string
  offer_made_date?: string
  offer_valid_till?: string
  offer_declined_reason?: string
  
  // Allocation
  allocated: boolean
  allocation_id?: string
  allocation_date?: string
  removed_date?: string
  removal_reason?: string
  
  // Estimated waiting
  estimated_wait_days?: number
  estimated_allocation_date?: string
  average_turnover_rate?: number
  
  // Preferences
  auto_allocate_enabled: boolean
  accept_alternate_size: boolean
  max_rent_willing?: number
  preferred_contact_method: string
  preferred_contact_time?: string
  contact_mobile?: string
  contact_email?: string
  
  special_requirements?: string
  remarks?: string
  created_at: string
  updated_at: string
}

export interface LockerKeyHandover {
  id: string
  handover_id: string
  key_register_number: string
  allocation_id: string
  locker_id: string
  customer_id: string
  
  handover_type: HandoverType
  handover_date: string
  
  // Customer key
  customer_key_number: string
  customer_key_type: KeyType
  customer_key_issued: boolean
  customer_key_issue_date?: string
  customer_key_returned: boolean
  customer_key_return_date?: string
  customer_key_condition?: string
  
  // Bank master key
  bank_key_number: string
  bank_key_location?: string
  bank_key_custodian?: string
  bank_key_status: string
  
  // Dual key
  requires_dual_key: boolean
  dual_key_policy?: string
  
  // Duplicate keys
  duplicate_key_issued: boolean
  duplicate_key_number?: string
  duplicate_key_reason?: string
  duplicate_key_charges: number
  duplicate_key_authorization?: string
  number_of_duplicate_keys: number
  duplicate_keys_list?: string
  
  // Recipient
  received_by: string
  received_by_relation: string
  received_by_id_proof: string
  received_by_id_number: string
  
  // Witnesses
  witness_1_name: string
  witness_1_employee_id: string
  witness_2_name?: string
  witness_2_employee_id?: string
  issued_by: string
  issued_by_name?: string
  
  // Security
  biometric_captured: boolean
  biometric_type?: string
  biometric_reference?: string
  recipient_photo_path?: string
  recipient_signature_path?: string
  
  // Testing
  key_tested: boolean
  key_working_condition?: string
  lock_tested: boolean
  lock_condition?: string
  
  // Lost key handling
  key_lost: boolean
  key_lost_date?: string
  key_lost_reported_date?: string
  fir_number?: string
  indemnity_bond_executed: boolean
  indemnity_bond_path?: string
  locker_breaking_required: boolean
  locker_breaking_date?: string
  locker_breaking_charges?: number
  
  // Deposit
  key_security_deposit: number
  deposit_refunded: boolean
  deposit_refund_date?: string
  deposit_refund_amount?: number
  
  // Acknowledgment
  acknowledgment_form_path?: string
  customer_acknowledgment: boolean
  acknowledgment_date?: string
  
  // Status
  status: KeyStatus
  
  special_instructions?: string
  remarks?: string
  created_at: string
  updated_at: string
}

export interface LockerAgreement {
  id: string
  agreement_number: string
  agreement_version: string
  allocation_id: string
  locker_id: string
  customer_id: string
  application_id?: string
  
  agreement_type: AgreementType
  parent_agreement_id?: string
  
  // Dates
  agreement_date: string
  agreement_start_date: string
  agreement_end_date: string
  agreement_duration_months: number
  
  // Template
  template_id?: string
  template_name?: string
  template_version?: string
  
  // Terms
  terms_and_conditions: string
  dos_and_donts: string
  bank_liability_clause: string
  insurance_clause?: string
  access_rules: string
  special_terms?: string
  additional_conditions?: string
  
  // Financial
  annual_rent: number
  security_deposit: number
  rent_frequency: string
  rent_escalation_clause?: string
  rent_escalation_percentage: number
  rent_escalation_frequency_years: number
  
  // Signatures
  joint_holder_signature_required: boolean
  customer_signature_path?: string
  customer_signed: boolean
  customer_signature_date?: string
  customer_signature_type?: SignatureType
  customer_digital_signature_id?: string
  customer_ip_address?: string
  
  joint_holder_1_signature_path?: string
  joint_holder_1_signed: boolean
  joint_holder_1_signature_date?: string
  
  joint_holder_2_signature_path?: string
  joint_holder_2_signed: boolean
  joint_holder_2_signature_date?: string
  
  bank_authorized_signatory: string
  bank_signature_path?: string
  bank_signed: boolean
  bank_signature_date?: string
  bank_official_stamp: boolean
  
  witness_1_name?: string
  witness_1_signature_path?: string
  witness_1_signature_date?: string
  witness_2_name?: string
  witness_2_signature_path?: string
  witness_2_signature_date?: string
  
  // Execution
  is_executed: boolean
  execution_date?: string
  execution_location?: string
  all_signatures_complete: boolean
  signatures_completed_date?: string
  
  // Document
  agreement_document_path: string
  agreement_document_type: string
  original_document_location?: string
  scanned_copy_path?: string
  agreement_file_size?: number
  
  // Stamp & notary
  stamp_paper_required: boolean
  stamp_paper_value?: number
  stamp_paper_number?: string
  stamp_paper_date?: string
  notarized: boolean
  notary_name?: string
  notary_registration_number?: string
  notary_date?: string
  
  // Status
  status: AgreementStatus
  
  // Renewal
  auto_renewal_enabled: boolean
  renewal_notice_period_days: number
  renewal_notice_sent: boolean
  renewal_notice_date?: string
  renewed: boolean
  renewed_agreement_id?: string
  renewal_date?: string
  
  // Termination
  terminated: boolean
  termination_date?: string
  termination_reason?: string
  termination_initiated_by?: string
  notice_period_days: number
  termination_notice_date?: string
  
  // Compliance
  kyc_verified_at_execution: boolean
  aml_check_done: boolean
  legal_review_done: boolean
  legal_reviewed_by?: string
  legal_review_date?: string
  
  // Amendments
  amendment_count: number
  last_amendment_date?: string
  amendment_details?: string
  
  // Communication
  customer_copy_sent: boolean
  customer_copy_sent_date?: string
  customer_copy_delivery_method?: string
  
  special_instructions?: string
  internal_notes?: string
  remarks?: string
  created_at: string
  updated_at: string
}

export interface ApplicationAnalytics {
  total_applications: number
  by_status: Record<string, number>
  by_type: Record<string, number>
  pending_review: number
  pending_approval: number
  approved_count: number
  rejected_count: number
  average_processing_days: number
}

export interface WaitingListAnalytics {
  total_waiting: number
  by_size: Record<string, number>
  by_branch: Record<string, number>
  average_wait_days: number
  longest_wait_days: number
  offers_made: number
  offers_accepted: number
  offers_declined: number
}

export interface KeyHandoverStatistics {
  total_handovers: number
  active_keys: number
  lost_keys: number
  duplicate_keys_issued: number
  keys_returned: number
  pending_returns: number
}

export interface AgreementStatistics {
  total_agreements: number
  by_status: Record<string, number>
  expiring_30_days: number
  expiring_60_days: number
  expiring_90_days: number
  pending_signatures: number
  fully_executed: number
  renewal_due: number
}


// ============================================
// Application Service Methods
// ============================================

export const applicationService = {
  // Create application
  createApplication: (data: Partial<LockerApplication>) =>
    apiClient.post<LockerApplication>('/lockers/applications', data),
  
  // Get application by ID
  getApplication: (applicationId: string) =>
    apiClient.get<LockerApplication>(`/lockers/applications/${applicationId}`),
  
  // Get application by number
  getApplicationByNumber: (applicationNumber: string) =>
    apiClient.get<LockerApplication>(`/lockers/applications/number/${applicationNumber}`),
  
  // List applications with filters
  listApplications: (filters: {
    customer_id?: string
    branch_id?: string
    application_type?: ApplicationType
    status?: ApplicationStatus
    current_stage?: ApplicationStage
    preferred_locker_size?: LockerSize
    application_date_from?: string
    application_date_to?: string
    page?: number
    page_size?: number
  }) =>
    apiClient.post('/lockers/applications/list', filters),
  
  // Update application
  updateApplication: (applicationId: string, data: Partial<LockerApplication>) =>
    apiClient.put<LockerApplication>(`/lockers/applications/${applicationId}`, data),
  
  // Review application
  reviewApplication: (applicationId: string, reviewData: {
    review_remarks: string
    kyc_verified?: boolean
    credit_check_done?: boolean
    move_to_stage?: ApplicationStage
  }) =>
    apiClient.post<LockerApplication>(`/lockers/applications/${applicationId}/review`, reviewData),
  
  // Approve or reject application
  approveApplication: (applicationId: string, approvalData: {
    approved: boolean
    approval_remarks?: string
    rejection_reason?: string
    add_to_waiting_list?: boolean
  }) =>
    apiClient.post<LockerApplication>(`/lockers/applications/${applicationId}/approve`, approvalData),
  
  // Allocate locker to application
  allocateLocker: (applicationId: string, allocationData: {
    locker_id: string
    allocation_date: string
    agreement_start_date: string
    agreement_end_date: string
    annual_rent: number
    security_deposit: number
  }) =>
    apiClient.post<LockerApplication>(`/lockers/applications/${applicationId}/allocate`, allocationData),
  
  // Cancel application
  cancelApplication: (applicationId: string, reason: string) =>
    apiClient.post<LockerApplication>(`/lockers/applications/${applicationId}/cancel`, null, {
      params: { reason }
    }),
  
  // Get pending approvals
  getPendingApprovals: (branchId?: string) =>
    apiClient.get<LockerApplication[]>('/lockers/applications/pending-approvals', {
      params: { branch_id: branchId }
    }),
  
  // Get customer applications
  getCustomerApplications: (customerId: string) =>
    apiClient.get<LockerApplication[]>(`/lockers/applications/customer/${customerId}`),
  
  // Get application history
  getApplicationHistory: (applicationId: string) =>
    apiClient.get<{ history: any[] }>(`/lockers/applications/${applicationId}/history`),
  
  // Get application analytics
  getAnalytics: (branchId?: string) =>
    apiClient.get<ApplicationAnalytics>('/lockers/applications/analytics', {
      params: { branch_id: branchId }
    })
}


// ============================================
// Waiting List Service Methods
// ============================================

export const waitingListService = {
  // Add to waiting list
  addToWaitingList: (data: Partial<LockerWaitingList>) =>
    apiClient.post<LockerWaitingList>('/lockers/waiting-list', data),
  
  // Get waiting list entry
  getWaitingListEntry: (entryId: string) =>
    apiClient.get<LockerWaitingList>(`/lockers/waiting-list/${entryId}`),
  
  // List waiting list entries
  listWaitingList: (filters: {
    branch_id?: string
    locker_size_requested?: LockerSize
    status?: WaitingListStatus
    min_priority_score?: number
    page?: number
    page_size?: number
  }) =>
    apiClient.post('/lockers/waiting-list/list', filters),
  
  // Update waiting list entry
  updateWaitingListEntry: (entryId: string, data: Partial<LockerWaitingList>) =>
    apiClient.put<LockerWaitingList>(`/lockers/waiting-list/${entryId}`, data),
  
  // Make locker offer
  makeOffer: (entryId: string, offerData: {
    locker_id: string
    offer_valid_days?: number
    notification_method?: string
  }) =>
    apiClient.post<LockerWaitingList>(`/lockers/waiting-list/${entryId}/make-offer`, offerData),
  
  // Record customer response
  recordCustomerResponse: (entryId: string, response: {
    accepted: boolean
    response_date: string
    declined_reason?: string
  }) =>
    apiClient.post<LockerWaitingList>(`/lockers/waiting-list/${entryId}/respond`, response),
  
  // Process allocation
  processAllocation: (entryId: string, allocationId: string) =>
    apiClient.post<LockerWaitingList>(`/lockers/waiting-list/${entryId}/allocate`, null, {
      params: { allocation_id: allocationId }
    }),
  
  // Remove from waiting list
  removeFromWaitingList: (entryId: string, reason: string) =>
    apiClient.delete<LockerWaitingList>(`/lockers/waiting-list/${entryId}`, {
      params: { reason }
    }),
  
  // Get next in queue
  getNextInQueue: (branchId: string, lockerSize: LockerSize) =>
    apiClient.get<LockerWaitingList>('/lockers/waiting-list/next-in-queue', {
      params: { branch_id: branchId, locker_size: lockerSize }
    }),
  
  // Get customer waiting entries
  getCustomerWaitingEntries: (customerId: string) =>
    apiClient.get<LockerWaitingList[]>(`/lockers/waiting-list/customer/${customerId}`),
  
  // Get waiting list analytics
  getAnalytics: (branchId?: string) =>
    apiClient.get<WaitingListAnalytics>('/lockers/waiting-list/analytics', {
      params: { branch_id: branchId }
    }),
  
  // Get waiting list statistics
  getStatistics: (branchId?: string) =>
    apiClient.get('/lockers/waiting-list/statistics', {
      params: { branch_id: branchId }
    })
}


// ============================================
// Key Handover Service Methods
// ============================================

export const keyHandoverService = {
  // Issue keys
  issueKeys: (data: Partial<LockerKeyHandover>) =>
    apiClient.post<LockerKeyHandover>('/lockers/key-handovers', data),
  
  // Get key handover
  getKeyHandover: (handoverId: string) =>
    apiClient.get<LockerKeyHandover>(`/lockers/key-handovers/${handoverId}`),
  
  // Get handover by allocation
  getHandoverByAllocation: (allocationId: string) =>
    apiClient.get<LockerKeyHandover>(`/lockers/key-handovers/allocation/${allocationId}`),
  
  // List key handovers
  listKeyHandovers: (filters: {
    allocation_id?: string
    locker_id?: string
    customer_id?: string
    handover_type?: HandoverType
    status?: KeyStatus
    key_lost?: boolean
    page?: number
    page_size?: number
  }) =>
    apiClient.post('/lockers/key-handovers/list', filters),
  
  // Update key handover
  updateKeyHandover: (handoverId: string, data: Partial<LockerKeyHandover>) =>
    apiClient.put<LockerKeyHandover>(`/lockers/key-handovers/${handoverId}`, data),
  
  // Return keys
  returnKeys: (handoverId: string, returnData: {
    return_date: string
    key_condition: string
    all_duplicate_keys_returned?: boolean
    remarks?: string
  }) =>
    apiClient.post<LockerKeyHandover>(`/lockers/key-handovers/${handoverId}/return`, returnData),
  
  // Report lost key
  reportLostKey: (handoverId: string, reportData: {
    key_lost_date: string
    fir_number?: string
    indemnity_bond_path: string
    duplicate_key_required?: boolean
    locker_breaking_required?: boolean
  }) =>
    apiClient.post<LockerKeyHandover>(`/lockers/key-handovers/${handoverId}/report-lost`, reportData),
  
  // Issue duplicate key
  issueDuplicateKey: (handoverId: string, reason: string, authorization: string) =>
    apiClient.post<LockerKeyHandover>(`/lockers/key-handovers/${handoverId}/issue-duplicate`, null, {
      params: { reason, authorization }
    }),
  
  // Get customer active keys
  getCustomerActiveKeys: (customerId: string) =>
    apiClient.get<LockerKeyHandover[]>(`/lockers/key-handovers/customer/${customerId}/active`),
  
  // Get lost keys pending action
  getLostKeysPendingAction: () =>
    apiClient.get<LockerKeyHandover[]>('/lockers/key-handovers/lost-keys/pending-action'),
  
  // Verify dual key availability
  verifyDualKeyAvailability: (lockerId: string) =>
    apiClient.get(`/lockers/key-handovers/locker/${lockerId}/verify-dual-key`),
  
  // Get key handover statistics
  getStatistics: (branchId?: string) =>
    apiClient.get<KeyHandoverStatistics>('/lockers/key-handovers/statistics', {
      params: { branch_id: branchId }
    })
}


// ============================================
// Agreement Service Methods
// ============================================

export const agreementService = {
  // Create agreement
  createAgreement: (data: Partial<LockerAgreement>) =>
    apiClient.post<LockerAgreement>('/lockers/agreements', data),
  
  // Get agreement by ID
  getAgreement: (agreementId: string) =>
    apiClient.get<LockerAgreement>(`/lockers/agreements/${agreementId}`),
  
  // Get agreement by number
  getAgreementByNumber: (agreementNumber: string) =>
    apiClient.get<LockerAgreement>(`/lockers/agreements/number/${agreementNumber}`),
  
  // Get agreement by allocation
  getAgreementByAllocation: (allocationId: string) =>
    apiClient.get<LockerAgreement>(`/lockers/agreements/allocation/${allocationId}`),
  
  // List agreements
  listAgreements: (filters: {
    allocation_id?: string
    customer_id?: string
    agreement_type?: AgreementType
    status?: AgreementStatus
    expiring_within_days?: number
    renewal_due?: boolean
    page?: number
    page_size?: number
  }) =>
    apiClient.post('/lockers/agreements/list', filters),
  
  // Update agreement
  updateAgreement: (agreementId: string, data: Partial<LockerAgreement>) =>
    apiClient.put<LockerAgreement>(`/lockers/agreements/${agreementId}`, data),
  
  // Add signature
  addSignature: (agreementId: string, signatureData: {
    signer_type: 'customer' | 'joint_holder_1' | 'joint_holder_2' | 'bank'
    signature_type: SignatureType
    signature_path: string
    signature_date: string
    digital_signature_id?: string
    ip_address?: string
  }) =>
    apiClient.post<LockerAgreement>(`/lockers/agreements/${agreementId}/sign`, signatureData),
  
  // Execute agreement
  executeAgreement: (agreementId: string, executionData: {
    execution_date: string
    execution_location: string
    stamp_paper_details?: any
    notary_details?: any
  }) =>
    apiClient.post<LockerAgreement>(`/lockers/agreements/${agreementId}/execute`, executionData),
  
  // Renew agreement
  renewAgreement: (agreementId: string, renewalData: {
    new_end_date: string
    annual_rent: number
    rent_escalation_applied?: boolean
    special_terms?: string
  }) =>
    apiClient.post<LockerAgreement>(`/lockers/agreements/${agreementId}/renew`, renewalData),
  
  // Terminate agreement
  terminateAgreement: (agreementId: string, terminationData: {
    termination_date: string
    termination_reason: string
    initiated_by: string
    notice_given?: boolean
    notice_date?: string
  }) =>
    apiClient.post<LockerAgreement>(`/lockers/agreements/${agreementId}/terminate`, terminationData),
  
  // Amend agreement
  amendAgreement: (agreementId: string, amendmentData: {
    amendment_details: string
    amendment_date: string
    amended_clauses: string[]
    requires_new_signatures?: boolean
  }) =>
    apiClient.post<LockerAgreement>(`/lockers/agreements/${agreementId}/amend`, amendmentData),
  
  // Get expiring agreements
  getExpiringAgreements: (days: number = 30) =>
    apiClient.get<LockerAgreement[]>('/lockers/agreements/expiring', {
      params: { days }
    }),
  
  // Get pending signatures
  getPendingSignatures: (branchId?: string) =>
    apiClient.get<LockerAgreement[]>('/lockers/agreements/pending-signatures', {
      params: { branch_id: branchId }
    }),
  
  // Get customer agreements
  getCustomerAgreements: (customerId: string) =>
    apiClient.get<LockerAgreement[]>(`/lockers/agreements/customer/${customerId}`),
  
  // Get agreement history
  getAgreementHistory: (allocationId: string) =>
    apiClient.get<LockerAgreement[]>(`/lockers/agreements/allocation/${allocationId}/history`),
  
  // Get agreement statistics
  getStatistics: (branchId?: string) =>
    apiClient.get<AgreementStatistics>('/lockers/agreements/statistics', {
      params: { branch_id: branchId }
    }),
  
  // Send renewal notices
  sendRenewalNotices: () =>
    apiClient.post('/lockers/agreements/send-renewal-notices')
}


// ============================================
// Export All Services
// ============================================

export const allocationProcessService = {
  ...applicationService,
  ...waitingListService,
  ...keyHandoverService,
  ...agreementService
}

// Re-export everything under lockerService namespace
export const completeLockerService = {
  ...lockerService,
  ...lockerCustomerService,
  ...allocationProcessService
}

    termination_reason: string
    termination_initiated_by: string
    notice_period_served?: boolean
  }) =>
    apiClient.post<LockerAgreement>(`/lockers/agreements/${agreementId}/terminate`, terminationData),
  
  // Amend agreement
  amendAgreement: (agreementId: string, amendmentData: {
    amendment_details: string
    amendment_reason: string
    amendment_document_path?: string
  }) =>
    apiClient.post<LockerAgreement>(`/lockers/agreements/${agreementId}/amend`, amendmentData),
  
  // Get expiring agreements
  getExpiringAgreements: (days: number = 30) =>
    apiClient.get<LockerAgreement[]>('/lockers/agreements/expiring', {
      params: { days }
    }),
  
  // Get pending signatures
  getPendingSignatures: (branchId?: string) =>
    apiClient.get<LockerAgreement[]>('/lockers/agreements/pending-signatures', {
      params: { branch_id: branchId }
    }),
  
  // Get customer agreements
  getCustomerAgreements: (customerId: string) =>
    apiClient.get<LockerAgreement[]>(`/lockers/agreements/customer/${customerId}`),
  
  // Get agreement history
  getAgreementHistory: (allocationId: string) =>
    apiClient.get<LockerAgreement[]>(`/lockers/agreements/allocation/${allocationId}/history`),
  
  // Get agreement statistics
  getStatistics: (branchId?: string) =>
    apiClient.get<AgreementStatistics>('/lockers/agreements/statistics', {
      params: { branch_id: branchId }
    }),
  
  // Send renewal notices
  sendRenewalNotices: () =>
    apiClient.post('/lockers/agreements/send-renewal-notices')
}


// ============================================
// Locker Operations Type Definitions
// ============================================

export enum AccessorType {
  CUSTOMER = 'customer',
  JOINT_HOLDER = 'joint_holder',
  NOMINEE = 'nominee',
  AUTHORIZED_PERSON = 'authorized_person',
  BANK_STAFF = 'bank_staff',
  LEGAL_HEIR = 'legal_heir',
  COURT_APPOINTED = 'court_appointed'
}

export enum AccessPurpose {
  DEPOSIT_ITEMS = 'deposit_items',
  RETRIEVE_ITEMS = 'retrieve_items',
  INSPECTION = 'inspection',
  INVENTORY_CHECK = 'inventory_check',
  EMERGENCY_ACCESS = 'emergency_access',
  MAINTENANCE = 'maintenance',
  LEGAL_REQUIREMENT = 'legal_requirement',
  OTHER = 'other'
}

export enum VerificationMethod {
  BIOMETRIC = 'biometric',
  PHOTO = 'photo',
  SIGNATURE = 'signature',
  ID_PROOF = 'id_proof',
  PASSWORD = 'password',
  DUAL_AUTH = 'dual_auth'
}

export interface LockerAccessLog {
  id: string
  access_log_number: string
  locker_id: string
  allocation_id: string
  customer_id: string
  
  // Access details
  access_date: string
  access_time: string
  entry_time: string
  exit_time?: string
  duration_minutes?: number
  
  // Accessor information
  accessor_type: AccessorType
  accessor_name: string
  accessor_id: string
  accessor_relationship?: string
  accessor_mobile?: string
  accessor_id_proof_type?: string
  accessor_id_proof_number?: string
  
  // Purpose
  purpose: AccessPurpose
  purpose_details?: string
  items_deposited?: string
  items_retrieved?: string
  declaration_provided: boolean
  declaration_document_path?: string
  
  // Authentication
  verification_method: VerificationMethod
  biometric_verified: boolean
  biometric_data?: string
  photo_captured: boolean
  photo_path?: string
  signature_captured: boolean
  signature_path?: string
  id_verification_done: boolean
  
  // Dual authentication
  bank_official_name: string
  bank_official_employee_id: string
  bank_official_signature_path?: string
  accompanied_by_bank_official: boolean
  escort_service_used: boolean
  
  // Operating hours
  within_operating_hours: boolean
  special_permission_required: boolean
  special_permission_granted: boolean
  special_permission_by?: string
  after_hours_access: boolean
  holiday_access: boolean
  emergency_access: boolean
  emergency_authorization?: string
  
  // Security
  dual_key_used: boolean
  customer_key_verified: boolean
  bank_key_verified: boolean
  locker_opened_successfully: boolean
  any_discrepancy: boolean
  discrepancy_details?: string
  
  // Status
  access_completed: boolean
  completion_time?: string
  
  remarks?: string
  created_at: string
  updated_at: string
}

export interface OperatingHours {
  day: string
  is_open: boolean
  opening_time?: string
  closing_time?: string
  lunch_break_start?: string
  lunch_break_end?: string
  special_note?: string
}

export interface FacilityStatus {
  is_open: boolean
  current_time: string
  reason?: string
  next_opening_time?: string
  next_opening_date?: string
}

export interface SpecialAccessRequest {
  id: string
  request_number: string
  customer_id: string
  locker_id: string
  allocation_id: string
  request_type: 'holiday' | 'after_hours'
  request_date: string
  access_date: string
  access_time?: string
  reason: string
  status: 'pending' | 'approved' | 'rejected'
  approved_by?: string
  approval_date?: string
  approval_remarks?: string
  rejection_reason?: string
  created_at: string
}

export interface EmergencyProtocol {
  requires_manager_approval: boolean
  requires_security_officer: boolean
  requires_dual_authentication: boolean
  minimum_authorization_level: string
  documentation_required: string[]
  notification_required: boolean
  incident_report_required: boolean
  special_procedures: string[]
}

export interface EscortRequirements {
  escort_required: boolean
  escort_mandatory_for: string[]
  minimum_designation: string
  escort_responsibilities: string[]
  exceptions: string[]
}

export interface AccessStatistics {
  total_accesses: number
  by_accessor_type: Record<string, number>
  by_purpose: Record<string, number>
  by_month: Array<{ month: string; count: number }>
  average_duration_minutes: number
  biometric_verification_rate: number
  after_hours_accesses: number
  emergency_accesses: number
  peak_hours: Array<{ hour: number; count: number }>
}

export interface AfterHoursStatistics {
  total_after_hours_requests: number
  approved_requests: number
  rejected_requests: number
  approval_rate: number
  by_reason: Record<string, number>
  by_customer: Array<{ customer_id: string; count: number }>
  average_approval_time_hours: number
}

export interface PeakHoursAnalysis {
  hourly_distribution: Array<{ hour: number; count: number; percentage: number }>
  daily_distribution: Array<{ day: string; count: number; percentage: number }>
  peak_hour: number
  peak_day: string
  recommended_staffing: Array<{
    time_slot: string
    recommended_staff: number
    current_average_traffic: number
  }>
}

export interface HolidayCalendar {
  date: string
  holiday_name: string
  recurring: boolean
  special_access_allowed: boolean
}

export interface OperatingHoursConfig {
  weekday_start: string
  weekday_end: string
  saturday_start: string
  saturday_end: string
  sunday_open: boolean
  lunch_start?: string
  lunch_end?: string
  last_updated: string
  updated_by: string
}


// ============================================
// Access Management Service Methods
// ============================================

export const accessService = {
  // Request locker access
  requestAccess: (data: {
    locker_id: string
    allocation_id: string
    customer_id: string
    access_date: string
    access_time: string
    accessor_type: AccessorType
    accessor_name: string
    accessor_id: string
    accessor_relationship?: string
    purpose: AccessPurpose
    purpose_details?: string
    bank_official_name: string
    bank_official_employee_id: string
    special_permission_required?: boolean
    emergency_access?: boolean
  }) =>
    apiClient.post<LockerAccessLog>('/lockers/access/request', data),
  
  // Complete access (record exit)
  completeAccess: (accessLogId: string, exitTime: string, remarks?: string) =>
    apiClient.patch<LockerAccessLog>(`/lockers/access/${accessLogId}/complete`, {
      exit_time: exitTime,
      remarks
    }),
  
  // Verify biometric
  verifyBiometric: (accessLogId: string, biometricData: string, verified: boolean) =>
    apiClient.patch<LockerAccessLog>(`/lockers/access/${accessLogId}/verify-biometric`, {
      biometric_data: biometricData,
      verified
    }),
  
  // Capture photo
  capturePhoto: (accessLogId: string, photoPath: string) =>
    apiClient.patch<LockerAccessLog>(`/lockers/access/${accessLogId}/capture-photo`, {
      photo_path: photoPath
    }),
  
  // Capture signature
  captureSignature: (accessLogId: string, signaturePath: string) =>
    apiClient.patch<LockerAccessLog>(`/lockers/access/${accessLogId}/capture-signature`, {
      signature_path: signaturePath
    }),
  
  // List access logs with filters
  listAccessLogs: (params?: {
    locker_id?: string
    allocation_id?: string
    customer_id?: string
    access_date_from?: string
    access_date_to?: string
    accessor_type?: AccessorType
    purpose?: AccessPurpose
    emergency_only?: boolean
    skip?: number
    limit?: number
  }) =>
    apiClient.get('/lockers/access/logs', { params }),
  
  // Get access log by ID
  getAccessLog: (accessLogId: string) =>
    apiClient.get<LockerAccessLog>(`/lockers/access/logs/${accessLogId}`),
  
  // Get active access sessions
  getActiveSessions: (lockerId?: string) =>
    apiClient.get<{ active_sessions: LockerAccessLog[] }>('/lockers/access/active-sessions', {
      params: { locker_id: lockerId }
    }),
  
  // Get customer access history
  getCustomerAccessHistory: (customerId: string, limit: number = 50) =>
    apiClient.get<{ access_history: LockerAccessLog[] }>(
      `/lockers/access/customer/${customerId}/history`,
      { params: { limit } }
    ),
  
  // Get access statistics
  getAccessStatistics: (dateFrom?: string, dateTo?: string) =>
    apiClient.get<AccessStatistics>('/lockers/access/statistics', {
      params: { date_from: dateFrom, date_to: dateTo }
    }),
  
  // Get access register report
  getAccessRegisterReport: (dateFrom: string, dateTo: string, lockerId?: string) =>
    apiClient.get('/lockers/access/register/report', {
      params: { date_from: dateFrom, date_to: dateTo, locker_id: lockerId }
    })
}


// ============================================
// Operating Hours Service Methods
// ============================================

export const operatingHoursService = {
  // Check facility status
  checkFacilityStatus: () =>
    apiClient.get<FacilityStatus>('/lockers/operations/facility-status'),
  
  // Get operating hours for date
  getOperatingHours: (forDate?: string) =>
    apiClient.get<OperatingHours>('/lockers/operations/hours', {
      params: { for_date: forDate }
    }),
  
  // Get weekly schedule
  getWeeklySchedule: () =>
    apiClient.get<{ weekly_schedule: OperatingHours[] }>('/lockers/operations/hours/weekly'),
  
  // Request holiday access
  requestHolidayAccess: (data: {
    customer_id: string
    locker_id: string
    allocation_id: string
    access_date: string
    reason: string
  }) =>
    apiClient.post<SpecialAccessRequest>('/lockers/operations/special-access/holiday', data),
  
  // Request after-hours access
  requestAfterHoursAccess: (data: {
    customer_id: string
    locker_id: string
    allocation_id: string
    access_date: string
    access_time: string
    reason: string
  }) =>
    apiClient.post<SpecialAccessRequest>('/lockers/operations/special-access/after-hours', data),
  
  // Approve special access request
  approveSpecialAccess: (requestId: string, approved: boolean, approvalRemarks?: string, rejectionReason?: string) =>
    apiClient.post('/lockers/operations/special-access/approve', {
      request_id: requestId,
      approved,
      approval_remarks: approvalRemarks,
      rejection_reason: rejectionReason
    }),
  
  // Get emergency protocol
  getEmergencyProtocol: () =>
    apiClient.get<EmergencyProtocol>('/lockers/operations/emergency-protocol'),
  
  // Get escort requirements
  getEscortRequirements: (accessType?: string) =>
    apiClient.get<EscortRequirements>('/lockers/operations/escort-requirements', {
      params: { access_type: accessType }
    }),
  
  // Get after-hours statistics
  getAfterHoursStatistics: (dateFrom?: string, dateTo?: string) =>
    apiClient.get<AfterHoursStatistics>('/lockers/operations/statistics/after-hours', {
      params: { date_from: dateFrom, date_to: dateTo }
    }),
  
  // Get peak hours analysis
  getPeakHoursAnalysis: (dateFrom?: string, dateTo?: string) =>
    apiClient.get<PeakHoursAnalysis>('/lockers/operations/statistics/peak-hours', {
      params: { date_from: dateFrom, date_to: dateTo }
    }),
  
  // Update operating hours config
  updateOperatingHours: (config: {
    weekday_start?: string
    weekday_end?: string
    saturday_start?: string
    saturday_end?: string
    lunch_start?: string
    lunch_end?: string
  }) =>
    apiClient.put<OperatingHoursConfig>('/lockers/operations/hours/update', null, {
      params: config
    }),
  
  // Get holiday calendar
  getHolidayCalendar: (year?: number) =>
    apiClient.get<{ holidays: HolidayCalendar[] }>('/lockers/operations/holidays', {
      params: { year }
    }),
  
  // Add holiday
  addHoliday: (holidayDate: string, holidayName: string, recurring: boolean = false) =>
    apiClient.post<HolidayCalendar>('/lockers/operations/holidays', {
      holiday_date: holidayDate,
      holiday_name: holidayName,
      recurring
    })
}


// ============================================
// Export Combined Service
// ============================================

export const lockerManagementService = {
  // Master and basic operations
  ...lockerService,
  
  // Customer management
  customer: lockerCustomerService,
  
  // Allocation process
  application: applicationService,
  waitingList: waitingListService,
  keyHandover: keyHandoverService,
  agreement: agreementService,
  
  // Operations
  access: accessService,
  operatingHours: operatingHoursService
}

// Default export
export default lockerManagementService


// ============================================
// Rent Collection Type Definitions
// ============================================

export interface RentCalculation {
  allocation_id: string
  year?: number
  base_rent: number
  gst_rate: number
  gst_amount: number
  total_annual_rent: number
  rent_frequency: string
  last_payment_date?: string
  next_due_date?: string
}

export interface ProrataRentCalculation {
  allocation_id: string
  from_date: string
  to_date: string
  number_of_days: number
  annual_rent: number
  prorata_rent: number
  gst_rate: number
  gst_amount: number
  total_amount: number
}

export interface AdvanceRentCalculation {
  allocation_id: string
  number_of_years: number
  annual_rent: number
  total_base_rent: number
  discount_rate: number
  discount_amount: number
  rent_after_discount: number
  gst_rate: number
  gst_amount: number
  total_amount: number
  valid_upto: string
}

export interface RentReceipt {
  receipt_number: string
  receipt_date: string
  customer_id: string
  allocation_id: string
  locker_number?: string
  locker_size?: string
  payment_details: {
    payment_type: string
    payment_mode: string
    payment_date: string
    transaction_reference?: string
  }
  rent_breakdown: {
    rent_amount: number
    gst_amount: number
    penalty_amount: number
    late_fee_amount: number
    total_amount: number
  }
  period: {
    from_date?: string
    to_date?: string
  }
  remarks?: string
}

export interface OverdueAllocation {
  allocation_id: string
  allocation_number: string
  customer_id: string
  locker_id: string
  rent_due_date: string
  days_overdue: number
  annual_rent: number
  outstanding_rent: number
  last_payment_date?: string
}

export interface RentCollectionSummary {
  period: {
    start_date: string
    end_date: string
  }
  summary: {
    total_payments: number
    total_collected: number
    rent_amount: number
    gst_amount: number
    penalty_amount: number
    late_fee_amount: number
  }
  by_payment_mode: Record<string, number>
  by_payment_type: Record<string, number>
}

export interface UpcomingDue {
  allocation_id: string
  allocation_number: string
  customer_id: string
  locker_id: string
  rent_due_date: string
  days_until_due: number
  annual_rent: number
  auto_renewal: boolean
}


// ============================================
// Rent Arrears Type Definitions
// ============================================

export interface PenaltyCalculation {
  overdue_days: number
  penalty_rate: number
  penalty_amount: number
  late_fee: number
  total_penalty: number
  overdue_amount: number
  total_payable: number
}

export interface AllocationArrears {
  allocation_id: string
  has_arrears: boolean
  rent_due_date?: string
  overdue_days?: number
  overdue_amount?: number
  penalty_details?: PenaltyCalculation
  total_outstanding?: number
  notices_sent?: number
  last_notice_date?: string
  last_notice_type?: string
  message?: string
}

export interface BreakingEligibility {
  allocation_id: string
  eligible: boolean
  overdue_days?: number
  years_overdue?: number
  three_year_threshold?: number
  days_until_eligible?: number
  all_notices_sent?: boolean
  missing_notices?: string[]
  total_outstanding?: number
  reason?: string
}

export interface ArrearsSummary {
  total_overdue_allocations: number
  total_outstanding_amount: number
  total_penalties: number
  grand_total: number
  by_overdue_period: {
    '0-30_days': {
      count: number
      allocations: any[]
    }
    '31-60_days': {
      count: number
      allocations: any[]
    }
    '61-90_days': {
      count: number
      allocations: any[]
    }
    '91-180_days': {
      count: number
      allocations: any[]
    }
    '181-365_days': {
      count: number
      allocations: any[]
    }
    '1-2_years': {
      count: number
      allocations: any[]
    }
    '2-3_years': {
      count: number
      allocations: any[]
    }
    '3+_years': {
      count: number
      allocations: any[]
      breaking_eligible: number
    }
  }
}

export interface NoticeRecord {
  notice_id: string
  notice_number: string
  allocation_id: string
  notice_type: string
  notice_date: string
  total_amount: number
  status: string
}


// ============================================
// Rent Collection Service Methods
// ============================================

export const rentCollectionService = {
  // Calculate annual rent
  calculateAnnualRent: (allocationId: string, forYear?: number) =>
    apiClient.get<RentCalculation>(`/lockers/rent/calculate-annual/${allocationId}`, {
      params: { for_year: forYear }
    }),

  // Calculate pro-rata rent
  calculateProrataRent: (allocationId: string, fromDate: string, toDate: string) =>
    apiClient.post<ProrataRentCalculation>('/lockers/rent/calculate-prorata', null, {
      params: { allocation_id: allocationId, from_date: fromDate, to_date: toDate }
    }),

  // Calculate advance rent
  calculateAdvanceRent: (allocationId: string, numberOfYears: number) =>
    apiClient.post<AdvanceRentCalculation>('/lockers/rent/calculate-advance', null, {
      params: { allocation_id: allocationId, number_of_years: numberOfYears }
    }),

  // Collect rent
  collectRent: (allocationId: string, paymentData: any) =>
    apiClient.post('/lockers/rent/collect', paymentData, {
      params: { allocation_id: allocationId }
    }),

  // Auto-debit rent
  autoDebitRent: (allocationId: string, customerAccountId: string) =>
    apiClient.post(`/lockers/rent/auto-debit/${allocationId}`, null, {
      params: { customer_account_id: customerAccountId }
    }),

  // Send rent reminder
  sendRentReminder: (allocationId: string, reminderType: string, daysBeforeDue: number) =>
    apiClient.post('/lockers/rent/reminder/send', null, {
      params: { allocation_id: allocationId, reminder_type: reminderType, days_before_due: daysBeforeDue }
    }),

  // Send bulk reminders
  sendBulkReminders: (reminderType: string, daysBeforeDue: number) =>
    apiClient.post('/lockers/rent/reminder/bulk-send', null, {
      params: { reminder_type: reminderType, days_before_due: daysBeforeDue }
    }),

  // Generate rent receipt
  generateRentReceipt: (paymentId: string) =>
    apiClient.get<RentReceipt>(`/lockers/rent/receipt/${paymentId}`),

  // Get overdue allocations
  getOverdueAllocations: (branchId?: string) =>
    apiClient.get<{ overdue_allocations: OverdueAllocation[] }>('/lockers/rent/overdue', {
      params: { branch_id: branchId }
    }),

  // Get rent collection summary
  getRentCollectionSummary: (startDate?: string, endDate?: string, branchId?: string) =>
    apiClient.get<RentCollectionSummary>('/lockers/rent/collection-summary', {
      params: { start_date: startDate, end_date: endDate, branch_id: branchId }
    }),

  // Get upcoming due dates
  getUpcomingDueDates: (daysAhead: number = 30, branchId?: string) =>
    apiClient.get<{ upcoming_due: UpcomingDue[] }>('/lockers/rent/upcoming-due', {
      params: { days_ahead: daysAhead, branch_id: branchId }
    })
}


// ============================================
// Rent Arrears Service Methods
// ============================================

export const rentArrearsService = {
  // Calculate penalty
  calculatePenalty: (allocationId: string, overdueDays: number, overdueAmount: number) =>
    apiClient.post<PenaltyCalculation>('/lockers/arrears/calculate-penalty', null, {
      params: { allocation_id: allocationId, overdue_days: overdueDays, overdue_amount: overdueAmount }
    }),

  // Get allocation arrears
  getAllocationArrears: (allocationId: string) =>
    apiClient.get<AllocationArrears>(`/lockers/arrears/${allocationId}`),

  // Send overdue notification
  sendOverdueNotification: (allocationId: string, notificationType: string = 'first_reminder') =>
    apiClient.post<NoticeRecord>('/lockers/arrears/send-notification', null, {
      params: { allocation_id: allocationId, notification_type: notificationType }
    }),

  // Send final notice
  sendFinalNotice: (allocationId: string) =>
    apiClient.post<NoticeRecord>(`/lockers/arrears/send-final-notice/${allocationId}`),

  // Send legal notice
  sendLegalNotice: (allocationId: string) =>
    apiClient.post<NoticeRecord>(`/lockers/arrears/send-legal-notice/${allocationId}`),

  // Check breaking eligibility
  checkBreakingEligibility: (allocationId: string) =>
    apiClient.get<BreakingEligibility>(`/lockers/arrears/breaking-eligibility/${allocationId}`),

  // Initiate breaking procedure
  initiateBreakingProcedure: (allocationId: string, authorizedBy: string, witnesses: string[]) =>
    apiClient.post('/lockers/arrears/initiate-breaking', null, {
      params: { allocation_id: allocationId, authorized_by: authorizedBy, witnesses }
    }),

  // Get arrears summary
  getArrearsSummary: (branchId?: string) =>
    apiClient.get<ArrearsSummary>('/lockers/arrears/summary', {
      params: { branch_id: branchId }
    }),

  // Get breaking eligible lockers
  getBreakingEligibleLockers: (branchId?: string) =>
    apiClient.get<{ breaking_eligible: any[] }>('/lockers/arrears/breaking-eligible', {
      params: { branch_id: branchId }
    })
}


// ============================================
// Export Updated Combined Service
// ============================================

export const lockerManagementService = {
  // Master and basic operations
  ...lockerService,
  
  // Customer management
  customer: lockerCustomerService,
  
  // Allocation process
  application: applicationService,
  waitingList: waitingListService,
  keyHandover: keyHandoverService,
  agreement: agreementService,
  
  // Operations
  access: accessService,
  operatingHours: operatingHoursService,
  
  // Rent Collection
  rentCollection: rentCollectionService,
  rentArrears: rentArrearsService
}

// Default export
export default lockerManagementService


// ============================================
// Breaking & Surrender Type Definitions
// ============================================

export enum BreakingReason {
  NON_PAYMENT = 'non_payment',
  DEATH_OF_HOLDER = 'death_of_holder',
  COURT_ORDER = 'court_order',
  SUSPICIOUS_ACTIVITY = 'suspicious_activity',
  EMERGENCY = 'emergency',
  STRUCTURAL_DAMAGE = 'structural_damage',
  UNCLAIMED_LOCKER = 'unclaimed_locker',
  OTHER = 'other'
}

export enum BreakingStatus {
  AUTHORIZED = 'authorized',
  INITIATED = 'initiated',
  POLICE_INTIMATED = 'police_intimated',
  VIDEOGRAPHY_DONE = 'videography_done',
  INVENTORY_PREPARED = 'inventory_prepared',
  VALUATION_DONE = 'valuation_done',
  CONTENTS_STORED = 'contents_stored',
  CHARGES_CALCULATED = 'charges_calculated',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled'
}

export enum SurrenderReason {
  RELOCATION = 'relocation',
  FINANCIAL_CONSTRAINTS = 'financial_constraints',
  NO_LONGER_REQUIRED = 'no_longer_required',
  SWITCHING_BANK = 'switching_bank',
  DISSATISFACTION = 'dissatisfaction',
  DEATH_OF_HOLDER = 'death_of_holder',
  OTHER = 'other'
}

export enum SurrenderStatus {
  APPLICATION_SUBMITTED = 'application_submitted',
  UNDER_REVIEW = 'under_review',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  DUES_CLEARED = 'dues_cleared',
  KEYS_RETURNED = 'keys_returned',
  INSPECTION_DONE = 'inspection_done',
  REFUND_PROCESSED = 'refund_processed',
  CERTIFICATE_ISSUED = 'certificate_issued',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled'
}

export interface InventoryItem {
  item_number: number
  description: string
  quantity: number
  estimated_value?: number
  condition?: string
  photo_reference?: string
  remarks?: string
}

export interface BreakingWitness {
  name: string
  employee_id?: string
  designation?: string
  signature_path?: string
}

export interface BreakingRecord {
  id: string
  breaking_number: string
  allocation_id: string
  locker_id: string
  customer_id: string
  branch_id: string
  
  // Reason & authorization
  breaking_reason: BreakingReason
  reason_details: string
  
  // Authorization
  authorization_required: boolean
  authorized_by_branch_manager: string
  branch_manager_approval_date: string
  authorized_by_regional_head: string
  regional_head_approval_date: string
  authorization_document_path?: string
  
  // Legal notice
  legal_notice_sent: boolean
  legal_notice_date?: string
  legal_notice_document_path?: string
  notice_period_days?: number
  notice_expiry_date?: string
  
  // Police intimation
  police_intimation_required: boolean
  police_station?: string
  police_intimation_date?: string
  police_reference_number?: string
  police_officer_name?: string
  police_document_path?: string
  
  // Witnesses
  witness_1: BreakingWitness
  witness_2: BreakingWitness
  witness_3?: BreakingWitness
  
  // Breaking details
  breaking_scheduled_date: string
  breaking_actual_date?: string
  breaking_time?: string
  breaking_location: string
  
  // Videography
  videography_done: boolean
  videography_start_time?: string
  videography_end_time?: string
  videography_duration?: number
  video_file_paths?: string[]
  video_storage_location?: string
  videographer_name?: string
  videographer_signature?: string
  
  // Inventory
  inventory_prepared: boolean
  inventory_date?: string
  inventory_items: InventoryItem[]
  total_items_count: number
  inventory_document_path?: string
  inventory_prepared_by?: string
  inventory_verified_by?: string
  
  // Valuation
  valuation_required: boolean
  valuation_done: boolean
  valuation_date?: string
  valuer_name?: string
  valuer_license_number?: string
  total_estimated_value?: number
  valuation_report_path?: string
  high_value_items_present: boolean
  
  // Content storage
  contents_stored: boolean
  storage_date?: string
  storage_location: string
  storage_vault_number?: string
  storage_packet_number?: string
  storage_seal_number?: string
  storage_receipt_path?: string
  storage_custodian_name?: string
  storage_custodian_signature?: string
  
  // Charges
  breaking_charges: number
  lock_replacement_charges: number
  videography_charges: number
  valuation_charges: number
  storage_charges_per_month: number
  legal_charges: number
  other_charges: number
  gst_rate: number
  gst_amount: number
  total_charges: number
  charges_document_path?: string
  
  // Notification
  customer_notified: boolean
  notification_date?: string
  notification_method?: string
  notification_document_path?: string
  
  // Legal documentation
  breaking_certificate_issued: boolean
  certificate_number?: string
  certificate_date?: string
  certificate_path?: string
  
  // Status
  status: BreakingStatus
  completion_date?: string
  
  // Follow-up
  customer_claim_pending: boolean
  customer_claim_date?: string
  contents_released: boolean
  contents_release_date?: string
  release_authorization_path?: string
  
  special_instructions?: string
  remarks?: string
  created_at: string
  updated_at: string
}

export interface SurrenderRecord {
  id: string
  surrender_number: string
  allocation_id: string
  locker_id: string
  customer_id: string
  branch_id: string
  
  // Application details
  application_date: string
  surrender_reason: SurrenderReason
  reason_details: string
  
  // Eligibility
  eligibility_checked: boolean
  eligibility_check_date?: string
  is_eligible: boolean
  ineligibility_reasons?: string[]
  
  // Planned surrender date
  requested_surrender_date: string
  expected_completion_date?: string
  
  // Approval
  approval_required: boolean
  approved: boolean
  approved_by?: string
  approval_date?: string
  approval_remarks?: string
  rejected_reason?: string
  
  // Dues clearance
  outstanding_rent: number
  outstanding_penalties: number
  outstanding_charges: number
  total_outstanding: number
  dues_cleared: boolean
  dues_clearance_date?: string
  payment_receipt_number?: string
  payment_receipt_path?: string
  
  // Key return
  customer_key_returned: boolean
  customer_key_return_date?: string
  customer_key_condition?: string
  bank_key_verified: boolean
  all_duplicate_keys_returned: boolean
  duplicate_keys_count?: number
  key_return_acknowledgment_path?: string
  keys_verified_by?: string
  
  // Locker inspection
  inspection_done: boolean
  inspection_date?: string
  inspected_by: string
  inspection_checklist_completed: boolean
  
  // Damage assessment
  damage_found: boolean
  damage_type?: string
  damage_description?: string
  damage_photos?: string[]
  damage_repair_cost?: number
  damage_assessment_report_path?: string
  
  // Cleanliness
  locker_cleaned: boolean
  cleaning_satisfactory: boolean
  cleaning_charges?: number
  
  // Lock condition
  lock_working: boolean
  lock_damaged: boolean
  lock_replacement_required: boolean
  lock_replacement_cost?: number
  
  // Security deposit refund
  security_deposit_amount: number
  damage_deductions: number
  outstanding_dues_deductions: number
  cleaning_charges_deductions: number
  other_deductions: number
  total_deductions: number
  refundable_amount: number
  
  refund_processed: boolean
  refund_processing_date?: string
  refund_mode?: string
  refund_reference_number?: string
  refund_account_number?: string
  refund_status?: string
  refund_completion_date?: string
  
  // Closure certificate
  certificate_issued: boolean
  certificate_number?: string
  certificate_date?: string
  certificate_path?: string
  certificate_issued_by?: string
  
  // Final settlement
  final_settlement_calculated: boolean
  final_settlement_amount: number
  settlement_paid: boolean
  settlement_payment_date?: string
  settlement_receipt_path?: string
  
  // No objection certificate
  noc_issued: boolean
  noc_number?: string
  noc_date?: string
  noc_path?: string
  
  // Locker status update
  locker_released_for_allocation: boolean
  locker_release_date?: string
  locker_made_available: boolean
  
  // Status
  status: SurrenderStatus
  completion_date?: string
  actual_surrender_date?: string
  
  // Communication
  acknowledgment_sent: boolean
  acknowledgment_date?: string
  acknowledgment_method?: string
  
  special_instructions?: string
  internal_notes?: string
  remarks?: string
  created_at: string
  updated_at: string
}

export interface BreakingAuthorization {
  is_authorized: boolean
  authorization_reasons: string[]
  legal_notice_required: boolean
  police_intimation_required: boolean
  minimum_witnesses_required: number
  estimated_days_to_complete: number
  authorization_checklist: {
    item: string
    required: boolean
    completed: boolean
  }[]
}

export interface SurrenderEligibility {
  is_eligible: boolean
  eligibility_reasons: string[]
  ineligibility_reasons: string[]
  outstanding_dues: number
  pending_documents: string[]
  estimated_refund_amount: number
  estimated_processing_days: number
  checklist: {
    item: string
    required: boolean
    completed: boolean
  }[]
}

export interface FinalSettlement {
  security_deposit: number
  outstanding_rent: number
  outstanding_penalties: number
  damage_charges: number
  cleaning_charges: number
  other_charges: number
  total_deductions: number
  refundable_amount: number
  payment_due_to_customer: number
  payment_due_to_bank: number
  net_settlement_amount: number
  settlement_breakdown: Array<{
    description: string
    amount: number
    type: 'credit' | 'debit'
  }>
}

export interface BreakingStatistics {
  total_breakings: number
  by_reason: Record<string, number>
  by_status: Record<string, number>
  by_branch: Record<string, number>
  average_days_to_complete: number
  pending_breakings: number
  completed_this_month: number
  completed_this_year: number
  total_charges_collected: number
  contents_in_custody: number
  unclaimed_contents: number
}

export interface SurrenderStatistics {
  total_surrenders: number
  by_reason: Record<string, number>
  by_status: Record<string, number>
  by_branch: Record<string, number>
  average_days_to_complete: number
  pending_approvals: number
  in_progress: number
  completed_this_month: number
  completed_this_year: number
  total_refunds_processed: number
  average_refund_amount: number
  lockers_released: number
}


// ============================================
// Breaking Service Methods
// ============================================

export const breakingService = {
  // Check breaking authorization
  checkBreakingAuthorization: (allocationId: string) =>
    apiClient.get<BreakingAuthorization>(`/lockers/breaking/${allocationId}/check-authorization`),
  
  // Initiate breaking
  initiateBreaking: (data: {
    allocation_id: string
    locker_id: string
    customer_id: string
    branch_id: string
    breaking_reason: BreakingReason
    reason_details: string
    authorized_by_branch_manager: string
    branch_manager_approval_date: string
    authorized_by_regional_head: string
    regional_head_approval_date: string
    legal_notice_sent?: boolean
    police_intimation_required?: boolean
    witness_1: BreakingWitness
    witness_2: BreakingWitness
    breaking_scheduled_date: string
  }) =>
    apiClient.post<BreakingRecord>('/lockers/breaking/initiate', data),
  
  // Record videography
  recordVideography: (breakingId: string, data: {
    videography_start_time: string
    videography_end_time: string
    video_file_paths: string[]
    videographer_name: string
    videographer_signature?: string
  }) =>
    apiClient.post<BreakingRecord>(`/lockers/breaking/${breakingId}/videography`, data),
  
  // Prepare inventory
  prepareInventory: (breakingId: string, data: {
    inventory_date: string
    inventory_items: InventoryItem[]
    inventory_prepared_by: string
    inventory_verified_by: string
  }) =>
    apiClient.post<BreakingRecord>(`/lockers/breaking/${breakingId}/inventory`, data),
  
  // Conduct valuation
  conductValuation: (breakingId: string, data: {
    valuation_date: string
    valuer_name: string
    valuer_license_number: string
    total_estimated_value: number
    valuation_report_path: string
    high_value_items_present: boolean
  }) =>
    apiClient.post<BreakingRecord>(`/lockers/breaking/${breakingId}/valuation`, data),
  
  // Store contents
  storeContents: (breakingId: string, data: {
    storage_date: string
    storage_location: string
    storage_vault_number?: string
    storage_packet_number: string
    storage_seal_number: string
    storage_custodian_name: string
  }) =>
    apiClient.post<BreakingRecord>(`/lockers/breaking/${breakingId}/storage`, data),
  
  // Calculate charges
  calculateBreakingCharges: (breakingId: string, data: {
    breaking_charges: number
    lock_replacement_charges: number
    videography_charges: number
    valuation_charges?: number
    storage_charges_per_month: number
    legal_charges?: number
    other_charges?: number
  }) =>
    apiClient.post<BreakingRecord>(`/lockers/breaking/${breakingId}/calculate-charges`, data),
  
  // Complete breaking
  completeBreaking: (breakingId: string, data: {
    completion_date: string
    certificate_number: string
    customer_notified: boolean
    notification_method?: string
  }) =>
    apiClient.post<BreakingRecord>(`/lockers/breaking/${breakingId}/complete`, data),
  
  // Get breaking record
  getBreakingRecord: (breakingId: string) =>
    apiClient.get<BreakingRecord>(`/lockers/breaking/${breakingId}`),
  
  // Get breaking by allocation
  getBreakingByAllocation: (allocationId: string) =>
    apiClient.get<BreakingRecord>(`/lockers/breaking/allocation/${allocationId}`),
  
  // List breaking records
  listBreakingRecords: (params?: {
    branch_id?: string
    reason?: BreakingReason
    status?: BreakingStatus
    date_from?: string
    date_to?: string
    skip?: number
    limit?: number
  }) =>
    apiClient.get<{
      records: BreakingRecord[]
      total: number
      skip: number
      limit: number
    }>('/lockers/breaking/records', { params }),
  
  // Get breaking statistics
  getStatistics: (branchId?: string, year?: number) =>
    apiClient.get<BreakingStatistics>('/lockers/breaking/statistics', {
      params: { branch_id: branchId, year }
    }),
  
  // Get breaking records pending action
  getPendingAction: (branchId?: string) =>
    apiClient.get<BreakingRecord[]>('/lockers/breaking/pending-action', {
      params: { branch_id: branchId }
    })
}


// ============================================
// Surrender Service Methods
// ============================================

export const surrenderService = {
  // Check surrender eligibility
  checkSurrenderEligibility: (allocationId: string) =>
    apiClient.get<SurrenderEligibility>(`/lockers/surrender/${allocationId}/check-eligibility`),
  
  // Submit surrender application
  submitApplication: (data: {
    allocation_id: string
    locker_id: string
    customer_id: string
    branch_id: string
    application_date: string
    surrender_reason: SurrenderReason
    reason_details: string
    requested_surrender_date: string
  }) =>
    apiClient.post<SurrenderRecord>('/lockers/surrender/submit-application', data),
  
  // Approve surrender application
  approveApplication: (surrenderId: string, data: {
    approved: boolean
    approval_remarks?: string
    rejected_reason?: string
  }) =>
    apiClient.post<SurrenderRecord>(`/lockers/surrender/${surrenderId}/approve`, data),
  
  // Clear dues
  clearDues: (surrenderId: string, data: {
    payment_receipt_number: string
    payment_receipt_path: string
    total_amount_paid: number
  }) =>
    apiClient.post<SurrenderRecord>(`/lockers/surrender/${surrenderId}/clear-dues`, data),
  
  // Return keys
  returnKeys: (surrenderId: string, data: {
    customer_key_return_date: string
    customer_key_condition: string
    all_duplicate_keys_returned: boolean
    duplicate_keys_count?: number
    keys_verified_by: string
  }) =>
    apiClient.post<SurrenderRecord>(`/lockers/surrender/${surrenderId}/return-keys`, data),
  
  // Conduct inspection
  conductInspection: (surrenderId: string, data: {
    inspection_date: string
    inspected_by: string
    damage_found: boolean
    damage_type?: string
    damage_description?: string
    damage_repair_cost?: number
    damage_photos?: string[]
    locker_cleaned: boolean
    lock_working: boolean
  }) =>
    apiClient.post<SurrenderRecord>(`/lockers/surrender/${surrenderId}/inspection`, data),
  
  // Process refund
  processRefund: (surrenderId: string, data: {
    refund_mode: string
    refund_account_number?: string
    refund_reference_number: string
    refund_processing_date: string
  }) =>
    apiClient.post<SurrenderRecord>(`/lockers/surrender/${surrenderId}/process-refund`, data),
  
  // Issue closure certificate
  issueCertificate: (surrenderId: string, data: {
    certificate_number: string
    certificate_date: string
    certificate_path: string
    certificate_issued_by: string
  }) =>
    apiClient.post<SurrenderRecord>(`/lockers/surrender/${surrenderId}/issue-certificate`, data),
  
  // Complete surrender
  completeSurrender: (surrenderId: string, data: {
    completion_date: string
    locker_made_available: boolean
  }) =>
    apiClient.post<SurrenderRecord>(`/lockers/surrender/${surrenderId}/complete`, data),
  
  // Calculate final settlement
  calculateFinalSettlement: (surrenderId: string) =>
    apiClient.post<FinalSettlement>(`/lockers/surrender/${surrenderId}/calculate-settlement`),
  
  // Get surrender record
  getSurrenderRecord: (surrenderId: string) =>
    apiClient.get<SurrenderRecord>(`/lockers/surrender/${surrenderId}`),
  
  // Get surrender by allocation
  getSurrenderByAllocation: (allocationId: string) =>
    apiClient.get<SurrenderRecord>(`/lockers/surrender/allocation/${allocationId}`),
  
  // List surrender records
  listSurrenderRecords: (params?: {
    branch_id?: string
    status?: SurrenderStatus
    reason?: SurrenderReason
    date_from?: string
    date_to?: string
    skip?: number
    limit?: number
  }) =>
    apiClient.get<{
      records: SurrenderRecord[]
      total: number
      skip: number
      limit: number
    }>('/lockers/surrender/records', { params }),
  
  // Get surrender statistics
  getStatistics: (branchId?: string, year?: number) =>
    apiClient.get<SurrenderStatistics>('/lockers/surrender/statistics', {
      params: { branch_id: branchId, year }
    }),
  
  // Get pending approvals
  getPendingApprovals: (branchId?: string) =>
    apiClient.get<SurrenderRecord[]>('/lockers/surrender/pending-approval', {
      params: { branch_id: branchId }
    }),
  
  // Get in-progress surrenders
  getInProgress: (branchId?: string) =>
    apiClient.get<SurrenderRecord[]>('/lockers/surrender/in-progress', {
      params: { branch_id: branchId }
    })
}


// ============================================
// Export Complete Locker Service with Breaking & Surrender
// ============================================

export const fullLockerService = {
  ...lockerService,
  ...lockerCustomerService,
  ...applicationService,
  ...waitingListService,
  ...keyHandoverService,
  ...agreementService,
  ...breakingService,
  ...surrenderService
}


// ============================================
// Locker Maintenance Type Definitions
// ============================================

export enum MaintenanceType {
  LOCK_SERVICING = 'lock_servicing',
  KEY_DUPLICATION = 'key_duplication',
  LOCKER_CLEANING = 'locker_cleaning',
  VAULT_MAINTENANCE = 'vault_maintenance',
  FIRE_PROTECTION_CHECK = 'fire_protection_check',
  LOCK_JAMMING = 'lock_jamming',
  KEY_LOST = 'key_lost',
  LOCK_REPLACEMENT = 'lock_replacement',
  MASTER_KEY_REGENERATION = 'master_key_regeneration',
  LOCKER_REPAIR = 'locker_repair',
  OTHER = 'other'
}

export enum MaintenanceStatus {
  SCHEDULED = 'scheduled',
  IN_PROGRESS = 'in_progress',
  ON_HOLD = 'on_hold',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled',
  FAILED = 'failed'
}

export enum MaintenancePriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  URGENT = 'urgent',
  EMERGENCY = 'emergency'
}

export enum MaintenanceCategory {
  PREVENTIVE = 'preventive',
  BREAKDOWN = 'breakdown',
  EMERGENCY = 'emergency'
}

export enum CleaningType {
  REGULAR = 'regular',
  DEEP_CLEANING = 'deep_cleaning',
  SANITIZATION = 'sanitization'
}

export enum LockJammingCause {
  RUST = 'rust',
  FOREIGN_OBJECT = 'foreign_object',
  MECHANICAL_FAULT = 'mechanical_fault',
  WEAR_AND_TEAR = 'wear_and_tear',
  CUSTOMER_MISUSE = 'customer_misuse',
  UNKNOWN = 'unknown'
}

export enum KeyReplacementAction {
  DUPLICATE = 'duplicate',
  REPLACEMENT = 'replacement'
}

export enum RecurringFrequency {
  MONTHLY = 'monthly',
  QUARTERLY = 'quarterly',
  SEMI_ANNUAL = 'semi_annual',
  ANNUAL = 'annual'
}

export interface MaintenanceRecord {
  id: string
  maintenance_number: string
  locker_id: string
  branch_id: string
  
  // Type and category
  maintenance_type: MaintenanceType
  maintenance_category: MaintenanceCategory
  priority: MaintenancePriority
  
  // Scheduling
  scheduled_date: string
  scheduled_time?: string
  started_date?: string
  completed_date?: string
  
  // Recurring maintenance
  is_recurring: boolean
  recurring_frequency?: RecurringFrequency
  next_maintenance_due_date?: string
  
  // Assignment
  assigned_to: string
  assigned_to_name?: string
  assigned_date?: string
  
  // Lock servicing details
  lock_condition_before?: string
  lock_serviced: boolean
  lubrication_done: boolean
  parts_replaced: boolean
  replaced_parts_list?: string[]
  lock_tested_after_servicing: boolean
  lock_condition_after?: string
  
  // Key duplication details
  number_of_keys_duplicated?: number
  key_type_duplicated?: string
  key_storage_location?: string
  
  // Cleaning details
  cleaning_type?: CleaningType
  areas_cleaned?: string[]
  cleaning_materials_used?: string[]
  sanitization_done: boolean
  
  // Vault maintenance details
  humidity_level_before?: number
  humidity_level_after?: number
  dehumidifier_checked: boolean
  dehumidifier_condition?: string
  ventilation_checked: boolean
  fire_system_checked: boolean
  
  // Fire protection system
  fire_extinguisher_checked: boolean
  fire_extinguisher_expiry_date?: string
  smoke_detector_tested: boolean
  smoke_detector_working: boolean
  sprinkler_system_tested: boolean
  sprinkler_system_working: boolean
  
  // Lock jamming resolution
  jamming_cause?: LockJammingCause
  jamming_resolution_steps?: string[]
  lock_repaired: boolean
  lock_replaced_due_to_jamming: boolean
  
  // Lost key handling
  key_lost_by_customer: boolean
  fir_details?: string
  indemnity_bond_collected: boolean
  indemnity_bond_path?: string
  key_replacement_action?: KeyReplacementAction
  new_key_number?: string
  
  // Lock replacement
  old_lock_number?: string
  old_lock_condition?: string
  new_lock_number?: string
  new_lock_type?: string
  lock_installation_date?: string
  keys_issued_count?: number
  customer_notified_of_replacement: boolean
  
  // Master key regeneration
  master_key_compromised: boolean
  authorization_for_regeneration?: string
  new_master_key_number?: string
  all_affected_lockers?: string[]
  customer_keys_retained: boolean
  
  // Locker repair
  damage_type?: string
  damage_description?: string
  damage_assessment_report_path?: string
  repair_materials_used?: string[]
  before_repair_photos?: string[]
  after_repair_photos?: string[]
  
  // Cost tracking
  labor_cost: number
  material_cost: number
  external_service_cost: number
  total_maintenance_cost: number
  
  // Customer charges (if customer fault)
  customer_charged: boolean
  customer_charge_reason?: string
  customer_charge_amount: number
  customer_charge_gst_amount: number
  customer_total_charge: number
  customer_charge_paid: boolean
  customer_charge_payment_date?: string
  
  // Quality check
  quality_check_done: boolean
  quality_check_by?: string
  quality_check_passed: boolean
  quality_check_remarks?: string
  
  // Customer satisfaction
  customer_satisfaction_rating?: number
  customer_satisfaction_feedback?: string
  customer_complaint_resolved: boolean
  
  // Response time tracking
  reported_time?: string
  response_time_minutes?: number
  resolution_time_minutes?: number
  
  // Completion
  completion_certificate_path?: string
  
  // Status
  status: MaintenanceStatus
  cancellation_reason?: string
  failure_reason?: string
  
  // Locker status impact
  locker_temporarily_blocked: boolean
  locker_block_start_date?: string
  locker_block_end_date?: string
  customer_access_restricted: boolean
  
  // Notes
  description?: string
  findings?: string
  action_taken?: string
  recommendations?: string
  special_instructions?: string
  remarks?: string
  created_at: string
  updated_at: string
}

export interface MaintenanceStatistics {
  // Overall counts
  total_maintenance: number
  preventive_maintenance: number
  breakdown_maintenance: number
  emergency_maintenance: number
  
  // Status breakdown
  scheduled: number
  in_progress: number
  completed: number
  cancelled: number
  
  // Priority breakdown
  low_priority: number
  medium_priority: number
  high_priority: number
  urgent_priority: number
  emergency_priority: number
  
  // Type breakdown
  by_type: Record<string, number>
  
  // Upcoming and overdue
  upcoming_7_days: number
  upcoming_30_days: number
  overdue: number
  
  // Cost tracking
  total_cost: number
  average_cost_per_maintenance: number
  preventive_cost: number
  breakdown_cost: number
  customer_charges_collected: number
  
  // Performance metrics
  average_response_time_minutes: number
  average_resolution_time_minutes: number
  quality_check_pass_rate: number
  average_customer_satisfaction: number
  
  // Frequency analysis
  by_month: Array<{ month: string; count: number; cost: number }>
  by_branch: Array<{ branch_id: string; count: number; cost: number }>
  
  // Trending
  maintenance_trend: 'increasing' | 'decreasing' | 'stable'
  most_common_issue: string
  most_costly_issue: string
}


// ============================================
// Maintenance Service Methods
// ============================================

export const maintenanceService = {
  // Schedule preventive maintenance
  schedulePreventiveMaintenance: (data: {
    locker_id: string
    branch_id: string
    maintenance_type: MaintenanceType
    scheduled_date: string
    scheduled_time?: string
    is_recurring?: boolean
    recurring_frequency?: RecurringFrequency
    assigned_to: string
    description?: string
  }) =>
    apiClient.post<MaintenanceRecord>('/lockers/maintenance/schedule', data),
  
  // Report breakdown maintenance
  reportBreakdown: (data: {
    locker_id: string
    branch_id: string
    maintenance_type: MaintenanceType
    priority: MaintenancePriority
    description: string
    customer_reported?: boolean
    customer_id?: string
    assigned_to: string
  }) =>
    apiClient.post<MaintenanceRecord>('/lockers/maintenance/report-breakdown', data),
  
  // Perform lock servicing
  performLockServicing: (maintenanceId: string, data: {
    lock_condition_before: string
    lubrication_done: boolean
    parts_replaced: boolean
    replaced_parts_list?: string[]
    lock_tested_after_servicing: boolean
    lock_condition_after: string
    action_taken: string
  }) =>
    apiClient.post<MaintenanceRecord>(`/lockers/maintenance/${maintenanceId}/lock-servicing`, data),
  
  // Perform key duplication
  performKeyDuplication: (maintenanceId: string, data: {
    number_of_keys_duplicated: number
    key_type_duplicated: string
    key_storage_location: string
    action_taken: string
  }) =>
    apiClient.post<MaintenanceRecord>(`/lockers/maintenance/${maintenanceId}/key-duplication`, data),
  
  // Perform cleaning
  performCleaning: (maintenanceId: string, data: {
    cleaning_type: CleaningType
    areas_cleaned: string[]
    cleaning_materials_used: string[]
    sanitization_done: boolean
    action_taken: string
  }) =>
    apiClient.post<MaintenanceRecord>(`/lockers/maintenance/${maintenanceId}/cleaning`, data),
  
  // Perform vault maintenance
  performVaultMaintenance: (maintenanceId: string, data: {
    humidity_level_before?: number
    humidity_level_after?: number
    dehumidifier_checked: boolean
    dehumidifier_condition?: string
    ventilation_checked: boolean
    action_taken: string
  }) =>
    apiClient.post<MaintenanceRecord>(`/lockers/maintenance/${maintenanceId}/vault-maintenance`, data),
  
  // Check fire protection system
  checkFireProtectionSystem: (maintenanceId: string, data: {
    fire_extinguisher_checked: boolean
    fire_extinguisher_expiry_date?: string
    smoke_detector_tested: boolean
    smoke_detector_working: boolean
    sprinkler_system_tested: boolean
    sprinkler_system_working: boolean
    action_taken: string
  }) =>
    apiClient.post<MaintenanceRecord>(`/lockers/maintenance/${maintenanceId}/fire-check`, data),
  
  // Resolve lock jamming
  resolveLockJamming: (maintenanceId: string, data: {
    jamming_cause: LockJammingCause
    jamming_resolution_steps: string[]
    lock_repaired: boolean
    lock_replaced_due_to_jamming?: boolean
    action_taken: string
  }) =>
    apiClient.post<MaintenanceRecord>(`/lockers/maintenance/${maintenanceId}/resolve-jamming`, data),
  
  // Handle lost key
  handleLostKey: (maintenanceId: string, data: {
    fir_details: string
    indemnity_bond_collected: boolean
    indemnity_bond_path?: string
    key_replacement_action: KeyReplacementAction
    new_key_number?: string
    customer_charge_amount?: number
    action_taken: string
  }) =>
    apiClient.post<MaintenanceRecord>(`/lockers/maintenance/${maintenanceId}/handle-lost-key`, data),
  
  // Replace lock
  replaceLock: (maintenanceId: string, data: {
    old_lock_number: string
    old_lock_condition: string
    new_lock_number: string
    new_lock_type: string
    lock_installation_date: string
    keys_issued_count: number
    customer_notified_of_replacement: boolean
    action_taken: string
  }) =>
    apiClient.post<MaintenanceRecord>(`/lockers/maintenance/${maintenanceId}/replace-lock`, data),
  
  // Regenerate master key
  regenerateMasterKey: (maintenanceId: string, data: {
    authorization_for_regeneration: string
    new_master_key_number: string
    all_affected_lockers: string[]
    customer_keys_retained: boolean
    action_taken: string
  }) =>
    apiClient.post<MaintenanceRecord>(`/lockers/maintenance/${maintenanceId}/regenerate-master-key`, data),
  
  // Repair locker
  repairLocker: (maintenanceId: string, data: {
    damage_type: string
    damage_description: string
    damage_assessment_report_path?: string
    repair_materials_used: string[]
    before_repair_photos?: string[]
    after_repair_photos?: string[]
    customer_charged?: boolean
    customer_charge_reason?: string
    customer_charge_amount?: number
    action_taken: string
  }) =>
    apiClient.post<MaintenanceRecord>(`/lockers/maintenance/${maintenanceId}/repair`, data),
  
  // Complete maintenance
  completeMaintenance: (maintenanceId: string, data: {
    completed_date: string
    quality_check_done: boolean
    quality_check_by?: string
    quality_check_passed: boolean
    quality_check_remarks?: string
    customer_satisfaction_rating?: number
    customer_satisfaction_feedback?: string
    recommendations?: string
    completion_certificate_path?: string
  }) =>
    apiClient.post<MaintenanceRecord>(`/lockers/maintenance/${maintenanceId}/complete`, data),
  
  // Get maintenance record
  getMaintenanceRecord: (maintenanceId: string) =>
    apiClient.get<MaintenanceRecord>(`/lockers/maintenance/${maintenanceId}`),
  
  // Get maintenance by locker
  getMaintenanceByLocker: (lockerId: string) =>
    apiClient.get<{ maintenance_records: MaintenanceRecord[] }>(`/lockers/maintenance/locker/${lockerId}`),
  
  // List maintenance records
  listMaintenanceRecords: (params?: {
    locker_id?: string
    maintenance_type?: MaintenanceType
    status?: MaintenanceStatus
    priority?: MaintenancePriority
    scheduled_date_from?: string
    scheduled_date_to?: string
    skip?: number
    limit?: number
  }) =>
    apiClient.get<{
      records: MaintenanceRecord[]
      total: number
      skip: number
      limit: number
    }>('/lockers/maintenance/records', { params }),
  
  // Get upcoming maintenance
  getUpcomingMaintenance: (daysAhead: number = 30, branchId?: string) =>
    apiClient.get<{ upcoming_maintenance: MaintenanceRecord[] }>('/lockers/maintenance/upcoming', {
      params: { days_ahead: daysAhead, branch_id: branchId }
    }),
  
  // Get overdue maintenance
  getOverdueMaintenance: (branchId?: string) =>
    apiClient.get<{ overdue_maintenance: MaintenanceRecord[] }>('/lockers/maintenance/overdue', {
      params: { branch_id: branchId }
    }),
  
  // Get pending breakdowns
  getPendingBreakdowns: (branchId?: string) =>
    apiClient.get<{ pending_breakdowns: MaintenanceRecord[] }>('/lockers/maintenance/breakdowns', {
      params: { branch_id: branchId }
    }),
  
  // Get maintenance statistics
  getStatistics: (branchId?: string, year?: number) =>
    apiClient.get<MaintenanceStatistics>('/lockers/maintenance/statistics', {
      params: { branch_id: branchId, year }
    })
}


// ============================================
// Export Complete Locker Service with Maintenance
// ============================================

export const completeLockerManagementService = {
  ...lockerService,
  ...lockerCustomerService,
  ...applicationService,
  ...waitingListService,
  ...keyHandoverService,
  ...agreementService,
  ...accessService,
  ...operatingHoursService,
  ...rentCollectionService,
  ...rentArrearsService,
  ...breakingService,
  ...surrenderService,
  ...maintenanceService
}

// Export as default
export default completeLockerManagementService


// ============================================
// Safety & Security Module Types
// ============================================

export enum VaultAccessType {
  REGULAR_OPERATION = 'regular_operation',
  MAINTENANCE = 'maintenance',
  EMERGENCY = 'emergency',
  AUDIT = 'audit',
  INCIDENT_RESPONSE = 'incident_response'
}

export enum SecurityEventType {
  VAULT_OPENED = 'vault_opened',
  VAULT_CLOSED = 'vault_closed',
  UNAUTHORIZED_ACCESS_ATTEMPT = 'unauthorized_access_attempt',
  ALARM_TRIGGERED = 'alarm_triggered',
  CCTV_OFFLINE = 'cctv_offline',
  DUAL_CUSTODY_VIOLATION = 'dual_custody_violation',
  TIME_LOCK_OVERRIDE = 'time_lock_override',
  SUSPICIOUS_ACTIVITY = 'suspicious_activity'
}

export enum SecurityEventSeverity {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
  EMERGENCY = 'emergency'
}

export enum InsuranceType {
  BANK_COVERAGE = 'bank_coverage',
  CUSTOMER_OPTIONAL = 'customer_optional',
  COMPREHENSIVE = 'comprehensive',
  THIRD_PARTY = 'third_party'
}

export enum InsuranceStatus {
  ACTIVE = 'active',
  EXPIRED = 'expired',
  CANCELLED = 'cancelled',
  PENDING_RENEWAL = 'pending_renewal',
  SUSPENDED = 'suspended'
}

export enum IncidentType {
  THEFT = 'theft',
  BURGLARY = 'burglary',
  FIRE = 'fire',
  WATER_DAMAGE = 'water_damage',
  FLOOD = 'flood',
  EARTHQUAKE = 'earthquake',
  NATURAL_CALAMITY = 'natural_calamity',
  UNAUTHORIZED_ACCESS = 'unauthorized_access',
  VANDALISM = 'vandalism',
  TECHNICAL_FAILURE = 'technical_failure',
  OTHER = 'other'
}

export enum IncidentSeverity {
  MINOR = 'minor',
  MODERATE = 'moderate',
  MAJOR = 'major',
  CRITICAL = 'critical',
  CATASTROPHIC = 'catastrophic'
}

export enum IncidentStatus {
  REPORTED = 'reported',
  UNDER_INVESTIGATION = 'under_investigation',
  EVIDENCE_COLLECTED = 'evidence_collected',
  REPORTED_TO_AUTHORITIES = 'reported_to_authorities',
  CLAIM_FILED = 'claim_filed',
  COMPENSATION_PROCESSED = 'compensation_processed',
  CLOSED = 'closed'
}

export enum CompensationStatus {
  PENDING_ASSESSMENT = 'pending_assessment',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  PAID = 'paid'
}

export interface VaultAccessRecord {
  id: string
  tenant_id: string
  branch_id: string
  access_type: VaultAccessType
  official_1_id: string
  official_2_id: string
  purpose: string
  opened_at: string
  closed_at?: string
  time_lock_override: boolean
  override_reason?: string
  notes?: string
  created_by: string
  created_at: string
}

export interface SecurityEvent {
  id: string
  tenant_id: string
  branch_id: string
  event_type: SecurityEventType
  severity: SecurityEventSeverity
  description: string
  officials_involved: string[]
  additional_data?: any
  event_timestamp: string
  logged_by: string
}

export interface InsurancePolicy {
  id: string
  tenant_id: string
  policy_number: string
  policy_type: InsuranceType
  locker_id?: string
  customer_id?: string
  insurer_name: string
  coverage_amount: number
  premium_amount: number
  start_date: string
  end_date: string
  status: InsuranceStatus
  terms_conditions?: string
  created_at: string
  created_by: string
}

export interface InsuranceClaim {
  id: string
  claim_number: string
  policy_id: string
  incident_id: string
  claim_amount: number
  claim_description: string
  supporting_documents: string[]
  filed_date: string
  status: string
  filed_by: string
}

export interface SecurityIncident {
  id: string
  tenant_id: string
  incident_number: string
  incident_type: IncidentType
  severity: IncidentSeverity
  branch_id: string
  affected_lockers: string[]
  incident_date: string
  description: string
  reported_by: string
  reported_at: string
  status: IncidentStatus
  rbi_notified: boolean
  police_notified: boolean
  investigation_findings?: string
  evidence_collected?: string[]
  root_cause?: string
  recommendations?: string
}

export interface Compensation {
  id: string
  incident_id: string
  customer_id: string
  locker_id: string
  compensation_amount: number
  compensation_type: string
  assessment_date: string
  approved_by: string
  payment_date?: string
  status: CompensationStatus
  notes?: string
  processed_by: string
}

export interface SecurityDashboard {
  vault_status: string
  last_opened?: string
  cctv_cameras_online: number
  cctv_cameras_total: number
  active_alarms: number
  recent_security_events: SecurityEvent[]
  incidents_this_month: number
  active_insurance_policies: number
  expiring_policies_30_days: number
}

export interface SecurityStatistics {
  total_incidents: number
  incidents_by_type: Record<string, number>
  incidents_by_severity: Record<string, number>
  open_incidents: number
  total_insurance_policies: number
  active_policies: number
  expired_policies: number
  total_claims_filed: number
  claims_approved: number
  total_compensation_paid: number
  security_events_today: number
  critical_events_this_week: number
  vault_opens_this_month: number
  cctv_uptime_percentage: number
}

// ============================================
// Safety & Security Service Methods
// ============================================

export const safetySecurityService = {
  // ========== Vault Operations ==========
  
  /**
   * Open vault with dual custody
   */
  openVault: async (data: {
    branch_id: string
    access_type: VaultAccessType
    official_1_id: string
    official_2_id: string
    purpose: string
    time_lock_override?: boolean
    override_reason?: string
  }) => {
    return apiClient.post('/locker/safety-security/vault/open', data)
  },

  /**
   * Close vault with dual custody
   */
  closeVault: async (data: {
    access_record_id: string
    official_1_id: string
    official_2_id: string
    notes?: string
  }) => {
    return apiClient.post('/locker/safety-security/vault/close', data)
  },

  /**
   * Get vault access log
   */
  getVaultAccessLog: async (
    branch_id: string,
    start_date?: string,
    end_date?: string
  ) => {
    return apiClient.get('/locker/safety-security/vault/access-log', {
      params: { branch_id, start_date, end_date }
    })
  },

  // ========== Security Monitoring ==========

  /**
   * Record CCTV camera status
   */
  recordCCTVStatus: async (data: {
    branch_id: string
    camera_id: string
    status: string
    recording_status: boolean
    last_check: string
  }) => {
    return apiClient.post('/locker/safety-security/cctv/status', data)
  },

  /**
   * Trigger alarm
   */
  triggerAlarm: async (data: {
    branch_id: string
    alarm_type: string
    triggered_by: string
    location: string
    reason: string
  }) => {
    return apiClient.post('/locker/safety-security/alarm/trigger', data)
  },

  /**
   * Get security events
   */
  getSecurityEvents: async (
    branch_id?: string,
    severity?: SecurityEventSeverity,
    limit: number = 50
  ) => {
    return apiClient.get('/locker/safety-security/security-events', {
      params: { branch_id, severity, limit }
    })
  },

  /**
   * Get security dashboard
   */
  getSecurityDashboard: async (branch_id?: string) => {
    return apiClient.get<SecurityDashboard>('/locker/safety-security/dashboard', {
      params: { branch_id }
    })
  },

  // ========== Insurance Management ==========

  /**
   * Create insurance policy
   */
  createInsurancePolicy: async (data: {
    policy_type: InsuranceType
    locker_id?: string
    customer_id?: string
    insurer_name: string
    coverage_amount: number
    premium_amount: number
    start_date: string
    end_date: string
    terms_conditions?: string
  }) => {
    return apiClient.post<{ success: boolean; policy: InsurancePolicy }>(
      '/locker/safety-security/insurance/policy',
      data
    )
  },

  /**
   * Renew insurance policy
   */
  renewInsurancePolicy: async (data: {
    policy_id: string
    new_end_date: string
    premium_amount: number
  }) => {
    return apiClient.post('/locker/safety-security/insurance/renew', data)
  },

  /**
   * File insurance claim
   */
  fileInsuranceClaim: async (data: {
    policy_id: string
    incident_id: string
    claim_amount: number
    claim_description: string
    supporting_documents?: string[]
  }) => {
    return apiClient.post<{ success: boolean; claim: InsuranceClaim }>(
      '/locker/safety-security/insurance/claim',
      data
    )
  },

  /**
   * Get insurance policies
   */
  getInsurancePolicies: async (
    customer_id?: string,
    status?: InsuranceStatus
  ) => {
    return apiClient.get<{ policies: InsurancePolicy[]; total: number }>(
      '/locker/safety-security/insurance/policies',
      { params: { customer_id, status } }
    )
  },

  // ========== Incident Management ==========

  /**
   * Report incident
   */
  reportIncident: async (data: {
    incident_type: IncidentType
    severity: IncidentSeverity
    branch_id: string
    affected_lockers?: string[]
    incident_date: string
    description: string
  }) => {
    return apiClient.post<{ success: boolean; incident: SecurityIncident }>(
      '/locker/safety-security/incident/report',
      data
    )
  },

  /**
   * Investigate incident
   */
  investigateIncident: async (
    incident_id: string,
    data: {
      findings: string
      evidence_collected?: string[]
      root_cause?: string
      recommendations?: string
    }
  ) => {
    return apiClient.post(
      `/locker/safety-security/incident/${incident_id}/investigate`,
      data
    )
  },

  /**
   * Notify authorities (RBI/Police)
   */
  notifyAuthorities: async (
    incident_id: string,
    data: {
      authority_type: 'rbi' | 'police'
      reference_number?: string
      contact_person?: string
      acknowledgment_received?: boolean
    }
  ) => {
    return apiClient.post(
      `/locker/safety-security/incident/${incident_id}/notify-authorities`,
      data
    )
  },

  /**
   * Process compensation
   */
  processCompensation: async (
    incident_id: string,
    data: {
      customer_id: string
      locker_id: string
      compensation_amount: number
      compensation_type: string
      approved_by: string
      payment_date?: string
      notes?: string
    }
  ) => {
    return apiClient.post<{ success: boolean; compensation: Compensation }>(
      `/locker/safety-security/incident/${incident_id}/compensation`,
      data
    )
  },

  /**
   * Get incidents list
   */
  getIncidents: async (
    branch_id?: string,
    status?: IncidentStatus,
    severity?: IncidentSeverity
  ) => {
    return apiClient.get<{ incidents: SecurityIncident[]; total: number }>(
      '/locker/safety-security/incident/list',
      { params: { branch_id, status, severity } }
    )
  },

  /**
   * Get incident details
   */
  getIncidentDetails: async (incident_id: string) => {
    return apiClient.get<SecurityIncident>(
      `/locker/safety-security/incident/${incident_id}`
    )
  },

  // ========== Statistics ==========

  /**
   * Get safety & security statistics
   */
  getStatistics: async () => {
    return apiClient.get<SecurityStatistics>(
      '/locker/safety-security/statistics'
    )
  }
}


// ============================================
// Compliance Type Definitions
// ============================================

export enum ComplianceType {
  RBI_GUIDELINES = 'rbi_guidelines',
  FAIR_ALLOCATION = 'fair_allocation',
  RENT_TRANSPARENCY = 'rent_transparency',
  CUSTOMER_EDUCATION = 'customer_education',
  COMPLAINT_REDRESSAL = 'complaint_redressal',
  AGREEMENT_FORMAT = 'agreement_format'
}

export enum ComplianceStatus {
  COMPLIANT = 'compliant',
  NON_COMPLIANT = 'non_compliant',
  PARTIALLY_COMPLIANT = 'partially_compliant',
  UNDER_REVIEW = 'under_review',
  REMEDIATION_IN_PROGRESS = 'remediation_in_progress'
}

export enum AuditType {
  INTERNAL_AUDIT = 'internal_audit',
  CONCURRENT_AUDIT = 'concurrent_audit',
  STATUTORY_AUDIT = 'statutory_audit',
  RBI_INSPECTION = 'rbi_inspection',
  SPECIAL_AUDIT = 'special_audit'
}

export enum AuditStatus {
  SCHEDULED = 'scheduled',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  REPORT_PENDING = 'report_pending',
  CLOSED = 'closed'
}

export enum InspectionType {
  ACCESS_LOG_VERIFICATION = 'access_log_verification',
  RENT_COLLECTION_VERIFICATION = 'rent_collection_verification',
  PHYSICAL_VERIFICATION = 'physical_verification',
  AGREEMENT_VERIFICATION = 'agreement_verification',
  INSURANCE_VERIFICATION = 'insurance_verification',
  MAINTENANCE_VERIFICATION = 'maintenance_verification'
}

export enum FindingsSeverity {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}

export interface ComplianceCheck {
  id: string
  tenant_id: string
  branch_id: string
  check_date: string
  overall_status: ComplianceStatus
  compliance_results: Record<string, {
    status: ComplianceStatus
    details: string
    last_checked: string
    score: number
  }>
  checked_by: string
}

export interface ComplianceIssue {
  id: string
  tenant_id: string
  issue_number: string
  compliance_type: ComplianceType
  branch_id: string
  severity: FindingsSeverity
  description: string
  identified_date: string
  remediation_plan?: string
  target_resolution_date?: string
  status: string
  remediation_details?: string
  resolved_date?: string
  identified_by: string
  updated_at: string
  updated_by: string
}

export interface AuditRecord {
  id: string
  tenant_id: string
  audit_number: string
  audit_type: AuditType
  branch_id: string
  scheduled_date: string
  auditor_name: string
  audit_scope: string
  checklist_items: any[]
  status: AuditStatus
  created_at: string
  created_by: string
  start_date?: string
  end_date?: string
  checklist_results?: any[]
  findings?: any[]
  observations?: string
  recommendations?: string
  executed_by?: string
}

export interface AuditReport {
  id: string
  audit_id: string
  report_number: string
  executive_summary: string
  detailed_findings: string
  risk_rating: string
  compliance_score: number
  recommendations: string
  action_items: any[]
  report_date: string
  prepared_by: string
}

export interface InspectionRecord {
  id: string
  tenant_id: string
  inspection_number: string
  inspection_type: InspectionType
  branch_id: string
  inspection_date: string
  inspector_name: string
  items_checked: any[]
  findings: any[]
  discrepancies_found: any[]
  recommendations?: string
  conducted_by: string
  created_at: string
}

export interface AccessLogVerification {
  id: string
  branch_id: string
  verification_date: string
  period_start: string
  period_end: string
  total_access_records: number
  verified_records: number
  discrepancies: any[]
  compliance_status: ComplianceStatus
  verified_by: string
}

export interface RentCollectionVerification {
  id: string
  branch_id: string
  verification_date: string
  period_start: string
  period_end: string
  total_collections: number
  verified_collections: number
  outstanding_amount: number
  discrepancies: any[]
  compliance_status: ComplianceStatus
  verified_by: string
}

export interface PhysicalVerification {
  id: string
  branch_id: string
  verification_date: string
  lockers_to_verify: number
  lockers_verified: number
  lockers_found_ok: number
  lockers_with_issues: number
  issues_found: any[]
  verified_by: string
}

export interface ComplianceDashboard {
  overall_compliance_score: number
  compliant_areas: number
  non_compliant_areas: number
  pending_audits: number
  completed_audits_this_month: number
  open_compliance_issues: number
  critical_issues: number
  upcoming_inspections: number
  last_rbi_compliance_check?: string
}

export interface ComplianceStatistics {
  period: string
  total_audits: number
  audits_by_type: Record<string, number>
  total_inspections: number
  inspections_by_type: Record<string, number>
  compliance_issues: {
    total: number
    open: number
    resolved: number
    by_severity: Record<string, number>
  }
  compliance_trends: Array<{
    month: string
    score: number
  }>
}

// ============================================
// Compliance Service Methods
// ============================================

export const complianceService = {
  // ========== Compliance Management ==========

  /**
   * Check RBI compliance across various areas
   */
  checkRBICompliance: async (data: {
    branch_id: string
    compliance_areas?: ComplianceType[]
  }) => {
    return apiClient.post<{ success: boolean; compliance_check: ComplianceCheck }>(
      '/api/locker/compliance/check-compliance',
      data
    )
  },

  /**
   * Record compliance issue
   */
  recordComplianceIssue: async (data: {
    compliance_type: ComplianceType
    branch_id: string
    severity: FindingsSeverity
    description: string
    remediation_plan?: string
    target_resolution_date?: string
  }) => {
    return apiClient.post<{ success: boolean; issue: ComplianceIssue }>(
      '/api/locker/compliance/issues',
      data
    )
  },

  /**
   * Update compliance issue status
   */
  updateComplianceStatus: async (
    issue_id: string,
    data: {
      status: string
      remediation_details?: string
    }
  ) => {
    return apiClient.put<{ success: boolean; update: any }>(
      `/api/locker/compliance/issues/${issue_id}/status`,
      data
    )
  },

  /**
   * Get compliance issues list
   */
  getComplianceIssues: async (params?: {
    branch_id?: string
    compliance_type?: ComplianceType
    severity?: FindingsSeverity
    status?: string
  }) => {
    return apiClient.get<{ issues: ComplianceIssue[] }>(
      '/api/locker/compliance/issues',
      { params }
    )
  },

  // ========== Audit Management ==========

  /**
   * Schedule an audit
   */
  scheduleAudit: async (data: {
    audit_type: AuditType
    branch_id: string
    scheduled_date: string
    auditor_name: string
    audit_scope: string
    checklist_items?: any[]
  }) => {
    return apiClient.post<{ success: boolean; audit: AuditRecord }>(
      '/api/locker/compliance/audits/schedule',
      data
    )
  },

  /**
   * Execute an audit
   */
  executeAudit: async (
    audit_id: string,
    data: {
      start_date?: string
      end_date?: string
      checklist_results?: any[]
      findings?: any[]
      observations?: string
      recommendations?: string
    }
  ) => {
    return apiClient.post<{ success: boolean; execution: any }>(
      `/api/locker/compliance/audits/${audit_id}/execute`,
      data
    )
  },

  /**
   * Generate audit report
   */
  generateAuditReport: async (
    audit_id: string,
    data: {
      executive_summary: string
      detailed_findings: string
      risk_rating: string
      compliance_score: number
      recommendations: string
      action_items: any[]
    }
  ) => {
    return apiClient.post<{ success: boolean; report: AuditReport }>(
      `/api/locker/compliance/audits/${audit_id}/report`,
      data
    )
  },

  /**
   * Get audits list
   */
  getAudits: async (params?: {
    branch_id?: string
    audit_type?: AuditType
    status?: AuditStatus
    from_date?: string
    to_date?: string
  }) => {
    return apiClient.get<{ audits: AuditRecord[] }>(
      '/api/locker/compliance/audits',
      { params }
    )
  },

  /**
   * Get audit details
   */
  getAuditDetails: async (audit_id: string) => {
    return apiClient.get<AuditRecord>(
      `/api/locker/compliance/audits/${audit_id}`
    )
  },

  // ========== Inspection Management ==========

  /**
   * Conduct inspection
   */
  conductInspection: async (data: {
    inspection_type: InspectionType
    branch_id: string
    inspection_date?: string
    inspector_name: string
    items_checked?: any[]
    findings?: any[]
    discrepancies_found?: any[]
    recommendations?: string
  }) => {
    return apiClient.post<{ success: boolean; inspection: InspectionRecord }>(
      '/api/locker/compliance/inspections',
      data
    )
  },

  /**
   * Verify access logs
   */
  verifyAccessLogs: async (data: {
    branch_id: string
    start_date: string
    end_date: string
  }) => {
    return apiClient.post<{ success: boolean; verification: AccessLogVerification }>(
      '/api/locker/compliance/inspections/verify-access-logs',
      data
    )
  },

  /**
   * Verify rent collection
   */
  verifyRentCollection: async (data: {
    branch_id: string
    start_date: string
    end_date: string
  }) => {
    return apiClient.post<{ success: boolean; verification: RentCollectionVerification }>(
      '/api/locker/compliance/inspections/verify-rent-collection',
      data
    )
  },

  /**
   * Conduct physical verification
   */
  conductPhysicalVerification: async (data: {
    branch_id: string
    locker_ids: string[]
  }) => {
    return apiClient.post<{ success: boolean; verification: PhysicalVerification }>(
      '/api/locker/compliance/inspections/physical-verification',
      data
    )
  },

  /**
   * Get inspections list
   */
  getInspections: async (params?: {
    branch_id?: string
    inspection_type?: InspectionType
    from_date?: string
    to_date?: string
  }) => {
    return apiClient.get<{ inspections: InspectionRecord[] }>(
      '/api/locker/compliance/inspections',
      { params }
    )
  },

  /**
   * Get inspection details
   */
  getInspectionDetails: async (inspection_id: string) => {
    return apiClient.get<InspectionRecord>(
      `/api/locker/compliance/inspections/${inspection_id}`
    )
  },

  // ========== Dashboard & Statistics ==========

  /**
   * Get compliance dashboard
   */
  getDashboard: async (branch_id?: string) => {
    return apiClient.get<ComplianceDashboard>(
      '/api/locker/compliance/dashboard',
      { params: { branch_id } }
    )
  },

  /**
   * Get compliance statistics
   */
  getStatistics: async (params?: {
    branch_id?: string
    period?: string
  }) => {
    return apiClient.get<ComplianceStatistics>(
      '/api/locker/compliance/statistics',
      { params }
    )
  }
}


// ============================================
// Reports & Analytics Type Definitions
// ============================================

export enum ReportType {
  ALLOCATION_REGISTER = 'allocation_register',
  AVAILABLE_OCCUPIED = 'available_occupied',
  WAITING_LIST = 'waiting_list',
  RENT_COLLECTION = 'rent_collection',
  OVERDUE_RENT = 'overdue_rent',
  ACCESS_LOG = 'access_log',
  LOCKER_BREAKING = 'locker_breaking',
  BRANCH_WISE = 'branch_wise',
  REVENUE = 'revenue',
  OCCUPANCY_RATE = 'occupancy_rate',
  CUSTOMER_DEMOGRAPHICS = 'customer_demographics'
}

export enum ExportFormat {
  PDF = 'pdf',
  EXCEL = 'excel',
  CSV = 'csv',
  JSON = 'json'
}

export enum ReportPeriod {
  TODAY = 'today',
  YESTERDAY = 'yesterday',
  THIS_WEEK = 'this_week',
  LAST_WEEK = 'last_week',
  THIS_MONTH = 'this_month',
  LAST_MONTH = 'last_month',
  THIS_QUARTER = 'this_quarter',
  LAST_QUARTER = 'last_quarter',
  THIS_YEAR = 'this_year',
  LAST_YEAR = 'last_year',
  CUSTOM = 'custom'
}

export enum ReportStatus {
  PENDING = 'pending',
  GENERATING = 'generating',
  COMPLETED = 'completed',
  FAILED = 'failed'
}

export interface LockersDashboard {
  total_lockers: {
    total: number
    by_size: Record<string, number>
  }
  occupancy: {
    total_lockers: number
    occupied: number
    available: number
    occupancy_percentage: number
    under_maintenance: number
    blocked: number
  }
  rent_collection: {
    current_month: {
      total_expected: number
      collected: number
      pending: number
      collection_percentage: number
    }
    comparison: {
      last_month: number
      growth_percentage: number
    }
  }
  overdue: {
    total_overdue_lockers: number
    total_overdue_amount: number
    by_period: Record<string, number>
  }
  waiting_list: {
    total_waiting: number
    by_size: Record<string, number>
    average_wait_days: number
  }
  recent_allocations: {
    today: number
    this_week: number
    this_month: number
    last_allocation?: string
  }
  recent_surrenders: {
    today: number
    this_week: number
    this_month: number
    last_surrender?: string
  }
  revenue_trends: Array<{
    month: string
    revenue: number
  }>
  occupancy_trends: Array<{
    month: string
    percentage: number
  }>
}

export interface ReportData {
  report_type: ReportType
  generated_at: string
  filters?: any
  total_records: number
  data: any[]
  summary: any
}

export interface AllocationRegisterReport extends ReportData {
  summary: {
    total_allocations: number
    active_allocations: number
    expired_allocations: number
    total_rent_collected: number
    total_security_deposit: number
  }
}

export interface AvailableOccupiedReport extends ReportData {
  branch_id?: string
  summary: {
    total_lockers: number
    available: number
    occupied: number
    under_maintenance: number
    blocked: number
    occupancy_rate: number
  }
  by_size: Array<{
    size: string
    total: number
    available: number
    occupied: number
    occupancy_rate: number
  }>
  by_branch: any[]
}

export interface WaitingListReport extends ReportData {
  branch_id?: string
  total_waiting: number
  summary: {
    by_size: Record<string, number>
    by_priority: Record<string, number>
    average_wait_days: number
    longest_wait_days: number
  }
}

export interface RentCollectionReport extends ReportData {
  period: {
    start: string
    end: string
  }
  summary: {
    total_expected: number
    total_collected: number
    total_pending: number
    collection_percentage: number
    by_payment_mode: Record<string, number>
    by_branch: any[]
  }
}

export interface OverdueRentReport extends ReportData {
  branch_id?: string
  summary: {
    total_overdue_lockers: number
    total_overdue_amount: number
    by_aging: Record<string, { count: number; amount: number }>
    by_customer_category: Record<string, number>
  }
}

export interface AccessLogReport extends ReportData {
  period: {
    start: string
    end: string
  }
  branch_id?: string
  summary: {
    total_accesses: number
    unique_lockers_accessed: number
    unique_customers: number
    by_access_type: Record<string, number>
    busiest_hours: any[]
    busiest_days: any[]
  }
}

export interface LockerBreakingReport extends ReportData {
  period: {
    start: string
    end: string
  }
  summary: {
    total_breakings: number
    by_reason: Record<string, number>
    total_charges_collected: number
    pending_charges: number
  }
}

export interface BranchWiseReport extends ReportData {
  total_branches: number
  summary: {
    total_lockers_all_branches: number
    total_occupied: number
    total_available: number
    overall_occupancy_rate: number
    total_revenue_current_month: number
    top_performing_branches: any[]
    low_occupancy_branches: any[]
  }
}

export interface RevenueReport extends ReportData {
  period: {
    start: string
    end: string
  }
  branch_id?: string
  summary: {
    total_revenue: number
    rent_revenue: number
    security_deposit: number
    penalty_revenue: number
    other_charges: number
    by_locker_size: Record<string, number>
    by_payment_mode: Record<string, number>
    revenue_trends: any[]
  }
  details: any[]
}

export interface OccupancyRateReport extends ReportData {
  period: {
    start: string
    end: string
  }
  summary: {
    current_occupancy_rate: number
    average_occupancy_rate: number
    highest_occupancy_rate: number
    lowest_occupancy_rate: number
    by_size: Record<string, number>
    by_branch: any[]
    trends: Array<{
      date: string
      rate: number
    }>
  }
}

export interface CustomerDemographicsReport extends ReportData {
  branch_id?: string
  summary: {
    total_customers: number
    by_category: Record<string, number>
    by_age_group: Record<string, number>
    by_gender: Record<string, number>
    by_occupation: Record<string, number>
    by_locker_purpose: Record<string, number>
  }
}

export interface ReportListItem {
  id: string
  report_type: ReportType
  status: ReportStatus
  generated_at: string
  generated_by: string
  file_path?: string
}

export interface ExportResult {
  success: boolean
  format: ExportFormat
  file_path: string
  file_size: number
  exported_at: string
}

export interface StatisticsData {
  metric: string
  period: ReportPeriod
  date_range: {
    start: string
    end: string
  }
  value: number
  comparison: {
    previous_period: number
    change_percentage: number
  }
}

// ============================================
// Reports & Analytics Service Methods
// ============================================

export const reportsService = {
  // ========== Dashboard ==========

  /**
   * Get comprehensive dashboard with all KPIs
   */
  getDashboard: async (branch_id?: string) => {
    return apiClient.get<LockersDashboard>(
      '/api/locker/reports/dashboard',
      { params: { branch_id } }
    )
  },

  // ========== Report Generation ==========

  /**
   * Generate allocation register report
   */
  generateAllocationRegister: async (filters: {
    branch_id?: string
    allocation_status?: string
    customer_category?: string
    from_date?: string
    to_date?: string
  }) => {
    return apiClient.post<AllocationRegisterReport>(
      '/api/locker/reports/allocation-register',
      filters
    )
  },

  /**
   * Generate available/occupied lockers report
   */
  generateAvailableOccupiedReport: async (branch_id?: string) => {
    return apiClient.get<AvailableOccupiedReport>(
      '/api/locker/reports/available-occupied',
      { params: { branch_id } }
    )
  },

  /**
   * Generate waiting list report
   */
  generateWaitingListReport: async (branch_id?: string) => {
    return apiClient.get<WaitingListReport>(
      '/api/locker/reports/waiting-list',
      { params: { branch_id } }
    )
  },

  /**
   * Generate rent collection report
   */
  generateRentCollectionReport: async (data: {
    branch_id?: string
    period?: ReportPeriod
    custom_start?: string
    custom_end?: string
    payment_mode?: string
  }) => {
    return apiClient.post<RentCollectionReport>(
      '/api/locker/reports/rent-collection',
      data
    )
  },

  /**
   * Generate overdue rent report
   */
  generateOverdueRentReport: async (data: {
    branch_id?: string
    min_overdue_days?: number
    max_overdue_days?: number
  }) => {
    return apiClient.post<OverdueRentReport>(
      '/api/locker/reports/overdue-rent',
      data
    )
  },

  /**
   * Generate access log report
   */
  generateAccessLogReport: async (data: {
    branch_id?: string
    locker_id?: string
    period?: ReportPeriod
    custom_start?: string
    custom_end?: string
  }) => {
    return apiClient.post<AccessLogReport>(
      '/api/locker/reports/access-log',
      data
    )
  },

  /**
   * Generate locker breaking register
   */
  generateLockerBreakingReport: async (data: {
    branch_id?: string
    period?: ReportPeriod
    custom_start?: string
    custom_end?: string
  }) => {
    return apiClient.post<LockerBreakingReport>(
      '/api/locker/reports/locker-breaking',
      data
    )
  },

  /**
   * Generate branch-wise report
   */
  generateBranchWiseReport: async (include_details: boolean = true) => {
    return apiClient.get<BranchWiseReport>(
      '/api/locker/reports/branch-wise',
      { params: { include_details } }
    )
  },

  /**
   * Generate revenue report
   */
  generateRevenueReport: async (data: {
    branch_id?: string
    period?: ReportPeriod
    custom_start?: string
    custom_end?: string
    group_by?: string
  }) => {
    return apiClient.post<RevenueReport>(
      '/api/locker/reports/revenue',
      data
    )
  },

  /**
   * Generate occupancy rate report
   */
  generateOccupancyRateReport: async (data: {
    branch_id?: string
    period?: ReportPeriod
    custom_start?: string
    custom_end?: string
  }) => {
    return apiClient.post<OccupancyRateReport>(
      '/api/locker/reports/occupancy-rate',
      data
    )
  },

  /**
   * Generate customer demographics report
   */
  generateCustomerDemographicsReport: async (branch_id?: string) => {
    return apiClient.get<CustomerDemographicsReport>(
      '/api/locker/reports/customer-demographics',
      { params: { branch_id } }
    )
  },

  // ========== Report Management ==========

  /**
   * Get list of generated reports
   */
  getReportList: async (params?: {
    report_type?: ReportType
    status?: ReportStatus
    from_date?: string
    to_date?: string
  }) => {
    return apiClient.get<{ reports: ReportListItem[] }>(
      '/api/locker/reports/list',
      { params }
    )
  },

  /**
   * Get report details by ID
   */
  getReportDetails: async (report_id: string) => {
    return apiClient.get<ReportListItem>(
      `/api/locker/reports/${report_id}`
    )
  },

  // ========== Export ==========

  /**
   * Export report to specified format
   */
  exportReport: async (data: {
    report_type: ReportType
    format: ExportFormat
    filters?: any
  }) => {
    return apiClient.post<ExportResult>(
      '/api/locker/reports/export',
      data
    )
  },

  // ========== Statistics ==========

  /**
   * Get specific statistics
   */
  getStatistics: async (
    metric: string,
    period: ReportPeriod = ReportPeriod.THIS_MONTH
  ) => {
    return apiClient.get<StatisticsData>(
      `/api/locker/reports/statistics/${metric}`,
      { params: { period } }
    )
  }
}
