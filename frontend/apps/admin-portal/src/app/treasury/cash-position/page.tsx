'use client';

import { useRouter } from 'next/navigation';

export default function CashPositionPage() {
  const router = useRouter();

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Cash Position Monitoring</h1>
        <p className="text-sm text-gray-600 mt-1">Real-time cash position across all bank accounts</p>
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
              <p>The Cash Position Monitoring feature is currently under development.</p>
              <p className="mt-2">This module will include:</p>
              <ul className="list-disc list-inside mt-2 space-y-1">
                <li>Real-time cash position dashboard</li>
                <li>Multi-bank account consolidation</li>
                <li>Intraday position tracking</li>
                <li>Currency-wise breakup</li>
                <li>Historical position trends</li>
                <li>Automated position calculations</li>
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
            <li>• Real-time position updates</li>
            <li>• Multi-currency support</li>
            <li>• Position forecasting</li>
            <li>• Alert configuration</li>
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
    </div>
  );
}
