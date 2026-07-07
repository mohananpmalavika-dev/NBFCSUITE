'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
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
import { ArrowLeft, Download, BarChart3 } from 'lucide-react'
import { almService, type GapType } from '@/services/alm.service'
import { toast } from 'sonner'

export default function GapAnalysisPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [reportDate, setReportDate] = useState(
    new Date().toISOString().split('T')[0]
  )
  const [gapType, setGapType] = useState<GapType>('liquidity_gap')
  const [gapData, setGapData] = useState<any[]>([])

  const handleAnalyze = async () => {
    try {
      setLoading(true)
      const response = await almService.getGapAnalysis(reportDate, gapType)
      if (response.success && response.data) {
        setGapData(response.data)
        toast.success('Gap analysis loaded')
      }
    } catch (error: any) {
      toast.error(error.message || 'Failed to load gap analysis')
      // Mock data
      setGapData([
        {
          bucket: 'upto_1_month',
          gap_amount: 50000000,
          cumulative_gap: 50000000,
          risk_level: 'low',
        },
        {
          bucket: 'upto_3_months',
          gap_amount: -30000000,
          cumulative_gap: 20000000,
          risk_level: 'medium',
        },
        {
          bucket: 'upto_6_months',
          gap_amount: 80000000,
          cumulative_gap: 100000000,
          risk_level: 'low',
        },
        {
          bucket: 'upto_1_year',
          gap_amount: -50000000,
          cumulative_gap: 50000000,
          risk_level: 'high',
        },
      ])
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

  const totalGap = gapData.reduce((sum, row) => sum + row.gap_amount, 0)
  const negativeGaps = gapData.filter((row) => row.gap_amount < 0).length
  const criticalBuckets = gapData.filter(
    (row) => row.risk_level === 'critical' || row.risk_level === 'high'
  ).length

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="icon" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">Gap Analysis</h1>
            <p className="text-muted-foreground">
              Liquidity, interest rate, maturity & duration gap analysis
            </p>
          </div>
        </div>
        <Button variant="outline">
          <Download className="mr-2 h-4 w-4" />
          Export Report
        </Button>
      </div>

      {/* Analysis Parameters */}
      <Card>
        <CardHeader>
          <CardTitle>Analysis Parameters</CardTitle>
          <CardDescription>Select date and gap type for analysis</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <Label htmlFor="reportDate">Report Date</Label>
              <Input
                id="reportDate"
                type="date"
                value={reportDate}
                onChange={(e) => setReportDate(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="gapType">Gap Type</Label>
              <Select value={gapType} onValueChange={(v) => setGapType(v as GapType)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="liquidity_gap">Liquidity Gap</SelectItem>
                  <SelectItem value="interest_rate_gap">
                    Interest Rate Gap
                  </SelectItem>
                  <SelectItem value="maturity_gap">Maturity Gap</SelectItem>
                  <SelectItem value="duration_gap">Duration Gap</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-end">
              <Button onClick={handleAnalyze} disabled={loading} className="w-full">
                <BarChart3 className="mr-2 h-4 w-4" />
                {loading ? 'Analyzing...' : 'Analyze'}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {gapData.length > 0 && (
        <>
          {/* Summary Cards */}
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">
                  Total {almService.getGapTypeLabel(gapType)}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div
                  className={`text-2xl font-bold ${
                    totalGap >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  {formatCurrency(totalGap)}
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  Net position
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">
                  Negative Gaps
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-orange-600">
                  {negativeGaps}
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  Buckets with deficit
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">
                  High Risk Buckets
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">
                  {criticalBuckets}
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  Requires attention
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Gap Analysis Table */}
          <Card>
            <CardHeader>
              <CardTitle>{almService.getGapTypeLabel(gapType)} Details</CardTitle>
              <CardDescription>Gap amounts by time bucket</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Time Bucket</TableHead>
                    <TableHead className="text-right">Gap Amount</TableHead>
                    <TableHead className="text-right">Cumulative Gap</TableHead>
                    <TableHead>Risk Level</TableHead>
                    <TableHead>Action Required</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {gapData.map((row, index) => (
                    <TableRow key={index}>
                      <TableCell className="font-medium">
                        {almService.getBucketLabel(row.bucket)}
                      </TableCell>
                      <TableCell
                        className={`text-right font-semibold ${
                          row.gap_amount >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}
                      >
                        {formatCurrency(row.gap_amount)}
                      </TableCell>
                      <TableCell className="text-right">
                        {formatCurrency(row.cumulative_gap)}
                      </TableCell>
                      <TableCell>
                        <Badge
                          className={almService.getRiskLevelColor(row.risk_level)}
                        >
                          {row.risk_level.toUpperCase()}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {row.risk_level === 'high' || row.risk_level === 'critical'
                          ? 'Immediate action required'
                          : row.risk_level === 'medium'
                          ? 'Monitor closely'
                          : 'Within acceptable limits'}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          {/* Risk Assessment */}
          <Card>
            <CardHeader>
              <CardTitle>Risk Assessment</CardTitle>
              <CardDescription>
                Analysis of gap distribution and risk exposure
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {criticalBuckets > 0 && (
                  <div className="p-4 bg-red-50 rounded-lg border-2 border-red-200">
                    <p className="text-sm font-medium text-red-900">
                      High Risk Exposure Detected
                    </p>
                    <p className="text-sm text-red-700 mt-1">
                      {criticalBuckets} time bucket(s) show high or critical risk
                      levels. Immediate risk mitigation actions recommended.
                    </p>
                  </div>
                )}

                {negativeGaps > 0 && (
                  <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                    <p className="text-sm font-medium text-yellow-900">
                      Negative Gap Alert
                    </p>
                    <p className="text-sm text-yellow-700 mt-1">
                      {negativeGaps} time bucket(s) show negative gaps. Consider
                      adjusting asset-liability mix for these periods.
                    </p>
                  </div>
                )}

                {totalGap >= 0 && criticalBuckets === 0 && (
                  <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                    <p className="text-sm font-medium text-green-900">
                      Favorable Gap Position
                    </p>
                    <p className="text-sm text-green-700 mt-1">
                      Overall gap position is positive with manageable risk levels
                      across all time buckets.
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </>
      )}

      {gapData.length === 0 && !loading && (
        <Card>
          <CardContent className="text-center py-12">
            <BarChart3 className="mx-auto h-16 w-16 mb-4 opacity-30" />
            <p className="text-lg font-medium text-muted-foreground">
              No gap analysis data
            </p>
            <p className="text-sm text-muted-foreground">
              Select parameters and click Analyze to view gap analysis
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
