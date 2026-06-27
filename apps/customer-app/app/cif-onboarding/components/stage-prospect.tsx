'use client';

import { useState } from 'react';
import { useCIFStore } from '@/lib/cif-store';
import { cifApi } from '@/lib/cif-api';

interface StageProspectProps {
  onNext: () => void;
}

export default function StageProspect({ onNext }: StageProspectProps) {
  const {
    prospectData,
    updateProspectData,
    setProspectId,
    setCustomerId,
    setLoading,
    setError,
  } = useCIFStore();
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prospectData.firstName || !prospectData.lastName || !prospectData.phone || !prospectData.email) {
      setError('Please fill all required fields');
      return;
    }

    setLoading(true);
    try {
      const response = await cifApi.createProspect({
        first_name: prospectData.firstName,
        last_name: prospectData.lastName,
        phone: prospectData.phone,
        email: prospectData.email,
        source: prospectData.source || 'direct',
      });

      setProspectId(response.prospect_id);
      const customerResponse = await cifApi.convertProspectToCustomer(response.prospect_id);
      setCustomerId(customerResponse.customer_id);
      setSubmitted(true);
      setError(null);
      setTimeout(onNext, 1500);
    } catch (err: any) {
      setError(err.message || 'Failed to create prospect');
    } finally {
      setLoading(false);
    }
  };

  if (submitted) {
    return (
      <div className="text-center space-y-4 py-12">
        <div className="text-5xl mb-4">✅</div>
        <h2 className="text-2xl font-bold text-slate-900">Prospect Created Successfully!</h2>
        <p className="text-slate-600">
          Moving to next stage...
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Stage 2: Create Prospect</h2>
        <p className="text-slate-600">
          Create a temporary prospect record for this new customer. This will be converted to a permanent CIF after all verifications.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              First Name *
            </label>
            <input
              type="text"
              required
              value={prospectData.firstName}
              onChange={(e) => updateProspectData({ firstName: e.target.value })}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="John"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Last Name *
            </label>
            <input
              type="text"
              required
              value={prospectData.lastName}
              onChange={(e) => updateProspectData({ lastName: e.target.value })}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Doe"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Mobile Number *
            </label>
            <input
              type="tel"
              required
              value={prospectData.phone}
              onChange={(e) => updateProspectData({ phone: e.target.value })}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="9876543210"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Email Address *
            </label>
            <input
              type="email"
              required
              value={prospectData.email}
              onChange={(e) => updateProspectData({ email: e.target.value })}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="john@example.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Product Interest
            </label>
            <select
              value={prospectData.source || ''}
              onChange={(e) => updateProspectData({ source: e.target.value })}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select...</option>
              <option value="gold_loan">Gold Loan</option>
              <option value="savings_account">Savings Account</option>
              <option value="deposit">Fixed Deposit</option>
              <option value="forex">Forex</option>
              <option value="personal_loan">Personal Loan</option>
              <option value="direct">Walk-in</option>
            </select>
          </div>
        </div>

        <button
          type="submit"
          className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold transition-colors"
        >
          💼 Create Prospect
        </button>
      </form>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-semibold text-blue-900 mb-2">📌 Prospect Status</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Prospect created with temporary ID</li>
          <li>• Will be converted to permanent CIF after verification</li>
          <li>• Status: Lead → Prospect → Verified → Active</li>
        </ul>
      </div>
    </div>
  );
}
