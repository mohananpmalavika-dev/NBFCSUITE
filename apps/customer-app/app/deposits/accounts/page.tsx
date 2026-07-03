/**
 * Deposit Accounts - List & Search
 * Browse and manage all deposit accounts
 */

'use client';

import { useState, useEffect } from 'react';
import { Search, Filter, Download, PiggyBank, Clock, Eye, MoreVertical } from 'lucide-react';
import Link from 'next/link';

interface DepositAccount {
  id: string;
  account_number: string;
  customer_id: string;
  cif_number: string;
  deposit_type: string;
  principal_amount: number;
  interest_rate: number;
  open_date: string;
  maturity_date: string;
  status: string;
  maturity_amount?: number;
}

export default function AccountsPage() {
  const [accounts, setAccounts] = useState<DepositAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [typeFilter, setTypeFilter] = useState('ALL');

  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    try {
      const response = await fetch('http://localhost:8007/api/v1/accounts/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status: statusFilter !== 'ALL' ? statusFilter : null,
          page: 1,
          page_size: 100
        })
      });
      const data = await response.json();
      setAccounts(data);
    } catch (error) {
      console.error('Error fetching accounts:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredAccounts = accounts.filter(acc => {
    const matchesSearch = 
      acc.account_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      acc.cif_number.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === 'ALL' || acc.status === statusFilter;
    const matchesType = typeFilter === 'ALL' || acc.deposit_type === typeFilter;
    
    return matchesSearch && matchesStatus && matchesType;
  });

  const totalPrincipal = filteredAccounts.reduce((sum, acc) => sum + acc.principal_amount, 0);
  const activeCount = filteredAccounts.filter(acc => acc.status === 'ACTIVE').length;

  if (loading) {
    return <LoadingState />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50/30 p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-4xl font-bold text-slate-900">Deposit Accounts</h1>
            <p className="text-slate-600 mt-2">Manage and track all deposit accounts</p>
          </div>
          
          <div className="flex gap-3">
            <button className="px-6 py-3 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors flex items-center gap-2">
              <Download className="w-4 h-4" />
              Export
            </button>
            <Link href="/deposits/products">
              <button className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                Open New Account
              </button>
            </Link>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <SummaryCard
            label="Total Accounts"
            value={filteredAccounts.length}
            icon={<PiggyBank className="w-6 h-6 text-blue-600" />}
          />
          <SummaryCard
            label="Active Accounts"
            value={activeCount}
            icon={<Clock className="w-6 h-6 text-green-600" />}
          />
          <SummaryCard
            label="Total Principal"
            value={`₹${(totalPrincipal / 10000000).toFixed(2)} Cr`}
            icon={<PiggyBank className="w-6 h-6 text-purple-600" />}
          />
          <SummaryCard
            label="Avg. Rate"
            value={`${(filteredAccounts.reduce((sum, acc) => sum + acc.interest_rate, 0) / filteredAccounts.length || 0).toFixed(2)}%`}
            icon={<PiggyBank className="w-6 h-6 text-orange-600" />}
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
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="ALL">All Types</option>
              <option value="FIXED_DEPOSIT">Fixed Deposit</option>
              <option value="RECURRING_DEPOSIT">Recurring Deposit</option>
            </select>
            
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                fetchAccounts();
              }}
              className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="ALL">All Status</option>
              <option value="ACTIVE">Active</option>
              <option value="MATURED">Matured</option>
              <option value="PENDING_APPROVAL">Pending</option>
              <option value="CLOSED">Closed</option>
            </select>
          </div>
        </div>

        {/* Accounts Table */}
        <div className="bg-white rounded-xl shadow-lg border border-slate-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-slate-900">Account</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-slate-900">Customer</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-slate-900">Type</th>
                  <th className="px-6 py-4 text-right text-sm font-semibold text-slate-900">Principal</th>
                  <th className="px-6 py-4 text-center text-sm font-semibold text-slate-900">Rate</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-slate-900">Maturity</th>
                  <th className="px-6 py-4 text-center text-sm font-semibold text-slate-900">Status</th>
                  <th className="px-6 py-4 text-center text-sm font-semibold text-slate-900">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {filteredAccounts.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="px-6 py-12 text-center text-slate-600">
                      No accounts found
                    </td>
                  </tr>
                ) : (
                  filteredAccounts.map((account) => (
                    <AccountRow key={account.id} account={account} />
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

function AccountRow({ account }: { account: DepositAccount }) {
  const statusColors = {
    ACTIVE: 'bg-green-100 text-green-700',
    PENDING_APPROVAL: 'bg-yellow-100 text-yellow-700',
    MATURED: 'bg-blue-100 text-blue-700',
    CLOSED: 'bg-slate-100 text-slate-700',
    PREMATURELY_CLOSED: 'bg-red-100 text-red-700'
  };

  const typeIcons = {
    FIXED_DEPOSIT: <PiggyBank className="w-4 h-4" />,
    RECURRING_DEPOSIT: <Clock className="w-4 h-4" />
  };

  return (
    <tr className="hover:bg-slate-50 transition-colors">
      <td className="px-6 py-4">
        <div>
          <p className="font-semibold text-slate-900">{account.account_number}</p>
          <p className="text-xs text-slate-600">{account.id.substring(0, 8)}</p>
        </div>
      </td>
      <td className="px-6 py-4">
        <p className="text-slate-900">{account.cif_number}</p>
      </td>
      <td className="px-6 py-4">
        <div className="flex items-center gap-2">
          {typeIcons[account.deposit_type as keyof typeof typeIcons]}
          <span className="text-sm text-slate-700">
            {account.deposit_type === 'FIXED_DEPOSIT' ? 'FD' : 'RD'}
          </span>
        </div>
      </td>
      <td className="px-6 py-4 text-right">
        <p className="font-semibold text-slate-900">₹{account.principal_amount.toLocaleString('en-IN')}</p>
      </td>
      <td className="px-6 py-4 text-center">
        <span className="font-semibold text-blue-600">{account.interest_rate}%</span>
      </td>
      <td className="px-6 py-4">
        <p className="text-slate-900 text-sm">{new Date(account.maturity_date).toLocaleDateString()}</p>
      </td>
      <td className="px-6 py-4 text-center">
        <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${
          statusColors[account.status as keyof typeof statusColors] || 'bg-slate-100 text-slate-700'
        }`}>
          {account.status.replace(/_/g, ' ')}
        </span>
      </td>
      <td className="px-6 py-4 text-center">
        <div className="flex items-center justify-center gap-2">
          <Link href={`/deposits/accounts/${account.id}`}>
            <button className="p-2 hover:bg-slate-100 rounded-lg transition-colors">
              <Eye className="w-4 h-4 text-slate-600" />
            </button>
          </Link>
          <button className="p-2 hover:bg-slate-100 rounded-lg transition-colors">
            <MoreVertical className="w-4 h-4 text-slate-600" />
          </button>
        </div>
      </td>
    </tr>
  );
}

function SummaryCard({ label, value, icon }: any) {
  return (
    <div className="bg-white rounded-xl shadow border border-slate-200 p-6">
      <div className="flex items-start justify-between mb-4">
        <div className="p-3 bg-slate-50 rounded-xl">{icon}</div>
      </div>
      <p className="text-slate-600 text-sm mb-1">{label}</p>
      <p className="text-3xl font-bold text-slate-900">{value}</p>
    </div>
  );
}

function LoadingState() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50/30 p-8 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-slate-600">Loading accounts...</p>
      </div>
    </div>
  );
}
