'use client';

import { useCIFStore } from '@/lib/cif-store';
import { cifApi } from '@/lib/cif-api';
import { useState } from 'react';

interface StageBusinessProps {
  onNext: () => void;
}

export default function StageBusiness({ onNext }: StageBusinessProps) {
  const { customerId, employment, setLoading, setError, markStageComplete } = useCIFStore();
  const [submitted, setSubmitted] = useState(false);
  const [business, setBusiness] = useState({
    businessName: '',
    businessType: 'proprietorship',
    annualTurnover: '',
    employees: '',
    registrationNumber: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!customerId) {
      setError('No customer selected');
      return;
    }

    // Only submit if self-employed or business owner
    if (employment.type !== 'self-employed' && employment.type !== 'business') {
      markStageComplete(9);
      onNext();
      return;
    }

    setLoading(true);
    try {
      await cifApi.addEmployment(customerId, {
        employment_type: employment.type,
        employer_name: business.businessName,
        designation: business.businessType,
        salary: business.annualTurnover ? parseFloat(business.annualTurnover) : 0,
        experience_years: business.employees ? parseInt(business.employees, 10) : 0,
      });

      markStageComplete(9);
      setSubmitted(true);
      setTimeout(onNext, 1000);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Skip if not self-employed
  if (employment.type !== 'self-employed' && employment.type !== 'business') {
    return (
      <div className="text-center py-12 space-y-4">
        <div className="text-5xl mb-4">✓</div>
        <h2 className="text-2xl font-bold text-slate-900">Stage 9: Business Profile</h2>
        <p className="text-slate-600">Not applicable for this employment type</p>
        <button
          onClick={onNext}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold inline-block"
        >
          Continue →
        </button>
      </div>
    );
  }

  if (submitted) {
    return (
      <div className="text-center py-12">
        <div className="text-5xl mb-4">✅</div>
        <h2 className="text-2xl font-bold text-slate-900">Business Profile Saved!</h2>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Stage 9: Business Profile</h2>
        <p className="text-slate-600">
          Detailed business information for self-employed and business owners.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Business Name
          </label>
          <input
            type="text"
            value={business.businessName}
            onChange={(e) => setBusiness({ ...business, businessName: e.target.value })}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg"
            placeholder="Your business name"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Business Type
          </label>
          <select
            value={business.businessType}
            onChange={(e) => setBusiness({ ...business, businessType: e.target.value })}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg"
          >
            <option value="proprietorship">Proprietorship</option>
            <option value="partnership">Partnership</option>
            <option value="llp">LLP</option>
            <option value="pvt_limited">Private Limited</option>
            <option value="public_limited">Public Limited</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Annual Turnover (₹)
          </label>
          <input
            type="number"
            value={business.annualTurnover}
            onChange={(e) => setBusiness({ ...business, annualTurnover: e.target.value })}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg"
            placeholder="50000000"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Number of Employees
          </label>
          <input
            type="number"
            value={business.employees}
            onChange={(e) => setBusiness({ ...business, employees: e.target.value })}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg"
            placeholder="5"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Registration Number
          </label>
          <input
            type="text"
            value={business.registrationNumber}
            onChange={(e) => setBusiness({ ...business, registrationNumber: e.target.value })}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg"
            placeholder="CIN/GSTIN/PAN"
          />
        </div>

        <button
          type="submit"
          className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold"
        >
          💼 Save Business Profile
        </button>
      </form>
    </div>
  );
}
