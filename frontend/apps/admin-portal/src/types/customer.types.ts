/**
 * Customer 360 / CIF TypeScript Types
 * Interfaces matching backend schemas for customer module
 */

// ============================================================================
// ENUMS
// ============================================================================

export enum CustomerTypeEnum {
  INDIVIDUAL = "individual",
  PROPRIETORSHIP = "proprietorship",
  PARTNERSHIP = "partnership",
  PRIVATE_LIMITED = "private_limited",
}

export enum GenderEnum {
  MALE = "male",
  FEMALE = "female",
  OTHER = "other",
}

export enum MaritalStatusEnum {
  SINGLE = "single",
  MARRIED = "married",
  DIVORCED = "divorced",
  WIDOWED = "widowed",
}

export enum KYCStatusEnum {
  PENDING = "pending",
  IN_PROGRESS = "in_progress",
  COMPLETED = "completed",
  REJECTED = "rejected",
}

export enum RiskRatingEnum {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high",
  VERY_HIGH = "very_high",
}

export enum AccountTypeEnum {
  SAVINGS = "savings",
  CURRENT = "current",
  OVERDRAFT = "overdraft",
}

export enum ActivityTypeEnum {
  CUSTOMER_CREATED = "customer_created",
  CUSTOMER_UPDATED = "customer_updated",
  CUSTOMER_DEACTIVATED = "customer_deactivated",
  KYC_INITIATED = "kyc_initiated",
  KYC_COMPLETED = "kyc_completed",
  DOCUMENT_UPLOADED = "document_uploaded",
  DOCUMENT_VERIFIED = "document_verified",
  BUREAU_PULLED = "bureau_pulled",
  LOAN_APPLIED = "loan_applied",
  LOAN_APPROVED = "loan_approved",
  LOAN_DISBURSED = "loan_disbursed",
  PAYMENT_RECEIVED = "payment_received",
}

// ============================================================================
// CUSTOMER INTERFACES
// ============================================================================

export interface Customer {
  id: number;
  customer_code: string;
  customer_type: CustomerTypeEnum;
  first_name?: string;
  middle_name?: string;
  last_name?: string;
  full_name?: string;
  business_name?: string;
  email?: string;
  mobile: string;
  alternate_mobile?: string;
  pan_number?: string;
  aadhaar_number?: string;
  date_of_birth?: string;
  age?: number;
  gender?: GenderEnum;
  marital_status?: MaritalStatusEnum;
  father_name?: string;
  mother_name?: string;
  occupation_name?: string;
  industry_name?: string;
  monthly_income?: number;
  annual_income?: number;
  current_city_name?: string;
  current_state_name?: string;
  kyc_status: KYCStatusEnum;
  is_kyc_verified: boolean;
  risk_rating: RiskRatingEnum;
  cibil_score?: number;
  is_active: boolean;
  is_blacklisted: boolean;
  created_at: string;
  updated_at?: string;
}

export interface CustomerCreate {
  customer_type?: CustomerTypeEnum;
  first_name?: string;
  middle_name?: string;
  last_name?: string;
  business_name?: string;
  email?: string;
  mobile: string;
  alternate_mobile?: string;
  pan_number?: string;
  aadhaar_number?: string;
  date_of_birth?: string;
  gender?: GenderEnum;
  marital_status?: MaritalStatusEnum;
  father_name?: string;
  mother_name?: string;
}

export interface CustomerUpdate {
  first_name?: string;
  middle_name?: string;
  last_name?: string;
  email?: string;
  mobile?: string;
  alternate_mobile?: string;
  date_of_birth?: string;
  gender?: GenderEnum;
  marital_status?: MaritalStatusEnum;
  occupation_id?: number;
  industry_id?: number;
  monthly_income?: number;
  current_address_line1?: string;
  current_city_id?: number;
  current_state_id?: number;
  current_pincode?: string;
}

export interface CustomerListItem {
  id: number;
  customer_code: string;
  full_name: string;
  mobile: string;
  email?: string;
  kyc_status: KYCStatusEnum;
  risk_rating: RiskRatingEnum;
  cibil_score?: number;
  is_active: boolean;
  created_at: string;
}

