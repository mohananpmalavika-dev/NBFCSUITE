'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { interviewApi } from '@/services/recruitment.service';
import {
  Interview,
  InterviewStatus,
  InterviewType,
  InterviewMode
} from '@/types/recruitment.types';

export default function InterviewsCalendarPage() {
  const [interviews, setInterviews] = useState<Interview[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentDate, setCurrentDate] = useState(new Date());
  const [viewMode, setViewMode] = useState<'list' | 'calendar'>('list');
  
  // Filters
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [typeFilter, setTypeFilter] = useState<string>('');

  useEffect(() => {
    loadInterviews();
  }, [currentDate, statusFilter, typeFilter]);

  const loadInterviews = async () => {
    try {
      setLoading(true);
      
      // Get date range (current month)
      const year = currentDate.getFullYear();
      const month = currentDate.getMonth();
      const firstDay = new Date(year, month, 1);
      const lastDay = new Date(year, month + 1, 0);
      
      const response = await interviewApi.list({
        page: 1,
        page_size: 100,
        status: statusFilter || undefined,
        interview_type: typeFilter || undefined,
        from_date: firstDay.toISOString().split('T')[0],
        to_date: lastDay.toISOString().split('T')[0]
      });
      
      setInterviews(response.items);
    } catch (error) {
      console.error('Failed to load interviews:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleComplete = async (id: string) => {
    if (!confirm('Mark this interview as completed?')) return;
    try {
      await interviewApi.complete(id);
      loadInterviews();
    } catch (error) {
      console.error('Failed to complete interview:', error);
      alert('Failed to complete interview');
    }
  };

  const handleCancel = async (id: string) => {
    const reason = prompt('Enter cancellation reason:');
    if (!reason) return;
    try {
      await interviewApi.cancel(id, reason);
      loadInterviews();
    } catch (error) {
      console.error('Failed to cancel interview:', error);
      alert('Failed to cancel interview');
    }
  };

  const getStatusBadgeColor = (status: InterviewStatus) => {
    switch (status) {
      case InterviewStatus.SCHEDULED: return 'bg-blue-100 text-blue-800';
      case InterviewStatus.COMPLETED: return 'bg-green-100 text-green-800';
      case InterviewStatus.CANCELLED: return 'bg-red-100 text-red-800';
      case InterviewStatus.NO_SHOW: return 'bg-orange-100 text-orange-800';
      case InterviewStatus.RESCHEDULED: return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getTypeBadgeColor = (type: InterviewType) => {
    switch (type) {
      case InterviewType.SCREENING: return 'bg-purple-100 text-purple-800';
      case InterviewType.TECHNICAL: return 'bg-blue-100 text-blue-800';
      case InterviewType.HR: return 'bg-green-100 text-green-800';
      case InterviewType.MANAGERIAL: return 'bg-indigo-100 text-indigo-800';
      case InterviewType.FINAL: return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const prevMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1));
  };

  const nextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1));
  };

  const todayInterviews = interviews.filter(
    i => new Date(i.scheduled_date).toDateString() === new Date().toDateString()
  );

  const upcomingInterviews = interviews.filter(
    i => new Date(i.scheduled_date) > new Date() && i.status === InterviewStatus.SCHEDULED
  ).sort((a, b) => new Date(a.scheduled_date).getTime() - new Date(b.scheduled_date).getTime());

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Interview Schedule</h1>
            <p className="text-gray-600 mt-1">Manage interview scheduling and feedback</p>
          </div>
          <Link
            href="/recruitment/interviews/new"
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            + Schedule Interview
          </Link>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-gray-600 text-sm font-medium">Today's Interviews</div>
          <div className="text-2xl font-bold text-blue-600 mt-1">{todayInterviews.length}</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-gray-600 text-sm font-medium">Upcoming</div>
          <div className="text-2xl font-bold text-green-600 mt-1">{upcomingInterviews.length}</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-gray-600 text-sm font-medium">Total (This Month)</div>
          <div className="text-2xl font-bold text-gray-900 mt-1">{interviews.length}</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-gray-600 text-sm font-medium">Completed</div>
          <div className="text-2xl font-bold text-green-600 mt-1">
            {interviews.filter(i => i.status === InterviewStatus.COMPLETED).length}
          </div>
        </div>
      </div>

      {/* Filters & View Toggle */}
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Status</option>
              <option value="SCHEDULED">Scheduled</option>
              <option value="COMPLETED">Completed</option>
              <option value="CANCELLED">Cancelled</option>
              <option value="NO_SHOW">No Show</option>
            </select>
          </div>
          <div>
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Types</option>
              <option value="SCREENING">Screening</option>
              <option value="TECHNICAL">Technical</option>
              <option value="HR">HR</option>
              <option value="MANAGERIAL">Managerial</option>
              <option value="FINAL">Final</option>
            </select>
          </div>
          <div>
            <button
              onClick={() => {
                setStatusFilter('');
                setTypeFilter('');
              }}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Clear Filters
            </button>
          </div>
          <div>
            <div className="flex gap-2">
              <button
                onClick={() => setViewMode('list')}
                className={`flex-1 px-4 py-2 rounded-lg font-medium ${
                  viewMode === 'list'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                List View
              </button>
              <button
                onClick={() => setViewMode('calendar')}
                className={`flex-1 px-4 py-2 rounded-lg font-medium ${
                  viewMode === 'calendar'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Calendar
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Month Navigation */}
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="flex justify-between items-center">
          <button
            onClick={prevMonth}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            ← Previous
          </button>
          <h2 className="text-xl font-semibold text-gray-900">
            {currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
          </h2>
          <button
            onClick={nextMonth}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Next →
          </button>
        </div>
      </div>

      {/* Today's Interviews Highlight */}
      {todayInterviews.length > 0 && (
        <div className="bg-blue-50 border-2 border-blue-300 rounded-lg p-4 mb-6">
          <h3 className="font-semibold text-blue-900 mb-3">Today's Schedule ({todayInterviews.length})</h3>
          <div className="space-y-2">
            {todayInterviews.map(interview => (
              <div key={interview.id} className="bg-white p-3 rounded-lg">
                <div className="flex justify-between items-start">
                  <div>
                    <div className="font-medium text-gray-900">
                      {interview.application?.applicant_name || 'N/A'}
                    </div>
                    <div className="text-sm text-gray-600 mt-1">
                      {interview.start_time} - {interview.end_time} | {interview.interview_type}
                    </div>
                  </div>
                  <Link
                    href={`/recruitment/interviews/${interview.id}`}
                    className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                  >
                    View Details
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Interviews List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-gray-500">Loading interviews...</div>
        ) : interviews.length === 0 ? (
          <div className="p-8 text-center text-gray-500">No interviews scheduled for this period</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Code
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Candidate
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date & Time
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Mode
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
                {interviews.map((interview) => (
                  <tr key={interview.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600">
                      {interview.interview_code}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      <div className="font-medium">
                        {interview.application?.applicant_name || 'N/A'}
                      </div>
                      <div className="text-gray-500">
                        {interview.application?.email || ''}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getTypeBadgeColor(interview.interview_type)}`}>
                        {interview.interview_type}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <div>{new Date(interview.scheduled_date).toLocaleDateString()}</div>
                      <div className="text-gray-500">{interview.start_time} - {interview.end_time}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {interview.interview_mode}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusBadgeColor(interview.status)}`}>
                        {interview.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <div className="flex gap-2">
                        <Link
                          href={`/recruitment/interviews/${interview.id}`}
                          className="text-blue-600 hover:text-blue-800"
                        >
                          View
                        </Link>
                        {interview.status === InterviewStatus.SCHEDULED && (
                          <>
                            <button
                              onClick={() => handleComplete(interview.id)}
                              className="text-green-600 hover:text-green-800"
                            >
                              Complete
                            </button>
                            <button
                              onClick={() => handleCancel(interview.id)}
                              className="text-red-600 hover:text-red-800"
                            >
                              Cancel
                            </button>
                          </>
                        )}
                        {interview.status === InterviewStatus.COMPLETED && !interview.feedback_notes && (
                          <Link
                            href={`/recruitment/interviews/${interview.id}/feedback`}
                            className="text-purple-600 hover:text-purple-800"
                          >
                            Add Feedback
                          </Link>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
