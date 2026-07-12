'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { customerServiceApi, Ticket, TicketStatus } from '@/services/customerServiceApi'

export default function TicketBoard() {
  const router = useRouter()
  const [tickets, setTickets] = useState<Ticket[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const columns: { status: TicketStatus; title: string; color: string }[] = [
    { status: 'new', title: 'New', color: 'border-purple-300 bg-purple-50' },
    { status: 'open', title: 'Open', color: 'border-blue-300 bg-blue-50' },
    { status: 'in_progress', title: 'In Progress', color: 'border-yellow-300 bg-yellow-50' },
    { status: 'pending_customer', title: 'Pending Customer', color: 'border-orange-300 bg-orange-50' },
    { status: 'resolved', title: 'Resolved', color: 'border-green-300 bg-green-50' },
  ]

  useEffect(() => {
    loadTickets()
  }, [])

  const loadTickets = async () => {
    try {
      setLoading(true)
      setError(null)

      // Load all active tickets
      const response = await customerServiceApi.tickets.list({
        limit: 1000,
      })

      if (response.success && response.data) {
        setTickets(response.data.tickets)
      } else {
        setError('Failed to load tickets')
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load tickets')
    } finally {
      setLoading(false)
    }
  }

  const getTicketsByStatus = (status: TicketStatus) => {
    return tickets.filter((ticket) => ticket.status === status)
  }

  const handleStatusChange = async (ticketId: string, newStatus: TicketStatus) => {
    try {
      const response = await customerServiceApi.tickets.update(ticketId, {
        status: newStatus,
      })

      if (response.success) {
        // Update local state
        setTickets((prev) =>
          prev.map((ticket) =>
            ticket.id === ticketId ? { ...ticket, status: newStatus } : ticket
          )
        )
      } else {
        alert('Failed to update ticket status')
      }
    } catch (err: any) {
      alert(err.message || 'Failed to update ticket status')
    }
  }

  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      low: 'bg-gray-500',
      medium: 'bg-blue-500',
      high: 'bg-yellow-500',
      urgent: 'bg-orange-500',
      critical: 'bg-red-500',
    }
    return colors[priority] || 'bg-gray-500'
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      month: 'short',
      day: 'numeric',
    })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading ticket board...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Ticket Board</h1>
            <p className="text-gray-600 mt-1">Kanban view of support tickets</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => router.push('/crm/tickets')}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
            >
              List View
            </button>
            <button
              onClick={() => router.push('/crm/tickets/new')}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              + Create Ticket
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Kanban Board */}
      <div className="flex gap-4 overflow-x-auto pb-4">
        {columns.map((column) => {
          const columnTickets = getTicketsByStatus(column.status)
          return (
            <div key={column.status} className="flex-shrink-0 w-80">
              <div className={`rounded-lg border-2 ${column.color} h-full`}>
                {/* Column Header */}
                <div className="p-4 border-b border-gray-300">
                  <div className="flex justify-between items-center">
                    <h2 className="font-semibold text-gray-900">{column.title}</h2>
                    <span className="px-2 py-1 bg-white rounded-full text-sm font-medium text-gray-700">
                      {columnTickets.length}
                    </span>
                  </div>
                </div>

                {/* Column Content */}
                <div className="p-4 space-y-3 max-h-[calc(100vh-250px)] overflow-y-auto">
                  {columnTickets.map((ticket) => (
                    <div
                      key={ticket.id}
                      className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow cursor-pointer"
                      onClick={() => router.push(`/crm/tickets/${ticket.id}`)}
                    >
                      {/* Ticket Header */}
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1">
                          <div className="text-xs font-medium text-gray-500 mb-1">
                            {ticket.ticket_number}
                          </div>
                          <h3 className="font-medium text-gray-900 text-sm leading-tight">
                            {ticket.subject}
                          </h3>
                        </div>
                        <div
                          className={`w-2 h-2 rounded-full ${getPriorityColor(ticket.priority)} flex-shrink-0 ml-2 mt-1`}
                          title={`Priority: ${ticket.priority}`}
                        />
                      </div>

                      {/* Ticket Details */}
                      <div className="space-y-2 text-xs text-gray-600">
                        {ticket.contact_name && (
                          <div className="flex items-center gap-1">
                            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                            </svg>
                            <span className="truncate">{ticket.contact_name}</span>
                          </div>
                        )}

                        <div className="flex items-center gap-1">
                          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                          </svg>
                          <span className="capitalize">{ticket.category}</span>
                        </div>

                        <div className="flex items-center gap-1">
                          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                          </svg>
                          <span>{formatDate(ticket.created_at)}</span>
                        </div>
                      </div>

                      {/* SLA Warning */}
                      {ticket.sla_breached && (
                        <div className="mt-2 px-2 py-1 bg-red-100 text-red-800 rounded text-xs font-medium">
                          ⚠️ SLA Breached
                        </div>
                      )}

                      {/* Tags */}
                      {ticket.tags && ticket.tags.length > 0 && (
                        <div className="mt-2 flex flex-wrap gap-1">
                          {ticket.tags.slice(0, 2).map((tag, index) => (
                            <span
                              key={index}
                              className="px-2 py-0.5 bg-gray-100 text-gray-700 rounded-full text-xs"
                            >
                              {tag}
                            </span>
                          ))}
                          {ticket.tags.length > 2 && (
                            <span className="px-2 py-0.5 bg-gray-100 text-gray-700 rounded-full text-xs">
                              +{ticket.tags.length - 2}
                            </span>
                          )}
                        </div>
                      )}

                      {/* Status Actions */}
                      <div className="mt-3 pt-3 border-t border-gray-100">
                        <select
                          value={ticket.status}
                          onChange={(e) => {
                            e.stopPropagation()
                            handleStatusChange(ticket.id, e.target.value as TicketStatus)
                          }}
                          onClick={(e) => e.stopPropagation()}
                          className="w-full text-xs px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                        >
                          <option value="new">New</option>
                          <option value="open">Open</option>
                          <option value="in_progress">In Progress</option>
                          <option value="pending_customer">Pending Customer</option>
                          <option value="pending_internal">Pending Internal</option>
                          <option value="resolved">Resolved</option>
                          <option value="closed">Closed</option>
                        </select>
                      </div>
                    </div>
                  ))}

                  {columnTickets.length === 0 && (
                    <div className="text-center py-8 text-gray-400 text-sm">
                      No tickets
                    </div>
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Legend */}
      <div className="mt-6 bg-white rounded-lg shadow p-4">
        <h3 className="text-sm font-semibold text-gray-900 mb-2">Priority Legend</h3>
        <div className="flex flex-wrap gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-gray-500"></div>
            <span className="text-gray-700">Low</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-blue-500"></div>
            <span className="text-gray-700">Medium</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
            <span className="text-gray-700">High</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-orange-500"></div>
            <span className="text-gray-700">Urgent</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-red-500"></div>
            <span className="text-gray-700">Critical</span>
          </div>
        </div>
      </div>
    </div>
  )
}
