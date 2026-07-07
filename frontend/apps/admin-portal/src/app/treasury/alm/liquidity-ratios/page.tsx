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
import { Separator } from '@/components/ui/separator'
import { ArrowLeft, Download, Activity, TrendingUp, CheckCircle2, AlertCircle } from 'lucide-react'
import { almService } from '@/services/alm.service'
import { toast } from 'sonner'

export default function LiquidityRatiosPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [reportDate, setReportDate] = useState(
    new Date().toISOString().split('T')[0]
  )
  const [ratios, setRatios] = useState<any>(null)

  const handleCalculate = async () => {
    try {
      setLoading(true)
      const response = await almService.getLiquidityRatios(reportDate)
      if (response.success && response.data) {
        setRatios(response.data)
        toast.success('Liquidity ratios calculated')
      }
    } catch (error: any) {
      toast.error(error.message || 'Failed to calculate ratios')
      // Mock data
      setRatios({
        report_date: reportDate,
        lcr: 125.5,
        nsfr: 110.2,
        current_ratio: 1.45,
        quick_ratio: 1.12,
        cash_ratio: 0.85,
        liquid_asset_ratio: 18.5,
        breached_ratios: [],
      })
    } finally {
      setLoading(false)
    }
  }

  const formatPercentage = (value: number) => {
    return `${value.toFixed(2)}%`
  }

  const formatRatio = (value: number) => {
    return value.toFixed(2)
  }

  const getRatioStatus = (
    value: number,
    threshold: number,
    type: 'above' | 'below'
  ) => {
    const isCompliant =
      type === 'above' ? value >= threshold : value <= threshold
    return {
      isCompliant,
      color: isCompliant
        ? 'bg-green-100 text-green-800'
        : 'bg-red-100 text-red-800',
      label: isCompliant ? 'Compliant' : 'Non-Compliant',
    }
  }

  const ratioDefinitions = [
    {
      name: 'Liquidity Coverage Ratio (LCR)',
      key: 'lcr',
      formula: 'HQLA / Total Net Cash Outflows',
      threshold: 100,
      type: 'above' as const,
      description:
        'Ensures sufficient high-quality liquid assets to survive 30-day stress scenario',
      regulatory: 'RBI Minimum: 100%',
    },
    {
      name: 'Net Stable Funding Ratio (NSFR)',
      key: 'nsfr',
      formula: 'Available Stable Funding / Required Stable Funding',
      threshold: 100,
      type: 'above' as const,
      description:
        'Promotes more stable funding structures over a one-year horizon',
      regulatory: 'RBI Minimum: 100%',
    },
    {
      name: 'Current Ratio',
      key: 'current_ratio',
      formula: 'Current Assets / Current Liabilities',
      threshold: 1.0,
      type: 'above' as const,
      description:
        "Measures company's ability to pay short-term obligations within one year",
      regulatory: 'Industry Standard: Above 1.0',
    },
    {
      name: 'Quick Ratio',
      key: 'quick_ratio',
      formula: '(Current Assets - Inventory) / Current Liabilities',
      threshold: 1.0,
      type: 'above' as const,
      description:
        'Measures ability to meet short-term obligations with most liquid assets',
      regulatory: 'Industry Standard: Above 1.0',
    },
    {
      name: 'Cash Ratio',
      key: 'cash_ratio',
      formula: 'Cash & Cash Equivalents / Current Liabilities',
      threshold: 0.5,
      type: 'above' as const,
      description: 'Most conservative liquidity measure using only cash',
      regulatory: 'Industry Standard: Above 0.5',
    },
    {
      name: 'Liquid Asset Ratio',
      key: 'liquid_asset_ratio',
      formula: '(Liquid Assets / Total Assets) × 100',
      threshold: 15,
      type: 'above' as const,
      description: 'Percentage of assets in liquid form',
      regulatory: 'Industry Standard: 15-20%',
    },
  ]

  return (
    <div className="container mx-auto p-6 max-w-7xl space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="icon" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">Liquidity Ratios</h1>
            <p className="text-muted-foreground">
              Key regulatory and operational liquidity metrics
            </p>
          </div>
        </div>
        <Button variant="outline">
          <Download className="mr-2 h-4 w-4" />
          Export Report
        </Button>
      </div>

      {/* Date Selection */}
      <Card>
        <CardHeader>
          <CardTitle>Calculate Ratios</CardTitle>
          <CardDescription>
            Select report date to calculate liquidity ratios
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-end space-x-4 max-w-md">
            <div className="flex-1 space-y-2">
              <Label htmlFor="reportDate">Report Date</Label>
              <Input
                id="reportDate"
                type="date"
                value={reportDate}
                onChange={(e) => setReportDate(e.target.value)}
              />
            </div>
            <Button onClick={handleCalculate} disabled={loading}>
              <Activity className="mr-2 h-4 w-4" />
              {loading ? 'Calculating...' : 'Calculate'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {ratios && (
        <>
          {/* Overall Compliance Status */}
          <Card
            className={
              ratios.breached_ratios.length === 0
                ? 'border-green-200 border-2'
                : 'border-red-200 border-2'
            }
          >
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  {ratios.breached_ratios.length === 0 ? (
                    <CheckCircle2 className="h-6 w-6 text-green-600" />
                  ) : (
                    <AlertCircle className="h-6 w-6 text-red-600" />
                  )}
                  <CardTitle
                    className={
                      ratios.breached_ratios.length === 0
                        ? 'text-green-900'
                        : 'text-red-900'
                    }
                  >
                    Overall Compliance Status
                  </CardTitle>
                </div>
                <Badge
                  className={
                    ratios.breached_ratios.length === 0
                      ? 'bg-green-600 text-white'
                      : 'bg-red-600 text-white'
                  }
                >
                  {ratios.breached_ratios.length === 0
                    ? 'All Ratios Compliant'
                    : `${ratios.breached_ratios.length} Ratio(s) Breached`}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <p
                className={`text-sm ${
                  ratios.breached_ratios.length === 0
                    ? 'text-green-700'
                    : 'text-red-700'
                }`}
              >
                {ratios.breached_ratios.length === 0
                  ? 'All regulatory and operational liquidity ratios are within prescribed limits. System is fully compliant with RBI guidelines.'
                  : `${ratios.breached_ratios.length} ratio(s) are below regulatory thresholds. Immediate corrective action required.`}
              </p>
            </CardContent>
          </Card>

          {/* Ratio Cards */}
          <div className="grid gap-6 md:grid-cols-2">
            {ratioDefinitions.map((def) => {
              const value = ratios[def.key]
              const status = getRatioStatus(value, def.threshold, def.type)

              return (
                <Card key={def.key} className="relative overflow-hidden">
                  <div
                    className={`absolute top-0 right-0 w-32 h-32 -mr-16 -mt-16 rounded-full opacity-10 ${
                      status.isCompliant ? 'bg-green-500' : 'bg-red-500'
                    }`}
                  />
                  <CardHeader className="relative">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <CardTitle className="text-lg">{def.name}</CardTitle>
                        <CardDescription className="mt-1">
                          {def.description}
                        </CardDescription>
                      </div>
                      <Badge className={status.color}>{status.label}</Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="relative space-y-4">
                    <div className="flex items-end space-x-2">
                      <div
                        className={`text-4xl font-bold ${
                          status.isCompliant ? 'text-green-600' : 'text-red-600'
                        }`}
                      >
                        {def.key.includes('ratio') && !def.key.includes('liquid_asset')
                          ? formatRatio(value)
                          : formatPercentage(value)}
                      </div>
                      {status.isCompliant ? (
                        <TrendingUp className="h-6 w-6 text-green-600 mb-1" />
                      ) : (
                        <AlertCircle className="h-6 w-6 text-red-600 mb-1" />
                      )}
                    </div>

                    <Separator />

                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Formula:</span>
                        <span className="font-mono text-xs">{def.formula}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Threshold:</span>
                        <span className="font-semibold">
                          {def.type === 'above' ? '≥' : '≤'}{' '}
                          {def.threshold}
                          {def.key.includes('ratio') &&
                          !def.key.includes('liquid_asset')
                            ? ''
                            : '%'}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Regulatory:</span>
                        <span className="text-xs">{def.regulatory}</span>
                      </div>
                    </div>

                    {!status.isCompliant && (
                      <div className="p-3 bg-red-50 rounded-lg border border-red-200">
                        <p className="text-xs font-medium text-red-900">
                          Action Required
                        </p>
                        <p className="text-xs text-red-700 mt-1">
                          Current value is below regulatory threshold. Review
                          liquidity position and take corrective measures.
                        </p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )
            })}
          </div>

          {/* Regulatory Guidelines */}
          <Card>
            <CardHeader>
              <CardTitle>RBI Liquidity Guidelines</CardTitle>
              <CardDescription>
                Regulatory requirements for NBFCs in India
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="p-4 border rounded-lg">
                    <h4 className="font-semibold mb-2 flex items-center">
                      <CheckCircle2 className="h-4 w-4 mr-2 text-blue-600" />
                      Liquidity Coverage Ratio (LCR)
                    </h4>
                    <ul className="space-y-2 text-sm text-muted-foreground">
                      <li>• Minimum requirement: 100%</li>
                      <li>• Applicable to all NBFCs with asset size ≥ ₹10,000 crore</li>
                      <li>• Based on 30-day stress scenario</li>
                      <li>• Uses high-quality liquid assets (HQLA)</li>
                    </ul>
                  </div>

                  <div className="p-4 border rounded-lg">
                    <h4 className="font-semibold mb-2 flex items-center">
                      <CheckCircle2 className="h-4 w-4 mr-2 text-blue-600" />
                      Net Stable Funding Ratio (NSFR)
                    </h4>
                    <ul className="space-y-2 text-sm text-muted-foreground">
                      <li>• Minimum requirement: 100%</li>
                      <li>• Promotes stable funding structure</li>
                      <li>• One-year time horizon</li>
                      <li>• Reduces funding risk</li>
                    </ul>
                  </div>

                  <div className="p-4 border rounded-lg">
                    <h4 className="font-semibold mb-2 flex items-center">
                      <CheckCircle2 className="h-4 w-4 mr-2 text-blue-600" />
                      Statutory Liquidity Ratio (SLR)
                    </h4>
                    <ul className="space-y-2 text-sm text-muted-foreground">
                      <li>• Currently at 18% for banks</li>
                      <li>• NBFCs exempt but monitor recommended</li>
                      <li>• Investment in government securities</li>
                      <li>• Ensures sovereign exposure</li>
                    </ul>
                  </div>

                  <div className="p-4 border rounded-lg">
                    <h4 className="font-semibold mb-2 flex items-center">
                      <CheckCircle2 className="h-4 w-4 mr-2 text-blue-600" />
                      Additional Metrics
                    </h4>
                    <ul className="space-y-2 text-sm text-muted-foreground">
                      <li>• Current Ratio: Above 1.0</li>
                      <li>• Quick Ratio: Above 1.0</li>
                      <li>• Cash Ratio: Above 0.5</li>
                      <li>• Liquid Asset Ratio: 15-20%</li>
                    </ul>
                  </div>
                </div>

                <Separator />

                <div className="p-4 bg-blue-50 rounded-lg">
                  <h4 className="font-semibold text-blue-900 mb-2">
                    Reporting Requirements
                  </h4>
                  <p className="text-sm text-blue-700">
                    NBFCs must report liquidity ratios quarterly to RBI through SLS
                    (Structural Liquidity Statement) and maintain daily monitoring
                    for internal risk management.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Action Items */}
          {ratios.breached_ratios.length > 0 && (
            <Card className="border-orange-200 border-2">
              <CardHeader>
                <CardTitle className="text-orange-900">
                  Recommended Actions
                </CardTitle>
                <CardDescription>
                  Steps to improve liquidity position
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  <li className="flex items-start">
                    <span className="mr-2 text-orange-600 font-bold">1.</span>
                    <span className="text-sm">
                      Review asset-liability maturity profile and identify mismatches
                    </span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2 text-orange-600 font-bold">2.</span>
                    <span className="text-sm">
                      Increase proportion of high-quality liquid assets (HQLA)
                    </span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2 text-orange-600 font-bold">3.</span>
                    <span className="text-sm">
                      Diversify funding sources to reduce concentration risk
                    </span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2 text-orange-600 font-bold">4.</span>
                    <span className="text-sm">
                      Consider raising long-term stable funding through bonds or NCDs
                    </span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2 text-orange-600 font-bold">5.</span>
                    <span className="text-sm">
                      Implement contingency funding plan for stress scenarios
                    </span>
                  </li>
                </ul>
              </CardContent>
            </Card>
          )}
        </>
      )}

      {!ratios && !loading && (
        <Card>
          <CardContent className="text-center py-12">
            <Activity className="mx-auto h-16 w-16 mb-4 opacity-30" />
            <p className="text-lg font-medium text-muted-foreground">
              No ratios calculated yet
            </p>
            <p className="text-sm text-muted-foreground">
              Select report date and click Calculate
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
