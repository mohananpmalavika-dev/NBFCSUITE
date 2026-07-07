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
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { ArrowLeft, Plus, Download, RefreshCw, TrendingUp } from 'lucide-react'
import { toast } from 'sonner'

const MOCK_PROVISIONS = [
  {
    id: 1,
    loan_account_number: 'LA-2024-00123',
    customer_name: 'Rajesh Kumar',
    outstanding: 500000,
    npa_category: 'SUBSTANDARD',
    provisioning_rate: 15.0,
    required_provision: 75000,
    existing_provision: 50000,
    additional_provision: 25000,
    last_updated: '2024-01-15',
    status: 'Adequate',
  },
  {
    id: 2,
    loan_account_number: 'LA-2024-00145',
    customer_name: 'Priya Sharma',
    outstanding: 1000000,
    npa_category: 'DOUBTFUL_1',
    provisioning_rate: 50.0,
    required_provision: 500000,
    existing_provision: 400000,
    additional_provision: 100000,
    last_updated: '2024-01-15',
    status: 'Shortfall',
  },
  {
    id: 3,
    loan_account_number: 'LA-2024-00089',
    customer_name: 'Amit Patel',
    outstanding: 750000,
    npa_category: 'DOUBTFUL_2',
    provisioning_rate: 70.0,
    required_provision: 525000,
    existing_provision: 525000,
    additional_provision: 0,
    last_updated: '2024-01-15',
    status: 'Adequate',
  },
]

export default function ProvisionsPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [provisions, setProvisions] = useState(MOCK_PROVISIONS)
  const [categoryFilter, setCategoryFilter] = useState<string>('')
  const [statusFilter, setStatusFilter] = useState<string>('')

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount)
  }

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      STANDARD: 'bg-green-100 text-green-800',
      SUBSTANDARD: 'bg-red-100 text-red-800',
      DOUBTFUL_1: 'bg-red-200 text-red-900',
      DOUBTFUL_2: 'bg-red-300 text-red-900',
      DOUBTFUL_3: 'bg-red-400 text-red-950',
      LOSS: 'bg-gray-800 text-white',
    }
    return colors[category] || 'bg-gray-100 text-gray-800'
  }

  const getStatusColor = (status: string) => {
    return status === 'Adequate'
      ? 'bg-green-100 text-green-800'
      : 'bg-orange-100 text-orange-800'
  }

  const filteredProvisions = provisions.filter((prov) => {
    if (categoryFilter && prov.npa_category !== categoryFilter) return false
    if (statusFilter && prov.status !== statusFilter) return false
    return true
  })

  const totalOutstanding = filteredProvisions.reduce(
    (sum, p) => sum + p.outstanding,
    0
  )
  const totalRequiredProvision = filteredProvisions.reduce(
    (sum, p) => sum + p.required_provision,
    0
  )
  const totalExistingProvision = filteredProvisions.reduce(
    (sum, p) => sum + p.existing_provision,
    0
  )
  const totalAdditionalProvision = filteredProvisions.reduce(
    (sum, p) => sum + p.additional_provision,
    0
  )

  const provisioningCoverageRatio =
    totalRequiredProvision > 0
      ? (totalExistingProvision / totalRequiredProvision) * 100
      : 0

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="icon" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">Provision Management</h1>
            <p className="text-muted-foreground">
              Track and manage loan loss provisions
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" onClick={() => setLoading(true)}>
            <RefreshCw
              className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`}
            />
            Refresh
          </Button>
          <Button variant="outline">
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
          <Button onClick={() => router.push('/accounting/npa/calculator')}>
            <Plus className="mr-2 h-4 w-4" />
            Create Provision
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">
              Total Outstanding
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(totalOutstanding)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {filteredProvisions.length} accounts
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">
              Required Provision
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              {formatCurrency(totalRequiredProvision)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">As per RBI norms</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">
              Existing Provision
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">
              {formatCurrency(totalExistingProvision)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">Current balance</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">
              Additional Needed
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {formatCurrency(totalAdditionalProvision)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {provisioningCoverageRatio.toFixed(1)}% coverage
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <label className="text-sm font-medium">NPA Category</label>
              <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="All categories" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Categories</SelectItem>
                  <SelectItem value="SUBSTANDARD">Substandard</SelectItem>
                  <SelectItem value="DOUBTFUL_1">Doubtful-1</SelectItem>
                  <SelectItem value="DOUBTFUL_2">Doubtful-2</SelectItem>
                  <SelectItem value="DOUBTFUL_3">Doubtful-3</SelectItem>
                  <SelectItem value="LOSS">Loss</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Provision Status</label>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="All statuses" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Statuses</SelectItem>
                  <SelectItem value="Adequate">Adequate</SelectItem>
                  <SelectItem value="Shortfall">Shortfall</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-end">
              <Button
                variant="outline"
                onClick={() => {
                  setCategoryFilter('')
                  setStatusFilter('')
                }}
                className="w-full"
              >
                Clear Filters
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Provisions Table */}
      <Card>
        <CardHeader>
          <CardTitle>Provision Register</CardTitle>
          <CardDescription>
            Detailed list of all loan provisions and requirements
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Loan Account</TableHead>
                <TableHead>Customer</TableHead>
                <TableHead>Category</TableHead>
                <TableHead className="text-right">Outstanding</TableHead>
                <TableHead className="text-right">Rate</TableHead>
                <TableHead className="text-right">Required</TableHead>
                <TableHead className="text-right">Existing</TableHead>
                <TableHead className="text-right">Additional</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Last Updated</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredProvisions.map((provision) => (
                <TableRow key={provision.id}>
                  <TableCell className="font-medium">
                    {provision.loan_account_number}
                  </TableCell>
                  <TableCell>{provision.customer_name}</TableCell>
                  <TableCell>
                    <Badge className={getCategoryColor(provision.npa_category)}>
                      {provision.npa_category.replace(/_/g, '-')}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    {formatCurrency(provision.outstanding)}
                  </TableCell>
                  <TableCell className="text-right">
                    {provision.provisioning_rate}%
                  </TableCell>
                  <TableCell className="text-right font-semibold">
                    {formatCurrency(provision.required_provision)}
                  </TableCell>
                  <TableCell className="text-right">
                    {formatCurrency(provision.existing_provision)}
                  </TableCell>
                  <TableCell className="text-right font-semibold text-red-600">
                    {formatCurrency(provision.additional_provision)}
                  </TableCell>
                  <TableCell>
                    <Badge className={getStatusColor(provision.status)}>
                      {provision.status}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {new Date(provision.last_updated).toLocaleDateString()}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Coverage Ratio Card */}
      <Card>
        <CardHeader>
          <CardTitle>Provisioning Coverage Ratio (PCR)</CardTitle>
          <CardDescription>
            Ratio of provisions held to total NPAs
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <TrendingUp className="h-8 w-8 text-blue-600" />
              <div>
                <p className="text-3xl font-bold text-blue-600">
                  {provisioningCoverageRatio.toFixed(2)}%
                </p>
                <p className="text-sm text-muted-foreground">
                  {totalExistingProvision > 0
                    ? 'Provisions held vs required'
                    : 'No provisions yet'}
                </p>
              </div>
            </div>
            <Button
              onClick={() => router.push('/accounting/npa/pcr')}
              variant="outline"
            >
              View Detailed PCR Report
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
