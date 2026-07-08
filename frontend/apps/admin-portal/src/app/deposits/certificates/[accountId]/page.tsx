'use client'

import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { useParams, useRouter } from 'next/navigation'
import { 
  Download, 
  FileText,
  ArrowLeft,
  Award,
  FileCheck,
  Send,
  Info
} from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { depositService } from '@/services/deposit.service'
import { formatCurrency } from '@/lib/utils'
import { useToast } from '@/hooks/use-toast'

export default function CertificatesPage() {
  const params = useParams()
  const router = useRouter()
  const { toast } = useToast()
  const accountId = parseInt(params.accountId as string)

  const [activeTab, setActiveTab] = useState('interest')
  const [financialYear, setFinancialYear] = useState('2025-26')
  const [tdsQuarter, setTdsQuarter] = useState<number>(1)

  // Fetch account details
  const { data: accountData } = useQuery({
    queryKey: ['deposit-account', accountId],
    queryFn: () => depositService.getAccount(accountId.toString()),
  })

  // Fetch interest summary
  const { data: interestSummary, isLoading: interestLoading } = useQuery({
    queryKey: ['interest-summary', accountId, financialYear],
    queryFn: () => depositService.getInterestSummary(accountId, { financial_year: financialYear }),
    enabled: activeTab === 'interest',
  })

  // Generate interest certificate mutation
  const generateInterestCertMutation = useMutation({
    mutationFn: () =>
      depositService.getInterestCertificatePDF(accountId, { financial_year: financialYear }),
    onSuccess: (response) => {
      const blob = response.data
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `interest_certificate_${accountId}_FY${financialYear}.pdf`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
      
      toast({
        title: 'Success',
        description: 'Interest certificate downloaded successfully',
      })
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to generate interest certificate',
        variant: 'destructive',
      })
    },
  })

  // Generate TDS certificate mutation
  const generateTDSCertMutation = useMutation({
    mutationFn: (quarter?: number) =>
      depositService.getTDSCertificate(accountId, {
        financial_year: financialYear,
        quarter: quarter,
      }),
    onSuccess: (response) => {
      const blob = response.data
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `tds_certificate_${accountId}_FY${financialYear}_Q${tdsQuarter || 'Annual'}.pdf`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
      
      toast({
        title: 'Success',
        description: 'TDS certificate (Form 16A) downloaded successfully',
      })
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to generate TDS certificate',
        variant: 'destructive',
      })
    },
  })

  // Issue certificate mutation
  const issueCertificateMutation = useMutation({
    mutationFn: (data: {
      certificate_type: 'interest' | 'tds'
      financial_year: string
      quarter?: number
    }) => depositService.issueCertificate(accountId, data),
    onSuccess: () => {
      toast({
        title: 'Success',
        description: 'Certificate issued and recorded successfully',
      })
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to issue certificate',
        variant: 'destructive',
      })
    },
  })

  const handleGenerateInterestCert = () => {
    generateInterestCertMutation.mutate()
  }

  const handleGenerateTDSCert = (quarter?: number) => {
    generateTDSCertMutation.mutate(quarter)
  }

  const handleIssueAndDownload = (type: 'interest' | 'tds') => {
    issueCertificateMutation.mutate({
      certificate_type: type,
      financial_year: financialYear,
      quarter: type === 'tds' ? tdsQuarter : undefined,
    })

    if (type === 'interest') {
      handleGenerateInterestCert()
    } else {
      handleGenerateTDSCert(tdsQuarter)
    }
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" onClick={() => router.back()}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Certificates</h1>
              {accountData && (
                <p className="text-gray-600 mt-1">
                  Account: {accountData.data?.account_number} - {accountData.data?.customer_name}
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Financial Year Selector */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <Label className="text-base font-semibold">Financial Year:</Label>
              <Select value={financialYear} onValueChange={setFinancialYear}>
                <SelectTrigger className="w-48">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {['2025-26', '2024-25', '2023-24', '2022-23', '2021-22'].map((fy) => (
                    <SelectItem key={fy} value={fy}>
                      FY {fy}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Badge variant="outline" className="text-sm">
                April {financialYear.split('-')[0]} to March {financialYear.split('-')[1]}
              </Badge>
            </div>
          </CardContent>
        </Card>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="interest">
              <Award className="h-4 w-4 mr-2" />
              Interest Certificate
            </TabsTrigger>
            <TabsTrigger value="tds">
              <FileCheck className="h-4 w-4 mr-2" />
              TDS Certificate (Form 16A)
            </TabsTrigger>
          </TabsList>

          {/* Interest Certificate Tab */}
          <TabsContent value="interest" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Interest Certificate</CardTitle>
                <p className="text-sm text-gray-600 mt-1">
                  Annual certificate showing total interest earned for tax filing
                </p>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Interest Summary */}
                {interestLoading ? (
                  <div className="space-y-4">
                    <div className="h-20 bg-gray-100 rounded animate-pulse" />
                    <div className="h-20 bg-gray-100 rounded animate-pulse" />
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-blue-50 p-4 rounded-lg">
                      <p className="text-sm text-gray-600">Total Interest Earned</p>
                      <p className="text-2xl font-bold text-blue-600 mt-1">
                        {formatCurrency(interestSummary?.data?.total_interest || 0)}
                      </p>
                    </div>
                    <div className="bg-red-50 p-4 rounded-lg">
                      <p className="text-sm text-gray-600">TDS Deducted</p>
                      <p className="text-2xl font-bold text-red-600 mt-1">
                        {formatCurrency(interestSummary?.data?.total_tds || 0)}
                      </p>
                    </div>
                    <div className="bg-green-50 p-4 rounded-lg">
                      <p className="text-sm text-gray-600">Net Interest</p>
                      <p className="text-2xl font-bold text-green-600 mt-1">
                        {formatCurrency(interestSummary?.data?.net_interest || 0)}
                      </p>
                    </div>
                  </div>
                )}

                {/* Monthly Breakdown */}
                {interestSummary?.data?.monthly_breakdown && (
                  <div>
                    <h4 className="font-semibold mb-3">Monthly Breakdown</h4>
                    <div className="overflow-x-auto">
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Month</TableHead>
                            <TableHead className="text-right">Interest</TableHead>
                            <TableHead className="text-right">TDS</TableHead>
                            <TableHead className="text-right">Net Amount</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {interestSummary.data.monthly_breakdown.map((month: any) => (
                            <TableRow key={month.month}>
                              <TableCell className="font-medium">{month.month}</TableCell>
                              <TableCell className="text-right">
                                {formatCurrency(month.interest)}
                              </TableCell>
                              <TableCell className="text-right text-red-600">
                                {formatCurrency(month.tds)}
                              </TableCell>
                              <TableCell className="text-right font-semibold">
                                {formatCurrency(month.net_amount)}
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className="flex gap-3">
                  <Button
                    onClick={handleGenerateInterestCert}
                    disabled={generateInterestCertMutation.isPending}
                    className="flex-1"
                    size="lg"
                  >
                    {generateInterestCertMutation.isPending ? (
                      <>Generating...</>
                    ) : (
                      <>
                        <Download className="h-5 w-5 mr-2" />
                        Download Certificate
                      </>
                    )}
                  </Button>
                  <Button
                    onClick={() => handleIssueAndDownload('interest')}
                    disabled={
                      generateInterestCertMutation.isPending ||
                      issueCertificateMutation.isPending
                    }
                    variant="outline"
                    className="flex-1"
                    size="lg"
                  >
                    <Send className="h-5 w-5 mr-2" />
                    Issue & Download
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Info Card */}
            <Card className="bg-green-50 border-green-200">
              <CardContent className="pt-6">
                <div className="flex gap-3">
                  <Info className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
                  <div>
                    <h3 className="font-semibold text-green-900">About Interest Certificate</h3>
                    <ul className="text-sm text-green-800 mt-2 space-y-1">
                      <li>• Certificate shows total interest earned during the financial year</li>
                      <li>• Includes month-wise breakdown and TDS deducted</li>
                      <li>• Required for income tax filing (ITR)</li>
                      <li>• Customer can use this for claiming interest income</li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* TDS Certificate Tab */}
          <TabsContent value="tds" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>TDS Certificate (Form 16A)</CardTitle>
                <p className="text-sm text-gray-600 mt-1">
                  Quarterly or annual TDS certificate as per Income Tax rules
                </p>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Quarter Selection */}
                <div className="space-y-2">
                  <Label>Select Quarter (Optional)</Label>
                  <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                    <Button
                      variant={tdsQuarter === 0 ? 'default' : 'outline'}
                      onClick={() => setTdsQuarter(0)}
                      className="w-full"
                    >
                      Annual
                    </Button>
                    <Button
                      variant={tdsQuarter === 1 ? 'default' : 'outline'}
                      onClick={() => setTdsQuarter(1)}
                      className="w-full"
                    >
                      Q1
                      <span className="text-xs ml-1">(Apr-Jun)</span>
                    </Button>
                    <Button
                      variant={tdsQuarter === 2 ? 'default' : 'outline'}
                      onClick={() => setTdsQuarter(2)}
                      className="w-full"
                    >
                      Q2
                      <span className="text-xs ml-1">(Jul-Sep)</span>
                    </Button>
                    <Button
                      variant={tdsQuarter === 3 ? 'default' : 'outline'}
                      onClick={() => setTdsQuarter(3)}
                      className="w-full"
                    >
                      Q3
                      <span className="text-xs ml-1">(Oct-Dec)</span>
                    </Button>
                    <Button
                      variant={tdsQuarter === 4 ? 'default' : 'outline'}
                      onClick={() => setTdsQuarter(4)}
                      className="w-full"
                    >
                      Q4
                      <span className="text-xs ml-1">(Jan-Mar)</span>
                    </Button>
                  </div>
                </div>

                {/* Certificate Details */}
                <div className="bg-gray-50 p-4 rounded-lg space-y-3">
                  <h4 className="font-semibold">Certificate Details</h4>
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div>
                      <p className="text-gray-600">Account Number</p>
                      <p className="font-medium">{accountData?.data?.account_number}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Account Type</p>
                      <p className="font-medium">{accountData?.data?.account_type}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Financial Year</p>
                      <p className="font-medium">FY {financialYear}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Period</p>
                      <p className="font-medium">
                        {tdsQuarter === 0 ? 'Annual' : `Quarter ${tdsQuarter}`}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-3">
                  <Button
                    onClick={() => handleGenerateTDSCert(tdsQuarter || undefined)}
                    disabled={generateTDSCertMutation.isPending}
                    className="flex-1"
                    size="lg"
                  >
                    {generateTDSCertMutation.isPending ? (
                      <>Generating...</>
                    ) : (
                      <>
                        <Download className="h-5 w-5 mr-2" />
                        Download Form 16A
                      </>
                    )}
                  </Button>
                  <Button
                    onClick={() => handleIssueAndDownload('tds')}
                    disabled={
                      generateTDSCertMutation.isPending ||
                      issueCertificateMutation.isPending
                    }
                    variant="outline"
                    className="flex-1"
                    size="lg"
                  >
                    <Send className="h-5 w-5 mr-2" />
                    Issue & Download
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Info Card */}
            <Card className="bg-blue-50 border-blue-200">
              <CardContent className="pt-6">
                <div className="flex gap-3">
                  <Info className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
                  <div>
                    <h3 className="font-semibold text-blue-900">About Form 16A</h3>
                    <ul className="text-sm text-blue-800 mt-2 space-y-1">
                      <li>• Form 16A is the TDS certificate issued by deductor to deductee</li>
                      <li>• Contains details of TDS deducted and deposited with tax authorities</li>
                      <li>• Includes TAN, PAN, and challan details</li>
                      <li>• Can be generated quarterly or annually</li>
                      <li>• Customer needs this to claim TDS credit while filing ITR</li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Button variant="outline" className="justify-start h-auto py-4">
                <div className="text-left">
                  <div className="flex items-center gap-2 font-semibold">
                    <FileText className="h-5 w-5" />
                    View Certificate History
                  </div>
                  <p className="text-sm text-gray-600 mt-1">
                    See all previously issued certificates
                  </p>
                </div>
              </Button>
              <Button variant="outline" className="justify-start h-auto py-4">
                <div className="text-left">
                  <div className="flex items-center gap-2 font-semibold">
                    <Send className="h-5 w-5" />
                    Email Certificates
                  </div>
                  <p className="text-sm text-gray-600 mt-1">
                    Send certificates directly to customer email
                  </p>
                </div>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
