'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Plus, Search, Filter, Eye, Mail, MessageSquare, FileText } from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { notificationService } from '@/services/notification.service'
import { getStatusColor } from '@/lib/utils'
import type { NotificationTemplate } from '@/types'

export default function NotificationTemplatesPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [channelFilter, setChannelFilter] = useState<string>('')

  const { data, isLoading } = useQuery({
    queryKey: ['notification-templates', page, search, channelFilter],
    queryFn: () => notificationService.getTemplates({ 
      page, 
      page_size: 12,
      channel: channelFilter || undefined
    }),
  })

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Notification Templates</h1>
            <p className="text-gray-600 mt-1">Manage notification message templates</p>
          </div>
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            New Template
          </Button>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              type="search"
              placeholder="Search templates by name, code..."
              className="pl-10"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <select
            value={channelFilter}
            onChange={(e) => setChannelFilter(e.target.value)}
            className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
          >
            <option value="">All Channels</option>
            <option value="SMS">SMS</option>
            <option value="Email">Email</option>
            <option value="WhatsApp">WhatsApp</option>
          </select>
          <Button variant="outline">
            <Filter className="h-4 w-4 mr-2" />
            More Filters
          </Button>
        </div>

        {/* Templates Grid */}
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <Card key={i}>
                <CardHeader>
                  <Skeleton className="h-6 w-3/4" />
                  <Skeleton className="h-4 w-1/2 mt-2" />
                </CardHeader>
                <CardContent>
                  <Skeleton className="h-20 w-full" />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : data?.data?.items && data.data.items.length > 0 ? (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {data.data.items.map((template: NotificationTemplate) => (
                <TemplateCard key={template.id} template={template} />
              ))}
            </div>

            {/* Pagination */}
            {data.data.items.length > 0 && (
              <div className="flex items-center justify-between">
                <p className="text-sm text-gray-600">
                  Showing {((page - 1) * 12) + 1} to {Math.min(page * 12, data.metadata?.total || 0)} of {data.metadata?.total || 0} templates
                </p>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={!data.metadata?.has_prev}
                    onClick={() => setPage(page - 1)}
                  >
                    Previous
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={!data.metadata?.has_next}
                    onClick={() => setPage(page + 1)}
                  >
                    Next
                  </Button>
                </div>
              </div>
            )}
          </>
        ) : (
          <Card>
            <CardContent className="py-12">
              <div className="text-center text-gray-500">
                <FileText className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                <p className="text-lg font-medium">No templates found</p>
                <p className="text-sm mt-1">Try adjusting your search or filters</p>
                <Button className="mt-4">
                  <Plus className="h-4 w-4 mr-2" />
                  Create Template
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  )
}

function TemplateCard({ template }: { template: NotificationTemplate }) {
  const getChannelIcon = (channel: string) => {
    switch (channel) {
      case 'Email':
        return Mail
      case 'SMS':
        return MessageSquare
      case 'WhatsApp':
        return MessageSquare
      default:
        return FileText
    }
  }

  const getChannelColor = (channel: string) => {
    switch (channel) {
      case 'Email':
        return 'bg-blue-100 text-blue-700'
      case 'SMS':
        return 'bg-green-100 text-green-700'
      case 'WhatsApp':
        return 'bg-green-100 text-green-700'
      default:
        return 'bg-gray-100 text-gray-700'
    }
  }

  const Icon = getChannelIcon(template.channel)

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg mb-2">{template.template_name}</CardTitle>
            <p className="text-sm text-gray-500 mb-3">{template.template_code}</p>
            <Badge className={getChannelColor(template.channel)}>
              {template.channel}
            </Badge>
          </div>
          <div className={`h-12 w-12 rounded-lg ${getChannelColor(template.channel)} flex items-center justify-center`}>
            <Icon className="h-6 w-6" />
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Subject (for Email) */}
        {template.subject && (
          <div>
            <p className="text-xs text-gray-500 mb-1">Subject</p>
            <p className="text-sm font-medium line-clamp-1">{template.subject}</p>
          </div>
        )}

        {/* Content Preview */}
        <div>
          <p className="text-xs text-gray-500 mb-1">Content Preview</p>
          <p className="text-sm text-gray-700 line-clamp-3 bg-gray-50 p-2 rounded">
            {template.template_content}
          </p>
        </div>

        {/* Meta Info */}
        <div className="grid grid-cols-2 gap-4 pt-2 border-t">
          <div>
            <p className="text-xs text-gray-500 mb-1">Category</p>
            <Badge variant="outline" className="text-xs">
              {template.category}
            </Badge>
          </div>
          <div>
            <p className="text-xs text-gray-500 mb-1">Status</p>
            <Badge className={getStatusColor(template.is_active ? 'Active' : 'Inactive')}>
              {template.is_active ? 'Active' : 'Inactive'}
            </Badge>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          <Button variant="outline" size="sm" className="flex-1">
            <Eye className="h-4 w-4 mr-2" />
            View
          </Button>
          <Button size="sm" className="flex-1" disabled={!template.is_active}>
            Edit
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
