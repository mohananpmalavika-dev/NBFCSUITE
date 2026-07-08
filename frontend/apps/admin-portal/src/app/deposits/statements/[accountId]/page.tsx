'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { useParams, useRouter } from 'next/navigation'
import { 
  Download, 
  Mail, 
  FileText,
  ArrowLeft,
  Calendar,
  FileSpreadsheet,
  Send,
  CheckCircle
} from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { depositService } from '@/services/deposit.service'
import { useToast } from '@/hooks/use-toast'
import { format as formatDate } from 'date-fns'

export default function StatementGenerationPage() {
  const params = useParams()
  const router = useRouter()
  const { toast } = useToast()
  const accountId = parseInt(params.accountId as string)

  const [activeTab, setActiveTab] = useState('custom')
  
  // Custom statement fields
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [format, setFormat] = useState<'pdf' | 'excel'>('pdf')
  const [includeDetails, setIncludeDetails] = useState(true)

  // Email fields
  const [emailTo, setEmailTo] = useState('')
  const [emailFormat, setEmailFormat] = useState<'pdf' | 'excel'>('pdf')

  // Quarterly statement fields
  const [quarterYear, setQuarterYear] = useState(new Date().getFullYear())
  const [quarter, setQuarter] = useState(1)

  // Annual statement fields
  const [financialYear, setFinancialYear] = useState('2025-26')

  // Generate custom statement mutation
  const generateStatementMutation = useMutation({
    mutationFn: () => {
      if (format === 'pdf') {
        return depositService.generateStatementPDF(accountId, {
          start_date: startDate,
          end_date: endDate,
        })
      } else {
        return depositService.generateStatementExcel(accountId, {
          start_date: startDate,
          end_date: endDate,
        })
      }
    },
    onSuccess: (response) => {
      const blob = response.data
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `statement_${accountId}_${startDate}_${endDate}.${format === 'pdf' ? 'pdf' : 'xlsx'}`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
      
      toast({
        title: 'Success',
        description: `Statement downloaded successfully as ${format.toUpperCase()}`,
      })
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to generate statement',
        variant: 'destructive',
      })
    },
  })

  // Email statement mutation
  const emailStatementMutation = useMutation({
    mutationFn: () =>
      depositService.emailStatement(accountId, {
        start_date: startDate,
        end_date: endDate,
        email_to: emailTo,
        format: emailFormat,
      }),
    onSuccess: () => {
      toast({
        title: 'Success',
        description: `Statement sent to ${emailTo}`,
      })
      setEmailTo('')
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to send statement',
        variant: 'destructive',
      })
    },
  })

  // Generate quarterly statement mutation
  const generateQuarterlyMutation = useMutation({
    mutationFn: () =>
      depositService.getQuarterlyStatement(accountId, {
        year: quarterYear,
        quarter: quarter,
      }),
    onSuccess: (response) => {
      const blob = response.data
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `quarterly_statement_${accountId}_Q${quarter}_${quarterYear}.pdf`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
      
      toast({
        title: 'Success',
        description: `Quarterly statement downloaded successfully`,
      })
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to generate quarterly statement',
        variant: 'destructive',
      })
    },
  })

  // Generate annual statement mutation
  const generateAnnualMutation = useMutation({
    mutationFn: () =>
      depositService.getAnnualStatement(accountId, {
        financial_year: financialYear,
      }),
    onSuccess: (response) => {
      const blob = response.data
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `annual_statement_${accountId}_FY${financialYear}.pdf`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
      
      toast({
        title: 'Success',
        description: `Annual statement downloaded successfully`,
      })
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to generate annual statement',
        variant: 'destructive',
      })
    },
  })

  const handleGenerateStatement = () => {
    if (!startDate || !endDate) {
      toast({
        title: 'Validation Error',
        description: 'Please select start and end dates',
        variant: 'destructive',
      })
      return
    }

    if (new Date(startDate) > new Date(endDate)) {
      toast({
        title: 'Validation Error',
        description: 'Start date must be before end date',
        variant: 'destructive',
      })
      return
    }

    generateStatementMutation.mutate()
  }

  const handleEmailStatement = () => {
    if (!startDate || !endDate) {
      toast({
        title: 'Validation Error',
        description: 'Please select start and end dates',
        variant: 'destructive',
      })
      return
    }

    if (!emailTo) {
      toast({
        title: 'Validation Error',
        description: 'Please enter email address',
        variant: 'destructive',
      })
      return
    }

    emailStatementMutation.mutate()
  }

  const handleQuickDateRange = (range: string) => {
    const today = new Date()
    let start = new Date()
    
    switch (range) {
      case 'last7days':
        start.setDate(today.getDate() - 7)
        break
      case 'last30days':
        start.setDate(today.getDate() - 30)
        break
      case 'last3months':
        start.setMonth(today.getMonth() - 3)
        break
      case 'last6months':
        start.setMonth(today.getMonth() - 6)
        break
      case 'thisyear':
        start = new Date(today.getFullYear(), 0, 1)
        break
    }

    setStartDate(formatDate(start, 'yyyy-MM-dd'))
    setEndDate(formatDate(today, 'yyyy-MM-dd'))
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
              <h1 className="text-3xl font-bold text-gray-900">Generate Statement</h1>
              <p className="text-gray-600 mt-1">
                Account: {accountId}
              </p>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="custom">Custom Statement</TabsTrigger>
            <TabsTrigger value="email">Email Statement</TabsTrigger>
            <TabsTrigger value="quarterly">Quarterly</TabsTrigger>
            <TabsTrigger value="annual">Annual</TabsTrigger>
          </TabsList>

          {/* Custom Statement Tab */}
          <TabsContent value="custom" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Custom Date Range Statement</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Quick Date Ranges */}
                <div>
                  <Label className="mb-3 block">Quick Select</Label>
                  <div className="flex flex-wrap gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleQuickDateRange('last7days')}
                    >
                      Last 7 Days
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleQuickDateRange('last30days')}
                    >
                      Last 30 Days
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleQuickDateRange('last3months')}
                    >
                      Last 3 Months
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleQuickDateRange('last6months')}
                    >
                      Last 6 Months
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleQuickDateRange('thisyear')}
                    >
                      This Year
                    </Button>
                  </div>
                </div>

                {/* Date Range */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="startDate">Start Date</Label>
                    <Input
                      id="startDate"
                      type="date"
                      value={startDate}
                      onChange={(e) => setStartDate(e.target.value)}
                      max={endDate || undefined}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="endDate">End Date</Label>
                    <Input
                      id="endDate"
                      type="date"
                      value={endDate}
                      onChange={(e) => setEndDate(e.target.value)}
                      min={startDate || undefined}
                      max={formatDate(new Date(), 'yyyy-MM-dd')}
                    />
                  </div>
                </div>

                {/* Format Selection */}
                <div className="space-y-2">
                  <Label htmlFor="format">Download Format</Label>
                  <Select
                    value={format}
                    onValueChange={(value: 'pdf' | 'excel') => setFormat(value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="pdf">
                        <div className="flex items-center gap-2">
                          <FileText className="h-4 w-4" />
                          PDF Format
                        </div>
                      </SelectItem>
                      <SelectItem value="excel">
                        <div className="flex items-center gap-2">
                          <FileSpreadsheet className="h-4 w-4" />
                          Excel Format
                        </div>
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Options */}
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="includeDetails"
                    checked={includeDetails}
                    onChange={(e) => setIncludeDetails(e.target.checked)}
                    className="rounded border-gray-300"
                  />
                  <Label htmlFor="includeDetails" className="cursor-pointer">
                    Include transaction details and interest breakup
                  </Label>
                </div>

                {/* Generate Button */}
                <Button
                  onClick={handleGenerateStatement}
                  disabled={generateStatementMutation.isPending}
                  className="w-full"
                  size="lg"
                >
                  {generateStatementMutation.isPending ? (
                    <>Generating...</>
                  ) : (
                    <>
                      <Download className="h-5 w-5 mr-2" />
                      Generate & Download Statement
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Email Statement Tab */}
          <TabsContent value="email" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Email Statement to Customer</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Date Range */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="emailStartDate">Start Date</Label>
                    <Input
                      id="emailStartDate"
                      type="date"
                      value={startDate}
                      onChange={(e) => setStartDate(e.target.value)}
                      max={endDate || undefined}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="emailEndDate">End Date</Label>
                    <Input
                      id="emailEndDate"
                      type="date"
                      value={endDate}
                      onChange={(e) => setEndDate(e.target.value)}
                      min={startDate || undefined}
                      max={formatDate(new Date(), 'yyyy-MM-dd')}
                    />
                  </div>
                </div>

                {/* Email Address */}
                <div className="space-y-2">
                  <Label htmlFor="emailTo">Email Address</Label>
                  <Input
                    id="emailTo"
                    type="email"
                    placeholder="customer@example.com"
                    value={emailTo}
                    onChange={(e) => setEmailTo(e.target.value)}
                  />
                  <p className="text-xs text-gray-500">
                    Statement will be sent to this email address
                  </p>
                </div>

                {/* Format Selection */}
                <div className="space-y-2">
                  <Label htmlFor="emailFormat">Format</Label>
                  <Select
                    value={emailFormat}
                    onValueChange={(value: 'pdf' | 'excel') => setEmailFormat(value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="pdf">PDF Format</SelectItem>
                      <SelectItem value="excel">Excel Format</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Send Button */}
                <Button
                  onClick={handleEmailStatement}
                  disabled={emailStatementMutation.isPending}
                  className="w-full"
                  size="lg"
                >
                  {emailStatementMutation.isPending ? (
                    <>Sending...</>
                  ) : (
                    <>
                      <Send className="h-5 w-5 mr-2" />
                      Send Statement via Email
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Quarterly Statement Tab */}
          <TabsContent value="quarterly" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Quarterly Statement</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Year Selection */}
                <div className="space-y-2">
                  <Label htmlFor="quarterYear">Year</Label>
                  <Select
                    value={quarterYear.toString()}
                    onValueChange={(value) => setQuarterYear(parseInt(value))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {[...Array(5)].map((_, i) => {
                        const year = new Date().getFullYear() - i
                        return (
                          <SelectItem key={year} value={year.toString()}>
                            {year}
                          </SelectItem>
                        )
                      })}
                    </SelectContent>
                  </Select>
                </div>

                {/* Quarter Selection */}
                <div className="space-y-2">
                  <Label htmlFor="quarter">Quarter</Label>
                  <Select
                    value={quarter.toString()}
                    onValueChange={(value) => setQuarter(parseInt(value))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1">Q1 (Jan - Mar)</SelectItem>
                      <SelectItem value="2">Q2 (Apr - Jun)</SelectItem>
                      <SelectItem value="3">Q3 (Jul - Sep)</SelectItem>
                      <SelectItem value="4">Q4 (Oct - Dec)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Generate Button */}
                <Button
                  onClick={() => generateQuarterlyMutation.mutate()}
                  disabled={generateQuarterlyMutation.isPending}
                  className="w-full"
                  size="lg"
                >
                  {generateQuarterlyMutation.isPending ? (
                    <>Generating...</>
                  ) : (
                    <>
                      <Download className="h-5 w-5 mr-2" />
                      Generate Quarterly Statement
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Annual Statement Tab */}
          <TabsContent value="annual" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Annual Statement</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Financial Year Selection */}
                <div className="space-y-2">
                  <Label htmlFor="financialYear">Financial Year</Label>
                  <Select
                    value={financialYear}
                    onValueChange={setFinancialYear}
                  >
                    <SelectTrigger>
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
                  <p className="text-xs text-gray-500">
                    Financial year runs from April to March
                  </p>
                </div>

                {/* Generate Button */}
                <Button
                  onClick={() => generateAnnualMutation.mutate()}
                  disabled={generateAnnualMutation.isPending}
                  className="w-full"
                  size="lg"
                >
                  {generateAnnualMutation.isPending ? (
                    <>Generating...</>
                  ) : (
                    <>
                      <Download className="h-5 w-5 mr-2" />
                      Generate Annual Statement
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Info Card */}
        <Card className="bg-blue-50 border-blue-200">
          <CardContent className="pt-6">
            <div className="flex gap-3">
              <CheckCircle className="h-5 w-5 text-blue-600 mt-0.5" />
              <div>
                <h3 className="font-semibold text-blue-900">Statement Features</h3>
                <ul className="text-sm text-blue-800 mt-2 space-y-1 list-disc list-inside">
                  <li>Professional PDF format with complete transaction details</li>
                  <li>Excel format for easy data analysis and record keeping</li>
                  <li>Email statements directly to customers with one click</li>
                  <li>Quarterly and annual statements for tax and compliance purposes</li>
                  <li>All statements include opening balance, transactions, and closing balance</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
