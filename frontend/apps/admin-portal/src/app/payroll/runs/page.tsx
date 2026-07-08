'use client';

import { useState, useEffect } from 'react';
import { PayrollRunService } from '@/services/payroll.service';
import type { PayrollRun, PayrollRunCreate, PayrollStatus } from '@/types/payroll.types';

export default function PayrollRunsPage() {
  const [runs, setRuns] = useState<PayrollRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const [formData, setFormData] = useState<PayrollRunCreate>({
    month: new Date().getMonth() + 1,
    year: new Date().getFullYear(),
    cutoff_date: new Date().toISOString().split('T')[0],
    description: ''
  });

  useEffect(() => {
    loadRuns();
  }, [currentPage]);

  const loadRuns = async () => {
    try {
      setLoading(true);
      const response = await PayrollRunService.list({ page: currentPage, page_size: 20 });
      setRuns(response.items);
      setTotalPages(response.pages);
    } catch (error) {
      console.error('Failed to load runs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRun = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await PayrollRunService.create(formData);
      setShowCreateModal(false);
      loadRuns();
    } catch (error) {
      console.error('Failed to create run:', error);
    }
  };

  const handleProcessRun = async (runId: number) => {
    if (confirm('Process payroll for all employees?')) {
      try {
        await PayrollRunService.process(runId, {});
        loadRuns();
        alert('Payroll processed successfully');
      } catch (error) {
        console.error('Failed to process:', error);
        alert('Failed to process payroll');
      }
    }
  };

  const handleApproveRun = async (runId: number) => {
    if (confirm('Approve this payroll run?')) {
      try {
        await PayrollRunService.approve(runId, { approval_remarks: 'Approved' });
        loadRuns();
        alert('Payroll approved successfully');
      } catch (error) {
        console.error('Failed to approve:', error);
      }
    }
  };

  const getStatusBadge = (status: PayrollStatus) => {
    const styles = {
      DRAFT: 'bg-gray-100 text-gray-700',
      IN_PROGRESS: 'bg-blue-100 text-blue-700',
      COMPLETED: 'bg-green-100 text-green-700',
      APPROVED: 'bg-purple-100 text-purple-700',
      PAID: 'bg-emerald-100 text-emerald-700'
    };
    return <span className={`px-2 py-1 rounded text-xs ${styles[status]}`}>{status}</span>;
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Payroll Processing</h1>
          <p className="text-sm text-gray-600 mt-1">Create and manage monthly payroll runs</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          + Create Payroll Run
        </button>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Run Code</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Period</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Employees</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total Amount</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {loading ? (
              <tr><td colSpan={6} className="px-6 py-4 text-center">Loading...</td></tr>
            ) : runs.length === 0 ? (
              <tr><td colSpan={6} className="px-6 py-4 text-center">No payroll runs found</td></tr>
            ) : (
              runs.map((run) => (
                <tr key={run.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">{run.run_code}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{run.month}/{run.year}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{run.total_employees || 0}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">₹{(run.total_net_pay || 0).toLocaleString('en-IN')}</td>
                  <td className="px-6 py-4 whitespace-nowrap">{getStatusBadge(run.status)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm space-x-2">
                    {run.status === 'DRAFT' && (
                      <button onClick={() => handleProcessRun(run.id)} className="text-blue-600 hover:text-blue-900">
                        Process
                      </button>
                    )}
                    {run.status === 'COMPLETED' && (
                      <button onClick={() => handleApproveRun(run.id)} className="text-green-600 hover:text-green-900">
                        Approve
                      </button>
                    )}
                    <a href={`/payroll/payslips?run_id=${run.id}`} className="text-purple-600 hover:text-purple-900">
                      View Payslips
                    </a>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h2 className="text-xl font-bold mb-4">Create Payroll Run</h2>
            <form onSubmit={handleCreateRun} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Month *</label>
                  <select
                    value={formData.month}
                    onChange={(e) => setFormData({...formData, month: parseInt(e.target.value)})}
                    className="w-full px-4 py-2 border rounded-lg"
                    required
                  >
                    {[1,2,3,4,5,6,7,8,9,10,11,12].map(m => (
                      <option key={m} value={m}>{new Date(2000, m-1).toLocaleString('default', { month: 'long' })}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Year *</label>
                  <input
                    type="number"
                    value={formData.year}
                    onChange={(e) => setFormData({...formData, year: parseInt(e.target.value)})}
                    className="w-full px-4 py-2 border rounded-lg"
                    required
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Cutoff Date *</label>
                <input
                  type="date"
                  value={formData.cutoff_date}
                  onChange={(e) => setFormData({...formData, cutoff_date: e.target.value})}
                  className="w-full px-4 py-2 border rounded-lg"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  className="w-full px-4 py-2 border rounded-lg"
                  rows={3}
                />
              </div>
              <div className="flex justify-end gap-3">
                <button type="button" onClick={() => setShowCreateModal(false)} className="px-4 py-2 border rounded-lg">
                  Cancel
                </button>
                <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
