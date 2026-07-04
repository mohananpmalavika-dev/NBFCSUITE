'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Sparkles, Users, DollarSign, TrendingUp, Activity, LogOut } from 'lucide-react'

export default function DashboardPage() {
  const router = useRouter()
  const [user, setUser] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('access_token')
    const userData = localStorage.getItem('user')

    if (!token || !userData) {
      router.push('/login')
      return
    }

    setUser(JSON.parse(userData))
    setIsLoading(false)
  }, [router])

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    router.push('/login')
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-2">
              <Sparkles className="h-8 w-8 text-blue-600" />
              <span className="text-xl font-bold text-gray-900">NBFC Suite</span>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">
                  {user?.first_name} {user?.last_name}
                </p>
                <p className="text-xs text-gray-500">{user?.email}</p>
              </div>
              <button
                onClick={handleLogout}
                className="inline-flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition"
              >
                <LogOut className="h-4 w-4" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Banner */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl p-8 text-white mb-8">
          <h1 className="text-3xl font-bold mb-2">
            Welcome back, {user?.first_name}! 👋
          </h1>
          <p className="text-blue-100">
            Here's what's happening with your NBFC operations today
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            icon={<Users className="h-6 w-6" />}
            title="Total Customers"
            value="2,543"
            change="+12.5%"
            positive={true}
          />
          <StatCard
            icon={<DollarSign className="h-6 w-6" />}
            title="Total Loans"
            value="₹45.2 Cr"
            change="+8.2%"
            positive={true}
          />
          <StatCard
            icon={<TrendingUp className="h-6 w-6" />}
            title="Collections"
            value="₹12.8 Cr"
            change="+15.3%"
            positive={true}
          />
          <StatCard
            icon={<Activity className="h-6 w-6" />}
            title="NPA Ratio"
            value="2.4%"
            change="-0.5%"
            positive={true}
          />
        </div>

        {/* User Info Card */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Your Account Details</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <InfoRow label="User ID" value={user?.id} />
            <InfoRow label="Username" value={user?.username} />
            <InfoRow label="Email" value={user?.email} />
            <InfoRow label="Phone" value={user?.phone || 'Not provided'} />
            <InfoRow label="Tenant" value={user?.tenant_id} />
            <InfoRow label="Employee Code" value={user?.employee_code || 'N/A'} />
            <InfoRow label="Department" value={user?.department || 'N/A'} />
            <InfoRow label="Designation" value={user?.designation || 'N/A'} />
            <InfoRow 
              label="Status" 
              value={
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  user?.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  {user?.is_active ? 'Active' : 'Inactive'}
                </span>
              } 
            />
            <InfoRow 
              label="Roles" 
              value={user?.roles?.join(', ') || 'No roles assigned'} 
            />
          </div>
        </div>

        {/* Permissions */}
        {user?.permissions && user.permissions.length > 0 && (
          <div className="mt-6 bg-white rounded-xl border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Your Permissions</h2>
            <div className="flex flex-wrap gap-2">
              {user.permissions.map((permission: string, index: number) => (
                <span
                  key={index}
                  className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                >
                  {permission}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Quick Actions */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <ActionCard
            title="Customer Management"
            description="View and manage customer accounts"
            href="/customers"
          />
          <ActionCard
            title="Loan Processing"
            description="Process loan applications"
            href="/loans"
          />
          <ActionCard
            title="Reports"
            description="View analytics and reports"
            href="/reports"
          />
        </div>
      </main>
    </div>
  )
}

function StatCard({ icon, title, value, change, positive }: any) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="p-2 bg-blue-100 rounded-lg text-blue-600">
          {icon}
        </div>
        <span className={`text-sm font-medium ${positive ? 'text-green-600' : 'text-red-600'}`}>
          {change}
        </span>
      </div>
      <h3 className="text-sm font-medium text-gray-600 mb-1">{title}</h3>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
    </div>
  )
}

function InfoRow({ label, value }: any) {
  return (
    <div>
      <dt className="text-sm font-medium text-gray-500">{label}</dt>
      <dd className="mt-1 text-sm text-gray-900">{value}</dd>
    </div>
  )
}

function ActionCard({ title, description, href }: any) {
  return (
    <a
      href={href}
      className="block bg-white rounded-xl border border-gray-200 p-6 hover:border-blue-300 hover:shadow-lg transition"
    >
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-sm text-gray-600">{description}</p>
    </a>
  )
}
