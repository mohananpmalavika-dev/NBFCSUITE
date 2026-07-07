/**
 * ALM (Asset Liability Management) Types
 */

export enum MaturityBucket {
  UPTO_1_DAY = 'upto_1_day',
  UPTO_7_DAYS = 'upto_7_days',
  UPTO_14_DAYS = 'upto_14_days',
  UPTO_1_MONTH = 'upto_1_month',
  UPTO_2_MONTHS = 'upto_2_months',
  UPTO_3_MONTHS = 'upto_3_months',
  UPTO_6_MONTHS = 'upto_6_months',
  UPTO_1_YEAR = 'upto_1_year',
  UPTO_2_YEARS = 'upto_2_years',
  UPTO_3_YEARS = 'upto_3_years',
  UPTO_5_YEARS = 'upto_5_years',
  ABOVE_5_YEARS = 'above_5_years',
}

export enum GapType {
  LIQUIDITY_GAP = 'liquidity_gap',
  INTEREST_RATE_GAP = 'interest_rate_gap',
  MATURITY_GAP = 'maturity_gap',
  DURATION_GAP = 'duration_gap',
}

export enum RiskLevel {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

export enum InterestRateScenario {
  BASE = 'base',
  PARALLEL_UP_100 = 'parallel_up_100',
  PARALLEL_DOWN_100 = 'parallel_down_100',
  PARALLEL_UP_200 = 'parallel_up_200',
  PARALLEL_DOWN_200 = 'parallel_down_200',
  STEEPENING = 'steepening',
  FLATTENING = 'flattening',
}

// Maturity Ladder Types
export interface MaturityLadderEntry {
  id: number;
  tenant_id: number;
  report_date: string;
  bucket: MaturityBucket;
  cash_and_bank_balance: number;
  investments: number;
  loans_and_advances: number;
  fixed_assets: number;
  other_assets: number;
  total_assets: number;
  deposits: number;
  borrowings: number;
  debt_securities: number;
  other_liabilities: number;
  total_liabilities: number;
  gap_amount: number;
  cumulative_gap: number;
  gap_percentage: number | null;
  interest_sensitive_assets: number;
  interest_sensitive_liabilities: number;
  interest_rate_gap: number | null;
  avg_asset_duration: number | null;
  avg_liability_duration: number | null;
  duration_gap: number | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface MaturityLadderCreate {
  report_date: string;
  bucket: MaturityBucket;
  cash_and_bank_balance: number;
  investments: number;
  loans_and_advances: number;
  fixed_assets: number;
  other_assets: number;
  deposits: number;
  borrowings: number;
  debt_securities: number;
  other_liabilities: number;
  interest_sensitive_assets: number;
  interest_sensitive_liabilities: number;
  avg_asset_duration?: number;
  avg_liability_duration?: number;
  notes?: string;
}

export interface MaturityLadderSummary {
  report_date: string;
  total_assets: number;
  total_liabilities: number;
  overall_gap: number;
  short_term_gap: number;
  medium_term_gap: number;
  long_term_gap: number;
  risk_level: RiskLevel;
  largest_gap_bucket: MaturityBucket;
  largest_gap_amount: number;
}

// Gap Analysis Types
export interface GapAnalysisEntry {
  id: number;
  tenant_id: number;
  report_date: string;
  analysis_type: GapType;
  bucket: MaturityBucket;
  total_inflows: number;
  contractual_inflows: number;
  behavioral_inflows: number;
  total_outflows: number;
  contractual_outflows: number;
  behavioral_outflows: number;
  gap_amount: number;
  cumulative_gap: number;
  gap_ratio: number | null;
  risk_level: RiskLevel | null;
  risk_score: number | null;
  mitigation_required: boolean;
  mitigation_strategy: string | null;
  limit_breach: boolean;
  limit_value: number | null;
  actual_value: number | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface GapAnalysisCreate {
  report_date: string;
  analysis_type: GapType;
  bucket: MaturityBucket;
  contractual_inflows: number;
  behavioral_inflows: number;
  contractual_outflows: number;
  behavioral_outflows: number;
  risk_level?: RiskLevel;
  risk_score?: number;
  mitigation_required?: boolean;
  mitigation_strategy?: string;
  limit_value?: number;
  notes?: string;
}

export interface GapAnalysisSummary {
  report_date: string;
  analysis_type: GapType;
  total_gap: number;
  critical_buckets: string[];
  limit_breaches: number;
  mitigation_required: boolean;
  overall_risk_level: RiskLevel;
}

// Liquidity Ratio Types
export interface LiquidityRatio {
  id: number;
  tenant_id: number;
  report_date: string;
  current_ratio: number | null;
  quick_ratio: number | null;
  cash_ratio: number | null;
  liquidity_coverage_ratio: number | null;
  net_stable_funding_ratio: number | null;
  liquid_assets_to_total_assets: number | null;
  liquid_assets_to_deposits: number | null;
  liquid_assets_to_short_term_liabilities: number | null;
  slr_ratio: number | null;
  slr_requirement: number | null;
  slr_compliance: boolean;
  loan_to_deposit_ratio: number | null;
  deposit_concentration_ratio: number | null;
  large_deposits_ratio: number | null;
  stable_funding_ratio: number | null;
  core_deposit_ratio: number | null;
  volatile_liability_ratio: number | null;
  liquidity_stress_index: number | null;
  funding_gap_ratio: number | null;
  high_quality_liquid_assets: number | null;
  total_net_cash_outflows: number | null;
  available_stable_funding: number | null;
  required_stable_funding: number | null;
  all_ratios_compliant: boolean;
  breached_ratios: Record<string, any> | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface LiquidityRatioCreate {
  report_date: string;
  current_ratio?: number;
  quick_ratio?: number;
  cash_ratio?: number;
  liquidity_coverage_ratio?: number;
  net_stable_funding_ratio?: number;
  liquid_assets_to_total_assets?: number;
  liquid_assets_to_deposits?: number;
  liquid_assets_to_short_term_liabilities?: number;
  slr_ratio?: number;
  slr_requirement?: number;
  loan_to_deposit_ratio?: number;
  deposit_concentration_ratio?: number;
  large_deposits_ratio?: number;
  stable_funding_ratio?: number;
  core_deposit_ratio?: number;
  volatile_liability_ratio?: number;
  liquidity_stress_index?: number;
  funding_gap_ratio?: number;
  high_quality_liquid_assets?: number;
  total_net_cash_outflows?: number;
  available_stable_funding?: number;
  required_stable_funding?: number;
  notes?: string;
}

// Interest Rate Risk Types
export interface InterestRateRisk {
  id: number;
  tenant_id: number;
  report_date: string;
  scenario: InterestRateScenario;
  net_interest_income_base: number;
  market_value_equity_base: number;
  interest_rate_change_bps: number;
  net_interest_income_change: number | null;
  net_interest_income_change_pct: number | null;
  market_value_equity_change: number | null;
  market_value_equity_change_pct: number | null;
  modified_duration_assets: number | null;
  modified_duration_liabilities: number | null;
  duration_gap: number | null;
  repricing_gap_1_month: number | null;
  repricing_gap_3_months: number | null;
  repricing_gap_6_months: number | null;
  repricing_gap_1_year: number | null;
  cumulative_repricing_gap: number | null;
  rate_sensitive_assets: number | null;
  rate_sensitive_liabilities: number | null;
  rate_sensitive_gap: number | null;
  earnings_at_risk: number | null;
  value_at_risk: number | null;
  risk_level: RiskLevel | null;
  risk_score: number | null;
  limit_breach: boolean;
  hedging_required: boolean;
  hedging_strategy: string | null;
  hedge_effectiveness: number | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface InterestRateRiskCreate {
  report_date: string;
  scenario: InterestRateScenario;
  net_interest_income_base: number;
  market_value_equity_base: number;
  interest_rate_change_bps: number;
  net_interest_income_change?: number;
  net_interest_income_change_pct?: number;
  market_value_equity_change?: number;
  market_value_equity_change_pct?: number;
  modified_duration_assets?: number;
  modified_duration_liabilities?: number;
  duration_gap?: number;
  repricing_gap_1_month?: number;
  repricing_gap_3_months?: number;
  repricing_gap_6_months?: number;
  repricing_gap_1_year?: number;
  rate_sensitive_assets?: number;
  rate_sensitive_liabilities?: number;
  earnings_at_risk?: number;
  value_at_risk?: number;
  risk_level?: RiskLevel;
  risk_score?: number;
  hedging_required?: boolean;
  hedging_strategy?: string;
  hedge_effectiveness?: number;
  notes?: string;
}

// Quarterly Return Types
export interface QuarterlyReturn {
  id: number;
  tenant_id: number;
  return_number: string;
  quarter: number;
  year: number;
  report_date: string;
  sls_data: Record<string, any> | null;
  irs_data: Record<string, any> | null;
  behavioral_data: Record<string, any> | null;
  total_assets: number;
  total_liabilities: number;
  net_worth: number;
  liquidity_coverage_ratio: number | null;
  cumulative_gap_1_year: number | null;
  cumulative_gap_1_year_pct: number | null;
  interest_rate_shock_impact_100bps: number | null;
  interest_rate_shock_impact_200bps: number | null;
  earnings_at_risk: number | null;
  is_compliant: boolean;
  compliance_issues: Record<string, any> | null;
  prepared_by: number;
  prepared_at: string | null;
  reviewed_by: number | null;
  reviewed_at: string | null;
  approved_by: number | null;
  approved_at: string | null;
  filed_to_regulator: boolean;
  filing_date: string | null;
  filing_reference: string | null;
  attachments: Record<string, any> | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface QuarterlyReturnCreate {
  quarter: number;
  year: number;
  report_date: string;
  total_assets: number;
  total_liabilities: number;
  net_worth: number;
  sls_data?: Record<string, any>;
  irs_data?: Record<string, any>;
  behavioral_data?: Record<string, any>;
  liquidity_coverage_ratio?: number;
  cumulative_gap_1_year?: number;
  cumulative_gap_1_year_pct?: number;
  interest_rate_shock_impact_100bps?: number;
  interest_rate_shock_impact_200bps?: number;
  earnings_at_risk?: number;
  compliance_issues?: Record<string, any>;
  attachments?: Record<string, any>;
  notes?: string;
}

// ALM Alert Types
export interface ALMAlert {
  id: number;
  tenant_id: number;
  alert_date: string;
  alert_type: string;
  severity: RiskLevel;
  metric_name: string;
  metric_value: number;
  limit_value: number | null;
  deviation: number | null;
  deviation_percentage: number | null;
  alert_message: string;
  recommendation: string | null;
  is_acknowledged: boolean;
  acknowledged_by: number | null;
  acknowledged_at: string | null;
  is_resolved: boolean;
  resolved_by: number | null;
  resolved_at: string | null;
  resolution_notes: string | null;
  created_at: string;
  updated_at: string;
}

// ALM Dashboard Types
export interface ALMDashboard {
  as_of_date: string;
  maturity_summary: MaturityLadderSummary | null;
  liquidity_gap_summary: GapAnalysisSummary | null;
  interest_rate_gap_summary: GapAnalysisSummary | null;
  current_ratio: number | null;
  lcr: number | null;
  nsfr: number | null;
  interest_rate_risk_summary: Record<string, any>;
  active_alerts: number;
  critical_alerts: number;
  all_limits_compliant: boolean;
  breached_limits: string[];
}

// Helper Types
export const MATURITY_BUCKET_LABELS: Record<MaturityBucket, string> = {
  [MaturityBucket.UPTO_1_DAY]: 'Up to 1 Day',
  [MaturityBucket.UPTO_7_DAYS]: 'Up to 7 Days',
  [MaturityBucket.UPTO_14_DAYS]: 'Up to 14 Days',
  [MaturityBucket.UPTO_1_MONTH]: 'Up to 1 Month',
  [MaturityBucket.UPTO_2_MONTHS]: 'Up to 2 Months',
  [MaturityBucket.UPTO_3_MONTHS]: 'Up to 3 Months',
  [MaturityBucket.UPTO_6_MONTHS]: 'Up to 6 Months',
  [MaturityBucket.UPTO_1_YEAR]: 'Up to 1 Year',
  [MaturityBucket.UPTO_2_YEARS]: 'Up to 2 Years',
  [MaturityBucket.UPTO_3_YEARS]: 'Up to 3 Years',
  [MaturityBucket.UPTO_5_YEARS]: 'Up to 5 Years',
  [MaturityBucket.ABOVE_5_YEARS]: 'Above 5 Years',
};

export const GAP_TYPE_LABELS: Record<GapType, string> = {
  [GapType.LIQUIDITY_GAP]: 'Liquidity Gap',
  [GapType.INTEREST_RATE_GAP]: 'Interest Rate Gap',
  [GapType.MATURITY_GAP]: 'Maturity Gap',
  [GapType.DURATION_GAP]: 'Duration Gap',
};

export const SCENARIO_LABELS: Record<InterestRateScenario, string> = {
  [InterestRateScenario.BASE]: 'Base Scenario',
  [InterestRateScenario.PARALLEL_UP_100]: 'Rates Up 100 bps',
  [InterestRateScenario.PARALLEL_DOWN_100]: 'Rates Down 100 bps',
  [InterestRateScenario.PARALLEL_UP_200]: 'Rates Up 200 bps',
  [InterestRateScenario.PARALLEL_DOWN_200]: 'Rates Down 200 bps',
  [InterestRateScenario.STEEPENING]: 'Yield Curve Steepening',
  [InterestRateScenario.FLATTENING]: 'Yield Curve Flattening',
};
