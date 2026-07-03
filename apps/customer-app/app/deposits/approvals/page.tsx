'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { 
  CheckCircle, XCircle, Clock, Search, Filter, 
  Eye, User, DollarSign, Calendar, FileText,
  TrendingUp, AlertCircle, CheckSquare, XSquare,
  RefreshCw
} from 'lucide-react';

// Types
interface PendingApproval {
  id: string;
  account_number: string;
  customer_id: string;
  customer_name?: string;
  cif_number?: string;
  product_name?: string;
  deposit_type: string;
  principal_amount: number;
  interest_rate: number;
  tenure_days: number;
  maturity_amount: number;
  open_date: string;
  maturity_date: string;
  status: string;
  branch_code?: string;
  is_senior_citizen: boolean;
  auto_renewal: boolean;
  created_at: string;
  submitted_by?: string;
  submitted_at?: string;
  approval_level?: number;
  pending_with?: string;
}

interface ApprovalStats {
  total_pending: number;
  total_amount: number;
  avg_processing_time_hours: number;
  pending_today: number;
}

export default function ApprovalsPage() {
  const router = useRouter();
  const [approvals, setApprovals] = useState<PendingApproval[]>([]);
  const [filteredApprovals, setFilteredApprovals] = useState<PendingApproval[]>([]);
  const [stats, setStats] = useState<ApprovalStats>({
    total_pending: 0,
    total_amount: 0,
    avg_processing_time_hours: 0,
    pending_today: 0
  });
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<'ALL' | 'FD' | 'RD'>('ALL');
  const [selectedApprovals, setSelectedApprovals] = useState<Set<string>>(new Set());
  const [processingId, setProcessingId] = useState<string | null>(null);

  useEffect(() => {
    fetchApprovals();
  }, []);

  useEffect(() => {
    filterApprovals();
  }, [approvals, searchTerm, filterType]);

  const fetchApprovals = async () => {
    try {
      setLoading(true);
      
      // Fetch pending approvals
      const response = await fetch('http://localhost:8007/api/v1/accounts?status=PENDING_APPROVAL');
      if (response.ok) {
        const data = await response.json();
        setApprovals(data);
        
        // Calculate stats
        const totalAmount = data.reduce((sum: number, acc: PendingApproval) => sum + acc.principal_amount, 0);
        const today = new Date().toDateString();
        const pendingToday = data.filter((acc: PendingApproval) => 
          new Date(acc.created_at).toDateString() === today
        ).length;
        
        setStats({
          total_pending: data.length,
          total_amount: totalAmount,
          avg_processing_time_hours: 4.5, // Mock value
          pending_today: pendingToday
        });
      }
    } catch (error) {
      console.error('Error fetching approvals:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterApprovals = () => {
    let filtered = approvals;

    // Filter by type
    if (filterType !== 'ALL') {
      filtered = filtered.filter(acc => {
        if (filterType === 'FD') return acc.deposit_type === 'FIXED_DEPOSIT';
        if (filterType === 'RD') return acc.deposit_type === 'RECURRING_DEPOSIT';
        return true;
      });
    }

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(acc =>
        acc.account_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        acc.cif_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        acc.customer_name?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    setFilteredApprovals(filtered);
  };

  const handleApprove = async (accountId: string) => {
    if (!confirm('Are you sure you want to approve this account?')) return;

    try {
      setProcessingId(accountId);
      const response = await fetch(`http://localhost:8007/api/v1/accounts/${accountId}/approve`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          approved_by: 'ADMIN', // Replace with actual user
          remarks: 'Approved'
        })
      });

      if (response.ok) {
        alert('Account approved successfully!');
        fetchApprovals(); // Refresh list
      } else {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error approving account:', error);
      alert('Failed to approve account');
    } finally {
      setProcessingId(null);
    }
  };

  const handleReject = async (accountId: string) => {
    const reason = prompt('Please provide a reason for rejection:');
    if (!reason) return;

    try {
      setProcessingId(accountId);
      const response = await fetch(`http://localhost:8007/api/v1/accounts/${accountId}/reject`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          rejected_by: 'ADMIN', // Replace with actual user
          remarks: reason
        })
      });

      if (response.ok) {
        alert('Account rejected successfully!');
        fetchApprovals(); // Refresh list
      } else {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error rejecting account:', error);
      alert('Failed to reject account');
    } finally {
      setProcessingId(null);
    }
  };

  const handleBulkApprove = async () => {
    if (selectedApprovals.size === 0) {
      alert('Please select accounts to approve');
      return;
    }

    if (!confirm(`Approve ${selectedApprovals.size} selected accounts?`)) return;

    try {
      setLoading(true);
      const promises = Array.from(selectedApprovals).map(id =>
        fetch(`http://localhost:8007/api/v1/accounts/${id}/approve`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ approved_by: 'ADMIN', remarks: 'Bulk approval' })
        })
      );

      await Promise.all(promises);
      alert(`Successfully approved ${selectedApprovals.size} accounts!`);
      setSelectedApprovals(new Set());
      fetchApprovals();
    } catch (error) {
      console.error('Error in bulk approval:', error);
      alert('Some approvals failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const toggleSelection = (accountId: string) => {
    const newSelection = new Set(selectedApprovals);
    if (newSelection.has(accountId)) {
      newSelection.delete(accountId);
    } else {
      newSelection.add(accountId);
    }
    setSelectedApprovals(newSelection);
  };

  const toggleSelectAll = () => {
    if (selectedApprovals.size === filteredApprovals.length) {
      setSelectedApprovals(new Set());
    } else {
      setSelectedApprovals(new Set(filteredApprovals.map(acc => acc.id)));
    }
  };

  if (loading && approvals.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50/30 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600">Loading approvals...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50/30 p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">Pending Approvals</h1>
            <p className="text-slate-600 mt-1">Review and approve deposit accounts</p>
          </div>
          <button
            onClick={fetchApprovals}
            className="px-4 py-2 bg-white border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors flex items-center gap-2"
          >
            <RefreshCw className="h-4 w-4" />
            Refresh
          </button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl p-6 text-white shadow-lg">
            <div className="flex items-center gap-3 mb-2">
              <Clock className="h-6 w-6" />
              <span className="text-sm opacity-90">Total Pending</span>
            </div>
            <p className="text-3xl font-bold">{stats.total_pending}</p>
            <p className="text-sm opacity-75 mt-1">Accounts awaiting approval</p>
          </div>

          <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-6 text-white shadow-lg">
            <div className="flex items-center gap-3 mb-2">
              <DollarSign className="h-6 w-6" />
              <span className="text-sm opacity-90">Total Amount</span>
            </div>
            <p className="text-3xl font-bold">₹{(stats.total_amount / 10000000).toFixed(1)}Cr</p>
            <p className="text-sm opacity-75 mt-1">Pending approval value</p>
          </div>

          <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-6 text-white shadow-lg">
            <div className="flex items-center gap-3 mb-2">
              <TrendingUp className="h-6 w-6" />
              <span className="text-sm opacity-90">Avg Processing Time</span>
            </div>
            <p className="text-3xl font-bold">{stats.avg_processing_time_hours}h</p>
            <p className="text-sm opacity-75 mt-1">Average turnaround time</p>
          </div>

          <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl p-6 text-white shadow-lg">
            <div className="flex items-center gap-3 mb-2">
              <Calendar className="h-6 w-6" />
              <span className="text-sm opacity-90">Today's Submissions</span>
            </div>
            <p className="text-3xl font-bold">{stats.pending_today}</p>
            <p className="text-sm opacity-75 mt-1">New applications today</p>
          </div>
        </div>

        {/* Filters and Actions */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
          <div className="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
            {/* Search */}
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-slate-400" />
              <input
                type="text"
                placeholder="Search by account, CIF, or customer name..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Filter Buttons */}
            <div className="flex gap-2">
              {['ALL', 'FD', 'RD'].map((type) => (
                <button
                  key={type}
                  onClick={() => setFilterType(type as any)}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    filterType === type
                      ? 'bg-blue-600 text-white'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  {type}
                </button>
              ))}
            </div>

            {/* Bulk Actions */}
            {selectedApprovals.size > 0 && (
              <button
                onClick={handleBulkApprove}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
              >
                <CheckSquare className="h-4 w-4" />
                Approve Selected ({selectedApprovals.size})
              </button>
            )}
          </div>
        </div>

        {/* Approvals Table */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
          {filteredApprovals.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-50 border-b border-slate-200">
                  <tr>
                    <th className="px-4 py-3 text-left">
                      <input
                        type="checkbox"
                        checked={selectedApprovals.size === filteredApprovals.length && filteredApprovals.length > 0}
                        onChange={toggleSelectAll}
                        className="rounded border-slate-300"
                      />
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-slate-600 uppercase">Account</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-slate-600 uppercase">Customer</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-slate-600 uppercase">Product</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-slate-600 uppercase">Amount</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-slate-600 uppercase">Rate</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-slate-600 uppercase">Tenure</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-slate-600 uppercase">Maturity</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-slate-600 uppercase">Submitted</th>
                    <th className="px-4 py-3 text-center text-xs font-medium text-slate-600 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200">
                  {filteredApprovals.map((approval) => {
                    const daysAgo = Math.floor((Date.now() - new Date(approval.created_at).getTime()) / (1000 * 60 * 60 * 24));
                    const isUrgent = daysAgo >= 1;
                    
                    return (
                      <tr 
                        key={approval.id} 
                        className={`hover:bg-slate-50 transition-colors ${isUrgent ? 'bg-red-50/50' : ''}`}
                      >
                        <td className="px-4 py-4">
                          <input
                            type="checkbox"
                            checked={selectedApprovals.has(approval.id)}
                            onChange={() => toggleSelection(approval.id)}
                            className="rounded border-slate-300"
                          />
                        </td>
                        <td className="px-4 py-4">
                          <div>
                            <p className="text-sm font-medium text-slate-900">{approval.account_number}</p>
                            <p className="text-xs text-slate-500">{approval.branch_code || 'HO'}</p>
                          </div>
                        </td>
                        <td className="px-4 py-4">
                          <div className="flex items-center gap-2">
                            <User className="h-4 w-4 text-slate-400" />
                            <div>
                              <p className="text-sm font-medium text-slate-900">{approval.customer_name || 'N/A'}</p>
                              <p className="text-xs text-slate-500">CIF: {approval.cif_number || 'N/A'}</p>
                            </div>
                          </div>
                        </td>
                        <td className="px-4 py-4">
                          <div>
                            <p className="text-sm text-slate-900">{approval.product_name || 'N/A'}</p>
                            <span className="text-xs px-2 py-0.5 bg-blue-100 text-blue-800 rounded-full">
                              {approval.deposit_type === 'FIXED_DEPOSIT' ? 'FD' : 'RD'}
                            </span>
                          </div>
                        </td>
                        <td className="px-4 py-4 text-right">
                          <p className="text-sm font-medium text-slate-900">
                            ₹{approval.principal_amount.toLocaleString('en-IN')}
                          </p>
                        </td>
                        <td className="px-4 py-4 text-right">
                          <p className="text-sm font-medium text-green-600">
                            {approval.interest_rate}%
                          </p>
                        </td>
                        <td className="px-4 py-4 text-right">
                          <p className="text-sm text-slate-900">
                            {Math.floor(approval.tenure_days / 365)}y {approval.tenure_days % 365}d
                          </p>
                        </td>
                        <td className="px-4 py-4 text-right">
                          <p className="text-sm font-medium text-slate-900">
                            ₹{approval.maturity_amount.toLocaleString('en-IN')}
                          </p>
                        </td>
                        <td className="px-4 py-4">
                          <div className="flex items-center gap-1">
                            {isUrgent && <AlertCircle className="h-4 w-4 text-red-500" />}
                            <div>
                              <p className="text-xs text-slate-600">
                                {new Date(approval.created_at).toLocaleDateString('en-IN')}
                              </p>
                              <p className={`text-xs ${isUrgent ? 'text-red-600 font-medium' : 'text-slate-500'}`}>
                                {daysAgo === 0 ? 'Today' : `${daysAgo}d ago`}
                              </p>
                            </div>
                          </div>
                        </td>
                        <td className="px-4 py-4">
                          <div className="flex items-center justify-center gap-2">
                            <button
                              onClick={() => router.push(`/deposits/accounts/${approval.id}`)}
                              className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                              title="View Details"
                            >
                              <Eye className="h-4 w-4" />
                            </button>
                            <button
                              onClick={() => handleApprove(approval.id)}
                              disabled={processingId === approval.id}
                              className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors disabled:opacity-50"
                              title="Approve"
                            >
                              {processingId === approval.id ? (
                                <div className="animate-spin h-4 w-4 border-2 border-green-600 border-t-transparent rounded-full" />
                              ) : (
                                <CheckCircle className="h-4 w-4" />
                              )}
                            </button>
                            <button
                              onClick={() => handleReject(approval.id)}
                              disabled={processingId === approval.id}
                              className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
                              title="Reject"
                            >
                              <XCircle className="h-4 w-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-16">
              <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-slate-900 mb-2">All Clear!</h3>
              <p className="text-slate-600">No pending approvals at the moment.</p>
            </div>
          )}
        </div>

        {/* Summary Footer */}
        {filteredApprovals.length > 0 && (
          <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">
                  Showing <span className="font-medium text-slate-900">{filteredApprovals.length}</span> pending approvals
                </p>
                {selectedApprovals.size > 0 && (
                  <p className="text-sm text-blue-600 mt-1">
                    {selectedApprovals.size} selected for bulk approval
                  </p>
                )}
              </div>
              <div className="text-right">
                <p className="text-sm text-slate-600">Total Value</p>
                <p className="text-xl font-bold text-slate-900">
                  ₹{filteredApprovals.reduce((sum, acc) => sum + acc.principal_amount, 0).toLocaleString('en-IN')}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
