'use client';

import { useRouter } from 'next/navigation';

export default function FundTransfersPage() {
  const router = useRouter();

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Fund Transfer Management</h1>
        <p className="text-sm text-gray-600 mt-1">Inter-bank and intra-bank fund transfers</p>
      </div>

      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <svg className="h-6 w-6 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-yellow-800">Coming Soon</h3>
            <div className="mt-2 text-sm text-yellow-700">
              <p>The Fund Transfer Management feature is currently under development.</p>
              <p className="mt-2">This module will include:</p>
              <ul className="list-disc list-inside mt-2 space-y-1">
                <li>Inter-bank fund transfers (NEFT/RTGS/IMPS)</li>
                <li>Intra-bank account transfers</li>
                <li>Bulk transfer processing</li>
                <li>Transfer templates and scheduling</li>
                <li>Multi-level approval workflows</li>
                <li>Real-time status tracking</li>
                <li>Transfer history and audit logs</li>
                <li>Beneficiary management</li>
              </ul>
            </div>
            <div className="mt-4">
              <button
                onClick={() => router.push('/treasury/dashboard')}
                className="text-sm font-medium text-yellow-800 hover:text-yellow-900"
              >
                Back to Treasury Dashboard →
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-medium text-gray-900 mb-2">Planned Features</h3>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>• NEFT/RTGS/IMPS integration</li>
            <li>• Bulk upload (Excel)</li>
            <li>• Scheduled transfers</li>
            <li>• Maker-checker approval</li>
            <li>• Transfer limits</li>
            <li>• SMS/Email notifications</li>
          </ul>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-medium text-gray-900 mb-2">Implementation Status</h3>
          <div className="text-sm text-gray-600">
            <p className="mb-2">Week 1: Complete</p>
            <p className="mb-2">Week 2: In Progress</p>
            <p className="text-gray-400">Week 3: Pending</p>
          </div>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-medium text-gray-900 mb-2">Expected Timeline</h3>
          <p className="text-sm text-gray-600">Q1 2027</p>
          <p className="text-xs text-gray-500 mt-1">Estimated completion date</p>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mt-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Available Now</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            onClick={() => router.push('/treasury/bank-accounts')}
            className="bg-white border border-gray-200 rounded-lg p-4 text-left hover:border-blue-300 hover:shadow-sm transition-all"
          >
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-medium text-gray-900">Bank Accounts</h3>
                <p className="text-xs text-gray-600 mt-1">Manage treasury bank accounts</p>
              </div>
              <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </button>
          <button
            onClick={() => router.push('/treasury/dashboard')}
            className="bg-white border border-gray-200 rounded-lg p-4 text-left hover:border-blue-300 hover:shadow-sm transition-all"
          >
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-medium text-gray-900">Treasury Dashboard</h3>
                <p className="text-xs text-gray-600 mt-1">View treasury overview</p>
              </div>
              <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
}
