'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { requisitionApi } from '@/services/recruitment.service';
import {
  JobRequisition,
  RequisitionStatus,
  RequisitionPriority,
  RequisitionDashboardStats
} from '@/types/recruitment.types';

export default function RequisitionsListPage() {
  const [requisitions, setRequisitions] = useState<JobRequisition[]>([]);
  const [stats, setStats] = useState<RequisitionDashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  
  // Filters
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [priorityFilter, setPriorityFilter] = useState<string>('');

  useEffect(() => {
    loadRequisitions();
    loadStats();
  }, [page, search, statusFilter, priorityFilter]);

  const loadRequisitions = async () => {
    try {
      setLoading(true);
      const response = await requisitionApi.list({
        page,
        page_size: 20,
        search: search || undefined,
        status: statusFilter || undefined,
        priority: priorityFilter || undefined
      });
      setRequisitions(response.items);
      setTotal(response.total);
      setTotalPages(response.total_pages);
    } catch (error) {
      console.error('Failed to load requisitions:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const statsData = await requisitionApi.getDashboardStats();
      setStats(statsData);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const handleSubmitForApproval = async (id: string) => {
    if (!confirm('Submit this requisition for approval?')) return;
    try {
      await requisitionApi.submit(id);
      loadRequisitions();
      loadStats();
    } catch (error) {
      console.error('Failed to submit requisition:', error);
      alert('Failed to submit requisition');
    }
  };

  const handleApprove = async (id: string) => {
    if (!confirm('Approve this requisition?')) return;
    try {
      await requisitionApi.approve(id, true);
      loadRequisitions();
      loadStats();
    } catch (error) {
      console.error('Failed to approve requisition:', error);
      alert('Failed to approve requisition');
    }
  };

  const handleReject = async (id: string) => {
    const reason = prompt('Enter rejection reason:');
    if (!reason) return;
    try {
      await requisitionApi.approve(id, false, reason);
      loadRequisitions();
      loadStats();
    } catch (error) {
      console.error('Failed to reject requisition:', error);
      alert('Failed to reject requisition');
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this requisition? This action cannot be undone.')) return;
    try {
      await requisitionApi.delete(id);
      loadRequisitions();
      loadStats();
    } catch (error) {
      console.error('Failed to delete requisition:', error);
      alert('Failed to delete requisition');
    }
  };

  const getStatusBadgeColor = (status: RequisitionStatus) => {
    switch (status) {
      case RequisitionStatus.DRAFT: return 'bg-gray-100 text-gray-800';
      case RequisitionStatus.PENDING_APPROVAL: return 'bg-yellow-100 text-yellow-800';
      case RequisitionStatus.APPROVED: return 'bg-green-100 text-green-800';
      case RequisitionStatus.REJECTED: return 'bg-red-100 text-red-800';
      case RequisitionStatus.CLOSED: return 'bg-gray-100 text-gray-600';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityBadgeColor = (priority: RequisitionPriority) => {
    switch (priority) {
      case RequisitionPriority.URGENT: return 'bg-red-100 text-red-800';
      case RequisitionPriority.HIGH: return 'bg-orange-100 text-orange-800';
      case RequisitionPriority.MEDIUM: return 'bg-blue-100 text-blue-800';
      case RequisitionPriority.LOW: return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Job Requisitions</h1>
            <p className="text-gray-600 mt-1">Manage job opening requests and approval workflow</p>
          </div>
          <Link
            href="/recruitment/requisitions/new"
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            + New Requisition
          </Link>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-gray-600 text-sm font-medium">Total</div>
            <div className="text-2xl font-bold text-gray-900 mt-1">{stats.total_requisitions}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-gray-600 text-sm font-medium">Draft</div>
            <div className="text-2xl font-bold text-gray-900 mt-1">{stats.draft}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-yellow-600 text-sm font-medium">Pending Approval</div>
            <div className="text-2xl font-bold text-yellow-600 mt-1">{stats.pending_approval}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-green-600 text-sm font-medium">Approved</div>
            <div className="text-2xl font-bold text-green-600 mt-1">{stats.approved}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-red-600 text-sm font-medium">Rejected</div>
            <div className="text-2xl font-bold text-red-600 mt-1">{stats.rejected}</div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <input
              type="text"
              placeholder="Search by title or code..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Status</option>
              <option value="DRAFT">Draft</option>
              <option value="PENDING_APPROVAL">Pending Approval</option>
              <option value="APPROVED">Approved</option>
              <option value="REJECTED">Rejected</option>
              <option value="CLOSED">Closed</option>
            </select>
          </div>
          <div>
            <select
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Priority</option>
              <option value="LOW">Low</option>
              <option value="MEDIUM">Medium</option>
              <option value="HIGH">High</option>
              <option value="URGENT">Urgent</option>
            </select>
          </div>
          <div>
            <button
              onClick={() => {
                setSearch('');
                setStatusFilter('');
                setPriorityFilter('');
              }}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      {/* Requisitions Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-gray-500">Loading requisitions...</div>
        ) : requisitions.length === 0 ? (
          <div className="p-8 text-center text-gray-500">No requisitions found</div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Code
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Title
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Department
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Positions
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Priority
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {requisitions.map((req) => (
                    <tr key={req.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600">
                        {req.requisition_code}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">
                        <div className="font-medium">{req.title}</div>
                        <div className="text-gray-500">{req.employment_type}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {req.department?.name || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {req.number_of_positions}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getPriorityBadgeColor(req.priority)}`}>
                          {req.priority}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusBadgeColor(req.status)}`}>
                          {req.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <div className="flex gap-2">
                          <Link
                            href={`/recruitment/requisitions/${req.id}`}
                            className="text-blue-600 hover:text-blue-800"
                          >
                            View
                          </Link>
                          {req.status === RequisitionStatus.DRAFT && (
                            <>
                              <Link
                                href={`/recruitment/requisitions/${req.id}/edit`}
                                className="text-green-600 hover:text-green-800"
                              >
                                Edit
                              </Link>
                              <button
                                onClick={() => handleSubmitForApproval(req.id)}
                                className="text-yellow-600 hover:text-yellow-800"
                              >
                                Submit
                              </button>
                            </>
                          )}
                          {req.status === RequisitionStatus.PENDING_APPROVAL && (
                            <>
                              <button
                                onClick={() => handleApprove(req.id)}
                                className="text-green-600 hover:text-green-800"
                              >
                                Approve
                              </button>
                              <button
                                onClick={() => handleReject(req.id)}
                                className="text-red-600 hover:text-red-800"
                              >
                                Reject
                              </button>
                            </>
                          )}
                          {req.status === RequisitionStatus.DRAFT && (
                            <button
                              onClick={() => handleDelete(req.id)}
                              className="text-red-600 hover:text-red-800"
                            >
                              Delete
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="bg-white px-4 py-3 border-t border-gray-200 sm:px-6">
              <div className="flex items-center justify-between">
                <div className="text-sm text-gray-700">
                  Showing <span className="font-medium">{(page - 1) * 20 + 1}</span> to{' '}
                  <span className="font-medium">{Math.min(page * 20, total)}</span> of{' '}
                  <span className="font-medium">{total}</span> results
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => setPage(page - 1)}
                    disabled={page === 1}
                    className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                  >
                    Previous
                  </button>
                  <button
                    onClick={() => setPage(page + 1)}
                    disabled={page === totalPages}
                    className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                  >
                    Next
                  </button>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
