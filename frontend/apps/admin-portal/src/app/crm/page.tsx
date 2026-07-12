'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { 
  Building2, 
  Users, 
  TrendingUp, 
  Network,
  ArrowRight,
  Plus
} from 'lucide-react'
import { crmAccountService } from '@/services/crm-account.service'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'

export default function CRMDashboardPage() {
  const router = useRouter()
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      const response = await crmAccountService.getAccountsSummary()
      if (response.success) {
        setStats(response.data)
      }
    } catch (error: any) {
      toast.error('Failed to load statistics')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">CRM Dashboard</h1>
          <p className="text-muted-foreground">
            Manage accounts, contacts, and customer relationships
          </p>
        </div>
        <Button onClick={() => router.push('/crm/accounts/new')} className="gap-2">
          <Plus className="h-4 w-4" />
          New Account
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Accounts</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_accounts || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Active customer accounts
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Contacts</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_contacts || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Contact persons
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ₹{(stats?.total_revenue || 0).toLocaleString()}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Lifetime value
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Customers</CardTitle>
            <Network className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats?.by_status?.customer || 0}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Current customers
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Account Status Breakdown */}
      {stats?.by_status && (
        <Card>
          <CardHeader>
            <CardTitle>Accounts by Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {Object.entries(stats.by_status).map(([status, count]: [string, any]) => (
                <div key={status} className="text-center p-4 bg-muted rounded-lg">
                  <div className="text-2xl font-bold">{count}</div>
                  <div className="text-sm text-muted-foreground capitalize">
                    {status}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Account Type Breakdown */}
      {stats?.by_type && (
        <Card>
          <CardHeader>
            <CardTitle>Accounts by Type</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {Object.entries(stats.by_type).map(([type, count]: [string, any]) => (
                <div key={type} className="text-center p-4 bg-muted rounded-lg">
                  <div className="text-2xl font-bold">{count}</div>
                  <div className="text-sm text-muted-foreground capitalize">
                    {type.replace('_', ' ')}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => router.push('/crm/accounts')}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Building2 className="h-5 w-5" />
              View All Accounts
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Browse and manage all customer accounts
            </p>
            <Button variant="outline" className="w-full gap-2">
              Go to Accounts
              <ArrowRight className="h-4 w-4" />
            </Button>
          </CardContent>
        </Card>

        <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => router.push('/crm/contacts')}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              Manage Contacts
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              View and manage all contact persons
            </p>
            <Button variant="outline" className="w-full gap-2">
              Go to Contacts
              <ArrowRight className="h-4 w-4" />
            </Button>
          </CardContent>
        </Card>

        <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => router.push('/crm/relationships')}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Network className="h-5 w-5" />
              View Relationships
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Explore account relationships and networks
            </p>
            <Button variant="outline" className="w-full gap-2">
              Go to Relationships
              <ArrowRight className="h-4 w-4" />
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
