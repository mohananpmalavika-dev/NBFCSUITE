/**
 * Document Management System (DMS) Types
 * TypeScript types for document management
 */

// ============================================================================
// ENUMS
// ============================================================================

export enum DocumentType {
  LOAN_APPLICATION = "loan_application",
  KYC_DOCUMENT = "kyc_document",
  INCOME_PROOF = "income_proof",
  PROPERTY_DOCUMENT = "property_document",
  AGREEMENT = "agreement",
  SANCTION_LETTER = "sanction_letter",
  DISBURSEMENT_LETTER = "disbursement_letter",
  INSURANCE_DOCUMENT = "insurance_document",
  LEGAL_DOCUMENT = "legal_document",
  FINANCIAL_STATEMENT = "financial_statement",
  CORRESPONDENCE = "correspondence",
  INTERNAL_MEMO = "internal_memo",
  COMPLIANCE_DOCUMENT = "compliance_document",
  REPORT = "report",
  POLICY = "policy",
  CONTRACT = "contract",
  INVOICE = "invoice",
  RECEIPT = "receipt",
  OTHER = "other"
}

export enum DocumentStatus {
  DRAFT = "draft",
  PENDING_REVIEW = "pending_review",
  UNDER_REVIEW = "under_review",
  APPROVED = "approved",
  REJECTED = "rejected",
  ARCHIVED = "archived",
  EXPIRED = "expired"
}

export enum AccessLevel {
  PRIVATE = "private",
  INTERNAL = "internal",
  RESTRICTED = "restricted",
  PUBLIC = "public"
}

export enum PermissionType {
  VIEW = "view",
  DOWNLOAD = "download",
  EDIT = "edit",
  DELETE = "delete",
  SHARE = "share",
  FULL_ACCESS = "full_access"
}

export enum WorkflowStatus {
  PENDING = "pending",
  IN_PROGRESS = "in_progress",
  APPROVED = "approved",
  REJECTED = "rejected",
  CANCELLED = "cancelled"
}

export enum ApprovalStatus {
  PENDING = "pending",
  APPROVED = "approved",
  REJECTED = "rejected",
  DELEGATED = "delegated",
  SKIPPED = "skipped"
}

export enum SignatureStatus {
  PENDING = "pending",
  SIGNED = "signed",
  DECLINED = "declined",
  EXPIRED = "expired"
}

export enum AuditAction {
  CREATED = "created",
  UPDATED = "updated",
  DELETED = "deleted",
  VIEWED = "viewed",
  DOWNLOADED = "downloaded",
  SHARED = "shared",
  VERSION_UPLOADED = "version_uploaded",
  WORKFLOW_STARTED = "workflow_started",
  APPROVED = "approved",
  REJECTED = "rejected",
  SIGNED = "signed",
  PERMISSION_GRANTED = "permission_granted",
  PERMISSION_REVOKED = "permission_revoked"
}

// ============================================================================
// DOCUMENT INTERFACES
// ============================================================================

export interface Document {
  id: number;
  title: string;
  description?: string;
  document_type: DocumentType;
  status: DocumentStatus;
  access_level: AccessLevel;
  current_version_id?: number;
  current_version_number: number;
  file_name: string;
  file_size: number;
  mime_type: string;
  file_path: string;
  file_hash: string;
  is_encrypted: boolean;
  tags?: string[];
  metadata?: Record<string, any>;
  customer_id?: number;
  loan_id?: number;
  policy_id?: number;
  reference_type?: string;
  reference_id?: number;
  expiry_date?: string;
  is_archived: boolean;
  archived_date?: string;
  tenant_id: number;
  created_by_id: number;
  created_by_name?: string;
  created_at: string;
  updated_at: string;
  updated_by_id?: number;
  updated_by_name?: string;
  
  // Relationships
  current_version?: DocumentVersion;
  versions?: DocumentVersion[];
  permissions?: DocumentPermission[];
  comments?: DocumentComment[];
  audit_logs?: DocumentAuditLog[];
  workflows?: DocumentWorkflow[];
  signatures?: DocumentSignature[];
}

export interface DocumentVersion {
  id: number;
  document_id: number;
  version_number: number;
  file_name: string;
  file_size: number;
  mime_type: string;
  file_path: string;
  file_hash: string;
  change_description?: string;
  is_current: boolean;
  uploaded_by_id: number;
  uploaded_by_name?: string;
  uploaded_at: string;
  tenant_id: number;
}

export interface DocumentPermission {
  id: number;
  document_id: number;
  user_id?: number;
  role_id?: number;
  permission_type: PermissionType;
  granted_by_id: number;
  granted_by_name?: string;
  granted_at: string;
  expires_at?: string;
  tenant_id: number;
  
  // Additional fields
  user_name?: string;
  role_name?: string;
}

export interface DocumentComment {
  id: number;
  document_id: number;
  parent_comment_id?: number;
  comment_text: string;
  is_internal: boolean;
  mentioned_user_ids?: number[];
  created_by_id: number;
  created_by_name?: string;
  created_at: string;
  updated_at?: string;
  tenant_id: number;
  
  // Relationships
  replies?: DocumentComment[];
}

export interface DocumentAuditLog {
  id: number;
  document_id: number;
  action: AuditAction;
  action_details?: Record<string, any>;
  ip_address?: string;
  user_agent?: string;
  performed_by_id: number;
  performed_by_name?: string;
  performed_at: string;
  tenant_id: number;
}

