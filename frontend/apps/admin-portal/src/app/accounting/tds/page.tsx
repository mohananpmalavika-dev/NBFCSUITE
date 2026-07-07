'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { tdsService } from '@/services/accounting.service'
import { useToast } from '@/hooks/use-toast'
import { 
  FileText, 
  Receipt, 
  Award, 
  Calendar,
  TrendingUp,
  AlertCircle,
  Download,
  Plus
} from 'lucide-react'
import Link from 'next/link'

export default function TDSPage() {
  const { toast } = useToast()
  const [loading, setLoading] = useState(true)
  const [summary, setSummary] = useState<any>(null)
  const [financialYear] = useState(new Date().getFullYear())

  useEffect(() => {
    loadSummary()
  }, [])

  const loadSummary = async () => {
    try {
      setLoading(true)
      const response = await tdsService.getSummary(financialYear)
      setSummary(response.data)
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to load TDS summary',
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  const stats = [
    {
      title: 'Total Deductions',
      value: summary?.total_deductions || 0,
      icon: FileText,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      title: 'Gross Amount',
      value: `₹${(summary?.total_gross_amount || 0).toLocaleString('en-IN')}`,
      icon: TrendingUp,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      title: 'Total TDS',
      value: `₹${(summary?.total_tds_amount || 0).toLocaleString('en-IN')}`,
      icon: Receipt,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
    {
      title: 'Pending Payment',
      value: `₹${(summary?.payment_status_summary?.find((s: any) => s.status === 'pending')?.amount || 0).toLocaleString('en-IN')}`,
      icon: AlertCircle,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
    },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">TDS Management</h1>
          <p className="text-muted-foreground">
            Tax Deducted at Source - FY {financialYear}-{financialYear + 1}
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" asChild>
            <Link href="/accounting/tds/sections">
              <FileText className="w-4 h-4 mr-2" />
              Configure Sections
            </Link>
          </Button>
          <Button asChild>
            <Link href="/accounting/tds/deductions/new">
              <Plus className="w-4 h-4 mr-2" />
              Record Deduction
            </Link>
          </Button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.title}>
            <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
              <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
              <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                <stat.icon className={`w-4 h-4 ${stat.color}`} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="deductions">Deductions</TabsTrigger>
          <TabsTrigger value="challans">Challans</TabsTrigger>
          <TabsTrigger value="certificates">Certificates</TabsTrigger>
          <TabsTrigger value="returns">Returns</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            {/* Section-wise Summary */}
            <Card>
              <CardHeader>
                <CardTitle>Section-wise Summary</CardTitle>
                <CardDescription>TDS deductions by section</CardDescription>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="text-center py-8 text-muted-foreground">Loading...</div>
                ) : summary?.section_wise_summary?.length > 0 ? (
                  <div className="space-y-3">
                    {summary.section_wise_summary.map((section: any) => (
                      <div key={section.section_code} className="flex items-center justify-between p-3 border rounded-lg">
                        <div>
                          <p className="font-medium">{section.section_code}</p>
                          <p className="text-sm text-muted-foreground">{section.deduction_count} deductions</p>
                        </div>
                        <div className="text-right">
                          <p className="font-semibold">₹{section.total_tds_amount.toLocaleString('en-IN')}</p>
                          <p className="text-sm text-muted-foreground">
                            ₹{section.total_gross_amount.toLocaleString('en-IN')} gross
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    No deductions recorded yet
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Payment Status */}
            <Card>
              <CardHeader>
                <CardTitle>Payment Status</CardTitle>
                <CardDescription>TDS payment tracking</CardDescription>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="text-center py-8 text-muted-foreground">Loading...</div>
                ) : summary?.payment_status_summary?.length > 0 ? (
                  <div className="space-y-3">
                    {summary.payment_status_summary.map((status: any) => (
                      <div key={status.status} className="flex items-center justify-between p-3 border rounded-lg">
                        <div>
                          <p className="font-medium capitalize">{status.status}</p>
                          <p className="text-sm text-muted-foreground">{status.count} deductions</p>
                        </div>
                        <div className="text-right">
                          <p className="font-semibold">₹{status.amount.toLocaleString('en-IN')}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    No payment data available
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
              <CardDescription>Common TDS operations</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
                <Button variant="outline" className="h-auto flex-col py-4" asChild>
                  <Link href="/accounting/tds/deductions/new">
                    <Plus className="w-6 h-6 mb-2" />
                    <span>Record Deduction</span>
                  </Link>
                </Button>
                <Button variant="outline" className="h-auto flex-col py-4" asChild>
                  <Link href="/accounting/tds/challans/new">
                    <Receipt className="w-6 h-6 mb-2" />
                    <span>Create Challan</span>
                  </Link>
                </Button>
                <Button variant="outline" className="h-auto flex-col py-4" asChild>
                  <Link href="/accounting/tds/certificates">
                    <Award className="w-6 h-6 mb-2" />
                    <span>Generate Certificate</span>
                  </Link>
                </Button>
                <Button variant="outline" className="h-auto flex-col py-4" asChild>
                  <Link href="/accounting/tds/returns">
                    <Calendar className="w-6 h-6 mb-2" />
                    <span>Prepare Return</span>
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="deductions">
          <Card>
            <CardHeader>
              <CardTitle>TDS Deductions</CardTitle>
              <CardDescription>View and manage all TDS deductions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <Button asChild>
                  <Link href="/accounting/tds/deductions">View All Deductions</Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="challans">
          <Card>
            <CardHeader>
              <CardTitle>TDS Challans</CardTitle>
              <CardDescription>Payment challans (Form 281)</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <Button asChild>
                  <Link href="/accounting/tds/challans">View All Challans</Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="certificates">
          <Card>
            <CardHeader>
              <CardTitle>TDS Certificates</CardTitle>
              <CardDescription>Form 16A certificates</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <Button asChild>
                  <Link href="/accounting/tds/certificates">View All Certificates</Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="returns">
          <Card>
            <CardHeader>
              <CardTitle>TDS Returns</CardTitle>
              <CardDescription>Form 26Q returns</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <Button asChild>
                  <Link href="/accounting/tds/returns">View All Returns</Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
