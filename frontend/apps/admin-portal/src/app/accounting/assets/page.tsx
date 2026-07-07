"use client";

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { assetService } from '@/services/accounting.service';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Plus, Package, TrendingDown, Wrench, ArrowRightLeft } from 'lucide-react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function AssetsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [dashboard, setDashboard] = useState<any>(null);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      // TODO: Implement getDashboard endpoint in backend
      // const response = await assetService.getDashboard();
      // setDashboard(response.data);
      setDashboard(null);
    } catch (error) {
      console.error('Failed to load dashboard', error);
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

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6'];

  if (loading) {
    return <div className="container mx-auto py-6">Loading...</div>;
  }

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Asset Management</h1>
          <p className="text-muted-foreground">Track and manage fixed assets with depreciation</p>
        </div>
        <Button onClick={() => router.push('/accounting/assets/new')}>
          <Plus className="mr-2 h-4 w-4" />
          Add Asset
        </Button>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Assets
            </CardTitle>
            <Package className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboard?.total_assets || 0}</div>
            <p className="text-xs text-muted-foreground">Active and inactive</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Purchase Value
            </CardTitle>
            <Package className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(dashboard?.total_value || 0)}</div>
            <p className="text-xs text-muted-foreground">Original cost</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Current Value (WDV)
            </CardTitle>
            <TrendingDown className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(dashboard?.total_wdv || 0)}</div>
            <p className="text-xs text-muted-foreground">Written down value</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Depreciation
            </CardTitle>
            <TrendingDown className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(dashboard?.total_depreciation || 0)}</div>
            <p className="text-xs text-muted-foreground">Accumulated</p>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Assets by Category</CardTitle>
            <CardDescription>Distribution of assets across categories</CardDescription>
          </CardHeader>
          <CardContent>
            {dashboard?.category_breakdown && dashboard.category_breakdown.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={dashboard.category_breakdown}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ category, count }) => `${category}: ${count}`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="count"
                  >
                    {dashboard.category_breakdown.map((entry: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                No assets to display
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Asset Value by Category</CardTitle>
            <CardDescription>Current value (WDV) distribution</CardDescription>
          </CardHeader>
          <CardContent>
            {dashboard?.category_breakdown && dashboard.category_breakdown.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={dashboard.category_breakdown}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="category" angle={-45} textAnchor="end" height={100} />
                  <YAxis />
                  <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                  <Legend />
                  <Bar dataKey="value" fill="#3b82f6" name="Value (₹)" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                No assets to display
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Status Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle>Asset Status</CardTitle>
          <CardDescription>Current status of all assets</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {dashboard?.status_breakdown && Object.entries(dashboard.status_breakdown).map(([status, count]) => (
              <div key={status} className="p-4 border rounded-lg">
                <p className="text-sm text-muted-foreground">{status}</p>
                <p className="text-2xl font-bold">{count as number}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Common asset management tasks</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Button 
              variant="outline" 
              className="h-auto py-4 flex flex-col gap-2"
              onClick={() => router.push('/accounting/assets/list')}
            >
              <Package className="h-6 w-6" />
              <span>View All Assets</span>
            </Button>
            <Button 
              variant="outline" 
              className="h-auto py-4 flex flex-col gap-2"
              onClick={() => router.push('/accounting/assets/depreciation')}
            >
              <TrendingDown className="h-6 w-6" />
              <span>Depreciation</span>
            </Button>
            <Button 
              variant="outline" 
              className="h-auto py-4 flex flex-col gap-2"
              onClick={() => router.push('/accounting/assets/new')}
            >
              <Plus className="h-6 w-6" />
              <span>Add New Asset</span>
            </Button>
            <Button 
              variant="outline" 
              className="h-auto py-4 flex flex-col gap-2"
              onClick={() => router.push('/accounting/assets/list')}
            >
              <ArrowRightLeft className="h-6 w-6" />
              <span>Transfer Assets</span>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Information Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Depreciation Methods</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div>
              <strong>Straight Line Method (SLM):</strong>
              <p className="text-muted-foreground">Equal depreciation every year</p>
              <p className="text-xs text-muted-foreground mt-1">
                Formula: (Cost - Salvage Value) / Useful Life
              </p>
            </div>
            <div className="mt-3">
              <strong>Written Down Value (WDV):</strong>
              <p className="text-muted-foreground">Depreciation on reducing balance</p>
              <p className="text-xs text-muted-foreground mt-1">
                Formula: WDV × Rate %
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Asset Lifecycle</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-muted-foreground">
            <div className="flex items-start gap-2">
              <span className="font-bold text-foreground">1.</span>
              <span>Purchase & Record - Add asset with purchase details</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="font-bold text-foreground">2.</span>
              <span>Depreciation - Calculate and post monthly/yearly</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="font-bold text-foreground">3.</span>
              <span>Transfer - Move between locations/departments</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="font-bold text-foreground">4.</span>
              <span>Maintenance - Track repairs and upkeep</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="font-bold text-foreground">5.</span>
              <span>Disposal - Sell or scrap at end of life</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
