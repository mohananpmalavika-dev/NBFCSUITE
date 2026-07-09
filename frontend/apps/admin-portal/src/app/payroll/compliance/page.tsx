'use client';

import { useState, useEffect } from 'react';
import { StatutoryComplianceService } from '@/services/payroll.service';
import type { StatutoryCompliance } from '@/types/payroll.types';
import { StatutoryType } from '@/types/payroll.types';

export default function StatutoryCompliancePage() {
  const [compliance, setCompliance] = useState<StatutoryCompliance[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<StatutoryType>(StatutoryType.PF);
  const [filterMonth, setFilterMonth] = useState<number>(new Date().getMonth() + 1);
  const [filterYear, setFilterYear] = useState<number>(new Date().getFullYear());
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    loadCompliance();
  }, [currentPage, activeTab, filterMonth, filterYear]);

  const loadCompliance = async () => {
    try {
      setLoading(true);
      const response = await StatutoryComplianceService.list({
        page: currentPage,
        page_size: 20,
        // statutory_type filter not supported by PayrollFilterParams
        month: filterMonth,
        year: filterYear
      });
      setCompliance(response.items);
      // Calculate total pages from total and page_size
      const calculatedPages = Math.ceil(response.total / (response.page_size || 20));
      setTotalPages(calculatedPages);
    } catch (error) {
      console.error('Failed to load compliance:', error);
    } finally {
      setLoading(false);
    }
  };

  const tabs: StatutoryType[] = [StatutoryType.PF, StatutoryType.ESI, StatutoryType.PT, StatutoryType.TDS];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Statutory Compliance</h1>
          <p className="text-sm text-gray-600 mt-1">Track PF, ESI, PT, and TDS compliance</p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg border border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <select
            value={filterMonth}
            onChange={(e) => setFilterMonth(parseInt(e.target.value))}
            className="px-4 py-2 border border-gray-300 rounded-lg"
          >
            {[1,2,3,4,5,6,7,8,9,10,11,12].map(m => (
              <option key={m} value={m}>{new Date(2000, m-1).toLocaleString('default', { month: 'long' })}</option>
            ))}
          </select>
          <select
            value={filterYear}
            onChange={(e) => setFilterYear(parseInt(e.target.value))}
            className="px-4 py-2 border border-gray-300 rounded-lg"
          >
            {[2024, 2025, 2026].map(y => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>
          <button
            onClick={loadCompliance}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Apply Filters
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab}
            </button>
          ))}
        </nav>
      </div>

      {/* Compliance Table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Code</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Period</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Employee</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Employer</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Due Date</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {loading ? (
              <tr><td colSpan={8} className="px-6 py-4 text-center">Loading...</td></tr>
            ) : compliance.length === 0 ? (
              <tr><td colSpan={8} className="px-6 py-4 text-center">No compliance records found</td></tr>
            ) : (
              compliance.map((record) => (
                <tr key={record.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">{record.compliance_code}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{record.month}/{record.year}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    ₹{(record.employee_contribution || 0).toLocaleString('en-IN')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    ₹{(record.employer_contribution || 0).toLocaleString('en-IN')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold">
                    ₹{record.total_amount.toLocaleString('en-IN')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 rounded text-xs ${
                      record.payment_status === 'PAID'
                        ? 'bg-green-100 text-green-700'
                        : record.payment_status === 'PENDING'
                        ? 'bg-yellow-100 text-yellow-700'
                        : 'bg-red-100 text-red-700'
                    }`}>
                      {record.payment_status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {record.due_date ? new Date(record.due_date).toLocaleDateString() : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm space-x-2">
                    {record.payment_status === 'PENDING' && (
                      <button className="text-green-600 hover:text-green-900">Update Payment</button>
                    )}
                    <button className="text-blue-600 hover:text-blue-900">View</button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
