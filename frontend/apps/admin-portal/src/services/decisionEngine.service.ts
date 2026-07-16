/**
 * Instant Decision Framework Service
 * Real-time decisioning with parallel async checks
 */
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

// =====================================================================
// TYPES & INTERFACES
// =====================================================================

export enum DecisionStatus {
  PENDING = 'PENDING',
  IN_PROGRESS = 'IN_PROGRESS',
  COMPLETED = 'COMPLETED',
  FAILED = 'FAILED'
}

export enum DecisionOutcome {
  APPROVED = 'APPROVED',
  APPROVED_WITH_CONDITIONS = 'APPROVED_WITH_CONDITIONS',
  DECLINED = 'DECLINED',
  MANUAL_REVIEW = 'MANUAL_REVIEW'
}

export enum CheckStatus {
  PENDING = 'PENDING',
  IN_PROGRESS = 'IN_PROGRESS',
  COMPLETED = 'COMPLETED',
  FAILED = 'FAILED',
  SKIPPED = 'SKIPPED'
}

export enum CheckResult {
  PASS = 'PASS',
  FAIL = 'FAIL',
  WARNING = 'WARNING',
  NOT_APPLICABLE = 'NOT_APPLICABLE'
}

export enum BureauProvider {
  CIBIL = 'CIBIL',
  EXPERIAN = 'EXPERIAN',
  EQUIFAX = 'EQUIFAX',
  CRIF = 'CRIF'
}

export enum FraudRiskLevel {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  CRITICAL = 'CRITICAL'
}

export enum DeclineReason {
  LOW_CREDIT_SCORE = 'LOW_CREDIT_SCORE',
  HIGH_DTI = 'HIGH_DTI',
  INSUFFICIENT_INCOME = 'INSUFFICIENT_INCOME',
  EMPLOYMENT_ISSUES = 'EMPLOYMENT_ISSUES',
  ADVERSE_CREDIT_HISTORY = 'ADVERSE_CREDIT_HISTORY',
  KYC_VERIFICATION_FAILED = 'KYC_VERIFICATION_FAILED',
  FRAUD_DETECTED = 'FRAUD_DETECTED',
  ELIGIBILITY_NOT_MET = 'ELIGIBILITY_NOT_MET',
  POLICY_VIOLATION = 'POLICY_VIOLATION'
}

// Main Decision Request interface
export interface DecisionRequest {
  id: string;
  tenant_id: string;
  application_id: string;
  customer_id: string;
  product_id: string;
  loan_amount: number;
  tenure_months: number;
  purpose?: string;
  applicant_data: Record<string, any>;
  status: DecisionStatus;
  decision_outcome?: DecisionOutcome;
  decision_score?: number;
  confidence_score?: number;
  approved_amount?: number;
  approved_rate?: number;
  decline_reasons?: string[];
  conditions?: string[];
  requires_manual_review: boolean;
  manual_review_reason?: string;
  fraud_score?: number;
  fraud_risk_level?: FraudRiskLevel;
  fraud_indicators?: string[];
  total_checks: number;
  passed_checks: number;
  failed_checks: number;
  warning_checks: number;
  request_time: string;
  start_time?: string;
  end_time?: string;
  total_duration_ms?: number;
  created_at: string;
  updated_at: string;
  created_by?: string;
}

// Bureau Check interface
export interface BureauCheck {
  id: string;
  decision_request_id: string;
  tenant_id: string;
  bureau_provider: BureauProvider;
  status: CheckStatus;
  result?: CheckResult;
  credit_score?: number;
  total_accounts?: number;
  active_accounts?: number;
  total_outstanding?: number;
  credit_utilization?: number;
  max_dpd_last_12m?: number;
  enquiries_last_6m?: number;
  start_time: string;
  end_time?: string;
  duration_ms?: number;
  error_message?: string;
  raw_response?: Record<string, any>;
  created_at: string;
}

// Bank Statement Analysis interface
export interface BankStatementAnalysis {
  id: string;
  decision_request_id: string;
  tenant_id: string;
  status: CheckStatus;
  result?: CheckResult;
  statement_period_months?: number;
  bank_name?: string;
  account_number_masked?: string;
  average_monthly_credit?: number;
  salary_credits_count?: number;
  salary_amount?: number;
  salary_regularity_score?: number;
  average_monthly_debit?: number;
  emi_deductions?: number;
  average_balance?: number;
  minimum_balance?: number;
  bounced_cheques_count?: number;
  banking_behavior_score?: number;
  calculated_monthly_income?: number;
  calculated_monthly_obligations?: number;
  calculated_dti?: number;
  start_time: string;
  end_time?: string;
  duration_ms?: number;
  error_message?: string;
  insights?: Record<string, any>;
  created_at: string;
}

