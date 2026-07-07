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
import { ArrowLeft, Download, TrendingUp, TrendingDown } from 'lucide-react'
import { npaService } from '@/services/npa.service'
import { toast } from 'sonner'

const MOCK_COHORTS = [
  {
    cohort_period: '2024-Q1',
    loans_originated: 150,
    original_amount: 75000000,
    current_outstanding: 68000000,
    npa_amount: 3400000,
    npa_percentage: 5.0,
    age_buckets: {
      '0-30': 85,
      '31-60': 40,
      '61-90': 15,
      '90+': 10,
    },
  },
  {
    cohort_period: '2023-Q4',
    loans_originated: 180,
    original_amount: 90000000,
    current_outstanding: 75000000,
    npa_amount: 6000000,
    npa_percentage: 8.0,
    age_buckets: {
      '0-30': 90,
      '31-60': 50,
      '61-90': 25,
      '90+': 15,
    },
  },
  {
    cohort_period: '2023-Q3',
    loans_originated: 160,
    original_amount: 80000000,
    current_outstanding: 60000000,
    npa_amount: 7200000,
    npa_percentage: 12.0,
    age_buckets: {
      '0-30': 70,
      '31-60': 45,
      '61-90': 30,
      '90+': 15,
    },
  },
  {
    cohort_period: '2023-Q2',
    loans_originated: 140,
    original_amount: 70000000,
    current_outstanding: 45000000,
    npa_amount: 6750000,
    npa_percentage: 15.0,
    age_buckets: {
      '0-30': 50,
      '31-60': 40,
      '61-90': 30,
      '90+': 20,
    },
  },
]

