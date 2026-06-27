'use client';

import { useState } from 'react';
import { useCIFStore } from '@/lib/cif-store';
import { cifApi } from '@/lib/cif-api';

interface StageBasicDetailsProps {
  onNext: () => void;
}

export default function StageBasicDetails({ onNext }: StageBasicDetailsProps) {
  const {
    customerId,
    prospectData,
    basicDetails,
    updateBasicDetails,
    setLoading,
    setError,
    markStageComplete,
  } = useCIFStore();
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!customerId) {
      setError('No customer selected');
      return;
    }

    if (!basicDetails.dateOfBirth || !basicDetails.gender) {
      setError('Please provide date of birth and gender');
      setLoading(false);
      return;
    }

    setLoading(true);
    try {
      await cifApi.addBasicDetails(customerId, {
        first_name: prospectData.firstName,
        last_name: prospectData.lastName,
        date_of_birth: basicDetails.dateOfBirth,
        gender: basicDetails.gender,
        occupation: basicDetails.occupation,
        marital_status: basicDetails.maritalStatus,
        education_level: basicDetails.education,
        pan: basicDetails.pan,
        aadhar: basicDetails.aadhar,
        nationality: 'India',
        resident_status: 'Resident',
      });

      markStageComplete(3);
      setSubmitted(true);
      setError(null);
      setTimeout(onNext, 1000);
    } catch (err: any) {
      setError(err.message || 'Failed to save details');
    } finally {
      setLoading(false);
    }
  };

  if (submitted) {
    return (
      <div className="text-center space-y-4 py-12">
        <div className="text-5xl mb-4">✅</div>
        <h2 className="text-2xl font-bold text-slate-900">Basic Details Saved!</h2>
        <p className="text-slate-600">Moving to identity verification...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Stage 3: Basic Details</h2>
        <p className="text-slate-600">Enter personal and identification information.</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Date of Birth
            </label>
            <input
              type="date"
              value={basicDetails.dateOfBirth || ''}
              onChange={(e) => updateBasicDetails({ dateOfBirth: e.target.value })}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Gender
            </label>
            <select
              value={basicDetails.gender || ''}
              onChange={(e) => updateBasicDetails({ gender: e.target.value })}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select...</option>
              <option value="M">Male</option>
              <option value="F">Female</option>
              <option value="O">Other</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Occupation
            </label>
            <select
              value={basicDetails.occupation || ''}
              onChange={(e) => updateBasicDetails({ occupation: e.target.value })}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select...</option>
              <option value="employed">Employed</option>
              <option value="self_employed">Self-Employed</option>
              <option value="business">Business Owner</option>
              <option value="retired">Retired</option>
              <option value="student">Student</option>
              <option value="housewife">Housewife</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Marital Status
            </label>
            <select
              value={basicDetails.maritalStatus || ''}
              onChange={(e) => updateBasicDetails({ maritalStatus: e.target.value })}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select...</option>
              <option value="single">Single</option>
              <option value="married">Married</option>
              <option value="divorced">Divorced</option>
              <option value="widowed">Widowed</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Education
            </label>
            <select
              value={basicDetails.education || ''}
              onChange={(e) => updateBasicDetails({ education: e.target.value })}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select...</option>
              <option value="12th">12th Pass</option>
              <option value="graduate">Graduate</option>
              <option value="post_graduate">Post Graduate</option>
              <option value="professional">Professional</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              PAN Number
            </label>
            <input
              type="text"
              value={basicDetails.pan || ''}
              onChange={(e) => updateBasicDetails({ pan: e.target.value.toUpperCase() })}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="AAAPB1234C"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Aadhaar Number
            </label>
            <input
              type="text"
              value={basicDetails.aadhar || ''}
              onChange={(e) => updateBasicDetails({ aadhar: e.target.value })}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="1234 5678 9012"
            />
          </div>
        </div>

        <button
          type="submit"
          className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold transition-colors"
        >
          📝 Save Basic Details
        </button>
      </form>
    </div>
  );
}
