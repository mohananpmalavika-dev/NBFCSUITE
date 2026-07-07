'use client'

/**
 * Create Bank Reconciliation Page
 * Form to create a new bank reconciliation
 */

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { reconciliationService, treasuryService } from '@/services/treasury.service'
import type { BankReconciliationCreate, BankAccount } from '@/services/treasury.service'

export default function CreateReconciliationPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [bankAccounts, setBankAccounts] = useState<BankAccount[]>([])
  
  const [formData, setFormData] = useState<BankReconciliationCreate>({
    bank_account_id: 0,
    reconciliation_date: new Date().toISOString().split('T')[0],
    period_start_date: '',
    period_end_date: '',
    book_balance: 0,
    bank_balance: 0,
    notes: ''
  })

  useEffect(() => {
    fetchBankAccounts()
  }, [])

  const fetchBankAccounts = async () => {
    try {
      const response = await treasuryService.getActiveBankAccounts()
      setBankAccounts(response)
    } catch (err: any) {
      console.error('Failed to fetch bank accounts:', err)
    }
  }

  const handleInputChange = (field: keyof BankReconciliationCreate, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Validation
    if (!formData.bank_account_id) {
      setError('Please select a bank account')
      return
    }
    if (!formData.period_start_date || !formData.period_end_date) {
      setError('Please select period dates')
      return
    }
    if (formData.period_end_date < formData.period_start_date) {
      setError('Period end date must be after start date')
      return
    }
    
    try {
      setLoading(true)
      setError(null)
      const reconciliation = await reconciliationService.createReconciliation(formData)
      alert('Reconciliation created successfully')
      router.push(`/treasury/reconciliation/${reconciliation.id}`)
    } catch (err: any) {
      setError(err.message || 'Failed to create reconciliation')
    } finally {
      setLoading(false)
    }
  }

  const difference = formData.bank_balance - formData.book_balance

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => router.back()}
          className="text-blue-600 hover:text-blue-800 mb-2"
        >
          ← Back
        </button>
        <h1 className="text-3xl font-bold text-gray-900">Create Bank Reconciliation</h1>
        <p className="text-gray-600 mt-1">Create a new bank reconciliation</p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
          {error}
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit}>
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-6">Reconciliation Details</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Bank Account */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Bank Account <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.bank_account_id}
                onChange={(e) => handleInputChange('bank_account_id', parseInt(e.target.value))}
                className="w-full border border-gray-300 rounded-lg px-4 py-2"
                required
              >
                <option value={0}>Select Bank Account</option>
                {bankAccounts.map(account => (
                  <option key={account.id} value={account.id}>
                    {account.account_name} - {account.account_number}
                  </option>
                ))}
              </select>
            </div>

            {/* Reconciliation Date */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Reconciliation Date <span className="text-red-500">*</span>
              </label>
              <input
                type="date"
                value={formData.reconciliation_date}
                onChange={(e) => handleInputChange('reconciliation_date', e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-4 py-2"
                required
              />
            </div>

            {/* Period Start Date */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Period Start Date <span className="text-red-500">*</span>
              </label>
              <input
                type="date"
                value={formData.period_start_date}
                onChange={(e) => handleInputChange('period_start_date', e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-4 py-2"
                required
              />
            </div>

            {/* Period End Date */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Period End Date <span className="text-red-500">*</span>
              </label>
              <input
                type="date"
                value={formData.period_end_date}
                onChange={(e) => handleInputChange('period_end_date', e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-4 py-2"
                required
              />
            </div>

            {/* Book Balance */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Book Balance (GL) <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.book_balance}
                onChange={(e) => handleInputChange('book_balance', parseFloat(e.target.value))}
                className="w-full border border-gray-300 rounded-lg px-4 py-2"
                required
              />
            </div>

            {/* Bank Balance */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Bank Balance (Statement) <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.bank_balance}
                onChange={(e) => handleInputChange('bank_balance', parseFloat(e.target.value))}
                className="w-full border border-gray-300 rounded-lg px-4 py-2"
                required
              />
            </div>

            {/* Difference Display */}
            <div className="md:col-span-2">
              <div className={`p-4 rounded-lg ${
                difference === 0 
                  ? 'bg-green-50 border border-green-200' 
                  : 'bg-yellow-50 border border-yellow-200'
              }`}>
                <div className="text-sm font-medium text-gray-700 mb-1">Difference</div>
                <div className={`text-2xl font-bold ${
                  difference === 0 ? 'text-green-600' : 'text-yellow-600'
                }`}>
                  ₹ {Math.abs(difference).toFixed(2)}
                  {difference !== 0 && (
                    <span className="text-sm ml-2">
                      ({difference > 0 ? 'Bank higher' : 'Book higher'})
                    </span>
                  )}
                </div>
              </div>
            </div>

            {/* Notes */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Notes
              </label>
              <textarea
                value={formData.notes}
                onChange={(e) => handleInputChange('notes', e.target.value)}
                rows={4}
                className="w-full border border-gray-300 rounded-lg px-4 py-2"
                placeholder="Add any notes or comments..."
              />
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-4">
          <button
            type="button"
            onClick={() => router.back()}
            className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            disabled={loading}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            disabled={loading}
          >
            {loading ? 'Creating...' : 'Create Reconciliation'}
          </button>
        </div>
      </form>
    </div>
  )
}
