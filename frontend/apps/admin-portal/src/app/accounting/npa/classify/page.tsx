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
import { Checkbox } from '@/components/ui/checkbox'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { ArrowLeft, Calculator, AlertCircle, CheckCircle2 } from 'lucide-react'
import { npaService } from '@/services/npa.service'
import { toast } from 'sonner'

const NPA_CATEGORIES = {
  STANDARD: { label: 'Standard', color: 'bg-green-100 text-green-800', dpd: '0 DPD' },
  SPECIAL_MENTION_0: { label: 'SMA-0', color: 'bg-yellow-100 text-yellow-800', dpd: '1-30 DPD' },
  SPECIAL_MENTION_1: { label: 'SMA-1', color: 'bg-yellow-100 text-yellow-800', dpd: '31-60 DPD' },
  SPECIAL_MENTION_2: { label: 'SMA-2', color: 'bg-orange-100 text-orange-800', dpd: '61-90 DPD' },
  SUBSTANDARD: { label: 'Substandard', color: 'bg-red-100 text-red-800', dpd: '91-365 DPD' },
  DOUBTFUL_1: { label: 'Doubtful-1', color: 'bg-red-200 text-red-900', dpd: '366-730 DPD' },
  DOUBTFUL_2: { label: 'Doubtful-2', color: 'bg-red-300 text-red-900', dpd: '731-1095 DPD' },
  DOUBTFUL_3: { label: 'Doubtful-3', color: 'bg-red-400 text-red-900', dpd: '1096+ DPD' },
  LOSS: { label: 'Loss', color: 'bg-gray-800 text-white', dpd: 'Identified loss' },
}

export default function ClassifyLoanPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    days_past_due: '',
    is_restructured: false,
    is_written_off: false,
  })
  const [result, setResult] = useState<any>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.days_past_due) {
      toast.error('Please enter Days Past Due')
      return
    }

    try {
      setLoading(true)
      const response = await npaService.classifyAsset({
        days_past_due: parseInt(formData.days_past_due),
        is_restructured: formData.is_restructured,
        is_written_off: formData.is_written_off,
      })

      if (response.success) {
        setResult(response.data)
        toast.success('Classification completed successfully')
      }
    } catch (error: any) {
      toast.error(error.message || 'Failed to classify loan')
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setFormData({
      days_past_due: '',
      is_restructured: false,
      is_written_off: false,
    })
    setResult(null)
  }

  return (
    <div className="container mx-auto p-6 max-w-4xl space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => router.back()}
        >
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold">Loan Classification</h1>
          <p className="text-muted-foreground">
            Classify loan based on Days Past Due (DPD)
          </p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Input Form */}
        <Card>
          <CardHeader>
            <CardTitle>Classification Input</CardTitle>
            <CardDescription>
              Enter loan details for classification
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="dpd">Days Past Due (DPD) *</Label>
                <Input
                  id="dpd"
                  type="number"
                  min="0"
                  placeholder="Enter days overdue"
                  value={formData.days_past_due}
                  onChange={(e) =>
                    setFormData({ ...formData, days_past_due: e.target.value })
                  }
                  required
                />
                <p className="text-xs text-muted-foreground">
                  Number of days the loan is overdue
                </p>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="restructured"
                  checked={formData.is_restructured}
                  onCheckedChange={(checked) =>
                    setFormData({ ...formData, is_restructured: checked as boolean })
                  }
                />
                <Label htmlFor="restructured" className="font-normal">
                  Loan is restructured
                </Label>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="written_off"
                  checked={formData.is_written_off}
                  onCheckedChange={(checked) =>
                    setFormData({ ...formData, is_written_off: checked as boolean })
                  }
                />
                <Label htmlFor="written_off" className="font-normal">
                  Loan is written off
                </Label>
              </div>

              <div className="flex space-x-2">
                <Button type="submit" disabled={loading} className="flex-1">
                  <Calculator className="mr-2 h-4 w-4" />
                  {loading ? 'Classifying...' : 'Classify'}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleReset}
                  disabled={loading}
                >
                  Reset
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Classification Result */}
        <Card>
          <CardHeader>
            <CardTitle>Classification Result</CardTitle>
            <CardDescription>
              NPA category and classification details
            </CardDescription>
          </CardHeader>
          <CardContent>
            {result ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-accent rounded-lg">
                  <span className="text-sm font-medium">NPA Category</span>
                  <Badge className={NPA_CATEGORIES[result.npa_category as keyof typeof NPA_CATEGORIES]?.color}>
                    {NPA_CATEGORIES[result.npa_category as keyof typeof NPA_CATEGORIES]?.label || result.npa_category}
                  </Badge>
                </div>

                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Days Past Due</span>
                    <span className="font-medium">{result.days_past_due} days</span>
                  </div>

                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Is NPA?</span>
                    <span className="font-medium flex items-center">
                      {result.is_npa ? (
                        <>
                          <AlertCircle className="mr-1 h-4 w-4 text-red-600" />
                          Yes
                        </>
                      ) : (
                        <>
                          <CheckCircle2 className="mr-1 h-4 w-4 text-green-600" />
                          No
                        </>
                      )}
                    </span>
                  </div>

                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Is SMA?</span>
                    <span className="font-medium flex items-center">
                      {result.is_sma ? (
                        <>
                          <AlertCircle className="mr-1 h-4 w-4 text-yellow-600" />
                          Yes
                        </>
                      ) : (
                        'No'
                      )}
                    </span>
                  </div>

                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Classification Date</span>
                    <span className="font-medium">
                      {new Date(result.classification_date).toLocaleDateString()}
                    </span>
                  </div>
                </div>

                {result.is_npa && (
                  <Alert>
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>
                      This loan is classified as NPA. Immediate action required for
                      provisioning and collection.
                    </AlertDescription>
                  </Alert>
                )}

                {result.is_sma && !result.is_npa && (
                  <Alert className="border-yellow-200 bg-yellow-50">
                    <AlertCircle className="h-4 w-4 text-yellow-600" />
                    <AlertDescription className="text-yellow-800">
                      Special Mention Account - Early warning indicator. Monitor
                      closely to prevent NPA.
                    </AlertDescription>
                  </Alert>
                )}
              </div>
            ) : (
              <div className="text-center text-muted-foreground py-8">
                <Calculator className="mx-auto h-12 w-12 mb-2 opacity-50" />
                <p>Enter loan details and click Classify to see results</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Classification Guide */}
      <Card>
        <CardHeader>
          <CardTitle>RBI Classification Guide</CardTitle>
          <CardDescription>
            Asset classification categories as per RBI norms
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 md:grid-cols-3">
            {Object.entries(NPA_CATEGORIES).map(([key, value]) => (
              <div
                key={key}
                className="flex items-center justify-between p-3 border rounded-lg"
              >
                <div>
                  <Badge className={value.color}>{value.label}</Badge>
                  <p className="text-xs text-muted-foreground mt-1">
                    {value.dpd}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
