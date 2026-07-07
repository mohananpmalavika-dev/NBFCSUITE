'use client';

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  AlertTriangle, Shield, FileText, Users, 
  TrendingUp, Activity, CheckCircle, XCircle 
} from 'lucide-react';
import { amlService, type AMLDashboard } from '@/services/aml.service';
import Link from 'next/link';

export default function AMLDashboardPage() {
  const [dashboard, setDashboard] = useState<AMLDashboard | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const data = await amlService.getDashboardStats();
      setDashboard(data);
    } catch (error) {
      console.error('Failed to load AML dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!dashboard) {
    return <div>Error loading dashboard</div>;
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">AML/CFT Compliance</h1>
          <p className="text-muted-foreground">
            Anti-Money Laundering & Counter Financing of Terrorism
          </p>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Alerts</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboard.total_alerts}</div>
            <div className="flex gap-2 mt-2">
              <Badge variant="destructive" className="text-xs">
                {dashboard.open_alerts} Open
              </Badge>
              <Badge variant="warning" className="text-xs">
                {dashboard.under_review_alerts} Review
              </Badge>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Transactions Monitored</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboard.total_transactions_monitored.toLocaleString()}</div>
            <div className="text-xs text-muted-foreground">
              {dashboard.high_risk_transactions} high risk
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Reports Submitted</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {dashboard.submitted_ctr_reports + dashboard.submitted_str_reports}
            </div>
            <div className="text-xs text-muted-foreground">
              {dashboard.submitted_ctr_reports} CTR / {dashboard.submitted_str_reports} STR
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">PEP Screenings</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboard.total_pep_screenings}</div>
            <div className="text-xs text-muted-foreground">
              {dashboard.confirmed_peps} confirmed PEPs
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="alerts" className="space-y-4">
        <TabsList>
          <TabsTrigger value="alerts">Alerts</TabsTrigger>
          <TabsTrigger value="transactions">Transaction Monitoring</TabsTrigger>
          <TabsTrigger value="ctr">CTR Reports</TabsTrigger>
          <TabsTrigger value="str">STR Reports</TabsTrigger>
          <TabsTrigger value="pep">PEP Screening</TabsTrigger>
          <TabsTrigger value="sanctions">Sanction Screening</TabsTrigger>
        </TabsList>

        <TabsContent value="alerts" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Alert Management</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3">
                <div className="p-4 border rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertTriangle className="h-5 w-5 text-red-500" />
                    <h3 className="font-semibold">Open Alerts</h3>
                  </div>
                  <p className="text-3xl font-bold">{dashboard.open_alerts}</p>
                  <Link href="/aml/alerts?status=open">
                    <Button variant="link" className="p-0 h-auto">View All →</Button>
                  </Link>
                </div>
                <div className="p-4 border rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <Shield className="h-5 w-5 text-yellow-500" />
                    <h3 className="font-semibold">Under Review</h3>
                  </div>
                  <p className="text-3xl font-bold">{dashboard.under_review_alerts}</p>
                  <Link href="/aml/alerts?status=under_review">
                    <Button variant="link" className="p-0 h-auto">View All →</Button>
                  </Link>
                </div>
                <div className="p-4 border rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <TrendingUp className="h-5 w-5 text-orange-500" />
                    <h3 className="font-semibold">Escalated</h3>
                  </div>
                  <p className="text-3xl font-bold">{dashboard.escalated_alerts}</p>
                  <Link href="/aml/alerts?status=escalated">
                    <Button variant="link" className="p-0 h-auto">View All →</Button>
                  </Link>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="transactions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Transaction Monitoring</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="p-4 border rounded-lg">
                  <h3 className="font-semibold mb-2">Total Monitored</h3>
                  <p className="text-3xl font-bold">{dashboard.total_transactions_monitored.toLocaleString()}</p>
                </div>
                <div className="p-4 border rounded-lg">
                  <h3 className="font-semibold mb-2">High Risk</h3>
                  <p className="text-3xl font-bold text-red-500">{dashboard.high_risk_transactions}</p>
                </div>
                <div className="p-4 border rounded-lg">
                  <h3 className="font-semibold mb-2">Cash Transactions</h3>
                  <p className="text-3xl font-bold">{dashboard.cash_transactions}</p>
                </div>
                <div className="p-4 border rounded-lg">
                  <h3 className="font-semibold mb-2">Cross-Border</h3>
                  <p className="text-3xl font-bold">{dashboard.cross_border_transactions}</p>
                </div>
              </div>
              <div className="mt-4">
                <Link href="/aml/transaction-monitoring">
                  <Button>View Transaction Monitoring</Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="ctr" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Cash Transaction Reports (CTR)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3">
                <div className="p-4 border rounded-lg">
                  <h3 className="font-semibold mb-2">Total Reports</h3>
                  <p className="text-3xl font-bold">{dashboard.total_ctr_reports}</p>
                </div>
                <div className="p-4 border rounded-lg">
                  <h3 className="font-semibold mb-2">Pending</h3>
                  <p className="text-3xl font-bold text-yellow-500">{dashboard.pending_ctr_reports}</p>
                </div>
                <div className="p-4 border rounded-lg">
                  <h3 className="font-semibold mb-2">Submitted to FIU</h3>
                  <p className="text-3xl font-bold text-green-500">{dashboard.submitted_ctr_reports}</p>
                </div>
              </div>
              <div className="mt-4">
                <Link href="/aml/ctr">
                  <Button>Manage CTR Reports</Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="str" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Suspicious Transaction Reports (STR)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3">
                <div className="p-4 border rounded-lg">
                  <h3 className="font-semibold mb-2">Total Reports</h3>
                  <p className="text-3xl font-bold">{dashboard.total_str_reports}</p>
                </div>
                <div className="p-4 border rounded-lg">
                  <h3 className="font-semibold mb-2">Pending</h3>
                  <p className="text-3xl font-bold text-yellow-500">{dashboard.pending_str_reports}</p>
                </div>
                <div className="p-4 border rounded-lg">
                  <h3 className="font-semibold mb-2">Submitted to FIU</h3>
                  <p className="text-3xl font-bold text-green-500">{dashboard.submitted_str_reports}</p>
                </div>
              </div>
              <div className="mt-4">
                <Link href="/aml/str">
                  <Button>Manage STR Reports</Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="pep" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>PEP Screening</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="p-4 border rounded-lg">
                  <h3 className="font-semibold mb-2">Total Screenings</h3>
                  <p className="text-3xl font-bold">{dashboard.total_pep_screenings}</p>
                </div>
                <div className="p-4 border rounded-lg">
                  <h3 className="font-semibold mb-2">Confirmed PEPs</h3>
                  <p className="text-3xl font-bold text-orange-500">{dashboard.confirmed_peps}</p>
                </div>
              </div>
              <div className="mt-4">
                <Link href="/aml/pep-screening">
                  <Button>Manage PEP Screening</Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="sanctions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Sanction List Screening</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="p-4 border rounded-lg">
                  <h3 className="font-semibold mb-2">Total Screenings</h3>
                  <p className="text-3xl font-bold">{dashboard.total_sanction_screenings}</p>
                </div>
                <div className="p-4 border rounded-lg">
                  <h3 className="font-semibold mb-2">Sanction Matches</h3>
                  <p className="text-3xl font-bold text-red-500">{dashboard.sanction_matches}</p>
                </div>
              </div>
              <div className="mt-4">
                <Link href="/aml/sanction-screening">
                  <Button>Manage Sanction Screening</Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-4">
            <Link href="/aml/alerts">
              <Button variant="outline">
                <AlertTriangle className="mr-2 h-4 w-4" />
                View All Alerts
              </Button>
            </Link>
            <Link href="/aml/ctr/create">
              <Button variant="outline">
                <FileText className="mr-2 h-4 w-4" />
                Create CTR Report
              </Button>
            </Link>
            <Link href="/aml/str/create">
              <Button variant="outline">
                <FileText className="mr-2 h-4 w-4" />
                Create STR Report
              </Button>
            </Link>
            <Link href="/aml/pep-screening/create">
              <Button variant="outline">
                <Users className="mr-2 h-4 w-4" />
                Screen for PEP
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
