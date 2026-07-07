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
import { Progress } from '@/components/ui/progress'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { ArrowLeft, PlayCircle, CheckCircle2, AlertCircle, Clock } from 'lucide-react'
import { npaService } from '@/services/npa.service'
import { toast } from 'sonner'

export default function BatchClassificationPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [asOfDate, setAsOfDate] = useState(new Date().toISOString().split('T')[0])
  const [result, setResult] = useState<any>(null)
  const [progress, setProgress] = useState(0)

  const runBatchClassification = async () => {
    try {
      setLoading(true)
      setProgress(0)
      
      // Simulate progress
      const progressInterval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return 90
          }
          return prev + 10
        })
      }, 500)

      const response = await npaService.runMonthlyClassification(asOfDate)

      clearInterval(progressInterval)
      setProgress(100)

      if (response.success) {
        setResult(response.data)
        toast.success('Batch classification completed successfully')
      }
    } catch (error: any) {
      toast.error(error.message || 'Failed to run batch classification')
      setProgress(0)
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
    <div className="container mx-auto p-6 max-w-6xl space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <Button variant="ghost" size="icon" onClick={() => router.back()}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold">Monthly NPA Classification</h1>
          <p className="text-muted-foreground">
            Classify entire loan portfolio and create provisioning entries
          </p>
        </div>
      </div>

      {/* Configuration */}
      <Card>
        <CardHeader>
          <CardTitle>Classification Configuration</CardTitle>
          <CardDescription>
            Select the date for monthly classification run
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="asOfDate">As of Date *</Label>
              <Input
                id="asOfDate"
                type="date"
                value={asOfDate}
                onChange={(e) => setAsOfDate(e.target.value)}
                disabled={loading}
              />
              <p className="text-xs text-muted-foreground">
                Typically run on the last day of the month
              </p>
            </div>

            <div className="flex items-end">
              <Button
                onClick={runBatchClassification}
                disabled={loading}
                className="w-full"
                size="lg"
              >
                <PlayCircle className="mr-2 h-5 w-5" />
                {loading ? 'Processing...' : 'Run Classification'}
              </Button>
            </div>
          </div>

          {loading && (
            <div className="mt-6 space-y-2">
              <div className="flex justify-between text-sm">
                <span>Processing loans...</span>
                <span>{progress}%</span>
              </div>
              <Progress value={progress} className="h-2" />
            </div>
          )}
        </CardContent>
      </Card>

      {/* Processing Alert */}
      {loading && (
        <Alert>
          <Clock className="h-4 w-4" />
          <AlertDescription>
            Classification is in progress. This may take a few minutes depending on
            portfolio size. Please do not close this page.
          </AlertDescription>
        </Alert>
      )}

      {/* Results */}
      {result && (
        <>
          {/* Summary Statistics */}
          <div className="grid gap-4 md:grid-cols-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">
                  Total Processed
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center space-x-2">
                  <CheckCircle2 className="h-5 w-5 text-green-600" />
                  <span className="text-2xl font-bold">
                    {result.total_accounts_processed}
                  </span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">
                  Provisions Created
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-orange-600">
                  {formatCurrency(result.provisions_created)}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">
                  Journal Entries
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-600">
                  {result.journal_entries?.length || 0}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">
                  NPA Ratio
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">
                  {result.summary?.total_npa_ratio?.toFixed(2)}%
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Success Alert */}
          <Alert className="border-green-200 bg-green-50">
            <CheckCircle2 className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-800">
              Classification completed successfully on{' '}
              {new Date(result.processed_at).toLocaleString()}. All provisioning
              entries have been posted to the general ledger.
            </AlertDescription>
          </Alert>

          {/* Classification Breakdown */}
          <Card>
            <CardHeader>
              <CardTitle>Classification Summary</CardTitle>
              <CardDescription>
                Distribution of loans across NPA categories
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>NPA Category</TableHead>
                    <TableHead className="text-right">Account Count</TableHead>
                    <TableHead className="text-right">Percentage</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {Object.entries(result.classifications).map(([category, count]: [string, any]) => (
                    <TableRow key={category}>
                      <TableCell>
                        <Badge
                          variant="outline"
                          className={
                            category.startsWith('STANDARD')
                              ? 'bg-green-50'
                              : category.startsWith('SPECIAL')
                              ? 'bg-yellow-50'
                              : 'bg-red-50'
                          }
                        >
                          {category.replace(/_/g, ' ')}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right font-medium">
                        {count}
                      </TableCell>
                      <TableCell className="text-right">
                        {((count / result.total_accounts_processed) * 100).toFixed(2)}%
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          {/* Additional Insights */}
          {result.summary && (
            <Card>
              <CardHeader>
                <CardTitle>Key Insights</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-3">
                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">New NPAs</p>
                    <p className="text-2xl font-bold text-red-600">
                      {result.summary.new_npas || 0}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Accounts that crossed 90 DPD
                    </p>
                  </div>

                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">Upgrades</p>
                    <p className="text-2xl font-bold text-green-600">
                      {result.summary.upgrades || 0}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Accounts improved classification
                    </p>
                  </div>

                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">
                      Provision Coverage
                    </p>
                    <p className="text-2xl font-bold text-blue-600">
                      {result.summary.provision_coverage?.toFixed(2)}%
                    </p>
                    <p className="text-xs text-muted-foreground">
                      PCR (target: 70%+)
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Next Steps */}
          <Card>
            <CardHeader>
              <CardTitle>Next Steps</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex items-start space-x-2">
                  <CheckCircle2 className="h-5 w-5 text-green-600 mt-0.5" />
                  <div>
                    <p className="font-medium">Review Classification Results</p>
                    <p className="text-sm text-muted-foreground">
                      Check the asset classification register for details
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-2">
                  <CheckCircle2 className="h-5 w-5 text-green-600 mt-0.5" />
                  <div>
                    <p className="font-medium">Verify Journal Entries</p>
                    <p className="text-sm text-muted-foreground">
                      Ensure all provisioning entries are posted correctly
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-2">
                  <CheckCircle2 className="h-5 w-5 text-green-600 mt-0.5" />
                  <div>
                    <p className="font-medium">Initiate Collection Actions</p>
                    <p className="text-sm text-muted-foreground">
                      Trigger collection workflows for new NPAs
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-2">
                  <AlertCircle className="h-5 w-5 text-orange-600 mt-0.5" />
                  <div>
                    <p className="font-medium">Management Review</p>
                    <p className="text-sm text-muted-foreground">
                      Present findings to management and board
                    </p>
                  </div>
                </div>
              </div>

              <div className="flex space-x-2 mt-6">
                <Button onClick={() => router.push('/accounting/npa/register')}>
                  View Register
                </Button>
                <Button
                  variant="outline"
                  onClick={() => router.push('/accounting/npa/movement')}
                >
                  View Movement Report
                </Button>
              </div>
            </CardContent>
          </Card>
        </>
      )}

      {/* Instructions */}
      {!result && !loading && (
        <Card>
          <CardHeader>
            <CardTitle>About Monthly Classification</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h4 className="font-semibold mb-2">What This Process Does:</h4>
              <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
                <li>Calculates Days Past Due (DPD) for all active loans</li>
                <li>Classifies each loan into appropriate NPA category</li>
                <li>Calculates required provisioning as per RBI norms</li>
                <li>Creates journal entries for provisioning</li>
                <li>Updates loan records with classification status</li>
                <li>Generates summary reports and statistics</li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold mb-2">Best Practices:</h4>
              <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
                <li>Run this process on the last day of each month</li>
                <li>Ensure all payments are posted before running</li>
                <li>Review results before month-end closing</li>
                <li>Keep management informed of significant changes</li>
                <li>Schedule during off-peak hours for large portfolios</li>
              </ul>
            </div>

            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                This is a critical monthly process. Ensure all payments and
                adjustments are posted before running the classification.
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
