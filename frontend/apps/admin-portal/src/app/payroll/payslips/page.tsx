'use client';

import { useState, useEffect } from 'react';
import { PayslipService } from '@/services/payroll.service';
import type { Payslip } from '@/types/payroll.types';

export default function PayslipsPage() {
  const [payslips, setPayslips] = useState<Payslip[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPayslip, setSelectedPayslip] = useState<Payslip | null>(null);
  const [filterMonth, setFilterMonth] = useState<number>(new Date().getMonth() + 1);
  const [filterYear, setFilterYear] = useState<number>(new Date().getFullYear());
  const [searchEmployee, setSearchEmployee] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    loadPayslips();
  }, [currentPage, filterMonth, filterYear]);

  const loadPayslips = async () => {
    try {
      setLoading(true);
      const response = await PayslipService.list({
        page: currentPage,
        page_size: 20,
        month: filterMonth,
        year: filterYear
      });
      setPayslips(response.items);
      setTotalPages(response.pages);
    } catch (error) {
      console.error('Failed to load payslips:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (payslipId: number) => {
    try {
      await PayslipService.download(payslipId);
      alert('Download started (PDF generation pending)');
    } catch (error) {
      console.error('Failed to download:', error);
    }
  };

  const viewPayslipDetails = (payslip: Payslip) => {
    setSelectedPayslip(payslip);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Employee Payslips</h1>
          <p className="text-sm text-gray-600 mt-1">View and download employee payslips</p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg border border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <input
            type="text"
            placeholder="Search employee..."
            value={searchEmployee}
            onChange={(e) => setSearchEmployee(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg"
          />
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
            onClick={() => {
              setFilterMonth(new Date().getMonth() + 1);
              setFilterYear(new Date().getFullYear());
              setSearchEmployee('');
            }}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Clear Filters
          </button>
        </div>
      </div>

      {/* Payslips Table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Payslip Code</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Employee</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Period</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Gross Salary</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Deductions</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Net Salary</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {loading ? (
              <tr><td colSpan={7} className="px-6 py-4 text-center">Loading...</td></tr>
            ) : payslips.length === 0 ? (
              <tr><td colSpan={7} className="px-6 py-4 text-center">No payslips found</td></tr>
            ) : (
              payslips.map((payslip) => (
                <tr key={payslip.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">{payslip.payslip_code}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {payslip.employee?.first_name} {payslip.employee?.last_name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{payslip.month}/{payslip.year}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">₹{payslip.gross_salary.toLocaleString('en-IN')}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">₹{payslip.total_deductions.toLocaleString('en-IN')}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold">₹{payslip.net_salary.toLocaleString('en-IN')}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm space-x-2">
                    <button
                      onClick={() => viewPayslipDetails(payslip)}
                      className="text-blue-600 hover:text-blue-900"
                    >
                      View
                    </button>
                    <button
                      onClick={() => handleDownload(payslip.id)}
                      className="text-green-600 hover:text-green-900"
                    >
                      Download
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Payslip Details Modal */}
      {selectedPayslip && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold">Payslip Details</h2>
              <button onClick={() => setSelectedPayslip(null)} className="text-gray-500 hover:text-gray-700">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Employee</p>
                  <p className="font-semibold">{selectedPayslip.employee?.first_name} {selectedPayslip.employee?.last_name}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Period</p>
                  <p className="font-semibold">{selectedPayslip.month}/{selectedPayslip.year}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Days Worked</p>
                  <p className="font-semibold">{selectedPayslip.days_worked} / {selectedPayslip.total_days}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">LOP Days</p>
                  <p className="font-semibold">{selectedPayslip.lop_days}</p>
                </div>
              </div>

              <div className="border-t pt-4">
                <h3 className="font-semibold mb-2">Earnings</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Gross Salary</span>
                    <span className="font-semibold">₹{selectedPayslip.gross_salary.toLocaleString('en-IN')}</span>
                  </div>
                </div>
              </div>

              <div className="border-t pt-4">
                <h3 className="font-semibold mb-2">Deductions</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>PF</span>
                    <span>₹{selectedPayslip.pf.toLocaleString('en-IN')}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>ESI</span>
                    <span>₹{selectedPayslip.esi.toLocaleString('en-IN')}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Professional Tax</span>
                    <span>₹{selectedPayslip.professional_tax.toLocaleString('en-IN')}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>TDS</span>
                    <span>₹{selectedPayslip.tds.toLocaleString('en-IN')}</span>
                  </div>
                  <div className="flex justify-between font-semibold border-t pt-2">
                    <span>Total Deductions</span>
                    <span>₹{selectedPayslip.total_deductions.toLocaleString('en-IN')}</span>
                  </div>
                </div>
              </div>

              <div className="border-t pt-4">
                <div className="flex justify-between text-lg font-bold">
                  <span>Net Salary</span>
                  <span>₹{selectedPayslip.net_salary.toLocaleString('en-IN')}</span>
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-4">
                <button
                  onClick={() => handleDownload(selectedPayslip.id)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Download PDF
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
