'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { attendanceService } from '@/services/attendance.service';
import { LeavePolicy, LeaveBalance } from '@/types/attendance.types';

export default function ApplyLeavePage() {
  const router = useRouter();
  const [leaveTypes, setLeaveTypes] = useState<LeavePolicy[]>([]);
  const [balances, setBalances] = useState<LeaveBalance[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    leave_policy_id: '',
    start_date: '',
    end_date: '',
    is_half_day: false,
    half_day_type: 'first_half' as 'first_half' | 'second_half',
    reason: '',
    contact_details: '',
    emergency_contact: '',
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load leave types
      const typesResponse = await attendanceService.leave.listLeaveTypes({
        is_active: true,
        page: 1,
        page_size: 100,
      });
      setLeaveTypes(typesResponse.items);

      // Load employee leave balances
      try {
        const balancesResponse = await attendanceService.leave.listBalances({
          page: 1,
          page_size: 100,
        });
        setBalances(balancesResponse.items);
      } catch (err) {
        console.error('Failed to load balances:', err);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load leave data');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.leave_policy_id) {
      alert('Please select a leave type');
      return;
    }

    if (!formData.start_date || !formData.end_date) {
      alert('Please select start and end dates');
      return;
    }

    if (!formData.reason.trim()) {
      alert('Please provide a reason for leave');
      return;
    }

    try {
      setSubmitting(true);
      await attendanceService.leave.createApplication(formData);
      alert('Leave application submitted successfully!');
      router.push('/leave');
    } catch (err: any) {
      alert(err.message || 'Failed to submit leave application');
    } finally {
      setSubmitting(false);
    }
  };

  const getAvailableBalance = (policyId: string) => {
    const balance = balances.find(b => b.leave_policy_id === policyId);
    return balance?.current_balance || 0;
  };

  const calculateDays = () => {
    if (!formData.start_date || !formData.end_date) return 0;

    const start = new Date(formData.start_date);
    const end = new Date(formData.end_date);
    
    if (end < start) return 0;

    const diffTime = Math.abs(end.getTime() - start.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;

    return formData.is_half_day ? 0.5 : diffDays;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-3xl">
      <div className="flex items-center mb-6">
        <button
          onClick={() => router.back()}
          className="mr-4 text-gray-600 hover:text-gray-900"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
        </button>
        <h1 className="text-3xl font-bold text-gray-900">Apply for Leave</h1>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Leave Balance Summary */}
      {balances.length > 0 && (
        <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Your Leave Balance</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {balances.map((balance) => (
              <div key={balance.id} className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                <div className="text-sm text-gray-600 mb-1">
                  {balance.leave_type}
                </div>
                <div className="text-2xl font-bold text-blue-600">
                  {balance.current_balance}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Total: {balance.opening_balance + balance.accrued} | Used: {balance.availed}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Application Form */}
      <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
        <form onSubmit={handleSubmit}>
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Leave Type *
            </label>
            <select
              required
              value={formData.leave_policy_id}
              onChange={(e) => setFormData({ ...formData, leave_policy_id: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select leave type</option>
              {leaveTypes.map((policy) => (
                <option key={policy.id} value={policy.id}>
                  {policy.policy_name} - {policy.policy_code} 
                  (Available: {getAvailableBalance(policy.id)} days)
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Start Date *
              </label>
              <input
                type="date"
                required
                value={formData.start_date}
                onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                min={new Date().toISOString().split('T')[0]}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                End Date *
              </label>
              <input
                type="date"
                required
                value={formData.end_date}
                onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                min={formData.start_date || new Date().toISOString().split('T')[0]}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Half Day Option */}
          <div className="mb-6">
            <label className="flex items-center mb-2">
              <input
                type="checkbox"
                checked={formData.is_half_day}
                onChange={(e) => setFormData({ ...formData, is_half_day: e.target.checked })}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <span className="ml-2 text-sm text-gray-700">Half Day Leave</span>
            </label>

            {formData.is_half_day && (
              <div className="ml-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Half Day Type
                </label>
                <div className="flex gap-4">
                  <label className="flex items-center">
                    <input
                      type="radio"
                      value="first_half"
                      checked={formData.half_day_type === 'first_half'}
                      onChange={(e) => setFormData({ ...formData, half_day_type: e.target.value as 'first_half' | 'second_half' })}
                      className="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                    />
                    <span className="ml-2 text-sm text-gray-700">First Half</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="radio"
                      value="second_half"
                      checked={formData.half_day_type === 'second_half'}
                      onChange={(e) => setFormData({ ...formData, half_day_type: e.target.value as 'first_half' | 'second_half' })}
                      className="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                    />
                    <span className="ml-2 text-sm text-gray-700">Second Half</span>
                  </label>
                </div>
              </div>
            )}
          </div>

          {/* Total Days Calculation */}
          {formData.start_date && formData.end_date && (
            <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">Total Leave Days:</span>
                <span className="text-xl font-bold text-blue-600">{calculateDays()}</span>
              </div>
              {formData.leave_policy_id && (
                <div className="mt-2 text-xs text-gray-600">
                  Available Balance: {getAvailableBalance(formData.leave_policy_id)} days
                </div>
              )}
            </div>
          )}

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Reason for Leave *
            </label>
            <textarea
              required
              value={formData.reason}
              onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Please provide detailed reason for your leave..."
            />
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Contact Details During Leave
            </label>
            <input
              type="text"
              value={formData.contact_details}
              onChange={(e) => setFormData({ ...formData, contact_details: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Phone number or alternate contact"
            />
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Emergency Contact
            </label>
            <input
              type="text"
              value={formData.emergency_contact}
              onChange={(e) => setFormData({ ...formData, emergency_contact: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Emergency contact person and number"
            />
          </div>

          {/* Info Box */}
          <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex items-start">
              <svg className="w-5 h-5 text-yellow-600 mt-0.5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div className="flex-1">
                <h3 className="text-sm font-medium text-yellow-900 mb-1">Important Notes</h3>
                <ul className="text-sm text-yellow-800 list-disc list-inside space-y-1">
                  <li>Leave applications require approval from your reporting manager and HR</li>
                  <li>Apply for leave at least 3 days in advance for planned leaves</li>
                  <li>Emergency leaves should be regularized within 24 hours</li>
                  <li>Check your leave balance before applying</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="flex justify-end gap-3">
            <button
              type="button"
              onClick={() => router.back()}
              className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              disabled={submitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={submitting}
            >
              {submitting ? 'Submitting...' : 'Submit Application'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
