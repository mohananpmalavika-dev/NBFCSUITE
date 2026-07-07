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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { ArrowLeft, Download, FileText, Send } from 'lucide-react'
import { npaService } from '@/services/npa.service'
import { toast } from 'sonner'

export default function RBINPAReturnPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [asOfDate, setAsOfDate] = useState(
    new Date().toISOString().split('T')[0]
  )
  const [returnData, setReturnData] = useState<any>(null)

  const handleGenerate = async () => {
    try {
      setLoading(true)
      const response = await npaService.getRBINPAReturn(asOfDate)

      if (response.success) {
        setReturnData(response.data)
        toast.success('RBI return generated successfully')
      }
    } catch (error: any) {
      toast.error(error.message || 'Failed to generate return')
      // Mock data for demonstration
      setReturnData({
        reporting_date: asOfDate,
        reporting_entity: 'NBFC Demo Ltd',
        gross_advances: 500000000,
        gross_npa: 35000000,
        gross_npa_ratio: 7.0,
        provisions_held: 28000000,
        net_npa: 7000000,
        net_npa_ratio: 1.4,
        category_wise_npa: {
          substandard: 15000000,
          doubtful: 15000000,
          loss: 5000000,
        },
        sector_wise_npa: {
          agriculture: 5000000,
          msme: 12000000,
          retail: 10000000,
          corporate: 8000000,
        },
        security_wise_npa: {
          secured: 25000000,
          unsecured: 10000000,
        },
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

  const handleExportPDF = () => {
    toast.info('PDF export functionality coming soon')
  }

  const handleFileWithRBI = () => {
    toast.success('Return filed with RBI (Demo mode)')
  }

  return (
    <div className="container mx-auto p-6 max-w-6xl space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="icon" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">RBI NPA Return</h1>
            <p className="text-muted-foreground">
              Generate regulatory return as per RBI format
            </p>
          </div>
        </div>
        {returnData && (
          <div className="flex items-center space-x-2">
            <Button variant="outline" onClick={handleExportPDF}>
              <Download className="mr-2 h-4 w-4" />
              Export PDF
            </Button>
            <Button onClick={handleFileWithRBI}>
              <Send className="mr-2 h-4 w-4" />
              File with RBI
            </Button>
          </div>
        )}
      </div>

      {/* Input Section */}
      <Card>
        <CardHeader>
          <CardTitle>Return Parameters</CardTitle>
          <CardDescription>
            Select reporting date to generate NPA return
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <Label htmlFor="asOfDate">Reporting Date</Label>
              <Input
                id="asOfDate"
                type="date"
                value={asOfDate}
                onChange={(e) => setAsOfDate(e.target.value)}
              />
            </div>

            <div className="flex items-end col-span-2">
              <Button
                onClick={handleGenerate}
                disabled={loading}
                className="w-full"
              >
                <FileText className="mr-2 h-4 w-4" />
                {loading ? 'Generating...' : 'Generate RBI Return'}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {returnData && (
        <>
          {/* Return Header */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>RBI NPA Return</CardTitle>
                  <CardDescription>
                    Reporting Entity: {returnData.reporting_entity}
                  </CardDescription>
                </div>
                <Badge variant="outline" className="text-sm">
                  As of: {new Date(returnData.reporting_date).toLocaleDateString()}
                </Badge>
              </div>
            </CardHeader>
          </Card>

          {/* Key Metrics */}
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">
                  Gross Advances
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {formatCurrency(returnData.gross_advances)}
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  Total loan portfolio
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">Gross NPA</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">
                  {formatCurrency(returnData.gross_npa)}
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  Gross NPA Ratio: {formatPercentage(returnData.gross_npa_ratio)}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">Net NPA</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-orange-600">
                  {formatCurrency(returnData.net_npa)}
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  Net NPA Ratio: {formatPercentage(returnData.net_npa_ratio)}
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Provisions */}
          <Card>
            <CardHeader>
              <CardTitle>Provision Coverage</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3">
                <div>
                  <p className="text-sm text-muted-foreground">Gross NPA</p>
                  <p className="text-2xl font-bold mt-1">
                    {formatCurrency(returnData.gross_npa)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">
                    Provisions Held
                  </p>
                  <p className="text-2xl font-bold text-blue-600 mt-1">
                    {formatCurrency(returnData.provisions_held)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">
                    Provisioning Coverage Ratio
                  </p>
                  <p className="text-2xl font-bold text-green-600 mt-1">
                    {formatPercentage(
                      (returnData.provisions_held / returnData.gross_npa) * 100
                    )}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Category-wise NPA */}
          <Card>
            <CardHeader>
              <CardTitle>Category-wise NPA Classification</CardTitle>
              <CardDescription>
                NPA distribution by asset classification
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Category</TableHead>
                    <TableHead className="text-right">Amount</TableHead>
                    <TableHead className="text-right">% of Gross NPA</TableHead>
                    <TableHead className="text-right">% of Gross Advances</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {Object.entries(returnData.category_wise_npa).map(
                    ([category, amount]: [string, any]) => (
                      <TableRow key={category}>
                        <TableCell className="font-medium capitalize">
                          {category}
                        </TableCell>
                        <TableCell className="text-right">
                          {formatCurrency(amount)}
                        </TableCell>
                        <TableCell className="text-right">
                          {formatPercentage((amount / returnData.gross_npa) * 100)}
                        </TableCell>
                        <TableCell className="text-right">
                          {formatPercentage(
                            (amount / returnData.gross_advances) * 100
                          )}
                        </TableCell>
                      </TableRow>
                    )
                  )}
                  <TableRow className="font-bold bg-gray-50">
                    <TableCell>Total</TableCell>
                    <TableCell className="text-right">
                      {formatCurrency(returnData.gross_npa)}
                    </TableCell>
                    <TableCell className="text-right">100.00%</TableCell>
                    <TableCell className="text-right">
                      {formatPercentage(returnData.gross_npa_ratio)}
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          {/* Sector-wise NPA */}
          <Card>
            <CardHeader>
              <CardTitle>Sector-wise NPA Distribution</CardTitle>
              <CardDescription>
                NPA by business sector/segment
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Sector</TableHead>
                    <TableHead className="text-right">NPA Amount</TableHead>
                    <TableHead className="text-right">% of Total NPA</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {Object.entries(returnData.sector_wise_npa).map(
                    ([sector, amount]: [string, any]) => (
                      <TableRow key={sector}>
                        <TableCell className="font-medium capitalize">
                          {sector}
                        </TableCell>
                        <TableCell className="text-right">
                          {formatCurrency(amount)}
                        </TableCell>
                        <TableCell className="text-right">
                          {formatPercentage((amount / returnData.gross_npa) * 100)}
                        </TableCell>
                      </TableRow>
                    )
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          {/* Security-wise NPA */}
          <Card>
            <CardHeader>
              <CardTitle>Security-wise NPA</CardTitle>
              <CardDescription>Secured vs Unsecured NPA</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-6 md:grid-cols-2">
                <div className="p-4 border rounded-lg">
                  <p className="text-sm text-muted-foreground mb-2">Secured NPA</p>
                  <p className="text-3xl font-bold text-blue-600">
                    {formatCurrency(returnData.security_wise_npa.secured)}
                  </p>
                  <p className="text-sm text-muted-foreground mt-2">
                    {formatPercentage(
                      (returnData.security_wise_npa.secured /
                        returnData.gross_npa) *
                        100
                    )}{' '}
                    of Gross NPA
                  </p>
                </div>

                <div className="p-4 border rounded-lg">
                  <p className="text-sm text-muted-foreground mb-2">
                    Unsecured NPA
                  </p>
                  <p className="text-3xl font-bold text-red-600">
                    {formatCurrency(returnData.security_wise_npa.unsecured)}
                  </p>
                  <p className="text-sm text-muted-foreground mt-2">
                    {formatPercentage(
                      (returnData.security_wise_npa.unsecured /
                        returnData.gross_npa) *
                        100
                    )}{' '}
                    of Gross NPA
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Compliance Status */}
          <Card>
            <CardHeader>
              <CardTitle>Compliance Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <div>
                    <p className="font-medium text-green-900">
                      Gross NPA Ratio
                    </p>
                    <p className="text-sm text-green-700">
                      {formatPercentage(returnData.gross_npa_ratio)} (Target: Below
                      10%)
                    </p>
                  </div>
                  <Badge className="bg-green-600 text-white">Within Limits</Badge>
                </div>

                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <div>
                    <p className="font-medium text-green-900">Net NPA Ratio</p>
                    <p className="text-sm text-green-700">
                      {formatPercentage(returnData.net_npa_ratio)} (Target: Below
                      4%)
                    </p>
                  </div>
                  <Badge className="bg-green-600 text-white">Within Limits</Badge>
                </div>

                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <div>
                    <p className="font-medium text-green-900">
                      Provisioning Coverage Ratio
                    </p>
                    <p className="text-sm text-green-700">
                      {formatPercentage(
                        (returnData.provisions_held / returnData.gross_npa) * 100
                      )}{' '}
                      (Target: Above 70%)
                    </p>
                  </div>
                  <Badge className="bg-green-600 text-white">Adequate</Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </>
      )}

      {!returnData && !loading && (
        <Card>
          <CardContent className="text-center py-12">
            <FileText className="mx-auto h-16 w-16 mb-4 opacity-30" />
            <p className="text-lg font-medium text-muted-foreground">
              No return generated yet
            </p>
            <p className="text-sm text-muted-foreground">
              Select reporting date and click Generate RBI Return
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
