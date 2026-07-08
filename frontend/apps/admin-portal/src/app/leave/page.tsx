'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { attendanceService } from '@/services/attendance.service';
import { LeaveApplication, LeaveStatus } from '@/types/attendance.types';

export default function LeaveApplicationsPage() {
  const router = useRouter();
  const [applications, setApplications] = useState<LeaveApplication[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<LeaveStatus | 'all'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 20;

  useEffect(() => {
    loadApplications();
  }, [statusFilter, searchQuery, currentPage]);

  const loadApplications = async () => {
    try {
      setLoading(true);
      setError(null);

      const params: any = {
        page: currentPage,
        page_size: pageSize,
      };

      if (statusFilter !== 'all') {
        params.status = statusFilter;
      }

      if (searchQuery) {
        params.search = searchQuery;
      }

      const response = await attendanceService.leave.listApplications(params);
      setApplications(response.items);
    } catch (err: any) {
      setError(err.message || 'Failed to load leave applications');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (id: number) => {
    if (!confirm('Approve this leave application?')) return;

    try {
      await attendanceService.leave.approveApplication(id, {
        remarks: 'Approved',
      });
      loadApplications();
      alert('Leave application approved successfully');
    } catch (err: any) {
      alert(err.message || 'Failed to approve leave application');
    }
  };

  const handleReject = async (id: number) => {
    const remarks = prompt('Enter rejection reason:');
    if (!remarks) return;

    try {
      await attendanceService.leave.rejectApplication(id, {
        remarks,
      });
      loadApplications();
      alert('Leave application rejected');
    } catch (err: any) {
      alert(err.message || 'Failed to reject leave application');
    }
  };

  const handleCancel = async (id: number) => {
    if (!confirm('Cancel this leave application?')) return;

    try {
      await attendanceService.leave.cancelApplication(id);
      loadApplications();
      alert('Leave application cancelled');
    } catch (err: any) {
      alert(err.message || 'Failed to cancel leave application');
    }
  };

  const getStatusBadgeClass = (status: LeaveStatus) => {
    switch (status) {
      case LeaveStatus.PENDING:
        return 'bg-yellow-100 text-yellow-800';
      case LeaveStatus.APPROVED:
        return 'bg-green-100 text-green-800';
      case LeaveStatus.REJECTED:
        return 'bg-red-100 text-red-800';
      case LeaveStatus.CANCELLED:
        return 'bg-gray-100 text-gray-800';
      case LeaveStatus.PENDING_REPORTING_MANAGER:
        return 'bg-blue-100 text-blue-800';
      case LeaveStatus.PENDING_HR:
        return 'bg-indigo-100 text-indigo-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  if (loading && applications.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading leave applications...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Leave Applications</h1>
        <div className="flex gap-3">
          <button
            onClick={() => router.push('/leave/balance')}
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            View Balance
          </button>
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

      {/* Filters */}
      <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Status
            </label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as LeaveStatus | 'all')}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Status</option>
              <option value={LeaveStatus.PENDING}>Pending</option>
              <option value={LeaveStatus.PENDING_REPORTING_MANAGER}>Pending - Manager</option>
              <option value={LeaveStatus.PENDING_HR}>Pending - HR</option>
              <option value={LeaveStatus.APPROVED}>Approved</option>
              <option value={LeaveStatus.REJECTED}>Rejected</option>
              <option value={LeaveStatus.CANCELLED}>Cancelled</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search
            </label>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by employee or leave type..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      </div>

      {/* Applications List */}
      <div className="bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Application Details
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Leave Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Period
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Days
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
              {applications.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                    No leave applications found
                  </td>
                </tr>
              ) : (
                applications.map((app) => (
                  <tr key={app.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="text-sm font-medium text-gray-900">
                        {app.application_code}
                      </div>
                      <div className="text-xs text-gray-500">
                        Employee: {app.employee_id}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        Applied: {formatDate(app.created_at)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {app.leave_type_name || `Type ${app.leave_type_id}`}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {formatDate(app.start_date)}
                      </div>
                      <div className="text-xs text-gray-500">
                        to {formatDate(app.end_date)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {app.total_days}
                      </div>
                      {app.is_half_day && (
                        <div className="text-xs text-gray-500">(Half Day)</div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusBadgeClass(app.status)}`}>
                        {app.status.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      {app.status === LeaveStatus.PENDING || 
                       app.status === LeaveStatus.PENDING_REPORTING_MANAGER || 
                       app.status === LeaveStatus.PENDING_HR ? (
                        <>
                          <button
                            onClick={() => handleApprove(app.id)}
                            className="text-green-600 hover:text-green-900 mr-3"
                          >
                            Approve
                          </button>
                          <button
                            onClick={() => handleReject(app.id)}
                            className="text-red-600 hover:text-red-900 mr-3"
                          >
                            Reject
                          </button>
                          <button
                            onClick={() => handleCancel(app.id)}
                            className="text-gray-600 hover:text-gray-900"
                          >
                            Cancel
                          </button>
                        </>
                      ) : (
                        <span className="text-gray-400">No actions</span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {applications.length > 0 && (
          <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
            <div className="text-sm text-gray-700">
              Page {currentPage}
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <button
                onClick={() => setCurrentPage(p => p + 1)}
                disabled={applications.length < pageSize}
                className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Details Panel */}
      {applications.length > 0 && (
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start">
            <svg className="w-5 h-5 text-blue-600 mt-0.5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div className="flex-1">
              <h3 className="text-sm font-medium text-blue-900 mb-1">Leave Application Workflow</h3>
              <p className="text-sm text-blue-800">
                Applications go through multi-level approval: Employee → Reporting Manager → HR → Final Approval
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
