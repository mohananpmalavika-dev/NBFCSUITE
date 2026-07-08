/**
 * Grievance & Complaint Management - TypeScript Types
 */

// ============================================================================
// ENUMS
// ============================================================================

export enum ComplaintStatus {
  REGISTERED = 'REGISTERED',
  ACKNOWLEDGED = 'ACKNOWLEDGED',
  IN_PROGRESS = 'IN_PROGRESS',
  UNDER_REVIEW = 'UNDER_REVIEW',
  RESOLVED = 'RESOLVED',
  CLOSED = 'CLOSED',
  REOPENED = 'REOPENED',
  ESCALATED = 'ESCALATED',
  REJECTED = 'REJECTED',
}

export enum ComplaintPriority {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  CRITICAL = 'CRITICAL',
  URGENT = 'URGENT',
}

export enum ComplaintCategory {
  PRODUCT_SERVICE = 'PRODUCT_SERVICE',
  ACCOUNT_MANAGEMENT = 'ACCOUNT_MANAGEMENT',
  LOAN_DISBURSEMENT = 'LOAN_DISBURSEMENT',
  COLLECTION_HARASSMENT = 'COLLECTION_HARASSMENT',
  INTEREST_CHARGES = 'INTEREST_CHARGES',
  DOCUMENT_ISSUES = 'DOCUMENT_ISSUES',
  BRANCH_SERVICE = 'BRANCH_SERVICE',
  DIGITAL_BANKING = 'DIGITAL_BANKING',
  STAFF_BEHAVIOR = 'STAFF_BEHAVIOR',
  FRAUD_SECURITY = 'FRAUD_SECURITY',
  REGULATORY = 'REGULATORY',
  OTHER = 'OTHER',
}

export enum ChannelType {
  EMAIL = 'EMAIL',
  PHONE = 'PHONE',
  WEB_PORTAL = 'WEB_PORTAL',
  MOBILE_APP = 'MOBILE_APP',
  BRANCH_VISIT = 'BRANCH_VISIT',
  SOCIAL_MEDIA = 'SOCIAL_MEDIA',
  LETTER = 'LETTER',
  SMS = 'SMS',
  WHATSAPP = 'WHATSAPP',
  CHATBOT = 'CHATBOT',
}

export enum EscalationLevel {
  LEVEL_0 = 'LEVEL_0',
  LEVEL_1 = 'LEVEL_1',
  LEVEL_2 = 'LEVEL_2',
  LEVEL_3 = 'LEVEL_3',
  LEVEL_4 = 'LEVEL_4',
  LEVEL_5 = 'LEVEL_5',
  OMBUDSMAN = 'OMBUDSMAN',
}

export enum OmbudsmanStatus {
  PENDING = 'PENDING',
  SUBMITTED = 'SUBMITTED',
  UNDER_REVIEW = 'UNDER_REVIEW',
  HEARING_SCHEDULED = 'HEARING_SCHEDULED',
  AWARD_ISSUED = 'AWARD_ISSUED',
  CLOSED = 'CLOSED',
  WITHDRAWN = 'WITHDRAWN',
}

// ============================================================================
// LABEL MAPPINGS
// ============================================================================

export const ComplaintStatusLabels: Record<ComplaintStatus, string> = {
  [ComplaintStatus.REGISTERED]: 'Registered',
  [ComplaintStatus.ACKNOWLEDGED]: 'Acknowledged',
  [ComplaintStatus.IN_PROGRESS]: 'In Progress',
  [ComplaintStatus.UNDER_REVIEW]: 'Under Review',
  [ComplaintStatus.RESOLVED]: 'Resolved',
  [ComplaintStatus.CLOSED]: 'Closed',
  [ComplaintStatus.REOPENED]: 'Reopened',
  [ComplaintStatus.ESCALATED]: 'Escalated',
  [ComplaintStatus.REJECTED]: 'Rejected',
};

export const ComplaintPriorityLabels: Record<ComplaintPriority, string> = {
  [ComplaintPriority.LOW]: 'Low',
  [ComplaintPriority.MEDIUM]: 'Medium',
  [ComplaintPriority.HIGH]: 'High',
  [ComplaintPriority.CRITICAL]: 'Critical',
  [ComplaintPriority.URGENT]: 'Urgent',
};

