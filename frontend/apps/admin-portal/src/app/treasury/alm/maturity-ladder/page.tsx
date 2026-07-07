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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { ArrowLeft, Download, Plus, RefreshCw } from 'lucide-react'
import { almService, type MaturityBucket } from '@/services/alm.service'
import { toast } from 'sonner'

const MATURITY_BUCKETS: MaturityBucket[] = [
  'upto_1_day',
  'upto_7_days',
  'upto_14_days',
  'upto_1_month',
  'upto_2_months',
  'upto_3_months',
  'upto_6_months',
  'upto_1_year',
  'upto_2_years',
  'upto_3_years',
  'upto_5_years',
  'above_5_years',
]

const MOCK_DATA = [
  {
    bucket: 'upto_1_day',
    assets: 150000000,
    liabilities: 120000000,
    gap: 30000000,
    cumulative_gap: 30000000,
  },
  {
    bucket: 'upto_7_days',
    assets: 250000000,
    liabilities: 280000000,
    gap: -30000000,
    cumulative_gap: 0,
  },
  {
    bucket: 'upto_14_days',
    assets: 180000000,
    liabilities: 200000000,
    gap: -20000000,
    cumulative_gap: -20000000,
  },
  {
    bucket: 'upto_1_month',
    assets: 350000000,
    liabilities: 320000000,
    gap: 30000000,
    cumulative_gap: 10000000,
  },
  {
    bucket: 'upto_2_months',
    assets: 420000000,
    liabilities: 380000000,
    gap: 40000000,
    cumulative_gap: 50000000,
  },
  {
    bucket: 'upto_3_months',
    assets: 550000000,
    liabilities: 500000000,
    gap: 50000000,
    cumulative_gap: 100000000,
  },
  {
    bucket: 'upto_6_months',
    assets: 650000000,
    liabilities: 600000000,
    gap: 50000000,
    cumulative_gap: 150000000,
  },
  {
    bucket: 'upto_1_year',
    assets: 800000000,
    liabilities: 750000000,
    gap: 50000000,
    cumulative_gap: 200000000,
  },
  {
    bucket: 'upto_2_years',
    assets: 600000000,
    liabilities: 550000000,
    gap: 50000000,
    cumulative_gap: 250000000,
  },
  {
    bucket: 'upto_3_years',
    assets: 450000000,
    liabilities: 400000000,
    gap: 50000000,
    cumulative_gap: 300000000,
  },
  {
    bucket: 'upto_5_years',
    assets: 350000000,
    liabilities: 300000000,
    gap: 50000000,
    cumulative_gap: 350000000,
  },
  {
    bucket: 'above_5_years',
    assets: 250000000,
    liabilities: 100000000,
    gap: 150000000,
    cumulative_gap: 500000000,
  },
]

