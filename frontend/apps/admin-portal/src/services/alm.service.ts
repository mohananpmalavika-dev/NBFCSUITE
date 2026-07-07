/**
 * ALM (Asset Liability Management) Service
 * API calls for maturity ladder, gap analysis, liquidity ratios, IRR, and regulatory returns
 */

import { apiClient } from '@/lib/api-client'
import type { PaginationParams } from '@/types'

// ============================================
// Types & Interfaces
// ============================================

export type MaturityBucket =
  | 'upto_1_day'
  | 'upto_7_days'
  | 'upto_14_days'
  | 'upto_1_month'
  | 'upto_2_months'
  | 'upto_3_months'
  | 'upto_6_months'
  | 'upto_1_year'
  | 'upto_2_years'
  | 'upto_3_years'
  | 'upto_5_years'
  | 'above_5_years'

export type GapType = 'liquidity_gap' | 'interest_rate_gap' | 'maturity_gap' | 'duration_gap'

export type RiskLevel = 'low' | 'medium' | 'high' | 'critical'

export type InterestRateScenario =
  | 'base'
  | 'parallel_up_100'
  | 'parallel_down_100'
  | 'parallel_up_200'
  | 'parallel_down_200'
  | 'steepening'
  | 'flattening'

export interface MaturityLadderRequest {
  report_date: string
  bucket: MaturityBucket
  cash_and_bank_balance?: number
  money_market_instruments?: number
  investments?: number
  loans_and_advances?: number
  fixed_assets?: number
  other_assets?: number
  deposits?: number
  borrowings?: number
  debt_securities?: number
  other_liabilities?: number
  interest_rate_sensitive?: boolean
  notes?: string
}

export interface MaturityLadderResponse {
  id: number
  report_date: string
  bucket: MaturityBucket
  total_assets: number
  total_liabilities: number
  gap_amount: number
  cumulative_gap: number
  gap_percentage: number
  created_at: string
}

export interface GapAnalysisRequest {
  report_date: string
  analysis_type: GapType
  bucket: MaturityBucket
  contractual_inflows?: number
  contractual_outflows?: number
  behavioral_inflows?: number
  behavioral_outflows?: number
  rate_sensitive_assets?: number
  rate_sensitive_liabilities?: number
  notes?: string
}

export interface GapAnalysisResponse {
  id: number
  report_date: string
  analysis_type: GapType
  bucket: MaturityBucket
  gap_amount: number
  cumulative_gap: number
  risk_level: RiskLevel
  created_at: string
}

export interface LiquidityRatioRequest {
  report_date: string
  high_quality_liquid_assets: number
  total_net_cash_outflows: number
  available_stable_funding: number
  required_stable_funding: number
  liquid_assets: number
  total_assets: number
  current_assets?: number
  current_liabilities?: number
  cash_and_equivalents?: number
  short_term_liabilities?: number
}

export interface LiquidityRatioResponse {
  id: number
  report_date: string
  lcr: number // Liquidity Coverage Ratio
  nsfr: number // Net Stable Funding Ratio
  current_ratio: number
  quick_ratio: number
  cash_ratio: number
  liquid_asset_ratio: number
  breached_ratios: string[]
  created_at: string
}

export interface InterestRateRiskRequest {
  report_date: string
  scenario: InterestRateScenario
  net_interest_income_impact: number
  market_value_equity_impact: number
  modified_duration_assets?: number
  modified_duration_liabilities?: number
  duration_gap?: number
}

export interface InterestRateRiskResponse {
  id: number
  report_date: string
  scenario: InterestRateScenario
  net_interest_income_impact: number
  market_value_equity_impact: number
  risk_level: RiskLevel
  created_at: string
}

export interface QuarterlyReturnRequest {
  year: number
  quarter: number
  return_type: 'SLS' | 'IRS'
  data_json: Record<string, any>
}

export interface QuarterlyReturnResponse {
  id: number
  year: number
  quarter: number
  return_number: string
  return_type: string
  status: string
  prepared_by: string
  approved_by?: string
  filed_date?: string
  created_at: string
}

export interface ALMAlertResponse {
  id: number
  alert_type: string
  severity: string
  title: string
  description: string
  status: string
  created_at: string
}

export interface ALMDashboardResponse {
  report_date: string
  maturity_ladder_summary: {
    total_assets: number
    total_liabilities: number
    cumulative_gap: number
    negative_gaps: number
  }
  gap_analysis_summary: {
    liquidity_gap: number
    interest_rate_gap: number
    critical_buckets: number
  }
  liquidity_ratios: {
    lcr: number
    nsfr: number
    slr: number
    all_ratios_compliant: boolean
  }
  interest_rate_risk_summary: {
    base_scenario_nii: number
    worst_case_nii: number
    max_loss_percentage: number
  }
  alerts: {
    active_count: number
    critical_count: number
    high_count: number
  }
}

// ============================================
// ALM Service
// ============================================