export const ComplaintCategoryLabels: Record<ComplaintCategory, string> = {
  [ComplaintCategory.PRODUCT_SERVICE]: 'Product/Service',
  [ComplaintCategory.ACCOUNT_MANAGEMENT]: 'Account Management',
  [ComplaintCategory.LOAN_DISBURSEMENT]: 'Loan Disbursement',
  [ComplaintCategory.COLLECTION_HARASSMENT]: 'Collection Harassment',
  [ComplaintCategory.INTEREST_CHARGES]: 'Interest Charges',
  [ComplaintCategory.DOCUMENT_ISSUES]: 'Document Issues',
  [ComplaintCategory.BRANCH_SERVICE]: 'Branch Service',
  [ComplaintCategory.DIGITAL_BANKING]: 'Digital Banking',
  [ComplaintCategory.STAFF_BEHAVIOR]: 'Staff Behavior',
  [ComplaintCategory.FRAUD_SECURITY]: 'Fraud/Security',
  [ComplaintCategory.REGULATORY]: 'Regulatory',
  [ComplaintCategory.OTHER]: 'Other',
};

export const ChannelTypeLabels: Record<ChannelType, string> = {
  [ChannelType.EMAIL]: 'Email',
  [ChannelType.PHONE]: 'Phone',
  [ChannelType.WEB_PORTAL]: 'Web Portal',
  [ChannelType.MOBILE_APP]: 'Mobile App',
  [ChannelType.BRANCH_VISIT]: 'Branch Visit',
  [ChannelType.SOCIAL_MEDIA]: 'Social Media',
  [ChannelType.LETTER]: 'Letter',
  [ChannelType.SMS]: 'SMS',
  [ChannelType.WHATSAPP]: 'WhatsApp',
  [ChannelType.CHATBOT]: 'Chatbot',
};

export const EscalationLevelLabels: Record<EscalationLevel, string> = {
  [EscalationLevel.LEVEL_0]: 'Level 0 - Initial',
  [EscalationLevel.LEVEL_1]: 'Level 1 - Team Lead',
  [EscalationLevel.LEVEL_2]: 'Level 2 - Manager',
  [EscalationLevel.LEVEL_3]: 'Level 3 - Senior Manager',
  [EscalationLevel.LEVEL_4]: 'Level 4 - Head of Department',
  [EscalationLevel.LEVEL_5]: 'Level 5 - Executive',
  [EscalationLevel.OMBUDSMAN]: 'Ombudsman',
};

export const OmbudsmanStatusLabels: Record<OmbudsmanStatus, string> = {
  [OmbudsmanStatus.PENDING]: 'Pending',
  [OmbudsmanStatus.SUBMITTED]: 'Submitted',
  [OmbudsmanStatus.UNDER_REVIEW]: 'Under Review',
  [OmbudsmanStatus.HEARING_SCHEDULED]: 'Hearing Scheduled',
  [OmbudsmanStatus.AWARD_ISSUED]: 'Award Issued',
  [OmbudsmanStatus.CLOSED]: 'Closed',
  [OmbudsmanStatus.WITHDRAWN]: 'Withdrawn',
};

// ============================================================================
// COLOR MAPPINGS
// ============================================================================

export const ComplaintStatusColors: Record<ComplaintStatus, string> = {
  [ComplaintStatus.REGISTERED]: 'bg-blue-100 text-blue-800',
  [ComplaintStatus.ACKNOWLEDGED]: 'bg-cyan-100 text-cyan-800',
  [ComplaintStatus.IN_PROGRESS]: 'bg-yellow-100 text-yellow-800',
  [ComplaintStatus.UNDER_REVIEW]: 'bg-orange-100 text-orange-800',
  [ComplaintStatus.RESOLVED]: 'bg-green-100 text-green-800',
  [ComplaintStatus.CLOSED]: 'bg-gray-100 text-gray-800',
  [ComplaintStatus.REOPENED]: 'bg-purple-100 text-purple-800',
  [ComplaintStatus.ESCALATED]: 'bg-red-100 text-red-800',
  [ComplaintStatus.REJECTED]: 'bg-red-100 text-red-800',
};

export const ComplaintPriorityColors: Record<ComplaintPriority, string> = {
  [ComplaintPriority.LOW]: 'bg-green-100 text-green-800',
  [ComplaintPriority.MEDIUM]: 'bg-yellow-100 text-yellow-800',
  [ComplaintPriority.HIGH]: 'bg-orange-100 text-orange-800',
  [ComplaintPriority.CRITICAL]: 'bg-red-100 text-red-800',
  [ComplaintPriority.URGENT]: 'bg-red-200 text-red-900 font-bold',
};

