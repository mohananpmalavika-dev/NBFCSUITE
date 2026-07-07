'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { almService } from '@/services/almService';
import type { ALMDashboard } from '@/types/alm';
import { formatCurrency, formatPercentage } from '@/lib/utils';
import { 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  CheckCircle2, 
  Activity,
  DollarSign,
  BarChart3,
  Shield
} from 'lucide-react';

export default function ALMDashboardPage() {
  const [dashboard, setDashboard] = useState<ALMDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);

  useEffect(() => {
    loadDashboard();
  }, [selectedDate]);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      const data = await almService.getDashboard(selectedDate);
      setDashboard(data);
    } catch (error) {
      console.error('Failed to load ALM dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRiskLevelColor = (level: string) => {
    switch (level?.toLowerCase()) {
      case 'low': return 'text-green-600 bg-green-50';
      case 'medium': return 'text-yellow-600 bg-yellow-50';
      case 'high': return 'text-orange-600 bg-orange-50';
      case 'critical': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading ALM Dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">ALM Dashboard</h1>
          <p className="text-muted-foreground">
            Asset Liability Management - Comprehensive Overview
          </p>
        </div>
        <div className="flex items-center gap-4">
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="px-4 py-2 border rounded-lg"
          />
          <Button onClick={loadDashboard}>Refresh</Button>
        </div>
      </div>

      {/* Alert Summary */}
      {dashboard && dashboard.critical_alerts > 0 && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            {dashboard.critical_alerts} critical alert{dashboard.critical_alerts > 1 ? 's' : ''} require immediate attention!
          </AlertDescription>
        </Alert>
      )}

      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {/* LCR */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Liquidity Coverage Ratio</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {dashboard?.lcr ? `${dashboard.lcr.toFixed(2)}%` : 'N/A'}
            </div>
            <p className="text-xs text-muted-foreground">
              {dashboard?.lcr && dashboard.lcr >= 100 ? (
                <span className="text-green-600 flex items-center gap-1">
                  <CheckCircle2 className="h-3 w-3" /> Above RBI requirement
                </span>
              ) : (
                <span className="text-red-600 flex items-center gap-1">
                  <AlertTriangle className="h-3 w-3" /> Below RBI requirement
                </span>
              )}
            </p>
          </CardContent>
        </Card>

        {/* NSFR */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Net Stable Funding Ratio</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {dashboard?.nsfr ? `${dashboard.nsfr.toFixed(2)}%` : 'N/A'}
            </div>
            <p className="text-xs text-muted-foreground">
              Stable funding indicator
            </p>
          </CardContent>
        </Card>

        {/* Current Ratio */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Current Ratio</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {dashboard?.current_ratio ? dashboard.current_ratio.toFixed(2) : 'N/A'}
            </div>
            <p className="text-xs text-muted-foreground">
              Short-term liquidity health
            </p>
          </CardContent>
        </Card>

        {/* Active Alerts */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Alerts</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {dashboard?.active_alerts || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              {dashboard?.critical_alerts || 0} critical
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Maturity Summary */}
      {dashboard?.maturity_summary && (
        <Card>
          <CardHeader>
            <CardTitle>Maturity Ladder Summary</CardTitle>
            <CardDescription>Asset-Liability gap analysis across time buckets</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-3">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Assets</p>
                <p className="text-2xl font-bold">
                  {formatCurrency(dashboard.maturity_summary.total_assets)}
                </p>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Liabilities</p>
                <p className="text-2xl font-bold">
                  {formatCurrency(dashboard.maturity_summary.total_liabilities)}
                </p>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Overall Gap</p>
                <p className={`text-2xl font-bold ${dashboard.maturity_summary.overall_gap >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {formatCurrency(dashboard.maturity_summary.overall_gap)}
                </p>
              </div>
            </div>
            <div className="mt-4 pt-4 border-t grid gap-4 md:grid-cols-3">
              <div>
                <p className="text-sm font-medium mb-2">Short-term Gap (Up to 1 Year)</p>
                <p className={`text-xl font-semibold ${dashboard.maturity_summary.short_term_gap >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {formatCurrency(dashboard.maturity_summary.short_term_gap)}
                </p>
              </div>
              <div>
                <p className="text-sm font-medium mb-2">Medium-term Gap (1-3 Years)</p>
                <p className={`text-xl font-semibold ${dashboard.maturity_summary.medium_term_gap >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {formatCurrency(dashboard.maturity_summary.medium_term_gap)}
                </p>
              </div>
              <div>
                <p className="text-sm font-medium mb-2">Long-term Gap (3+ Years)</p>
                <p className={`text-xl font-semibold ${dashboard.maturity_summary.long_term_gap >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {formatCurrency(dashboard.maturity_summary.long_term_gap)}
                </p>
              </div>
            </div>
            <div className="mt-4 pt-4 border-t">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Risk Level:</span>
                <Badge className={getRiskLevelColor(dashboard.maturity_summary.risk_level)}>
                  {dashboard.maturity_summary.risk_level.toUpperCase()}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Gap Analysis Summary */}
      <div className="grid gap-4 md:grid-cols-2">
        {/* Liquidity Gap */}
        {dashboard?.liquidity_gap_summary && (
          <Card>
            <CardHeader>
              <CardTitle>Liquidity Gap Analysis</CardTitle>
              <CardDescription>Cash inflow vs outflow gaps</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Total Gap:</span>
                  <span className={`text-lg font-bold ${dashboard.liquidity_gap_summary.total_gap >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {formatCurrency(dashboard.liquidity_gap_summary.total_gap)}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Limit Breaches:</span>
                  <Badge variant={dashboard.liquidity_gap_summary.limit_breaches > 0 ? 'destructive' : 'default'}>
                    {dashboard.liquidity_gap_summary.limit_breaches}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Risk Level:</span>
                  <Badge className={getRiskLevelColor(dashboard.liquidity_gap_summary.overall_risk_level)}>
                    {dashboard.liquidity_gap_summary.overall_risk_level.toUpperCase()}
                  </Badge>
                </div>
                {dashboard.liquidity_gap_summary.mitigation_required && (
                  <Alert>
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription>
                      Mitigation action required
                    </AlertDescription>
                  </Alert>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Interest Rate Gap */}
        {dashboard?.interest_rate_gap_summary && (
          <Card>
            <CardHeader>
              <CardTitle>Interest Rate Gap Analysis</CardTitle>
              <CardDescription>Rate sensitivity exposure</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Total Gap:</span>
                  <span className={`text-lg font-bold ${dashboard.interest_rate_gap_summary.total_gap >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {formatCurrency(dashboard.interest_rate_gap_summary.total_gap)}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Limit Breaches:</span>
                  <Badge variant={dashboard.interest_rate_gap_summary.limit_breaches > 0 ? 'destructive' : 'default'}>
                    {dashboard.interest_rate_gap_summary.limit_breaches}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Risk Level:</span>
                  <Badge className={getRiskLevelColor(dashboard.interest_rate_gap_summary.overall_risk_level)}>
                    {dashboard.interest_rate_gap_summary.overall_risk_level.toUpperCase()}
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Compliance Status */}
      <Card>
        <CardHeader>
          <CardTitle>Compliance Status</CardTitle>
          <CardDescription>Regulatory limits and compliance monitoring</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            {dashboard?.all_limits_compliant ? (
              <>
                <CheckCircle2 className="h-8 w-8 text-green-600" />
                <div>
                  <p className="font-semibold text-green-600">All Limits Compliant</p>
                  <p className="text-sm text-muted-foreground">
                    All regulatory and internal limits are being met
                  </p>
                </div>
              </>
            ) : (
              <>
                <AlertTriangle className="h-8 w-8 text-red-600" />
                <div>
                  <p className="font-semibold text-red-600">Limit Breaches Detected</p>
                  <p className="text-sm text-muted-foreground">
                    {dashboard?.breached_limits?.length || 0} limit(s) breached: {dashboard?.breached_limits?.join(', ')}
                  </p>
                </div>
              </>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-4">
            <Button variant="outline" className="w-full" onClick={() => window.location.href = '/treasury/alm/maturity-ladder'}>
              View Maturity Ladder
            </Button>
            <Button variant="outline" className="w-full" onClick={() => window.location.href = '/treasury/alm/gap-analysis'}>
              Gap Analysis
            </Button>
            <Button variant="outline" className="w-full" onClick={() => window.location.href = '/treasury/alm/liquidity-ratios'}>
              Liquidity Ratios
            </Button>
            <Button variant="outline" className="w-full" onClick={() => window.location.href = '/treasury/alm/alerts'}>
              View Alerts
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
