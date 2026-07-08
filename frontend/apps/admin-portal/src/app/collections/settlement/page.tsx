'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { settlementApi } from '@/lib/api/collection';
import { SettlementProposal, SettlementStatus } from '@/types/collection';
import { StatusBadge, CollectionStatCard } from '@/components/collections';

export default function SettlementPage() {
  const router = useRouter();
  const [proposals, setProposals] = useState<SettlementProposal[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<SettlementStatus | 'all'>('all');
  const [stats, setStats] = useState({
    total: 0,
    pending: 0,
    approved: 0,
    rejected: 0,
    totalOsAmount: 0,
    totalSettlement: 0,
  });

  useEffect(() => {
    loadProposals();
  }, [filter]);

  const loadProposals = async () => {
    try {
      setLoading(true);
      const data = await settlementApi.listProposals(
        filter === 'all' ? undefined : { proposal_status: filter }
      );
      setProposals(data.items || data);
      calculateStats(data.items || data);
    } catch (error) {
      console.error('Failed to load proposals:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = (data: SettlementProposal[]) => {
    setStats({
      total: data.length,
      pending: data.filter(p => p.status === 'pending_approval').length,
      approved: data.filter(p => p.status === 'approved').length,
      rejected: data.filter(p => p.status === 'rejected').length,
      totalOsAmount: data.reduce((sum, p) => sum + p.original_outstanding, 0),
      totalSettlement: data.reduce((sum, p) => sum + p.settlement_amount, 0),
    });
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  };

  const getStatusColor = (status: SettlementStatus) => {
    const colors = {
      draft: 'bg-gray-100 text-gray-800',
      pending_approval: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
      payment_pending: 'bg-blue-100 text-blue-800',
      completed: 'bg-purple-100 text-purple-800',
      cancelled: 'bg-gray-100 text-gray-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getDiscountPercentage = (original: number, settlement: number) => {
    const discount = ((original - settlement) / original) * 100;
    return discount.toFixed(1);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Settlement & One-Time Settlement (OTS)
          </h1>
          <p className="text-gray-600 mt-1">
            Manage settlement proposals and OTS workflows
          </p>
        </div>
        <button
          onClick={() => router.push('/collections/settlement/new')}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          + New Settlement Proposal
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <CollectionStatCard
          title="Total Proposals"
          value={stats.total.toString()}
          icon="📋"
        />
        <CollectionStatCard
          title="Pending Approval"
          value={stats.pending.toString()}
          icon="⏳"
          trend="warning"
        />
        <CollectionStatCard
          title="Approved"
          value={stats.approved.toString()}
          icon="✅"
          trend="success"
        />
        <CollectionStatCard
          title="Rejected"
          value={stats.rejected.toString()}
          icon="❌"
          trend="danger"
        />
        <CollectionStatCard
          title="Total Outstanding"
          value={formatCurrency(stats.totalOsAmount)}
          icon="💰"
        />
        <CollectionStatCard
          title="Settlement Amount"
          value={formatCurrency(stats.totalSettlement)}
          icon="💵"
          trend="success"
        />
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex items-center gap-4">
          <label className="text-sm font-medium text-gray-700">
            Filter by Status:
          </label>
          <div className="flex gap-2 flex-wrap">
            {['all', 'draft', 'pending_approval', 'approved', 'rejected', 'payment_pending', 'completed'].map(
              (status) => (
                <button
                  key={status}
                  onClick={() => setFilter(status as any)}
                  className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                    filter === status
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {status.replace('_', ' ').toUpperCase()}
                </button>
              )
            )}
          </div>
        </div>
      </div>

      {/* Proposals Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-gray-500">Loading proposals...</div>
        ) : proposals.length === 0 ? (
          <div className="p-8 text-center">
            <p className="text-gray-500 mb-4">No settlement proposals found</p>
            <button
              onClick={() => router.push('/collections/settlement/new')}
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              Create your first proposal
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Proposal Details
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Loan Account
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Financial Details
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Discount
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Dates
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {proposals.map((proposal) => (
                  <tr
                    key={proposal.id}
                    className="hover:bg-gray-50 cursor-pointer"
                    onClick={() => router.push(`/collections/settlement/${proposal.id}`)}
                  >
                    <td className="px-6 py-4">
                      <div className="text-sm">
                        <div className="font-medium text-gray-900">
                          {proposal.proposal_number}
                        </div>
                        {proposal.customer_name && (
                          <div className="text-gray-500">{proposal.customer_name}</div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900">
                        {proposal.loan_account_id}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm">
                        <div className="text-gray-900">
                          OS: {formatCurrency(proposal.original_outstanding)}
                        </div>
                        <div className="text-green-600 font-medium">
                          Settlement: {formatCurrency(proposal.settlement_amount)}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                          {getDiscountPercentage(
                            proposal.original_outstanding,
                            proposal.settlement_amount
                          )}
                          % off
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                          proposal.status
                        )}`}
                      >
                        {proposal.status.replace('_', ' ').toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900">
                        <div>Created: {formatDate(proposal.created_at)}</div>
                        {proposal.valid_until && (
                          <div className="text-red-600">
                            Valid: {formatDate(proposal.valid_until)}
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-right text-sm font-medium">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          router.push(`/collections/settlement/${proposal.id}`);
                        }}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        View Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
