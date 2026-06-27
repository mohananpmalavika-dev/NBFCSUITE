'use client';

import { useCIFStore } from '@/lib/cif-store';
import { cifApi } from '@/lib/cif-api';
import { useState } from 'react';

interface StageEmploymentProps {
  onNext: () => void;
}

export default function StageEmployment({ onNext }: StageEmploymentProps) {
  const { customerId, employment, updateEmployment, setLoading, setError, markStageComplete } =
    useCIFStore();
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!customerId || !employment.type) {
      setError('Please select employment type');
      return;
    }

    setLoading(true);
    try {
      await cifApi.addEmployment(customerId, {
        employment_type: employment.type,
        employer_name: employment.employer,
        designation: employment.designation,
        salary: employment.salary,
      });

      markStageComplete(8);
      setSubmitted(true);
      setTimeout(onNext, 1000);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (submitted) {
    return (
      <div className="text-center py-12">
        <div className="text-5xl mb-4">✅</div>
        <h2 className="text-2xl font-bold text-slate-900">Employment Saved!</h2>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Stage 8: Employment Details</h2>
        <p className="text-slate-600">Provide employment and income information.</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Employment Type *
          </label>
          <select
            required
            value={employment.type || ''}
            onChange={(e) => updateEmployment({ type: e.target.value })}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg"
          >
            <option value="">Select...</option>
            <option value="employed">Employed</option>
            <option value="self_employed">Self-Employed</option>
            <option value="business">Business Owner</option>
            <option value="retired">Retired</option>
            <option value="student">Student</option>
          </select>
        </div>

        {employment.type === 'employed' && (
          <>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Employer Name
              </label>
              <input
                type="text"
                value={employment.employer || ''}
                onChange={(e) => updateEmployment({ employer: e.target.value })}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg"
                placeholder="Company Name"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Designation
              </label>
              <input
                type="text"
                value={employment.designation || ''}
                onChange={(e) => updateEmployment({ designation: e.target.value })}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg"
                placeholder="Job Title"
              />
            </div>
          </>
        )}

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Monthly Salary (₹)
          </label>
          <input
            type="number"
            value={employment.salary || ''}
            onChange={(e) => updateEmployment({ salary: parseFloat(e.target.value) })}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg"
            placeholder="50000"
          />
        </div>

        <button
          type="submit"
          className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold"
        >
          💼 Save Employment Details
        </button>
      </form>
    </div>
  );
}
