'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { 
  Megaphone, 
  Users, 
  FileText, 
  TrendingUp,
  ArrowRight,
  Plus,
  Mail,
  MessageSquare
} from 'lucide-react'
import { crmMarketingService, type MarketingStats } from '@/services/crm-marketing.service'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'

export function MarketingDashboard() {
  const router = useRouter()
  const [stats, setStats] = useState<MarketingStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      const response = await crmMarketingService.getMarketingStats()
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
          <h1 className="text-3xl font-bold tracking-tight">Marketing Automation</h1>
          <p className="text-muted-foreground">
            Manage campaigns, segments, and landing pages
          </p>
        </div>
        <Button onClick={() => router.push('/crm/marketing/campaigns/new')} className="gap-2">
          <Plus className="h-4 w-4" />
          New Campaign
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Campaigns</CardTitle>
            <Megaphone className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_campaigns || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">
              All time campaigns
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Campaigns</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.active_campaigns || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Currently running
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Customer Segments</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_segments || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Targeted audiences
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Landing Pages</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_landing_pages || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Conversion pages
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Campaign Status Breakdown */}
      {stats?.by_status && Object.keys(stats.by_status).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Campaigns by Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {Object.entries(stats.by_status).map(([status, count]) => (
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

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => router.push('/crm/marketing/campaigns')}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Megaphone className="h-5 w-5" />
              Campaigns
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Create and manage email, SMS, and multi-channel campaigns
            </p>
            <div className="flex items-center gap-4 mb-4">
              <div className="flex items-center gap-2">
                <Mail className="h-4 w-4 text-blue-600" />
                <span className="text-sm">Email</span>
              </div>
              <div className="flex items-center gap-2">
                <MessageSquare className="h-4 w-4 text-green-600" />
                <span className="text-sm">SMS</span>
              </div>
            </div>
            <Button variant="outline" className="w-full gap-2">
              View Campaigns
              <ArrowRight className="h-4 w-4" />
            </Button>
          </CardContent>
        </Card>

        <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => router.push('/crm/marketing/segments')}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              Segments
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Build customer segments with dynamic rules and criteria
            </p>
            <Button variant="outline" className="w-full gap-2">
              Manage Segments
              <ArrowRight className="h-4 w-4" />
            </Button>
          </CardContent>
        </Card>

        <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => router.push('/crm/marketing/landing-pages')}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Landing Pages
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Create high-converting landing pages for your campaigns
            </p>
            <Button variant="outline" className="w-full gap-2">
              View Pages
              <ArrowRight className="h-4 w-4" />
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default MarketingDashboard