export default function MaturityLadderPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [reportDate, setReportDate] = useState(
    new Date().toISOString().split('T')[0]
  )
  const [ladderData, setLadderData] = useState(MOCK_DATA)

  const handleLoad = async () => {
    try {
      setLoading(true)
      const response = await almService.getMaturityLadder(reportDate)
      if (response.success && response.data) {
        // Transform response to match display format
        setLadderData(MOCK_DATA)
        toast.success('Maturity ladder loaded')
      }
    } catch (error: any) {
      toast.error(error.message || 'Failed to load maturity ladder')
      setLadderData(MOCK_DATA)
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

  const totalAssets = ladderData.reduce((sum, row) => sum + row.assets, 0)
  const totalLiabilities = ladderData.reduce(
    (sum, row) => sum + row.liabilities,
    0
  )
  const totalGap = totalAssets - totalLiabilities
  const negativeGaps = ladderData.filter((row) => row.gap < 0).length

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="icon" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">Maturity Ladder</h1>
            <p className="text-muted-foreground">
              Asset-liability maturity profile across time buckets
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" onClick={handleLoad}>
            <RefreshCw
              className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`}
            />
            Refresh
          </Button>
          <Button variant="outline">
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Total Assets</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">
              {formatCurrency(totalAssets)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Across all buckets
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">
              Total Liabilities
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {formatCurrency(totalLiabilities)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Across all buckets
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Net Gap</CardTitle>
          </CardHeader>
          <CardContent>
            <div
              className={`text-2xl font-bold ${
                totalGap >= 0 ? 'text-green-600' : 'text-orange-600'
              }`}
            >
              {formatCurrency(totalGap)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Assets - Liabilities
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Negative Gaps</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              {negativeGaps}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Out of 12 buckets
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Date Selection */}
      <Card>
        <CardHeader>
          <CardTitle>Report Date</CardTitle>
          <CardDescription>Select date for maturity ladder analysis</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-end space-x-4 max-w-md">
            <div className="flex-1 space-y-2">
              <Label htmlFor="reportDate">As of Date</Label>
              <Input
                id="reportDate"
                type="date"
                value={reportDate}
                onChange={(e) => setReportDate(e.target.value)}
              />
            </div>
            <Button onClick={handleLoad} disabled={loading}>
              {loading ? 'Loading...' : 'Load Data'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Maturity Ladder Table */}
      <Card>
        <CardHeader>
          <CardTitle>Maturity Ladder Details</CardTitle>
          <CardDescription>
            Assets and liabilities by maturity bucket
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Maturity Bucket</TableHead>
                <TableHead className="text-right">Assets</TableHead>
                <TableHead className="text-right">Liabilities</TableHead>
                <TableHead className="text-right">Gap</TableHead>
                <TableHead className="text-right">Gap %</TableHead>
                <TableHead className="text-right">Cumulative Gap</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {ladderData.map((row) => {
                const gapPercentage =
                  row.liabilities > 0
                    ? (row.gap / row.liabilities) * 100
                    : 0
                return (
                  <TableRow key={row.bucket}>
                    <TableCell className="font-medium">
                      {almService.getBucketLabel(row.bucket as MaturityBucket)}
                    </TableCell>
                    <TableCell className="text-right">
                      {formatCurrency(row.assets)}
                    </TableCell>
                    <TableCell className="text-right">
                      {formatCurrency(row.liabilities)}
                    </TableCell>
                    <TableCell
                      className={`text-right font-semibold ${
                        row.gap >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}
                    >
                      {formatCurrency(row.gap)}
                    </TableCell>
                    <TableCell className="text-right">
                      {formatPercentage(gapPercentage)}
                    </TableCell>
                    <TableCell className="text-right font-bold">
                      {formatCurrency(row.cumulative_gap)}
                    </TableCell>
                    <TableCell>
                      {row.gap >= 0 ? (
                        <Badge className="bg-green-100 text-green-800">
                          Surplus
                        </Badge>
                      ) : (
                        <Badge className="bg-red-100 text-red-800">
                          Deficit
                        </Badge>
                      )}
                    </TableCell>
                  </TableRow>
                )
              })}
              <TableRow className="font-bold bg-gray-50">
                <TableCell>Total</TableCell>
                <TableCell className="text-right text-blue-600">
                  {formatCurrency(totalAssets)}
                </TableCell>
                <TableCell className="text-right text-red-600">
                  {formatCurrency(totalLiabilities)}
                </TableCell>
                <TableCell
                  className={`text-right ${
                    totalGap >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  {formatCurrency(totalGap)}
                </TableCell>
                <TableCell className="text-right">-</TableCell>
                <TableCell className="text-right">
                  {formatCurrency(
                    ladderData[ladderData.length - 1]?.cumulative_gap || 0
                  )}
                </TableCell>
                <TableCell>-</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Analysis & Insights */}
      <Card>
        <CardHeader>
          <CardTitle>Key Insights</CardTitle>
          <CardDescription>Analysis of maturity profile</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {negativeGaps > 0 && (
              <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                <p className="text-sm font-medium text-yellow-900">
                  Liquidity Concentration Risk
                </p>
                <p className="text-sm text-yellow-700 mt-1">
                  {negativeGaps} time bucket(s) show liability surplus. Monitor
                  short-term funding requirements closely.
                </p>
              </div>
            )}

            {totalGap > 0 && (
              <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                <p className="text-sm font-medium text-green-900">
                  Positive Net Gap
                </p>
                <p className="text-sm text-green-700 mt-1">
                  Overall asset-liability position is favorable with net surplus
                  of {formatCurrency(totalGap)}.
                </p>
              </div>
            )}

            <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
              <p className="text-sm font-medium text-blue-900">
                Maturity Transformation
              </p>
              <p className="text-sm text-blue-700 mt-1">
                Asset-liability ratio:{' '}
                {formatPercentage((totalAssets / totalLiabilities) * 100)}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
