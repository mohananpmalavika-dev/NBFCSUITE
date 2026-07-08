'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import {
  ArrowLeft,
  User,
  Calendar,
  Tag,
  MessageSquare,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  Phone,
  Mail,
  MapPin,
} from 'lucide-react';
import { grievanceService } from '@/services/grievance.service';
import type { Complaint } from '@/types/grievance';
import {
  ComplaintStatus,
  ComplaintStatusLabels,
  ComplaintStatusColors,
  ComplaintPriorityLabels,
  ComplaintPriorityColors,
  ComplaintCategoryLabels,
  ChannelTypeLabels,
  ChannelTypeColors,
  formatDate,
  formatDateTime,
  getSLAStatus,
  formatCurrency,
} from '@/types/grievance';

export default function ComplaintDetailsPage() {
  const router = useRouter();
  const params = useParams();
  const [complaint, setComplaint] = useState<Complaint | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState(false);

  // Action modals
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [showAcknowledgeModal, setShowAcknowledgeModal] = useState(false);
  const [showResolveModal, setShowResolveModal] = useState(false);
  const [showCloseModal, setShowCloseModal] = useState(false);

  useEffect(() => {
    if (params.id) {
      loadComplaint(Number(params.id));
    }
  }, [params.id]);

  const loadComplaint = async (id: number) => {
    try {
      setLoading(true);
      setError(null);
      const data = await grievanceService.getComplaint(id);
      setComplaint(data);
    } catch (err) {
      console.error('Failed to load complaint:', err);
      setError('Failed to load complaint details. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !complaint) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <p className="text-red-700">{error || 'Complaint not found'}</p>
        <button
          onClick={() => router.back()}
          className="mt-4 text-blue-600 hover:text-blue-700"
        >
          ← Go Back
        </button>
      </div>
    );
  }

  const slaStatus = getSLAStatus(complaint);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => router.back()}
            className="p-2 hover:bg-gray-100 rounded-lg"
          >
            <ArrowLeft className="h-5 w-5" />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{complaint.complaint_number}</h1>
            <p className="text-gray-600 mt-1">{complaint.subject}</p>
          </div>
        </div>
        <div className="flex gap-2">
          {complaint.status === ComplaintStatus.REGISTERED && (
            <button
              onClick={() => setShowAcknowledgeModal(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Acknowledge
            </button>
          )}
          {complaint.status === ComplaintStatus.IN_PROGRESS && (
            <button
              onClick={() => setShowResolveModal(true)}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              Resolve
            </button>
          )}
          {complaint.status === ComplaintStatus.RESOLVED && (
            <button
              onClick={() => setShowCloseModal(true)}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
            >
              Close
            </button>
          )}
        </div>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="text-sm text-gray-600 mb-1">Status</div>
          <span className={`inline-flex px-3 py-1 text-sm font-medium rounded-full ${ComplaintStatusColors[complaint.status]}`}>
            {ComplaintStatusLabels[complaint.status]}
          </span>
        </div>

        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="text-sm text-gray-600 mb-1">Priority</div>
          <span className={`inline-flex px-3 py-1 text-sm font-medium rounded-full ${ComplaintPriorityColors[complaint.priority]}`}>
            {ComplaintPriorityLabels[complaint.priority]}
          </span>
        </div>

        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="text-sm text-gray-600 mb-1">SLA Status</div>
          <div className={`text-sm font-medium ${slaStatus.color}`}>
            {slaStatus.label}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="text-sm text-gray-600 mb-1">Registered</div>
          <div className="text-sm font-medium text-gray-900">
            {formatDate(complaint.registered_date)}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Complaint Details */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">Complaint Details</h2>
            
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-500">Category</label>
                <p className="text-gray-900">{ComplaintCategoryLabels[complaint.category]}</p>
                {complaint.sub_category && (
                  <p className="text-sm text-gray-600">{complaint.sub_category}</p>
                )}
              </div>

              <div>
                <label className="text-sm font-medium text-gray-500">Description</label>
                <p className="text-gray-900 whitespace-pre-wrap">{complaint.description}</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">Channel</label>
                  <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${ChannelTypeColors[complaint.channel]}`}>
                    {ChannelTypeLabels[complaint.channel]}
                  </span>
                </div>

                {complaint.source_reference && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">Source Reference</label>
                    <p className="text-sm text-gray-900">{complaint.source_reference}</p>
                  </div>
                )}
              </div>

              {complaint.related_entity_type && (
                <div>
                  <label className="text-sm font-medium text-gray-500">Related To</label>
                  <p className="text-gray-900">
                    {complaint.related_entity_type} #{complaint.related_entity_id}
                  </p>
                </div>
              )}

              {complaint.tags && (
                <div>
                  <label className="text-sm font-medium text-gray-500">Tags</label>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {complaint.tags.split(',').map((tag, idx) => (
                      <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                        {tag.trim()}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Resolution Details */}
          {complaint.resolution && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold mb-4">Resolution</h2>
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">Resolution</label>
                  <p className="text-gray-900 whitespace-pre-wrap">{complaint.resolution}</p>
                </div>

                {complaint.resolution_remarks && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">Remarks</label>
                    <p className="text-gray-900">{complaint.resolution_remarks}</p>
                  </div>
                )}

                {complaint.compensation_amount && complaint.compensation_amount > 0 && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">Compensation</label>
                    <p className="text-gray-900 font-semibold">
                      {formatCurrency(complaint.compensation_amount)}
                      {complaint.compensation_paid && (
                        <span className="ml-2 text-green-600 text-sm">(Paid)</span>
                      )}
                    </p>
                  </div>
                )}

                {complaint.customer_satisfaction && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">Customer Satisfaction</label>
                    <div className="flex items-center gap-2">
                      <div className="flex">
                        {[1, 2, 3, 4, 5].map((star) => (
                          <span
                            key={star}
                            className={`text-xl ${
                              star <= complaint.customer_satisfaction!
                                ? 'text-yellow-400'
                                : 'text-gray-300'
                            }`}
                          >
                            ★
                          </span>
                        ))}
                      </div>
                      <span className="text-sm text-gray-600">
                        {complaint.customer_satisfaction}/5
                      </span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Timeline */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">Timeline</h2>
            <div className="space-y-4">
              {/* Registered */}
              <div className="flex gap-4">
                <div className="flex-shrink-0">
                  <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                    <MessageSquare className="h-5 w-5 text-blue-600" />
                  </div>
                </div>
                <div className="flex-1">
                  <p className="font-medium text-gray-900">Complaint Registered</p>
                  <p className="text-sm text-gray-600">{formatDateTime(complaint.registered_date)}</p>
                </div>
              </div>

              {/* Acknowledged */}
              {complaint.acknowledged_date && (
                <div className="flex gap-4">
                  <div className="flex-shrink-0">
                    <div className="h-10 w-10 rounded-full bg-cyan-100 flex items-center justify-center">
                      <CheckCircle className="h-5 w-5 text-cyan-600" />
                    </div>
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">Acknowledged</p>
                    <p className="text-sm text-gray-600">{formatDateTime(complaint.acknowledged_date)}</p>
                  </div>
                </div>
              )}

              {/* Resolved */}
              {complaint.actual_resolution_date && (
                <div className="flex gap-4">
                  <div className="flex-shrink-0">
                    <div className="h-10 w-10 rounded-full bg-green-100 flex items-center justify-center">
                      <CheckCircle className="h-5 w-5 text-green-600" />
                    </div>
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">Resolved</p>
                    <p className="text-sm text-gray-600">{formatDateTime(complaint.actual_resolution_date)}</p>
                  </div>
                </div>
              )}

              {/* Closed */}
              {complaint.closed_date && (
                <div className="flex gap-4">
                  <div className="flex-shrink-0">
                    <div className="h-10 w-10 rounded-full bg-gray-100 flex items-center justify-center">
                      <XCircle className="h-5 w-5 text-gray-600" />
                    </div>
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">Closed</p>
                    <p className="text-sm text-gray-600">{formatDateTime(complaint.closed_date)}</p>
                  </div>
                </div>
              )}

              {/* Escalation */}
              {complaint.escalated_to_ombudsman && (
                <div className="flex gap-4">
                  <div className="flex-shrink-0">
                    <div className="h-10 w-10 rounded-full bg-red-100 flex items-center justify-center">
                      <AlertTriangle className="h-5 w-5 text-red-600" />
                    </div>
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">Escalated to Ombudsman</p>
                    <p className="text-sm text-gray-600">Banking Ombudsman case initiated</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Customer Information */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="font-semibold mb-4 flex items-center gap-2">
              <User className="h-5 w-5 text-gray-600" />
              Customer Information
            </h3>
            <div className="space-y-3">
              <div>
                <label className="text-sm text-gray-500">Name</label>
                <p className="text-gray-900">{complaint.customer_name || `Customer #${complaint.customer_id}`}</p>
              </div>

              {complaint.customer_email && (
                <div>
                  <label className="text-sm text-gray-500">Email</label>
                  <p className="text-gray-900 text-sm">{complaint.customer_email}</p>
                </div>
              )}

              {complaint.customer_phone && (
                <div>
                  <label className="text-sm text-gray-500">Phone</label>
                  <p className="text-gray-900">{complaint.customer_phone}</p>
                </div>
              )}

              {complaint.is_repeat && (
                <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <p className="text-sm text-yellow-800 font-medium">Repeat Complaint</p>
                  <p className="text-xs text-yellow-700 mt-1">Customer has filed similar complaints before</p>
                </div>
              )}

              {complaint.is_regulatory && (
                <div className="mt-4 p-3 bg-purple-50 border border-purple-200 rounded-lg">
                  <p className="text-sm text-purple-800 font-medium">Regulatory Complaint</p>
                  <p className="text-xs text-purple-700 mt-1">Requires special handling (30-day timeline)</p>
                </div>
              )}
            </div>
          </div>

          {/* Assignment */}
          {complaint.assigned_to && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="font-semibold mb-4">Assignment</h3>
              <div className="space-y-3">
                <div>
                  <label className="text-sm text-gray-500">Assigned To</label>
                  <p className="text-gray-900">User #{complaint.assigned_to}</p>
                </div>

                {complaint.assigned_department && (
                  <div>
                    <label className="text-sm text-gray-500">Department</label>
                    <p className="text-gray-900">{complaint.assigned_department}</p>
                  </div>
                )}

                {complaint.assigned_at && (
                  <div>
                    <label className="text-sm text-gray-500">Assigned On</label>
                    <p className="text-sm text-gray-900">{formatDateTime(complaint.assigned_at)}</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* SLA Information */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="font-semibold mb-4 flex items-center gap-2">
              <Clock className="h-5 w-5 text-gray-600" />
              SLA Information
            </h3>
            <div className="space-y-3">
              <div>
                <label className="text-sm text-gray-500">SLA Hours</label>
                <p className="text-gray-900">{complaint.sla_hours} hours</p>
              </div>

              {complaint.target_resolution_date && (
                <div>
                  <label className="text-sm text-gray-500">Target Resolution</label>
                  <p className="text-gray-900">{formatDateTime(complaint.target_resolution_date)}</p>
                </div>
              )}

              {complaint.sla_breach && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-sm text-red-800 font-medium">SLA Breached</p>
                  <p className="text-xs text-red-700 mt-1">
                    Breached by {complaint.sla_breach_hours} hours
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
