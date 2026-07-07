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
  AlertTriangle,
  TrendingDown,
  TrendingUp,
  FileText,
  Calculator,
  BarChart3,
  PlayCircle,
} from 'lucide-react'
import { npaService } from '@/services/npa.service'
import { toast } from 'sonner'

export default function NPAManagementPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [summary, setSummary] = useState<any>(null)

  useEffect(() => {
    loadNPASummary()
  }, [])

  const loadNPASummary = async () => {
    try {
      setLoading(true)
      const response = await npaService.getNPASummary()
      if (response.success) {
        setSummary(response.data)
      }
    } catch (error: any) {
      toast.error(error.message || 'Failed to load NPA summary')
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
          <h1 className="text-3xl font-bold">NPA Management</h1>
          <p className="text-muted-foreground">
            Non-Performing Asset classification, provisioning & reporting
          </p>
        </div>
        <Button
          onClick={() => router.push('/accounting/npa/batch-classification')}
        >
          <PlayCircle className="mr-2 h-4 w-4" />
          Run Monthly Classification
        </Button>
      </div>

      {/* Key Metrics */}
      {summary && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Gross NPA Ratio
              </CardTitle>
              <TrendingDown className="h-4 w-4 text-red-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                {formatPercentage(summary.gross_npa_ratio)}
              </div>
              <p className="text-xs text-muted-foreground">
                Target: Below 5%
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Net NPA Ratio
              </CardTitle>
              <TrendingUp className="h-4 w-4 text-orange-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-600">
                {formatPercentage(summary.net_npa_ratio)}
              </div>
              <p className="text-xs text-muted-foreground">
                Target: Below 2.5%
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Total NPA Amount
              </CardTitle>
              <AlertTriangle className="h-4 w-4 text-red-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {formatCurrency(summary.npa_assets.outstanding_amount)}
              </div>
              <p className="text-xs text-muted-foreground">
                {summary.npa_assets.account_count} accounts
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                SMA Accounts
              </CardTitle>
              <AlertTriangle className="h-4 w-4 text-yellow-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-600">
                {summary.sma_assets.account_count}
              </div>
              <p className="text-xs text-muted-foreground">
                Early warning indicators
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Navigation */}
      <Tabs defaultValue="dashboard" className="space-y-4">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
          <TabsTrigger value="classification">Classification</TabsTrigger>
          <TabsTrigger value="provisioning">Provisioning</TabsTrigger>
          <TabsTrigger value="reports">Reports</TabsTrigger>
          <TabsTrigger value="regulatory">Regulatory</TabsTrigger>
        </TabsList>

        <TabsContent value="dashboard" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <Card className="cursor-pointer hover:bg-accent transition-colors"
              onClick={() => router.push('/accounting/npa/register')}>
              <CardHeader>
                <FileText className="h-8 w-8 mb-2 text-blue-600" />
                <CardTitle>Asset Classification Register</CardTitle>
                <CardDescription>
                  View complete portfolio classification by NPA category
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="cursor-pointer hover:bg-accent transition-colors"
              onClick={() => router.push('/accounting/npa/calculator')}>
              <CardHeader>
                <Calculator className="h-8 w-8 mb-2 text-green-600" />
                <CardTitle>Provisioning Calculator</CardTitle>
                <CardDescription>
                  Calculate RBI-compliant provisioning requirements
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="cursor-pointer hover:bg-accent transition-colors"
              onClick={() => router.push('/accounting/npa/movement')}>
              <CardHeader>
                <BarChart3 className="h-8 w-8 mb-2 text-purple-600" />
                <CardTitle>Movement Reports</CardTitle>
                <CardDescription>
                  Track NPA additions, upgrades, and write-offs
                </CardDescription>
              </CardHeader>
            </Card>
          </div>

          {/* Portfolio Distribution */}
          {summary && (
            <Card>
              <CardHeader>
                <CardTitle>Portfolio Distribution</CardTitle>
                <CardDescription>
                  Distribution of loans across NPA categories
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline" className="bg-green-50">
                        Standard
                      </Badge>
                      <span className="text-sm">
                        {formatPercentage(summary.standard_assets.percentage)}
                      </span>
                    </div>
                    <div className="text-sm font-medium">
                      {formatCurrency(summary.standard_assets.outstanding_amount)}
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline" className="bg-yellow-50">
                        SMA
                      </Badge>
                      <span className="text-sm">
                        {formatPercentage(summary.sma_assets.percentage)}
                      </span>
                    </div>
                    <div className="text-sm font-medium">
                      {formatCurrency(summary.sma_assets.outstanding_amount)}
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline" className="bg-red-50">
                        NPA
                      </Badge>
                      <span className="text-sm">
                        {formatPercentage(summary.npa_assets.percentage)}
                      </span>
                    </div>
                    <div className="text-sm font-medium">
                      {formatCurrency(summary.npa_assets.outstanding_amount)}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="classification">
          <Card>
            <CardHeader>
              <CardTitle>Loan Classification</CardTitle>
              <CardDescription>
                Classify loans based on Days Past Due (DPD)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button onClick={() => router.push('/accounting/npa/classify')}>
                Classify Loan
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="provisioning">
          <Card>
            <CardHeader>
              <CardTitle>Provisioning Management</CardTitle>
              <CardDescription>
                Calculate and create provisions as per RBI norms
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-x-2">
                <Button onClick={() => router.push('/accounting/npa/calculator')}>
                  Calculate Provisioning
                </Button>
                <Button variant="outline" onClick={() => router.push('/accounting/npa/provisions')}>
                  View Provisions
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="reports">
          <div className="grid gap-4 md:grid-cols-2">
            <Card className="cursor-pointer hover:bg-accent transition-colors"
              onClick={() => router.push('/accounting/npa/register')}>
              <CardHeader>
                <CardTitle>Asset Classification Register</CardTitle>
                <CardDescription>
                  Complete register by NPA category
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="cursor-pointer hover:bg-accent transition-colors"
              onClick={() => router.push('/accounting/npa/movement')}>
              <CardHeader>
                <CardTitle>NPA Movement Report</CardTitle>
                <CardDescription>
                  Track changes over time
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="cursor-pointer hover:bg-accent transition-colors"
              onClick={() => router.push('/accounting/npa/vintage')}>
              <CardHeader>
                <CardTitle>Vintage Analysis</CardTitle>
                <CardDescription>
                  Cohort-based NPA analysis
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="regulatory">
          <div className="grid gap-4 md:grid-cols-2">
            <Card className="cursor-pointer hover:bg-accent transition-colors"
              onClick={() => router.push('/accounting/npa/rbi-return')}>
              <CardHeader>
                <CardTitle>RBI NPA Return</CardTitle>
                <CardDescription>
                  Generate regulatory return format
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="cursor-pointer hover:bg-accent transition-colors"
              onClick={() => router.push('/accounting/npa/pcr')}>
              <CardHeader>
                <CardTitle>Provisioning Coverage Ratio</CardTitle>
                <CardDescription>
                  Calculate and track PCR
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
