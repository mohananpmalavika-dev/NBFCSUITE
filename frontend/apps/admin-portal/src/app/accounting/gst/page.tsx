"use client";

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { gstService } from '@/services/accounting.service';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ArrowUpRight, ArrowDownRight, FileText, Settings, Database, Receipt } from 'lucide-react';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function GSTDashboardPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState({
    current_month: {
      sales: 0,
      purchases: 0,
      output_tax: 0,
      input_tax: 0,
      net_liability: 0
    },
    pending_returns: 0,
    itc_available: 0,
    gstin_count: 0
  });

  const [monthlyData, setMonthlyData] = useState<any[]>([]);
  const [taxBreakdown, setTaxBreakdown] = useState<any[]>([]);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch summary data (this would come from API)
      // Mock data for now
      setSummary({
        current_month: {
          sales: 5000000,
          purchases: 3500000,
          output_tax: 900000,
          input_tax: 630000,
          net_liability: 270000
        },
        pending_returns: 2,
        itc_available: 450000,
        gstin_count: 1
      });

      // Mock monthly trend data
      setMonthlyData([
        { month: 'Apr', sales: 4200000, purchases: 3100000, net_tax: 198000 },
        { month: 'May', sales: 4500000, purchases: 3200000, net_tax: 234000 },
        { month: 'Jun', sales: 4800000, purchases: 3400000, net_tax: 252000 },
        { month: 'Jul', sales: 5000000, purchases: 3500000, net_tax: 270000 }
      ]);

      // Mock tax breakdown
      setTaxBreakdown([
        { name: 'CGST', value: 135000, color: '#3b82f6' },
        { name: 'SGST', value: 135000, color: '#10b981' },
        { name: 'IGST', value: 0, color: '#f59e0b' }
      ]);

    } catch (error) {
      console.error('Failed to load dashboard data', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(value);
  };

  if (loading) {
    return <div className="container mx-auto py-6">Loading...</div>;
  }

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">GST Dashboard</h1>
          <p className="text-muted-foreground">Overview of GST transactions and compliance</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => router.push('/accounting/gst/configuration')}>
            <Settings className="mr-2 h-4 w-4" />
            Configuration
          </Button>
          <Button onClick={() => router.push('/accounting/gst/transactions/new')}>
            <Receipt className="mr-2 h-4 w-4" />
            New Transaction
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Sales
            </CardTitle>
            <ArrowUpRight className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(summary.current_month.sales)}</div>
            <p className="text-xs text-muted-foreground">Current month</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Purchases
            </CardTitle>
            <ArrowDownRight className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(summary.current_month.purchases)}</div>
            <p className="text-xs text-muted-foreground">Current month</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Output Tax
            </CardTitle>
            <FileText className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(summary.current_month.output_tax)}</div>
            <p className="text-xs text-muted-foreground">Tax collected</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Input Tax Credit
            </CardTitle>
            <Database className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(summary.current_month.input_tax)}</div>
            <p className="text-xs text-muted-foreground">ITC available</p>
          </CardContent>
        </Card>

        <Card className="bg-primary/5">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Net Tax Liability
            </CardTitle>
            <FileText className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-primary">
              {formatCurrency(summary.current_month.net_liability)}
            </div>
            <p className="text-xs text-muted-foreground">To be paid</p>
          </CardContent>
        </Card>
      </div>

      {/* Charts and Details */}
      <Tabs defaultValue="trends" className="space-y-4">
        <TabsList>
          <TabsTrigger value="trends">Monthly Trends</TabsTrigger>
          <TabsTrigger value="breakdown">Tax Breakdown</TabsTrigger>
          <TabsTrigger value="returns">Returns Status</TabsTrigger>
        </TabsList>

        <TabsContent value="trends" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Sales vs Purchases</CardTitle>
                <CardDescription>Monthly comparison</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={monthlyData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                    <Legend />
                    <Bar dataKey="sales" fill="#3b82f6" name="Sales" />
                    <Bar dataKey="purchases" fill="#f59e0b" name="Purchases" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Net Tax Liability Trend</CardTitle>
                <CardDescription>Last 4 months</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={monthlyData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                    <Legend />
                    <Line 
                      type="monotone" 
                      dataKey="net_tax" 
                      stroke="#8b5cf6" 
                      strokeWidth={2}
                      name="Net Tax"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="breakdown" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Current Month Tax Split</CardTitle>
                <CardDescription>CGST, SGST, IGST breakdown</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={taxBreakdown}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {taxBreakdown.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Tax Component Details</CardTitle>
                <CardDescription>Breakdown of current month</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">CGST (9%)</span>
                    <span className="font-semibold">{formatCurrency(135000)}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">SGST (9%)</span>
                    <span className="font-semibold">{formatCurrency(135000)}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">IGST (18%)</span>
                    <span className="font-semibold">{formatCurrency(0)}</span>
                  </div>
                  <div className="border-t pt-2 mt-2">
                    <div className="flex justify-between items-center">
                      <span className="font-semibold">Total Output Tax</span>
                      <span className="font-bold text-lg">{formatCurrency(270000)}</span>
                    </div>
                  </div>
                </div>

                <div className="mt-6 p-4 bg-muted rounded-lg">
                  <h4 className="font-semibold mb-2">Input Tax Credit Available</h4>
                  <div className="text-2xl font-bold text-green-600">
                    {formatCurrency(summary.itc_available)}
                  </div>
                  <Button 
                    variant="link" 
                    className="px-0 mt-2"
                    onClick={() => router.push('/accounting/gst/itc')}
                  >
                    View ITC Details →
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="returns" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>GSTR-1</CardTitle>
                <CardDescription>Outward supplies</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">Due Date: 11th of next month</p>
                  <Button 
                    className="w-full" 
                    onClick={() => router.push('/accounting/gst/returns/gstr1')}
                  >
                    Prepare GSTR-1
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>GSTR-3B</CardTitle>
                <CardDescription>Monthly summary return</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">Due Date: 20th of next month</p>
                  <Button 
                    className="w-full"
                    onClick={() => router.push('/accounting/gst/returns/gstr3b')}
                  >
                    Prepare GSTR-3B
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-orange-50 dark:bg-orange-950">
              <CardHeader>
                <CardTitle>Pending Returns</CardTitle>
                <CardDescription>Requires attention</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="text-3xl font-bold text-orange-600">
                    {summary.pending_returns}
                  </div>
                  <p className="text-sm text-muted-foreground">Returns to be filed</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Frequently used GST functions</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Button 
              variant="outline" 
              className="h-auto py-4 flex flex-col gap-2"
              onClick={() => router.push('/accounting/gst/transactions')}
            >
              <Receipt className="h-6 w-6" />
              <span>View Transactions</span>
            </Button>
            <Button 
              variant="outline" 
              className="h-auto py-4 flex flex-col gap-2"
              onClick={() => router.push('/accounting/gst/hsn-sac')}
            >
              <Database className="h-6 w-6" />
              <span>HSN/SAC Master</span>
            </Button>
            <Button 
              variant="outline" 
              className="h-auto py-4 flex flex-col gap-2"
              onClick={() => router.push('/accounting/gst/itc')}
            >
              <FileText className="h-6 w-6" />
              <span>Input Tax Credit</span>
            </Button>
            <Button 
              variant="outline" 
              className="h-auto py-4 flex flex-col gap-2"
              onClick={() => router.push('/accounting/gst/configuration')}
            >
              <Settings className="h-6 w-6" />
              <span>Configuration</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
