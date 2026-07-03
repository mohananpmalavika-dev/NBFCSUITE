'use client';

import { useState, useEffect } from 'react';
import { goldApi } from '../../goldApi';

export default function PaymentPromisesPage() {
  const [promises, setPromises] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ promise_status: '', skip: 0, limit: 50 });

  useEffect(() => {
    goldApi.getPaymentPromises(filters)
      .then(data => setPromises(data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [filters]);

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      'active': 'bg-blue-100 text-blue-800',
      'kept': 'bg-green-100 text-green-800',
      'broken': 'bg-red-100 text-red-800',
      'partial': 'bg-yellow-100 text-yellow-800',
      'cancelled': 'bg-gray-100 text-gray-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  if (loading) return <div className="flex items-center justify-center min-h-screen"><div className="text-lg">Loading...</div></div>;

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Payment Promises</h1>
        <p className="text-gray-600 mt-2">Track customer payment commitments and follow-ups</p>
      </div>

      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <select
          value={filters.promise_status}
          onChange={(e) => setFilters({ ...filters, promise_status: e.target.value })}
          className="border border-gray-300 rounded-md px-3 py-2"
        >
          <option value="">All Statuses</option>
          <option value="active">Active</option>
          <option value="kept">Kept</option>
          <option value="broken">Broken</option>
          <option value="partial">Partial</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        {[
          { label: 'Total Promises', value: promises.length },
          { label: 'Active', value: promises.filter(p => p.promise_status === 'active').length },
          { label: 'Kept', value: promises.filter(p => p.promise_status === 'kept').length },
          { label: 'Broken', value: promises.filter(p => p.promise_status === 'broken').length },
        ].map(stat => (
          <div key={stat.label} className="bg-white p-4 rounded-lg shadow">
            <div className="text-sm text-gray-600">{stat.label}</div>
            <div className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</div>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {['Promise Number', 'Promise Date', 'Payment Date', 'Promised Amount', 'Received Amount', 'Status', 'Fulfillment', 'Actions'].map(header => (
                <th key={header} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{header}</th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {promises.map(promise => (
              <tr key={promise.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600">{promise.promise_number}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">{new Date(promise.promise_date).toLocaleDateString()}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">{new Date(promise.promised_payment_date).toLocaleDateString()}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">₹{Number(promise.promised_amount).toLocaleString('en-IN')}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">₹{Number(promise.amount_received).toLocaleString('en-IN')}</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(promise.promise_status)}`}>
                    {promise.promise_status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">{promise.fulfillment_percentage ? `${promise.fulfillment_percentage}%` : '-'}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button className="text-blue-600 hover:text-blue-900">View</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {promises.length === 0 && <div className="text-center py-12 text-gray-500">No payment promises found</div>}
      </div>
    </div>
  );
}
