'use client';

import { useCIFStore } from '@/lib/cif-store';
import { cifApi } from '@/lib/cif-api';
import { useState } from 'react';

interface StageComplianceProps {
  onNext: () => void;
}

export default function StageCompliance({ onNext }: StageComplianceProps) {
  const { customerId, compliance, updateCompliance, setLoading, setError, markStageComplete } =
    useCIFStore();
  const [submitted, setSubmitted] = useState(false);
  const [checks] = useState([
    'PAN Verification',
    'Aadhar Verification',
    'CKYC',
    'Video KYC',
    'AML Check',
    'PEP Screening',
    'Sanction List Check',
    'Negative Media',
    'Fraud Detection',
    'Watchlist Check',
  ]);

  const handleRunChecks = async () => {
    if (!customerId) {
      setError('No customer selected');
      return;
    }

    setLoading(true);
    try {
      // Run multiple compliance checks
      await cifApi.initiateCompliance(customerId);

      updateCompliance({ status: 'in_progress' });
      
      // Simulate checks completing
      setTimeout(async () => {
        updateCompliance({
          panVerified: true,
          aadharVerified: true,
          amlPassed: true,
          status: 'completed',
        });

        markStageComplete(12);
        setSubmitted(true);
        setTimeout(onNext, 1500);
      }, 2000);
    } catch (err: any) {
      setError(err.message);
      setLoading(false);
    }
  };

  if (submitted) {
    return (
      <div className="text-center py-12 space-y-4">
        <div className="text-5xl mb-4">✅</div>
        <h2 className="text-2xl font-bold text-slate-900">All Compliance Checks Passed!</h2>
        <p className="text-slate-600">Customer cleared for further processing.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Stage 12: Compliance Verification</h2>
        <p className="text-slate-600">
          Automated compliance and anti-fraud checks. This ensures your platform stays compliant.
        </p>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-3">
        <h3 className="font-semibold text-blue-900">Compliance Checks to Run:</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {checks.map((check, idx) => (
            <div key={idx} className="flex items-center gap-2">
              <div className="w-5 h-5 rounded-full bg-blue-200 flex items-center justify-center">
                <span className="text-xs">✓</span>
              </div>
              <span className="text-sm text-blue-900">{check}</span>
            </div>
          ))}
        </div>
      </div>

      {compliance.status === 'in_progress' ? (
        <div className="text-center py-8">
          <div className="inline-block animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full mb-4"></div>
          <p className="text-slate-600">Running compliance checks...</p>
        </div>
      ) : (
        <button
          onClick={handleRunChecks}
          className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold"
        >
          ✅ Run Compliance Checks
        </button>
      )}

      {compliance.status === 'completed' && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 space-y-2">
          <h3 className="font-semibold text-green-900">✓ Verification Results</h3>
          <div className="text-sm text-green-800 space-y-1">
            <p>✓ PAN Verified: {compliance.panVerified ? 'Yes' : 'No'}</p>
            <p>✓ Aadhar Verified: {compliance.aadharVerified ? 'Yes' : 'No'}</p>
            <p>✓ AML Check: {compliance.amlPassed ? 'Passed' : 'Failed'}</p>
          </div>
        </div>
      )}

      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
        <h4 className="font-semibold text-amber-900 mb-2">⚠️ Compliance Notes</h4>
        <ul className="text-sm text-amber-800 space-y-1">
          <li>• All checks are performed against RBI/FEMA guidelines</li>
          <li>• Failed checks may require additional documentation</li>
          <li>• Checks are re-run periodically for ongoing monitoring</li>
        </ul>
      </div>
    </div>
  );
}
