'use client'

import { useQuery } from '@tanstack/react-query'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { 
  ArrowLeft, 
  Calendar,
  TrendingUp,
  DollarSign,
  User,
  FileText,
  ArrowUpCircle,
  ArrowDownCircle
} from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { depositService } from '@/services/deposit.service'
import { formatCurrency, formatDate, formatDateTime, getStatusColor } from '@/lib/utils'

export default function DepositAccountDetailPage() {
  const params = useParams()
  const accountId = params.id as string

  const { data: account, isLoading } = useQuery({
    queryKey: ['deposit-account', accountId],
    queryFn: () => depositService.getAccount(accountId),
  })

  const { data: transactions } = useQuery({
    queryKey: ['deposit-transactions', accountId],
    queryFn: () => depositService.getTransactions(accountId, { page: 1, page_size: 20 }),
    enabled: !!accountId,
  })

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="space-y-6">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-48 w-full" />
        </div>
      </DashboardLayout>
    )
  }

  if (!account?.data) {
    return (
      <DashboardLayout>
        <div className="text-center py-12">
          <p className="text-gray-600">Account not found</p>
        </div>
      </DashboardLayout>
    )
  }

  const acc = account.data

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/deposits/accounts">
              <Button variant="ghost" size="icon">
                <ArrowLeft className="h-5 w-5" />
              </Button>
            </Link>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                {acc.account_number}
              </h1>
              <p className="text-gray-600 mt-1">
                {acc.deposit_type} Account - {acc.customer_name || 'N/A'}
              </p>
            </div>
          </div>
          <div className="flex gap-2">
            <Badge className={getStatusColor(acc.account_status)} style={{ fontSize: '1rem', padding: '0.5rem 1rem' }}>
              {acc.account_status}
            </Badge>
          </div>
        </div>

        {/* Quick Actions */}
        {acc.account_status === 'Active' && (
          <Card className="bg-blue-50 border-blue-200">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-gray-900 mb-1">Account Actions</h3>
                  <p className="text-sm text-gray-600">
                    Deposit or withdraw funds from this account
                  </p>
                </div>
                <div className="flex gap-2">
                  <Button>
                    <ArrowUpCircle className="h-4 w-4 mr-2" />
                    Deposit
                  </Button>
                  {acc.deposit_type === 'Savings' && (
                    <Button variant="outline">
                      <ArrowDownCircle className="h-4 w-4 mr-2" />
                      Withdraw
                    </Button>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <SummaryCard
            label="Account Balance"
            value={formatCurrency(acc.account_balance)}
            icon={DollarSign}
          />
          <SummaryCard
            label="Deposit Amount"
            value={formatCurrency(acc.deposit_amount)}
            icon={TrendingUp}
          />
          <SummaryCard
            label="Interest Rate"
            value={`${acc.interest_rate}% p.a.`}
            icon={TrendingUp}
          />
          <SummaryCard
            label="Opened On"
            value={formatDate(acc.opening_date)}
            icon={Calendar}
          />
        </div>

        {/* Tabs */}
        <Tabs defaultValue="details" className="space-y-6">
          <TabsList>
            <TabsTrigger value="details">Account Details</TabsTrigger>
            <TabsTrigger value="transactions">Transactions</TabsTrigger>
            <TabsTrigger value="interest">Interest Details</TabsTrigger>
            <TabsTrigger value="documents">Documents</TabsTrigger>
          </TabsList>

          {/* Account Details */}
          <TabsContent value="details" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Account Information</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <InfoItem label="Account Number" value={acc.account_number} />
                  <InfoItem label="Deposit Type" value={acc.deposit_type} />
                  <InfoItem label="Account Status" value={acc.account_status} />
                  <InfoItem label="Opening Date" value={formatDate(acc.opening_date)} />
                  <InfoItem label="Deposit Amount" value={formatCurrency(acc.deposit_amount)} />
                  <InfoItem label="Current Balance" value={formatCurrency(acc.account_balance)} />
                  <InfoItem label="Interest Rate" value={`${acc.interest_rate}% per annum`} />
                  {acc.tenure_months && (
                    <InfoItem label="Tenure" value={`${acc.tenure_months} months`} />
                  )}
                  {acc.maturity_date && (
                    <InfoItem label="Maturity Date" value={formatDate(acc.maturity_date)} />
                  )}
                  {acc.maturity_amount && (
                    <InfoItem label="Maturity Amount" value={formatCurrency(acc.maturity_amount)} />
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Customer Information</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-start gap-3">
                  <User className="h-5 w-5 text-gray-400 mt-1" />
                  <div>
                    <p className="text-gray-900 font-medium">{acc.customer_name || 'Customer details not available'}</p>
                    <p className="text-sm text-gray-500 mt-1">
                      Customer ID: {acc.customer_id}
                    </p>
                    <Link href={`/customers/${acc.customer_id}`}>
                      <Button variant="link" className="px-0 h-auto mt-2">
                        View Full Customer Profile →
                      </Button>
                    </Link>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Transactions */}
          <TabsContent value="transactions">
            <Card>
              <CardHeader>
                <CardTitle>Transaction History</CardTitle>
              </CardHeader>
              <CardContent>
                {transactions?.data?.items && transactions.data.items.length > 0 ? (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Date</TableHead>
                        <TableHead>Type</TableHead>
                        <TableHead>Amount</TableHead>
                        <TableHead>Balance</TableHead>
                        <TableHead>Remarks</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {transactions.data.items.map((txn: any) => (
                        <TableRow key={txn.id}>
                          <TableCell>{formatDateTime(txn.transaction_date)}</TableCell>
                          <TableCell>
                            <Badge variant={txn.transaction_type === 'Credit' ? 'success' : 'outline'}>
                              {txn.transaction_type}
                            </Badge>
                          </TableCell>
                          <TableCell className="font-semibold">
                            {formatCurrency(txn.amount)}
                          </TableCell>
                          <TableCell>{formatCurrency(txn.balance_after)}</TableCell>
                          <TableCell className="text-sm text-gray-600">
                            {txn.remarks || '-'}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <FileText className="h-12 w-12 mx-auto text-gray-400 mb-2" />
                    <p>No transactions yet</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Interest Details */}
          <TabsContent value="interest">
            <Card>
              <CardHeader>
                <CardTitle>Interest Information</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <InfoItem label="Interest Rate" value={`${acc.interest_rate}% p.a.`} />
                    <InfoItem label="Interest Earned" value="₹0" />
                    <InfoItem label="Last Interest Posted" value="Not yet posted" />
                  </div>
                  <div className="text-center py-8 text-gray-500">
                    <TrendingUp className="h-12 w-12 mx-auto text-gray-400 mb-2" />
                    <p>Interest calculation history will appear here</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Documents */}
          <TabsContent value="documents">
            <Card>
              <CardHeader>
                <CardTitle>Account Documents</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8 text-gray-500">
                  <FileText className="h-12 w-12 mx-auto text-gray-400 mb-2" />
                  <p>No documents uploaded</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  )
}

function SummaryCard({ label, value, icon: Icon }: { label: string; value: string; icon: any }) {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600 mb-1">{label}</p>
            <p className="text-xl font-bold text-gray-900">{value}</p>
          </div>
          <Icon className="h-8 w-8 text-gray-400" />
        </div>
      </CardContent>
    </Card>
  )
}

function InfoItem({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-sm text-gray-600 mb-1">{label}</p>
      <p className="text-gray-900 font-medium">{value}</p>
    </div>
  )
}
