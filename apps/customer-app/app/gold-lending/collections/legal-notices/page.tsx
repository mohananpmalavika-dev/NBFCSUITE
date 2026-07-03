'use client';

import { useState, useEffect } from 'react';
import { goldApi } from '../../goldApi';

export default function LegalNoticesPage() {
  const [notices, setNotices] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ notice_type: '', notice_status: '', skip: 0, limit: 50 });

  useEffect(() => {
    goldApi.getLegalNotices(filters)
      .then(data => setNotices(data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [filters]);

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      'draft': 'bg-gray-100 text-gray-800',
      'approved': 'bg-blue-100 text-blue-800',
      'issued': 'bg-yellow-100 text-yellow-800',
      'delivered': 'bg-green-100 text-green-800',
      'acknowledged': 'bg-teal-100 text-teal-800',
      'responded': 'bg-purple-100 text-purple-800',
      'expired': 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  if (loading) return <div className="flex items-center justify-center min-h-screen"><div className="text-lg">Loading...</div></div>;

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Legal Notices</h1>
          <p className="text-gray-600 mt-2">Manage legal notices and demand letters</p>
        </div>
        <button className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700">Create Notice</button>
      </div>

      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <select
            value={filters.notice_type}
            onChange={(e) => setFilters({ ...filters, notice_type: e.target.value })}
            className="border border-gray-300 rounded-md px-3 py-2"
          >
            <option value="">All Types</option>
            <option value="reminder">Reminder</option>
            <option value="demand">Demand</option>
            <option value="final_demand">Final Demand</option>
            <option value="legal_action">Legal Action</option>
            <option value="arbitration">Arbitration</option>
            <option value="suit_filing">Suit Filing</option>
            <option value="auction_notice">Auction Notice</option>
          </select>
          <select
            value={filters.notice_status}
            onChange={(e) => setFilters({ ...filters, notice_status: e.target.value })}
            className="border border-gray-300 rounded-md px-3 py-2"
          >
            <option value="">All Statuses</option>
            <option value="draft">Draft</option>
            <option value="approved">Approved</option>
            <option value="issued">Issued</option>
            <option value="delivered">Delivered</option>
            <option value="acknowledged">Acknowledged</option>
            <option value="responded">Responded</option>
          </select>
          <button
            onClick={() => setFilters({ notice_type: '', notice_status: '', skip: 0, limit: 50 })}
            className="bg-gray-200 text-gray-800 px-4 py-2 rounded-md hover:bg-gray-300"
          >
            Clear
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
        {[
          { label: 'Total Notices', value: notices.length },
          { label: 'Issued', value: notices.filter(n => n.notice_status === 'issued').length },
          { label: 'Delivered', value: notices.filter(n => n.notice_status === 'delivered').length },
          { label: 'Responded', value: notices.filter(n => n.notice_status === 'responded').length },
          { label: 'Expired', value: notices.filter(n => n.notice_status === 'expired').length },
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
              {['Notice Number', 'Type', 'Date', 'Status', 'Demand Amount', 'Response Deadline', 'Delivery Mode', 'Actions'].map(header => (
                <th key={header} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{header}</th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {notices.map(notice => (
              <tr key={notice.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600">{notice.notice_number}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm capitalize">{notice.notice_type.replace('_', ' ')}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">{new Date(notice.notice_date).toLocaleDateString()}</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(notice.notice_status)}`}>
                    {notice.notice_status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">₹{Number(notice.demand_amount).toLocaleString('en-IN')}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">{new Date(notice.response_deadline).toLocaleDateString()}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm capitalize">{notice.delivery_mode.replace('_', ' ')}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button className="text-blue-600 hover:text-blue-900 mr-3">View</button>
                  {notice.notice_status === 'draft' && (
                    <button className="text-green-600 hover:text-green-900">Approve</button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {notices.length === 0 && <div className="text-center py-12 text-gray-500">No legal notices found</div>}
      </div>
    </div>
  );
}
