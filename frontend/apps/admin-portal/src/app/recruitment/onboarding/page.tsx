'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { onboardingApi, verificationApi } from '@/services/recruitment.service';
import {
  Onboarding,
  OnboardingStatus,
  BackgroundVerification,
  VerificationStatus,
  ChecklistItem
} from '@/types/recruitment.types';

export default function OnboardingListPage() {
  const [onboardings, setOnboardings] = useState<Onboarding[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [selectedOnboarding, setSelectedOnboarding] = useState<Onboarding | null>(null);
  const [showChecklistModal, setShowChecklistModal] = useState(false);

  useEffect(() => {
    loadOnboardings();
  }, [page, statusFilter]);

  const loadOnboardings = async () => {
    try {
      setLoading(true);
      const response = await onboardingApi.list({
        page,
        page_size: 20,
        status: statusFilter || undefined
      });
      setOnboardings(response.items);
      setTotal(response.total);
      setTotalPages(response.total_pages);
    } catch (error) {
      console.error('Failed to load onboardings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStart = async (id: string) => {
    if (!confirm('Start onboarding process?')) return;
    try {
      await onboardingApi.start(id);
      loadOnboardings();
    } catch (error) {
      console.error('Failed to start onboarding:', error);
      alert('Failed to start onboarding');
    }
  };

  const handleComplete = async (id: string) => {
    if (!confirm('Mark onboarding as completed?')) return;
    try {
      await onboardingApi.complete(id);
      loadOnboardings();
    } catch (error) {
      console.error('Failed to complete onboarding:', error);
      alert('Failed to complete onboarding');
    }
  };

  const handleChecklistItemToggle = async (onboardingId: string, itemKey: string, completed: boolean) => {
    try {
      await onboardingApi.updateChecklistItem(onboardingId, itemKey, completed);
      // Reload onboarding details
      const updated = await onboardingApi.get(onboardingId);
      setSelectedOnboarding(updated);
      loadOnboardings();
    } catch (error) {
      console.error('Failed to update checklist item:', error);
      alert('Failed to update checklist item');
    }
  };

  const openChecklistModal = async (onboarding: Onboarding) => {
    // Fetch full details if checklist items are not loaded
    const details = await onboardingApi.get(onboarding.id);
    setSelectedOnboarding(details);
    setShowChecklistModal(true);
  };

  const getStatusBadgeColor = (status: OnboardingStatus) => {
    switch (status) {
      case OnboardingStatus.PENDING: return 'bg-gray-100 text-gray-800';
      case OnboardingStatus.IN_PROGRESS: return 'bg-blue-100 text-blue-800';
      case OnboardingStatus.COMPLETED: return 'bg-green-100 text-green-800';
      case OnboardingStatus.CANCELLED: return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getVerificationStatusColor = (status: VerificationStatus) => {
    switch (status) {
      case VerificationStatus.INITIATED: return 'bg-gray-100 text-gray-800';
      case VerificationStatus.IN_PROGRESS: return 'bg-yellow-100 text-yellow-800';
      case VerificationStatus.COMPLETED: return 'bg-green-100 text-green-800';
      case VerificationStatus.FAILED: return 'bg-red-100 text-red-800';
      case VerificationStatus.ON_HOLD: return 'bg-orange-100 text-orange-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Employee Onboarding</h1>
            <p className="text-gray-600 mt-1">Manage new hire onboarding and verification</p>
          </div>
          <Link
            href="/recruitment/onboarding/new"
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            + New Onboarding
          </Link>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-gray-600 text-sm font-medium">Total</div>
          <div className="text-2xl font-bold text-gray-900 mt-1">{total}</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-gray-600 text-sm font-medium">Pending</div>
          <div className="text-2xl font-bold text-gray-600 mt-1">
            {onboardings.filter(o => o.status === OnboardingStatus.PENDING).length}
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-blue-600 text-sm font-medium">In Progress</div>
          <div className="text-2xl font-bold text-blue-600 mt-1">
            {onboardings.filter(o => o.status === OnboardingStatus.IN_PROGRESS).length}
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-green-600 text-sm font-medium">Completed</div>
          <div className="text-2xl font-bold text-green-600 mt-1">
            {onboardings.filter(o => o.status === OnboardingStatus.COMPLETED).length}
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Status</option>
              <option value="PENDING">Pending</option>
              <option value="IN_PROGRESS">In Progress</option>
              <option value="COMPLETED">Completed</option>
              <option value="CANCELLED">Cancelled</option>
            </select>
          </div>
          <div>
            <button
              onClick={() => setStatusFilter('')}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      {/* Onboarding List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-gray-500">Loading onboarding records...</div>
        ) : onboardings.length === 0 ? (
          <div className="p-8 text-center text-gray-500">No onboarding records found</div>
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
                      Candidate
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Position
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Joining Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Progress
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
                  {onboardings.map((onboarding) => (
                    <tr key={onboarding.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600">
                        {onboarding.onboarding_code}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">
                        <div className="font-medium">
                          {onboarding.application?.applicant_name || 'N/A'}
                        </div>
                        <div className="text-gray-500">
                          {onboarding.application?.email || ''}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">
                        <div className="font-medium">{onboarding.designation?.title || 'N/A'}</div>
                        <div className="text-gray-500">{onboarding.department?.name || ''}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {new Date(onboarding.joining_date).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <div className="flex items-center gap-2">
                          <div className="flex-1 bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-blue-600 h-2 rounded-full"
                              style={{ width: `${onboarding.completion_percentage}%` }}
                            />
                          </div>
                          <span className="text-gray-700 font-medium">
                            {onboarding.completion_percentage.toFixed(0)}%
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusBadgeColor(onboarding.status)}`}>
                          {onboarding.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <div className="flex gap-2">
                          <Link
                            href={`/recruitment/onboarding/${onboarding.id}`}
                            className="text-blue-600 hover:text-blue-800"
                          >
                            View
                          </Link>
                          <button
                            onClick={() => openChecklistModal(onboarding)}
                            className="text-purple-600 hover:text-purple-800"
                          >
                            Checklist
                          </button>
                          {onboarding.status === OnboardingStatus.PENDING && (
                            <button
                              onClick={() => handleStart(onboarding.id)}
                              className="text-green-600 hover:text-green-800"
                            >
                              Start
                            </button>
                          )}
                          {onboarding.status === OnboardingStatus.IN_PROGRESS && (
                            <button
                              onClick={() => handleComplete(onboarding.id)}
                              className="text-green-600 hover:text-green-800"
                            >
                              Complete
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

      {/* Checklist Modal */}
      {showChecklistModal && selectedOnboarding && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">Onboarding Checklist</h2>
                  <p className="text-gray-600 mt-1">
                    {selectedOnboarding.application?.applicant_name} - {selectedOnboarding.onboarding_code}
                  </p>
                </div>
                <button
                  onClick={() => setShowChecklistModal(false)}
                  className="text-gray-400 hover:text-gray-600 text-2xl"
                >
                  ×
                </button>
              </div>
            </div>

            <div className="p-6">
              {/* Progress Bar */}
              <div className="mb-6">
                <div className="flex justify-between text-sm text-gray-600 mb-2">
                  <span>Overall Progress</span>
                  <span className="font-medium">{selectedOnboarding.completion_percentage.toFixed(0)}%</span>
                </div>
                <div className="bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-blue-600 h-3 rounded-full transition-all duration-300"
                    style={{ width: `${selectedOnboarding.completion_percentage}%` }}
                  />
                </div>
              </div>

              {/* Checklist Items */}
              <div className="space-y-3">
                {selectedOnboarding.checklist_items && selectedOnboarding.checklist_items.length > 0 ? (
                  selectedOnboarding.checklist_items.map((item: ChecklistItem, index: number) => (
                    <div key={index} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                      <input
                        type="checkbox"
                        checked={item.completed}
                        onChange={(e) =>
                          handleChecklistItemToggle(
                            selectedOnboarding.id,
                            item.key,
                            e.target.checked
                          )
                        }
                        className="mt-1 h-5 w-5 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <div className="flex-1">
                        <div className={`font-medium ${item.completed ? 'line-through text-gray-500' : 'text-gray-900'}`}>
                          {item.label}
                        </div>
                        {item.completed && item.completed_date && (
                          <div className="text-xs text-gray-500 mt-1">
                            Completed on {new Date(item.completed_date).toLocaleDateString()}
                          </div>
                        )}
                        {item.notes && (
                          <div className="text-sm text-gray-600 mt-1">{item.notes}</div>
                        )}
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center text-gray-500 py-8">
                    No checklist items configured
                  </div>
                )}
              </div>

              {/* Background Verifications */}
              {selectedOnboarding.verifications && selectedOnboarding.verifications.length > 0 && (
                <div className="mt-6 pt-6 border-t border-gray-200">
                  <h3 className="font-semibold text-gray-900 mb-3">Background Verifications</h3>
                  <div className="space-y-2">
                    {selectedOnboarding.verifications.map((verification: BackgroundVerification) => (
                      <div key={verification.id} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                        <div>
                          <div className="font-medium text-gray-900">{verification.verification_type}</div>
                          {verification.verification_agency && (
                            <div className="text-sm text-gray-600">{verification.verification_agency}</div>
                          )}
                        </div>
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getVerificationStatusColor(verification.status)}`}>
                          {verification.status.replace('_', ' ')}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="p-6 border-t border-gray-200 bg-gray-50">
              <button
                onClick={() => setShowChecklistModal(false)}
                className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
