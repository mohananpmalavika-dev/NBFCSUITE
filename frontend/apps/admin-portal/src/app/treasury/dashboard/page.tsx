'use client'

/**
 * Treasury Dashboard Page
 * Overview of treasury operations and cash position
 */

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { treasuryService, type TreasuryBankAccount, type BankAccountStatistics } from '@/services/treasury.service'

export default function TreasuryDashboardPage() {
  const router = useRouter()
  const [stats, setStats] = useState<BankAccountStatistics | null>(null)
  const [accounts, setAccounts] = useState<TreasuryBankAccount[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      const [statsResponse, accountsResponse] = await Promise.all([
        treasuryService.getBankAccountStatistics(),
        treasuryService.getActiveBankAccounts()
      ])
      setStats(statsResponse.data)
      setAccounts(accountsResponse.data)
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    } finally {
      setLoading(false)
    }
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

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex justify-center items-center h-64">
          <div className="inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Treasury Dashboard</h1>
        <p className="text-gray-600 mt-2">Overview of cash position and bank accounts</p>
      </div>

      {/* Main Statistics */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 p-6 rounded-lg shadow-lg text-white">
            <div className="text-sm opacity-90">Total Accounts</div>
            <div className="text-3xl font-bold mt-2">{stats.total_accounts}</div>
            <div className="text-sm opacity-75 mt-2">
              {stats.active_accounts} Active • {stats.inactive_accounts} Inactive
            </div>
          </div>

          <div className="bg-gradient-to-br from-green-500 to-green-600 p-6 rounded-lg shadow-lg text-white">
            <div className="text-sm opacity-90">Total Balance</div>
            <div className="text-3xl font-bold mt-2">{formatCurrency(stats.total_balance)}</div>
            <div className="text-sm opacity-75 mt-2">Across all accounts</div>
          </div>

          <div className="bg-gradient-to-br from-orange-500 to-orange-600 p-6 rounded-lg shadow-lg text-white">
            <div className="text-sm opacity-90">Below Minimum</div>
            <div className="text-3xl font-bold mt-2">{stats.accounts_below_minimum}</div>
            <div className="text-sm opacity-75 mt-2">
              {stats.accounts_below_minimum > 0 ? 'Needs attention' : 'All good'}
            </div>
          </div>

          <div className="bg-gradient-to-br from-purple-500 to-purple-600 p-6 rounded-lg shadow-lg text-white">
            <div className="text-sm opacity-90">Account Types</div>
            <div className="text-3xl font-bold mt-2">{Object.keys(stats.accounts_by_type).length}</div>
            <div className="text-sm opacity-75 mt-2">Different types in use</div>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="bg-white p-6 rounded-lg shadow mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button
            onClick={() => router.push('/treasury/bank-accounts')}
            className="p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition text-center"
          >
            <div className="text-3xl mb-2">🏦</div>
            <div className="text-sm font-medium text-gray-900">Bank Accounts</div>
          </button>

          <button
            onClick={() => router.push('/treasury/cash-position')}
            className="p-4 border-2 border-gray-200 rounded-lg hover:border-green-500 hover:bg-green-50 transition text-center"
          >
            <div className="text-3xl mb-2">💰</div>
            <div className="text-sm font-medium text-gray-900">Cash Position</div>
          </button>

          <button
            onClick={() => router.push('/treasury/reconciliation')}
            className="p-4 border-2 border-gray-200 rounded-lg hover:border-purple-500 hover:bg-purple-50 transition text-center"
          >
            <div className="text-3xl mb-2">✅</div>
            <div className="text-sm font-medium text-gray-900">Reconciliation</div>
          </button>

          <button
            onClick={() => router.push('/treasury/transfers')}
            className="p-4 border-2 border-gray-200 rounded-lg hover:border-orange-500 hover:bg-orange-50 transition text-center"
          >
            <div className="text-3xl mb-2">↔️</div>
            <div className="text-sm font-medium text-gray-900">Fund Transfers</div>
          </button>
        </div>
      </div>

      {/* Active Bank Accounts */}
      <div className="bg-white p-6 rounded-lg shadow mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Active Bank Accounts</h2>
          <button
            onClick={() => router.push('/treasury/bank-accounts')}
            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            View All →
          </button>
        </div>

        {accounts.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-600 mb-4">No active bank accounts</p>
            <button
              onClick={() => router.push('/treasury/bank-accounts/create')}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Add Bank Account
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {accounts.slice(0, 5).map((account) => (
              <div
                key={account.id}
                className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
                onClick={() => router.push(`/treasury/bank-accounts/${account.id}`)}
              >
                <div className="flex-1">
                  <div className="font-medium text-gray-900">{account.bank_name}</div>
                  <div className="text-sm text-gray-600">{account.account_name}</div>
                  <div className="text-xs text-gray-500 mt-1">
                    {account.account_number} • {formatAccountType(account.account_purpose)}
                  </div>
                </div>
                <div className="text-right">
                  <div className={`text-lg font-semibold ${
                    account.current_balance < account.minimum_balance 
                      ? 'text-red-600' 
                      : 'text-green-600'
                  }`}>
                    {formatCurrency(account.current_balance)}
                  </div>
                  <div className="text-xs text-gray-500">
                    Min: {formatCurrency(account.minimum_balance)}
                  </div>
                  {account.current_balance < account.minimum_balance && (
                    <span className="inline-block mt-1 px-2 py-1 bg-red-100 text-red-800 text-xs rounded">
                      Below Min
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Account Distribution */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* By Type */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Distribution by Type</h3>
            <div className="space-y-3">
              {Object.entries(stats.accounts_by_type).map(([type, count]) => (
                <div key={type}>
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm text-gray-700">{formatAccountType(type)}</span>
                    <span className="text-sm font-semibold text-gray-900">{count}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${(count / stats.total_accounts) * 100}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* By Purpose */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Distribution by Purpose</h3>
            <div className="space-y-3">
              {Object.entries(stats.accounts_by_purpose).map(([purpose, count]) => (
                <div key={purpose}>
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm text-gray-700">{formatAccountType(purpose)}</span>
                    <span className="text-sm font-semibold text-gray-900">{count}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-600 h-2 rounded-full"
                      style={{ width: `${(count / stats.total_accounts) * 100}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Alerts Section */}
      {stats && stats.accounts_below_minimum > 0 && (
        <div className="mt-6 bg-orange-50 border-l-4 border-orange-400 p-6 rounded-lg">
          <div className="flex items-start">
            <div className="text-2xl mr-3">⚠️</div>
            <div>
              <h3 className="text-lg font-semibold text-orange-900">Attention Required</h3>
              <p className="text-orange-700 mt-1">
                {stats.accounts_below_minimum} account(s) are below minimum balance requirement.
                Please review and add funds to maintain account health.
              </p>
              <button
                onClick={() => router.push('/treasury/bank-accounts?filter=below_minimum')}
                className="mt-3 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700"
              >
                View Affected Accounts
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
