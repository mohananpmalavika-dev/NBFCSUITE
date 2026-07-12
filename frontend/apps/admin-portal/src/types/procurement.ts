/**
 * Procurement & Vendor Management - TypeScript Type Definitions
 */

// ============================================================================
// ENUMS
// ============================================================================

export enum VendorType {
  SUPPLIER = 'supplier',
  CONTRACTOR = 'contractor',
  SERVICE_PROVIDER = 'service_provider',
  MANUFACTURER = 'manufacturer',
  WHOLESALER = 'wholesaler',
  RETAILER = 'retailer',
  CONSULTANT = 'consultant',
}

export enum VendorStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  BLACKLISTED = 'blacklisted',
  SUSPENDED = 'suspended',
  UNDER_REVIEW = 'under_review',
}

export enum PaymentTerms {
  IMMEDIATE = 'immediate',
  NET_15 = 'net_15',
  NET_30 = 'net_30',
  NET_45 = 'net_45',
  NET_60 = 'net_60',
  NET_90 = 'net_90',
  ADVANCE = 'advance',
  COD = 'cod',
  CUSTOM = 'custom',
}

export enum RequisitionStatus {
  DRAFT = 'draft',
  SUBMITTED = 'submitted',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  CANCELLED = 'cancelled',
  CONVERTED_TO_PO = 'converted_to_po',
  PARTIALLY_CONVERTED = 'partially_converted',
}

export enum RequisitionPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  URGENT = 'urgent',
}

export enum RFQStatus {
  DRAFT = 'draft',
  SENT = 'sent',
  RESPONSE_RECEIVED = 'response_received',
  CLOSED = 'closed',
  CANCELLED = 'cancelled',
}

export enum POStatus {
  DRAFT = 'draft',
  APPROVED = 'approved',
  SENT_TO_VENDOR = 'sent_to_vendor',
  ACKNOWLEDGED = 'acknowledged',
  IN_PROGRESS = 'in_progress',
  PARTIALLY_RECEIVED = 'partially_received',
  FULLY_RECEIVED = 'fully_received',
  CLOSED = 'closed',
  CANCELLED = 'cancelled',
}

export enum GRNStatus {
  DRAFT = 'draft',
  RECEIVED = 'received',
  QUALITY_CHECK_PENDING = 'quality_check_pending',
  QUALITY_CHECK_PASSED = 'quality_check_passed',
  QUALITY_CHECK_FAILED = 'quality_check_failed',
  ACCEPTED = 'accepted',
  REJECTED = 'rejected',
  PARTIALLY_ACCEPTED = 'partially_accepted',
}

export enum InvoiceStatus {
  DRAFT = 'draft',
  SUBMITTED = 'submitted',
  UNDER_VERIFICATION = 'under_verification',
  MATCHED = 'matched',
  MISMATCH = 'mismatch',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  PAID = 'paid',
  PARTIALLY_PAID = 'partially_paid',
}

export enum InvoiceMatchingStatus {
  NOT_MATCHED = 'not_matched',
  TWO_WAY_MATCHED = 'two_way_matched',
  THREE_WAY_MATCHED = 'three_way_matched',
  PRICE_MISMATCH = 'price_mismatch',
  QUANTITY_MISMATCH = 'quantity_mismatch',
  TOLERANCE_MISMATCH = 'tolerance_mismatch',
}

// ============================================================================
// VENDOR TYPES
// ============================================================================

export interface Vendor {
  id: string;
  vendor_code: string;
  vendor_name: string;
  vendor_type: VendorType;
  status: VendorStatus;
  contact_person?: string;
  email?: string;
  phone?: string;
  mobile?: string;
  website?: string;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  pincode?: string;
  country: string;
  pan_number?: string;
  gst_number?: string;
  tan_number?: string;
  msme_registration?: string;
  bank_name?: string;
  bank_branch?: string;
  account_number?: string;
  ifsc_code?: string;
  account_holder_name?: string;
  payment_terms: PaymentTerms;
  credit_limit: number;
  credit_period_days: number;
  overall_rating: number;
  quality_rating: number;
  delivery_rating: number;
  price_rating: number;
  service_rating: number;
  total_orders: number;
  on_time_deliveries: number;
  products_services?: string;
  notes?: string;
  blacklist_reason?: string;
  created_at: string;
  updated_at: string;
}