export const ChannelTypeColors: Record<ChannelType, string> = {
  [ChannelType.EMAIL]: 'bg-blue-100 text-blue-800',
  [ChannelType.PHONE]: 'bg-green-100 text-green-800',
  [ChannelType.WEB_PORTAL]: 'bg-purple-100 text-purple-800',
  [ChannelType.MOBILE_APP]: 'bg-indigo-100 text-indigo-800',
  [ChannelType.BRANCH_VISIT]: 'bg-orange-100 text-orange-800',
  [ChannelType.SOCIAL_MEDIA]: 'bg-pink-100 text-pink-800',
  [ChannelType.LETTER]: 'bg-gray-100 text-gray-800',
  [ChannelType.SMS]: 'bg-teal-100 text-teal-800',
  [ChannelType.WHATSAPP]: 'bg-green-100 text-green-800',
  [ChannelType.CHATBOT]: 'bg-cyan-100 text-cyan-800',
};

// ============================================================================
// INTERFACES
// ============================================================================

export interface Complaint {
  id: number;
  complaint_number: string;
  customer_id: number;
  customer_name?: string;
  customer_email?: string;
  customer_phone?: string;
  related_entity_type?: string;
  related_entity_id?: number;
  category: ComplaintCategory;
  sub_category?: string;
  subject: string;
  description: string;
  channel: ChannelType;
  source_reference?: string;
  status: ComplaintStatus;
  priority: ComplaintPriority;
  assigned_to?: number;
  assigned_department?: string;
  assigned_at?: string;
  registered_date: string;
  acknowledged_date?: string;
  target_resolution_date?: string;
  actual_resolution_date?: string;
  closed_date?: string;
  sla_hours: number;
  sla_breach: boolean;
  sla_breach_hours: number;
  resolution?: string;
  resolution_remarks?: string;
  customer_satisfaction?: number;
  compensation_amount?: number;
  compensation_paid: boolean;
  escalation_level: EscalationLevel;
  escalated_to_ombudsman: boolean;
  is_regulatory: boolean;
  is_repeat: boolean;
  previous_complaint_id?: number;
  tags?: string;
  attachments?: string;
  created_by?: number;
  updated_by?: number;
  created_at: string;
  updated_at: string;
}

export interface ComplaintChannel {
  id: number;
  complaint_id: number;
  channel_type: ChannelType;
  communication_date: string;
  direction: string;
  subject?: string;
  message: string;
  response?: string;
  from_address?: string;
  to_address?: string;
  is_customer_initiated: boolean;
  requires_response: boolean;
  response_sent: boolean;
  attachments?: string;
  handled_by?: number;
  created_at: string;
}

export interface ComplaintEscalation {
  id: number;
  complaint_id: number;
  escalation_level: EscalationLevel;
  escalation_number: number;
  escalation_reason: string;
  reason_details?: string;
  is_auto_escalated: boolean;
  escalated_from?: number;
  escalated_to: number;
  escalated_to_department?: string;
  escalated_at: string;
  acknowledged_at?: string;
  resolved_at?: string;
  escalation_sla_hours: number;
  escalation_sla_breach: boolean;
  status: string;
  resolution_notes?: string;
  action_taken?: string;
  created_by?: number;
  created_at: string;
  updated_at: string;
}

export interface OmbudsmanCase {
  id: number;
  complaint_id: number;
  ombudsman_case_number: string;
  ombudsman_office: string;
  submitted_date?: string;
  submission_reference?: string;
  grounds_of_complaint: string;
  documents_submitted?: string;
  supporting_evidence?: string;
  status: OmbudsmanStatus;
  acknowledgement_date?: string;
  hearing_date?: string;
  award_date?: string;
  closure_date?: string;
  award_details?: string;
  compensation_awarded?: number;
  compensation_paid: boolean;
  compensation_paid_date?: string;
  bank_response?: string;
  bank_response_date?: string;
  bank_representative?: string;
  is_appealed: boolean;
  appeal_filed_by?: string;
  appeal_date?: string;
  appeal_outcome?: string;
  rbi_guidelines_followed: boolean;
  resolution_within_30_days?: boolean;
  notes?: string;
  internal_remarks?: string;
  created_by?: number;
  updated_by?: number;
  created_at: string;
  updated_at: string;
}

export interface ComplaintStatistics {
  total_complaints: number;
  registered: number;
  in_progress: number;
  resolved: number;
  closed: number;
  escalated: number;
  sla_breached: number;
  within_sla: number;
  by_priority: Record<string, number>;
  by_category: Record<string, number>;
  by_channel: Record<string, number>;
  by_status: Record<string, number>;
  avg_resolution_hours: number;
  customer_satisfaction_avg: number;
  escalation_rate: number;
  ombudsman_cases: number;
}

