'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Activity,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  BarChart3,
  Layers,
  Target,
  Shield,
} from 'lucide-react'
import { almService } from '@/services/alm.service'
import { toast } from 'sonner'

export default function ALMDashboardPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [dashboard, setDashboard] = useState<any>(null)
  const [asOfDate, setAsOfDate] = useState(
    new Date().toISOString().split('T')[0]
  )

  useEffect(() => {
    loadDashboard()
  }, [])

  const loadDashboard = async () => {
    try {
      setLoading(true)
      const response = await almService.getDashboard(asOfDate)
      if (response.success) {
        setDashboard(response.data)
      }
    } catch (error: any) {
      toast.error(error.message || 'Failed to load dashboard')
      // Mock data for demonstration
      setDashboard({
        report_date: asOfDate,
        maturity_ladder_summary: {
          total_assets: 5000000000,
          total_liabilities: 4500000000,
          cumulative_gap: 500000000,
          negative_gaps: 2,
        },
        gap_analysis_summary: {
          liquidity_gap: 250000000,
          interest_rate_gap: -50000000,
          critical_buckets: 1,
        },
        liquidity_ratios: {
          lcr: 125.5,
          nsfr: 110.2,
          slr: 22.5,
          all_ratios_compliant: true,
        },
        interest_rate_risk_summary: {
          base_scenario_nii: 450000000,
          worst_case_nii: 380000000,
          max_loss_percentage: 15.6,
        },
        alerts: {
          active_count: 3,
          critical_count: 0,
          high_count: 1,
        },
      })
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount)
  }

  const formatPercentage = (value: number) => {
    return `${value.toFixed(2)}%`
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Asset Liability Management (ALM)</h1>
          <p className="text-muted-foreground">
            Manage liquidity risk, interest rate risk & regulatory compliance
          </p>
        </div>
        <Button onClick={() => router.push('/treasury/alm/quarterly-returns')}>
          <Shield className="mr-2 h-4 w-4" />
          Quarterly Returns
        </Button>
      </div>

      {/* Key Metrics */}
      {dashboard && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Liquidity Coverage Ratio
              </CardTitle>
              <Activity className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">
                {formatPercentage(dashboard.liquidity_ratios.lcr)}
              </div>
              <p className="text-xs text-muted-foreground">
                Target: Above 100% | RBI Requirement
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Net Stable Funding Ratio
              </CardTitle>
              <TrendingUp className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {formatPercentage(dashboard.liquidity_ratios.nsfr)}
              </div>
              <p className="text-xs text-muted-foreground">
                Target: Above 100%
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Cumulative Gap
              </CardTitle>
              <Layers className="h-4 w-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {formatCurrency(
                  dashboard.maturity_ladder_summary.cumulative_gap
                )}
              </div>
              <p className="text-xs text-muted-foreground">
                {dashboard.maturity_ladder_summary.negative_gaps} negative gaps
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Active Alerts
              </CardTitle>
              <AlertTriangle className="h-4 w-4 text-orange-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-600">
                {dashboard.alerts.active_count}
              </div>
              <p className="text-xs text-muted-foreground">
                {dashboard.alerts.critical_count} critical
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Navigation */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="maturity">Maturity Ladder</TabsTrigger>
          <TabsTrigger value="gaps">Gap Analysis</TabsTrigger>
          <TabsTrigger value="ratios">Liquidity Ratios</TabsTrigger>
          <TabsTrigger value="risk">Interest Rate Risk</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <Card
              className="cursor-pointer hover:bg-accent transition-colors"
              onClick={() => router.push('/treasury/alm/maturity-ladder')}
            >
              <CardHeader>
                <Layers className="h-8 w-8 mb-2 text-blue-600" />
                <CardTitle>Maturity Ladder</CardTitle>
                <CardDescription>
                  Track assets & liabilities across 12 time buckets
                </CardDescription>
              </CardHeader>
            </Card>

            <Card
              className="cursor-pointer hover:bg-accent transition-colors"
              onClick={() => router.push('/treasury/alm/gap-analysis')}
            >
              <CardHeader>
                <BarChart3 className="h-8 w-8 mb-2 text-purple-600" />
                <CardTitle>Gap Analysis</CardTitle>
                <CardDescription>
                  Liquidity, interest rate, maturity & duration gaps
                </CardDescription>
              </CardHeader>
            </Card>

            <Card
              className="cursor-pointer hover:bg-accent transition-colors"
              onClick={() => router.push('/treasury/alm/liquidity-ratios')}
            >
              <CardHeader>
                <Activity className="h-8 w-8 mb-2 text-green-600" />
                <CardTitle>Liquidity Ratios</CardTitle>
                <CardDescription>
                  LCR, NSFR, SLR & 20+ liquidity metrics
                </CardDescription>
              </CardHeader>
            </Card>

            <Card
              className="cursor-pointer hover:bg-accent transition-colors"
              onClick={() => router.push('/treasury/alm/interest-rate-risk')}
            >
              <CardHeader>
                <TrendingDown className="h-8 w-8 mb-2 text-red-600" />
                <CardTitle>Interest Rate Risk</CardTitle>
                <CardDescription>
                  7 stress test scenarios with impact analysis
                </CardDescription>
              </CardHeader>
            </Card>

            <Card
              className="cursor-pointer hover:bg-accent transition-colors"
              onClick={() => router.push('/treasury/alm/quarterly-returns')}
            >
              <CardHeader>
                <Shield className="h-8 w-8 mb-2 text-indigo-600" />
                <CardTitle>Quarterly Returns</CardTitle>
                <CardDescription>
                  SLS & IRS returns for RBI compliance
                </CardDescription>
              </CardHeader>
            </Card>

            <Card
              className="cursor-pointer hover:bg-accent transition-colors"
              onClick={() => router.push('/treasury/alm/alerts')}
            >
              <CardHeader>
                <AlertTriangle className="h-8 w-8 mb-2 text-orange-600" />
                <CardTitle>Alert Management</CardTitle>
                <CardDescription>
                  Monitor limit breaches & risk thresholds
                </CardDescription>
              </CardHeader>
            </Card>
          </div>

          {/* Portfolio Summary */}
          {dashboard && (
            <>
              <Card>
                <CardHeader>
                  <CardTitle>Balance Sheet Summary</CardTitle>
                  <CardDescription>
                    As of {new Date(dashboard.report_date).toLocaleDateString()}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">
                          Total Assets
                        </p>
                        <p className="text-2xl font-bold">
                          {formatCurrency(
                            dashboard.maturity_ladder_summary.total_assets
                          )}
                        </p>
                      </div>
                      <Badge variant="outline" className="bg-blue-50">
                        Assets
                      </Badge>
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">
                          Total Liabilities
                        </p>
                        <p className="text-2xl font-bold">
                          {formatCurrency(
                            dashboard.maturity_ladder_summary.total_liabilities
                          )}
                        </p>
                      </div>
                      <Badge variant="outline" className="bg-red-50">
                        Liabilities
                      </Badge>
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">
                          Net Gap (Assets - Liabilities)
                        </p>
                        <p className="text-2xl font-bold text-green-600">
                          {formatCurrency(
                            dashboard.maturity_ladder_summary.cumulative_gap
                          )}
                        </p>
                      </div>
                      <Badge className="bg-green-100 text-green-800">
                        Positive
                      </Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Interest Rate Risk Exposure</CardTitle>
                  <CardDescription>Impact analysis across scenarios</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                      <div>
                        <p className="text-sm font-medium">Base Scenario NII</p>
                        <p className="text-lg font-bold text-blue-700">
                          {formatCurrency(
                            dashboard.interest_rate_risk_summary.base_scenario_nii
                          )}
                        </p>
                      </div>
                      <Target className="h-6 w-6 text-blue-600" />
                    </div>

                    <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                      <div>
                        <p className="text-sm font-medium">Worst Case NII</p>
                        <p className="text-lg font-bold text-red-700">
                          {formatCurrency(
                            dashboard.interest_rate_risk_summary.worst_case_nii
                          )}
                        </p>
                      </div>
                      <TrendingDown className="h-6 w-6 text-red-600" />
                    </div>

                    <div className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
                      <div>
                        <p className="text-sm font-medium">Maximum Loss</p>
                        <p className="text-lg font-bold text-orange-700">
                          {formatPercentage(
                            dashboard.interest_rate_risk_summary
                              .max_loss_percentage
                          )}
                        </p>
                      </div>
                      <AlertTriangle className="h-6 w-6 text-orange-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>

        <TabsContent value="maturity">
          <Card>
            <CardHeader>
              <CardTitle>Maturity Ladder Analysis</CardTitle>
              <CardDescription>
                Assets & liabilities distribution across time buckets
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button
                onClick={() => router.push('/treasury/alm/maturity-ladder')}
              >
                View Maturity Ladder
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="gaps">
          <Card>
            <CardHeader>
              <CardTitle>Gap Analysis</CardTitle>
              <CardDescription>
                Liquidity, interest rate, maturity & duration gap tracking
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button onClick={() => router.push('/treasury/alm/gap-analysis')}>
                View Gap Analysis
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="ratios">
          <Card>
            <CardHeader>
              <CardTitle>Liquidity Ratios</CardTitle>
              <CardDescription>
                Key regulatory and operational liquidity metrics
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button
                onClick={() => router.push('/treasury/alm/liquidity-ratios')}
              >
                View Liquidity Ratios
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="risk">
          <Card>
            <CardHeader>
              <CardTitle>Interest Rate Risk</CardTitle>
              <CardDescription>
                Stress testing and scenario analysis
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button
                onClick={() => router.push('/treasury/alm/interest-rate-risk')}
              >
                View IRR Analysis
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Compliance Status */}
      {dashboard && dashboard.liquidity_ratios.all_ratios_compliant && (
        <Card className="border-green-200 border-2">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <Shield className="h-5 w-5 text-green-600" />
              <CardTitle className="text-green-900">
                RBI Compliance Status
              </CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <p className="text-sm text-green-700">
                All regulatory ratios are within prescribed limits. System is
                compliant with RBI ALM guidelines.
              </p>
              <Badge className="bg-green-600 text-white">Compliant</Badge>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
