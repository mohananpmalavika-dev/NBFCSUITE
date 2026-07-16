/**
 * Credit Policy Integration Service
 * Risk-based pricing and credit decisioning
 */
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

// =====================================================================
// TYPES & INTERFACES
// =====================================================================

export enum PolicyStatus {
  DRAFT = 'DRAFT',
  ACTIVE = 'ACTIVE',
  INACTIVE = 'INACTIVE',
  ARCHIVED = 'ARCHIVED'
}

export enum DecisionOutcome {
  AUTO_APPROVED = 'AUTO_APPROVED',
  MANUAL_REVIEW = 'MANUAL_REVIEW',
  DECLINED = 'DECLINED',
  COUNTER_OFFER = 'COUNTER_OFFER'
}

export enum ReviewTriggerType {
  CREDIT_SCORE = 'CREDIT_SCORE',
  INCOME_VERIFICATION = 'INCOME_VERIFICATION',
  EMPLOYMENT_TYPE = 'EMPLOYMENT_TYPE',
  LOAN_AMOUNT = 'LOAN_AMOUNT',
  DEBT_TO_INCOME = 'DEBT_TO_INCOME',
  EXISTING_OBLIGATIONS = 'EXISTING_OBLIGATIONS',
  ADVERSE_BUREAU = 'ADVERSE_BUREAU',
  FRAUD_INDICATOR = 'FRAUD_INDICATOR',
  POLICY_EXCEPTION = 'POLICY_EXCEPTION'
}

export enum DeclineReason {
  LOW_CREDIT_SCORE = 'LOW_CREDIT_SCORE',
  INSUFFICIENT_INCOME = 'INSUFFICIENT_INCOME',
  HIGH_DTI_RATIO = 'HIGH_DTI_RATIO',
  ADVERSE_CREDIT_HISTORY = 'ADVERSE_CREDIT_HISTORY',
  EMPLOYMENT_UNSTABLE = 'EMPLOYMENT_UNSTABLE',
  INCOMPLETE_DOCUMENTATION = 'INCOMPLETE_DOCUMENTATION',
  POLICY_VIOLATION = 'POLICY_VIOLATION',
  FRAUD_DETECTED = 'FRAUD_DETECTED',
  EXPOSURE_LIMIT_EXCEEDED = 'EXPOSURE_LIMIT_EXCEEDED',
  CONCENTRATION_LIMIT = 'CONCENTRATION_LIMIT',
  SECTORAL_CAP_EXCEEDED = 'SECTORAL_CAP_EXCEEDED'
}

export enum PricingTier {
  PRIME = 'PRIME',
  NEAR_PRIME = 'NEAR_PRIME',
  SUB_PRIME = 'SUB_PRIME',
  HIGH_RISK = 'HIGH_RISK'
}

export enum ExposureType {
  CUSTOMER = 'CUSTOMER',
  GROUP = 'GROUP',
  INDUSTRY = 'INDUSTRY',
  GEOGRAPHY = 'GEOGRAPHY',
  PRODUCT = 'PRODUCT'
}

export interface CreditPolicy {
  id: string;
  tenant_id: string;
  product_id?: string;
  name: string;
  code: string;
  description?: string;
  version: string;
  status: PolicyStatus;
  is_active: boolean;
  effective_from?: string;
  effective_to?: string;
  created_at: string;
  updated_at: string;
  created_by?: string;
  updated_by?: string;
}

export interface RiskBasedPricing {
  base_interest_rate: number;
  min_interest_rate: number;
  max_interest_rate: number;
  credit_score_weight: number;
  ltv_weight: number;
  dti_weight: number;
  other_factors_weight: number;
  processing_fee_range: { min: number; max: number };
  risk_premium_range: { min: number; max: number };
}


export interface ScoreBasedRate {
  min_score: number;
  max_score: number;
  pricing_tier: PricingTier;
  base_rate: number;
  rate_adjustment: number;
  processing_fee_percent?: number;
  risk_premium_percent?: number;
  max_loan_amount?: number;
  max_ltv_ratio?: number;
  priority: number;
}

export interface LTVRatio {
  collateral_type: string;
  collateral_subtype?: string;
  max_ltv_ratio: number;
  preferred_ltv_ratio?: number;
  ltv_rate_adjustments?: Record<string, number>;
  requires_insurance: boolean;
  requires_guarantor: boolean;
}

export interface ExposureLimit {
  exposure_type: ExposureType;
  exposure_name: string;
  max_exposure_amount: number;
  max_exposure_percentage?: number;
  max_single_obligor_amount?: number;
  max_single_obligor_percentage?: number;
  warning_threshold_percentage: number;
}

export interface ConcentrationLimit {
  parameter_name: string;
  parameter_type: string;
  max_concentration_percentage: number;
  target_concentration_percentage?: number;
  calculation_criteria: Record<string, any>;
}

export interface SectoralCap {
  sector_code: string;
  sector_name: string;
  subsector?: string;
  max_sector_percentage: number;
  max_sector_amount?: number;
  min_sector_percentage?: number;
  is_priority_sector: boolean;
  priority_sector_category?: string;
}