// ============================================================================
// WORKFLOW INTERFACES
// ============================================================================

export interface WorkflowTemplate {
  id: number;
  name: string;
  description?: string;
  document_types: DocumentType[];
  stages: any[];
  is_sequential: boolean;
  auto_start: boolean;
  is_active: boolean;
  tenant_id: number;
  created_at: string;
  updated_at: string;
}

export interface DocumentWorkflow {
  id: number;
  document_id: number;
  template_id?: number;
  workflow_name: string;
  current_stage: number;
  total_stages: number;
  status: WorkflowStatus;
  stages: any[];
  initiated_by_id: number;
  initiated_by_name?: string;
  initiated_at: string;
  completed_at?: string;
  tenant_id: number;
  
  // Relationships
  document?: Document;
  template?: WorkflowTemplate;
  approvals?: DocumentApproval[];
}

export interface DocumentApproval {
  id: number;
  workflow_id: number;
  document_id: number;
  stage_number: number;
  approver_id: number;
  approver_name?: string;
  status: ApprovalStatus;
  comments?: string;
  approved_at?: string;
  due_date?: string;
  delegated_to_id?: number;
  delegated_to_name?: string;
  delegated_at?: string;
  tenant_id: number;
}

// ============================================================================
// SIGNATURE INTERFACES
// ============================================================================

export interface DocumentSignature {
  id: number;
  document_id: number;
  signer_id: number;
  signer_name?: string;
  signer_email: string;
  signature_order: number;
  status: SignatureStatus;
  signature_data?: string;
  signature_ip?: string;
  signature_location?: string;
  signed_at?: string;
  requested_at: string;
  expires_at?: string;
  declined_reason?: string;
  requested_by_id: number;
  requested_by_name?: string;
  tenant_id: number;
}

// ============================================================================
// REQUEST/RESPONSE TYPES
// ============================================================================

export interface DocumentCreate {
  title: string;
  description?: string;
  document_type: DocumentType;
  status?: DocumentStatus;
  access_level?: AccessLevel;
  customer_id?: number;
  loan_id?: number;
  policy_id?: number;
  reference_type?: string;
  reference_id?: number;
  expiry_date?: string;
  tags?: string[];
  metadata?: Record<string, any>;
  file: File;
}

export interface DocumentUpdate {
  title?: string;
  description?: string;
  document_type?: DocumentType;
  status?: DocumentStatus;
  access_level?: AccessLevel;
  customer_id?: number;
  loan_id?: number;
  policy_id?: number;
  reference_type?: string;
  reference_id?: number;
  expiry_date?: string;
  tags?: string[];
  metadata?: Record<string, any>;
}

export interface DocumentVersionCreate {
  change_description?: string;
  file: File;
}

export interface DocumentFilters {
  page?: number;
  page_size?: number;
  search?: string;
  document_type?: DocumentType;
  status?: DocumentStatus;
  access_level?: AccessLevel;
  customer_id?: number;
  loan_id?: number;
  created_by_id?: number;
  start_date?: string;
  end_date?: string;
  tags?: string[];
  has_expiry?: boolean;
  is_expired?: boolean;
  is_archived?: boolean;
}

export interface PaginatedDocumentResponse {
  items: Document[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface WorkflowCreate {
  document_id: number;
  template_id?: number;
  workflow_name?: string;
  stages?: any[];
}

export interface ApprovalAction {
  comments?: string;
}

export interface ApprovalDelegation {
  delegate_to_id: number;
  comments?: string;
}

export interface SignatureRequest {
  document_id: number;
  signers: Array<{
    signer_id: number;
    signer_email: string;
    signature_order: number;
  }>;
  expires_at?: string;
}

export interface SignatureData {
  signature_data: string;
  signature_location?: string;
}

export interface PermissionGrant {
  document_id: number;
  user_id?: number;
  role_id?: number;
  permission_type: PermissionType;
  expires_at?: string;
}

export interface BulkPermissionGrant {
  document_ids: number[];
  user_id?: number;
  role_id?: number;
  permission_type: PermissionType;
  expires_at?: string;
}

export interface CommentCreate {
  document_id: number;
  comment_text: string;
  parent_comment_id?: number;
  is_internal?: boolean;
  mentioned_user_ids?: number[];
}

// ============================================================================
// STATISTICS INTERFACES
// ============================================================================

export interface DocumentStatistics {
  total_documents: number;
  total_size_bytes: number;
  documents_by_type: Record<string, number>;
  documents_by_status: Record<string, number>;
  recent_activity_count: number;
  pending_approvals_count: number;
  pending_signatures_count: number;
  expiring_soon_count: number;
}

export interface DMSDashboardStats {
  total_documents: number;
  total_size: string;
  pending_approvals: number;
  pending_signatures: number;
  documents_by_type: Array<{ type: string; count: number }>;
  documents_by_status: Array<{ status: string; count: number }>;
  recent_activity: Array<{
    id: number;
    action: string;
    document_title: string;
    performed_by: string;
    performed_at: string;
  }>;
  expiring_documents: Array<{
    id: number;
    title: string;
    expiry_date: string;
    days_until_expiry: number;
  }>;
}
