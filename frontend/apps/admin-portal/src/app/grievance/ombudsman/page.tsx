'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Shield,
  AlertCircle,
  CheckCircle,
  Clock,
  Calendar,
  FileText,
  DollarSign,
  ChevronRight,
  Filter,
} from 'lucide-react';
import { grievanceService } from '@/services/grievance.service';
import type { OmbudsmanCase } from '@/types/grievance';
import {
  OmbudsmanStatus,
  OmbudsmanStatusLabels,
  formatDate,
  formatDateTime,
  formatCurrency,
  calculateDaysElapsed,
} from '@/types/grievance';

export default function OmbudsmanCasesPage() {
  const router = useRouter();
  const [cases, setCases] = useState<OmbudsmanCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [showFilters, setShowFilters] = useState(false);

  // Pagination
  const [page, setPage] = useState(1);
  const [limit] = useState(20);

  // Modal states
  const [selectedCase, setSelectedCase] = useState<OmbudsmanCase | null>(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);

  useEffect(() => {
    loadCases();
  }, [page, statusFilter]);

  const loadCases = async () => {
    try {
      setLoading(true);
      setError(null);

      const params: any = {
        skip: (page - 1) * limit,
        limit,
      };

      if (statusFilter) params.status = statusFilter;

      const data = await grievanceService.listOmbudsmanCases(params);
      setCases(data.cases);
      setTotal(data.total);
    } catch (err) {
      console.error('Failed to load ombudsman cases:', err);
      setError('Failed to load ombudsman cases. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: OmbudsmanStatus): string => {
    switch (status) {
      case OmbudsmanStatus.PENDING:
        return 'bg-yellow-100 text-yellow-800';
      case OmbudsmanStatus.SUBMITTED:
        return 'bg-blue-100 text-blue-800';
      case OmbudsmanStatus.UNDER_REVIEW:
        return 'bg-purple-100 text-purple-800';
      case OmbudsmanStatus.HEARING_SCHEDULED:
        return 'bg-orange-100 text-orange-800';
      case OmbudsmanStatus.AWARD_ISSUED:
        return 'bg-green-100 text-green-800';
      case OmbudsmanStatus.CLOSED:
        return 'bg-gray-100 text-gray-800';
      case OmbudsmanStatus.WITHDRAWN:
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const totalPages = Math.ceil(total / limit);

  const pendingCount = cases.filter(c => c.status === OmbudsmanStatus.PENDING).length;
  const submittedCount = cases.filter(c => c.status === OmbudsmanStatus.SUBMITTED).length;
  const underReviewCount = cases.filter(c => c.status === OmbudsmanStatus.UNDER_REVIEW).length;
  const awardIssuedCount = cases.filter(c => c.status === OmbudsmanStatus.AWARD_ISSUED).length;
  const totalCompensation = cases
    .filter(c => c.compensation_awarded)
    .reduce((sum, c) => sum + (c.compensation_awarded || 0), 0);
  const within30Days = cases.filter(c => c.resolution_within_30_days === true).length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Banking Ombudsman Cases</h1>
          <p className="text-gray-600 mt-1">
            {total} total cases • Page {page} of {totalPages}
          </p>
        </div>
        <button
          onClick={() => router.push('/grievance/complaints')}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          View Complaints
        </button>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex items-center gap-2 mb-2">
            <Shield className="h-5 w-5 text-blue-600" />
            <span className="text-sm text-gray-600">Total Cases</span>
          </div>
          <p className="text-3xl font-bold text-gray-900">{total}</p>
          <div className="mt-2 flex gap-2 text-xs">
            <span className="text-yellow-600">{pendingCount} Pending</span>
            <span className="text-blue-600">{submittedCount} Submitted</span>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex items-center gap-2 mb-2">
            <Clock className="h-5 w-5 text-purple-600" />
            <span className="text-sm text-gray-600">Under Review</span>
          </div>
          <p className="text-3xl font-bold text-purple-600">{underReviewCount}</p>
          <p className="mt-2 text-xs text-gray-500">Active cases being reviewed</p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle className="h-5 w-5 text-green-600" />
            <span className="text-sm text-gray-600">Awards Issued</span>
          </div>
          <p className="text-3xl font-bold text-green-600">{awardIssuedCount}</p>
          <p className="mt-2 text-xs text-gray-500">{within30Days} within 30 days</p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex items-center gap-2 mb-2">
            <DollarSign className="h-5 w-5 text-orange-600" />
            <span className="text-sm text-gray-600">Total Compensation</span>
          </div>
          <p className="text-2xl font-bold text-orange-600">{formatCurrency(totalCompensation)}</p>
          <p className="mt-2 text-xs text-gray-500">Awarded to customers</p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-md p-4">
        <div className="flex flex-col md:flex-row gap-4">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2"
          >
            <Filter className="h-4 w-4" />
            Filters
          </button>

          {showFilters && (
            <div className="flex flex-col md:flex-row gap-4 flex-1">
              <div className="flex-1">
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Statuses</option>
                  {Object.entries(OmbudsmanStatusLabels).map(([key, label]) => (
                    <option key={key} value={key}>{label}</option>
                  ))}
                </select>
              </div>

              <button
                onClick={() => setStatusFilter('')}
                className="px-4 py-2 text-blue-600 hover:text-blue-700"
              >
                Reset
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Cases List */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : cases.length === 0 ? (
          <div className="text-center py-16">
            <Shield className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">No ombudsman cases found</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {cases.map((ombudsmanCase) => {
              const daysElapsed = ombudsmanCase.submitted_date 
                ? calculateDaysElapsed(ombudsmanCase.submitted_date)
                : 0;
              const isDelayed = daysElapsed > 30 && ombudsmanCase.status !== OmbudsmanStatus.CLOSED;

              return (
                <div
                  key={ombudsmanCase.id}
                  className="p-6 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      {/* Header */}
                      <div className="flex items-center gap-3 mb-3">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {ombudsmanCase.ombudsman_case_number}
                        </h3>
                        <span className={`inline-flex px-3 py-1 text-xs font-medium rounded-full ${getStatusColor(ombudsmanCase.status)}`}>
                          {OmbudsmanStatusLabels[ombudsmanCase.status]}
                        </span>
                        {ombudsmanCase.is_appealed && (
                          <span className="inline-flex px-3 py-1 text-xs font-medium rounded-full bg-orange-100 text-orange-800">
                            Appealed
                          </span>
                        )}
                        {isDelayed && (
                          <span className="inline-flex items-center gap-1 px-3 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800">
                            <AlertCircle className="h-3 w-3" />
                            Delayed (30+ days)
                          </span>
                        )}
                        {ombudsmanCase.resolution_within_30_days && (
                          <span className="inline-flex items-center gap-1 px-3 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">
                            <CheckCircle className="h-3 w-3" />
                            Resolved within 30 days
                          </span>
                        )}
                      </div>

                      {/* Content */}
                      <div className="space-y-2">
                        <div className="flex items-center gap-2 text-sm">
                          <span className="text-gray-500">Complaint:</span>
                          <button
                            onClick={() => router.push(`/grievance/complaints/${ombudsmanCase.complaint_id}`)}
                            className="text-blue-600 hover:text-blue-700 font-medium"
                          >
                            View Complaint #{ombudsmanCase.complaint_id}
                          </button>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-3">
                          <div className="flex items-start gap-2">
                            <FileText className="h-4 w-4 text-gray-400 mt-0.5" />
                            <div className="flex-1">
                              <p className="text-xs text-gray-500">Ombudsman Office</p>
                              <p className="text-sm font-medium text-gray-900">{ombudsmanCase.ombudsman_office}</p>
                            </div>
                          </div>

                          {ombudsmanCase.submitted_date && (
                            <div className="flex items-start gap-2">
                              <Calendar className="h-4 w-4 text-gray-400 mt-0.5" />
                              <div className="flex-1">
                                <p className="text-xs text-gray-500">Submitted</p>
                                <p className="text-sm font-medium text-gray-900">
                                  {formatDate(ombudsmanCase.submitted_date)}
                                  <span className="text-gray-500 ml-2">({daysElapsed} days ago)</span>
                                </p>
                              </div>
                            </div>
                          )}

                          {ombudsmanCase.hearing_date && (
                            <div className="flex items-start gap-2">
                              <Calendar className="h-4 w-4 text-orange-400 mt-0.5" />
                              <div className="flex-1">
                                <p className="text-xs text-gray-500">Hearing Date</p>
                                <p className="text-sm font-medium text-gray-900">{formatDate(ombudsmanCase.hearing_date)}</p>
                                {ombudsmanCase.bank_representative && (
                                  <p className="text-xs text-gray-500">Rep: {ombudsmanCase.bank_representative}</p>
                                )}
                              </div>
                            </div>
                          )}

                          {ombudsmanCase.compensation_awarded && ombudsmanCase.compensation_awarded > 0 && (
                            <div className="flex items-start gap-2">
                              <DollarSign className="h-4 w-4 text-green-400 mt-0.5" />
                              <div className="flex-1">
                                <p className="text-xs text-gray-500">Compensation Awarded</p>
                                <p className="text-sm font-medium text-green-600">
                                  {formatCurrency(ombudsmanCase.compensation_awarded)}
                                  {ombudsmanCase.compensation_paid && (
                                    <span className="text-xs text-green-700 ml-2">(Paid)</span>
                                  )}
                                </p>
                              </div>
                            </div>
                          )}
                        </div>

                        {/* Grounds of Complaint */}
                        <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                          <p className="text-xs font-medium text-gray-700 mb-1">Grounds of Complaint:</p>
                          <p className="text-sm text-gray-600">{ombudsmanCase.grounds_of_complaint}</p>
                        </div>

                        {/* Award Details */}
                        {ombudsmanCase.award_details && (
                          <div className="mt-3 p-3 bg-green-50 rounded-lg">
                            <p className="text-xs font-medium text-green-900 mb-1">Award Details:</p>
                            <p className="text-sm text-green-700">{ombudsmanCase.award_details}</p>
                            {ombudsmanCase.award_date && (
                              <p className="text-xs text-green-600 mt-1">
                                Issued on {formatDate(ombudsmanCase.award_date)}
                              </p>
                            )}
                          </div>
                        )}

                        {/* Bank Response */}
                        {ombudsmanCase.bank_response && (
                          <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                            <p className="text-xs font-medium text-blue-900 mb-1">Bank Response:</p>
                            <p className="text-sm text-blue-700">{ombudsmanCase.bank_response}</p>
                            {ombudsmanCase.bank_response_date && (
                              <p className="text-xs text-blue-600 mt-1">
                                Responded on {formatDate(ombudsmanCase.bank_response_date)}
                              </p>
                            )}
                          </div>
                        )}

                        {/* Compliance Indicators */}
                        <div className="mt-3 flex items-center gap-4">
                          {ombudsmanCase.rbi_guidelines_followed && (
                            <div className="flex items-center gap-1 text-xs text-green-600">
                              <CheckCircle className="h-3 w-3" />
                              RBI Guidelines Followed
                            </div>
                          )}
                          {ombudsmanCase.resolution_within_30_days && (
                            <div className="flex items-center gap-1 text-xs text-green-600">
                              <CheckCircle className="h-3 w-3" />
                              Resolved within 30 days
                            </div>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex flex-col gap-2 ml-4">
                      <button
                        onClick={() => router.push(`/grievance/complaints/${ombudsmanCase.complaint_id}`)}
                        className="px-4 py-2 border border-gray-300 text-sm rounded-lg hover:bg-gray-50 flex items-center gap-2"
                      >
                        View Details
                        <ChevronRight className="h-4 w-4" />
                      </button>
                    </div>
                  </div>

                  {/* Timeline */}
                  <div className="mt-4 pt-4 border-t border-gray-100">
                    <div className="flex flex-wrap items-center gap-3 text-xs text-gray-500">
                      <div className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        Created: {formatDate(ombudsmanCase.created_at)}
                      </div>
                      {ombudsmanCase.submitted_date && (
                        <>
                          <span>→</span>
                          <div>Submitted: {formatDate(ombudsmanCase.submitted_date)}</div>
                        </>
                      )}
                      {ombudsmanCase.acknowledgement_date && (
                        <>
                          <span>→</span>
                          <div>Acknowledged: {formatDate(ombudsmanCase.acknowledgement_date)}</div>
                        </>
                      )}
                      {ombudsmanCase.award_date && (
                        <>
                          <span>→</span>
                          <div>Award: {formatDate(ombudsmanCase.award_date)}</div>
                        </>
                      )}
                      {ombudsmanCase.closure_date && (
                        <>
                          <span>→</span>
                          <div>Closed: {formatDate(ombudsmanCase.closure_date)}</div>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Pagination */}
        {!loading && cases.length > 0 && (
          <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
            <div className="text-sm text-gray-700">
              Showing {(page - 1) * limit + 1} to {Math.min(page * limit, total)} of {total} results
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      {/* RBI Compliance Info */}
      <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
        <div className="flex items-start gap-3">
          <Shield className="h-6 w-6 text-purple-600 flex-shrink-0" />
          <div>
            <h3 className="font-semibold text-purple-900 mb-2">RBI Banking Ombudsman Scheme</h3>
            <p className="text-sm text-purple-700 mb-2">
              All cases are tracked in compliance with the Banking Ombudsman Scheme 2006. 
              Cases should ideally be resolved within 30 days of submission.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-3">
              <div className="bg-white bg-opacity-50 rounded p-3">
                <p className="text-xs text-purple-600 font-medium">Total Cases</p>
                <p className="text-lg font-bold text-purple-900">{total}</p>
              </div>
              <div className="bg-white bg-opacity-50 rounded p-3">
                <p className="text-xs text-purple-600 font-medium">Resolved within SLA</p>
                <p className="text-lg font-bold text-purple-900">{within30Days}</p>
              </div>
              <div className="bg-white bg-opacity-50 rounded p-3">
                <p className="text-xs text-purple-600 font-medium">Compliance Rate</p>
                <p className="text-lg font-bold text-purple-900">
                  {total > 0 ? ((within30Days / total) * 100).toFixed(1) : 0}%
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
