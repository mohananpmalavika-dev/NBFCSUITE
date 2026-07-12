'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Megaphone,
  Search,
  Plus,
  Eye,
  Edit,
  Trash2,
  Play,
  Pause,
  Mail,
  MessageSquare,
  TrendingUp
} from 'lucide-react'
import { crmMarketingService, type MarketingCampaign, type CampaignFilters } from '@/services/crm-marketing.service'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'

const CAMPAIGN_STATUS_COLORS: Record<string, string> = {
  draft: 'bg-gray-100 text-gray-800',
  scheduled: 'bg-blue-100 text-blue-800',
  running: 'bg-green-100 text-green-800',
  paused: 'bg-yellow-100 text-yellow-800',
  completed: 'bg-purple-100 text-purple-800',
  cancelled: 'bg-red-100 text-red-800',
  failed: 'bg-red-100 text-red-800',
}

const CAMPAIGN_TYPES = [
  { value: 'email', label: 'Email', icon: Mail },
  { value: 'sms', label: 'SMS', icon: MessageSquare },
  { value: 'whatsapp', label: 'WhatsApp', icon: MessageSquare },
  { value: 'multi_channel', label: 'Multi-Channel', icon: TrendingUp },
]

const CAMPAIGN_STATUSES = [
  { value: 'draft', label: 'Draft' },
  { value: 'scheduled', label: 'Scheduled' },
  { value: 'running', label: 'Running' },
  { value: 'paused', label: 'Paused' },
  { value: 'completed', label: 'Completed' },
]

export function CampaignList() {
  const router = useRouter()
  const [campaigns, setCampaigns] = useState<MarketingCampaign[]>([])
  const [loading, setLoading] = useState(true)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize] = useState(20)
  
  const [filters, setFilters] = useState<CampaignFilters>({
    search: '',
    status: '',
    campaign_type: '',
  })

  useEffect(() => {
    loadCampaigns()
  }, [page, filters])

  const loadCampaigns = async () => {
    try {
      setLoading(true)
      const response = await crmMarketingService.listCampaigns({
        ...filters,
        skip: (page - 1) * pageSize,
        limit: pageSize,
      })

      if (response.success) {
        setCampaigns(response.data.campaigns)
        setTotal(response.data.total)
      }
    } catch (error: any) {
      toast.error(error.message || 'Failed to load campaigns')
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (value: string) => {
    setFilters(prev => ({ ...prev, search: value }))
    setPage(1)
  }

  const handleFilterChange = (key: keyof CampaignFilters, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value || undefined }))
    setPage(1)
  }

  const handleLaunch = async (campaignId: string, campaignName: string) => {
    if (!confirm(`Launch campaign "${campaignName}"?`)) return

    try {
      const response = await crmMarketingService.launchCampaign(campaignId)
      if (response.success) {
        toast.success('Campaign launched successfully')
        loadCampaigns()
      }
    } catch (error: any) {
      toast.error(error.message || 'Failed to launch campaign')
    }
  }

  const handleDelete = async (campaignId: string, campaignName: string) => {
    if (!confirm(`Delete campaign "${campaignName}"?`)) return

    try {
      const response = await crmMarketingService.deleteCampaign(campaignId)
      if (response.success) {
        toast.success('Campaign deleted successfully')
        loadCampaigns()
      }
    } catch (error: any) {
      toast.error(error.message || 'Failed to delete campaign')
    }
  }

  const totalPages = Math.ceil(total / pageSize)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Marketing Campaigns</h1>
          <p className="text-muted-foreground">
            Manage email, SMS, and multi-channel marketing campaigns
          </p>
        </div>
        <Button onClick={() => router.push('/crm/marketing/campaigns/new')} className="gap-2">
          <Plus className="h-4 w-4" />
          New Campaign
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="md:col-span-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Search campaigns..."
                  value={filters.search}
                  onChange={(e) => handleSearch(e.target.value)}
                  className="pl-9"
                />
              </div>
            </div>
            
            <Select
              value={filters.status || ''}
              onValueChange={(value) => handleFilterChange('status', value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="All Statuses" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Statuses</SelectItem>
                {CAMPAIGN_STATUSES.map((status) => (
                  <SelectItem key={status.value} value={status.value}>
                    {status.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select
              value={filters.campaign_type || ''}
              onValueChange={(value) => handleFilterChange('campaign_type', value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="All Types" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Types</SelectItem>
                {CAMPAIGN_TYPES.map((type) => (
                  <SelectItem key={type.value} value={type.value}>
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Campaigns Table */}
      <Card>
        <CardContent className="p-0">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : campaigns.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-64 text-center">
              <Megaphone className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No campaigns found</h3>
              <p className="text-muted-foreground mb-4">
                Get started by creating your first campaign
              </p>
              <Button onClick={() => router.push('/crm/marketing/campaigns/new')} className="gap-2">
                <Plus className="h-4 w-4" />
                Create Campaign
              </Button>
            </div>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Campaign</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Audience</TableHead>
                    <TableHead>Performance</TableHead>
                    <TableHead>Start Date</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {campaigns.map((campaign) => (
                    <TableRow key={campaign.id}>
                      <TableCell>
                        <div>
                          <div className="font-medium">{campaign.campaign_name}</div>
                          <div className="text-sm text-muted-foreground">
                            {campaign.campaign_number}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="capitalize">
                        {campaign.campaign_type.replace('_', ' ')}
                      </TableCell>
                      <TableCell>
                        <Badge
                          className={
                            CAMPAIGN_STATUS_COLORS[campaign.status] || 'bg-gray-100 text-gray-800'
                          }
                        >
                          {campaign.status}
                        </Badge>
                      </TableCell>
                      <TableCell>{campaign.target_audience_size.toLocaleString()}</TableCell>
                      <TableCell>
                        <div className="space-y-1 text-sm">
                          <div>Sent: {campaign.total_sent.toLocaleString()}</div>
                          <div>Opens: {campaign.open_rate || 0}%</div>
                        </div>
                      </TableCell>
                      <TableCell>
                        {campaign.start_date
                          ? new Date(campaign.start_date).toLocaleDateString()
                          : '-'}
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-2">
                          {(campaign.status === 'draft' || campaign.status === 'paused') && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleLaunch(campaign.id, campaign.campaign_name)}
                              title="Launch"
                            >
                              <Play className="h-4 w-4 text-green-600" />
                            </Button>
                          )}
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => router.push(`/crm/marketing/campaigns/${campaign.id}`)}
                            title="View"
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => router.push(`/crm/marketing/campaigns/${campaign.id}/edit`)}
                            title="Edit"
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDelete(campaign.id, campaign.campaign_name)}
                            title="Delete"
                          >
                            <Trash2 className="h-4 w-4 text-red-600" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between border-t px-6 py-4">
                  <div className="text-sm text-muted-foreground">
                    Showing {(page - 1) * pageSize + 1} to{' '}
                    {Math.min(page * pageSize, total)} of {total} campaigns
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage(page - 1)}
                      disabled={page === 1}
                    >
                      Previous
                    </Button>
                    <div className="text-sm">
                      Page {page} of {totalPages}
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage(page + 1)}
                      disabled={page === totalPages}
                    >
                      Next
                    </Button>
                  </div>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default CampaignList
