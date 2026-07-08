'use client';

import { useState, useEffect } from 'react';
import { Form16Service } from '@/services/payroll.service';
import type { Form16, Form16Status } from '@/types/payroll.types';

export default function Form16Page() {
  const [forms, setForms] = useState<Form16[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterYear, setFilterYear] = useState<string>('2024-2025');
  const [filterStatus, setFilterStatus] = useState<Form16Status | ''>('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    loadForms();
  }, [currentPage, filterYear, filterStatus]);

  const loadForms = async () => {
    try {
      setLoading(true);
      const response = await Form16Service.list({
        page: currentPage,
        page_size: 20,
        financial_year: filterYear,
        status: filterStatus || undefined
      });
      setForms(response.items);
      setTotalPages(response.pages);
    } catch (error) {
      console.error('Failed to load Form 16:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async (employeeId: number) => {
    if (confirm('Generate Form 16 for this employee?')) {
      try {
        await Form16Service.generate(employeeId, filterYear);
        loadForms();
        alert('Form 16 generated successfully');
      } catch (error) {
        console.error('Failed to generate:', error);
        alert('Failed to generate Form 16');
      }
    }
  };

  const handleIssue = async (form16Id: number) => {
    if (confirm('Issue Form 16 to employee?')) {
      try {
        await Form16Service.issue(form16Id);
        loadForms();
        alert('Form 16 issued successfully');
      } catch (error) {
        console.error('Failed to issue:', error);
      }
    }
  };

  const handleDownload = async (form16Id: number) => {
    try {
      await Form16Service.download(form16Id);
      alert('Download started (PDF generation pending)');
    } catch (error) {
      console.error('Failed to download:', error);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Form 16 Management</h1>
          <p className="text-sm text-gray-600 mt-1">Generate and manage Form 16 certificates</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          Bulk Generate
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg border border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <select
            value={filterYear}
            onChange={(e) => setFilterYear(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg"
          >
            <option value="2023-2024">FY 2023-2024</option>
            <option value="2024-2025">FY 2024-2025</option>
            <option value="2025-2026">FY 2025-2026</option>
          </select>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value as Form16Status | '')}
            className="px-4 py-2 border border-gray-300 rounded-lg"
          >
            <option value="">All Status</option>
            <option value="DRAFT">Draft</option>
            <option value="GENERATED">Generated</option>
            <option value="ISSUED">Issued</option>
          </select>
          <button
            onClick={() => {
              setFilterYear('2024-2025');
              setFilterStatus('');
            }}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Clear Filters
          </button>
        </div>
      </div>

      {/* Form 16 Table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Form 16 Code</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Employee</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Financial Year</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Gross Salary</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tax Deducted</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {loading ? (
              <tr><td colSpan={7} className="px-6 py-4 text-center">Loading...</td></tr>
            ) : forms.length === 0 ? (
              <tr><td colSpan={7} className="px-6 py-4 text-center">No Form 16 records found</td></tr>
            ) : (
              forms.map((form) => (
                <tr key={form.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">{form.form16_code}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {form.employee?.first_name} {form.employee?.last_name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{form.financial_year}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    ₹{form.gross_salary.toLocaleString('en-IN')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    ₹{form.tax_deducted.toLocaleString('en-IN')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 rounded text-xs ${
                      form.status === 'ISSUED'
                        ? 'bg-green-100 text-green-700'
                        : form.status === 'GENERATED'
                        ? 'bg-blue-100 text-blue-700'
                        : 'bg-gray-100 text-gray-700'
                    }`}>
                      {form.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm space-x-2">
                    {form.status === 'GENERATED' && (
                      <button
                        onClick={() => handleIssue(form.id)}
                        className="text-green-600 hover:text-green-900"
                      >
                        Issue
                      </button>
                    )}
                    <button
                      onClick={() => handleDownload(form.id)}
                      className="text-blue-600 hover:text-blue-900"
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
    </div>
  );
}