// KYC Verification interface
export interface KYCVerification {
  id: string;
  decision_request_id: string;
  tenant_id: string;
  status: CheckStatus;
  result?: CheckResult;
  aadhaar_verified: boolean;
  aadhaar_name_match: boolean;
  aadhaar_address_match: boolean;
  aadhaar_dob_match: boolean;
  pan_verified: boolean;
  pan_name_match: boolean;
  pan_dob_match: boolean;
  pan_status?: string;
  address_verified: boolean;
  address_match_score?: number;
  employment_verified: boolean;
  kyc_score?: number;
  start_time: string;
  end_time?: string;
  duration_ms?: number;
  error_message?: string;
  verification_details?: Record<string, any>;
  created_at: string;
}

// Fraud Check interface
export interface FraudCheck {
  id: string;
  decision_request_id: string;
  tenant_id: string;
  status: CheckStatus;
  result?: CheckResult;
  device_id?: string;
  device_type?: string;
  device_risk_score?: number;
  ip_address?: string;
  geo_country?: string;
  geo_state?: string;
  geo_city?: string;
  geo_risk_score?: number;
  applications_last_24h: number;
  applications_last_7d: number;
  applications_last_30d: number;
  velocity_risk_score?: number;
  duplicate_applications: number;
  duplicate_phone: boolean;
  duplicate_email: boolean;
  blacklisted: boolean;
  email_verified: boolean;
  email_risk_score?: number;
  phone_verified: boolean;
  phone_risk_score?: number;
  fraud_score?: number;
  fraud_risk_level?: FraudRiskLevel;
  fraud_indicators?: string[];
  start_time: string;
  end_time?: string;
  duration_ms?: number;
  error_message?: string;
  fraud_analysis?: Record<string, any>;
  created_at: string;
}

// Eligibility Check interface
export interface EligibilityCheck {
  id: string;
  decision_request_id: string;
  tenant_id: string;
  status: CheckStatus;
  result?: CheckResult;
  age: number;
  age_eligible: boolean;
  min_age: number;
  max_age: number;
  monthly_income?: number;
  income_eligible: boolean;
  min_income: number;
  monthly_obligations?: number;
  dti_ratio?: number;
  dti_eligible: boolean;
  max_dti: number;
  employment_type?: string;
  employment_duration_months?: number;
  employment_eligible: boolean;
  min_employment_months: number;
  credit_score?: number;
  credit_score_eligible: boolean;
  min_credit_score: number;
  requested_amount: number;
  amount_eligible: boolean;
  min_loan_amount: number;
  max_loan_amount: number;
  geography_eligible: boolean;
  product_rules_passed: boolean;
  policy_rules_passed: boolean;
  overall_eligible: boolean;
  failed_criteria?: string[];
  eligibility_score?: number;
  start_time: string;
  end_time?: string;
  duration_ms?: number;
  error_message?: string;
  created_at: string;
}

// Decision Audit interface
export interface DecisionAudit {
  id: string;
  decision_request_id: string;
  tenant_id: string;
  action: string;
  details: string;
  timestamp: string;
}

// Decision Details (full) interface
export interface DecisionDetails {
  decision: DecisionRequest;
  bureau_checks: BureauCheck[];
  bank_analysis: BankStatementAnalysis[];
  kyc_verification: KYCVerification[];
  fraud_checks: FraudCheck[];
  eligibility_checks: EligibilityCheck[];
  audit_trail: DecisionAudit[];
}

// Decision Statistics interface
export interface DecisionStatistics {
  total_decisions: number;
  approved: number;
  approved_with_conditions: number;
  declined: number;
  manual_review: number;
  approval_rate: number;
  avg_decision_score: number;
  avg_confidence_score: number;
  avg_processing_time_ms: number;
  fraud_risk_distribution: Record<string, number>;
}

// Dashboard Summary interface
export interface DashboardSummary {
  today_stats: DecisionStatistics;
  pending_decisions: number;
  needs_manual_review: number;
  recent_decisions: DecisionRequest[];
}