export interface AutoApprovalCriteria {
  min_credit_score?: number;
  credit_score_source?: string;
  min_monthly_income?: number;
  max_dti_ratio?: number;
  allowed_employment_types?: string[];
  min_employment_months?: number;
  max_loan_amount?: number;
  max_ltv_ratio?: number;
  allowed_loan_purposes?: string[];
  max_active_loans?: number;
  max_dpd_days?: number;
  allow_restructured_accounts: boolean;
  allowed_residence_types?: string[];
  min_residence_months?: number;
  allowed_geographies?: string[];
  required_document_types?: string[];
  require_bank_statement_analysis: boolean;
  min_bank_statement_months: number;
  require_dedupe_check: boolean;
  require_fraud_check: boolean;
}

export interface ManualReviewTrigger {
  trigger_type: ReviewTriggerType;
  trigger_name: string;
  description?: string;
  condition_field: string;
  condition_operator: string;
  condition_value: any;
  review_level?: string;
  priority: string;
  additional_checks?: string[];
  additional_documents?: string[];
  reviewer_instructions?: string;
  is_active: boolean;
}

export interface DecisionMatrix {
  rule_name: string;
  rule_priority: number;
  credit_score_range?: { min: number; max: number };
  loan_amount_range?: { min: number; max: number };
  ltv_range?: { min: number; max: number };
  dti_range?: { min: number; max: number };
  employment_types?: string[];
  income_range?: { min: number; max: number };
  bureau_conditions?: Record<string, any>;
  custom_conditions?: Record<string, any>;
  decision_outcome: DecisionOutcome;
  decline_reason?: DeclineReason;
  decline_message?: string;
  review_level?: string;
  review_instructions?: string;
  allow_counter_offer: boolean;
  is_active: boolean;
}


export interface CounterOfferRule {
  rule_name: string;
  rule_priority: number;
  trigger_conditions: Record<string, any>;
  loan_amount_adjustment?: Record<string, any>;
  interest_rate_adjustment?: Record<string, any>;
  tenure_adjustment?: Record<string, any>;
  require_guarantor: boolean;
  require_collateral: boolean;
  additional_documents?: string[];
  processing_fee_adjustment?: Record<string, any>;
  counter_offer_message?: string;
  terms_and_conditions?: string;
  offer_validity_days: number;
  is_active: boolean;
}

export interface PricingCalculationRequest {
  policy_id: string;
  credit_score: number;
  loan_amount: number;
  collateral_value?: number;
  monthly_income: number;
  monthly_obligations: number;
  employment_type: string;
  other_factors?: Record<string, any>;
}

export interface PricingCalculationResponse {
  base_rate: number;
  risk_adjusted_rate: number;
  final_interest_rate: number;
  processing_fee_percent: number;
  risk_premium_percent: number;
  pricing_tier: PricingTier;
  ltv_ratio?: number;
  dti_ratio: number;
  rate_breakdown: Record<string, number>;
  pricing_factors: Record<string, any>;
}

export interface CreditDecisionRequest {
  policy_id: string;
  application_id: string;
  credit_score: number;
  loan_amount: number;
  monthly_income: number;
  monthly_obligations: number;
  employment_type: string;
  employment_months: number;
  collateral_value?: number;
  residence_type: string;
  residence_months: number;
  geography: string;
  bureau_data: Record<string, any>;
  bank_statement_data?: Record<string, any>;
  additional_data?: Record<string, any>;
}

export interface CreditDecisionResponse {
  decision_outcome: DecisionOutcome;
  approved_amount?: number;
  interest_rate?: number;
  decline_reason?: DeclineReason;
  decline_message?: string;
  review_level?: string;
  review_instructions?: string;
  counter_offer?: Record<string, any>;
  decision_reasons: string[];
  matched_rules: string[];
  risk_assessment: Record<string, any>;
}

export interface ExposureCheckRequest {
  policy_id: string;
  customer_id?: string;
  group_id?: string;
  industry?: string;
  geography?: string;
  product_id?: string;
  loan_amount: number;
}

export interface ExposureCheckResponse {
  is_within_limits: boolean;
  exceeded_limits: Array<Record<string, any>>;
  current_exposure: Record<string, number>;
  available_limit: Record<string, number>;
  warnings: string[];
}

export interface PolicyStatistics {
  policy_id: string;
  policy_name: string;
  is_active: boolean;
  effective_from?: string;
  configuration: {
    has_risk_pricing: boolean;
    score_rate_tiers: number;
    ltv_configurations: number;
    exposure_limits: number;
    manual_review_triggers: number;
    decision_rules: number;
    counter_offer_rules: number;
  };
  pricing_range: {
    min_rate?: number;
    max_rate?: number;
  };
}

// =====================================================================
// SERVICE CLASS
// =====================================================================

class CreditPolicyService {
  private getAuthHeaders() {
    const token = localStorage.getItem('token');
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
  }

  // =====================================================================
  // CREDIT POLICY CRUD
  // =====================================================================

