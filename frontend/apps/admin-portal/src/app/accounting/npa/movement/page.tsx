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
import { Separator } from '@/components/ui/separator'
import { ArrowLeft, TrendingUp, TrendingDown, Download, BarChart3 } from 'lucide-react'
import { npaService } from '@/services/npa.service'
import { toast } from 'sonner'

export default function NPAMovementReportPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [fromDate, setFromDate] = useState('')
  const [toDate, setToDate] = useState('')
  const [report, setReport] = useState<any>(null)

  const loadMovementReport = async () => {
    if (!fromDate || !toDate) {
      toast.error('Please select both dates')
      return
    }

    try {
      setLoading(true)
      const response = await npaService.getNPAMovementReport({
        from_date: fromDate,
        to_date: toDate,
      })

      setReport(response.data)
      toast.success('Movement report generated successfully')
    } catch (error: any) {
      toast.error(error.message || 'Failed to generate report')
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

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="icon" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">NPA Movement Report</h1>
            <p className="text-muted-foreground">
              Track additions, reductions, and net movement
            </p>
          </div>
        </div>
        {report && (
          <Button variant="outline">
            <Download className="mr-2 h-4 w-4" />
            Export Report
          </Button>
        )}
      </div>

      {/* Date Selection */}
      <Card>
        <CardHeader>
          <CardTitle>Report Period</CardTitle>
          <CardDescription>Select date range for movement analysis</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <Label htmlFor="fromDate">From Date</Label>
              <Input
                id="fromDate"
                type="date"
                value={fromDate}
                onChange={(e) => setFromDate(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="toDate">To Date</Label>
              <Input
                id="toDate"
                type="date"
                value={toDate}
                onChange={(e) => setToDate(e.target.value)}
              />
            </div>

            <div className="flex items-end">
              <Button onClick={loadMovementReport} disabled={loading} className="w-full">
                <BarChart3 className="mr-2 h-4 w-4" />
                {loading ? 'Generating...' : 'Generate Report'}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {report && (
        <>
          {/* Opening and Closing Balance */}
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Opening Balance</CardTitle>
                <CardDescription>
                  As of {new Date(fromDate).toLocaleDateString()}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">NPA Accounts</span>
                    <span className="font-bold">{report.opening_balance.npa_accounts}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">NPA Amount</span>
                    <span className="font-bold">
                      {formatCurrency(report.opening_balance.npa_amount)}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Closing Balance</CardTitle>
                <CardDescription>
                  As of {new Date(toDate).toLocaleDateString()}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">NPA Accounts</span>
                    <span className="font-bold">{report.closing_balance.npa_accounts}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">NPA Amount</span>
                    <span className="font-bold">
                      {formatCurrency(report.closing_balance.npa_amount)}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Net Movement */}
          <Card>
            <CardHeader>
              <CardTitle>Net Movement Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3">
                <div className="text-center p-4 bg-red-50 rounded-lg">
                  <TrendingUp className="mx-auto h-8 w-8 text-red-600 mb-2" />
                  <div className="text-2xl font-bold text-red-600">
                    {report.closing_balance.npa_accounts - report.opening_balance.npa_accounts}
                  </div>
                  <p className="text-sm text-muted-foreground">Net Change (Accounts)</p>
                </div>

                <div className="text-center p-4 bg-orange-50 rounded-lg">
                  <TrendingUp className="mx-auto h-8 w-8 text-orange-600 mb-2" />
                  <div className="text-2xl font-bold text-orange-600">
                    {formatCurrency(
                      report.closing_balance.npa_amount - report.opening_balance.npa_amount
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground">Net Change (Amount)</p>
                </div>

                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <BarChart3 className="mx-auto h-8 w-8 text-blue-600 mb-2" />
                  <div className="text-2xl font-bold text-blue-600">
                    {(((report.closing_balance.npa_amount - report.opening_balance.npa_amount) /
                      report.opening_balance.npa_amount) *
                      100).toFixed(2)}%
                  </div>
                  <p className="text-sm text-muted-foreground">Growth Rate</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Additions */}
          <Card>
            <CardHeader>
              <div className="flex items-center space-x-2">
                <TrendingUp className="h-5 w-5 text-red-600" />
                <CardTitle className="text-red-600">Additions to NPA</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="p-4 border rounded-lg">
                  <p className="text-sm text-muted-foreground mb-1">Fresh NPAs</p>
                  <p className="text-2xl font-bold">
                    {report.additions.fresh_npa.account_count}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {formatCurrency(report.additions.fresh_npa.amount)}
                  </p>
                </div>

                <div className="p-4 border rounded-lg">
                  <p className="text-sm text-muted-foreground mb-1">Increased Provision</p>
                  <p className="text-2xl font-bold">
                    {report.additions.increased_provision.account_count}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {formatCurrency(report.additions.increased_provision.amount)}
                  </p>
                </div>
              </div>

              {report.additions.fresh_npa.accounts?.length > 0 && (
                <>
                  <Separator />
                  <div>
                    <h4 className="font-semibold mb-3">Fresh NPA Details</h4>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Loan Account</TableHead>
                          <TableHead>Customer</TableHead>
                          <TableHead>Previous Category</TableHead>
                          <TableHead>Current Category</TableHead>
                          <TableHead className="text-right">Amount</TableHead>
                          <TableHead>Movement Date</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {report.additions.fresh_npa.accounts.map((acc: any) => (
                          <TableRow key={acc.loan_account_id}>
                            <TableCell className="font-medium">
                              {acc.loan_account_number}
                            </TableCell>
                            <TableCell>{acc.customer_name}</TableCell>
                            <TableCell>
                              <Badge variant="outline">
                                {acc.previous_category?.replace(/_/g, ' ')}
                              </Badge>
                            </TableCell>
                            <TableCell>
                              <Badge className="bg-red-100 text-red-800">
                                {acc.current_category.replace(/_/g, ' ')}
                              </Badge>
                            </TableCell>
                            <TableCell className="text-right">
                              {formatCurrency(acc.outstanding_amount)}
                            </TableCell>
                            <TableCell>
                              {new Date(acc.movement_date).toLocaleDateString()}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                </>
              )}
            </CardContent>
          </Card>

          {/* Reductions */}
          <Card>
            <CardHeader>
              <div className="flex items-center space-x-2">
                <TrendingDown className="h-5 w-5 text-green-600" />
                <CardTitle className="text-green-600">Reductions from NPA</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3">
                <div className="p-4 border rounded-lg">
                  <p className="text-sm text-muted-foreground mb-1">Upgrades</p>
                  <p className="text-2xl font-bold text-green-600">
                    {report.reductions.upgrades.account_count}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {formatCurrency(report.reductions.upgrades.amount)}
                  </p>
                </div>

                <div className="p-4 border rounded-lg">
                  <p className="text-sm text-muted-foreground mb-1">Recoveries</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {report.reductions.recoveries.account_count}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {formatCurrency(report.reductions.recoveries.amount)}
                  </p>
                </div>

                <div className="p-4 border rounded-lg">
                  <p className="text-sm text-muted-foreground mb-1">Write-offs</p>
                  <p className="text-2xl font-bold text-gray-600">
                    {report.reductions.write_offs.account_count}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {formatCurrency(report.reductions.write_offs.amount)}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Category-wise Movement */}
          <Card>
            <CardHeader>
              <CardTitle>Category-wise Movement Matrix</CardTitle>
              <CardDescription>
                Account movement across NPA categories
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Category</TableHead>
                    <TableHead className="text-right">Opening</TableHead>
                    <TableHead className="text-right">Additions</TableHead>
                    <TableHead className="text-right">Upgrades</TableHead>
                    <TableHead className="text-right">Downgrades</TableHead>
                    <TableHead className="text-right">Closing</TableHead>
                    <TableHead className="text-right">Net Change</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {Object.entries(report.movements_by_category).map(([category, data]: [string, any]) => (
                    <TableRow key={category}>
                      <TableCell className="font-medium">
                        {category.replace(/_/g, ' ')}
                      </TableCell>
                      <TableCell className="text-right">{data.opening}</TableCell>
                      <TableCell className="text-right text-red-600">
                        +{data.additions}
                      </TableCell>
                      <TableCell className="text-right text-green-600">
                        -{data.upgrades}
                      </TableCell>
                      <TableCell className="text-right text-orange-600">
                        +{data.downgrades}
                      </TableCell>
                      <TableCell className="text-right font-bold">
                        {data.closing}
                      </TableCell>
                      <TableCell className="text-right font-bold">
                        {data.closing - data.opening > 0 ? '+' : ''}
                        {data.closing - data.opening}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </>
      )}

      {!report && !loading && (
        <Card>
          <CardContent className="text-center py-12">
            <BarChart3 className="mx-auto h-16 w-16 mb-4 opacity-30" />
            <p className="text-lg font-medium text-muted-foreground">
              No report generated
            </p>
            <p className="text-sm text-muted-foreground">
              Select date range and click Generate Report
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
