/**
 * Appraisal Cycle List Component
 * Display and manage appraisal cycles
 */

import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import performanceManagementService from '../../../services/performance.service';
import { AppraisalCycle, AppraisalCycleStatus } from '../../../types/performance.types';
import StatusBadge from '../../../components/performance/StatusBadge';

const AppraisalCycleList: React.FC = () => {
  const navigate = useNavigate();
  const [cycles, setCycles] = useState<AppraisalCycle[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState<AppraisalCycleStatus | ''>('');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadCycles();
  }, [filterStatus]);

  const loadCycles = async () => {
    try {
      setLoading(true);
      const response = await performanceManagementService.cycles.list({
        status: filterStatus || undefined,
        limit: 100
      });
      setCycles(response.items as AppraisalCycle[]);
    } catch (error) {
      console.error('Error loading cycles:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this appraisal cycle?')) {
      try {
        await performanceManagementService.cycles.delete(id);
        loadCycles();
      } catch (error) {
        console.error('Error deleting cycle:', error);
        alert('Failed to delete cycle');
      }
    }
  };

  const getStatusVariant = (status: AppraisalCycleStatus) => {
    const variants: Record<AppraisalCycleStatus, 'default' | 'success' | 'warning' | 'danger' | 'info'> = {
      draft: 'default',
      active: 'success',
      goal_setting: 'info',
      self_assessment: 'info',
      manager_review: 'info',
      normalization: 'warning',
      hr_review: 'warning',
      completed: 'success',
      closed: 'default',
      cancelled: 'danger'
    };
    return variants[status];
  };

  const filteredCycles = cycles.filter(cycle =>
    cycle.cycle_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    cycle.cycle_code.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="appraisal-cycle-list">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Appraisal Cycles</h1>
          <p className="text-gray-600 mt-1">Manage performance appraisal cycles</p>
        </div>
        <Link
          to="/performance/cycles/new"
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          + Create New Cycle
        </Link>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Search</label>
            <input
              type="text"
              placeholder="Search by cycle name or code..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value as AppraisalCycleStatus | '')}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">All Statuses</option>
              <option value="draft">Draft</option>
              <option value="active">Active</option>
              <option value="completed">Completed</option>
              <option value="closed">Closed</option>
            </select>
          </div>
        </div>
      </div>

      {/* Cycles Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {filteredCycles.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <p className="text-lg">No appraisal cycles found</p>
            <p className="text-sm mt-2">Create your first cycle to get started</p>
          </div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Cycle
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Fiscal Year
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Timeline
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Progress
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredCycles.map((cycle) => (
                <tr key={cycle.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{cycle.cycle_name}</div>
                      <div className="text-sm text-gray-500">{cycle.cycle_code}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {cycle.fiscal_year}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {new Date(cycle.start_date).toLocaleDateString()} - {new Date(cycle.end_date).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900">
                      {cycle.completed_appraisals} / {cycle.total_employees}
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{
                          width: `${cycle.total_employees > 0 ? (cycle.completed_appraisals / cycle.total_employees) * 100 : 0}%`
                        }}
                      />
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <StatusBadge
                      status={cycle.status.replace(/_/g, ' ')}
                      variant={getStatusVariant(cycle.status)}
                    />
                  </td>
                  <td className="px-6 py-4 text-right text-sm font-medium space-x-2">
                    <button
                      onClick={() => navigate(`/performance/cycles/${cycle.id}`)}
                      className="text-blue-600 hover:text-blue-900"
                    >
                      View
                    </button>
                    <button
                      onClick={() => navigate(`/performance/cycles/${cycle.id}/edit`)}
                      className="text-green-600 hover:text-green-900"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(cycle.id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default AppraisalCycleList;
