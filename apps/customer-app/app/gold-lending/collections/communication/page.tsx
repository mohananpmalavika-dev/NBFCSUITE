'use client';

import { useState, useEffect } from 'react';
import { goldApi } from '../../goldApi';

export default function CommunicationLogsPage() {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ communication_type: '', direction: '', skip: 0, limit: 50 });

  useEffect(() => {
    goldApi.getCommunicationLogs(filters)
      .then(data => setLogs(data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [filters]);

  if (loading) return <div className="flex items-center justify-center min-h-screen"><div className="text-lg">Loading...</div></div>;

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Communication Logs</h1>
          <p className="text-gray-600 mt-2">Track all customer communications and interactions</p>
        </div>
        <button className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700">Log Communication</button>
      </div>

      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <select
            value={filters.communication_type}
            onChange={(e) => setFilters({ ...filters, communication_type: e.target.value })}
            className="border border-gray-300 rounded-md px-3 py-2"
          >
            <option value="">All Types</option>
            <option value="call">Call</option>
            <option value="sms">SMS</option>
            <option value="email">Email</option>
            <option value="whatsapp">WhatsApp</option>
            <option value="letter">Letter</option>
            <option value="telegram">Telegram</option>
          </select>
          <select
            value={filters.direction}
            onChange={(e) => setFilters({ ...filters, direction: e.target.value })}
            className="border border-gray-300 rounded-md px-3 py-2"
          >
            <option value="">All Directions</option>
            <option value="inbound">Inbound</option>
            <option value="outbound">Outbound</option>
          </select>
          <button
            onClick={() => setFilters({ communication_type: '', direction: '', skip: 0, limit: 50 })}
            className="bg-gray-200 text-gray-800 px-4 py-2 rounded-md hover:bg-gray-300"
          >
            Clear
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
        {[
          { label: 'Total Logs', value: logs.length },
          { label: 'Calls', value: logs.filter(l => l.communication_type === 'call').length },
          { label: 'SMS', value: logs.filter(l => l.communication_type === 'sms').length },
          { label: 'Emails', value: logs.filter(l => l.communication_type === 'email').length },
          { label: 'Response Rate', value: `${logs.length > 0 ? Math.round(logs.filter(l => l.response_received).length / logs.length * 100) : 0}%` },
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
              {['Date & Time', 'Type', 'Direction', 'From/To', 'Subject', 'Status', 'Response', 'Cost', 'Actions'].map(header => (
                <th key={header} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{header}</th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {logs.map(log => (
              <tr key={log.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  {new Date(log.communication_date).toLocaleString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800 uppercase">
                    {log.communication_type}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${log.direction === 'inbound' ? 'bg-green-100 text-green-800' : 'bg-purple-100 text-purple-800'}`}>
                    {log.direction}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm">
                  <div>{log.direction === 'inbound' ? log.from_party : log.to_party}</div>
                  <div className="text-gray-500 text-xs">{log.contact_number || log.email_address}</div>
                </td>
                <td className="px-6 py-4 text-sm max-w-xs truncate">{log.subject || '-'}</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${log.communication_status === 'delivered' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                    {log.communication_status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${log.response_received ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                    {log.response_received ? 'Yes' : 'No'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  {log.cost ? `₹${Number(log.cost).toFixed(2)}` : '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button className="text-blue-600 hover:text-blue-900">View</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {logs.length === 0 && <div className="text-center py-12 text-gray-500">No communication logs found</div>}
      </div>
    </div>
  );
}
