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
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { ArrowLeft, Calculator, TrendingUp } from 'lucide-react'
import { npaService } from '@/services/npa.service'
import { toast } from 'sonner'

const NPA_CATEGORIES = [
  { value: 'STANDARD', label: 'Standard', rate: '0.25%' },
  { value: 'SPECIAL_MENTION_0', label: 'SMA-0', rate: '0%' },
  { value: 'SPECIAL_MENTION_1', label: 'SMA-1', rate: '0%' },
  { value: 'SPECIAL_MENTION_2', label: 'SMA-2', rate: '0%' },
  { value: 'SUBSTANDARD', label: 'Substandard', rate: '15-25%' },
  { value: 'DOUBTFUL_1', label: 'Doubtful-1', rate: '25-100%' },
  { value: 'DOUBTFUL_2', label: 'Doubtful-2', rate: '40-100%' },
  { value: 'DOUBTFUL_3', label: 'Doubtful-3', rate: '100%' },
  { value: 'LOSS', label: 'Loss', rate: '100%' },
]

export default function ProvisioningCalculatorPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    outstanding_principal: '',
    npa_category: '',
    is_secured: 'true',
    security_coverage_ratio: '100',
    existing_provision: '0',
  })
  const [result, setResult] = useState<any>(null)

  const handleCalculate = async () => {
    if (!formData.outstanding_principal || !formData.npa_category) {
      toast.error('Please fill all required fields')
      return
    }

    try {
      setLoading(true)
      const response = await npaService.calculateProvisioning({
        outstanding_principal: parseFloat(formData.outstanding_principal),
        npa_category: formData.npa_category,
        is_secured: formData.is_secured === 'true',
        security_coverage_ratio: parseFloat(formData.security_coverage_ratio),
        existing_provision: parseFloat(formData.existing_provision),
      })

      setResult(response.data)
      toast.success('Provisioning calculated successfully')
    } catch (error: any) {
      toast.error(error.message || 'Failed to calculate provisioning')
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 2,
    }).format(amount)
  }

  return (
    <div className="container mx-auto p-6 max-w-6xl space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <Button variant="ghost" size="icon" onClick={() => router.back()}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold">Provisioning Calculator</h1>
          <p className="text-muted-foreground">
            Calculate RBI-compliant loan loss provisioning
          </p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Input Form */}
        <Card>
          <CardHeader>
            <CardTitle>Loan Details</CardTitle>
            <CardDescription>
              Enter loan information for provisioning calculation
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="outstanding">Outstanding Principal *</Label>
              <Input
                id="outstanding"
                type="number"
                min="0"
                step="0.01"
                placeholder="Enter outstanding amount"
                value={formData.outstanding_principal}
                onChange={(e) =>
                  setFormData({ ...formData, outstanding_principal: e.target.value })
                }
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="category">NPA Category *</Label>
              <Select
                value={formData.npa_category}
                onValueChange={(value) =>
                  setFormData({ ...formData, npa_category: value })
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select NPA category" />
                </SelectTrigger>
                <SelectContent>
                  {NPA_CATEGORIES.map((cat) => (
                    <SelectItem key={cat.value} value={cat.value}>
                      {cat.label} ({cat.rate})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="secured">Security Status</Label>
              <Select
                value={formData.is_secured}
                onValueChange={(value) =>
                  setFormData({ ...formData, is_secured: value })
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="true">Secured Loan</SelectItem>
                  <SelectItem value="false">Unsecured Loan</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {formData.is_secured === 'true' && (
              <div className="space-y-2">
                <Label htmlFor="coverage">Security Coverage Ratio (%)</Label>
                <Input
                  id="coverage"
                  type="number"
                  min="0"
                  max="100"
                  step="0.1"
                  value={formData.security_coverage_ratio}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      security_coverage_ratio: e.target.value,
                    })
                  }
                />
                <p className="text-xs text-muted-foreground">
                  Security value as % of outstanding (0-100%)
                </p>
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="existing">Existing Provision</Label>
              <Input
                id="existing"
                type="number"
                min="0"
                step="0.01"
                placeholder="Enter existing provision amount"
                value={formData.existing_provision}
                onChange={(e) =>
                  setFormData({ ...formData, existing_provision: e.target.value })
                }
              />
            </div>

            <Button onClick={handleCalculate} disabled={loading} className="w-full">
              <Calculator className="mr-2 h-4 w-4" />
              {loading ? 'Calculating...' : 'Calculate Provisioning'}
            </Button>
          </CardContent>
        </Card>

        {/* Calculation Result */}
        <Card>
          <CardHeader>
            <CardTitle>Provisioning Result</CardTitle>
            <CardDescription>
              Required provisions as per RBI norms
            </CardDescription>
          </CardHeader>
          <CardContent>
            {result ? (
              <div className="space-y-6">
                {/* Summary */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">Outstanding</p>
                    <p className="text-2xl font-bold">
                      {formatCurrency(result.outstanding_principal)}
                    </p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">
                      Provisioning Rate
                    </p>
                    <p className="text-2xl font-bold text-orange-600">
                      {result.provisioning_rate}%
                    </p>
                  </div>
                </div>

                <Separator />

                {/* Detailed Breakdown */}
                <div className="space-y-4">
                  <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
                    <span className="text-sm font-medium">Required Provision</span>
                    <span className="text-lg font-bold text-blue-700">
                      {formatCurrency(result.required_provision)}
                    </span>
                  </div>

                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <span className="text-sm font-medium">Existing Provision</span>
                    <span className="text-lg font-semibold">
                      {formatCurrency(result.existing_provision)}
                    </span>
                  </div>

                  <Separator />

                  <div className="flex justify-between items-center p-4 bg-green-50 rounded-lg border-2 border-green-200">
                    <div className="flex items-center space-x-2">
                      <TrendingUp className="h-5 w-5 text-green-700" />
                      <span className="font-medium text-green-900">
                        Additional Provision Needed
                      </span>
                    </div>
                    <span className="text-xl font-bold text-green-700">
                      {formatCurrency(result.additional_provision)}
                    </span>
                  </div>
                </div>

                {/* Category Badge */}
                <div className="flex items-center justify-between pt-4">
                  <span className="text-sm text-muted-foreground">NPA Category</span>
                  <Badge variant="outline" className="text-sm">
                    {result.npa_category.replace(/_/g, ' ')}
                  </Badge>
                </div>

                {/* Action Button */}
                {result.additional_provision > 0 && (
                  <Button className="w-full" variant="default">
                    Create Provisioning Entry
                  </Button>
                )}
              </div>
            ) : (
              <div className="text-center text-muted-foreground py-12">
                <Calculator className="mx-auto h-16 w-16 mb-4 opacity-30" />
                <p className="text-lg font-medium">No calculation yet</p>
                <p className="text-sm">
                  Fill in the loan details and click Calculate
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Provisioning Rates Guide */}
      <Card>
        <CardHeader>
          <CardTitle>RBI Provisioning Norms</CardTitle>
          <CardDescription>
            Standard provisioning rates for different NPA categories
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <h4 className="font-semibold text-sm">Standard Assets</h4>
              <p className="text-xs text-muted-foreground">
                <strong>0.25%</strong> on outstanding principal
              </p>
            </div>

            <div className="space-y-2">
              <h4 className="font-semibold text-sm">SMA (0, 1, 2)</h4>
              <p className="text-xs text-muted-foreground">
                <strong>0%</strong> - No provisioning required
              </p>
            </div>

            <div className="space-y-2">
              <h4 className="font-semibold text-sm">Substandard</h4>
              <p className="text-xs text-muted-foreground">
                <strong>15%</strong> secured, <strong>25%</strong> unsecured
              </p>
            </div>

            <div className="space-y-2">
              <h4 className="font-semibold text-sm">Doubtful-1</h4>
              <p className="text-xs text-muted-foreground">
                <strong>25%</strong> secured + <strong>100%</strong> unsecured
              </p>
            </div>

            <div className="space-y-2">
              <h4 className="font-semibold text-sm">Doubtful-2</h4>
              <p className="text-xs text-muted-foreground">
                <strong>40%</strong> secured + <strong>100%</strong> unsecured
              </p>
            </div>

            <div className="space-y-2">
              <h4 className="font-semibold text-sm">Doubtful-3 & Loss</h4>
              <p className="text-xs text-muted-foreground">
                <strong>100%</strong> on entire outstanding
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
