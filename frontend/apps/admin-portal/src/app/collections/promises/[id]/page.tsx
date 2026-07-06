'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { promiseApi } from '@/lib/api/collection';
import { PaymentPromise } from '@/types/collection';

export default function PromiseDetailPage() {
  const router = useRouter();
  const params = useParams();
  const promiseId = params.id as string;

  const [promise, setPromise] = useState<PaymentPromise | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    loadPromiseDetails();
  }, [promiseId]);

  const loadPromiseDetails = async () => {
    try {
      setLoading(true);
      const data = await promiseApi.getPromise(promiseId);
      setPromise(data);
    } catch (error) {
      console.error('Failed to load promise details:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleMarkFulfilled = async () => {
    if (!promise) return;
    
    const confirmed = window.confirm('Mark this promise as fulfilled?');
    if (!confirmed) return;

    setActionLoading(true);
    try {
      await promiseApi.fulfillPromise(promise.id);
      loadPromiseDetails();
    } catch (error) {
      console.error('Failed to fulfill promise:', error);
      alert('Failed to mark promise as fulfilled');
    } finally {
      setActionLoading(false);
    }
  };

  const handleMarkBroken = async () => {
    if (!promise) return;
    
    const reason = window.prompt('Reason for marking as broken:');
    if (!reason) return;

    setActionLoading(true);
    try {
      await promiseApi.breakPromise(promise.id, reason);
      loadPromiseDetails();
    } catch (error) {
      console.error('Failed to break promise:', error);
      alert('Failed to mark promise as broken');
    } finally {
      setActionLoading(false);
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

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'bg-yellow-100 text-yellow-800',
      fulfilled: 'bg-green-100 text-green-800',
      broken: 'bg-red-100 text-red-800',
      partially_fulfilled: 'bg-blue-100 text-blue-800',
      rescheduled: 'bg-purple-100 text-purple-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getDaysUntilDue = (dueDate: string) => {
    const today = new Date();
    const due = new Date(dueDate);
    const diffTime = due.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gray-500">Loading promise details...</div>
      </div>
    );
  }

  if (!promise) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-gray-500 mb-4">Promise not found</p>
          <button
            onClick={() => router.push('/collections/promises')}
            className="text-blue-600 hover:text-blue-700"
          >
            Back to Promises
          </button>
        </div>
      </div>
    );
  }

  const daysUntilDue = getDaysUntilDue(promise.promise_date);
  const isPastDue = daysUntilDue < 0;
  const isDueSoon = daysUntilDue >= 0 && daysUntilDue <= 3;

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <button
            onClick={() => router.push('/collections/promises')}
            className="text-blue-600 hover:text-blue-700 mb-2 flex items-center gap-1"
          >
            ← Back to Promises
          </button>
          <h1 className="text-2xl font-bold text-gray-900">Payment Promise</h1>
          <p className="text-gray-600 mt-1">Loan: {promise.loan_account_id}</p>
        </div>
        <span className={`px-4 py-2 rounded-lg text-sm font-medium ${getStatusColor(promise.status)}`}>
          {promise.status.replace('_', ' ').toUpperCase()}
        </span>
      </div>

      {/* Alert Banner */}
      {promise.status === 'pending' && isPastDue && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-red-900">Promise Overdue</h3>
              <p className="text-sm text-red-700 mt-1">
                This promise is {Math.abs(daysUntilDue)} days overdue. Follow up immediately.
              </p>
            </div>
            <button
              onClick={handleMarkBroken}
              disabled={actionLoading}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
            >
              Mark as Broken
            </button>
          </div>
        </div>
      )}

      {promise.status === 'pending' && isDueSoon && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-yellow-900">Due Soon</h3>
              <p className="text-sm text-yellow-700 mt-1">
                This promise is due in {daysUntilDue} day{daysUntilDue !== 1 ? 's' : ''}. Send reminder.
              </p>
            </div>
          </div>
        </div>
      )}

      {promise.status === 'pending' && !isPastDue && !isDueSoon && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-green-900">Active Promise</h3>
              <p className="text-sm text-green-700 mt-1">
                Payment expected on {formatDate(promise.promise_date)}
              </p>
            </div>
            <button
              onClick={handleMarkFulfilled}
              disabled={actionLoading}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
            >
              Mark as Fulfilled
            </button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Promise Details */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Promise Details</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Loan Account</p>
                <p className="font-medium text-gray-900">{promise.loan_account_id}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Customer Name</p>
                <p className="font-medium text-gray-900">{promise.customer_name || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Promised Amount</p>
                <p className="text-xl font-bold text-blue-600">{formatCurrency(promise.promised_amount)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Promise Date</p>
                <p className="font-medium text-gray-900">{formatDate(promise.promise_date)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Promise Type</p>
                <p className="font-medium text-gray-900 capitalize">{promise.promise_type.replace('_', ' ')}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Created On</p>
                <p className="font-medium text-gray-900">{formatDateTime(promise.created_at)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Created By</p>
                <p className="font-medium text-gray-900">{promise.created_by}</p>
              </div>
              {promise.channel && (
                <div>
                  <p className="text-sm text-gray-600">Channel</p>
                  <p className="font-medium text-gray-900 capitalize">{promise.channel}</p>
                </div>
              )}
            </div>
          </div>

          {/* Fulfillment Details */}
          {(promise.fulfilled_amount > 0 || promise.status === 'fulfilled' || promise.status === 'partially_fulfilled') && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Fulfillment Details</h2>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Fulfilled Amount</p>
                  <p className="text-xl font-bold text-green-600">{formatCurrency(promise.fulfilled_amount)}</p>
                </div>
                {promise.fulfilled_date && (
                  <div>
                    <p className="text-sm text-gray-600">Fulfilled Date</p>
                    <p className="font-medium text-gray-900">{formatDate(promise.fulfilled_date)}</p>
                  </div>
                )}
                {promise.payment_mode && (
                  <div>
                    <p className="text-sm text-gray-600">Payment Mode</p>
                    <p className="font-medium text-gray-900 capitalize">{promise.payment_mode.replace('_', ' ')}</p>
                  </div>
                )}
                {promise.reference_number && (
                  <div>
                    <p className="text-sm text-gray-600">Reference Number</p>
                    <p className="font-medium text-gray-900">{promise.reference_number}</p>
                  </div>
                )}
              </div>
              {promise.promised_amount > promise.fulfilled_amount && (
                <div className="mt-4 p-3 bg-yellow-50 rounded-lg">
                  <p className="text-sm text-yellow-800">
                    <strong>Partial Fulfillment:</strong> Pending amount: {formatCurrency(promise.promised_amount - promise.fulfilled_amount)}
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Broken Promise Details */}
          {promise.status === 'broken' && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Broken Promise</h2>
              <div className="space-y-3">
                {promise.broken_date && (
                  <div>
                    <p className="text-sm text-gray-600">Broken Date</p>
                    <p className="font-medium text-gray-900">{formatDate(promise.broken_date)}</p>
                  </div>
                )}
                {promise.broken_reason && (
                  <div>
                    <p className="text-sm text-gray-600">Reason</p>
                    <p className="font-medium text-red-600">{promise.broken_reason}</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Notes */}
          {promise.notes && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Notes</h2>
              <p className="text-gray-700 whitespace-pre-wrap">{promise.notes}</p>
            </div>
          )}

          {/* Follow-up Actions */}
          {promise.follow_up_actions && promise.follow_up_actions.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Follow-up Actions</h2>
              <div className="space-y-3">
                {promise.follow_up_actions.map((action, index) => (
                  <div key={index} className="p-4 bg-gray-50 rounded-lg">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">{action.action}</p>
                        <p className="text-sm text-gray-600 mt-1">{action.description}</p>
                        <p className="text-xs text-gray-500 mt-2">
                          Due: {formatDate(action.due_date)}
                        </p>
                      </div>
                      <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${action.completed ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                        {action.completed ? 'Completed' : 'Pending'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Quick Actions */}
          {promise.status === 'pending' && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
              <div className="space-y-2">
                <button
                  onClick={handleMarkFulfilled}
                  disabled={actionLoading}
                  className="w-full px-4 py-2 bg-green-50 text-green-700 rounded-lg hover:bg-green-100 text-left disabled:opacity-50"
                >
                  ✅ Mark as Fulfilled
                </button>
                <button
                  onClick={handleMarkBroken}
                  disabled={actionLoading}
                  className="w-full px-4 py-2 bg-red-50 text-red-700 rounded-lg hover:bg-red-100 text-left disabled:opacity-50"
                >
                  ❌ Mark as Broken
                </button>
                <button
                  onClick={() => router.push(`/collections/promises/${promise.id}/reschedule`)}
                  className="w-full px-4 py-2 bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 text-left"
                >
                  📅 Reschedule
                </button>
                <button
                  onClick={() => alert('Send reminder functionality')}
                  className="w-full px-4 py-2 bg-purple-50 text-purple-700 rounded-lg hover:bg-purple-100 text-left"
                >
                  📨 Send Reminder
                </button>
              </div>
            </div>
          )}

          {/* Timeline */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Timeline</h2>
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 bg-blue-600 rounded-full mt-2"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">Promise Created</p>
                  <p className="text-xs text-gray-600">{formatDateTime(promise.created_at)}</p>
                  <p className="text-xs text-gray-500">by {promise.created_by}</p>
                </div>
              </div>
              {promise.fulfilled_date && (
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-green-600 rounded-full mt-2"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">Fulfilled</p>
                    <p className="text-xs text-gray-600">{formatDateTime(promise.fulfilled_date)}</p>
                    <p className="text-xs text-green-600">{formatCurrency(promise.fulfilled_amount)}</p>
                  </div>
                </div>
              )}
              {promise.broken_date && (
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-red-600 rounded-full mt-2"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">Promise Broken</p>
                    <p className="text-xs text-gray-600">{formatDateTime(promise.broken_date)}</p>
                    {promise.broken_reason && (
                      <p className="text-xs text-red-600">{promise.broken_reason}</p>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Statistics */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Promise Stats</h2>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Days Until Due</span>
                <span className={`font-semibold ${isPastDue ? 'text-red-600' : isDueSoon ? 'text-yellow-600' : 'text-green-600'}`}>
                  {isPastDue ? `${Math.abs(daysUntilDue)} days overdue` : `${daysUntilDue} days`}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Fulfillment %</span>
                <span className="font-semibold text-gray-900">
                  {((promise.fulfilled_amount / promise.promised_amount) * 100).toFixed(0)}%
                </span>
              </div>
              {promise.reminder_sent && (
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Reminder Sent</span>
                  <span className="text-green-600">✓</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
