'use client'

import { useState, useEffect } from 'react'
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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ArrowLeft, Download, RefreshCw, FileText } from 'lucide-react'
import { npaService } from '@/services/npa.service'
import { toast } from 'sonner'

const CATEGORY_COLORS: Record<string, string> = {
  STANDARD: 'bg-green-100 text-green-800',
  SPECIAL_MENTION_0: 'bg-yellow-100 text-yellow-800',
  SPECIAL_MENTION_1: 'bg-yellow-100 text-yellow-800',
  SPECIAL_MENTION_2: 'bg-orange-100 text-orange-800',
  SUBSTANDARD: 'bg-red-100 text-red-800',
  DOUBTFUL_1: 'bg-red-200 text-red-900',
  DOUBTFUL_2: 'bg-red-300 text-red-900',
  DOUBTFUL_3: 'bg-red-400 text-red-900',
  LOSS: 'bg-gray-800 text-white',
}

export default function AssetClassificationRegisterPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [asOfDate, setAsOfDate] = useState(
    new Date().toISOString().split('T')[0]
  )
  const [categoryFilter, setCategoryFilter] = useState<string>('')
  const [register, setRegister] = useState<any>(null)

  useEffect(() => {
    loadRegister()
  }, [])

  const loadRegister = async () => {
    try {
      setLoading(true)
      const response = await npaService.getAssetClassificationRegister({
        as_of_date: asOfDate,
        category_filter: categoryFilter || undefined,
      })

      if (response.success) {
        setRegister(response.data)
      }
    } catch (error: any) {
      toast.error(error.message || 'Failed to load register')
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

  const exportToExcel = () => {
    toast.info('Excel export functionality coming soon')
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="icon" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">Asset Classification Register</h1>
            <p className="text-muted-foreground">
              Complete portfolio view by NPA category
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" onClick={loadRegister} disabled={loading}>
            <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button variant="outline" onClick={exportToExcel}>
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
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

            <div className="space-y-2">
              <Label htmlFor="category">Category Filter</Label>
              <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="All categories" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Categories</SelectItem>
                  <SelectItem value="STANDARD">Standard</SelectItem>
                  <SelectItem value="SPECIAL_MENTION_0">SMA-0</SelectItem>
                  <SelectItem value="SPECIAL_MENTION_1">SMA-1</SelectItem>
                  <SelectItem value="SPECIAL_MENTION_2">SMA-2</SelectItem>
                  <SelectItem value="SUBSTANDARD">Substandard</SelectItem>
                  <SelectItem value="DOUBTFUL_1">Doubtful-1</SelectItem>
                  <SelectItem value="DOUBTFUL_2">Doubtful-2</SelectItem>
                  <SelectItem value="DOUBTFUL_3">Doubtful-3</SelectItem>
                  <SelectItem value="LOSS">Loss</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-end">
              <Button onClick={loadRegister} disabled={loading} className="w-full">
                <FileText className="mr-2 h-4 w-4" />
                Generate Register
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Summary Statistics */}
      {register && (
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">
                Total Accounts
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {register.summary.total_accounts}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">
                Total Outstanding
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {formatCurrency(register.summary.total_outstanding)}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">
                Total Provision
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-600">
                {formatCurrency(register.summary.total_provision)}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">NPA Ratio</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                {formatPercentage(register.summary.npa_ratio)}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Category-wise Details */}
      {register && (
        <Tabs defaultValue="all" className="space-y-4">
          <TabsList>
            <TabsTrigger value="all">All Categories</TabsTrigger>
            <TabsTrigger value="npa">NPA Only</TabsTrigger>
            <TabsTrigger value="sma">SMA Only</TabsTrigger>
          </TabsList>

          <TabsContent value="all" className="space-y-4">
            {Object.entries(register.categories).map(([category, data]: [string, any]) => (
              <Card key={category}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <Badge className={CATEGORY_COLORS[category]}>
                        {category.replace(/_/g, ' ')}
                      </Badge>
                      <div>
                        <CardTitle className="text-lg">
                          {data.account_count} Accounts
                        </CardTitle>
                        <CardDescription>
                          Outstanding: {formatCurrency(data.total_outstanding)} |
                          Provision: {formatCurrency(data.total_provision)} ({formatPercentage(data.provisioning_rate)})
                        </CardDescription>
                      </div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  {data.accounts && data.accounts.length > 0 ? (
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Loan Account</TableHead>
                          <TableHead>Customer</TableHead>
                          <TableHead className="text-right">Outstanding</TableHead>
                          <TableHead className="text-right">DPD</TableHead>
                          <TableHead className="text-right">Required Provision</TableHead>
                          <TableHead className="text-right">Existing Provision</TableHead>
                          <TableHead>Last Payment</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {data.accounts.slice(0, 10).map((account: any) => (
                          <TableRow key={account.loan_account_id}>
                            <TableCell className="font-medium">
                              {account.loan_account_number}
                            </TableCell>
                            <TableCell>{account.customer_name}</TableCell>
                            <TableCell className="text-right">
                              {formatCurrency(account.outstanding_principal)}
                            </TableCell>
                            <TableCell className="text-right">
                              {account.days_past_due}
                            </TableCell>
                            <TableCell className="text-right">
                              {formatCurrency(account.required_provision)}
                            </TableCell>
                            <TableCell className="text-right">
                              {formatCurrency(account.existing_provision)}
                            </TableCell>
                            <TableCell>
                              {account.last_payment_date
                                ? new Date(account.last_payment_date).toLocaleDateString()
                                : 'N/A'}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  ) : (
                    <p className="text-center text-muted-foreground py-4">
                      No accounts in this category
                    </p>
                  )}
                </CardContent>
              </Card>
            ))}
          </TabsContent>

          <TabsContent value="npa">
            <Card>
              <CardHeader>
                <CardTitle>NPA Accounts Only</CardTitle>
                <CardDescription>
                  Substandard, Doubtful, and Loss categories
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Filter shows only NPA categories
                </p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="sma">
            <Card>
              <CardHeader>
                <CardTitle>SMA Accounts Only</CardTitle>
                <CardDescription>
                  Special Mention Accounts (early warning)
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Filter shows only SMA categories
                </p>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}

      {!register && !loading && (
        <Card>
          <CardContent className="text-center py-12">
            <FileText className="mx-auto h-16 w-16 mb-4 opacity-30" />
            <p className="text-lg font-medium text-muted-foreground">
              No data loaded
            </p>
            <p className="text-sm text-muted-foreground">
              Select date and click Generate Register
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
