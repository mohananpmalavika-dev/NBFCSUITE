'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Clock,
  Filter,
  Search,
  ChevronRight,
} from 'lucide-react';
import { grievanceService } from '@/services/grievance.service';
import type { ComplaintEscalation } from '@/types/grievance';
import {
  EscalationLevel,
  EscalationLevelLabels,
  formatDate,
  formatDateTime,
  calculateHoursElapsed,
} from '@/types/grievance';

export default function EscalationsPage() {
  const router = useRouter();
  const [escalations, setEscalations] = useState<ComplaintEscalation[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [levelFilter, setLevelFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [showFilters, setShowFilters] = useState(false);

  // Pagination
  const [page, setPage] = useState(1);
  const [limit] = useState(20);

  useEffect(() => {
    loadEscalations();
  }, [page, levelFilter, statusFilter]);

  const loadEscalations = async () => {
    try {
      setLoading(true);
      setError(null);

      const params: any = {
        skip: (page - 1) * limit,
        limit,
      };

      if (levelFilter) params.escalation_level = levelFilter;
      if (statusFilter) params.status = statusFilter;

      const data = await grievanceService.listEscalations(params);
      setEscalations(data.escalations);
      setTotal(data.total);
    } catch (err) {
      console.error('Failed to load escalations:', err);
      setError('Failed to load escalations. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleAcknowledge = async (escalationId: number) => {
    try {
      await grievanceService.acknowledgeEscalation(escalationId, {
        acknowledgement_notes: 'Escalation acknowledged via UI',
      });
      loadEscalations();
    } catch (err) {
      console.error('Failed to acknowledge escalation:', err);
      alert('Failed to acknowledge escalation');
    }
  };

  const handleResolve = async (escalationId: number) => {
    const resolutionNotes = prompt('Enter resolution notes:');
    const actionTaken = prompt('Enter action taken:');

    if (!resolutionNotes || !actionTaken) {
      return;
    }

    try {
      await grievanceService.resolveEscalation(escalationId, {
        resolution_notes: resolutionNotes,
        action_taken: actionTaken,
      });
      loadEscalations();
    } catch (err) {
      console.error('Failed to resolve escalation:', err);
      alert('Failed to resolve escalation');
    }
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'PENDING':
        return 'bg-yellow-100 text-yellow-800';
      case 'ACKNOWLEDGED':
        return 'bg-blue-100 text-blue-800';
      case 'RESOLVED':
        return 'bg-green-100 text-green-800';
      case 'REJECTED':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getLevelColor = (level: EscalationLevel): string => {
    const levelNum = parseInt(level.replace('LEVEL_', '')) || 0;
    if (level === EscalationLevel.OMBUDSMAN) return 'bg-red-100 text-red-800';
    if (levelNum >= 4) return 'bg-orange-100 text-orange-800';
    if (levelNum >= 2) return 'bg-yellow-100 text-yellow-800';
    return 'bg-blue-100 text-blue-800';
  };

  const totalPages = Math.ceil(total / limit);

  const pendingCount = escalations.filter(e => e.status === 'PENDING').length;
  const acknowledgedCount = escalations.filter(e => e.status === 'ACKNOWLEDGED').length;
  const resolvedCount = escalations.filter(e => e.status === 'RESOLVED').length;
  const breachedCount = escalations.filter(e => e.escalation_sla_breach).length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Escalation Management</h1>
          <p className="text-gray-600 mt-1">
            {total} total escalations • Page {page} of {totalPages}
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
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-yellow-50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-1">
            <Clock className="h-4 w-4 text-yellow-600" />
            <span className="text-sm text-gray-600">Pending</span>
          </div>
          <p className="text-2xl font-bold text-yellow-600">{pendingCount}</p>
        </div>

        <div className="bg-blue-50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-1">
            <CheckCircle className="h-4 w-4 text-blue-600" />
            <span className="text-sm text-gray-600">Acknowledged</span>
          </div>
          <p className="text-2xl font-bold text-blue-600">{acknowledgedCount}</p>
        </div>

        <div className="bg-green-50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-1">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <span className="text-sm text-gray-600">Resolved</span>
          </div>
          <p className="text-2xl font-bold text-green-600">{resolvedCount}</p>
        </div>

        <div className="bg-red-50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-1">
            <AlertTriangle className="h-4 w-4 text-red-600" />
            <span className="text-sm text-gray-600">SLA Breached</span>
          </div>
          <p className="text-2xl font-bold text-red-600">{breachedCount}</p>
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
                  value={levelFilter}
                  onChange={(e) => setLevelFilter(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Levels</option>
                  {Object.entries(EscalationLevelLabels).map(([key, label]) => (
                    <option key={key} value={key}>{label}</option>
                  ))}
                </select>
              </div>

              <div className="flex-1">
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Statuses</option>
                  <option value="PENDING">Pending</option>
                  <option value="ACKNOWLEDGED">Acknowledged</option>
                  <option value="RESOLVED">Resolved</option>
                  <option value="REJECTED">Rejected</option>
                </select>
              </div>

              <button
                onClick={() => {
                  setLevelFilter('');
                  setStatusFilter('');
                }}
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

      {/* Escalations List */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : escalations.length === 0 ? (
          <div className="text-center py-16">
            <TrendingUp className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">No escalations found</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {escalations.map((escalation) => {
              const hoursElapsed = calculateHoursElapsed(escalation.escalated_at);
              const isOverdue = escalation.escalation_sla_breach;

              return (
                <div
                  key={escalation.id}
                  className="p-6 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      {/* Header */}
                      <div className="flex items-center gap-3 mb-2">
                        <span className={`inline-flex px-3 py-1 text-xs font-medium rounded-full ${getLevelColor(escalation.escalation_level)}`}>
                          {EscalationLevelLabels[escalation.escalation_level]}
                        </span>
                        <span className={`inline-flex px-3 py-1 text-xs font-medium rounded-full ${getStatusColor(escalation.status)}`}>
                          {escalation.status}
                        </span>
                        {escalation.is_auto_escalated && (
                          <span className="inline-flex px-3 py-1 text-xs font-medium rounded-full bg-purple-100 text-purple-800">
                            Auto-Escalated
                          </span>
                        )}
                        {isOverdue && (
                          <span className="inline-flex items-center gap-1 px-3 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800">
                            <AlertTriangle className="h-3 w-3" />
                            SLA Breached
                          </span>
                        )}
                      </div>

                      {/* Content */}
                      <div className="space-y-2">
                        <div className="flex items-center gap-2 text-sm">
                          <span className="text-gray-500">Complaint:</span>
                          <button
                            onClick={() => router.push(`/grievance/complaints/${escalation.complaint_id}`)}
                            className="text-blue-600 hover:text-blue-700 font-medium"
                          >
                            View Complaint #{escalation.complaint_id}
                          </button>
                        </div>

                        <div className="flex items-center gap-2 text-sm">
                          <span className="text-gray-500">Reason:</span>
                          <span className="font-medium">{escalation.escalation_reason}</span>
                        </div>

                        {escalation.reason_details && (
                          <p className="text-sm text-gray-600">{escalation.reason_details}</p>
                        )}

                        <div className="flex items-center gap-4 text-sm text-gray-500">
                          <span>Escalation #{escalation.escalation_number}</span>
                          <span>•</span>
                          <span>Escalated {hoursElapsed}h ago</span>
                          <span>•</span>
                          <span>SLA: {escalation.escalation_sla_hours}h</span>
                        </div>

                        {escalation.resolution_notes && (
                          <div className="mt-3 p-3 bg-green-50 rounded-lg">
                            <p className="text-sm font-medium text-green-900">Resolution Notes:</p>
                            <p className="text-sm text-green-700 mt-1">{escalation.resolution_notes}</p>
                            {escalation.action_taken && (
                              <p className="text-sm text-green-700 mt-1">
                                <span className="font-medium">Action:</span> {escalation.action_taken}
                              </p>
                            )}
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex flex-col gap-2 ml-4">
                      {escalation.status === 'PENDING' && (
                        <button
                          onClick={() => handleAcknowledge(escalation.id)}
                          className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700"
                        >
                          Acknowledge
                        </button>
                      )}
                      {escalation.status === 'ACKNOWLEDGED' && (
                        <button
                          onClick={() => handleResolve(escalation.id)}
                          className="px-4 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700"
                        >
                          Resolve
                        </button>
                      )}
                      <button
                        onClick={() => router.push(`/grievance/complaints/${escalation.complaint_id}`)}
                        className="px-4 py-2 border border-gray-300 text-sm rounded-lg hover:bg-gray-50 flex items-center gap-2"
                      >
                        View
                        <ChevronRight className="h-4 w-4" />
                      </button>
                    </div>
                  </div>

                  {/* Timeline */}
                  <div className="mt-4 pt-4 border-t border-gray-100">
                    <div className="flex items-center gap-4 text-xs text-gray-500">
                      <div className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        Escalated: {formatDateTime(escalation.escalated_at)}
                      </div>
                      {escalation.acknowledged_at && (
                        <>
                          <span>•</span>
                          <div>Acknowledged: {formatDateTime(escalation.acknowledged_at)}</div>
                        </>
                      )}
                      {escalation.resolved_at && (
                        <>
                          <span>•</span>
                          <div>Resolved: {formatDateTime(escalation.resolved_at)}</div>
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
        {!loading && escalations.length > 0 && (
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

      {/* Escalation Hierarchy Reference */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="font-semibold mb-4">Escalation Hierarchy</h3>
        <div className="grid grid-cols-1 md:grid-cols-7 gap-2">
          {Object.entries(EscalationLevelLabels).map(([key, label]) => (
            <div key={key} className={`p-3 rounded-lg text-center ${getLevelColor(key as EscalationLevel)}`}>
              <p className="text-xs font-medium">{label}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
