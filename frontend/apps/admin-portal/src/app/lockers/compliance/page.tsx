'use client'

import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Shield, 
  FileCheck, 
  AlertTriangle, 
  CheckCircle2, 
  XCircle, 
  Clock,
  Plus,
  Eye,
  Calendar,
  TrendingUp,
  BarChart3,
  FileText,
  ClipboardCheck,
  Search
} from 'lucide-react'
import { 
  complianceService,
  ComplianceType,
  ComplianceStatus,
  AuditType,
  AuditStatus,
  InspectionType,
  FindingsSeverity
} from '@/services/locker.service'
import { format } from 'date-fns'


export default function CompliancePage() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [checkComplianceDialog, setCheckComplianceDialog] = useState(false)
  const [scheduleAuditDialog, setScheduleAuditDialog] = useState(false)
  const [conductInspectionDialog, setConductInspectionDialog] = useState(false)
  const [recordIssueDialog, setRecordIssueDialog] = useState(false)
  const [selectedAudit, setSelectedAudit] = useState<any>(null)
  const [selectedInspection, setSelectedInspection] = useState<any>(null)
  
  const queryClient = useQueryClient()

  // Auto-refresh every 60 seconds
  const refreshInterval = 60000

  // Fetch dashboard data
  const { data: dashboardData, isLoading: dashboardLoading } = useQuery({
    queryKey: ['compliance-dashboard'],
    queryFn: () => complianceService.getDashboard(),
    refetchInterval: refreshInterval,
  })

  // Fetch compliance issues
  const { data: issuesData } = useQuery({
    queryKey: ['compliance-issues'],
    queryFn: () => complianceService.getComplianceIssues(),
    refetchInterval: refreshInterval,
  })

  // Fetch audits
  const { data: auditsData } = useQuery({
    queryKey: ['compliance-audits'],
    queryFn: () => complianceService.getAudits(),
    refetchInterval: refreshInterval,
  })

  // Fetch inspections
  const { data: inspectionsData } = useQuery({
    queryKey: ['compliance-inspections'],
    queryFn: () => complianceService.getInspections(),
    refetchInterval: refreshInterval,
  })

  // Fetch statistics
  const { data: statisticsData } = useQuery({
    queryKey: ['compliance-statistics'],
    queryFn: () => complianceService.getStatistics({ period: 'month' }),
    refetchInterval: refreshInterval,
  })


  // Mutations
  const checkComplianceMutation = useMutation({
    mutationFn: complianceService.checkRBICompliance,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['compliance-dashboard'] })
      setCheckComplianceDialog(false)
    },
  })

  const scheduleAuditMutation = useMutation({
    mutationFn: complianceService.scheduleAudit,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['compliance-audits'] })
      setScheduleAuditDialog(false)
    },
  })

  const conductInspectionMutation = useMutation({
    mutationFn: complianceService.conductInspection,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['compliance-inspections'] })
      setConductInspectionDialog(false)
    },
  })

  const recordIssueMutation = useMutation({
    mutationFn: complianceService.recordComplianceIssue,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['compliance-issues'] })
      setRecordIssueDialog(false)
    },
  })

  // Helper functions
  const getComplianceStatusBadge = (status: ComplianceStatus) => {
    const variants: Record<ComplianceStatus, { color: string; label: string }> = {
      [ComplianceStatus.COMPLIANT]: { color: 'bg-green-500', label: 'Compliant' },
      [ComplianceStatus.NON_COMPLIANT]: { color: 'bg-red-500', label: 'Non-Compliant' },
      [ComplianceStatus.PARTIALLY_COMPLIANT]: { color: 'bg-yellow-500', label: 'Partial' },
      [ComplianceStatus.UNDER_REVIEW]: { color: 'bg-blue-500', label: 'Under Review' },
      [ComplianceStatus.REMEDIATION_IN_PROGRESS]: { color: 'bg-orange-500', label: 'In Progress' },
    }
    const variant = variants[status]
    return <Badge className={variant.color}>{variant.label}</Badge>
  }

  const getSeverityBadge = (severity: FindingsSeverity) => {
    const variants: Record<FindingsSeverity, { color: string; label: string }> = {
      [FindingsSeverity.LOW]: { color: 'bg-blue-500', label: 'Low' },
      [FindingsSeverity.MEDIUM]: { color: 'bg-yellow-500', label: 'Medium' },
      [FindingsSeverity.HIGH]: { color: 'bg-orange-500', label: 'High' },
      [FindingsSeverity.CRITICAL]: { color: 'bg-red-500', label: 'Critical' },
    }
    const variant = variants[severity]
    return <Badge className={variant.color}>{variant.label}</Badge>
  }

  const getAuditStatusBadge = (status: AuditStatus) => {
    const variants: Record<AuditStatus, { color: string; label: string }> = {
      [AuditStatus.SCHEDULED]: { color: 'bg-blue-500', label: 'Scheduled' },
      [AuditStatus.IN_PROGRESS]: { color: 'bg-yellow-500', label: 'In Progress' },
      [AuditStatus.COMPLETED]: { color: 'bg-green-500', label: 'Completed' },
      [AuditStatus.REPORT_PENDING]: { color: 'bg-orange-500', label: 'Report Pending' },
      [AuditStatus.CLOSED]: { color: 'bg-gray-500', label: 'Closed' },
    }
    const variant = variants[status]
    return <Badge className={variant.color}>{variant.label}</Badge>
  }


  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Locker Compliance</h1>
          <p className="text-gray-500">RBI Guidelines, Audits & Inspections</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={() => setCheckComplianceDialog(true)} variant="outline">
            <FileCheck className="mr-2 h-4 w-4" />
            Check Compliance
          </Button>
          <Button onClick={() => setScheduleAuditDialog(true)} variant="outline">
            <Calendar className="mr-2 h-4 w-4" />
            Schedule Audit
          </Button>
          <Button onClick={() => setConductInspectionDialog(true)}>
            <ClipboardCheck className="mr-2 h-4 w-4" />
            Conduct Inspection
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
          <TabsTrigger value="compliance">Compliance Checks</TabsTrigger>
          <TabsTrigger value="audits">Audits</TabsTrigger>
          <TabsTrigger value="inspections">Inspections</TabsTrigger>
          <TabsTrigger value="issues">Issues</TabsTrigger>
          <TabsTrigger value="statistics">Statistics</TabsTrigger>
        </TabsList>

        {/* Dashboard Tab */}
        <TabsContent value="dashboard" className="space-y-4">
          <ComplianceDashboardTab 
            data={dashboardData} 
            loading={dashboardLoading}
          />
        </TabsContent>

        {/* Compliance Checks Tab */}
        <TabsContent value="compliance" className="space-y-4">
          <ComplianceChecksTab 
            onRecordIssue={() => setRecordIssueDialog(true)}
          />
        </TabsContent>

        {/* Audits Tab */}
        <TabsContent value="audits" className="space-y-4">
          <AuditsTab 
            audits={auditsData?.audits || []}
            onSchedule={() => setScheduleAuditDialog(true)}
            onViewDetails={setSelectedAudit}
          />
        </TabsContent>

        {/* Inspections Tab */}
        <TabsContent value="inspections" className="space-y-4">
          <InspectionsTab 
            inspections={inspectionsData?.inspections || []}
            onConduct={() => setConductInspectionDialog(true)}
            onViewDetails={setSelectedInspection}
          />
        </TabsContent>

        {/* Issues Tab */}
        <TabsContent value="issues" className="space-y-4">
          <IssuesTab 
            issues={issuesData?.issues || []}
            onRecordNew={() => setRecordIssueDialog(true)}
          />
        </TabsContent>

        {/* Statistics Tab */}
        <TabsContent value="statistics" className="space-y-4">
          <StatisticsTab data={statisticsData} />
        </TabsContent>
      </Tabs>

      {/* Dialogs */}
      <CheckComplianceDialog 
        open={checkComplianceDialog}
        onClose={() => setCheckComplianceDialog(false)}
        onSubmit={checkComplianceMutation.mutate}
      />
      
      <ScheduleAuditDialog 
        open={scheduleAuditDialog}
        onClose={() => setScheduleAuditDialog(false)}
        onSubmit={scheduleAuditMutation.mutate}
      />
      
      <ConductInspectionDialog 
        open={conductInspectionDialog}
        onClose={() => setConductInspectionDialog(false)}
        onSubmit={conductInspectionMutation.mutate}
      />
      
      <RecordIssueDialog 
        open={recordIssueDialog}
        onClose={() => setRecordIssueDialog(false)}
        onSubmit={recordIssueMutation.mutate}
      />
    </div>
  )
}