export interface PaginatedCustomerResponse {
  items: CustomerListItem[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface CustomerDashboardStats {
  total_customers: number;
  active_customers: number;
  kyc_pending: number;
  kyc_completed: number;
  high_risk_customers: number;
  blacklisted_customers: number;
  new_this_month: number;
  avg_cibil_score?: number;
}

// ============================================================================
// CUSTOMER DOCUMENT INTERFACES
// ============================================================================

export interface CustomerDocument {
  id: number;
  customer_id: number;
  document_type_id: number;
  document_type_name?: string;
  document_number?: string;
  document_name: string;
  document_url: string;
  document_format: string;
  issue_date?: string;
  expiry_date?: string;
  status: string;
  verified_by?: number;
  verified_date?: string;
  is_expired: boolean;
  uploaded_date: string;
}

export interface CustomerDocumentCreate {
  customer_id: number;
  document_type_id: number;
  document_number?: string;
  document_name: string;
  document_url: string;
  issue_date?: string;
  expiry_date?: string;
}

// ============================================================================
// CUSTOMER FAMILY INTERFACES
// ============================================================================

export interface CustomerFamily {
  id: number;
  customer_id: number;
  relationship_type_id: number;
  relationship_type_name?: string;
  name: string;
  date_of_birth?: string;
  age?: number;
  gender?: GenderEnum;
  mobile?: string;
  occupation?: string;
  monthly_income?: number;
  is_dependent: boolean;
  is_emergency_contact: boolean;
  is_nominee: boolean;
  nominee_percentage?: number;
  created_at: string;
}

export interface CustomerFamilyCreate {
  customer_id: number;
  relationship_type_id: number;
  name: string;
  date_of_birth?: string;
  gender?: GenderEnum;
  mobile?: string;
  occupation?: string;
  monthly_income?: number;
  is_dependent?: boolean;
  is_emergency_contact?: boolean;
  is_nominee?: boolean;
  nominee_percentage?: number;
}

export interface CustomerFamilyUpdate {
  relationship_type_id?: number;
  name?: string;
  date_of_birth?: string;
  gender?: GenderEnum;
  mobile?: string;
  occupation?: string;
  monthly_income?: number;
  is_dependent?: boolean;
  is_emergency_contact?: boolean;
  is_nominee?: boolean;
  nominee_percentage?: number;
}

// ============================================================================
// CUSTOMER BANK ACCOUNT INTERFACES
// ============================================================================

export interface CustomerBankAccount {
  id: number;
  customer_id: number;
  bank_id: number;
  bank_name?: string;
  branch_name?: string;
  account_number: string;
  account_holder_name: string;
  account_type: AccountTypeEnum;
  ifsc_code: string;
  is_primary: boolean;
  use_for_disbursement: boolean;
  use_for_collection: boolean;
  is_verified: boolean;
  verified_date?: string;
  is_active: boolean;
  created_at: string;
}

export interface CustomerBankAccountCreate {
  customer_id: number;
  bank_id: number;
  account_number: string;
  account_holder_name: string;
  account_type?: AccountTypeEnum;
  ifsc_code: string;
  is_primary?: boolean;
  use_for_disbursement?: boolean;
  use_for_collection?: boolean;
}

export interface CustomerBankAccountUpdate {
  bank_id?: number;
  account_number?: string;
  account_holder_name?: string;
  account_type?: AccountTypeEnum;
  ifsc_code?: string;
  is_primary?: boolean;
  use_for_disbursement?: boolean;
  use_for_collection?: boolean;
  is_active?: boolean;
}

// ============================================================================
// KYC INTERFACES
// ============================================================================

export interface CustomerKYC {
  id: number;
  customer_id: number;
  aadhaar_verified: boolean;
  aadhaar_verified_date?: string;
  pan_verified: boolean;
  pan_verified_date?: string;
  bank_account_verified: boolean;
  video_kyc_done: boolean;
  in_person_verification_done: boolean;
  overall_kyc_status: KYCStatusEnum;
  kyc_completion_percentage: number;
  created_at: string;
  updated_at?: string;
}

export interface CustomerKYCUpdate {
  aadhaar_verified?: boolean;
  aadhaar_verification_method?: string;
  pan_verified?: boolean;
  bank_account_verified?: boolean;
  video_kyc_done?: boolean;
  in_person_verification_done?: boolean;
  cibil_consent_given?: boolean;
  overall_kyc_status?: KYCStatusEnum;
  kyc_remarks?: string;
}

// ============================================================================
// TIMELINE INTERFACES
// ============================================================================

export interface TimelineActivity {
  id: number;
  customer_id: number;
  activity_type: string;
  title: string;
  description?: string;
  event_date: string;
  event_category?: string;
  event_source?: string;
  related_entity_type?: string;
  related_entity_id?: number;
  performed_by?: number;
  performed_by_name?: string;
  performed_by_role?: string;
  old_value?: Record<string, any>;
  new_value?: Record<string, any>;
  changes?: Record<string, any>;
  metadata?: Record<string, any>;
  is_important: boolean;
  is_system_generated: boolean;
  is_visible_to_customer: boolean;
  priority: number;
  created_at: string;
}

export interface TimelineActivityCreate {
  activity_type: string;
  title: string;
  description?: string;
  event_category?: string;
  related_entity_type?: string;
  related_entity_id?: number;
  metadata?: Record<string, any>;
  is_important?: boolean;
  is_visible_to_customer?: boolean;
}

export interface PaginatedTimelineResponse {
  items: TimelineActivity[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface TimelineSummaryResponse {
  customer_id: number;
  days: number;
  activity_counts: Record<string, number>;
}

// ============================================================================
// CREDIT BUREAU INTERFACES
// ============================================================================

export interface BureauPullRequest {
  bureau_provider: string; // cibil, equifax, experian, crif
  request_purpose?: string;
}

export interface BureauPullResponse {
  id: number;
  customer_id: number;
  bureau_provider: string;
  bureau_request_id: string;
  request_date: string;
  response_date?: string;
  status: string;
  credit_score?: number;
  score_date?: string;
  total_accounts?: number;
  active_accounts?: number;
  total_outstanding?: number;
  recent_enquiries_1m?: number;
  recent_enquiries_3m?: number;
  recent_enquiries_6m?: number;
  recent_enquiries_12m?: number;
  response_time_ms?: number;
  error_message?: string;
  created_at: string;
}

export interface BureauHistoryResponse {
  id: number;
  bureau_provider: string;
  request_date: string;
  status: string;
  credit_score?: number;
  response_time_ms?: number;
}

export interface CreditScoreResponse {
  customer_id: number;
  credit_score: number;
}

// ============================================================================
// eKYC / AADHAAR INTERFACES
// ============================================================================

export interface AadhaarOTPInitRequest {
  aadhaar_number: string;
}

export interface AadhaarOTPInitResponse {
  success: boolean;
  request_id: string;
  message: string;
  expires_at: string;
}

export interface AadhaarOTPVerifyRequest {
  aadhaar_number: string;
  otp: string;
  request_id: string;
}

export interface AadhaarOTPVerifyResponse {
  success: boolean;
  verified: boolean;
  message: string;
  ekyc_data?: Record<string, any>;
}

export interface BiometricVerifyRequest {
  aadhaar_number: string;
  biometric_data: string;
  biometric_type?: string;
}

export interface BiometricVerifyResponse {
  success: boolean;
  verified: boolean;
  message: string;
  ekyc_data?: Record<string, any>;
}

// ============================================================================
// DIGILOCKER INTERFACES
// ============================================================================

export interface DigiLockerAuthInitResponse {
  authorization_url: string;
  state: string;
}

export interface DigiLockerAuthCompleteRequest {
  code: string;
  redirect_uri: string;
}

export interface DigiLockerAuthCompleteResponse {
  success: boolean;
  access_token: string;
  expires_in: number;
  documents: Array<Record<string, any>>;
}

export interface DigiLockerDocumentResponse {
  uri: string;
  name: string;
  type: string;
  size: number;
  date: string;
  issuer: string;
}

export interface DigiLockerFetchDocumentRequest {
  access_token: string;
  document_uri: string;
  document_type_id: string;
}

// ============================================================================
// FILTER & SEARCH INTERFACES
// ============================================================================

export interface CustomerFilters {
  search?: string;
  kyc_status?: KYCStatusEnum;
  risk_rating?: RiskRatingEnum;
  is_active?: boolean;
  page?: number;
  page_size?: number;
}

export interface CustomerSearchParams {
  mobile?: string;
  pan?: string;
  aadhaar?: string;
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

export interface CustomerBadgeProps {
  status: KYCStatusEnum | RiskRatingEnum;
  variant?: "default" | "secondary" | "outline";
}

export interface CustomerCardProps {
  customer: Customer | CustomerListItem;
  onView?: (id: number) => void;
  onEdit?: (id: number) => void;
  onDelete?: (id: number) => void;
}
