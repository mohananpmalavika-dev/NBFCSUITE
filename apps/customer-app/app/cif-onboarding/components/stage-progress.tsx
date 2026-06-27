'use client';

import Link from 'next/link';
import { useCIFStore } from '@/lib/cif-store';

export default function StageProgress() {
  const { cifId, behavior, financial } = useCIFStore();

  return (
    <div className="space-y-6">
      <div className="text-center space-y-4 py-8">
        <div className="text-6xl mb-4">🎉</div>
        <h2 className="text-3xl font-bold text-slate-900">Welcome to NBFCSUITE!</h2>
        <p className="text-lg text-slate-600">Your Customer Information File is now active.</p>
      </div>

      {/* CIF ID Display */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg p-8 text-center shadow-lg">
        <p className="text-sm font-medium opacity-90 mb-2">YOUR PERMANENT CIF ID</p>
        <p className="text-4xl font-bold mb-1">{cifId}</p>
        <p className="text-sm opacity-90">This ID is unique and permanent for your entire banking journey with us</p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
          <div className="text-4xl mb-2">✅</div>
          <p className="text-sm text-slate-600 mb-1">Onboarding Status</p>
          <p className="font-bold text-green-900">Complete</p>
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
          <div className="text-4xl mb-2">📊</div>
          <p className="text-sm text-slate-600 mb-1">FinDNA Score</p>
          <p className="font-bold text-blue-900">{behavior.finDna}</p>
        </div>

        <div className="bg-purple-50 border border-purple-200 rounded-lg p-6 text-center">
          <div className="text-4xl mb-2">💰</div>
          <p className="text-sm text-slate-600 mb-1">Monthly Income</p>
          <p className="font-bold text-purple-900">
            ₹{financial.monthlyIncome?.toLocaleString('en-IN')}
          </p>
        </div>
      </div>

      {/* Completion Summary */}
      <div className="bg-white border border-slate-200 rounded-lg p-6 space-y-4">
        <h3 className="font-bold text-slate-900">📋 Onboarding Summary</h3>
        <div className="space-y-2">
          <div className="flex items-center justify-between p-3 bg-slate-50 rounded">
            <span className="text-slate-700">✓ All 18 Stages Completed</span>
            <span className="text-lg">18/18</span>
          </div>
          <div className="flex items-center justify-between p-3 bg-slate-50 rounded">
            <span className="text-slate-700">✓ All Compliance Checks Passed</span>
            <span className="text-lg">11/11</span>
          </div>
          <div className="flex items-center justify-between p-3 bg-slate-50 rounded">
            <span className="text-slate-700">✓ Multi-Level Approvals Granted</span>
            <span className="text-lg">4/4</span>
          </div>
          <div className="flex items-center justify-between p-3 bg-slate-50 rounded">
            <span className="text-slate-700">✓ Behavioral Profile Generated</span>
            <span className="text-lg">✓</span>
          </div>
        </div>
      </div>

      {/* Next Steps */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 space-y-4">
        <h3 className="font-bold text-blue-900">🚀 Next Steps</h3>
        <div className="space-y-3">
          <p className="text-sm text-blue-800">
            Your CIF is now active! You can proceed with any product:
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <Link
              href="/loans/new"
              className="block px-4 py-2 bg-blue-600 text-white text-center rounded hover:bg-blue-700 font-semibold text-sm"
            >
              🏦 Apply for Gold Loan
            </Link>
            <Link
              href="/deposits/new"
              className="block px-4 py-2 bg-blue-600 text-white text-center rounded hover:bg-blue-700 font-semibold text-sm"
            >
              💰 Open Fixed Deposit
            </Link>
            <Link
              href="/profile"
              className="block px-4 py-2 bg-blue-600 text-white text-center rounded hover:bg-blue-700 font-semibold text-sm"
            >
              👤 View Customer 360
            </Link>
            <Link
              href="/"
              className="block px-4 py-2 bg-blue-600 text-white text-center rounded hover:bg-blue-700 font-semibold text-sm"
            >
              🏠 Back to Home
            </Link>
          </div>
        </div>
      </div>

      {/* Features Available */}
      <div className="bg-white border border-slate-200 rounded-lg p-6 space-y-4">
        <h3 className="font-bold text-slate-900">✨ Now Available</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div className="flex gap-3">
            <span className="text-lg">📊</span>
            <div>
              <p className="font-semibold text-slate-900">Customer 360</p>
              <p className="text-slate-600">View complete customer profile</p>
            </div>
          </div>
          <div className="flex gap-3">
            <span className="text-lg">💳</span>
            <div>
              <p className="font-semibold text-slate-900">Product Application</p>
              <p className="text-slate-600">Apply for any product instantly</p>
            </div>
          </div>
          <div className="flex gap-3">
            <span className="text-lg">📱</span>
            <div>
              <p className="font-semibold text-slate-900">Mobile & Web</p>
              <p className="text-slate-600">Access from any device</p>
            </div>
          </div>
          <div className="flex gap-3">
            <span className="text-lg">🔐</span>
            <div>
              <p className="font-semibold text-slate-900">Secure Access</p>
              <p className="text-slate-600">Encrypted and authenticated</p>
            </div>
          </div>
        </div>
      </div>

      {/* Footer Message */}
      <div className="bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 rounded-lg p-6 text-center">
        <p className="text-slate-700 font-medium mb-2">Welcome to NBFCSUITE Family! 👋</p>
        <p className="text-sm text-slate-600">
          Your CIF ID {cifId} is now the single source of truth for your banking relationship.
          All products will use this ID to serve you better.
        </p>
      </div>
    </div>
  );
}
