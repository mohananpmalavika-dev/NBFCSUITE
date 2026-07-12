'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { customerServiceApi, TicketStats } from '@/services/customerServiceApi'

export default function ServiceDashboard() {
  const router = useRouter()
  const [stats, setStats] = useState<TicketStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await customerServiceApi.tickets.getStats()

      if (response.success && response.data) {
        setStats(response.data)
      } else {
        setError('Failed to load statistics')
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load statistics')
    } finally {
      setLoading(false)
    }
  }

  const formatTime = (minutes?: number) => {
    if (!minutes) return 'N/A'
    if (minutes < 60) return `${Math.round(minutes)}m`
    const hours = Math.floor(minutes / 60)
    const mins = Math.round(minutes % 60)
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  if (error || !stats) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error || 'Failed to load dashboard'}
        </div>
      </div>
    )
  }

  const statCards = [
    {
      title: 'Total Tickets',
      value: stats.total_tickets,
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      ),
      color: 'bg-blue-500',
      textColor: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      title: 'New Tickets',
      value: stats.new_tickets,
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
      ),
      color: 'bg-purple-500',
      textColor: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
    {
      title: 'Open Tickets',
      value: stats.open_tickets,
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      ),
      color: 'bg-blue-500',
      textColor: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      title: 'In Progress',
      value: stats.in_progress_tickets,
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      ),
      color: 'bg-yellow-500',
      textColor: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
    },
    {
      title: 'Pending',
      value: stats.pending_tickets,
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      color: 'bg-orange-500',
      textColor: 'text-orange-600',
      bgColor: 'bg-orange-50',
    },
    {
      title: 'Resolved',
      value: stats.resolved_tickets,
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      color: 'bg-green-500',
      textColor: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      title: 'Closed',
      value: stats.closed_tickets,
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
      ),
      color: 'bg-gray-500',
      textColor: 'text-gray-600',
      bgColor: 'bg-gray-50',
    },
    {
      title: 'SLA Breached',
      value: stats.sla_breached_tickets,
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      ),
      color: 'bg-red-500',
      textColor: 'text-red-600',
      bgColor: 'bg-red-50',
    },
  ]

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Customer Service Dashboard</h1>
        <p className="text-gray-600 mt-1">Overview of support operations and performance</p>
      </div>

      {/* Quick Actions */}
      <div className="mb-6 bg-white rounded-lg shadow p-4">
        <div className="flex gap-3">
          <button
            onClick={() => router.push('/crm/tickets/new')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            + New Ticket
          </button>
          <button
            onClick={() => router.push('/crm/tickets')}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
          >
            View All Tickets
          </button>
          <button
            onClick={() => router.push('/crm/tickets/board')}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
          >
            Kanban Board
          </button>
          <button
            onClick={() => router.push('/crm/knowledge')}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
          >
            Knowledge Base
          </button>
          <button
            onClick={() => router.push('/crm/slas')}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
          >
            SLA Config
          </button>
        </div>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        {statCards.map((card, index) => (
          <div key={index} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <div className={`p-3 rounded-lg ${card.bgColor}`}>
                <div className={card.textColor}>{card.icon}</div>
              </div>
            </div>
            <h3 className="text-2xl font-bold text-gray-900">{card.value}</h3>
            <p className="text-gray-600 text-sm mt-1">{card.title}</p>
          </div>
        ))}
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 rounded-lg bg-blue-50">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900">Avg. First Response</h3>
          </div>
          <p className="text-3xl font-bold text-blue-600">
            {formatTime(stats.avg_first_response_time)}
          </p>
          <p className="text-sm text-gray-500 mt-2">Time to first customer response</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 rounded-lg bg-green-50">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900">Avg. Resolution Time</h3>
          </div>
          <p className="text-3xl font-bold text-green-600">
            {formatTime(stats.avg_resolution_time)}
          </p>
          <p className="text-sm text-gray-500 mt-2">Time to close tickets</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 rounded-lg bg-yellow-50">
              <svg className="w-6 h-6 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900">Customer Satisfaction</h3>
          </div>
          <p className="text-3xl font-bold text-yellow-600">
            {stats.avg_satisfaction_rating?.toFixed(1) || 'N/A'}
          </p>
          <p className="text-sm text-gray-500 mt-2">Average rating out of 5</p>
        </div>
      </div>

      {/* Ticket Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Status Distribution */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Ticket Status Distribution</h3>
          <div className="space-y-3">
            {[
              { label: 'New', value: stats.new_tickets, total: stats.total_tickets, color: 'bg-purple-500' },
              { label: 'Open', value: stats.open_tickets, total: stats.total_tickets, color: 'bg-blue-500' },
              { label: 'In Progress', value: stats.in_progress_tickets, total: stats.total_tickets, color: 'bg-yellow-500' },
              { label: 'Pending', value: stats.pending_tickets, total: stats.total_tickets, color: 'bg-orange-500' },
              { label: 'Resolved', value: stats.resolved_tickets, total: stats.total_tickets, color: 'bg-green-500' },
              { label: 'Closed', value: stats.closed_tickets, total: stats.total_tickets, color: 'bg-gray-500' },
            ].map((item, index) => {
              const percentage = item.total > 0 ? (item.value / item.total) * 100 : 0
              return (
                <div key={index}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-700">{item.label}</span>
                    <span className="text-gray-900 font-medium">
                      {item.value} ({percentage.toFixed(0)}%)
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`${item.color} h-2 rounded-full transition-all`}
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* SLA Performance */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">SLA Performance</h3>
          <div className="space-y-4">
            <div className="text-center p-6 bg-gradient-to-br from-green-50 to-blue-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-2">SLA Compliance Rate</p>
              <p className="text-4xl font-bold text-green-600">
                {stats.total_tickets > 0
                  ? (((stats.total_tickets - stats.sla_breached_tickets) / stats.total_tickets) * 100).toFixed(1)
                  : '0'}%
              </p>
              <p className="text-sm text-gray-500 mt-2">
                {stats.total_tickets - stats.sla_breached_tickets} of {stats.total_tickets} tickets met SLA
              </p>
            </div>

            {stats.sla_breached_tickets > 0 && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <h4 className="font-semibold text-red-900">SLA Breaches</h4>
                </div>
                <p className="text-2xl font-bold text-red-600">{stats.sla_breached_tickets}</p>
                <p className="text-sm text-red-700 mt-1">Tickets require immediate attention</p>
                <button
                  onClick={() => router.push('/crm/tickets?sla_breached=true')}
                  className="mt-3 text-sm text-red-600 hover:text-red-700 font-medium"
                >
                  View Breached Tickets →
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Help Text */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <svg className="w-5 h-5 text-blue-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h4 className="font-semibold text-blue-900 mb-1">Dashboard Tips</h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Monitor SLA breaches closely and prioritize urgent tickets</li>
              <li>• Track average response and resolution times to improve efficiency</li>
              <li>• Review customer satisfaction ratings to identify improvement areas</li>
              <li>• Use the Kanban board for visual ticket management</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
