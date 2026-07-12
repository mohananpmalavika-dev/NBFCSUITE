'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { customerServiceApi, SLA } from '@/services/customerServiceApi'

export default function SLAList() {
  const router = useRouter()
  const [slas, setSlas] = useState<SLA[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadSLAs()
  }, [])

  const loadSLAs = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await customerServiceApi.slas.list({ limit: 100 })

      if (response.success && response.data) {
        setSlas(response.data.slas)
      } else {
        setError('Failed to load SLAs')
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load SLAs')
    } finally {
      setLoading(false)
    }
  }

  const formatTime = (minutes: number) => {
    if (minutes < 60) return `${minutes}m`
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading SLAs...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="mb-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">SLA Configurations</h1>
            <p className="text-gray-600 mt-1">Manage service level agreements</p>
          </div>
          <button
            onClick={() => router.push('/crm/slas/new')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            + Create SLA
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Priority</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">First Response</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Resolution</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {slas.map((sla) => (
              <tr key={sla.id} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <div className="font-medium text-gray-900">{sla.name}</div>
                  {sla.is_default && (
                    <span className="inline-block text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded-full mt-1">
                      Default
                    </span>
                  )}
                </td>
                <td className="px-6 py-4">
                  <span className="capitalize">{sla.priority || 'All'}</span>
                </td>
                <td className="px-6 py-4">{formatTime(sla.first_response_time)}</td>
                <td className="px-6 py-4">{formatTime(sla.resolution_time)}</td>
                <td className="px-6 py-4">
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    sla.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {sla.status.toUpperCase()}
                  </span>
                </td>
                <td className="px-6 py-4 text-right">
                  <button
                    onClick={() => router.push(`/crm/slas/${sla.id}/edit`)}
                    className="text-blue-600 hover:text-blue-900"
                  >
                    Edit
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {slas.length === 0 && !loading && (
        <div className="bg-white rounded-lg shadow p-12 text-center mt-6">
          <h3 className="text-lg font-medium text-gray-900 mb-2">No SLAs configured</h3>
          <button
            onClick={() => router.push('/crm/slas/new')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Create SLA
          </button>
        </div>
      )}
    </div>
  )
}