  async createPolicy(policyData: Partial<CreditPolicy>): Promise<CreditPolicy> {
    const response = await axios.post(
      `${API_BASE_URL}/api/credit-policy/policies`,
      policyData,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async listPolicies(params?: {
    product_id?: string;
    status?: PolicyStatus;
    is_active?: boolean;
    skip?: number;
    limit?: number;
  }): Promise<CreditPolicy[]> {
    const response = await axios.get(
      `${API_BASE_URL}/api/credit-policy/policies`,
      {
        params,
        headers: this.getAuthHeaders()
      }
    );
    return response.data;
  }

  async getPolicy(policyId: string): Promise<CreditPolicy> {
    const response = await axios.get(
      `${API_BASE_URL}/api/credit-policy/policies/${policyId}`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async updatePolicy(
    policyId: string,
    policyData: Partial<CreditPolicy>
  ): Promise<CreditPolicy> {
    const response = await axios.put(
      `${API_BASE_URL}/api/credit-policy/policies/${policyId}`,
      policyData,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async activatePolicy(policyId: string): Promise<CreditPolicy> {
    const response = await axios.post(
      `${API_BASE_URL}/api/credit-policy/policies/${policyId}/activate`,
      {},
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async deactivatePolicy(policyId: string): Promise<CreditPolicy> {
    const response = await axios.post(
      `${API_BASE_URL}/api/credit-policy/policies/${policyId}/deactivate`,
      {},
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async deletePolicy(policyId: string): Promise<void> {
    await axios.delete(
      `${API_BASE_URL}/api/credit-policy/policies/${policyId}`,
      { headers: this.getAuthHeaders() }
    );
  }

  async clonePolicy(
    policyId: string,
    newName: string,
    newCode: string
  ): Promise<CreditPolicy> {
    const response = await axios.post(
      `${API_BASE_URL}/api/credit-policy/policies/${policyId}/clone`,
      null,
      {
        params: { new_name: newName, new_code: newCode },
        headers: this.getAuthHeaders()
      }
    );
    return response.data;
  }


  // =====================================================================
  // RISK-BASED PRICING
  // =====================================================================

  async calculatePricing(
    request: PricingCalculationRequest
  ): Promise<PricingCalculationResponse> {
    const response = await axios.post(
      `${API_BASE_URL}/api/credit-policy/pricing/calculate`,
      request,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  // =====================================================================
  // CREDIT DECISIONING
  // =====================================================================

  async evaluateCreditDecision(
    request: CreditDecisionRequest
  ): Promise<CreditDecisionResponse> {
    const response = await axios.post(
      `${API_BASE_URL}/api/credit-policy/decision/evaluate`,
      request,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  // =====================================================================
  // EXPOSURE CHECKING
  // =====================================================================

  async checkExposureLimits(
    request: ExposureCheckRequest
  ): Promise<ExposureCheckResponse> {
    const response = await axios.post(
      `${API_BASE_URL}/api/credit-policy/exposure/check`,
      request,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  // =====================================================================
  // ANALYTICS & TESTING
  // =====================================================================

  async getPolicyStatistics(policyId: string): Promise<PolicyStatistics> {
    const response = await axios.get(
      `${API_BASE_URL}/api/credit-policy/policies/${policyId}/statistics`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async testPolicy(
    policyId: string,
    testScenarios: Array<Record<string, any>>
  ): Promise<{
    policy_id: string;
    total_scenarios: number;
    results: Array<Record<string, any>>;
  }> {
    const response = await axios.post(
      `${API_BASE_URL}/api/credit-policy/policies/${policyId}/test`,
      testScenarios,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async getDashboardSummary(): Promise<{
    total_policies: number;
    active_policies: number;
    draft_policies: number;
    policies_by_product: Record<string, number>;
    recent_policies: Array<{
      id: string;
      name: string;
      code: string;
      status: string;
      is_active: boolean;
      created_at: string;
    }>;
  }> {
    const response = await axios.get(
      `${API_BASE_URL}/api/credit-policy/dashboard/summary`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  // =====================================================================
  // HELPER METHODS
  // =====================================================================

  formatCurrency(amount: number): string {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  }

  formatPercentage(value: number, decimals: number = 2): string {
    return `${value.toFixed(decimals)}%`;
  }

  formatDate(dateString?: string): string {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  }

  getDecisionOutcomeColor(outcome: DecisionOutcome): string {
    switch (outcome) {
      case DecisionOutcome.AUTO_APPROVED:
        return 'success';
      case DecisionOutcome.MANUAL_REVIEW:
        return 'warning';
      case DecisionOutcome.DECLINED:
        return 'error';
      case DecisionOutcome.COUNTER_OFFER:
        return 'info';
      default:
        return 'default';
    }
  }

  getPricingTierColor(tier: PricingTier): string {
    switch (tier) {
      case PricingTier.PRIME:
        return 'success';
      case PricingTier.NEAR_PRIME:
        return 'info';
      case PricingTier.SUB_PRIME:
        return 'warning';
      case PricingTier.HIGH_RISK:
        return 'error';
      default:
        return 'default';
    }
  }
}

export default new CreditPolicyService();
