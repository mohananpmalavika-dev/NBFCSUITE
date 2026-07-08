'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  AlertTriangle,
  CheckCircle,
  Clock,
  TrendingUp,
  Users,
  AlertCircle,
  MessageSquare,
  Shield,
  BarChart3,
  ArrowUpRight,
  ArrowDownRight,
} from 'lucide-react';
import { grievanceService } from '@/services/grievance.service';
import type { ComplaintStatistics, Complaint } from '@/types/grievance';
import {
  ComplaintStatusLabels,
  ComplaintStatusColors,
  ComplaintPriorityLabels,
  ComplaintCategoryLabels,
  ChannelTypeLabels,
  formatDate,
  getSLAStatus,
} from '@/types/grievance';

export default function GrievanceDashboard() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [statistics, setStatistics] = useState<ComplaintStatistics | null>(null);
  const [recentComplaints, setRecentComplaints] = useState<Complaint[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch statistics and recent complaints
      const [stats, complaintsData] = await Promise.all([
        grievanceService.getComplaintStatistics(),
        grievanceService.listComplaints({ limit: 10 }),
      ]);

      setStatistics(stats);
      setRecentComplaints(complaintsData.complaints);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      setError('Failed to load dashboard data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center gap-3">
          <AlertCircle className="h-5 w-5 text-red-600" />
          <div>
            <h3 className="font-semibold text-red-900">Error</h3>
            <p className="text-red-700">{error}</p>
          </div>
        </div>
        <button
          onClick={loadDashboardData}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!statistics) {
    return <div className="text-center text-gray-500">No data available</div>;
  }

  const slaComplianceRate = statistics.total_complaints > 0
    ? ((statistics.within_sla / statistics.total_complaints) * 100).toFixed(1)
    : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Grievance & Complaint Management</h1>
          <p className="text-gray-600 mt-1">
            Multi-channel intake, SLA tracking, escalation workflow, and ombudsman management
          </p>
        </div>
        <button
          onClick={() => router.push('/grievance/complaints/new')}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
        >
          <MessageSquare className="h-4 w-4" />
          Register Complaint
        </button>
      </div>

      {/* Quick Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Total Complaints */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-blue-100 rounded-lg">
              <MessageSquare className="h-6 w-6 text-blue-600" />
            </div>
            <span className="text-sm font-medium text-gray-500">Total</span>
          </div>
          <p className="text-3xl font-bold text-gray-900">{statistics.total_complaints}</p>
          <p className="text-sm text-gray-600 mt-1">Complaints Registered</p>
        </div>

        {/* SLA Compliance */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-green-100 rounded-lg">
              <CheckCircle className="h-6 w-6 text-green-600" />
            </div>
            <span className="text-sm font-medium text-gray-500">SLA</span>
          </div>
          <p className="text-3xl font-bold text-green-600">{slaComplianceRate}%</p>
          <p className="text-sm text-gray-600 mt-1">Within SLA ({statistics.within_sla})</p>
        </div>

        {/* SLA Breached */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-red-100 rounded-lg">
              <AlertTriangle className="h-6 w-6 text-red-600" />
            </div>
            <span className="text-sm font-medium text-gray-500">Breached</span>
          </div>
          <p className="text-3xl font-bold text-red-600">{statistics.sla_breached}</p>
          <p className="text-sm text-gray-600 mt-1">SLA Breached</p>
        </div>

        {/* Avg Resolution Time */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-purple-100 rounded-lg">
              <Clock className="h-6 w-6 text-purple-600" />
            </div>
            <span className="text-sm font-medium text-gray-500">Time</span>
          </div>
          <p className="text-3xl font-bold text-purple-600">
            {Math.round(statistics.avg_resolution_hours)}h
          </p>
          <p className="text-sm text-gray-600 mt-1">Avg Resolution Time</p>
        </div>
      </div>

      {/* Status Overview */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <BarChart3 className="h-5 w-5 text-gray-600" />
          Complaint Status Overview
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <p className="text-2xl font-bold text-blue-600">{statistics.registered}</p>
            <p className="text-sm text-gray-600">Registered</p>
          </div>
          <div className="text-center p-4 bg-yellow-50 rounded-lg">
            <p className="text-2xl font-bold text-yellow-600">{statistics.in_progress}</p>
            <p className="text-sm text-gray-600">In Progress</p>
          </div>
          <div className="text-center p-4 bg-red-50 rounded-lg">
            <p className="text-2xl font-bold text-red-600">{statistics.escalated}</p>
            <p className="text-sm text-gray-600">Escalated</p>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <p className="text-2xl font-bold text-green-600">{statistics.resolved}</p>
            <p className="text-sm text-gray-600">Resolved</p>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <p className="text-2xl font-bold text-gray-600">{statistics.closed}</p>
            <p className="text-sm text-gray-600">Closed</p>
          </div>
        </div>
      </div>

      {/* Key Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Escalation Rate */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="h-5 w-5 text-orange-600" />
            <h3 className="font-semibold">Escalation Metrics</h3>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Escalation Rate</span>
              <span className="font-bold text-orange-600">
                {statistics.escalation_rate.toFixed(1)}%
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Escalated Cases</span>
              <span className="font-bold">{statistics.escalated}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Ombudsman Cases</span>
              <span className="font-bold text-red-600">{statistics.ombudsman_cases}</span>
            </div>
          </div>
        </div>

        {/* Customer Satisfaction */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center gap-2 mb-4">
            <Users className="h-5 w-5 text-green-600" />
            <h3 className="font-semibold">Customer Satisfaction</h3>
          </div>
          <div className="text-center">
            <p className="text-4xl font-bold text-green-600">
              {statistics.customer_satisfaction_avg.toFixed(1)}
            </p>
            <p className="text-sm text-gray-600 mt-1">Out of 5.0</p>
            <div className="flex justify-center gap-1 mt-3">
              {[1, 2, 3, 4, 5].map((star) => (
                <span
                  key={star}
                  className={`text-2xl ${
                    star <= Math.round(statistics.customer_satisfaction_avg)
                      ? 'text-yellow-400'
                      : 'text-gray-300'
                  }`}
                >
                  ★
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Regulatory Alerts */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center gap-2 mb-4">
            <Shield className="h-5 w-5 text-purple-600" />
            <h3 className="font-semibold">Regulatory Compliance</h3>
          </div>
          <div className="space-y-3">
            <div className="p-3 bg-green-50 rounded-lg">
              <p className="text-sm text-gray-600">SLA Compliance</p>
              <p className="font-bold text-green-600">{slaComplianceRate}%</p>
            </div>
            <div className="p-3 bg-purple-50 rounded-lg">
              <p className="text-sm text-gray-600">Ombudsman Cases</p>
              <p className="font-bold text-purple-600">{statistics.ombudsman_cases}</p>
            </div>
            <div className="p-3 bg-blue-50 rounded-lg">
              <p className="text-sm text-gray-600">Audit Trail</p>
              <p className="font-bold text-blue-600">100%</p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Complaints */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            <Clock className="h-5 w-5 text-gray-600" />
            Recent Complaints
          </h2>
          <button
            onClick={() => router.push('/grievance/complaints')}
            className="text-blue-600 hover:text-blue-700 text-sm font-medium"
          >
            View All →
          </button>
        </div>
        <div className="space-y-3">
          {recentComplaints.length === 0 ? (
            <p className="text-center text-gray-500 py-8">No recent complaints</p>
          ) : (
            recentComplaints.map((complaint) => {
              const slaStatus = getSLAStatus(complaint);
              return (
                <div
                  key={complaint.id}
                  onClick={() => router.push(`/grievance/complaints/${complaint.id}`)}
                  className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors"
                >
                  <div className="flex-shrink-0">
                    <div className={`px-3 py-1 rounded-full text-xs font-medium ${ComplaintStatusColors[complaint.status]}`}>
                      {ComplaintStatusLabels[complaint.status]}
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-900 truncate">{complaint.subject}</p>
                    <p className="text-sm text-gray-600 truncate">
                      {complaint.complaint_number} • {complaint.customer_name || `Customer #${complaint.customer_id}`}
                    </p>
                  </div>
                  <div className="flex-shrink-0 text-right">
                    <p className={`text-sm font-medium ${slaStatus.color}`}>{slaStatus.label}</p>
                    <p className="text-xs text-gray-500">{formatDate(complaint.registered_date)}</p>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <button
          onClick={() => router.push('/grievance/complaints')}
          className="p-4 bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-lg hover:from-blue-600 hover:to-blue-700 transition-all shadow-lg"
        >
          <MessageSquare className="h-6 w-6 mb-2" />
          <h3 className="font-semibold">View All Complaints</h3>
          <p className="text-sm opacity-90">Manage and track complaints</p>
        </button>

        <button
          onClick={() => router.push('/grievance/escalations')}
          className="p-4 bg-gradient-to-br from-orange-500 to-orange-600 text-white rounded-lg hover:from-orange-600 hover:to-orange-700 transition-all shadow-lg"
        >
          <TrendingUp className="h-6 w-6 mb-2" />
          <h3 className="font-semibold">Escalations</h3>
          <p className="text-sm opacity-90">Manage escalated cases</p>
        </button>

        <button
          onClick={() => router.push('/grievance/ombudsman')}
          className="p-4 bg-gradient-to-br from-purple-500 to-purple-600 text-white rounded-lg hover:from-purple-600 hover:to-purple-700 transition-all shadow-lg"
        >
          <Shield className="h-6 w-6 mb-2" />
          <h3 className="font-semibold">Ombudsman Cases</h3>
          <p className="text-sm opacity-90">Track ombudsman proceedings</p>
        </button>
      </div>
    </div>
  );
}
