/**
 * Customer Module TypeScript Types
 * Type definitions for Customer 360 features
 */

// ============================================================================
// ENUMS
// ============================================================================

export enum CustomerType {
  INDIVIDUAL = 'individual',
  PROPRIETORSHIP = 'proprietorship',
  PARTNERSHIP = 'partnership',
  PRIVATE_LIMITED = 'private_limited',
}

export enum Gender {
  MALE = 'male',
  FEMALE = 'female',
  OTHER = 'other',
}

export enum MaritalStatus {
  SINGLE = 'single',
  MARRIED = 'married',
  DIVORCED = 'divorced',
  WIDOWED = 'widowed',
}

export enum KYCStatus {
  PENDING = 'pending',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  REJECTED = 'rejected',
}

export enum RiskRating {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  VERY_HIGH = 'very_high',
}

export enum DocumentStatus {
  PENDING = 'pending',
  VERIFIED = 'verified',
  REJECTED = 'rejected',
  EXPIRED = 'expired',
}

export enum AccountType {
  SAVINGS = 'savings',
  CURRENT = 'current',
  OVERDRAFT = 'overdraft',
}

export enum ActivityType {
  CUSTOMER_CREATED = 'customer_created',
  CUSTOMER_UPDATED = 'customer_updated',
  KYC_INITIATED = 'kyc_initiated',
  KYC_COMPLETED = 'kyc_completed',
  DOCUMENT_UPLOADED = 'document_uploaded',
  DOCUMENT_VERIFIED = 'document_verified',
  BUREAU_PULLED = 'bureau_pulled',
  NOTE_ADDED = 'note_added',
}

// ============================================================================
// CUSTOMER TYPES
// ============================================================================

export interface Customer {
  id: number
  customer_code: string
  customer_type: CustomerType
  first_name?: string
  middle_name?: string
  last_name?: string
  full_name: string
  business_name?: string
  email?: string
  mobile: string
  alternate_mobile?: string
  pan_number?: string
  aadhaar_number?: string
  date_of_birth?: string
  age?: number
  gender?: Gender
  marital_status?: MaritalStatus
  father_name?: string
  mother_name?: string
  occupation_name?: string
  industry_name?: string
  monthly_income?: number
  annual_income?: number
  current_address_line1?: string
  current_address_line2?: string
  current_city_name?: string
  current_state_name?: string
  current_pincode?: string
  kyc_status: KYCStatus
  is_kyc_verified: boolean
  risk_rating: RiskRating
  cibil_score?: number
  is_active: boolean
  is_blacklisted: boolean
  blacklist_reason?: string
  blacklist_date?: string
  created_at: string
  updated_at?: string
}

export interface CreateCustomerRequest {
  customer_type: CustomerType
  first_name?: string
  middle_name?: string
  last_name?: string
  business_name?: string
  email?: string
  mobile: string
  alternate_mobile?: string
  pan_number?: string
  aadhaar_number?: string
  date_of_birth?: string
  gender?: Gender
  marital_status?: MaritalStatus
  father_name?: string
  mother_name?: string
}

// ============================================================================
// DOCUMENT TYPES
// ============================================================================

export interface CustomerDocument {
  id: number
  customer_id: number
  document_type_id: number
  document_type_name?: string
  document_number?: string
  document_name: string
  document_url: string
  issue_date?: string
  expiry_date?: string
  status: DocumentStatus
  verified_by?: number
  verified_date?: string
  verification_remarks?: string
  is_expired: boolean
  uploaded_date: string
  created_at: string
}

export interface DocumentType {
  id: number
  name: string
  code: string
  description?: string
  is_mandatory: boolean
  requires_expiry: boolean
}

// ============================================================================
// FAMILY MEMBER TYPES
// ============================================================================

export interface CustomerFamily {
  id: number
  customer_id: number
  relationship_type_id: number
  relationship_type_name?: string
  name: string
  date_of_birth?: string
  age?: number
  gender?: Gender
  mobile?: string
  occupation?: string
  monthly_income?: number
  is_dependent: boolean
  is_emergency_contact: boolean
  is_nominee: boolean
  nominee_percentage?: number
  created_at: string
}

