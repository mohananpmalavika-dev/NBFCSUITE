'use client'

/**
 * Create Fund Transfer Page
 * Form to create a new fund transfer
 */

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { fundTransferService, treasuryService } from '@/services/treasury.service'
import type { FundTransferCreate, FundTransferType, BankAccount } from '@/services/treasury.service'

export default function CreateFundTransferPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [bankAccounts, setBankAccounts] = useState<BankAccount[]>([])
  
  const [formData, setFormData] = useState<FundTransferCreate>({
    transfer_type: 'internal',
    source_account_id: 0,
    destination_account_id: undefined,
    destination_account_number: '',
    destination_bank_name: '',
    destination_ifsc: '',
    destination_account_holder: '',
    amount: 0,
    currency: 'INR',
    purpose: '',
    reference_number: '',
    is_scheduled: false,
    scheduled_date: '',
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

  const handleInputChange = (field: keyof FundTransferCreate, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleTypeChange = (type: FundTransferType) => {
    setFormData(prev => ({
      ...prev,
      transfer_type: type,
      // Reset destination fields
      destination_account_id: type === 'internal' ? undefined : prev.destination_account_id,
      destination_account_number: type !== 'internal' ? prev.destination_account_number : '',
      destination_bank_name: type !== 'internal' ? prev.destination_bank_name : '',
      destination_ifsc: type !== 'internal' ? prev.destination_ifsc : '',
      destination_account_holder: type !== 'internal' ? prev.destination_account_holder : ''
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Validation
    if (!formData.source_account_id) {
      setError('Please select a source account')
      return
    }
    if (formData.transfer_type === 'internal' && !formData.destination_account_id) {
      setError('Please select a destination account for internal transfers')
      return
    }
    if (formData.transfer_type !== 'internal' && !formData.destination_account_number) {
      setError('Please enter destination account details for external transfers')
      return
    }
    if (formData.amount <= 0) {
      setError('Amount must be greater than zero')
      return
    }
    if (!formData.purpose) {
      setError('Please enter transfer purpose')
      return
    }
    if (formData.is_scheduled && !formData.scheduled_date) {
      setError('Please select scheduled date')
      return
    }
    
    try {
      setLoading(true)
      setError(null)
      const transfer = await fundTransferService.createTransfer(formData)
      alert('Transfer created successfully')
      router.push(`/treasury/fund-transfers/${transfer.id}`)
    } catch (err: any) {
      setError(err.message || 'Failed to create transfer')
    } finally {
      setLoading(false)
    }
  }

  const sourceAccount = bankAccounts.find(a => a.id === formData.source_account_id)

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
        <h1 className="text-3xl font-bold text-gray-900">Create Fund Transfer</h1>
        <p className="text-gray-600 mt-1">Initiate a new fund transfer</p>
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
          <h2 className="text-xl font-bold text-gray-900 mb-6">Transfer Details</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Transfer Type */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Transfer Type <span className="text-red-500">*</span>
              </label>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {(['internal', 'neft', 'rtgs', 'imps', 'upi', 'cheque', 'demand_draft'] as FundTransferType[]).map(type => (
                  <button
                    key={type}
                    type="button"
                    onClick={() => handleTypeChange(type)}
                    className={`px-4 py-2 rounded-lg border-2 transition ${
                      formData.transfer_type === type
                        ? 'border-blue-600 bg-blue-50 text-blue-700'
                        : 'border-gray-300 hover:border-gray-400'
                    }`}
                  >
                    {type === 'internal' ? 'Internal' :
                     type === 'neft' ? 'NEFT' :
                     type === 'rtgs' ? 'RTGS' :
                     type === 'imps' ? 'IMPS' :
                     type === 'upi' ? 'UPI' :
                     type === 'cheque' ? 'Cheque' :
                     'Demand Draft'}
                  </button>
                ))}
              </div>
            </div>

            {/* Source Account */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Source Account <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.source_account_id}
                onChange={(e) => handleInputChange('source_account_id', parseInt(e.target.value))}
                className="w-full border border-gray-300 rounded-lg px-4 py-2"
                required
              >
                <option value={0}>Select Source Account</option>
                {bankAccounts.map(account => (
                  <option key={account.id} value={account.id}>
                    {account.account_name} - {account.account_number}
                  </option>
                ))}
              </select>
              {sourceAccount && (
                <div className="mt-2 text-sm text-gray-600">
                  Available: ₹ {sourceAccount.available_balance.toLocaleString('en-IN')}
                </div>
              )}
            </div>

            {/* Destination - Internal */}
            {formData.transfer_type === 'internal' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Destination Account <span className="text-red-500">*</span>
                </label>
                <select
                  value={formData.destination_account_id || 0}
                  onChange={(e) => handleInputChange('destination_account_id', parseInt(e.target.value))}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2"
                  required
                >
                  <option value={0}>Select Destination Account</option>
                  {bankAccounts.filter(a => a.id !== formData.source_account_id).map(account => (
                    <option key={account.id} value={account.id}>
                      {account.account_name} - {account.account_number}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* Destination - External */}
            {formData.transfer_type !== 'internal' && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Destination Account Number <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.destination_account_number}
                    onChange={(e) => handleInputChange('destination_account_number', e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-4 py-2"
                    placeholder="Enter account number"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Account Holder Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.destination_account_holder}
                    onChange={(e) => handleInputChange('destination_account_holder', e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-4 py-2"
                    placeholder="Enter account holder name"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Bank Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.destination_bank_name}
                    onChange={(e) => handleInputChange('destination_bank_name', e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-4 py-2"
                    placeholder="Enter bank name"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    IFSC Code <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.destination_ifsc}
                    onChange={(e) => handleInputChange('destination_ifsc', e.target.value.toUpperCase())}
                    className="w-full border border-gray-300 rounded-lg px-4 py-2"
                    placeholder="e.g., SBIN0001234"
                    maxLength={11}
                    required
                  />
                </div>
              </>
            )}

            {/* Amount */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Amount <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.amount}
                onChange={(e) => handleInputChange('amount', parseFloat(e.target.value))}
                className="w-full border border-gray-300 rounded-lg px-4 py-2"
                placeholder="0.00"
                required
              />
              {sourceAccount && formData.amount > sourceAccount.available_balance && (
                <div className="mt-1 text-sm text-red-600">
                  Insufficient balance
                </div>
              )}
            </div>

            {/* Reference Number */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Reference Number
              </label>
              <input
                type="text"
                value={formData.reference_number}
                onChange={(e) => handleInputChange('reference_number', e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-4 py-2"
                placeholder="Optional reference"
              />
            </div>

            {/* Purpose */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Purpose <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.purpose}
                onChange={(e) => handleInputChange('purpose', e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-4 py-2"
                placeholder="Reason for transfer"
                maxLength={500}
                required
              />
            </div>

            {/* Scheduling */}
            <div className="md:col-span-2">
              <div className="flex items-center mb-4">
                <input
                  type="checkbox"
                  checked={formData.is_scheduled}
                  onChange={(e) => handleInputChange('is_scheduled', e.target.checked)}
                  className="mr-2"
                  id="scheduled"
                />
                <label htmlFor="scheduled" className="text-sm font-medium text-gray-700">
                  Schedule this transfer for a future date
                </label>
              </div>
              
              {formData.is_scheduled && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Scheduled Date <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="date"
                    value={formData.scheduled_date}
                    onChange={(e) => handleInputChange('scheduled_date', e.target.value)}
                    min={new Date().toISOString().split('T')[0]}
                    className="w-full border border-gray-300 rounded-lg px-4 py-2"
                    required
                  />
                </div>
              )}
            </div>

            {/* Notes */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Notes
              </label>
              <textarea
                value={formData.notes}
                onChange={(e) => handleInputChange('notes', e.target.value)}
                rows={3}
                className="w-full border border-gray-300 rounded-lg px-4 py-2"
                placeholder="Add any additional notes..."
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
            {loading ? 'Creating...' : 'Create Transfer'}
          </button>
        </div>
      </form>
    </div>
  )
}
