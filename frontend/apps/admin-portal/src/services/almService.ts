/**
 * ALM Service - API calls for Asset Liability Management
 */

import api from '@/lib/api/client';
import type {
  MaturityLadderEntry,
  MaturityLadderCreate,
  MaturityLadderSummary,
  GapAnalysisEntry,
  GapAnalysisCreate,
  GapAnalysisSummary,
  LiquidityRatio,
  LiquidityRatioCreate,
  InterestRateRisk,
  InterestRateRiskCreate,
  QuarterlyReturn,
  QuarterlyReturnCreate,
  ALMAlert,
  ALMDashboard,
  GapType,
} from '@/types/alm';

const BASE_URL = '/treasury/alm';

// Maturity Ladder APIs
export const almService = {
  // ==================== Maturity Ladder ====================
  
  /**
   * Create maturity ladder entry
   */
  createMaturityLadder: async (data: MaturityLadderCreate): Promise<MaturityLadderEntry> => {
    const response = await api.post(`${BASE_URL}/maturity-ladder`, data);
    return response.data;
  },

  /**
   * Get maturity ladder for a specific date
   */
  getMaturityLadder: async (reportDate: string): Promise<{
    entries: MaturityLadderEntry[];
    total: number;
    report_date: string;
    total_assets: number;
    total_liabilities: number;
    net_gap: number;
  }> => {
    const response = await api.get(`${BASE_URL}/maturity-ladder/${reportDate}`);
    return response.data;
  },

  /**
   * Get maturity ladder summary
   */
  getMaturityLadderSummary: async (reportDate: string): Promise<MaturityLadderSummary> => {
    const response = await api.get(`${BASE_URL}/maturity-ladder/${reportDate}/summary`);
    return response.data;
  },

  /**
   * Update maturity ladder entry
   */
  updateMaturityLadder: async (entryId: number, data: Partial<MaturityLadderCreate>): Promise<MaturityLadderEntry> => {
    const response = await api.put(`${BASE_URL}/maturity-ladder/${entryId}`, data);
    return response.data;
  },

  // ==================== Gap Analysis ====================
  
  /**
   * Create gap analysis entry
   */
  createGapAnalysis: async (data: GapAnalysisCreate): Promise<GapAnalysisEntry> => {
    const response = await api.post(`${BASE_URL}/gap-analysis`, data);
    return response.data;
  },

  /**
   * Get gap analysis for a specific date and type
   */
  getGapAnalysis: async (reportDate: string, analysisType: GapType): Promise<{
    entries: GapAnalysisEntry[];
    total: number;
    report_date: string;
    analysis_type: GapType;
  }> => {
    const response = await api.get(`${BASE_URL}/gap-analysis/${reportDate}/${analysisType}`);
    return response.data;
  },

  /**
   * Get gap analysis summary
   */
  getGapAnalysisSummary: async (reportDate: string, analysisType: GapType): Promise<GapAnalysisSummary> => {
    const response = await api.get(`${BASE_URL}/gap-analysis/${reportDate}/${analysisType}/summary`);
    return response.data;
  },

  // ==================== Liquidity Ratios ====================
  
  /**
   * Create liquidity ratio entry
   */
  createLiquidityRatio: async (data: LiquidityRatioCreate): Promise<LiquidityRatio> => {
    const response = await api.post(`${BASE_URL}/liquidity-ratios`, data);
    return response.data;
  },

  /**
   * Get liquidity ratio for a specific date
   */
  getLiquidityRatio: async (reportDate: string): Promise<LiquidityRatio> => {
    const response = await api.get(`${BASE_URL}/liquidity-ratios/${reportDate}`);
    return response.data;
  },

  /**
   * Get liquidity ratio trends
   */
  getLiquidityTrends: async (
    metricName: string,
    startDate: string,
    endDate: string
  ): Promise<{
    metric_name: string;
    values: Array<{ date: string; value: number }>;
    average: number;
    trend: string;
  }> => {
    const response = await api.get(`${BASE_URL}/liquidity-ratios/trends/${metricName}`, {
      params: { start_date: startDate, end_date: endDate },
    });
    return response.data;
  },

  // ==================== Interest Rate Risk ====================
  
  /**
   * Create interest rate risk analysis
   */
  createInterestRateRisk: async (data: InterestRateRiskCreate): Promise<InterestRateRisk> => {
    const response = await api.post(`${BASE_URL}/interest-rate-risk`, data);
    return response.data;
  },

  /**
   * Get interest rate risk for a specific date
   */
  getInterestRateRisk: async (reportDate: string): Promise<{
    entries: InterestRateRisk[];
    total: number;
    report_date: string;
  }> => {
    const response = await api.get(`${BASE_URL}/interest-rate-risk/${reportDate}`);
    return response.data;
  },

  /**
   * Get interest rate risk summary
   */
  getInterestRateRiskSummary: async (reportDate: string): Promise<{
    report_date: string;
    base_scenario: InterestRateRisk;
    worst_case_scenario: InterestRateRisk;
    overall_risk_level: string;
    hedging_recommended: boolean;
  }> => {
    const response = await api.get(`${BASE_URL}/interest-rate-risk/${reportDate}/summary`);
    return response.data;
  },

  // ==================== Quarterly Returns ====================
  
  /**
   * Create quarterly return
   */
  createQuarterlyReturn: async (data: QuarterlyReturnCreate): Promise<QuarterlyReturn> => {
    const response = await api.post(`${BASE_URL}/quarterly-returns`, data);
    return response.data;
  },

  /**
   * Get quarterly return
   */
  getQuarterlyReturn: async (year: number, quarter: number): Promise<QuarterlyReturn> => {
    const response = await api.get(`${BASE_URL}/quarterly-returns/${year}/${quarter}`);
    return response.data;
  },

  /**
   * List quarterly returns
   */
  listQuarterlyReturns: async (skip = 0, limit = 100): Promise<{
    returns: QuarterlyReturn[];
    total: number;
  }> => {
    const response = await api.get(`${BASE_URL}/quarterly-returns`, {
      params: { skip, limit },
    });
    return response.data;
  },

  /**
   * Approve quarterly return
   */
  approveQuarterlyReturn: async (returnId: number, notes?: string): Promise<QuarterlyReturn> => {
    const response = await api.post(`${BASE_URL}/quarterly-returns/${returnId}/approve`, {
      approval_notes: notes,
    });
    return response.data;
  },

  /**
   * File quarterly return
   */
  fileQuarterlyReturn: async (returnId: number, filingDate: string, filingReference?: string): Promise<QuarterlyReturn> => {
    const response = await api.post(`${BASE_URL}/quarterly-returns/${returnId}/file`, {
      filing_date: filingDate,
      filing_reference: filingReference,
    });
    return response.data;
  },

  // ==================== Alerts ====================
  
  /**
   * List ALM alerts
   */
  listAlerts: async (
    isResolved?: boolean,
    severity?: string,
    skip = 0,
    limit = 100
  ): Promise<{
    alerts: ALMAlert[];
    total: number;
    unresolved_count: number;
    critical_count: number;
  }> => {
    const response = await api.get(`${BASE_URL}/alerts`, {
      params: {
        is_resolved: isResolved,
        severity,
        skip,
        limit,
      },
    });
    return response.data;
  },

  /**
   * Acknowledge alert
   */
  acknowledgeAlert: async (alertId: number, notes?: string): Promise<ALMAlert> => {
    const response = await api.post(`${BASE_URL}/alerts/${alertId}/acknowledge`, {
      notes,
    });
    return response.data;
  },

  /**
   * Resolve alert
   */
  resolveAlert: async (alertId: number, resolutionNotes: string): Promise<ALMAlert> => {
    const response = await api.post(`${BASE_URL}/alerts/${alertId}/resolve`, {
      resolution_notes: resolutionNotes,
    });
    return response.data;
  },

  // ==================== Dashboard ====================
  
  /**
   * Get ALM dashboard
   */
  getDashboard: async (asOfDate: string): Promise<ALMDashboard> => {
    const response = await api.get(`${BASE_URL}/dashboard/${asOfDate}`);
    return response.data;
  },
};

export default almService;