export interface RelationshipType {
  id: number
  name: string
  code: string
}

// ============================================================================
// BANK ACCOUNT TYPES
// ============================================================================

export interface CustomerBankAccount {
  id: number
  customer_id: number
  bank_id: number
  bank_name?: string
  branch_name?: string
  account_number: string
  account_holder_name: string
  account_type: AccountType
  ifsc_code: string
  is_primary: boolean
  is_verified: boolean
  verified_date?: string
  verification_method?: string
  use_for_disbursement: boolean
  use_for_collection: boolean
  is_active: boolean
  created_at: string
}

export interface Bank {
  id: number
  name: string
  code: string
  logo_url?: string
}

// ============================================================================
// KYC TYPES
// ============================================================================

export interface CustomerKYC {
  id: number
  customer_id: number
  aadhaar_verified: boolean
  aadhaar_verified_date?: string
  aadhaar_verification_method?: string
  pan_verified: boolean
  pan_verified_date?: string
  bank_account_verified: boolean
  video_kyc_done: boolean
  in_person_verification_done: boolean
  cibil_consent_given: boolean
  overall_kyc_status: KYCStatus
  kyc_completion_percentage: number
  kyc_remarks?: string
  created_at: string
  updated_at?: string
}

// ============================================================================
// BUREAU TYPES
// ============================================================================

export interface BureauReport {
  id: number
  customer_id: number
  bureau_provider: string
  bureau_request_id: string
  request_date: string
  response_date?: string
  status: string
  credit_score?: number
  score_date?: string
  total_accounts?: number
  active_accounts?: number
  total_outstanding?: number
  recent_enquiries_1m?: number
  recent_enquiries_3m?: number
  recent_enquiries_6m?: number
  recent_enquiries_12m?: number
  response_time_ms?: number
  error_message?: string
  raw_data?: any
  created_at: string
}

export interface BureauProvider {
  code: string
  name: string
  description: string
  is_active: boolean
}

// ============================================================================
// TIMELINE TYPES
// ============================================================================

export interface CustomerTimeline {
  id: number
  customer_id: number
  activity_type: string
  title: string
  description?: string
  event_date: string
  event_category?: string
  event_source?: string
  related_entity_type?: string
  related_entity_id?: number
  performed_by?: number
  performed_by_name?: string
  performed_by_role?: string
  old_value?: any
  new_value?: any
  changes?: any
  metadata?: any
  is_important: boolean
  is_system_generated: boolean
  is_visible_to_customer: boolean
  priority: number
  created_at: string
}

// ============================================================================
// eKYC TYPES
// ============================================================================

export interface AadhaarOTPResponse {
  success: boolean
  request_id: string
  message: string
  expires_at: string
}

export interface AadhaarVerificationResponse {
  success: boolean
  verified: boolean
  message: string
  ekyc_data?: {
    name: string
    date_of_birth: string
    gender: string
    address: {
      line1: string
      line2?: string
      city: string
      district: string
      state: string
      pincode: string
    }
    photo?: string
    mobile?: string
    email?: string
  }
}

// ============================================================================
// DIGILOCKER TYPES
// ============================================================================

export interface DigiLockerDocument {
  uri: string
  name: string
  type: string
  size: number
  date: string
  issuer: string
}

export interface DigiLockerAuthResponse {
  authorization_url: string
  state: string
}

export interface DigiLockerCompleteResponse {
  success: boolean
  access_token: string
  expires_in: number
  documents: DigiLockerDocument[]
}

// ============================================================================
// STATISTICS TYPES
// ============================================================================

export interface CustomerStats {
  total_customers: number
  active_customers: number
  kyc_pending: number
  kyc_completed: number
  high_risk_customers: number
  blacklisted_customers: number
  new_this_month: number
  avg_cibil_score?: number
}

// ============================================================================
// RISK PROFILING TYPES
// ============================================================================

export interface RiskProfile {
  customer_id: number
  risk_rating: RiskRating
  risk_score: number
  risk_factors: RiskFactor[]
  last_updated: string
}

export interface RiskFactor {
  factor: string
  severity: 'low' | 'medium' | 'high'
  description: string
  score_impact: number
}