// Create Decision Request input
export interface CreateDecisionRequest {
  application_id: string;
  customer_id: string;
  product_id: string;
  loan_amount: number;
  tenure_months: number;
  purpose?: string;
  applicant_data: {
    // Personal info
    age?: number;
    monthly_income?: number;
    monthly_obligations?: number;
    employment_type?: string;
    employment_duration?: number;
    employment_verified?: boolean;
    
    // Credit info
    credit_score?: number;
    total_accounts?: number;
    active_accounts?: number;
    total_outstanding?: number;
    credit_utilization?: number;
    max_dpd_last_12m?: number;
    enquiries_last_6m?: number;
    
    // Location
    state?: string;
    city?: string;
    
    // Device/Session
    device_id?: string;
    device_type?: string;
    ip_address?: string;
    
    // Other
    [key: string]: any;
  };
}

// API Response wrapper
interface ApiResponse<T> {
  success: boolean;
  message?: string;
  data: T;
}

// =====================================================================
// SERVICE CLASS
// =====================================================================

class DecisionEngineService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = `${API_BASE_URL}/api/decision-engine`;
  }

  /**
   * Submit a new decision request for instant processing
   */
  async submitDecisionRequest(request: CreateDecisionRequest): Promise<DecisionRequest> {
    const response = await axios.post<ApiResponse<any>>(
      `${this.baseUrl}/decisions`,
      request
    );
    return response.data.data;
  }

  /**
   * List decision requests with filters
   */
  async listDecisions(params?: {
    skip?: number;
    limit?: number;
    status?: DecisionStatus;
    outcome?: DecisionOutcome;
    customer_id?: string;
    from_date?: string;
    to_date?: string;
  }): Promise<{ data: DecisionRequest[]; pagination: any }> {
    const response = await axios.get<ApiResponse<DecisionRequest[]>>(
      `${this.baseUrl}/decisions`,
      { params }
    );
    return {
      data: response.data.data,
      pagination: (response.data as any).pagination
    };
  }

  /**
   * Get decision by ID
   */
  async getDecision(decisionId: string): Promise<DecisionRequest> {
    const response = await axios.get<ApiResponse<DecisionRequest>>(
      `${this.baseUrl}/decisions/${decisionId}`
    );
    return response.data.data;
  }

  /**
   * Get complete decision details with all checks
   */
  async getDecisionDetails(decisionId: string): Promise<DecisionDetails> {
    const response = await axios.get<ApiResponse<DecisionDetails>>(
      `${this.baseUrl}/decisions/${decisionId}/details`
    );
    return response.data.data;
  }

  /**
   * Get audit trail for a decision
   */
  async getDecisionAudit(decisionId: string): Promise<DecisionAudit[]> {
    const response = await axios.get<ApiResponse<DecisionAudit[]>>(
      `${this.baseUrl}/decisions/${decisionId}/audit`
    );
    return response.data.data;
  }

  /**
   * Rerun an existing decision
   */
  async rerunDecision(decisionId: string): Promise<DecisionRequest> {
    const response = await axios.post<ApiResponse<any>>(
      `${this.baseUrl}/decisions/${decisionId}/rerun`
    );
    return response.data.data;
  }

  /**
   * Get dashboard summary
   */
  async getDashboardSummary(): Promise<DashboardSummary> {
    const response = await axios.get<ApiResponse<DashboardSummary>>(
      `${this.baseUrl}/dashboard`
    );
    return response.data.data;
  }

  /**
   * Get decision statistics
   */
  async getStatistics(params?: {
    from_date?: string;
    to_date?: string;
  }): Promise<DecisionStatistics> {
    const response = await axios.get<ApiResponse<DecisionStatistics>>(
      `${this.baseUrl}/statistics`,
      { params }
    );
    return response.data.data;
  }
}

// =====================================================================
// HELPER FUNCTIONS
// =====================================================================

/**
 * Format decision outcome for display
 */
export const formatDecisionOutcome = (outcome?: DecisionOutcome): string => {
  if (!outcome) return 'N/A';
  
  const outcomeMap: Record<DecisionOutcome, string> = {
    [DecisionOutcome.APPROVED]: 'Approved',
    [DecisionOutcome.APPROVED_WITH_CONDITIONS]: 'Approved (Conditions)',
    [DecisionOutcome.DECLINED]: 'Declined',
    [DecisionOutcome.MANUAL_REVIEW]: 'Manual Review'
  };
  
  return outcomeMap[outcome] || outcome;
};