export const almService = {
  // ============================================
  // Maturity Ladder
  // ============================================

  async createMaturityLadder(data: MaturityLadderRequest) {
    return apiClient.post<MaturityLadderResponse>(
      '/treasury/alm/maturity-ladder',
      data
    )
  },

  async getMaturityLadder(reportDate: string) {
    return apiClient.get<MaturityLadderResponse[]>(
      `/treasury/alm/maturity-ladder/${reportDate}`
    )
  },

  async getMaturityLadderSummary(reportDate: string) {
    return apiClient.get(`/treasury/alm/maturity-ladder/${reportDate}/summary`)
  },

  async updateMaturityLadder(entryId: number, data: Partial<MaturityLadderRequest>) {
    return apiClient.put(`/treasury/alm/maturity-ladder/${entryId}`, data)
  },

  // ============================================
  // Gap Analysis
  // ============================================

  async createGapAnalysis(data: GapAnalysisRequest) {
    return apiClient.post<GapAnalysisResponse>('/treasury/alm/gap-analysis', data)
  },

  async getGapAnalysis(reportDate: string, analysisType: GapType) {
    return apiClient.get<GapAnalysisResponse[]>(
      `/treasury/alm/gap-analysis/${reportDate}/${analysisType}`
    )
  },

  async getGapAnalysisSummary(reportDate: string, analysisType: GapType) {
    return apiClient.get(
      `/treasury/alm/gap-analysis/${reportDate}/${analysisType}/summary`
    )
  },

  // ============================================
  // Liquidity Ratios
  // ============================================

  async createLiquidityRatios(data: LiquidityRatioRequest) {
    return apiClient.post<LiquidityRatioResponse>(
      '/treasury/alm/liquidity-ratios',
      data
    )
  },

  async getLiquidityRatios(reportDate: string) {
    return apiClient.get<LiquidityRatioResponse>(
      `/treasury/alm/liquidity-ratios/${reportDate}`
    )
  },

  async getLiquidityRatioTrends(metricName: string, params?: { from_date?: string; to_date?: string }) {
    return apiClient.get(`/treasury/alm/liquidity-ratios/trends/${metricName}`, {
      params,
    })
  },

  // ============================================
  // Interest Rate Risk
  // ============================================

  async createInterestRateRisk(data: InterestRateRiskRequest) {
    return apiClient.post<InterestRateRiskResponse>(
      '/treasury/alm/interest-rate-risk',
      data
    )
  },

  async getInterestRateRisk(reportDate: string) {
    return apiClient.get<InterestRateRiskResponse[]>(
      `/treasury/alm/interest-rate-risk/${reportDate}`
    )
  },

  async getInterestRateRiskSummary(reportDate: string) {
    return apiClient.get(`/treasury/alm/interest-rate-risk/${reportDate}/summary`)
  },

  // ============================================
  // Quarterly Returns
  // ============================================

  async createQuarterlyReturn(data: QuarterlyReturnRequest) {
    return apiClient.post<QuarterlyReturnResponse>(
      '/treasury/alm/quarterly-returns',
      data
    )
  },

  async getQuarterlyReturn(year: number, quarter: number) {
    return apiClient.get<QuarterlyReturnResponse>(
      `/treasury/alm/quarterly-returns/${year}/${quarter}`
    )
  },

  async listQuarterlyReturns(params?: PaginationParams) {
    return apiClient.get<QuarterlyReturnResponse[]>(
      '/treasury/alm/quarterly-returns',
      { params }
    )
  },

  async approveQuarterlyReturn(returnId: number) {
    return apiClient.post(`/treasury/alm/quarterly-returns/${returnId}/approve`)
  },

  async fileQuarterlyReturn(returnId: number) {
    return apiClient.post(`/treasury/alm/quarterly-returns/${returnId}/file`)
  },

  // ============================================
  // Alerts
  // ============================================

  async getAlerts(params?: {
    severity?: string
    status?: string
    alert_type?: string
  }) {
    return apiClient.get<ALMAlertResponse[]>('/treasury/alm/alerts', { params })
  },

  async acknowledgeAlert(alertId: number) {
    return apiClient.post(`/treasury/alm/alerts/${alertId}/acknowledge`)
  },

  async resolveAlert(alertId: number, resolutionNotes?: string) {
    return apiClient.post(`/treasury/alm/alerts/${alertId}/resolve`, {
      resolution_notes: resolutionNotes,
    })
  },

  // ============================================
  // Dashboard
  // ============================================

  async getDashboard(asOfDate: string) {
    return apiClient.get<ALMDashboardResponse>(`/treasury/alm/dashboard/${asOfDate}`)
  },

  // ============================================
  // Utilities
  // ============================================

  getBucketLabel(bucket: MaturityBucket): string {
    const labels: Record<MaturityBucket, string> = {
      upto_1_day: 'Up to 1 day',
      upto_7_days: 'Up to 7 days',
      upto_14_days: 'Up to 14 days',
      upto_1_month: 'Up to 1 month',
      upto_2_months: 'Up to 2 months',
      upto_3_months: 'Up to 3 months',
      upto_6_months: 'Up to 6 months',
      upto_1_year: 'Up to 1 year',
      upto_2_years: 'Up to 2 years',
      upto_3_years: 'Up to 3 years',
      upto_5_years: 'Up to 5 years',
      above_5_years: 'Above 5 years',
    }
    return labels[bucket]
  },

  getScenarioLabel(scenario: InterestRateScenario): string {
    const labels: Record<InterestRateScenario, string> = {
      base: 'Base Scenario',
      parallel_up_100: 'Parallel Up 100 bps',
      parallel_down_100: 'Parallel Down 100 bps',
      parallel_up_200: 'Parallel Up 200 bps',
      parallel_down_200: 'Parallel Down 200 bps',
      steepening: 'Yield Curve Steepening',
      flattening: 'Yield Curve Flattening',
    }
    return labels[scenario]
  },

  getGapTypeLabel(gapType: GapType): string {
    const labels: Record<GapType, string> = {
      liquidity_gap: 'Liquidity Gap',
      interest_rate_gap: 'Interest Rate Gap',
      maturity_gap: 'Maturity Gap',
      duration_gap: 'Duration Gap',
    }
    return labels[gapType]
  },

  getRiskLevelColor(riskLevel: RiskLevel): string {
    const colors: Record<RiskLevel, string> = {
      low: 'bg-green-100 text-green-800',
      medium: 'bg-yellow-100 text-yellow-800',
      high: 'bg-orange-100 text-orange-800',
      critical: 'bg-red-100 text-red-800',
    }
    return colors[riskLevel]
  },
}
