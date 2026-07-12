'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { customerServiceApi, TicketCreate, TicketUpdate, Ticket, TicketPriority, TicketStatus, TicketCategory, TicketChannel } from '@/services/customerServiceApi'
import { crmApi, CRMAccount } from '@/services/crmApi'

interface TicketFormProps {
  ticketId?: string
  mode: 'create' | 'edit'
}

export default function TicketForm({ ticketId, mode }: TicketFormProps) {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [accounts, setAccounts] = useState<CRMAccount[]>([])

  // Form state
  const [formData, setFormData] = useState<TicketCreate>({
    subject: '',
    description: '',
    category: 'general',
    priority: 'medium',
    status: 'new',
    channel: 'web',
    contact_name: '',
    contact_email: '',
    contact_phone: '',
    account_id: '',
    assigned_to: '',
    assigned_team: '',
    tags: [],
  })

  const [tagInput, setTagInput] = useState('')

  useEffect(() => {
    loadAccounts()
    if (mode === 'edit' && ticketId) {
      loadTicket()
    }
  }, [ticketId, mode])

  const loadAccounts = async () => {
    try {
      const response = await crmApi.accounts.list({ limit: 1000 })
      if (response.success) {
        setAccounts(response.data.accounts)
      }
    } catch (err) {
      console.error('Failed to load accounts:', err)
    }
  }

  const loadTicket = async () => {
    if (!ticketId) return

    try {
      setLoading(true)
      const response = await customerServiceApi.tickets.get(ticketId)

      if (response.success) {
        const ticket = response.data!
        setFormData({
          subject: ticket.subject,
          description: ticket.description,
          category: ticket.category,
          priority: ticket.priority,
          status: ticket.status,
          channel: ticket.channel,
          contact_name: ticket.contact_name || '',
          contact_email: ticket.contact_email || '',
          contact_phone: ticket.contact_phone || '',
          account_id: ticket.account_id || '',
          assigned_to: ticket.assigned_to || '',
          assigned_team: ticket.assigned_team || '',
          tags: ticket.tags || [],
        })
      } else {
        setError('Failed to load ticket')
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load ticket')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleAddTag = () => {
    if (tagInput.trim() && !formData.tags?.includes(tagInput.trim())) {
      setFormData((prev) => ({
        ...prev,
        tags: [...(prev.tags || []), tagInput.trim()],
      }))
      setTagInput('')
    }
  }

  const handleRemoveTag = (tag: string) => {
    setFormData((prev) => ({
      ...prev,
      tags: (prev.tags || []).filter((t) => t !== tag),
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setSuccess(null)

    try {
      if (mode === 'create') {
        const response = await customerServiceApi.tickets.create(formData)
        if (response.success) {
          setSuccess('Ticket created successfully!')
          setTimeout(() => {
            router.push(`/crm/tickets/${response.data!.id}`)
          }, 1500)
        } else {
          setError('Failed to create ticket')
        }
      } else if (mode === 'edit' && ticketId) {
        const updateData: TicketUpdate = { ...formData }
        const response = await customerServiceApi.tickets.update(ticketId, updateData)
        if (response.success) {
          setSuccess('Ticket updated successfully!')
          setTimeout(() => {
            router.push(`/crm/tickets/${ticketId}`)
          }, 1500)
        } else {
          setError('Failed to update ticket')
        }
      }
    } catch (err: any) {
      setError(err.message || 'Failed to save ticket')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => router.back()}
            className="text-blue-600 hover:text-blue-700 mb-4 flex items-center"
          >
            ← Back
          </button>
          <h1 className="text-3xl font-bold text-gray-900">
            {mode === 'create' ? 'Create New Ticket' : 'Edit Ticket'}
          </h1>
          <p className="text-gray-600 mt-1">
            {mode === 'create'
              ? 'Create a new support ticket'
              : 'Update ticket information'}
          </p>
        </div>

        {/* Error/Success Messages */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}
        {success && (
          <div className="mb-6 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
            {success}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-6 space-y-6">
          {/* Basic Information */}
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Basic Information</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Subject <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  name="subject"
                  value={formData.subject}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Brief description of the issue"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description <span className="text-red-500">*</span>
                </label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  required
                  rows={6}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Detailed description of the issue..."
                />
              </div>
            </div>
          </div>

          {/* Classification */}
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Classification</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Category <span className="text-red-500">*</span>
                </label>
                <select
                  name="category"
                  value={formData.category}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="general">General</option>
                  <option value="technical">Technical</option>
                  <option value="billing">Billing</option>
                  <option value="account">Account</option>
                  <option value="product">Product</option>
                  <option value="complaint">Complaint</option>
                  <option value="feature_request">Feature Request</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Priority <span className="text-red-500">*</span>
                </label>
                <select
                  name="priority"
                  value={formData.priority}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                  <option value="critical">Critical</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Status <span className="text-red-500">*</span>
                </label>
                <select
                  name="status"
                  value={formData.status}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="new">New</option>
                  <option value="open">Open</option>
                  <option value="in_progress">In Progress</option>
                  <option value="pending_customer">Pending Customer</option>
                  <option value="pending_internal">Pending Internal</option>
                  <option value="resolved">Resolved</option>
                  <option value="closed">Closed</option>
                  <option value="cancelled">Cancelled</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Channel <span className="text-red-500">*</span>
                </label>
                <select
                  name="channel"
                  value={formData.channel}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="web">Web</option>
                  <option value="email">Email</option>
                  <option value="phone">Phone</option>
                  <option value="chat">Chat</option>
                  <option value="social_media">Social Media</option>
                  <option value="walk_in">Walk-in</option>
                </select>
              </div>
            </div>
          </div>

          {/* Contact Information */}
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Contact Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Account
                </label>
                <select
                  name="account_id"
                  value={formData.account_id}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select Account</option>
                  {accounts.map((account) => (
                    <option key={account.id} value={account.id}>
                      {account.account_name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Contact Name
                </label>
                <input
                  type="text"
                  name="contact_name"
                  value={formData.contact_name}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="John Doe"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Contact Email
                </label>
                <input
                  type="email"
                  name="contact_email"
                  value={formData.contact_email}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="john@example.com"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Contact Phone
                </label>
                <input
                  type="tel"
                  name="contact_phone"
                  value={formData.contact_phone}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="+91 98765 43210"
                />
              </div>
            </div>
          </div>

          {/* Assignment */}
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Assignment</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Assigned To
                </label>
                <input
                  type="text"
                  name="assigned_to"
                  value={formData.assigned_to}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="User ID or email"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Assigned Team
                </label>
                <input
                  type="text"
                  name="assigned_team"
                  value={formData.assigned_team}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., Support, Technical, Billing"
                />
              </div>
            </div>
          </div>

          {/* Tags */}
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Tags</h2>
            <div className="space-y-3">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={tagInput}
                  onChange={(e) => setTagInput(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault()
                      handleAddTag()
                    }
                  }}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Add a tag and press Enter"
                />
                <button
                  type="button"
                  onClick={handleAddTag}
                  className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                >
                  Add
                </button>
              </div>

              {formData.tags && formData.tags.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {formData.tags.map((tag, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                    >
                      {tag}
                      <button
                        type="button"
                        onClick={() => handleRemoveTag(tag)}
                        className="hover:bg-blue-200 rounded-full p-0.5"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Form Actions */}
          <div className="flex gap-4 pt-4 border-t">
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Saving...' : mode === 'create' ? 'Create Ticket' : 'Update Ticket'}
            </button>
            <button
              type="button"
              onClick={() => router.back()}
              className="px-6 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
