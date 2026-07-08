'use client';

import { useState, useEffect } from 'react';
import { SalaryStructureService } from '@/services/payroll.service';
import type { SalaryStructure, SalaryStructureCreate } from '@/types/payroll.types';

export default function SalaryStructuresPage() {
  const [structures, setStructures] = useState<SalaryStructure[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    loadStructures();
  }, [currentPage]);

  const loadStructures = async () => {
    try {
      setLoading(true);
      const response = await SalaryStructureService.list({ page: currentPage, page_size: 20 });
      setStructures(response.items);
      setTotalPages(response.pages);
    } catch (error) {
      console.error('Failed to load structures:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Salary Structures</h1>
          <p className="text-sm text-gray-600 mt-1">Manage salary structure templates</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          + Add Structure
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading ? (
          <div className="col-span-3 text-center py-8">Loading...</div>
        ) : structures.length === 0 ? (
          <div className="col-span-3 text-center py-8 text-gray-500">No structures found</div>
        ) : (
          structures.map((structure) => (
            <div key={structure.id} className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="font-semibold text-lg">{structure.structure_name}</h3>
                  <p className="text-sm text-gray-500">{structure.structure_code}</p>
                </div>
                <span className={`px-2 py-1 rounded text-xs ${
                  structure.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
                }`}>
                  {structure.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
              
              <div className="space-y-2 mb-4">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Total CTC:</span>
                  <span className="font-semibold">₹{structure.total_ctc.toLocaleString('en-IN')}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Employees:</span>
                  <span className="font-semibold">{structure.employees_count || 0}</span>
                </div>
              </div>

              <div className="flex gap-2">
                <button className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded hover:bg-gray-50">
                  Edit
                </button>
                <button className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded hover:bg-gray-50">
                  View Details
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
