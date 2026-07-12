'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { crmApi, RelationshipCreateData, CRMAccount } from '@/services/crmApi'

interface RelationshipFormProps {
  relationshipId?: string
  accountId?: string
  mode: 'create' | 'edit'
}

export default function RelationshipForm({ relationshipId, accountId, mode }: RelationshipFormProps) {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [accounts, setAccounts] = useState<CRMAccount[]>([])

  const [formData, setFormData] = useState<RelationshipCreateData>({
    primary_account_id: accountId || '',
    related_account_id: '',
    relationship_type: 'partner',
    relationship_description: '',
    strength: 'medium',
    start_date: '',
  })

  useEffect(() => {
    loadAccounts()
    if (mode === 'edit' && relationshipId) {
      // Load relationship data
    }
  }, [relationshipId, mode])

  const loadAccounts = async () => {
    try {
      const response = await crmApi.accounts.list({ limit: 100 })
      if (response.success) {
        setAccounts(response.data.accounts)
      }
    } catch (err: any) {
      console.error('Failed to load accounts:', err)
    }
  }

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError(null)

    try {
      if (mode === 'create') {
        const response = await crmApi.relationships.create(formData)
        if (response.success) {
          router.push(`/crm/accounts/${formData.primary_account_id}`)
        }
      }
    } catch (err: any) {
      setError(err.message || 'Failed to save relationship')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-6">
            {mode === 'create' ? 'Create New Relationship' : 'Edit Relationship'}
          </h1>

          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Primary Account
              </label>
              <select
                name="primary_account_id"
                value={formData.primary_account_id}
                onChange={handleChange}
                required
                disabled={!!accountId}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select Account</option>
                {accounts.map((account) => (
                  <option key={account.id} value={account.id}>
                    {account.account_name} ({account.account_number})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Related Account <span className="text-red-500">*</span>
              </label>
              <select
                name="related_account_id"
                value={formData.related_account_id}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select Account</option>
                {accounts
                  .filter((a) => a.id !== formData.primary_account_id)
                  .map((account) => (
                    <option key={account.id} value={account.id}>
                      {account.account_name} ({account.account_number})
                    </option>
                  ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Relationship Type
              </label>
              <select
                name="relationship_type"
                value={formData.relationship_type}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              >
                <option value="parent_child">Parent-Child</option>
                <option value="subsidiary">Subsidiary</option>
                <option value="partner">Partner</option>
                <option value="competitor">Competitor</option>
                <option value="vendor">Vendor</option>
                <option value="customer">Customer</option>
                <option value="referral">Referral</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Relationship Strength
              </label>
              <select
                name="strength"
                value={formData.strength}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              >
                <option value="strong">Strong</option>
                <option value="medium">Medium</option>
                <option value="weak">Weak</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Start Date
              </label>
              <input
                type="date"
                name="start_date"
                value={formData.start_date}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                name="relationship_description"
                value={formData.relationship_description}
                onChange={handleChange}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div className="flex justify-end gap-3 pt-4 border-t">
              <button
                type="button"
                onClick={() => router.back()}
                className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={saving}
                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {saving ? 'Saving...' : mode === 'create' ? 'Create Relationship' : 'Update Relationship'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
