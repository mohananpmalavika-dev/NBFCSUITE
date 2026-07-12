'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { customerServiceApi, Ticket, TicketComment, TicketCommentCreate } from '@/services/customerServiceApi'

interface TicketDetailProps {
  ticketId: string
}

export default function TicketDetail({ ticketId }: TicketDetailProps) {
  const router = useRouter()
  const [ticket, setTicket] = useState<Ticket | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [commentText, setCommentText] = useState('')
  const [isInternal, setIsInternal] = useState(false)
  const [submittingComment, setSubmittingComment] = useState(false)

  useEffect(() => {
    loadTicket()
  }, [ticketId])

  const loadTicket = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await customerServiceApi.tickets.get(ticketId)

      if (response.success) {
        setTicket(response.data!)
      } else {
        setError('Failed to load ticket')
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load ticket')
    } finally {
      setLoading(false)
    }
  }

  const handleAddComment = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!commentText.trim()) return

    try {
      setSubmittingComment(true)
      const commentData: TicketCommentCreate = {
        ticket_id: ticketId,
        content: commentText,
        is_internal: isInternal,
      }

      const response = await customerServiceApi.tickets.addComment(ticketId, commentData)

      if (response.success) {
        setCommentText('')
        setIsInternal(false)
        await loadTicket() // Reload to get updated comments
      } else {
        alert('Failed to add comment')
      }
    } catch (err: any) {
      alert(err.message || 'Failed to add comment')
    } finally {
      setSubmittingComment(false)
    }
  }

  const handleStatusUpdate = async (newStatus: string) => {
    if (!ticket) return

    try {
      const response = await customerServiceApi.tickets.update(ticketId, {
        status: newStatus as any,
      })

      if (response.success) {
        setTicket(response.data!)
      } else {
        alert('Failed to update ticket status')
      }
    } catch (err: any) {
      alert(err.message || 'Failed to update ticket status')
    }
  }

  const getPriorityBadge = (priority: string) => {
    const colors: Record<string, string> = {
      low: 'bg-gray-100 text-gray-800',
      medium: 'bg-blue-100 text-blue-800',
      high: 'bg-yellow-100 text-yellow-800',
      urgent: 'bg-orange-100 text-orange-800',
      critical: 'bg-red-100 text-red-800',
    }
    return colors[priority] || 'bg-gray-100 text-gray-800'
  }

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      new: 'bg-purple-100 text-purple-800',
      open: 'bg-blue-100 text-blue-800',
      in_progress: 'bg-yellow-100 text-yellow-800',
      pending_customer: 'bg-orange-100 text-orange-800',
      pending_internal: 'bg-pink-100 text-pink-800',
      resolved: 'bg-green-100 text-green-800',
      closed: 'bg-gray-100 text-gray-800',
      cancelled: 'bg-red-100 text-red-800',
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading ticket...</p>
        </div>
      </div>
    )
  }

  if (error || !ticket) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error || 'Ticket not found'}
          </div>
          <button
            onClick={() => router.push('/crm/tickets')}
            className="mt-4 text-blue-600 hover:text-blue-700"
          >
            ← Back to Tickets
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => router.push('/crm/tickets')}
            className="text-blue-600 hover:text-blue-700 mb-4 flex items-center"
          >
            ← Back to Tickets
          </button>
          
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{ticket.ticket_number}</h1>
              <p className="text-gray-600 mt-1">{ticket.subject}</p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => router.push(`/crm/tickets/${ticketId}/edit`)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Edit
              </button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Ticket Details */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Description</h2>
              <div className="prose max-w-none">
                <p className="text-gray-700 whitespace-pre-wrap">{ticket.description}</p>
              </div>

              {/* Contact Information */}
              {(ticket.contact_name || ticket.contact_email || ticket.contact_phone) && (
                <div className="mt-6 pt-6 border-t">
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Contact Information</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {ticket.contact_name && (
                      <div>
                        <span className="text-sm text-gray-600">Name:</span>
                        <p className="font-medium">{ticket.contact_name}</p>
                      </div>
                    )}
                    {ticket.contact_email && (
                      <div>
                        <span className="text-sm text-gray-600">Email:</span>
                        <p className="font-medium">{ticket.contact_email}</p>
                      </div>
                    )}
                    {ticket.contact_phone && (
                      <div>
                        <span className="text-sm text-gray-600">Phone:</span>
                        <p className="font-medium">{ticket.contact_phone}</p>
                      </div>
                    )}
                    {ticket.account_name && (
                      <div>
                        <span className="text-sm text-gray-600">Account:</span>
                        <p className="font-medium">{ticket.account_name}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Comments Section */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Comments ({ticket.comments?.length || 0})
              </h2>

              {/* Comment List */}
              <div className="space-y-4 mb-6">
                {ticket.comments && ticket.comments.length > 0 ? (
                  ticket.comments.map((comment) => (
                    <div
                      key={comment.id}
                      className={`p-4 rounded-lg ${
                        comment.is_internal
                          ? 'bg-yellow-50 border border-yellow-200'
                          : comment.is_system
                          ? 'bg-gray-50 border border-gray-200'
                          : 'bg-blue-50 border border-blue-200'
                      }`}
                    >
                      <div className="flex justify-between items-start mb-2">
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-gray-900">
                            {comment.created_by || 'System'}
                          </span>
                          {comment.is_internal && (
                            <span className="text-xs px-2 py-1 bg-yellow-200 text-yellow-800 rounded-full">
                              Internal
                            </span>
                          )}
                          {comment.is_system && (
                            <span className="text-xs px-2 py-1 bg-gray-200 text-gray-800 rounded-full">
                              System
                            </span>
                          )}
                        </div>
                        <span className="text-sm text-gray-600">
                          {formatDate(comment.created_at)}
                        </span>
                      </div>
                      <p className="text-gray-700 whitespace-pre-wrap">{comment.content}</p>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-500 text-center py-4">No comments yet</p>
                )}
              </div>

              {/* Add Comment Form */}
              <form onSubmit={handleAddComment} className="border-t pt-6">
                <div className="mb-3">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Add Comment
                  </label>
                  <textarea
                    value={commentText}
                    onChange={(e) => setCommentText(e.target.value)}
                    rows={4}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Write your comment..."
                    required
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      checked={isInternal}
                      onChange={(e) => setIsInternal(e.target.checked)}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label className="ml-2 text-sm text-gray-700">
                      Internal comment (not visible to customer)
                    </label>
                  </div>

                  <button
                    type="submit"
                    disabled={submittingComment}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {submittingComment ? 'Adding...' : 'Add Comment'}
                  </button>
                </div>
              </form>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Status Card */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Status</h3>
              
              <div className="space-y-3">
                <div>
                  <label className="block text-sm text-gray-600 mb-1">Current Status</label>
                  <span className={`inline-block text-xs px-3 py-1 rounded-full ${getStatusBadge(ticket.status)}`}>
                    {ticket.status.replace('_', ' ').toUpperCase()}
                  </span>
                </div>

                <div>
                  <label className="block text-sm text-gray-600 mb-1">Update Status</label>
                  <select
                    value={ticket.status}
                    onChange={(e) => handleStatusUpdate(e.target.value)}
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
              </div>
            </div>

            {/* Details Card */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Details</h3>
              
              <div className="space-y-3">
                <div>
                  <span className="text-sm text-gray-600">Priority</span>
                  <div className="mt-1">
                    <span className={`text-xs px-3 py-1 rounded-full ${getPriorityBadge(ticket.priority)}`}>
                      {ticket.priority.toUpperCase()}
                    </span>
                  </div>
                </div>

                <div>
                  <span className="text-sm text-gray-600">Category</span>
                  <p className="font-medium capitalize">{ticket.category}</p>
                </div>

                <div>
                  <span className="text-sm text-gray-600">Channel</span>
                  <p className="font-medium capitalize">{ticket.channel}</p>
                </div>

                {ticket.assigned_to_name && (
                  <div>
                    <span className="text-sm text-gray-600">Assigned To</span>
                    <p className="font-medium">{ticket.assigned_to_name}</p>
                  </div>
                )}

                {ticket.assigned_team && (
                  <div>
                    <span className="text-sm text-gray-600">Team</span>
                    <p className="font-medium">{ticket.assigned_team}</p>
                  </div>
                )}

                {ticket.tags && ticket.tags.length > 0 && (
                  <div>
                    <span className="text-sm text-gray-600">Tags</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {ticket.tags.map((tag, index) => (
                        <span
                          key={index}
                          className="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded-full"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* SLA Card */}
            {(ticket.first_response_due || ticket.resolution_due) && (
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">SLA</h3>
                
                {ticket.sla_breached && (
                  <div className="mb-3 px-3 py-2 bg-red-100 text-red-800 rounded-lg text-sm font-medium">
                    ⚠️ SLA Breached
                  </div>
                )}

                <div className="space-y-3">
                  {ticket.first_response_due && (
                    <div>
                      <span className="text-sm text-gray-600">First Response Due</span>
                      <p className="font-medium text-sm">{formatDate(ticket.first_response_due)}</p>
                      {ticket.first_response_at && (
                        <p className="text-xs text-green-600 mt-1">
                          Responded at {formatDate(ticket.first_response_at)}
                        </p>
                      )}
                    </div>
                  )}

                  {ticket.resolution_due && (
                    <div>
                      <span className="text-sm text-gray-600">Resolution Due</span>
                      <p className="font-medium text-sm">{formatDate(ticket.resolution_due)}</p>
                      {ticket.resolved_at && (
                        <p className="text-xs text-green-600 mt-1">
                          Resolved at {formatDate(ticket.resolved_at)}
                        </p>
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Timestamps Card */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Timestamps</h3>
              
              <div className="space-y-3 text-sm">
                <div>
                  <span className="text-gray-600">Created</span>
                  <p className="font-medium">{formatDate(ticket.created_at)}</p>
                </div>

                <div>
                  <span className="text-gray-600">Last Updated</span>
                  <p className="font-medium">{formatDate(ticket.updated_at)}</p>
                </div>

                {ticket.closed_at && (
                  <div>
                    <span className="text-gray-600">Closed</span>
                    <p className="font-medium">{formatDate(ticket.closed_at)}</p>
                  </div>
                )}
              </div>
            </div>

            {/* Satisfaction Rating */}
            {ticket.satisfaction_rating && (
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Customer Satisfaction</h3>
                
                <div className="flex items-center gap-1 mb-2">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <svg
                      key={star}
                      className={`w-6 h-6 ${
                        star <= ticket.satisfaction_rating!
                          ? 'text-yellow-400'
                          : 'text-gray-300'
                      }`}
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  ))}
                </div>

                {ticket.satisfaction_comment && (
                  <p className="text-sm text-gray-700 mt-2">{ticket.satisfaction_comment}</p>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