// ============================================
// Dashboard Tab Component
// ============================================

function ComplianceDashboardTab({ data, loading }: any) {
  if (loading) {
    return <div className="text-center py-8">Loading dashboard...</div>
  }

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              Overall Compliance Score
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-600">
              {data?.overall_compliance_score || 0}%
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {data?.compliant_areas || 0} compliant areas
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              Pending Audits
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {data?.pending_audits || 0}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {data?.completed_audits_this_month || 0} completed this month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              Open Issues
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-orange-600">
              {data?.open_compliance_issues || 0}
            </div>
            <p className="text-xs text-red-500 mt-1">
              {data?.critical_issues || 0} critical issues
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              Upcoming Inspections
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {data?.upcoming_inspections || 0}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Scheduled in next 30 days
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Compliance Areas Status */}
      <Card>
        <CardHeader>
          <CardTitle>Compliance Areas Overview</CardTitle>
          <CardDescription>Status of key RBI compliance areas</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {Object.values(ComplianceType).map((type) => (
              <div key={type} className="flex items-center justify-between p-3 border rounded">
                <div className="flex items-center gap-3">
                  <Shield className="h-5 w-5 text-blue-500" />
                  <div>
                    <p className="font-medium">{type.replace(/_/g, ' ').toUpperCase()}</p>
                    <p className="text-sm text-gray-500">Last checked: Recently</p>
                  </div>
                </div>
                <Badge className="bg-green-500">Compliant</Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}


// ============================================
// Compliance Checks Tab Component
// ============================================

function ComplianceChecksTab({ onRecordIssue }: any) {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>RBI Compliance Checklist</CardTitle>
              <CardDescription>Review and verify compliance with RBI guidelines</CardDescription>
            </div>
            <Button onClick={onRecordIssue} variant="outline">
              <AlertTriangle className="mr-2 h-4 w-4" />
              Record Issue
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {Object.values(ComplianceType).map((type) => (
              <Card key={type}>
                <CardHeader>
                  <CardTitle className="text-base">
                    {type.replace(/_/g, ' ').toUpperCase()}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Current Status</span>
                      <Badge className="bg-green-500">Compliant</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Last Verified</span>
                      <span className="text-sm">2 days ago</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Compliance Score</span>
                      <span className="text-sm font-medium">95%</span>
                    </div>
                    <Button size="sm" variant="outline" className="w-full mt-2">
                      View Details
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// ============================================
// Audits Tab Component
// ============================================

function AuditsTab({ audits, onSchedule, onViewDetails }: any) {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Audit Management</CardTitle>
              <CardDescription>Schedule and track internal and external audits</CardDescription>
            </div>
            <Button onClick={onSchedule}>
              <Plus className="mr-2 h-4 w-4" />
              Schedule Audit
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Audit Number</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Branch</TableHead>
                <TableHead>Scheduled Date</TableHead>
                <TableHead>Auditor</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {audits.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center text-gray-500">
                    No audits scheduled
                  </TableCell>
                </TableRow>
              ) : (
                audits.map((audit: any) => (
                  <TableRow key={audit.id}>
                    <TableCell className="font-medium">{audit.audit_number}</TableCell>
                    <TableCell>{audit.audit_type}</TableCell>
                    <TableCell>{audit.branch_id}</TableCell>
                    <TableCell>{format(new Date(audit.scheduled_date), 'PP')}</TableCell>
                    <TableCell>{audit.auditor_name}</TableCell>
                    <TableCell>{audit.status}</TableCell>
                    <TableCell>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => onViewDetails(audit)}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}


// ============================================
// Inspections Tab Component
// ============================================

function InspectionsTab({ inspections, onConduct, onViewDetails }: any) {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Inspection Management</CardTitle>
              <CardDescription>Track and conduct various types of inspections</CardDescription>
            </div>
            <Button onClick={onConduct}>
              <Plus className="mr-2 h-4 w-4" />
              Conduct Inspection
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Inspection Number</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Branch</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Inspector</TableHead>
                <TableHead>Findings</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {inspections.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center text-gray-500">
                    No inspections conducted
                  </TableCell>
                </TableRow>
              ) : (
                inspections.map((inspection: any) => (
                  <TableRow key={inspection.id}>
                    <TableCell className="font-medium">{inspection.inspection_number}</TableCell>
                    <TableCell>{inspection.inspection_type}</TableCell>
                    <TableCell>{inspection.branch_id}</TableCell>
                    <TableCell>{format(new Date(inspection.inspection_date), 'PP')}</TableCell>
                    <TableCell>{inspection.inspector_name}</TableCell>
                    <TableCell>
                      {inspection.findings?.length || 0} findings
                    </TableCell>
                    <TableCell>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => onViewDetails(inspection)}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}

// ============================================
// Issues Tab Component
// ============================================

function IssuesTab({ issues, onRecordNew }: any) {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Compliance Issues</CardTitle>
              <CardDescription>Track and remediate compliance issues</CardDescription>
            </div>
            <Button onClick={onRecordNew}>
              <Plus className="mr-2 h-4 w-4" />
              Record Issue
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Issue Number</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Severity</TableHead>
                <TableHead>Description</TableHead>
                <TableHead>Identified</TableHead>
                <TableHead>Target Resolution</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {issues.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center text-gray-500">
                    No compliance issues recorded
                  </TableCell>
                </TableRow>
              ) : (
                issues.map((issue: any) => (
                  <TableRow key={issue.id}>
                    <TableCell className="font-medium">{issue.issue_number}</TableCell>
                    <TableCell>{issue.compliance_type}</TableCell>
                    <TableCell>
                      <Badge className={
                        issue.severity === 'critical' ? 'bg-red-500' :
                        issue.severity === 'high' ? 'bg-orange-500' :
                        issue.severity === 'medium' ? 'bg-yellow-500' : 'bg-blue-500'
                      }>
                        {issue.severity}
                      </Badge>
                    </TableCell>
                    <TableCell className="max-w-xs truncate">{issue.description}</TableCell>
                    <TableCell>{format(new Date(issue.identified_date), 'PP')}</TableCell>
                    <TableCell>
                      {issue.target_resolution_date 
                        ? format(new Date(issue.target_resolution_date), 'PP')
                        : 'Not set'}
                    </TableCell>
                    <TableCell>
                      <Badge>{issue.status}</Badge>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}


// ============================================
// Statistics Tab Component
// ============================================

function StatisticsTab({ data }: any) {
  if (!data) {
    return <div className="text-center py-8">Loading statistics...</div>
  }

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Total Audits</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{data.total_audits || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Total Inspections</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{data.total_inspections || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Total Issues</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{data.compliance_issues?.total || 0}</div>
            <p className="text-sm text-gray-500">
              {data.compliance_issues?.open || 0} open, {data.compliance_issues?.resolved || 0} resolved
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Audits by Type</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {Object.entries(data.audits_by_type || {}).map(([type, count]) => (
                <div key={type} className="flex items-center justify-between">
                  <span className="text-sm">{type.replace(/_/g, ' ')}</span>
                  <span className="font-medium">{count as number}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Inspections by Type</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {Object.entries(data.inspections_by_type || {}).map(([type, count]) => (
                <div key={type} className="flex items-center justify-between">
                  <span className="text-sm">{type.replace(/_/g, ' ')}</span>
                  <span className="font-medium">{count as number}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Issues by Severity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {Object.entries(data.compliance_issues?.by_severity || {}).map(([severity, count]) => (
                <div key={severity} className="flex items-center justify-between">
                  <span className="text-sm capitalize">{severity}</span>
                  <Badge className={
                    severity === 'critical' ? 'bg-red-500' :
                    severity === 'high' ? 'bg-orange-500' :
                    severity === 'medium' ? 'bg-yellow-500' : 'bg-blue-500'
                  }>
                    {count as number}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Compliance Trends</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {(data.compliance_trends || []).map((trend: any) => (
                <div key={trend.month} className="flex items-center justify-between">
                  <span className="text-sm">{trend.month}</span>
                  <span className="font-medium">{trend.score}%</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}


// ============================================
// Check Compliance Dialog
// ============================================

function CheckComplianceDialog({ open, onClose, onSubmit }: any) {
  const [formData, setFormData] = useState({
    branch_id: '',
    compliance_areas: [] as ComplianceType[]
  })

  const handleSubmit = () => {
    onSubmit(formData)
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Check RBI Compliance</DialogTitle>
          <DialogDescription>
            Select areas to verify compliance with RBI guidelines
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div>
            <Label>Branch</Label>
            <Select
              value={formData.branch_id}
              onValueChange={(value) => setFormData({ ...formData, branch_id: value })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select branch" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="branch-001">Branch 001</SelectItem>
                <SelectItem value="branch-002">Branch 002</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label>Compliance Areas (Optional - leave empty to check all)</Label>
            <div className="mt-2 space-y-2">
              {Object.values(ComplianceType).map((type) => (
                <label key={type} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={formData.compliance_areas.includes(type)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setFormData({
                          ...formData,
                          compliance_areas: [...formData.compliance_areas, type]
                        })
                      } else {
                        setFormData({
                          ...formData,
                          compliance_areas: formData.compliance_areas.filter(a => a !== type)
                        })
                      }
                    }}
                    className="rounded"
                  />
                  <span className="text-sm">{type.replace(/_/g, ' ').toUpperCase()}</span>
                </label>
              ))}
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleSubmit}>
            Check Compliance
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}


// ============================================
// Schedule Audit Dialog
// ============================================

function ScheduleAuditDialog({ open, onClose, onSubmit }: any) {
  const [formData, setFormData] = useState({
    audit_type: AuditType.INTERNAL_AUDIT,
    branch_id: '',
    scheduled_date: '',
    auditor_name: '',
    audit_scope: '',
    checklist_items: []
  })

  const handleSubmit = () => {
    onSubmit(formData)
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Schedule Audit</DialogTitle>
          <DialogDescription>
            Schedule an internal or external audit
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div>
            <Label>Audit Type</Label>
            <Select
              value={formData.audit_type}
              onValueChange={(value: AuditType) => setFormData({ ...formData, audit_type: value })}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {Object.values(AuditType).map((type) => (
                  <SelectItem key={type} value={type}>
                    {type.replace(/_/g, ' ').toUpperCase()}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label>Branch</Label>
            <Select
              value={formData.branch_id}
              onValueChange={(value) => setFormData({ ...formData, branch_id: value })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select branch" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="branch-001">Branch 001</SelectItem>
                <SelectItem value="branch-002">Branch 002</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label>Scheduled Date</Label>
            <Input
              type="date"
              value={formData.scheduled_date}
              onChange={(e) => setFormData({ ...formData, scheduled_date: e.target.value })}
            />
          </div>

          <div>
            <Label>Auditor Name</Label>
            <Input
              value={formData.auditor_name}
              onChange={(e) => setFormData({ ...formData, auditor_name: e.target.value })}
              placeholder="Enter auditor name"
            />
          </div>

          <div>
            <Label>Audit Scope</Label>
            <Textarea
              value={formData.audit_scope}
              onChange={(e) => setFormData({ ...formData, audit_scope: e.target.value })}
              placeholder="Describe the scope of this audit"
              rows={4}
            />
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleSubmit}>
            Schedule Audit
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}


// ============================================
// Conduct Inspection Dialog
// ============================================

function ConductInspectionDialog({ open, onClose, onSubmit }: any) {
  const [formData, setFormData] = useState({
    inspection_type: InspectionType.PHYSICAL_VERIFICATION,
    branch_id: '',
    inspection_date: new Date().toISOString().split('T')[0],
    inspector_name: '',
    items_checked: [],
    findings: [],
    discrepancies_found: [],
    recommendations: ''
  })

  const handleSubmit = () => {
    onSubmit(formData)
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Conduct Inspection</DialogTitle>
          <DialogDescription>
            Record inspection details and findings
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div>
            <Label>Inspection Type</Label>
            <Select
              value={formData.inspection_type}
              onValueChange={(value: InspectionType) => 
                setFormData({ ...formData, inspection_type: value })
              }
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {Object.values(InspectionType).map((type) => (
                  <SelectItem key={type} value={type}>
                    {type.replace(/_/g, ' ').toUpperCase()}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label>Branch</Label>
            <Select
              value={formData.branch_id}
              onValueChange={(value) => setFormData({ ...formData, branch_id: value })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select branch" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="branch-001">Branch 001</SelectItem>
                <SelectItem value="branch-002">Branch 002</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label>Inspection Date</Label>
            <Input
              type="date"
              value={formData.inspection_date}
              onChange={(e) => setFormData({ ...formData, inspection_date: e.target.value })}
            />
          </div>

          <div>
            <Label>Inspector Name</Label>
            <Input
              value={formData.inspector_name}
              onChange={(e) => setFormData({ ...formData, inspector_name: e.target.value })}
              placeholder="Enter inspector name"
            />
          </div>

          <div>
            <Label>Recommendations</Label>
            <Textarea
              value={formData.recommendations}
              onChange={(e) => setFormData({ ...formData, recommendations: e.target.value })}
              placeholder="Enter any recommendations based on inspection findings"
              rows={3}
            />
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleSubmit}>
            Submit Inspection
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}


// ============================================
// Record Issue Dialog
// ============================================

function RecordIssueDialog({ open, onClose, onSubmit }: any) {
  const [formData, setFormData] = useState({
    compliance_type: ComplianceType.RBI_GUIDELINES,
    branch_id: '',
    severity: FindingsSeverity.MEDIUM,
    description: '',
    remediation_plan: '',
    target_resolution_date: ''
  })

  const handleSubmit = () => {
    onSubmit(formData)
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Record Compliance Issue</DialogTitle>
          <DialogDescription>
            Document a compliance issue for tracking and remediation
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div>
            <Label>Compliance Type</Label>
            <Select
              value={formData.compliance_type}
              onValueChange={(value: ComplianceType) => 
                setFormData({ ...formData, compliance_type: value })
              }
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {Object.values(ComplianceType).map((type) => (
                  <SelectItem key={type} value={type}>
                    {type.replace(/_/g, ' ').toUpperCase()}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label>Branch</Label>
            <Select
              value={formData.branch_id}
              onValueChange={(value) => setFormData({ ...formData, branch_id: value })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select branch" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="branch-001">Branch 001</SelectItem>
                <SelectItem value="branch-002">Branch 002</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label>Severity</Label>
            <Select
              value={formData.severity}
              onValueChange={(value: FindingsSeverity) => 
                setFormData({ ...formData, severity: value })
              }
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {Object.values(FindingsSeverity).map((severity) => (
                  <SelectItem key={severity} value={severity}>
                    {severity.toUpperCase()}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label>Description</Label>
            <Textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Describe the compliance issue in detail"
              rows={4}
            />
          </div>

          <div>
            <Label>Remediation Plan</Label>
            <Textarea
              value={formData.remediation_plan}
              onChange={(e) => setFormData({ ...formData, remediation_plan: e.target.value })}
              placeholder="Outline the plan to resolve this issue"
              rows={3}
            />
          </div>

          <div>
            <Label>Target Resolution Date</Label>
            <Input
              type="date"
              value={formData.target_resolution_date}
              onChange={(e) => setFormData({ ...formData, target_resolution_date: e.target.value })}
            />
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleSubmit}>
            Record Issue
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
