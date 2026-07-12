"use client";

import { useState, useEffect } from "react";
import { Plus, Clock, TrendingUp, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { SLAPolicyList } from "@/components/crm/customer-service/SLAPolicyList";
import { CreateSLAPolicyDialog } from "@/components/crm/customer-service/CreateSLAPolicyDialog";
import { useToast } from "@/hooks/use-toast";
import { customerServiceApi } from "@/lib/api/customer-service";

export default function SLAManagementPage() {
  const [policies, setPolicies] = useState([]);
  const [metrics, setMetrics] = useState({
    total_tickets: 0,
    within_sla: 0,
    approaching_breach: 0,
    breached: 0,
    average_first_response_time: 0,
    average_resolution_time: 0,
    sla_compliance_rate: 0
  });
  const [loading, setLoading] = useState(true);
  const [showCreateDialog, setShowCreateDialog] = useState(false);

  const { toast } = useToast();

  useEffect(() => {
    fetchPolicies();
    fetchMetrics();
  }, []);

  const fetchPolicies = async () => {
    try {
      setLoading(true);
      const data = await customerServiceApi.listSLAPolicies();
      setPolicies(Array.isArray(data) ? data : []);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch SLA policies",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchMetrics = async () => {
    try {
      const data = await customerServiceApi.getSLAMetrics();
      setMetrics(data || {
        total_tickets: 0,
        within_sla: 0,
        approaching_breach: 0,
        breached: 0,
        average_first_response_time: 0,
        average_resolution_time: 0,
        sla_compliance_rate: 0
      });
    } catch (error) {
      console.error("Failed to fetch SLA metrics", error);
    }
  };

  const handleCreatePolicy = () => {
    setShowCreateDialog(true);
  };

  const handlePolicyCreated = () => {
    setShowCreateDialog(false);
    fetchPolicies();
    toast({
      title: "Success",
      description: "SLA policy created successfully"
    });
  };

  const complianceRate = metrics.sla_compliance_rate || 0;

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">SLA Management</h1>
          <p className="text-muted-foreground">
            Configure and monitor Service Level Agreements
          </p>
        </div>
        <Button onClick={handleCreatePolicy}>
          <Plus className="h-4 w-4 mr-2" />
          Create SLA Policy
        </Button>
      </div>

      {/* Metrics Overview */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Compliance Rate</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{complianceRate.toFixed(1)}%</div>
            <Progress value={complianceRate} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Within SLA</CardTitle>
            <Clock className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {metrics.within_sla}
            </div>
            <p className="text-xs text-muted-foreground">
              of {metrics.total_tickets} tickets
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Approaching Breach</CardTitle>
            <AlertTriangle className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">
              {metrics.approaching_breach}
            </div>
            <p className="text-xs text-muted-foreground">
              Action required soon
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">SLA Breached</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {metrics.breached}
            </div>
            <p className="text-xs text-muted-foreground">
              Immediate attention needed
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Response & Resolution Times */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Average First Response Time</CardTitle>
            <CardDescription>Time taken to first respond to tickets</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {Math.round(metrics.average_first_response_time)} min
            </div>
            <p className="text-sm text-muted-foreground mt-2">
              Target varies by priority level
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Average Resolution Time</CardTitle>
            <CardDescription>Time taken to resolve tickets</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {Math.round(metrics.average_resolution_time)} min
            </div>
            <p className="text-sm text-muted-foreground mt-2">
              {(metrics.average_resolution_time / 60).toFixed(1)} hours average
            </p>
          </CardContent>
        </Card>
      </div>

      {/* SLA Policies */}
      <Card>
        <CardHeader>
          <CardTitle>SLA Policies</CardTitle>
          <CardDescription>
            Configure service level agreements for different ticket types
          </CardDescription>
        </CardHeader>
        <CardContent>
          <SLAPolicyList
            policies={policies}
            loading={loading}
            onRefresh={fetchPolicies}
          />
        </CardContent>
      </Card>

      {/* SLA Guide */}
      <Card>
        <CardHeader>
          <CardTitle>Understanding SLA</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h3 className="font-semibold mb-2">What is SLA?</h3>
            <p className="text-sm text-muted-foreground">
              Service Level Agreements (SLA) define the expected response and resolution times 
              for support tickets based on their priority, category, and channel.
            </p>
          </div>

          <div>
            <h3 className="font-semibold mb-2">SLA Status Indicators</h3>
            <div className="space-y-2 text-sm">
              <div className="flex items-center gap-2">
                <Badge className="bg-green-100 text-green-800">Within SLA</Badge>
                <span className="text-muted-foreground">Ticket is being handled within the defined timeframe</span>
              </div>
              <div className="flex items-center gap-2">
                <Badge className="bg-yellow-100 text-yellow-800">Approaching Breach</Badge>
                <span className="text-muted-foreground">Less than 1 hour remaining before SLA breach</span>
              </div>
              <div className="flex items-center gap-2">
                <Badge className="bg-red-100 text-red-800">Breached</Badge>
                <span className="text-muted-foreground">SLA time limit has been exceeded</span>
              </div>
            </div>
          </div>

          <div>
            <h3 className="font-semibold mb-2">Business Hours</h3>
            <p className="text-sm text-muted-foreground">
              SLA can be configured to count only business hours (e.g., 9 AM to 6 PM, Monday to Friday) 
              or run 24/7. This ensures fair SLA calculations based on your support availability.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Create SLA Policy Dialog */}
      {showCreateDialog && (
        <CreateSLAPolicyDialog
          open={showCreateDialog}
          onClose={() => setShowCreateDialog(false)}
          onSuccess={handlePolicyCreated}
        />
      )}
    </div>
  );
}
