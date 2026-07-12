'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { customerServiceApi, SLACreate, SLAUpdate, SLA } from '@/services/customerServiceApi'

interface SLAFormProps {
  slaId?: string
  mode: 'create' | 'edit'
}

export default function SLAForm({ slaId, mode }: SLAFormProps) {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const [formData, setFormData] = useState<SLACreate>({
    name: '',
    description: '',
    status: 'active',
    first_response_time: 60,
    resolution_time: 240,
    use_business_hours: false,
    business_hours_start: '09:00',
    business_hours_end: '18:00',
    business_days: [1, 2, 3, 4, 5], // Monday to Friday
    escalation_enabled: false,
    is_default: false,
    display_order: 0,
  })

  const weekDays = [
    { value: 0, label: 'Sunday' },
    { value: 1, label: 'Monday' },
    { value: 2, label: 'Tuesday' },
    { value: 3, label: 'Wednesday' },
    { value: 4, label: 'Thursday' },
    { value: 5, label: 'Friday' },
    { value: 6, label: 'Saturday' },
  ]

  useEffect(() => {
    if (mode === 'edit' && slaId) {
      loadSLA()
    }
  }, [slaId, mode])

  const loadSLA = async () => {
    if (!slaId) return

    try {
      setLoading(true)
      const response = await customerServiceApi.slas.get(slaId)

      if (response.success) {
        const sla = response.data!
        setFormData({
          name: sla.name,
          description: sla.description || '',
          status: sla.status,
          priority: sla.priority,
          category: sla.category,
          first_response_time: sla.first_response_time,
          resolution_time: sla.resolution_time,
          escalation_time: sla.escalation_time,
          use_business_hours: sla.use_business_hours,
          business_hours_start: sla.business_hours_start,
          business_hours_end: sla.business_hours_end,
          business_days: sla.business_days,
          escalation_enabled: sla.escalation_enabled,
          escalate_to: sla.escalate_to,
          is_default: sla.is_default,
          display_order: sla.display_order,
        })
      } else {
        setError('Failed to load SLA')
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load SLA')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target

    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked
      setFormData((prev) => ({ ...prev, [name]: checked }))
    } else if (type === 'number') {
      setFormData((prev) => ({ ...prev, [name]: parseInt(value) || 0 }))
    } else {
      setFormData((prev) => ({ ...prev, [name]: value || undefined }))
    }
  }

  const handleBusinessDayToggle = (dayValue: number) => {
    setFormData((prev) => {
      const currentDays = prev.business_days || []
      const newDays = currentDays.includes(dayValue)
        ? currentDays.filter((d) => d !== dayValue)
        : [...currentDays, dayValue].sort()
      return { ...prev, business_days: newDays }
    })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setSuccess(null)

    try {
      if (mode === 'create') {
        const response = await customerServiceApi.slas.create(formData)
        if (response.success) {
          setSuccess('SLA created successfully!')
          setTimeout(() => {
            router.push('/crm/slas')
          }, 1500)
        } else {
          setError('Failed to create SLA')
        }
      } else if (mode === 'edit' && slaId) {
        const updateData: SLAUpdate = { ...formData }
        const response = await customerServiceApi.slas.update(slaId, updateData)
        if (response.success) {
          setSuccess('SLA updated successfully!')
          setTimeout(() => {
            router.push('/crm/slas')
          }, 1500)
        } else {
          setError('Failed to update SLA')
        }
      }
    } catch (err: any) {
      setError(err.message || 'Failed to save SLA')
    } finally {
      setLoading(false)
    }
  }

  const formatMinutesToHours = (minutes: number) => {
    return (minutes / 60).toFixed(1)
  }

  const convertHoursToMinutes = (hours: number) => {
    return Math.round(hours * 60)
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="mb-6">
          <button
            onClick={() => router.back()}
            className="text-blue-600 hover:text-blue-700 mb-4 flex items-center"
          >
            ← Back
          </button>
          <h1 className="text-3xl font-bold text-gray-900">
            {mode === 'create' ? 'Create SLA Configuration' : 'Edit SLA Configuration'}
          </h1>
        </div>

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

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Information */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Basic Information</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  SLA Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., Critical Priority SLA"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Describe when this SLA applies..."
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Priority Filter
                  </label>
                  <select
                    name="priority"
                    value={formData.priority || ''}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">All Priorities</option>
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="urgent">Urgent</option>
                    <option value="critical">Critical</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Category Filter
                  </label>
                  <select
                    name="category"
                    value={formData.category || ''}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">All Categories</option>
                    <option value="technical">Technical</option>
                    <option value="billing">Billing</option>
                    <option value="account">Account</option>
                    <option value="product">Product</option>
                    <option value="complaint">Complaint</option>
                    <option value="general">General</option>
                  </select>
                </div>
              </div>

              <div className="flex items-center gap-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    name="is_default"
                    checked={formData.is_default}
                    onChange={handleChange}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm font-medium text-gray-700">
                    Default SLA (applies when no specific SLA matches)
                  </span>
                </label>
              </div>
            </div>
          </div>

          {/* Response Times */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Response Times</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  First Response Time (hours) <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  value={formatMinutesToHours(formData.first_response_time)}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      first_response_time: convertHoursToMinutes(parseFloat(e.target.value) || 0),
                    }))
                  }
                  required
                  min="0"
                  step="0.5"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p className="text-xs text-gray-500 mt-1">
                  {formData.first_response_time} minutes
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Resolution Time (hours) <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  value={formatMinutesToHours(formData.resolution_time)}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      resolution_time: convertHoursToMinutes(parseFloat(e.target.value) || 0),
                    }))
                  }
                  required
                  min="0"
                  step="0.5"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p className="text-xs text-gray-500 mt-1">
                  {formData.resolution_time} minutes
                </p>
              </div>
            </div>
          </div>

          {/* Business Hours */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Business Hours</h2>
            
            <div className="mb-4">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  name="use_business_hours"
                  checked={formData.use_business_hours}
                  onChange={handleChange}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="ml-2 text-sm font-medium text-gray-700">
                  Calculate SLA only during business hours
                </span>
              </label>
            </div>

            {formData.use_business_hours && (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Start Time
                    </label>
                    <input
                      type="time"
                      name="business_hours_start"
                      value={formData.business_hours_start}
                      onChange={handleChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      End Time
                    </label>
                    <input
                      type="time"
                      name="business_hours_end"
                      value={formData.business_hours_end}
                      onChange={handleChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Business Days
                  </label>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                    {weekDays.map((day) => (
                      <label
                        key={day.value}
                        className={`flex items-center justify-center px-4 py-2 border rounded-lg cursor-pointer transition-colors ${
                          formData.business_days?.includes(day.value)
                            ? 'bg-blue-100 border-blue-500 text-blue-700'
                            : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                        }`}
                      >
                        <input
                          type="checkbox"
                          checked={formData.business_days?.includes(day.value)}
                          onChange={() => handleBusinessDayToggle(day.value)}
                          className="sr-only"
                        />
                        <span className="text-sm font-medium">{day.label}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Escalation */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Escalation</h2>
            
            <div className="mb-4">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  name="escalation_enabled"
                  checked={formData.escalation_enabled}
                  onChange={handleChange}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="ml-2 text-sm font-medium text-gray-700">
                  Enable automatic escalation
                </span>
              </label>
            </div>

            {formData.escalation_enabled && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Escalation Time (hours)
                  </label>
                  <input
                    type="number"
                    value={formData.escalation_time ? formatMinutesToHours(formData.escalation_time) : ''}
                    onChange={(e) =>
                      setFormData((prev) => ({
                        ...prev,
                        escalation_time: convertHoursToMinutes(parseFloat(e.target.value) || 0),
                      }))
                    }
                    min="0"
                    step="0.5"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Escalate To (User ID)
                  </label>
                  <input
                    type="text"
                    name="escalate_to"
                    value={formData.escalate_to || ''}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="User ID or email"
                  />
                </div>
              </div>
            )}
          </div>

          {/* Form Actions */}
          <div className="flex gap-4">
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {loading ? 'Saving...' : mode === 'create' ? 'Create SLA' : 'Update SLA'}
            </button>
            <button
              type="button"
              onClick={() => router.back()}
              className="px-6 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
