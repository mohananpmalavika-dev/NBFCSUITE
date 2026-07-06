'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { 
  BarChart3, 
  TrendingUp, 
  AlertCircle,
  Download,
  RefreshCw,
  Loader2
} from 'lucide-react'
import { useToast } from '@/components/ui/use-toast'
import { customerService } from '@/services/customer.service'
import type { BureauReport } from '@/types/customer.types'
import { formatDate } from '@/lib/utils'

interface CreditBureauProps {
  customerId: string
}

export function CreditBureau({ customerId }: CreditBureauProps) {
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const [selectedProvider, setSelectedProvider] = useState('cibil')

  // Fetch bureau history
  const { data: history, isLoading } = useQuery({
    queryKey: ['bureau-history', customerId],
    queryFn: () => customerService.getBureauHistory(customerId, 10),
  })

  // Fetch latest score
  const { data: latestScore } = useQuery({
    queryKey: ['latest-score', customerId],
    queryFn: () => customerService.getLatestCreditScore(customerId),
  })

  // Pull report mutation
  const pullReportMutation = useMutation({
    mutationFn: () => customerService.pullCreditReport(customerId, selectedProvider),
    onSuccess: () => {
      toast({
        title: 'Report Pulled',
        description: 'Credit report fetched successfully',
      })
      queryClient.invalidateQueries({ queryKey: ['bureau-history', customerId] })
      queryClient.invalidateQueries({ queryKey: ['latest-score', customerId] })
    },
    onError: (error: any) => {
      toast({
        title: 'Pull Failed',
        description: error.response?.data?.detail || 'An error occurred',
        variant: 'destructive',
      })
    },
  })

  const reports = history?.data || []
  const score = latestScore?.data?.credit_score

  const getScoreColor = (score?: number) => {
    if (!score) return 'text-gray-400'
    if (score >= 750) return 'text-green-600'
    if (score >= 650) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getScoreLabel = (score?: number) => {
    if (!score) return 'Not Available'
    if (score >= 750) return 'Excellent'
    if (score >= 700) return 'Good'
    if (score >= 650) return 'Fair'
    return 'Poor'
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Credit Score Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Credit Score
          </CardTitle>
          <CardDescription>
            Latest credit score and bureau information
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <div className="flex items-baseline gap-3">
                <span className={`text-6xl font-bold ${getScoreColor(score)}`}>
                  {score || '-'}
                </span>
                {score && (
                  <Badge className={`${getScoreColor(score)} text-lg`}>
                    {getScoreLabel(score)}
                  </Badge>
                )}
              </div>
              {reports.length > 0 && (
                <p className="text-sm text-gray-600 mt-2">
                  Last updated: {formatDate(reports[0].request_date)}
                </p>
              )}
            </div>

            <div className="flex flex-col gap-2">
              <Select value={selectedProvider} onValueChange={setSelectedProvider}>
                <SelectTrigger className="w-48">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="cibil">CIBIL TransUnion</SelectItem>
                  <SelectItem value="equifax">Equifax</SelectItem>
                  <SelectItem value="experian">Experian</SelectItem>
                  <SelectItem value="crif">CRIF High Mark</SelectItem>
                </SelectContent>
              </Select>
              <Button
                onClick={() => pullReportMutation.mutate()}
                disabled={pullReportMutation.isPending}
                className="w-full"
              >
                {pullReportMutation.isPending ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <RefreshCw className="h-4 w-4 mr-2" />
                )}
                Pull Report
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Latest Report Details */}
      {reports.length > 0 && reports[0].status === 'success' && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <p className="text-2xl font-bold text-gray-900">
                  {reports[0].total_accounts || 0}
                </p>
                <p className="text-sm text-gray-600 mt-1">Total Accounts</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <p className="text-2xl font-bold text-green-600">
                  {reports[0].active_accounts || 0}
                </p>
                <p className="text-sm text-gray-600 mt-1">Active Accounts</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <p className="text-2xl font-bold text-gray-900">
                  ₹{(reports[0].total_outstanding || 0).toLocaleString('en-IN')}
                </p>
                <p className="text-sm text-gray-600 mt-1">Total Outstanding</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <p className="text-2xl font-bold text-orange-600">
                  {reports[0].recent_enquiries_6m || 0}
                </p>
                <p className="text-sm text-gray-600 mt-1">Enquiries (6M)</p>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Bureau History */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Bureau Pull History
          </CardTitle>
          <CardDescription>
            History of credit report pulls
          </CardDescription>
        </CardHeader>
        <CardContent>
          {reports.length === 0 ? (
            <div className="text-center py-8">
              <AlertCircle className="h-12 w-12 mx-auto text-gray-400 mb-4" />
              <p className="text-gray-600 mb-4">No credit reports pulled yet</p>
              <p className="text-sm text-gray-500">
                Pull a report to view credit history and score
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {reports.map((report) => (
                <div
                  key={report.id}
                  className="flex items-center gap-4 p-4 border rounded-lg hover:bg-gray-50"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="font-medium text-gray-900">
                        {report.bureau_provider.toUpperCase()}
                      </h4>
                      <Badge
                        className={
                          report.status === 'success'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }
                      >
                        {report.status}
                      </Badge>
                      {report.credit_score && (
                        <Badge variant="outline">
                          Score: {report.credit_score}
                        </Badge>
                      )}
                    </div>
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <span>Pulled on {formatDate(report.request_date)}</span>
                      {report.response_time_ms && (
                        <span>{report.response_time_ms}ms</span>
                      )}
                      {report.recent_enquiries_1m !== undefined && (
                        <span>{report.recent_enquiries_1m} enquiries (1M)</span>
                      )}
                    </div>
                    {report.error_message && (
                      <p className="text-sm text-red-600 mt-1">
                        Error: {report.error_message}
                      </p>
                    )}
                  </div>

                  {report.status === 'success' && (
                    <Button variant="ghost" size="icon">
                      <Download className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
