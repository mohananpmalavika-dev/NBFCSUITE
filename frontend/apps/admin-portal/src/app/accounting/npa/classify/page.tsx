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
import { Switch } from '@/components/ui/switch'
import { ArrowLeft, Search, AlertCircle } from 'lucide-react'
import { npaService } from '@/services/npa.service'
import { toast } from 'sonner'

const CLASSIFICATION_INFO = {
  STANDARD: {
    label: 'Standard',
    color: 'bg-green-100 text-green-800',
    description: '0 DPD - No overdue',
    provisioning: '0.25%',
  },
  SPECIAL_MENTION_0: {
    label: 'SMA-0',
    color: 'bg-yellow-100 text-yellow-800',
    description: '1-30 DPD',
    provisioning: '0%',
  },
  SPECIAL_MENTION_1: {
    label: 'SMA-1',
    color: 'bg-yellow-100 text-yellow-800',
    description: '31-60 DPD',
    provisioning: '0%',
  },
  SPECIAL_MENTION_2: {
    label: 'SMA-2',
    color: 'bg-orange-100 text-orange-800',
    description: '61-90 DPD',
    provisioning: '0%',
  },
  SUBSTANDARD: {
    label: 'Substandard',
    color: 'bg-red-100 text-red-800',
    description: '91-365 DPD (Up to 1 year)',
    provisioning: '15-25%',
  },
  DOUBTFUL_1: {
    label: 'Doubtful-1',
    color: 'bg-red-200 text-red-900',
    description: '366-730 DPD (1-2 years)',
    provisioning: '25-100%',
  },
  DOUBTFUL_2: {
    label: 'Doubtful-2',
    color: 'bg-red-300 text-red-900',
    description: '731-1095 DPD (2-3 years)',
    provisioning: '40-100%',
  },
  DOUBTFUL_3: {
    label: 'Doubtful-3',
    color: 'bg-red-400 text-red-950',
    description: '1096+ DPD (3+ years)',
    provisioning: '100%',
  },
  LOSS: {
    label: 'Loss',
    color: 'bg-gray-800 text-white',
    description: 'Identified loss',
    provisioning: '100%',
  },
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

  const handleClassify = async () => {
    if (!formData.days_past_due) {
      toast.error('Please enter days past due')
      return
    }

    try {
      setLoading(true)
      const response = await npaService.classifyAsset({
        days_past_due: parseInt(formData.days_past_due),
        is_restructured: formData.is_restructured,
        is_written_off: formData.is_written_off,
      })

      setResult(response.data)
      toast.success('Classification completed')
    } catch (error: any) {
      toast.error(error.message || 'Failed to classify asset')
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

  const classificationInfo = result
    ? CLASSIFICATION_INFO[result.npa_category as keyof typeof CLASSIFICATION_INFO]
    : null

  return (
    <div className="container mx-auto p-6 max-w-5xl space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <Button variant="ghost" size="icon" onClick={() => router.back()}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold">Loan Classification</h1>
          <p className="text-muted-foreground">
            Classify loans based on Days Past Due (DPD)
          </p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Input Form */}
        <Card>
          <CardHeader>
            <CardTitle>Classification Input</CardTitle>
            <CardDescription>
              Enter loan details to determine NPA category
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="dpd">Days Past Due (DPD) *</Label>
              <Input
                id="dpd"
                type="number"
                min="0"
                placeholder="Enter days past due"
                value={formData.days_past_due}
                onChange={(e) =>
                  setFormData({ ...formData, days_past_due: e.target.value })
                }
              />
              <p className="text-xs text-muted-foreground">
                Number of days since last payment
              </p>
            </div>

            <Separator />

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="restructured">Restructured Loan</Label>
                  <p className="text-xs text-muted-foreground">
                    Has this loan been restructured?
                  </p>
                </div>
                <Switch
                  id="restructured"
                  checked={formData.is_restructured}
                  onCheckedChange={(checked) =>
                    setFormData({ ...formData, is_restructured: checked })
                  }
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="writtenoff">Written Off</Label>
                  <p className="text-xs text-muted-foreground">
                    Has this loan been written off?
                  </p>
                </div>
                <Switch
                  id="writtenoff"
                  checked={formData.is_written_off}
                  onCheckedChange={(checked) =>
                    setFormData({ ...formData, is_written_off: checked })
                  }
                />
              </div>
            </div>

            <Separator />

            <div className="flex space-x-2">
              <Button onClick={handleClassify} disabled={loading} className="flex-1">
                <Search className="mr-2 h-4 w-4" />
                {loading ? 'Classifying...' : 'Classify'}
              </Button>
              <Button variant="outline" onClick={handleReset}>
                Reset
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Classification Result */}
        <Card>
          <CardHeader>
            <CardTitle>Classification Result</CardTitle>
            <CardDescription>NPA category and provisioning details</CardDescription>
          </CardHeader>
          <CardContent>
            {result && classificationInfo ? (
              <div className="space-y-6">
                {/* Category Badge */}
                <div className="flex items-center justify-center p-6 bg-gray-50 rounded-lg">
                  <Badge className={`${classificationInfo.color} text-lg px-4 py-2`}>
                    {classificationInfo.label}
                  </Badge>
                </div>

                {/* Details */}
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-muted-foreground">Days Past Due</p>
                      <p className="text-2xl font-bold">{result.days_past_due}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">
                        Provisioning Rate
                      </p>
                      <p className="text-2xl font-bold text-orange-600">
                        {classificationInfo.provisioning}
                      </p>
                    </div>
                  </div>

                  <Separator />

                  <div>
                    <p className="text-sm font-medium mb-2">Description</p>
                    <p className="text-sm text-muted-foreground">
                      {classificationInfo.description}
                    </p>
                  </div>

                  <div className="flex items-start space-x-2 p-4 bg-blue-50 rounded-lg">
                    <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5" />
                    <div className="flex-1">
                      <p className="text-sm font-medium text-blue-900">
                        Classification Status
                      </p>
                      <p className="text-sm text-blue-700 mt-1">
                        {result.is_npa
                          ? 'This is a Non-Performing Asset (NPA)'
                          : result.is_sma
                          ? 'This is a Special Mention Account (SMA)'
                          : 'This is a Standard Asset'}
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 pt-2">
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <p className="text-xs text-muted-foreground">NPA Status</p>
                      <p className="text-sm font-semibold">
                        {result.is_npa ? 'Yes' : 'No'}
                      </p>
                    </div>
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <p className="text-xs text-muted-foreground">SMA Status</p>
                      <p className="text-sm font-semibold">
                        {result.is_sma ? 'Yes' : 'No'}
                      </p>
                    </div>
                  </div>
                </div>

                <Separator />

                <Button
                  variant="outline"
                  className="w-full"
                  onClick={() => router.push('/accounting/npa/calculator')}
                >
                  Calculate Provisioning
                </Button>
              </div>
            ) : (
              <div className="text-center text-muted-foreground py-12">
                <Search className="mx-auto h-16 w-16 mb-4 opacity-30" />
                <p className="text-lg font-medium">No classification yet</p>
                <p className="text-sm">Enter loan details and click Classify</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Classification Guide */}
      <Card>
        <CardHeader>
          <CardTitle>NPA Classification Guide</CardTitle>
          <CardDescription>
            RBI guidelines for asset classification based on Days Past Due
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
            {Object.entries(CLASSIFICATION_INFO).map(([key, info]) => (
              <div key={key} className="p-3 border rounded-lg">
                <Badge className={`${info.color} mb-2`}>{info.label}</Badge>
                <p className="text-sm font-medium">{info.description}</p>
                <p className="text-xs text-muted-foreground mt-1">
                  Provisioning: {info.provisioning}
                </p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
