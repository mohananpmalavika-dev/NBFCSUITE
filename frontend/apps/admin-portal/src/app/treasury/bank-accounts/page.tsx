'use client'

/**
 * Treasury Bank Accounts Page
 * List and manage bank accounts
 */

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { treasuryService, type TreasuryBankAccount, type BankAccountStatistics } from '@/services/treasury.service'

export default function BankAccountsPage() {
  const router = useRouter()
  const [accounts, setAccounts] = useState<TreasuryBankAccount[]>([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState<BankAccountStatistics | null>(null)
  const [filters, setFilters] = useState({
    status: '',
    account_type: '',
    account_purpose: '',
    search: ''
  })
  const [showCreateModal, setShowCreateModal] = useState(false)

  useEffect(() => {
    loadAccounts()
    loadStatistics()
  }, [filters])

  const loadAccounts = async () => {
    try {
      setLoading(true)
      const response = await treasuryService.getBankAccounts({
        status: filters.status || undefined,
        account_type: filters.account_type || undefined,
        account_purpose: filters.account_purpose || undefined,
        search: filters.search || undefined,
        skip: 0,
        limit: 100
      })
      setAccounts(response.data.accounts || [])
    } catch (error) {
      console.error('Failed to load bank accounts:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadStatistics = async () => {
    try {
      const response = await treasuryService.getBankAccountStatistics()
      setStats(response.data)
    } catch (error) {
      console.error('Failed to load statistics:', error)
    }
  }

  const handleDeleteAccount = async (id: number) => {
    if (!confirm('Are you sure you want to delete this account? Account must have zero balance.')) {
      return
    }
    try {
      await treasuryService.deleteBankAccount(id)
      loadAccounts()
      loadStatistics()
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to delete account')
    }
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      active: 'bg-green-100 text-green-800',
      inactive: 'bg-gray-100 text-gray-800',
      dormant: 'bg-yellow-100 text-yellow-800',
      closed: 'bg-red-100 text-red-800',
      frozen: 'bg-blue-100 text-blue-800'
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2
    }).format(amount)
  }

  const formatAccountType = (type: string) => {
    return type.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ')
  }

  return (
    <div className="container mx-auto p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Treasury Bank Accounts</h1>
        <p className="text-gray-600 mt-2">Manage all bank accounts used for treasury operations</p>
      </div>

      {/* Statistics Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-sm text-gray-600">Total Accounts</div>
            <div className="text-2xl font-bold text-gray-900">{stats.total_accounts}</div>
            <div className="text-xs text-gray-500 mt-1">Active: {stats.active_accounts}</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-sm text-gray-600">Total Balance</div>
            <div className="text-2xl font-bold text-green-600">{formatCurrency(stats.total_balance)}</div>
            <div className="text-xs text-gray-500 mt-1">Across all accounts</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-sm text-gray-600">Below Minimum</div>
            <div className="text-2xl font-bold text-orange-600">{stats.accounts_below_minimum}</div>
            <div className="text-xs text-gray-500 mt-1">Accounts need attention</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-sm text-gray-600">Inactive Accounts</div>
            <div className="text-2xl font-bold text-gray-600">{stats.inactive_accounts}</div>
            <div className="text-xs text-gray-500 mt-1">Not currently used</div>
          </div>
        </div>
      )}

      {/* Actions and Filters */}
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="flex flex-wrap gap-4 items-center justify-between">
          <div className="flex gap-4">
            <button
              onClick={() => router.push('/treasury/bank-accounts/create')}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              + Add Bank Account
            </button>
            <button
              onClick={() => router.push('/treasury/dashboard')}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition"
            >
              📊 Dashboard
            </button>
          </div>

          <div className="flex gap-4 flex-wrap">
            <input
              type="text"
              placeholder="Search accounts..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />

            <select
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="dormant">Dormant</option>
              <option value="closed">Closed</option>
              <option value="frozen">Frozen</option>
            </select>

            <select
              value={filters.account_type}
              onChange={(e) => setFilters({ ...filters, account_type: e.target.value })}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Types</option>
              <option value="savings">Savings</option>
              <option value="current">Current</option>
              <option value="cash_credit">Cash Credit</option>
              <option value="overdraft">Overdraft</option>
              <option value="fixed_deposit">Fixed Deposit</option>
            </select>

            <select
              value={filters.account_purpose}
              onChange={(e) => setFilters({ ...filters, account_purpose: e.target.value })}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Purposes</option>
              <option value="operational">Operational</option>
              <option value="disbursement">Disbursement</option>
              <option value="collection">Collection</option>
              <option value="payroll">Payroll</option>
              <option value="tax">Tax</option>
              <option value="reserve">Reserve</option>
              <option value="investment">Investment</option>
            </select>
          </div>
        </div>
      </div>

      {/* Accounts Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {loading ? (
          <div className="p-8 text-center">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
            <p className="mt-2 text-gray-600">Loading accounts...</p>
          </div>
        ) : accounts.length === 0 ? (
          <div className="p-8 text-center">
            <p className="text-gray-600">No bank accounts found</p>
            <button
              onClick={() => router.push('/treasury/bank-accounts/create')}
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Add Your First Account
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Bank & Account
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Account Number
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type / Purpose
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Current Balance
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Min Balance
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {accounts.map((account) => (
                  <tr key={account.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{account.bank_name}</div>
                      <div className="text-sm text-gray-500">{account.account_name}</div>
                      {account.branch_name && (
                        <div className="text-xs text-gray-400">{account.branch_name}</div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900 font-mono">{account.account_number}</div>
                      {account.ifsc_code && (
                        <div className="text-xs text-gray-500">IFSC: {account.ifsc_code}</div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{formatAccountType(account.account_type)}</div>
                      <div className="text-xs text-gray-500">{formatAccountType(account.account_purpose)}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className={`text-sm font-semibold ${
                        account.current_balance < account.minimum_balance 
                          ? 'text-red-600' 
                          : 'text-green-600'
                      }`}>
                        {formatCurrency(account.current_balance)}
                      </div>
                      <div className="text-xs text-gray-500">
                        Available: {formatCurrency(account.available_balance)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatCurrency(account.minimum_balance)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(account.status)}`}>
                        {account.status.charAt(0).toUpperCase() + account.status.slice(1)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={() => router.push(`/treasury/bank-accounts/${account.id}`)}
                        className="text-blue-600 hover:text-blue-900 mr-3"
                      >
                        View
                      </button>
                      <button
                        onClick={() => router.push(`/treasury/bank-accounts/${account.id}/edit`)}
                        className="text-green-600 hover:text-green-900 mr-3"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDeleteAccount(account.id)}
                        className="text-red-600 hover:text-red-900"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Summary Section */}
      {stats && accounts.length > 0 && (
        <div className="mt-6 bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Account Distribution</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* By Type */}
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">By Account Type</h4>
              <div className="space-y-2">
                {Object.entries(stats.accounts_by_type).map(([type, count]) => (
                  <div key={type} className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">{formatAccountType(type)}</span>
                    <span className="text-sm font-semibold text-gray-900">{count}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* By Purpose */}
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">By Purpose</h4>
              <div className="space-y-2">
                {Object.entries(stats.accounts_by_purpose).map(([purpose, count]) => (
                  <div key={purpose} className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">{formatAccountType(purpose)}</span>
                    <span className="text-sm font-semibold text-gray-900">{count}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
