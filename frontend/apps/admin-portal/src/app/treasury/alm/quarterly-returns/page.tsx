'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { ArrowLeft, Plus, Download, Send, CheckCircle2 } from 'lucide-react'
import { almService } from '@/services/alm.service'
import { toast } from 'sonner'

const MOCK_RETURNS = [
  { id: 1, year: 2024, quarter: 2, return_number: 'SLS-2024-Q2', return_type: 'SLS', status: 'filed', filed_date: '2024-07-15' },
  { id: 2, year: 2024, quarter: 1, return_number: 'SLS-2024-Q1', return_type: 'SLS', status: 'filed', filed_date: '2024-04-15' },
  { id: 3, year: 2024, quarter: 1, return_number: 'IRS-2024-Q1', return_type: 'IRS', status: 'filed', filed_date: '2024-04-15' },
  { id: 4, year: 2023, quarter: 4, return_number: 'SLS-2023-Q4', return_type: 'SLS', status: 'filed', filed_date: '2024-01-15' },
]

export default function QuarterlyReturnsPage() {
  const router = useRouter()
  const [returns, setReturns] = useState(MOCK_RETURNS)
  const [loading, setLoading] = useState(false)

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      draft: 'bg-gray-100 text-gray-800',
      approved: 'bg-blue-100 text-blue-800',
      filed: 'bg-green-100 text-green-800',
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="icon" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">Quarterly Returns</h1>
            <p className="text-muted-foreground">SLS & IRS returns for RBI compliance</p>
          </div>
        </div>
        <Button><Plus className="mr-2 h-4 w-4" />New Return</Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-3"><CardTitle className="text-sm font-medium">Total Returns</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold">{returns.length}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3"><CardTitle className="text-sm font-medium">Filed This Year</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold text-green-600">{returns.filter(r => r.year === 2024 && r.status === 'filed').length}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3"><CardTitle className="text-sm font-medium">Pending Filing</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold text-orange-600">0</div></CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Returns History</CardTitle>
          <CardDescription>All quarterly returns submitted to RBI</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Return Number</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Year</TableHead>
                <TableHead>Quarter</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Filed Date</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {returns.map((ret) => (
                <TableRow key={ret.id}>
                  <TableCell className="font-medium">{ret.return_number}</TableCell>
                  <TableCell><Badge variant="outline">{ret.return_type}</Badge></TableCell>
                  <TableCell>{ret.year}</TableCell>
                  <TableCell>Q{ret.quarter}</TableCell>
                  <TableCell><Badge className={getStatusColor(ret.status)}>{ret.status.toUpperCase()}</Badge></TableCell>
                  <TableCell>{ret.filed_date ? new Date(ret.filed_date).toLocaleDateString() : '-'}</TableCell>
                  <TableCell>
                    <Button variant="ghost" size="sm"><Download className="h-4 w-4" /></Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Card className="border-blue-200 border-2">
        <CardHeader>
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="h-5 w-5 text-blue-600" />
            <CardTitle className="text-blue-900">Return Types</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="p-4 border rounded-lg">
              <h4 className="font-semibold mb-2">SLS (Structural Liquidity Statement)</h4>
              <ul className="space-y-1 text-sm text-muted-foreground">
                <li>• Maturity ladder of assets & liabilities</li>
                <li>• 12 time buckets from 1 day to 5+ years</li>
                <li>• Submitted quarterly within 15 days of quarter end</li>
              </ul>
            </div>
            <div className="p-4 border rounded-lg">
              <h4 className="font-semibold mb-2">IRS (Interest Rate Sensitivity)</h4>
              <ul className="space-y-1 text-sm text-muted-foreground">
                <li>• Rate sensitive assets & liabilities</li>
                <li>• Gap analysis across time buckets</li>
                <li>• Impact of rate changes on NII</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
