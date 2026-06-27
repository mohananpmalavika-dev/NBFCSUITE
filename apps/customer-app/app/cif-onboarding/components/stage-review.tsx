'use client';

import { useCIFStore } from '@/lib/cif-store';
import { useState } from 'react';

interface StageReviewProps {
  onNext: () => void;
}

export default function StageReview({ onNext }: StageReviewProps) {
  const {
    prospectData,
    basicDetails,
    address,
    contact,
    employment,
    financial,
    identityDocuments,
    documents,
    behavior,
    markStageComplete,
    customerId,
    setCifId,
  } = useCIFStore();

  const [submitted, setSubmitted] = useState(false);

  const handleGenerateCIF = async () => {
    // Simulate CIF generation
    const cifId = `CIF${String(Math.floor(Math.random() * 10000000000)).padStart(10, '0')}`;
    setCifId(cifId);
    markStageComplete(17);
    setSubmitted(true);
    setTimeout(onNext, 1500);
  };

  if (submitted) {
    return (
      <div className="text-center py-12 space-y-4">
        <div className="text-5xl mb-4">🎉</div>
        <h2 className="text-2xl font-bold text-slate-900">CIF Generated Successfully!</h2>
        <p className="text-slate-600">Your unique customer ID is ready.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Stage 17: CIF Generation & Review</h2>
        <p className="text-slate-600">
          Review all entered information before generating your permanent CIF ID.
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white border border-slate-200 rounded-lg p-4">
          <h3 className="font-bold text-slate-900 mb-3">👤 Personal Details</h3>
          <div className="space-y-2 text-sm">
            <p>
              <span className="text-slate-600">Name:</span>{' '}
              <span className="font-semibold">{prospectData.firstName} {prospectData.lastName}</span>
            </p>
            <p>
              <span className="text-slate-600">Phone:</span>{' '}
              <span className="font-semibold">{prospectData.phone}</span>
            </p>
            <p>
              <span className="text-slate-600">Email:</span>{' '}
              <span className="font-semibold">{prospectData.email}</span>
            </p>
            <p>
              <span className="text-slate-600">DOB:</span>{' '}
              <span className="font-semibold">{basicDetails.dateOfBirth}</span>
            </p>
            <p>
              <span className="text-slate-600">Gender:</span>{' '}
              <span className="font-semibold">{basicDetails.gender}</span>
            </p>
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-lg p-4">
          <h3 className="font-bold text-slate-900 mb-3">📍 Address & Contact</h3>
          <div className="space-y-2 text-sm">
            <p>
              <span className="text-slate-600">Address:</span>{' '}
              <span className="font-semibold">{address.street}, {address.city}</span>
            </p>
            <p>
              <span className="text-slate-600">Postal Code:</span>{' '}
              <span className="font-semibold">{address.postalCode}</span>
            </p>
            <p>
              <span className="text-slate-600">Phone:</span>{' '}
              <span className="font-semibold">{contact.phone}</span>
            </p>
            <p>
              <span className="text-slate-600">Language:</span>{' '}
              <span className="font-semibold">{contact.preferredLanguage}</span>
            </p>
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-lg p-4">
          <h3 className="font-bold text-slate-900 mb-3">💼 Employment & Financial</h3>
          <div className="space-y-2 text-sm">
            <p>
              <span className="text-slate-600">Employment Type:</span>{' '}
              <span className="font-semibold">{employment.type}</span>
            </p>
            <p>
              <span className="text-slate-600">Monthly Income:</span>{' '}
              <span className="font-semibold">₹{financial.monthlyIncome?.toLocaleString('en-IN')}</span>
            </p>
            <p>
              <span className="text-slate-600">Net Worth:</span>{' '}
              <span className="font-semibold">
                ₹{((financial.assets || 0) - (financial.liabilities || 0)).toLocaleString('en-IN')}
              </span>
            </p>
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-lg p-4">
          <h3 className="font-bold text-slate-900 mb-3">🧠 FinDNA Profile</h3>
          <div className="space-y-2 text-sm">
            <p>
              <span className="text-slate-600">Risk Appetite:</span>{' '}
              <span className="font-semibold">{behavior.riskAppetite}</span>
            </p>
            <p>
              <span className="text-slate-600">Spending Pattern:</span>{' '}
              <span className="font-semibold">{behavior.spendingPattern}</span>
            </p>
            <p>
              <span className="text-slate-600">FinDNA Score:</span>{' '}
              <span className="font-semibold text-purple-600">{behavior.finDna}</span>
            </p>
          </div>
        </div>
      </div>

      {/* Documents Summary */}
      <div className="bg-white border border-slate-200 rounded-lg p-4">
        <h3 className="font-bold text-slate-900 mb-3">📋 Documents Uploaded</h3>
        <div className="space-y-2 text-sm">
          <p>
            Identity Documents: <span className="font-semibold">{identityDocuments.length}</span>
          </p>
          <p>
            Supporting Documents: <span className="font-semibold">{documents.length}</span>
          </p>
        </div>
      </div>

      <button
        onClick={handleGenerateCIF}
        className="w-full px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:opacity-90 font-semibold text-lg transition-all"
      >
        🆔 Generate Permanent CIF ID
      </button>

      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
        <h4 className="font-semibold text-amber-900 mb-2">⚠️ Before You Continue</h4>
        <ul className="text-sm text-amber-800 space-y-1">
          <li>✓ All information has been verified</li>
          <li>✓ Compliance checks have passed</li>
          <li>✓ All approvals have been granted</li>
          <li>✓ CIF ID will be permanent and never change</li>
          <li>✓ Used for ALL products across the platform</li>
        </ul>
      </div>
    </div>
  );
}
