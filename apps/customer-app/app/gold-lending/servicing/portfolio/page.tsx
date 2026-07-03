'use client';

import { useState, useEffect } from 'react';
import { goldApi } from '../../goldApi';
import Link from 'next/link';

interface PortfolioHealth {
  total_active_loans: number;
  total_outstanding: number;
  total_overdue: number;
  npa_loans: number;
  npa_amount: number;
  dpd_0_30: number;
  dpd_31_60: number;
  dpd_61_90: number;
  dpd_90_plus: number;
  collection_efficiency: number;
  average_ltv: number;
}

export default function PortfolioHealthPage() {
  const [portfolio, setPortfolio] = useState<PortfolioHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [branchFilter, setBranchFilter] = useState('');

  useEffect(() => {
    loadPortfolio();
  }, [branchFilter]);

  const loadPortfolio = async () => {
    try {
      setLoading(true);
      const filters: any = {};
      if (branchFilter) filters.branch_id = branchFilter;
      
      const data = await goldApi.getLoanPortfolio(filters);
      setPortfolio(data);
      setError('');
    } catch (err: any) {
      setError(err.message || 'Failed to load portfolio health');
    } finally {
      setLoading(false);
    }
  };

  const formatAmount = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatPercentage = (value: number) => {
    return `${value.toFixed(2)}%`;
  };

  const getNPARatio = () => {
    if (!portfolio || portfolio.total_outstanding === 0) return 0;
    return (portfolio.npa_amount / portfolio.total_outstanding) * 100;
  };

  const getOverdueRatio = () => {
    if (!portfolio || portfolio.total_outstanding === 0) return 0;
    return (portfolio.total_overdue / portfolio.total_outstanding) * 100;
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Portfolio Health Dashboard</h1>
              <p className="text-gray-600 mt-1">Monitor loan portfolio health, NPAs, and collection metrics</p>
            </div>
            <div className="flex gap-2">
              <Link
                href="/gold-lending/servicing/emi-schedule"
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                View EMI Schedule
              </Link>
            </div>
          </div>
        </div>

        {/* Branch Filter */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Filter by Branch</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Branch ID</label>
              <input
                type="text"
                value={branchFilter}
                onChange={(e) => setBranchFilter(e.target.value)}
                placeholder="Enter branch ID (leave empty for all)"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div className="flex items-end">
              <button
                onClick={loadPortfolio}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Apply Filter
              </button>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {loading ? (
          <div className="p-12 text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Loading portfolio data...</p>
          </div>
        ) : portfolio ? (
          <>
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-white rounded-lg shadow p-4">
                <div className="text-sm text-gray-600 mb-1">Active Loans</div>
                <div className="text-2xl font-bold text-gray-900">{portfolio.total_active_loans}</div>
              </div>
              <div className="bg-blue-50 rounded-lg shadow p-4">
                <div className="text-sm text-blue-600 mb-1">Total Outstanding</div>
                <div className="text-2xl font-bold text-blue-900">
                  {formatAmount(portfolio.total_outstanding)}
                </div>
              </div>
              <div className="bg-orange-50 rounded-lg shadow p-4">
                <div className="text-sm text-orange-600 mb-1">Total Overdue</div>
                <div className="text-2xl font-bold text-orange-900">
                  {formatAmount(portfolio.total_overdue)}
                </div>
              </div>
              <div className="bg-red-50 rounded-lg shadow p-4">
                <div className="text-sm text-red-600 mb-1">NPA Amount</div>
                <div className="text-2xl font-bold text-red-900">
                  {formatAmount(portfolio.npa_amount)}
                </div>
              </div>
            </div>

            {/* Portfolio Quality Indicators */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="bg-gradient-to-r from-red-500 to-red-600 rounded-lg shadow p-6 text-white">
                <div className="text-sm opacity-90 mb-2">NPA Ratio</div>
                <div className="text-4xl font-bold">{formatPercentage(getNPARatio())}</div>
                <div className="text-xs opacity-75 mt-2">{portfolio.npa_loans} NPA loans</div>
              </div>
              <div className="bg-gradient-to-r from-orange-500 to-orange-600 rounded-lg shadow p-6 text-white">
                <div className="text-sm opacity-90 mb-2">Overdue Ratio</div>
                <div className="text-4xl font-bold">{formatPercentage(getOverdueRatio())}</div>
                <div className="text-xs opacity-75 mt-2">Overdue amount vs total outstanding</div>
              </div>
              <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-lg shadow p-6 text-white">
                <div className="text-sm opacity-90 mb-2">Collection Efficiency</div>
                <div className="text-4xl font-bold">{formatPercentage(portfolio.collection_efficiency)}</div>
                <div className="text-xs opacity-75 mt-2">Collections vs demand</div>
              </div>
            </div>

            {/* DPD Buckets */}
            <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Days Past Due (DPD) Analysis</h2>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="border border-green-200 rounded-lg p-4 bg-green-50">
                  <div className="text-sm text-green-600 mb-2">DPD 0-30 Days</div>
                  <div className="text-3xl font-bold text-green-900">{portfolio.dpd_0_30}</div>
                  <div className="text-xs text-green-600 mt-2">Current & Early Stage</div>
                </div>
                <div className="border border-yellow-200 rounded-lg p-4 bg-yellow-50">
                  <div className="text-sm text-yellow-600 mb-2">DPD 31-60 Days</div>
                  <div className="text-3xl font-bold text-yellow-900">{portfolio.dpd_31_60}</div>
                  <div className="text-xs text-yellow-600 mt-2">Requires Follow-up</div>
                </div>
                <div className="border border-orange-200 rounded-lg p-4 bg-orange-50">
                  <div className="text-sm text-orange-600 mb-2">DPD 61-90 Days</div>
                  <div className="text-3xl font-bold text-orange-900">{portfolio.dpd_61_90}</div>
                  <div className="text-xs text-orange-600 mt-2">High Risk</div>
                </div>
                <div className="border border-red-200 rounded-lg p-4 bg-red-50">
                  <div className="text-sm text-red-600 mb-2">DPD 90+ Days</div>
                  <div className="text-3xl font-bold text-red-900">{portfolio.dpd_90_plus}</div>
                  <div className="text-xs text-red-600 mt-2">NPA Classification</div>
                </div>
              </div>

              {/* DPD Visual Bar */}
              <div className="mt-6">
                <div className="flex items-center mb-2">
                  <span className="text-sm font-medium text-gray-700 mr-4">Portfolio Distribution:</span>
                </div>
                <div className="flex h-8 rounded-lg overflow-hidden">
                  {portfolio.dpd_0_30 > 0 && (
                    <div
                      className="bg-green-500 flex items-center justify-center text-white text-xs font-medium"
                      style={{
                        width: `${(portfolio.dpd_0_30 / portfolio.total_active_loans) * 100}%`,
                      }}
                      title={`0-30 Days: ${portfolio.dpd_0_30} loans`}
                    >
                      {portfolio.dpd_0_30}
                    </div>
                  )}
                  {portfolio.dpd_31_60 > 0 && (
                    <div
                      className="bg-yellow-500 flex items-center justify-center text-white text-xs font-medium"
                      style={{
                        width: `${(portfolio.dpd_31_60 / portfolio.total_active_loans) * 100}%`,
                      }}
                      title={`31-60 Days: ${portfolio.dpd_31_60} loans`}
                    >
                      {portfolio.dpd_31_60}
                    </div>
                  )}
                  {portfolio.dpd_61_90 > 0 && (
                    <div
                      className="bg-orange-500 flex items-center justify-center text-white text-xs font-medium"
                      style={{
                        width: `${(portfolio.dpd_61_90 / portfolio.total_active_loans) * 100}%`,
                      }}
                      title={`61-90 Days: ${portfolio.dpd_61_90} loans`}
                    >
                      {portfolio.dpd_61_90}
                    </div>
                  )}
                  {portfolio.dpd_90_plus > 0 && (
                    <div
                      className="bg-red-500 flex items-center justify-center text-white text-xs font-medium"
                      style={{
                        width: `${(portfolio.dpd_90_plus / portfolio.total_active_loans) * 100}%`,
                      }}
                      title={`90+ Days: ${portfolio.dpd_90_plus} loans`}
                    >
                      {portfolio.dpd_90_plus}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Additional Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              {/* LTV Metric */}
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Average Loan-to-Value (LTV)</h3>
                <div className="flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-5xl font-bold text-blue-600 mb-2">
                      {formatPercentage(portfolio.average_ltv)}
                    </div>
                    <p className="text-sm text-gray-600">Portfolio Average LTV</p>
                    <div className="mt-4">
                      <div className="w-64 bg-gray-200 rounded-full h-4">
                        <div
                          className="bg-blue-600 h-4 rounded-full"
                          style={{ width: `${portfolio.average_ltv}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Health Score */}
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Portfolio Health Score</h3>
                <div className="flex items-center justify-center">
                  <div className="text-center">
                    {getNPARatio() < 2 && getOverdueRatio() < 5 ? (
                      <>
                        <div className="text-5xl mb-2">🟢</div>
                        <div className="text-2xl font-bold text-green-600">Healthy</div>
                        <p className="text-sm text-gray-600 mt-2">Portfolio is performing well</p>
                      </>
                    ) : getNPARatio() < 5 && getOverdueRatio() < 10 ? (
                      <>
                        <div className="text-5xl mb-2">🟡</div>
                        <div className="text-2xl font-bold text-yellow-600">Moderate</div>
                        <p className="text-sm text-gray-600 mt-2">Requires monitoring</p>
                      </>
                    ) : (
                      <>
                        <div className="text-5xl mb-2">🔴</div>
                        <div className="text-2xl font-bold text-red-600">At Risk</div>
                        <p className="text-sm text-gray-600 mt-2">Immediate action required</p>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Link
                  href="/gold-lending/servicing/emi-schedule"
                  className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-center"
                >
                  <div className="text-3xl mb-2">📅</div>
                  <div className="text-sm font-medium text-gray-900">EMI Schedule</div>
                </Link>
                <Link
                  href="/gold-lending/servicing/repayments"
                  className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-center"
                >
                  <div className="text-3xl mb-2">💰</div>
                  <div className="text-sm font-medium text-gray-900">Record Payment</div>
                </Link>
                <Link
                  href="/gold-lending/servicing/interest"
                  className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-center"
                >
                  <div className="text-3xl mb-2">📊</div>
                  <div className="text-sm font-medium text-gray-900">Interest Accrual</div>
                </Link>
                <Link
                  href="/gold-lending/servicing/adjustments"
                  className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-center"
                >
                  <div className="text-3xl mb-2">📝</div>
                  <div className="text-sm font-medium text-gray-900">Adjustments</div>
                </Link>
              </div>
            </div>
          </>
        ) : (
          <div className="p-12 text-center">
            <div className="text-gray-400 text-5xl mb-4">📈</div>
            <p className="text-gray-600 text-lg">No portfolio data available</p>
          </div>
        )}
      </div>
    </div>
  );
}
