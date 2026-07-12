'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { crmApi, Account360View } from '@/services/crmApi'

interface Account360ViewProps {
  accountId: string
}

export default function Account360ViewComponent({ accountId }: Account360ViewProps) {
  const router = useRouter()
  const [data, setData] = useState<Account360View | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState('overview')

  useEffect(() => {
    loadAccountData()
  }, [accountId])

  const loadAccountData = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await crmApi.accounts.get360(accountId)
      if (response.success) {
        setData(response.data)
      } else {
        setError('Failed to load account data')
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load account data')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading account data...</p>
        </div>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="text-red-600 text-xl mb-4">⚠️ Error</div>
          <p className="text-gray-600">{error || 'No data available'}</p>
          <button
            onClick={loadAccountData}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  const { account, contacts, relationships, recent_activities, child_accounts, metrics } = data

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header Section */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex justify-between items-start">
          <div className="flex-1">
            <div className="flex items-center gap-4 mb-2">
              <button
                onClick={() => router.push('/crm/accounts')}
                className="text-gray-600 hover:text-gray-800"
              >
                ← Back
              </button>
              <h1 className="text-3xl font-bold text-gray-900">{account.account_name}</h1>
              <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                account.status === 'active' ? 'bg-green-100 text-green-800' :
                account.status === 'prospect' ? 'bg-yellow-100 text-yellow-800' :
                account.status === 'customer' ? 'bg-blue-100 text-blue-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {account.status.toUpperCase()}
              </span>
            </div>
            <p className="text-gray-600 mb-2">Account Number: {account.account_number}</p>
            <div className="flex gap-4 text-sm text-gray-600">
              <span>Type: {account.account_type}</span>
              {account.industry && <span>• Industry: {account.industry}</span>}
              {account.employee_count && <span>• Employees: {account.employee_count}</span>}
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => router.push(`/crm/accounts/${accountId}/edit`)}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Edit Account
            </button>
            <button
              onClick={() => router.push(`/crm/accounts/${accountId}/contacts/new`)}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            >
              Add Contact
            </button>
          </div>
        </div>

        {/* Metrics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mt-6">
          <div className="bg-blue-50 p-4 rounded-lg">
            <p className="text-sm text-blue-600 font-semibold">Total Revenue</p>
            <p className="text-2xl font-bold text-blue-900">
              ₹{metrics.total_revenue.toLocaleString()}
            </p>
          </div>
          <div className="bg-purple-50 p-4 rounded-lg">
            <p className="text-sm text-purple-600 font-semibold">Opportunities</p>
            <p className="text-2xl font-bold text-purple-900">{metrics.opportunities_count}</p>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <p className="text-sm text-green-600 font-semibold">Contacts</p>
            <p className="text-2xl font-bold text-green-900">{metrics.total_contacts}</p>
          </div>
          <div className="bg-orange-50 p-4 rounded-lg">
            <p className="text-sm text-orange-600 font-semibold">Relationships</p>
            <p className="text-2xl font-bold text-orange-900">{metrics.total_relationships}</p>
          </div>
          <div className="bg-indigo-50 p-4 rounded-lg">
            <p className="text-sm text-indigo-600 font-semibold">Child Accounts</p>
            <p className="text-2xl font-bold text-indigo-900">{metrics.total_child_accounts}</p>
          </div>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="bg-white rounded-t-lg shadow-md">
        <div className="flex border-b">
          {[
            { id: 'overview', label: 'Overview' },
            { id: 'contacts', label: `Contacts (${contacts.length})` },
            { id: 'relationships', label: `Relationships (${relationships.length})` },
            { id: 'activities', label: 'Activities' },
            { id: 'child-accounts', label: `Child Accounts (${child_accounts.length})` },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-6 py-3 font-semibold ${
                activeTab === tab.id
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="bg-white rounded-b-lg shadow-md p-6">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Account Details */}
            <div>
              <h3 className="text-xl font-bold mb-4">Account Details</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {account.email && (
                  <div>
                    <p className="text-sm text-gray-600">Email</p>
                    <p className="font-semibold">{account.email}</p>
                  </div>
                )}
                {account.phone && (
                  <div>
                    <p className="text-sm text-gray-600">Phone</p>
                    <p className="font-semibold">{account.phone}</p>
                  </div>
                )}
                {account.website && (
                  <div>
                    <p className="text-sm text-gray-600">Website</p>
                    <a href={account.website} target="_blank" rel="noopener noreferrer" className="font-semibold text-blue-600 hover:underline">
                      {account.website}
                    </a>
                  </div>
                )}
                {account.pan_number && (
                  <div>
                    <p className="text-sm text-gray-600">PAN Number</p>
                    <p className="font-semibold">{account.pan_number}</p>
                  </div>
                )}
                {account.gst_number && (
                  <div>
                    <p className="text-sm text-gray-600">GST Number</p>
                    <p className="font-semibold">{account.gst_number}</p>
                  </div>
                )}
                {account.annual_revenue && (
                  <div>
                    <p className="text-sm text-gray-600">Annual Revenue</p>
                    <p className="font-semibold">₹{account.annual_revenue.toLocaleString()}</p>
                  </div>
                )}
              </div>
            </div>

            {/* Billing Address */}
            {account.billing_address_line1 && (
              <div>
                <h3 className="text-xl font-bold mb-4">Billing Address</h3>
                <div className="text-gray-700">
                  <p>{account.billing_address_line1}</p>
                  {account.billing_address_line2 && <p>{account.billing_address_line2}</p>}
                  <p>{account.billing_city}, {account.billing_state} {account.billing_pincode}</p>
                  <p>{account.billing_country}</p>
                </div>
              </div>
            )}

            {/* Description */}
            {account.description && (
              <div>
                <h3 className="text-xl font-bold mb-4">Description</h3>
                <p className="text-gray-700">{account.description}</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'contacts' && (
          <div>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold">Contacts</h3>
              <button
                onClick={() => router.push(`/crm/accounts/${accountId}/contacts/new`)}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Add Contact
              </button>
            </div>
            {contacts.length === 0 ? (
              <p className="text-gray-600 text-center py-8">No contacts found</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Title</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Phone</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {contacts.map((contact) => (
                      <tr key={contact.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="font-medium text-gray-900">{contact.full_name}</div>
                          <div className="text-sm text-gray-500">{contact.contact_number}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{contact.job_title || '-'}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{contact.email || '-'}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{contact.mobile || contact.phone || '-'}</td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                            {contact.contact_type}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                            contact.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                          }`}>
                            {contact.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <button
                            onClick={() => router.push(`/crm/contacts/${contact.id}`)}
                            className="text-blue-600 hover:text-blue-800 mr-3"
                          >
                            View
                          </button>
                          <button
                            onClick={() => router.push(`/crm/contacts/${contact.id}/edit`)}
                            className="text-green-600 hover:text-green-800"
                          >
                            Edit
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {activeTab === 'relationships' && (
          <div>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold">Account Relationships</h3>
              <button
                onClick={() => router.push(`/crm/accounts/${accountId}/relationships/new`)}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Add Relationship
              </button>
            </div>
            {relationships.length === 0 ? (
              <p className="text-gray-600 text-center py-8">No relationships found</p>
            ) : (
              <div className="space-y-4">
                {relationships.map((rel) => (
                  <div key={rel.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex justify-between items-start">
                      <div>
                        <span className="px-3 py-1 bg-purple-100 text-purple-800 text-sm font-semibold rounded-full">
                          {rel.relationship_type.replace('_', ' ').toUpperCase()}
                        </span>
                        {rel.relationship_description && (
                          <p className="mt-2 text-gray-700">{rel.relationship_description}</p>
                        )}
                        {rel.strength && (
                          <p className="mt-1 text-sm text-gray-600">Strength: {rel.strength}</p>
                        )}
                      </div>
                      <button
                        onClick={() => router.push(`/crm/relationships/${rel.id}/edit`)}
                        className="text-blue-600 hover:text-blue-800"
                      >
                        Edit
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'activities' && (
          <div>
            <h3 className="text-xl font-bold mb-4">Recent Activities</h3>
            {recent_activities.length === 0 ? (
              <p className="text-gray-600 text-center py-8">No activities found</p>
            ) : (
              <div className="space-y-4">
                {recent_activities.map((activity) => (
                  <div key={activity.id} className="border-l-4 border-blue-500 pl-4 py-2">
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="font-semibold text-gray-900">{activity.subject}</h4>
                        <p className="text-sm text-gray-600">Type: {activity.activity_type}</p>
                        <p className="text-sm text-gray-600">Date: {new Date(activity.activity_date).toLocaleDateString()}</p>
                        {activity.description && (
                          <p className="mt-2 text-gray-700">{activity.description}</p>
                        )}
                      </div>
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                        activity.status === 'completed' ? 'bg-green-100 text-green-800' :
                        activity.status === 'planned' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {activity.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'child-accounts' && (
          <div>
            <h3 className="text-xl font-bold mb-4">Child Accounts</h3>
            {child_accounts.length === 0 ? (
              <p className="text-gray-600 text-center py-8">No child accounts found</p>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {child_accounts.map((childAccount) => (
                  <div
                    key={childAccount.id}
                    className="border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                    onClick={() => router.push(`/crm/accounts/${childAccount.id}`)}
                  >
                    <h4 className="font-semibold text-lg text-gray-900">{childAccount.account_name}</h4>
                    <p className="text-sm text-gray-600">{childAccount.account_number}</p>
                    <div className="mt-2 flex gap-2">
                      <span className="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                        {childAccount.account_type}
                      </span>
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                        childAccount.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                      }`}>
                        {childAccount.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