export default function VintageAnalysisPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [asOfDate, setAsOfDate] = useState(
    new Date().toISOString().split('T')[0]
  )
  const [cohortBy, setCohortBy] = useState<'month' | 'quarter' | 'year'>('quarter')
  const [cohorts, setCohorts] = useState(MOCK_COHORTS)

  const handleGenerate = async () => {
    try {
      setLoading(true)
      const response = await npaService.getVintageAnalysis({
        as_of_date: asOfDate,
        cohort_by: cohortBy,
      })

      if (response.success) {
        setCohorts(response.data.cohorts || MOCK_COHORTS)
        toast.success('Vintage analysis generated')
      }
    } catch (error: any) {
      toast.error(error.message || 'Failed to generate analysis')
      setCohorts(MOCK_COHORTS)
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

  const getTrendIcon = (current: number, previous: number) => {
    if (current > previous) {
      return <TrendingUp className="h-4 w-4 text-red-600" />
    }
    return <TrendingDown className="h-4 w-4 text-green-600" />
  }

  const totalLoansOriginated = cohorts.reduce(
    (sum, c) => sum + c.loans_originated,
    0
  )
  const totalOriginalAmount = cohorts.reduce(
    (sum, c) => sum + c.original_amount,
    0
  )
  const totalCurrentOutstanding = cohorts.reduce(
    (sum, c) => sum + c.current_outstanding,
    0
  )
  const totalNPAAmount = cohorts.reduce((sum, c) => sum + c.npa_amount, 0)
  const overallNPAPercentage =
    totalCurrentOutstanding > 0
      ? (totalNPAAmount / totalCurrentOutstanding) * 100
      : 0

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="icon" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">Vintage Analysis</h1>
            <p className="text-muted-foreground">
              Cohort-based NPA analysis by origination period
            </p>
          </div>
        </div>
        <Button variant="outline">
          <Download className="mr-2 h-4 w-4" />
          Export Report
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Analysis Parameters</CardTitle>
          <CardDescription>
            Select date and cohort grouping for vintage analysis
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <Label htmlFor="asOfDate">As of Date</Label>
              <Input
                id="asOfDate"
                type="date"
                value={asOfDate}
                onChange={(e) => setAsOfDate(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="cohortBy">Cohort Grouping</Label>
              <Select
                value={cohortBy}
                onValueChange={(value: any) => setCohortBy(value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="month">Monthly</SelectItem>
                  <SelectItem value="quarter">Quarterly</SelectItem>
                  <SelectItem value="year">Yearly</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-end">
              <Button onClick={handleGenerate} disabled={loading} className="w-full">
                {loading ? 'Generating...' : 'Generate Analysis'}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Summary Statistics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">
              Total Loans Originated
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalLoansOriginated}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {cohorts.length} cohorts
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Original Amount</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(totalOriginalAmount)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">Total disbursed</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">
              Current Outstanding
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(totalCurrentOutstanding)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {formatPercentage(
                (totalCurrentOutstanding / totalOriginalAmount) * 100
              )}{' '}
              of original
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Overall NPA Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {formatPercentage(overallNPAPercentage)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {formatCurrency(totalNPAAmount)} NPA
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Cohort Analysis Table */}
      <Card>
        <CardHeader>
          <CardTitle>Cohort-wise Analysis</CardTitle>
          <CardDescription>
            Performance metrics by origination cohort
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Cohort Period</TableHead>
                <TableHead className="text-right">Loans Originated</TableHead>
                <TableHead className="text-right">Original Amount</TableHead>
                <TableHead className="text-right">Current Outstanding</TableHead>
                <TableHead className="text-right">NPA Amount</TableHead>
                <TableHead className="text-right">NPA %</TableHead>
                <TableHead className="text-right">Trend</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {cohorts.map((cohort, index) => (
                <TableRow key={cohort.cohort_period}>
                  <TableCell className="font-medium">
                    {cohort.cohort_period}
                  </TableCell>
                  <TableCell className="text-right">
                    {cohort.loans_originated}
                  </TableCell>
                  <TableCell className="text-right">
                    {formatCurrency(cohort.original_amount)}
                  </TableCell>
                  <TableCell className="text-right">
                    {formatCurrency(cohort.current_outstanding)}
                  </TableCell>
                  <TableCell className="text-right font-semibold text-red-600">
                    {formatCurrency(cohort.npa_amount)}
                  </TableCell>
                  <TableCell className="text-right font-semibold">
                    {formatPercentage(cohort.npa_percentage)}
                  </TableCell>
                  <TableCell className="text-right">
                    {index < cohorts.length - 1 &&
                      getTrendIcon(
                        cohort.npa_percentage,
                        cohorts[index + 1].npa_percentage
                      )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Age Bucket Distribution */}
      <Card>
        <CardHeader>
          <CardTitle>DPD Distribution by Cohort</CardTitle>
          <CardDescription>
            Distribution of accounts across Days Past Due buckets
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Cohort Period</TableHead>
                <TableHead className="text-right">0-30 DPD</TableHead>
                <TableHead className="text-right">31-60 DPD</TableHead>
                <TableHead className="text-right">61-90 DPD</TableHead>
                <TableHead className="text-right">90+ DPD</TableHead>
                <TableHead className="text-right">Total</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {cohorts.map((cohort) => {
                const buckets = cohort.age_buckets
                const total =
                  buckets['0-30'] +
                  buckets['31-60'] +
                  buckets['61-90'] +
                  buckets['90+']
                return (
                  <TableRow key={cohort.cohort_period}>
                    <TableCell className="font-medium">
                      {cohort.cohort_period}
                    </TableCell>
                    <TableCell className="text-right">
                      {buckets['0-30']} (
                      {formatPercentage((buckets['0-30'] / total) * 100)})
                    </TableCell>
                    <TableCell className="text-right">
                      {buckets['31-60']} (
                      {formatPercentage((buckets['31-60'] / total) * 100)})
                    </TableCell>
                    <TableCell className="text-right">
                      {buckets['61-90']} (
                      {formatPercentage((buckets['61-90'] / total) * 100)})
                    </TableCell>
                    <TableCell className="text-right font-semibold text-red-600">
                      {buckets['90+']} (
                      {formatPercentage((buckets['90+'] / total) * 100)})
                    </TableCell>
                    <TableCell className="text-right font-bold">{total}</TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Insights */}
      <Card>
        <CardHeader>
          <CardTitle>Key Insights</CardTitle>
          <CardDescription>Analysis highlights and trends</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="p-3 bg-blue-50 rounded-lg">
              <p className="text-sm font-medium text-blue-900">
                Portfolio Aging Pattern
              </p>
              <p className="text-sm text-blue-700 mt-1">
                Older cohorts show higher NPA rates, with Q2-2023 at{' '}
                {formatPercentage(cohorts[cohorts.length - 1]?.npa_percentage || 0)}{' '}
                vs Q1-2024 at {formatPercentage(cohorts[0]?.npa_percentage || 0)}
              </p>
            </div>

            <div className="p-3 bg-yellow-50 rounded-lg">
              <p className="text-sm font-medium text-yellow-900">
                Early Warning Indicators
              </p>
              <p className="text-sm text-yellow-700 mt-1">
                Monitor recent cohorts closely as they age - historical patterns
                suggest NPA rates increase over time
              </p>
            </div>

            <div className="p-3 bg-green-50 rounded-lg">
              <p className="text-sm font-medium text-green-900">
                Collection Efficiency
              </p>
              <p className="text-sm text-green-700 mt-1">
                Recent cohorts performing better than historical average,
                indicating improved underwriting standards
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
