'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { treasuryService, BankAccount } from '@/services/treasury.service';

export default function BankAccountDetailPage() {
  const router = useRouter();
  const params = useParams();
  const accountId = params.id as string;
  
  const [account, setAccount] = useState<BankAccount | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    loadAccount();
  }, [accountId]);

  const loadAccount = async () => {
    try {
      setLoading(true);
      const data = await treasuryService.getBankAccount(parseInt(accountId));
      setAccount(data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load bank account');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = () => {
    router.push(`/treasury/bank-accounts/${accountId}/edit`);
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this bank account? This action cannot be undone.')) {
      return;
    }

    try {
      setDeleting(true);
      await treasuryService.deleteBankAccount(parseInt(accountId));
      router.push('/treasury/bank-accounts');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete bank account');
      setDeleting(false);
    }
  };

  const handleBack = () => {
    router.push('/treasury/bank-accounts');
  };

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'inactive':
        return 'bg-gray-100 text-gray-800';
      case 'closed':
        return 'bg-red-100 text-red-800';
      case 'frozen':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-600">Loading account details...</div>
        </div>
      </div>
    );
  }

  if (error || !account) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
          {error || 'Account not found'}
        </div>
        <button
          onClick={handleBack}
          className="mt-4 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
        >
          Back to List
        </button>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <button
            onClick={handleBack}
            className="text-sm text-blue-600 hover:text-blue-800 mb-2 flex items-center"
          >
            <span className="mr-1">←</span> Back to Bank Accounts
          </button>
          <h1 className="text-2xl font-bold text-gray-900">{account.account_name}</h1>
          <p className="text-sm text-gray-600 mt-1">{account.bank_name} - {account.branch_name}</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={handleEdit}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
          >
            Edit
          </button>
          <button
            onClick={handleDelete}
            disabled={deleting}
            className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50"
          >
            {deleting ? 'Deleting...' : 'Delete'}
          </button>
        </div>
      </div>

      {/* Status Badge */}
      <div className="mb-6">
        <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusBadgeClass(account.status)}`}>
          {account.status.charAt(0).toUpperCase() + account.status.slice(1)}
        </span>
        {account.is_primary && (
          <span className="ml-2 inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-purple-100 text-purple-800">
            Primary Account
          </span>
        )}
      </div>

      {/* Balance Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="text-sm text-gray-600 mb-1">Current Balance</div>
          <div className="text-2xl font-bold text-gray-900">{formatCurrency(account.current_balance)}</div>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="text-sm text-gray-600 mb-1">Available Balance</div>
          <div className="text-2xl font-bold text-green-600">{formatCurrency(account.available_balance)}</div>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="text-sm text-gray-600 mb-1">Opening Balance</div>
          <div className="text-2xl font-bold text-gray-900">{formatCurrency(account.opening_balance)}</div>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="text-sm text-gray-600 mb-1">Overdraft Limit</div>
          <div className="text-2xl font-bold text-orange-600">{formatCurrency(account.overdraft_limit)}</div>
        </div>
      </div>

      {/* Account Details */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Basic Information */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Account Information</h2>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Account Number:</span>
              <span className="text-sm font-medium text-gray-900">{account.account_number}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">IFSC Code:</span>
              <span className="text-sm font-medium text-gray-900">{account.ifsc_code}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Account Type:</span>
              <span className="text-sm font-medium text-gray-900 capitalize">
                {account.account_type.replace('_', ' ')}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Currency:</span>
              <span className="text-sm font-medium text-gray-900">{account.currency}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Minimum Balance:</span>
              <span className="text-sm font-medium text-gray-900">{formatCurrency(account.minimum_balance)}</span>
            </div>
          </div>
        </div>

        {/* Contact Information */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Contact Information</h2>
          <div className="space-y-3">
            {account.contact_person && (
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Contact Person:</span>
                <span className="text-sm font-medium text-gray-900">{account.contact_person}</span>
              </div>
            )}
            {account.contact_phone && (
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Phone:</span>
                <span className="text-sm font-medium text-gray-900">{account.contact_phone}</span>
              </div>
            )}
            {account.contact_email && (
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Email:</span>
                <span className="text-sm font-medium text-gray-900">{account.contact_email}</span>
              </div>
            )}
            {!account.contact_person && !account.contact_phone && !account.contact_email && (
              <div className="text-sm text-gray-500 italic">No contact information available</div>
            )}
          </div>
        </div>

        {/* System Information */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">System Information</h2>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Account ID:</span>
              <span className="text-sm font-medium text-gray-900">{account.id}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Created:</span>
              <span className="text-sm font-medium text-gray-900">{formatDate(account.created_at)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Last Updated:</span>
              <span className="text-sm font-medium text-gray-900">{formatDate(account.updated_at)}</span>
            </div>
            {account.last_reconciled_at && (
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Last Reconciled:</span>
                <span className="text-sm font-medium text-gray-900">{formatDate(account.last_reconciled_at)}</span>
              </div>
            )}
          </div>
        </div>

        {/* Notes */}
        {account.notes && (
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Notes</h2>
            <p className="text-sm text-gray-700 whitespace-pre-wrap">{account.notes}</p>
          </div>
        )}
      </div>

      {/* Recent Activity Section (Placeholder) */}
      <div className="mt-6 bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h2>
        <div className="text-sm text-gray-500 italic">
          Recent transactions and activity will be displayed here once integrated with the transaction module.
        </div>
      </div>
    </div>
  );
}