export interface VendorFormData {
  vendor_name: string;
  vendor_type: VendorType;
  status: VendorStatus;
  contact_person?: string;
  email?: string;
  phone?: string;
  mobile?: string;
  website?: string;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  pincode?: string;
  country: string;
  pan_number?: string;
  gst_number?: string;
  tan_number?: string;
  msme_registration?: string;
  bank_name?: string;
  bank_branch?: string;
  account_number?: string;
  ifsc_code?: string;
  account_holder_name?: string;
  payment_terms: PaymentTerms;
  credit_limit: number;
  credit_period_days: number;
  products_services?: string;
  notes?: string;
}

export interface VendorRating {
  id: string;
  vendor_id: string;
  po_id?: string;
  rating_date: string;
  rating_period_start?: string;
  rating_period_end?: string;
  quality_rating: number;
  delivery_rating: number;
  price_rating: number;
  service_rating: number;
  communication_rating: number;
  overall_rating: number;
  delivery_status?: string;
  days_late: number;
  defect_percentage: number;
  rejection_percentage: number;
  positive_points?: string;
  improvement_areas?: string;
  remarks?: string;
  rated_by: string;
  rated_by_name: string;
  created_at: string;
  updated_at: string;
}

// ============================================================================
// REQUISITION TYPES
// ============================================================================

export interface PurchaseRequisitionItem {
  id?: string;
  item_code?: string;
  item_name: string;
  description?: string;
  specification?: string;
  quantity: number;
  unit_of_measure: string;
  estimated_unit_price?: number;
  estimated_total_price?: number;
  notes?: string;
  quantity_converted?: number;
}

export interface PurchaseRequisition {
  id: string;
  requisition_number: string;
  requisition_date: string;
  required_by_date: string;
  status: RequisitionStatus;
  priority: RequisitionPriority;
  department: string;
  requester_id: string;
  requester_name: string;
  purpose: string;
  justification?: string;
  budget_code?: string;
  estimated_total: number;
  preferred_vendor_id?: string;
  approved_by?: string;
  approved_at?: string;
  rejection_reason?: string;
  items: PurchaseRequisitionItem[];
  created_at: string;
  updated_at: string;
}

export interface PurchaseRequisitionFormData {
  required_by_date: string;
  priority: RequisitionPriority;
  department: string;
  purpose: string;
  justification?: string;
  budget_code?: string;
  estimated_total: number;
  preferred_vendor_id?: string;
  items: PurchaseRequisitionItem[];
}

// ============================================================================
// PURCHASE ORDER TYPES
// ============================================================================

export interface PurchaseOrderItem {
  id?: string;
  item_code?: string;
  item_name: string;
  description?: string;
  specification?: string;
  ordered_quantity: number;
  received_quantity?: number;
  unit_of_measure: string;
  unit_price: number;
  total_price: number;
  tax_percentage: number;
  tax_amount: number;
  discount_percentage: number;
  discount_amount: number;
  net_amount: number;
  rfq_item_id?: string;
  requisition_item_id?: string;
}

export interface PurchaseOrder {
  id: string;
  po_number: string;
  po_date: string;
  expected_delivery_date: string;
  status: POStatus;
  vendor_id: string;
  rfq_id?: string;
  requisition_id?: string;
  delivery_address_line1?: string;
  delivery_address_line2?: string;
  delivery_city?: string;
  delivery_state?: string;
  delivery_pincode?: string;
  delivery_country: string;
  delivery_contact_person?: string;
  delivery_contact_phone?: string;
  subtotal: number;
  tax_amount: number;
  discount_amount: number;
  total_amount: number;
  payment_terms: PaymentTerms;
  advance_payment_percentage: number;
  advance_payment_amount: number;
  terms_and_conditions?: string;
  special_instructions?: string;
  approved_by?: string;
  approved_at?: string;
  acknowledged_by_vendor: boolean;
  acknowledged_at?: string;
  items: PurchaseOrderItem[];
  created_at: string;
  updated_at: string;
}

// ============================================================================
// API RESPONSE TYPES
// ============================================================================

export interface ApiResponse<T> {
  success: boolean;
  message?: string;
  data?: T;
  error?: string;
  detail?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface DashboardMetrics {
  total_vendors: number;
  active_vendors: number;
  total_requisitions: number;
  pending_approvals: number;
  active_rfqs: number;
  open_purchase_orders: number;
  pending_grns: number;
  pending_invoices: number;
  total_procurement_value: number;
  monthly_procurement_value: number;
}
