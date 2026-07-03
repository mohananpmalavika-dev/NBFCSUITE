'use client';

import { useState, useEffect } from 'react';
import { goldApi } from '../../goldApi';

export default function DocumentWorkflowsPage() {
  const [approvals, setApprovals] = useState<any[]>([]);
  const [workflows, setWorkflows] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Filters
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [workflowFilter, setWorkflowFilter] = useState('');
  
  // Stats
  const [stats, setStats] = useState<any>(null);
  
  // Selected approval for action
  const [selectedApproval, setSelectedApproval] = useState<any | null>(null);
  const [actionType, setActionType] = useState<'approve' | 'reject' | 'return'>('approve');
  const [actionComments, setActionComments] = useState('');
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, [statusFilter, priorityFilter, workflowFilter]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [approvalsData, workflowsData, statsData] = await Promise.all([
        goldApi.listDocumentApprovals({
          approval_status: statusFilter || undefined,
          priority: priorityFilter || undefined,
          workflow_id: workflowFilter || undefined,
          limit: 50
        }),
        goldApi.listDocumentWorkflows({ is_active: true }),
        goldApi.getWorkflowStatistics()
      ]);
      
      setApprovals(approvalsData);
      setWorkflows(workflowsData);
      setStats(statsData);
      setError('');
    } catch (err: any) {
      setError('Failed to load workflows: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleTakeAction = async () => {
    if (!selectedApproval) return;
    
    if (actionType === 'reject' && !actionComments) {
      alert('Please provide rejection reason');
      return;
    }

    setActionLoading(true);
    
    try {
      await goldApi.takeApprovalAction(selectedApproval.approval_id, {
        action: actionType,
        comments: actionComments || null,
        rejection_reason: actionType === 'reject' ? actionComments : null,
        action_by: 'current-user-id' // TODO: Replace with actual user ID
      });
      
      alert(`Action ${actionType} completed successfully`);
      setSelectedApproval(null);
      setActionComments('');
      loadData();
    } catch (err: any) {
      alert('Failed to complete action: ' + err.message);
    } finally {
      setActionLoading(false);
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return 'bg-green-100 text-green-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'returned': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading && approvals.length === 0) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-4"></div>
            <p className="text-gray-600">Loading workflows...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Document Workflows</h1>
        <p className="text-gray-600">Manage document approvals and workflow processes</p>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Statistics Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="text-sm font-medium text-gray-600 mb-1">Pending Approvals</div>
            <div className="text-3xl font-bold text-blue-600">{stats.pending_approvals}</div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="text-sm font-medium text-gray-600 mb-1">Approved Today</div>
            <div className="text-3xl font-bold text-green-600">{stats.approved_today}</div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="text-sm font-medium text-gray-600 mb-1">Avg. Approval Time</div>
            <div className="text-3xl font-bold text-purple-600">{stats.average_approval_time_hours}h</div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="text-sm font-medium text-gray-600 mb-1">Escalated</div>
            <div className="text-3xl font-bold text-red-600">{stats.escalated_workflows}</div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="mb-6 bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Workflow</label>
            <select
              value={workflowFilter}
              onChange={(e) => setWorkflowFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Workflows</option>
              {workflows.map(wf => (
                <option key={wf.workflow_id} value={wf.workflow_id}>
                  {wf.workflow_name}
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Status</option>
              <option value="pending">Pending</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
              <option value="returned">Returned</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
            <select
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Priorities</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
        </div>
      </div>

      {/* Approvals List */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Approval
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Workflow
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Progress
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Priority
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Initiated
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {approvals.map((approval) => (
                <tr key={approval.approval_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="text-sm font-medium text-gray-900">{approval.approval_number}</div>
                    {approval.is_escalated && (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800 mt-1">
                        <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                        </svg>
                        Escalated
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {workflows.find(w => w.workflow_id === approval.workflow_id)?.workflow_name || 'N/A'}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center">
                      <div className="text-sm text-gray-900">
                        Step {approval.current_step} of {approval.total_steps}
                      </div>
                      <div className="ml-2 w-24 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{ width: `${(approval.current_step / approval.total_steps) * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getPriorityColor(approval.priority)}`}>
                      {approval.priority}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(approval.approval_status)}`}>
                      {approval.approval_status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {formatDate(approval.initiated_at)}
                  </td>
                  <td className="px-6 py-4 text-right text-sm font-medium">
                    {approval.approval_status === 'pending' && (
                      <button
                        onClick={() => setSelectedApproval(approval)}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        Review
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {approvals.length === 0 && (
          <div className="text-center py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No approvals found</h3>
            <p className="mt-1 text-sm text-gray-500">Try adjusting your filters.</p>
          </div>
        )}
      </div>

      {/* Action Modal */}
      {selectedApproval && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-full max-w-2xl shadow-lg rounded-lg bg-white">
            <div className="mb-4">
              <h3 className="text-lg font-bold text-gray-900">Review Approval</h3>
              <p className="text-sm text-gray-600 mt-1">{selectedApproval.approval_number}</p>
            </div>

            <div className="mb-6 p-4 bg-gray-50 rounded-lg">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-medium text-gray-500">Workflow</label>
                  <p className="text-sm text-gray-900">
                    {workflows.find(w => w.workflow_id === selectedApproval.workflow_id)?.workflow_name}
                  </p>
                </div>
                <div>
                  <label className="text-xs font-medium text-gray-500">Priority</label>
                  <p className="text-sm text-gray-900 capitalize">{selectedApproval.priority}</p>
                </div>
                <div>
                  <label className="text-xs font-medium text-gray-500">Current Step</label>
                  <p className="text-sm text-gray-900">
                    {selectedApproval.current_step} of {selectedApproval.total_steps}
                  </p>
                </div>
                <div>
                  <label className="text-xs font-medium text-gray-500">Initiated</label>
                  <p className="text-sm text-gray-900">{formatDate(selectedApproval.initiated_at)}</p>
                </div>
              </div>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">Action</label>
              <div className="flex gap-2">
                <button
                  onClick={() => setActionType('approve')}
                  className={`flex-1 px-4 py-2 rounded-lg font-medium ${
                    actionType === 'approve'
                      ? 'bg-green-600 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  Approve
                </button>
                <button
                  onClick={() => setActionType('reject')}
                  className={`flex-1 px-4 py-2 rounded-lg font-medium ${
                    actionType === 'reject'
                      ? 'bg-red-600 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  Reject
                </button>
                <button
                  onClick={() => setActionType('return')}
                  className={`flex-1 px-4 py-2 rounded-lg font-medium ${
                    actionType === 'return'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  Return
                </button>
              </div>
            </div>

            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Comments {actionType === 'reject' && <span className="text-red-600">*</span>}
              </label>
              <textarea
                value={actionComments}
                onChange={(e) => setActionComments(e.target.value)}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder={`Enter ${actionType} comments...`}
              />
            </div>

            <div className="flex gap-3">
              <button
                onClick={handleTakeAction}
                disabled={actionLoading}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium"
              >
                {actionLoading ? 'Processing...' : `Submit ${actionType}`}
              </button>
              <button
                onClick={() => {
                  setSelectedApproval(null);
                  setActionComments('');
                }}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 font-medium"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
