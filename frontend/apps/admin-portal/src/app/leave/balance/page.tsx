'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { attendanceService } from '@/services/attendance.service';
import { LeaveBalance, LeavePolicy } from '@/types/attendance.types';

export default function LeaveBalancePage() {
  const router = useRouter();
  const [balances, setBalances] = useState<LeaveBalance[]>([]);
  const [leaveTypes, setLeaveTypes] = useState<LeavePolicy[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedYear, setSelectedYear] = useState<number>(new Date().getFullYear());

  useEffect(() => {
    loadData();
  }, [selectedYear]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load leave balances
      const balancesResponse = await attendanceService.leave.listBalances({
        page: 1,
        page_size: 100,
      });
      setBalances(balancesResponse.items);

      // Load leave types for reference
      const typesResponse = await attendanceService.leave.listLeaveTypes({
        is_active: true,
        page: 1,
        page_size: 100,
      });
      setLeaveTypes(typesResponse.items);
    } catch (err: any) {
      setError(err.message || 'Failed to load leave balance data');
    } finally {
      setLoading(false);
    }
  };

  const getLeaveTypeName = (policyId: string) => {
    const policy = leaveTypes.find(t => t.id === policyId);
    return policy?.policy_name || `Leave Policy ${policyId}`;
  };

  const getLeaveTypeCode = (policyId: string) => {
    const policy = leaveTypes.find(t => t.id === policyId);
    return policy?.policy_code || '';
  };

  const getTotalBalance = (balance: LeaveBalance) => {
    return balance.opening_balance + balance.accrued;
  };

  const getUtilizationPercentage = (balance: LeaveBalance) => {
    const total = getTotalBalance(balance);
    if (total === 0) return 0;
    return Math.round((balance.availed / total) * 100);
  };

  const getStatusColor = (balance: LeaveBalance) => {
    const available = balance.current_balance;
    const total = getTotalBalance(balance);
    const percentage = total > 0 ? (available / total) * 100 : 0;

    if (percentage > 50) return 'text-green-600';
    if (percentage > 20) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading leave balance...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Leave Balance</h1>
        <div className="flex gap-3">
          <select
            value={selectedYear}
            onChange={(e) => setSelectedYear(parseInt(e.target.value))}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {[0, 1, 2].map(offset => {
              const year = new Date().getFullYear() - offset;
              return <option key={year} value={year}>{year}</option>;
            })}
          </select>
          <button
            onClick={() => router.push('/leave/apply')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Apply Leave
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <p className="text-gray-500 text-sm">Total Allocated</p>
            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
            </div>
          </div>
          <p className="text-3xl font-bold text-gray-900">
            {balances.reduce((sum, b) => sum + getTotalBalance(b), 0).toFixed(1)}
          </p>
          <p className="text-xs text-gray-500 mt-1">days</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <p className="text-gray-500 text-sm">Available</p>
            <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
              <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
          </div>
          <p className="text-3xl font-bold text-green-600">
            {balances.reduce((sum, b) => sum + b.current_balance, 0).toFixed(1)}
          </p>
          <p className="text-xs text-gray-500 mt-1">days</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <p className="text-gray-500 text-sm">Used</p>
            <div className="w-10 h-10 bg-orange-100 rounded-full flex items-center justify-center">
              <svg className="w-5 h-5 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
              </svg>
            </div>
          </div>
          <p className="text-3xl font-bold text-orange-600">
            {balances.reduce((sum, b) => sum + b.availed, 0).toFixed(1)}
          </p>
          <p className="text-xs text-gray-500 mt-1">days</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <p className="text-gray-500 text-sm">Pending</p>
            <div className="w-10 h-10 bg-yellow-100 rounded-full flex items-center justify-center">
              <svg className="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
          <p className="text-3xl font-bold text-yellow-600">
            {balances.reduce((sum, b) => sum + b.pending_approval, 0).toFixed(1)}
          </p>
          <p className="text-xs text-gray-500 mt-1">days</p>
        </div>
      </div>

      {/* Balance Details */}
      <div className="bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Leave Balance by Type</h2>
        </div>

        {balances.length === 0 ? (
          <div className="px-6 py-12 text-center text-gray-500">
            No leave balance data found for {selectedYear}
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {balances.map((balance) => (
              <div key={balance.id} className="p-6 hover:bg-gray-50">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {getLeaveTypeName(balance.leave_policy_id)}
                      </h3>
                      <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded">
                        {getLeaveTypeCode(balance.leave_policy_id)}
                      </span>
                    </div>
                    <p className="text-sm text-gray-500">Year: {balance.financial_year}</p>
                  </div>
                  <div className="text-right">
                    <div className={`text-3xl font-bold ${getStatusColor(balance)}`}>
                      {balance.current_balance}
                    </div>
                    <div className="text-xs text-gray-500">days available</div>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="mb-4">
                  <div className="flex justify-between text-xs text-gray-600 mb-1">
                    <span>Utilization</span>
                    <span>{getUtilizationPercentage(balance)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${getUtilizationPercentage(balance)}%` }}
                    />
                  </div>
                </div>

                {/* Detailed Stats */}
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                  <div className="bg-gray-50 rounded-lg p-3">
                    <div className="text-xs text-gray-500 mb-1">Opening</div>
                    <div className="text-lg font-semibold text-gray-900">
                      {balance.opening_balance}
                    </div>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-3">
                    <div className="text-xs text-gray-500 mb-1">Accrued</div>
                    <div className="text-lg font-semibold text-green-600">
                      +{balance.accrued}
                    </div>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-3">
                    <div className="text-xs text-gray-500 mb-1">Availed</div>
                    <div className="text-lg font-semibold text-orange-600">
                      -{balance.availed}
                    </div>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-3">
                    <div className="text-xs text-gray-500 mb-1">Pending</div>
                    <div className="text-lg font-semibold text-yellow-600">
                      {balance.pending_approval}
                    </div>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-3">
                    <div className="text-xs text-gray-500 mb-1">Carry Forward</div>
                    <div className="text-lg font-semibold text-blue-600">
                      {balance.carry_forward}
                    </div>
                  </div>
                </div>

                {/* Additional Info */}
                {balance.lapsed > 0 && (
                  <div className="mt-3 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-800">
                    ⚠️ {balance.lapsed} days lapsed
                  </div>
                )}

                {balance.encashed > 0 && (
                  <div className="mt-3 p-2 bg-green-50 border border-green-200 rounded text-sm text-green-800">
                    💰 {balance.encashed} days encashed
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Info Panel */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-6">
        <div className="flex items-start">
          <svg className="w-6 h-6 text-blue-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div className="flex-1">
            <h3 className="text-sm font-medium text-blue-900 mb-2">Leave Balance Information</h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• <strong>Opening Balance:</strong> Leaves available at the start of the year</li>
              <li>• <strong>Accrued:</strong> Leaves earned during the year</li>
              <li>• <strong>Availed:</strong> Leaves already taken</li>
              <li>• <strong>Pending:</strong> Leaves applied but awaiting approval</li>
              <li>• <strong>Carry Forward:</strong> Unused leaves from previous year</li>
              <li>• <strong>Available:</strong> Total leaves you can currently apply for</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
