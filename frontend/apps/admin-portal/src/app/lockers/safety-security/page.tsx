'use client'

/**
 * Locker Safety & Security Management Page
 * Real-time security monitoring, insurance, and incident management
 */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Shield, Video, AlertTriangle, FileText, Activity, Lock } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { useToast } from '@/components/ui/use-toast'
import { 
  safetySecurityService,
  type SecurityDashboard,
  type SecurityStatistics,
  VaultAccessType,
  SecurityEventSeverity,
  IncidentSeverity
} from '@/services/locker.service'


export default function SafetySecurityPage() {
  const { toast } = useToast()
  const queryClient = useQueryClient()
  
  const [activeTab, setActiveTab] = useState('dashboard')
  const [openVaultDialog, setOpenVaultDialog] = useState(false)
  const [reportIncidentDialog, setReportIncidentDialog] = useState(false)
  
  // Fetch dashboard data
  const { data: dashboard } = useQuery<SecurityDashboard>({
    queryKey: ['safety-security', 'dashboard'],
    queryFn: async () => {
      const response = await safetySecurityService.getSecurityDashboard()
      return response.data
    },
    refetchInterval: 30000 // Refresh every 30 seconds
  })
  
  // Fetch statistics
  const { data: statistics } = useQuery<SecurityStatistics>({
    queryKey: ['safety-security', 'statistics'],
    queryFn: async () => {
      const response = await safetySecurityService.getStatistics()
      return response.data
    }
  })
  
  return (
    <div className="container mx-auto py-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <Shield className="h-8 w-8" />
            Safety & Security
          </h1>
          <p className="text-muted-foreground">
            Real-time monitoring, insurance, and incident management
          </p>
        </div>
        <div className="flex gap-2">
          <Button onClick={() => setReportIncidentDialog(true)} variant="destructive">
            <AlertTriangle className="mr-2 h-4 w-4" />
            Report Incident
          </Button>
          <Button onClick={() => setOpenVaultDialog(true)}>
            <Lock className="mr-2 h-4 w-4" />
            Vault Access
          </Button>
        </div>
      </div>
      
      {/* Real-time Status Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Vault Status</CardTitle>
            <Lock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {dashboard?.vault_status === 'closed' ? (
                <Badge variant="default">Closed</Badge>
              ) : (
                <Badge variant="destructive">Open</Badge>
              )}
            </div>
            {dashboard?.last_opened && (
              <p className="text-xs text-muted-foreground mt-2">
                Last opened: {new Date(dashboard.last_opened).toLocaleString()}
              </p>
            )}
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">CCTV Status</CardTitle>
            <Video className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {dashboard?.cctv_cameras_online}/{dashboard?.cctv_cameras_total}
            </div>
            <p className="text-xs text-muted-foreground">
              {((dashboard?.cctv_cameras_online || 0) / (dashboard?.cctv_cameras_total || 1) * 100).toFixed(1)}% uptime
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Alarms</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-destructive">
              {dashboard?.active_alarms || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              Requires immediate attention
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Incidents</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {dashboard?.incidents_this_month || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              This month
            </p>
          </CardContent>
        </Card>
      </div>
      
      {/* Main Content Tabs */}
      <Card>
        <CardHeader>
          <CardTitle>Security Management</CardTitle>
          <CardDescription>Monitor security systems and manage incidents</CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList>
              <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
              <TabsTrigger value="vault">Vault Access</TabsTrigger>
              <TabsTrigger value="monitoring">Monitoring</TabsTrigger>
              <TabsTrigger value="insurance">Insurance</TabsTrigger>
              <TabsTrigger value="incidents">Incidents</TabsTrigger>
              <TabsTrigger value="statistics">Statistics</TabsTrigger>
            </TabsList>
            
            <TabsContent value="dashboard">
              <SecurityDashboardTab dashboard={dashboard} />
            </TabsContent>
            
            <TabsContent value="vault">
              <VaultAccessTab />
            </TabsContent>
            
            <TabsContent value="monitoring">
              <SecurityMonitoringTab />
            </TabsContent>
            
            <TabsContent value="insurance">
              <InsuranceManagementTab />
            </TabsContent>
            
            <TabsContent value="incidents">
              <IncidentManagementTab />
            </TabsContent>
            
            <TabsContent value="statistics">
              <StatisticsTab statistics={statistics} />
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
      
      {/* Dialogs will be added here */}
    </div>
  )
}


// ==================== TAB COMPONENTS ====================

