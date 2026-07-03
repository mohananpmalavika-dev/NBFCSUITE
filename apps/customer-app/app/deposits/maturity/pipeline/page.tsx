/**
 * Maturity Pipeline - Upcoming Maturities
 * Track and process maturing deposits
 */

'use client';

import { useState, useEffect } from 'react';
import { Calendar, TrendingUp, RefreshCw, AlertCircle, CheckCircle, Clock, Search } from 'lucide-react';

interface MaturityItem {
  account_id: string;
  account_number: string;
  customer_id: string;
  cif_number: string;
  principal: number;
  maturity_date: string;
  days_to_maturity: number;
  maturity_amount: number;
  auto_renewal: boolean;
  maturity_instruction: string;
  branch_code: string;
}

export default function MaturityPipelinePage() {
  const [pipeline, setPipeline] = useState<MaturityItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('30');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchPipeline();
  }, [filter]);

  const fetchPipeline = async () => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8007/api/v1/maturity/pipeline?days_ahead=${filter}`);
      const data = await response.json();
      setPipeline(data);
    } catch (error) {
      console.error('Error fetching pipeline:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredPipeline = pipeline.filter(item =>
    item.account_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.cif_number.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalAmount = filteredPipeline.reduce((sum, item) => sum + item.maturity_amount, 0);
  const autoRenewCount = filteredPipeline.filter(item => item.auto_renewal).length;

  if (loading) {
    return <LoadingState />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50/30 p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-4xl font-bold text-slate-900">Maturity Pipeline</h1>
            <p className="text-slate-600 mt-2">Track and process upcoming maturities</p>
          </div>
          
          <button
            onClick={fetchPipeline}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <SummaryCard
            label="Total Maturities"
            value={filteredPipeline.length}
            icon={<Calendar className="w-6 h-6 text-blue-600" />}
            color="blue"
          />
          <SummaryCard
            label="Total Amount"
            value={`₹${(totalAmount / 10000000).toFixed(2)} Cr`}
            icon={<TrendingUp className="w-6 h-6 text-green-600" />}
            color="green"
          />
          <SummaryCard
            label="Auto-Renewal"
            value={autoRenewCount}
            subtitle={`${Math.round((autoRenewCount / filteredPipeline.length) * 100)}%`}
            icon={<RefreshCw className="w-6 h-6 text-purple-600" />}
            color="purple"
          />
          <SummaryCard
            label="Pending Action"
            value={filteredPipeline.length - autoRenewCount}
            icon={<AlertCircle className="w-6 h-6 text-orange-600" />}
            color="orange"
          />
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl shadow-lg border border-slate-200 p-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search by account or CIF..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="7">Next 7 Days</option>
              <option value="30">Next 30 Days</option>
              <option value="60">Next 60 Days</option>
              <option value="90">Next 90 Days</option>
            </select>
          </div>
        </div>

        {/* Pipeline Table */}
        <div className="bg-white rounded-xl shadow-lg border border-slate-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-slate-900">Account</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-slate-900">Customer</th>
                  <th className="px-6 py-4 text-right text-sm font-semibold text-slate-900">Principal</th>
                  <th className="px-6 py-4 text-right text-sm font-semibold text-slate-900">Maturity Amount</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-slate-900">Maturity Date</th>
                  <th className="px-6 py-4 text-center text-sm font-semibold text-slate-900">Status</th>
                  <th className="px-6 py-4 text-center text-sm font-semibold text-slate-900">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {filteredPipeline.map((item) => (
                  <MaturityRow key={item.account_id} item={item} />
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

function MaturityRow({ item }: { item: MaturityItem }) {
  const daysColor = 
    item.days_to_maturity <= 7 ? 'text-red-600' :
    item.days_to_maturity <= 30 ? 'text-orange-600' :
    'text-green-600';

  return (
    <tr className="hover:bg-slate-50 transition-colors">
      <td className="px-6 py-4">
        <div>
          <p className="font-semibold text-slate-900">{item.account_number}</p>
          <p className="text-xs text-slate-600">{item.branch_code}</p>
        </div>
      </td>
      <td className="px-6 py-4">
        <p className="text-slate-900">{item.cif_number}</p>
      </td>
      <td className="px-6 py-4 text-right">
        <p className="font-semibold text-slate-900">₹{item.principal.toLocaleString('en-IN')}</p>
      </td>
      <td className="px-6 py-4 text-right">
        <p className="font-semibold text-green-600">₹{item.maturity_amount.toLocaleString('en-IN')}</p>
      </td>
      <td className="px-6 py-4">
        <div>
          <p className="text-slate-900">{new Date(item.maturity_date).toLocaleDateString()}</p>
          <p className={`text-xs font-medium ${daysColor}`}>
            {item.days_to_maturity} days
          </p>
        </div>
      </td>
      <td className="px-6 py-4 text-center">
        {item.auto_renewal ? (
          <span className="inline-flex items-center gap-1 px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
            <RefreshCw className="w-3 h-3" />
            Auto-Renew
          </span>
        ) : (
          <span className="inline-flex items-center gap-1 px-3 py-1 bg-orange-100 text-orange-700 rounded-full text-xs font-medium">
            <Clock className="w-3 h-3" />
            Pending
          </span>
        )}
      </td>
      <td className="px-6 py-4 text-center">
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 transition-colors">
          Process
        </button>
      </td>
    </tr>
  );
}

function SummaryCard({ label, value, subtitle, icon, color }: any) {
  const bgColor = {
    blue: 'bg-blue-50',
    green: 'bg-green-50',
    purple: 'bg-purple-50',
    orange: 'bg-orange-50'
  }[color];

  return (
    <div className="bg-white rounded-xl shadow border border-slate-200 p-6">
      <div className="flex items-start justify-between mb-4">
        <div className={`p-3 ${bgColor} rounded-xl`}>{icon}</div>
      </div>
      <p className="text-slate-600 text-sm mb-1">{label}</p>
      <p className="text-3xl font-bold text-slate-900">{value}</p>
      {subtitle && <p className="text-slate-500 text-sm mt-1">{subtitle}</p>}
    </div>
  );
}

function LoadingState() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50/30 p-8 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-slate-600">Loading maturity pipeline...</p>
      </div>
    </div>
  );
}
