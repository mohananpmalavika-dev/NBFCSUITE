'use client';

import { useState, useEffect } from 'react';
import { goldApi } from '../../goldApi';

export default function ScheduledReportsPage() {
  const [schedules, setSchedules] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    loadSchedules();
  }, [statusFilter]);

  const loadSchedules = async () => {
    try {
      setLoading(true);
      const filters: any = { is_active: true };
      if (statusFilter !== 'all') {
        filters.status = statusFilter;
      }
      const data = await goldApi.getReportSchedules(filters);
      setSchedules(data);
    } catch (error) {
      console.error('Failed to load schedules:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePauseSchedule = async (scheduleId: string) => {
    try {
      await goldApi.pauseReportSchedule(scheduleId, 'Paused by user');
      await loadSchedules();
      alert('Schedule paused successfully');
    } catch (error) {
      console.error('Failed to pause schedule:', error);
      alert('Failed to pause schedule');
    }
  };

  const handleResumeSchedule = async (scheduleId: string) => {
    try {
      await goldApi.resumeReportSchedule(scheduleId);
      await loadSchedules();
      alert('Schedule resumed successfully');
    } catch (error) {
      console.error('Failed to resume schedule:', error);
      alert('Failed to resume schedule');
    }
  };

  const handleExecuteNow = async (scheduleId: string) => {
    try {
      await goldApi.executeScheduleNow(scheduleId);
      alert('Report execution started');
    } catch (error) {
      console.error('Failed to execute schedule:', error);
      alert('Failed to execute schedule');
    }
  };

  const handleDeleteSchedule = async (scheduleId: string) => {
    if (!confirm('Are you sure you want to delete this schedule?')) return;

    try {
      await goldApi.deleteReportSchedule(scheduleId);
      await loadSchedules();
      alert('Schedule deleted successfully');
    } catch (error) {
      console.error('Failed to delete schedule:', error);
      alert('Failed to delete schedule');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'paused': return 'bg-yellow-100 text-yellow-800';
      case 'failed': return 'bg-red-100 text-red-800';
      case 'completed': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getSuccessRate = (schedule: any) => {
    if (schedule.execution_count === 0) return 0;
    return Math.round((schedule.success_count / schedule.execution_count) * 100);
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="text-center py-12">Loading scheduled reports...</div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Scheduled Reports</h1>
          <p className="text-gray-600 mt-2">Manage automated report generation schedules</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
        >
          Create Schedule
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">Total Schedules</div>
          <div className="text-2xl font-bold text-gray-900 mt-1">{schedules.length}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">Active</div>
          <div className="text-2xl font-bold text-green-600 mt-1">
            {schedules.filter(s => s.status === 'active').length}
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">Paused</div>
          <div className="text-2xl font-bold text-yellow-600 mt-1">
            {schedules.filter(s => s.status === 'paused').length}
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">Total Executions</div>
          <div className="text-2xl font-bold text-blue-600 mt-1">
            {schedules.reduce((sum, s) => sum + (s.execution_count || 0), 0)}
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex gap-2">
          {['all', 'active', 'paused', 'failed'].map((status) => (
            <button
              key={status}
              onClick={() => setStatusFilter(status)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                statusFilter === status
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Schedules List */}
      <div className="space-y-4">
        {schedules.map((schedule) => (
          <div key={schedule.id} className="bg-white rounded-lg shadow hover:shadow-md transition-shadow">
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">{schedule.name}</h3>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(schedule.status)}`}>
                      {schedule.status}
                    </span>
                  </div>
                  {schedule.description && (
                    <p className="text-sm text-gray-600">{schedule.description}</p>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-4">
                <div>
                  <div className="text-xs text-gray-500 mb-1">Schedule Type</div>
                  <div className="text-sm font-medium text-gray-900">{schedule.schedule_type}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-500 mb-1">Frequency</div>
                  <div className="text-sm font-medium text-gray-900">{schedule.frequency || 'N/A'}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-500 mb-1">Next Execution</div>
                  <div className="text-sm font-medium text-gray-900">
                    {schedule.next_execution_at 
                      ? new Date(schedule.next_execution_at).toLocaleString()
                      : 'N/A'}
                  </div>
                </div>
                <div>
                  <div className="text-xs text-gray-500 mb-1">Last Execution</div>
                  <div className="text-sm font-medium text-gray-900">
                    {schedule.last_execution_at 
                      ? new Date(schedule.last_execution_at).toLocaleString()
                      : 'Never'}
                  </div>
                </div>
                <div>
                  <div className="text-xs text-gray-500 mb-1">Success Rate</div>
                  <div className="text-sm font-medium text-gray-900">
                    {getSuccessRate(schedule)}% ({schedule.success_count}/{schedule.execution_count})
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-4 pt-4 border-t">
                <div className="flex-1 text-sm text-gray-600">
                  Output: <span className="font-medium">{schedule.output_format?.toUpperCase() || 'PDF'}</span>
                  {schedule.delivery_method && (
                    <span className="ml-4">
                      Delivery: <span className="font-medium">{schedule.delivery_method}</span>
                    </span>
                  )}
                </div>
                <div className="flex gap-2">
                  {schedule.status === 'active' ? (
                    <button
                      onClick={() => handlePauseSchedule(schedule.id)}
                      className="px-3 py-1.5 text-sm border border-yellow-300 text-yellow-700 rounded hover:bg-yellow-50 transition-colors"
                    >
                      Pause
                    </button>
                  ) : (
                    <button
                      onClick={() => handleResumeSchedule(schedule.id)}
                      className="px-3 py-1.5 text-sm border border-green-300 text-green-700 rounded hover:bg-green-50 transition-colors"
                    >
                      Resume
                    </button>
                  )}
                  <button
                    onClick={() => handleExecuteNow(schedule.id)}
                    className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                  >
                    Run Now
                  </button>
                  <button
                    onClick={() => handleDeleteSchedule(schedule.id)}
                    className="px-3 py-1.5 text-sm border border-red-300 text-red-700 rounded hover:bg-red-50 transition-colors"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {schedules.length === 0 && (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No scheduled reports</h3>
          <p className="mt-1 text-sm text-gray-500">Get started by creating a new schedule.</p>
          <div className="mt-6">
            <button
              onClick={() => setShowCreateModal(true)}
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
            >
              Create Schedule
            </button>
          </div>
        </div>
      )}

      {/* Create Modal - Simplified placeholder */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h2 className="text-xl font-bold mb-4">Create Schedule</h2>
            <p className="text-gray-600 mb-4">Schedule creation form would go here.</p>
            <button
              onClick={() => setShowCreateModal(false)}
              className="w-full bg-gray-200 text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-300"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
