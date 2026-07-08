'use client';

import { useState, useEffect } from 'react';
import { EmployeeSalaryService } from '@/services/payroll.service';
import type { EmployeeSalary } from '@/types/payroll.types';

export default function EmployeeSalariesPage() {
  const [salaries, setSalaries] = useState<EmployeeSalary[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    loadSalaries();
  }, [currentPage]);

  const loadSalaries = async () => {
    try {
      setLoading(true);
      const response = await EmployeeSalaryService.list({ page: currentPage, page_size: 20 });
      setSalaries(response.items);
      setTotalPages(response.pages);
    } catch (error) {
      console.error('Failed to load salaries:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Employee Salary Assignments</h1>
          <p className="text-sm text-gray-600 mt-1">Assign salary structures to employees</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          + Assign Salary
        </button>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Employee</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Structure</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">CTC</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Effective Date</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {loading ? (
              <tr><td colSpan={6} className="px-6 py-4 text-center">Loading...</td></tr>
            ) : salaries.length === 0 ? (
              <tr><td colSpan={6} className="px-6 py-4 text-center">No salary assignments found</td></tr>
            ) : (
              salaries.map((salary) => (
                <tr key={salary.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {salary.employee?.first_name} {salary.employee?.last_name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {salary.salary_structure?.structure_name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold">
                    ₹{salary.total_ctc.toLocaleString('en-IN')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {new Date(salary.effective_date).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 rounded text-xs ${
                      salary.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
                    }`}>
                      {salary.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm space-x-2">
                    <button className="text-blue-600 hover:text-blue-900">Edit</button>
                    <button className="text-purple-600 hover:text-purple-900">View Breakdown</button>
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
