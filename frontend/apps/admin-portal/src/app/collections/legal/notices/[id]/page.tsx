'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { legalApi } from '@/lib/api/collection';
import { LegalNotice } from '@/types/collection';

export default function LegalNoticeDetailPage() {
  const router = useRouter();
  const params = useParams();
  const noticeId = params.id as string;

  const [notice, setNotice] = useState<LegalNotice | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadNoticeDetails();
  }, [noticeId]);

  const loadNoticeDetails = async () => {
    try {
      setLoading(true);
      const data = await legalApi.getNotice(noticeId);
      setNotice(data);
    } catch (error) {
      console.error('Failed to load notice details:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      draft: 'bg-gray-100 text-gray-800',
      sent: 'bg-blue-100 text-blue-800',
      acknowledged: 'bg-green-100 text-green-800',
      expired: 'bg-red-100 text-red-800',
      replied: 'bg-purple-100 text-purple-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getNoticeTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      demand_notice: 'Demand Notice',
      legal_notice_138: 'Legal Notice (Sec 138)',
      arbitration_notice: 'Arbitration Notice',
      possession_notice: 'Possession Notice',
      auction_notice: 'Auction Notice',
      recall_notice: 'Recall Notice',
    };
    return labels[type] || type;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gray-500">Loading notice details...</div>
      </div>
    );
  }

  if (!notice) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-gray-500 mb-4">Notice not found</p>
          <button
            onClick={() => router.push('/collections/legal')}
            className="text-blue-600 hover:text-blue-700"
          >
            Back to Legal & Recovery
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <button
            onClick={() => router.push('/collections/legal')}
            className="text-blue-600 hover:text-blue-700 mb-2 flex items-center gap-1"
          >
            ← Back to Legal & Recovery
          </button>
          <h1 className="text-2xl font-bold text-gray-900">
            {getNoticeTypeLabel(notice.notice_type)}
          </h1>
          <p className="text-gray-600 mt-1">{notice.notice_number}</p>
        </div>
        <div className="flex gap-3">
          <span className={`px-4 py-2 rounded-lg text-sm font-medium ${getStatusColor(notice.delivery_status)}`}>
            {notice.delivery_status.toUpperCase()}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Notice Details */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Notice Information</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Notice Number</p>
                <p className="font-medium text-gray-900">{notice.notice_number}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Notice Type</p>
                <p className="font-medium text-gray-900">{getNoticeTypeLabel(notice.notice_type)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Notice Stage</p>
                <p className="font-medium text-gray-900">{notice.notice_stage}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Loan Account ID</p>
                <p className="font-medium text-gray-900">{notice.loan_account_id}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Customer ID</p>
                <p className="font-medium text-gray-900">{notice.customer_id}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Amount Demanded</p>
                <p className="text-xl font-bold text-red-600">{formatCurrency(notice.notice_amount_demanded)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Notice Date</p>
                <p className="font-medium text-gray-900">{formatDate(notice.notice_date)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Dispatch Mode</p>
                <p className="font-medium text-gray-900 capitalize">{notice.dispatch_mode}</p>
              </div>
            </div>
          </div>

          {/* Delivery Details */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Delivery Information</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Delivery Status</p>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(notice.delivery_status)}`}>
                  {notice.delivery_status.toUpperCase()}
                </span>
              </div>
              {notice.delivery_date && (
                <div>
                  <p className="text-sm text-gray-600">Delivery Date</p>
                  <p className="font-medium text-green-600">{formatDate(notice.delivery_date)}</p>
                </div>
              )}
            </div>
          </div>

          {/* Response Information */}
          {notice.response_received && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Response Received</h2>
              <div className="space-y-3">
                {notice.response_date && (
                  <div>
                    <p className="text-sm text-gray-600">Response Date</p>
                    <p className="font-medium text-gray-900">{formatDate(notice.response_date)}</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Actions</h2>
            <div className="space-y-2">
              <button
                onClick={() => router.push(`/collections/legal/notices/${notice.id}/edit`)}
                className="w-full px-4 py-2 bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 text-left"
              >
                ✏️ Edit Notice
              </button>
              <button
                onClick={() => alert('Download PDF functionality')}
                className="w-full px-4 py-2 bg-purple-50 text-purple-700 rounded-lg hover:bg-purple-100 text-left"
              >
                📥 Download PDF
              </button>
              <button
                onClick={() => alert('Send notice functionality')}
                className="w-full px-4 py-2 bg-green-50 text-green-700 rounded-lg hover:bg-green-100 text-left"
              >
                📧 Send Notice
              </button>
              {notice.delivery_status === 'sent' && (
                <button
                  onClick={() => alert('Track delivery functionality')}
                  className="w-full px-4 py-2 bg-yellow-50 text-yellow-700 rounded-lg hover:bg-yellow-100 text-left"
                >
                  📍 Track Delivery
                </button>
              )}
              <button
                onClick={() => router.push(`/collections/legal/cases/new?notice_id=${notice.id}`)}
                className="w-full px-4 py-2 bg-red-50 text-red-700 rounded-lg hover:bg-red-100 text-left"
              >
                ⚖️ Create Legal Case
              </button>
            </div>
          </div>

          {/* Timeline */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Timeline</h2>
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 bg-blue-600 rounded-full mt-2"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">Notice Created</p>
                  <p className="text-xs text-gray-600">{formatDate(notice.created_at)}</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 bg-purple-600 rounded-full mt-2"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">Notice Date</p>
                  <p className="text-xs text-gray-600">{formatDate(notice.notice_date)}</p>
                </div>
              </div>
              {notice.delivery_date && (
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-green-600 rounded-full mt-2"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">Delivered</p>
                    <p className="text-xs text-gray-600">{formatDate(notice.delivery_date)}</p>
                  </div>
                </div>
              )}
              {notice.response_date && (
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-yellow-600 rounded-full mt-2"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">Response Received</p>
                    <p className="text-xs text-gray-600">{formatDate(notice.response_date)}</p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Status Info */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Status</h2>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Delivery Status</span>
                <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(notice.delivery_status)}`}>
                  {notice.delivery_status.toUpperCase()}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Response Received</span>
                <span className={notice.response_received ? 'text-green-600' : 'text-gray-400'}>
                  {notice.response_received ? '✓ Yes' : '✗ No'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