/**
 * Get color for decision outcome
 */
export const getDecisionOutcomeColor = (outcome?: DecisionOutcome): string => {
  if (!outcome) return 'default';
  
  const colorMap: Record<DecisionOutcome, string> = {
    [DecisionOutcome.APPROVED]: 'success',
    [DecisionOutcome.APPROVED_WITH_CONDITIONS]: 'info',
    [DecisionOutcome.DECLINED]: 'error',
    [DecisionOutcome.MANUAL_REVIEW]: 'warning'
  };
  
  return colorMap[outcome] || 'default';
};

/**
 * Format check result for display
 */
export const formatCheckResult = (result?: CheckResult): string => {
  if (!result) return 'N/A';
  
  const resultMap: Record<CheckResult, string> = {
    [CheckResult.PASS]: 'Pass',
    [CheckResult.FAIL]: 'Fail',
    [CheckResult.WARNING]: 'Warning',
    [CheckResult.NOT_APPLICABLE]: 'N/A'
  };
  
  return resultMap[result] || result;
};

/**
 * Get color for check result
 */
export const getCheckResultColor = (result?: CheckResult): string => {
  if (!result) return 'default';
  
  const colorMap: Record<CheckResult, string> = {
    [CheckResult.PASS]: 'success',
    [CheckResult.FAIL]: 'error',
    [CheckResult.WARNING]: 'warning',
    [CheckResult.NOT_APPLICABLE]: 'default'
  };
  
  return colorMap[result] || 'default';
};

/**
 * Format fraud risk level for display
 */
export const formatFraudRiskLevel = (level?: FraudRiskLevel): string => {
  if (!level) return 'N/A';
  
  const levelMap: Record<FraudRiskLevel, string> = {
    [FraudRiskLevel.LOW]: 'Low',
    [FraudRiskLevel.MEDIUM]: 'Medium',
    [FraudRiskLevel.HIGH]: 'High',
    [FraudRiskLevel.CRITICAL]: 'Critical'
  };
  
  return levelMap[level] || level;
};

/**
 * Get color for fraud risk level
 */
export const getFraudRiskColor = (level?: FraudRiskLevel): string => {
  if (!level) return 'default';
  
  const colorMap: Record<FraudRiskLevel, string> = {
    [FraudRiskLevel.LOW]: 'success',
    [FraudRiskLevel.MEDIUM]: 'warning',
    [FraudRiskLevel.HIGH]: 'error',
    [FraudRiskLevel.CRITICAL]: 'error'
  };
  
  return colorMap[level] || 'default';
};

/**
 * Format duration (milliseconds to readable format)
 */
export const formatDuration = (durationMs?: number): string => {
  if (!durationMs) return 'N/A';
  
  if (durationMs < 1000) {
    return `${durationMs}ms`;
  }
  
  const seconds = (durationMs / 1000).toFixed(2);
  return `${seconds}s`;
};

/**
 * Calculate approval rate percentage
 */
export const calculateApprovalRate = (
  approved: number,
  approvedWithConditions: number,
  total: number
): number => {
  if (total === 0) return 0;
  return ((approved + approvedWithConditions) / total) * 100;
};

/**
 * Format score with color coding
 */
export const getScoreColor = (score?: number): string => {
  if (!score) return 'default';
  
  if (score >= 70) return 'success';
  if (score >= 55) return 'warning';
  if (score >= 45) return 'info';
  return 'error';
};

/**
 * Format decision status for display
 */
export const formatDecisionStatus = (status: DecisionStatus): string => {
  const statusMap: Record<DecisionStatus, string> = {
    [DecisionStatus.PENDING]: 'Pending',
    [DecisionStatus.IN_PROGRESS]: 'In Progress',
    [DecisionStatus.COMPLETED]: 'Completed',
    [DecisionStatus.FAILED]: 'Failed'
  };
  
  return statusMap[status] || status;
};

/**
 * Get color for decision status
 */
export const getDecisionStatusColor = (status: DecisionStatus): string => {
  const colorMap: Record<DecisionStatus, string> = {
    [DecisionStatus.PENDING]: 'default',
    [DecisionStatus.IN_PROGRESS]: 'info',
    [DecisionStatus.COMPLETED]: 'success',
    [DecisionStatus.FAILED]: 'error'
  };
  
  return colorMap[status] || 'default';
};

// Export service instance
export const decisionEngineService = new DecisionEngineService();
export default decisionEngineService;
