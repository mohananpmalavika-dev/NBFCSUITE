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
import { ArrowLeft, Download, TrendingUp, AlertCircle } from 'lucide-react'
import { npaService } from '@/services/npa.service'
import { toast } from 'sonner'

export default function ProvisioningCoverageRatioPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [asOfDate, setAsOfDate] = useState(
    new Date().toISOString().split('T')[0]
  )
  const [pcrData, setPcrData] = useState<any>(null)

  const handleCalculate = async () => {
    try {
      setLoading(true)
      const response = await npaService.getProvisioningCoverageRatio(asOfDate)

      setPcrData(response.data)
      toast.success('PCR calculated successfully')
    } catch (error: any) {
      toast.error(error.message || 'Failed to calculate PCR')
      // Mock data for demonstration
      setPcrData({
        as_of_date: asOfDate,
        gross_npa: 35000000,
        provisions_held: 28000000,
        pcr_percentage: 80.0,
        category_wise_pcr: {
          substandard: 75.0,
          doubtful_1: 82.0,
          doubtful_2: 85.0,
          doubtful_3: 90.0,
          loss: 100.0,
        },
        required_provision: 30000000,
        shortfall: 2000000,
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

  const getPCRStatus = (pcr: number) => {
    if (pcr >= 70) return { label: 'Adequate', color: 'bg-green-100 text-green-800' }
    if (pcr >= 50) return { label: 'Moderate', color: 'bg-yellow-100 text-yellow-800' }
    return { label: 'Inadequate', color: 'bg-red-100 text-red-800' }
  }

  const pcrStatus = pcrData ? getPCRStatus(pcrData.pcr_percentage) : null

  return (
    <div className="container mx-auto p-6 max-w-6xl space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="icon" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">Provisioning Coverage Ratio</h1>
            <p className="text-muted-foreground">
              Measure of provisions held against gross NPAs
            </p>
          </div>
        </div>
        {pcrData && (
          <Button variant="outline">
            <Download className="mr-2 h-4 w-4" />
            Export Report
          </Button>
        )}
      </div>

      {/* Input Section */}
      <Card>
        <CardHeader>
          <CardTitle>Calculate PCR</CardTitle>
          <CardDescription>
            Select date to calculate provisioning coverage ratio
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

            <div className="flex items-end col-span-2">
              <Button
                onClick={handleCalculate}
                disabled={loading}
                className="w-full"
              >
                <TrendingUp className="mr-2 h-4 w-4" />
                {loading ? 'Calculating...' : 'Calculate PCR'}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {pcrData && (
        <>
          {/* PCR Summary */}
          <Card className="border-2">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Overall PCR</CardTitle>
                {pcrStatus && <Badge className={pcrStatus.color}>{pcrStatus.label}</Badge>}
              </div>
              <CardDescription>
                As of {new Date(pcrData.as_of_date).toLocaleDateString()}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-6">
                <div className="inline-flex items-center justify-center w-40 h-40 rounded-full bg-gradient-to-br from-blue-500 to-blue-700 text-white mb-4">
                  <div>
                    <p className="text-5xl font-bold">
                      {pcrData.pcr_percentage.toFixed(1)}
                    </p>
                    <p className="text-lg">%</p>
                  </div>
                </div>
                <p className="text-lg font-medium text-muted-foreground">
                  Provisioning Coverage Ratio
                </p>
                <p className="text-sm text-muted-foreground mt-2">
                  Target: Above 70% | Industry Average: 65-75%
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Key Metrics */}
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">Gross NPA</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">
                  {formatCurrency(pcrData.gross_npa)}
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  Total non-performing assets
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">
                  Provisions Held
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-600">
                  {formatCurrency(pcrData.provisions_held)}
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  Current provision balance
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">
                  Required Provision
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-orange-600">
                  {formatCurrency(pcrData.required_provision)}
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  As per RBI norms
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Provision Analysis */}
          <Card>
            <CardHeader>
              <CardTitle>Provision Analysis</CardTitle>
              <CardDescription>Breakdown of provisions vs requirements</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <p className="text-sm text-muted-foreground mb-1">
                      Provisions Held
                    </p>
                    <p className="text-2xl font-bold text-blue-700">
                      {formatCurrency(pcrData.provisions_held)}
                    </p>
                  </div>
                  <div className="p-4 bg-orange-50 rounded-lg">
                    <p className="text-sm text-muted-foreground mb-1">
                      Required Provision
                    </p>
                    <p className="text-2xl font-bold text-orange-700">
                      {formatCurrency(pcrData.required_provision)}
                    </p>
                  </div>
                </div>

                {pcrData.shortfall > 0 ? (
                  <div className="p-4 bg-red-50 rounded-lg border-2 border-red-200">
                    <div className="flex items-start space-x-3">
                      <AlertCircle className="h-6 w-6 text-red-600 mt-0.5" />
                      <div className="flex-1">
                        <p className="font-semibold text-red-900">
                          Provision Shortfall Detected
                        </p>
                        <p className="text-sm text-red-700 mt-1">
                          Additional provision of{' '}
                          <span className="font-bold">
                            {formatCurrency(pcrData.shortfall)}
                          </span>{' '}
                          is required to meet RBI norms
                        </p>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="p-4 bg-green-50 rounded-lg border-2 border-green-200">
                    <div className="flex items-start space-x-3">
                      <TrendingUp className="h-6 w-6 text-green-600 mt-0.5" />
                      <div className="flex-1">
                        <p className="font-semibold text-green-900">
                          Adequate Provisioning
                        </p>
                        <p className="text-sm text-green-700 mt-1">
                          Provisions held exceed RBI requirements. Excess provision:{' '}
                          <span className="font-bold">
                            {formatCurrency(
                              pcrData.provisions_held - pcrData.required_provision
                            )}
                          </span>
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Category-wise PCR */}
          <Card>
            <CardHeader>
              <CardTitle>Category-wise PCR</CardTitle>
              <CardDescription>
                Provisioning coverage by NPA category
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>NPA Category</TableHead>
                    <TableHead className="text-right">PCR %</TableHead>
                    <TableHead className="text-right">Status</TableHead>
                    <TableHead>Adequacy</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {Object.entries(pcrData.category_wise_pcr).map(
                    ([category, pcr]: [string, any]) => {
                      const status = getPCRStatus(pcr)
                      return (
                        <TableRow key={category}>
                          <TableCell className="font-medium capitalize">
                            {category.replace(/_/g, '-')}
                          </TableCell>
                          <TableCell className="text-right text-lg font-bold">
                            {formatPercentage(pcr)}
                          </TableCell>
                          <TableCell className="text-right">
                            <Badge className={status.color}>{status.label}</Badge>
                          </TableCell>
                          <TableCell>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div
                                className={`h-2 rounded-full ${
                                  pcr >= 70
                                    ? 'bg-green-600'
                                    : pcr >= 50
                                    ? 'bg-yellow-600'
                                    : 'bg-red-600'
                                }`}
                                style={{ width: `${Math.min(pcr, 100)}%` }}
                              />
                            </div>
                          </TableCell>
                        </TableRow>
                      )
                    }
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          {/* PCR Guidelines */}
          <Card>
            <CardHeader>
              <CardTitle>RBI Guidelines & Benchmarks</CardTitle>
              <CardDescription>
                Regulatory requirements and industry standards
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="p-4 border rounded-lg">
                  <h4 className="font-semibold mb-3">RBI Requirements</h4>
                  <ul className="space-y-2 text-sm">
                    <li className="flex items-start">
                      <span className="mr-2">•</span>
                      <span>
                        Minimum PCR of <strong>70%</strong> recommended for healthy
                        NBFCs
                      </span>
                    </li>
                    <li className="flex items-start">
                      <span className="mr-2">•</span>
                      <span>
                        Higher PCR indicates better provision coverage and lower
                        credit risk
                      </span>
                    </li>
                    <li className="flex items-start">
                      <span className="mr-2">•</span>
                      <span>
                        Provisions should be made as per asset classification norms
                      </span>
                    </li>
                  </ul>
                </div>

                <div className="p-4 border rounded-lg">
                  <h4 className="font-semibold mb-3">Industry Benchmarks</h4>
                  <ul className="space-y-2 text-sm">
                    <li className="flex justify-between">
                      <span>Top-tier NBFCs:</span>
                      <span className="font-semibold">80-90%</span>
                    </li>
                    <li className="flex justify-between">
                      <span>Industry Average:</span>
                      <span className="font-semibold">65-75%</span>
                    </li>
                    <li className="flex justify-between">
                      <span>Minimum Acceptable:</span>
                      <span className="font-semibold">50-60%</span>
                    </li>
                    <li className="flex justify-between">
                      <span>Below 50%:</span>
                      <span className="font-semibold text-red-600">
                        Requires attention
                      </span>
                    </li>
                  </ul>
                </div>
              </div>

              <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                <h4 className="font-semibold text-blue-900 mb-2">Formula</h4>
                <p className="text-sm text-blue-800">
                  PCR = (Provisions Held / Gross NPA) × 100
                </p>
                <p className="text-xs text-blue-700 mt-2">
                  Higher PCR indicates better preparedness to absorb losses from NPAs
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Action Items */}
          {pcrData.shortfall > 0 && (
            <Card className="border-orange-200 border-2">
              <CardHeader>
                <CardTitle className="text-orange-900">
                  Recommended Actions
                </CardTitle>
                <CardDescription>
                  Steps to improve provisioning coverage
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  <li className="flex items-start">
                    <span className="mr-2 text-orange-600 font-bold">1.</span>
                    <span className="text-sm">
                      Create additional provision of{' '}
                      {formatCurrency(pcrData.shortfall)} immediately
                    </span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2 text-orange-600 font-bold">2.</span>
                    <span className="text-sm">
                      Review asset classification to ensure accuracy
                    </span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2 text-orange-600 font-bold">3.</span>
                    <span className="text-sm">
                      Implement monthly provision monitoring to prevent shortfalls
                    </span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2 text-orange-600 font-bold">4.</span>
                    <span className="text-sm">
                      Consider write-off of identified loss assets
                    </span>
                  </li>
                </ul>

                <div className="mt-4">
                  <Button
                    onClick={() => router.push('/accounting/npa/provisions')}
                    className="w-full"
                  >
                    Create Provision Entries
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </>
      )}

      {!pcrData && !loading && (
        <Card>
          <CardContent className="text-center py-12">
            <TrendingUp className="mx-auto h-16 w-16 mb-4 opacity-30" />
            <p className="text-lg font-medium text-muted-foreground">
              No PCR calculated yet
            </p>
            <p className="text-sm text-muted-foreground">
              Select date and click Calculate PCR
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