// ============================================================================
// CREATE/UPDATE TYPES
// ============================================================================

export interface ComplaintCreateInput {
  customer_id: number;
  customer_name?: string;
  customer_email?: string;
  customer_phone?: string;
  related_entity_type?: string;
  related_entity_id?: number;
  category: ComplaintCategory;
  sub_category?: string;
  subject: string;
  description: string;
  channel: ChannelType;
  source_reference?: string;
  priority?: ComplaintPriority;
  tags?: string;
  attachments?: string;
}

export interface ComplaintUpdateInput {
  subject?: string;
  description?: string;
  category?: ComplaintCategory;
  sub_category?: string;
  priority?: ComplaintPriority;
  status?: ComplaintStatus;
  assigned_to?: number;
  assigned_department?: string;
  resolution?: string;
  resolution_remarks?: string;
  tags?: string;
}

export interface ComplaintAssignInput {
  assigned_to: number;
  assigned_department?: string;
  remarks?: string;
}

export interface ComplaintAcknowledgeInput {
  acknowledgement_message: string;
  expected_resolution_days?: number;
}

export interface ComplaintResolveInput {
  resolution: string;
  resolution_remarks?: string;
  compensation_amount?: number;
}

export interface ComplaintCloseInput {
  closure_remarks?: string;
  customer_satisfaction?: number;
}

export interface ComplaintReopenInput {
  reopen_reason: string;
}

export interface EscalationCreateInput {
  complaint_id: number;
  escalation_level: EscalationLevel;
  escalation_reason: string;
  reason_details?: string;
  escalated_to: number;
  escalated_to_department?: string;
  is_auto_escalated?: boolean;
}

export interface OmbudsmanCaseCreateInput {
  complaint_id: number;
  ombudsman_case_number: string;
  ombudsman_office: string;
  grounds_of_complaint: string;
  documents_submitted?: string;
  supporting_evidence?: string;
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

export const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
};

export const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(date);
};

export const formatDateTime = (dateString: string): string => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
};

export const calculateDaysElapsed = (startDate: string): number => {
  const start = new Date(startDate);
  const now = new Date();
  const diffTime = Math.abs(now.getTime() - start.getTime());
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return diffDays;
};

export const calculateHoursElapsed = (startDate: string): number => {
  const start = new Date(startDate);
  const now = new Date();
  const diffTime = Math.abs(now.getTime() - start.getTime());
  const diffHours = Math.ceil(diffTime / (1000 * 60 * 60));
  return diffHours;
};

export const isSLABreached = (
  targetDate: string | undefined,
  actualDate?: string
): boolean => {
  if (!targetDate) return false;
  
  const target = new Date(targetDate);
  const comparison = actualDate ? new Date(actualDate) : new Date();
  
  return comparison > target;
};

export const getSLAStatus = (complaint: Complaint): {
  status: 'within' | 'breached' | 'nearing';
  color: string;
  label: string;
} => {
  if (complaint.sla_breach) {
    return {
      status: 'breached',
      color: 'text-red-600',
      label: `Breached by ${complaint.sla_breach_hours}h`,
    };
  }
  
  if (complaint.target_resolution_date) {
    const hoursRemaining = calculateHoursRemaining(complaint.target_resolution_date);
    if (hoursRemaining <= 4) {
      return {
        status: 'nearing',
        color: 'text-orange-600',
        label: `${hoursRemaining}h remaining`,
      };
    }
  }
  
  return {
    status: 'within',
    color: 'text-green-600',
    label: 'Within SLA',
  };
};

export const calculateHoursRemaining = (targetDate: string): number => {
  const target = new Date(targetDate);
  const now = new Date();
  const diffTime = target.getTime() - now.getTime();
  const diffHours = Math.floor(diffTime / (1000 * 60 * 60));
  return Math.max(0, diffHours);
};

export const getCustomerSatisfactionLabel = (rating: number): string => {
  const labels = {
    1: 'Very Unsatisfied',
    2: 'Unsatisfied',
    3: 'Neutral',
    4: 'Satisfied',
    5: 'Very Satisfied',
  };
  return labels[rating as keyof typeof labels] || 'Unknown';
};

export const getCustomerSatisfactionColor = (rating: number): string => {
  if (rating >= 4) return 'text-green-600';
  if (rating === 3) return 'text-yellow-600';
  return 'text-red-600';
};