function SecurityDashboardTab({ dashboard }: { dashboard?: SecurityDashboard }) {
  return (
    <div className="space-y-4 py-4">
      <div className="grid gap-4 md:grid-cols-2">
        {/* Recent Security Events */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Security Events</CardTitle>
          </CardHeader>
          <CardContent>
            {dashboard?.recent_security_events && dashboard.recent_security_events.length > 0 ? (
              <div className="space-y-2">
                {dashboard.recent_security_events.slice(0, 5).map((event, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2 border rounded">
                    <div>
                      <p className="font-medium text-sm">{event.event_type.replace(/_/g, ' ')}</p>
                      <p className="text-xs text-muted-foreground">{event.description}</p>
                    </div>
                    <Badge variant={event.severity === 'critical' ? 'destructive' : 'default'}>
                      {event.severity}
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground text-center py-4">
                No recent security events
              </p>
            )}
          </CardContent>
        </Card>
        
        {/* Insurance Overview */}
        <Card>
          <CardHeader>
            <CardTitle>Insurance Overview</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Active Policies</span>
                <span className="text-2xl font-bold">{dashboard?.active_insurance_policies || 0}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Expiring in 30 days</span>
                <span className="text-xl font-semibold text-orange-600">
                  {dashboard?.expiring_policies_30_days || 0}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}


function VaultAccessTab() {
  const { toast } = useToast()
  const queryClient = useQueryClient()
  
  // Fetch vault access log
  const { data: accessLog } = useQuery({
    queryKey: ['vault-access-log'],
    queryFn: async () => {
      const response = await safetySecurityService.getVaultAccessLog('branch-1')
      return response.data
    }
  })
  
  return (
    <div className="space-y-4 py-4">
      <Card>
        <CardHeader>
          <CardTitle>Vault Access History</CardTitle>
          <CardDescription>Dual custody access records</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {accessLog?.access_logs && accessLog.access_logs.length > 0 ? (
              accessLog.access_logs.map((log: any, idx: number) => (
                <div key={idx} className="p-3 border rounded">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-medium">{log.access_type.replace(/_/g, ' ')}</p>
                      <p className="text-sm text-muted-foreground">{log.purpose}</p>
                      <p className="text-xs text-muted-foreground mt-1">
                        Officials: {log.official_1_id}, {log.official_2_id}
                      </p>
                    </div>
                    <div className="text-right text-sm">
                      <p>{new Date(log.opened_at).toLocaleString()}</p>
                      {log.closed_at && (
                        <p className="text-muted-foreground">
                          Closed: {new Date(log.closed_at).toLocaleString()}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-center text-muted-foreground py-8">No vault access records</p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}


function SecurityMonitoringTab() {
  const { data: securityEvents } = useQuery({
    queryKey: ['security-events'],
    queryFn: async () => {
      const response = await safetySecurityService.getSecurityEvents()
      return response.data
    }
  })
  
  return (
    <div className="space-y-4 py-4">
      <Card>
        <CardHeader>
          <CardTitle>Security Events</CardTitle>
          <CardDescription>Real-time security monitoring</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {securityEvents?.events && securityEvents.events.length > 0 ? (
              securityEvents.events.map((event: any, idx: number) => (
                <div key={idx} className="p-3 border rounded flex justify-between items-center">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <Badge variant={
                        event.severity === 'critical' || event.severity === 'emergency' 
                          ? 'destructive' 
                          : 'default'
                      }>
                        {event.severity}
                      </Badge>
                      <p className="font-medium">{event.event_type.replace(/_/g, ' ')}</p>
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">{event.description}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {new Date(event.event_timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-center text-muted-foreground py-8">No security events</p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}


function InsuranceManagementTab() {
  const { toast } = useToast()
  const [createPolicyDialog, setCreatePolicyDialog] = useState(false)
  
  const { data: policies } = useQuery({
    queryKey: ['insurance-policies'],
    queryFn: async () => {
      const response = await safetySecurityService.getInsurancePolicies()
      return response.data
    }
  })
  
  return (
    <div className="space-y-4 py-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Insurance Policies</h3>
        <Button onClick={() => setCreatePolicyDialog(true)}>
          <FileText className="mr-2 h-4 w-4" />
          Create Policy
        </Button>
      </div>
      
      <div className="grid gap-4 md:grid-cols-2">
        {policies?.policies && policies.policies.length > 0 ? (
          policies.policies.map((policy: any) => (
            <Card key={policy.id}>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <CardTitle className="text-base">{policy.policy_number}</CardTitle>
                  <Badge variant={policy.status === 'active' ? 'default' : 'secondary'}>
                    {policy.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Type</span>
                    <span>{policy.policy_type}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Coverage</span>
                    <span className="font-medium">₹{policy.coverage_amount.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Premium</span>
                    <span>₹{policy.premium_amount.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Valid Until</span>
                    <span>{new Date(policy.end_date).toLocaleDateString()}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        ) : (
          <p className="col-span-2 text-center text-muted-foreground py-8">
            No insurance policies found
          </p>
        )}
      </div>
    </div>
  )
}


function IncidentManagementTab() {
  const { toast } = useToast()
  
  const { data: incidents } = useQuery({
    queryKey: ['incidents'],
    queryFn: async () => {
      const response = await safetySecurityService.getIncidents()
      return response.data
    }
  })
  
  return (
    <div className="space-y-4 py-4">
      <Card>
        <CardHeader>
          <CardTitle>Security Incidents</CardTitle>
          <CardDescription>Incident tracking and management</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {incidents?.incidents && incidents.incidents.length > 0 ? (
              incidents.incidents.map((incident: any) => (
                <div key={incident.id} className="p-4 border rounded">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <p className="font-semibold">{incident.incident_number}</p>
                      <p className="text-sm text-muted-foreground">
                        {incident.incident_type.replace(/_/g, ' ')}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <Badge variant={
                        incident.severity === 'critical' || incident.severity === 'catastrophic'
                          ? 'destructive'
                          : 'default'
                      }>
                        {incident.severity}
                      </Badge>
                      <Badge variant="outline">{incident.status}</Badge>
                    </div>
                  </div>
                  <p className="text-sm mb-2">{incident.description}</p>
                  <div className="flex justify-between items-center text-xs text-muted-foreground">
                    <span>Branch: {incident.branch_id}</span>
                    <span>Reported: {new Date(incident.reported_at).toLocaleDateString()}</span>
                  </div>
                  {incident.affected_lockers && incident.affected_lockers.length > 0 && (
                    <div className="mt-2 text-xs">
                      <span className="text-muted-foreground">Affected lockers: </span>
                      <span>{incident.affected_lockers.join(', ')}</span>
                    </div>
                  )}
                </div>
              ))
            ) : (
              <p className="text-center text-muted-foreground py-8">No incidents reported</p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}


function StatisticsTab({ statistics }: { statistics?: SecurityStatistics }) {
  if (!statistics) {
    return <div className="py-8 text-center text-muted-foreground">Loading statistics...</div>
  }
  
  return (
    <div className="space-y-4 py-4">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {/* Incident Statistics */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Incident Overview</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Total Incidents</span>
              <span className="font-semibold">{statistics.total_incidents}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Open</span>
              <span className="font-semibold text-orange-600">{statistics.open_incidents}</span>
            </div>
          </CardContent>
        </Card>
        
        {/* Insurance Statistics */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Insurance Overview</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Total Policies</span>
              <span className="font-semibold">{statistics.total_insurance_policies}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Active</span>
              <span className="font-semibold text-green-600">{statistics.active_policies}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Expired</span>
              <span className="font-semibold text-red-600">{statistics.expired_policies}</span>
            </div>
          </CardContent>
        </Card>
        
        {/* Claims Statistics */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Claims & Compensation</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Claims Filed</span>
              <span className="font-semibold">{statistics.total_claims_filed}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Approved</span>
              <span className="font-semibold text-green-600">{statistics.claims_approved}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Total Paid</span>
              <span className="font-semibold">₹{statistics.total_compensation_paid.toLocaleString()}</span>
            </div>
          </CardContent>
        </Card>
        
        {/* Security Events */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Security Events</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Today</span>
              <span className="font-semibold">{statistics.security_events_today}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Critical (This Week)</span>
              <span className="font-semibold text-red-600">{statistics.critical_events_this_week}</span>
            </div>
          </CardContent>
        </Card>
        
        {/* Vault Activity */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Vault Activity</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Opens (This Month)</span>
              <span className="font-semibold">{statistics.vault_opens_this_month}</span>
            </div>
          </CardContent>
        </Card>
        
        {/* CCTV Uptime */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">CCTV Performance</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Uptime</span>
              <span className="font-semibold text-green-600">
                {statistics.cctv_uptime_percentage.toFixed(2)}%
              </span>
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* Incident Types Chart */}
      {Object.keys(statistics.incidents_by_type).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Incidents by Type</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {Object.entries(statistics.incidents_by_type).map(([type, count]) => (
                <div key={type} className="flex items-center justify-between">
                  <span className="text-sm capitalize">{type.replace(/_/g, ' ')}</span>
                  <div className="flex items-center gap-2">
                    <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-blue-600" 
                        style={{ width: `${(count / statistics.total_incidents) * 100}%` }}
                      />
                    </div>
                    <span className="text-sm font-semibold w-8 text-right">{count}</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
