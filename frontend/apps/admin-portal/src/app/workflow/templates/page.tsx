'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { Search, Filter, Eye, GitBranch, CheckCircle, XCircle } from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { workflowService } from '@/services/workflow.service'
import { getStatusColor } from '@/lib/utils'
import type { WorkflowTemplate } from '@/types'

export default function WorkflowTemplatesPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['workflow-templates', page, search],
    queryFn: () => workflowService.getTemplates({ 
      page, 
      page_size: 12
    }),
  })

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Workflow Templates</h1>
            <p className="text-gray-600 mt-1">Browse and manage workflow templates</p>
          </div>
          <Link href="/workflow/instances">
            <Button variant="outline">
              <GitBranch className="h-4 w-4 mr-2" />
              View Instances
            </Button>
          </Link>
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
              {data.data.items.map((template: WorkflowTemplate) => (
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
                <GitBranch className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                <p className="text-lg font-medium">No workflow templates found</p>
                <p className="text-sm mt-1">Try adjusting your search</p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  )
}

function TemplateCard({ template }: { template: WorkflowTemplate }) {
  const getTypeColor = (type: string) => {
    switch (type) {
      case 'sequential':
        return 'bg-blue-100 text-blue-700'
      case 'parallel':
        return 'bg-purple-100 text-purple-700'
      case 'conditional':
        return 'bg-orange-100 text-orange-700'
      default:
        return 'bg-gray-100 text-gray-700'
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'sequential':
        return GitBranch
      case 'parallel':
        return GitBranch
      case 'conditional':
        return GitBranch
      default:
        return GitBranch
    }
  }

  const Icon = getTypeIcon(template.workflow_type)

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg mb-2">{template.template_name}</CardTitle>
            <p className="text-sm text-gray-500 mb-3">{template.template_code}</p>
            <Badge className={getTypeColor(template.workflow_type)}>
              {template.workflow_type}
            </Badge>
          </div>
          <div className={`h-12 w-12 rounded-lg ${getTypeColor(template.workflow_type)} flex items-center justify-center`}>
            <Icon className="h-6 w-6" />
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Description */}
        {template.description && (
          <p className="text-sm text-gray-600 line-clamp-3">
            {template.description}
          </p>
        )}

        {/* Meta Info */}
        <div className="grid grid-cols-2 gap-4 pt-2 border-t">
          <div>
            <p className="text-xs text-gray-500 mb-1">Version</p>
            <p className="text-sm font-semibold text-gray-900">v{template.version}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 mb-1">Status</p>
            <Badge className={getStatusColor(template.is_active ? 'Active' : 'Inactive')}>
              {template.is_active ? 'Active' : 'Inactive'}
            </Badge>
          </div>
        </div>

        {/* Workflow Definition Info */}
        {template.workflow_definition && (
          <div className="pt-2 border-t">
            <p className="text-xs text-gray-500 mb-2">Workflow Steps</p>
            <div className="flex flex-wrap gap-2">
              {Array.isArray(template.workflow_definition.steps) 
                ? template.workflow_definition.steps.slice(0, 3).map((step: any, idx: number) => (
                    <Badge key={idx} variant="outline" className="text-xs">
                      {step.name || `Step ${idx + 1}`}
                    </Badge>
                  ))
                : <Badge variant="outline" className="text-xs">Custom Definition</Badge>
              }
              {Array.isArray(template.workflow_definition.steps) && 
               template.workflow_definition.steps.length > 3 && (
                <Badge variant="outline" className="text-xs">
                  +{template.workflow_definition.steps.length - 3} more
                </Badge>
              )}
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-2 pt-2">
          <Button 
            variant="outline" 
            size="sm" 
            className="flex-1"
            disabled={!template.is_active}
          >
            <Eye className="h-4 w-4 mr-2" />
            View Details
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
