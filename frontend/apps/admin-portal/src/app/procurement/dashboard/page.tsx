/**
 * Procurement Dashboard
 * Overview of procurement activities with KPIs and metrics
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Users,
  FileText,
  ShoppingCart,
  Package,
  TrendingUp,
  TrendingDown,
  Clock,
  CheckCircle,
  AlertCircle,
  DollarSign,
  Calendar,
  Star,
  ArrowRight,
} from 'lucide-react';
import { procurementService } from '@/services/procurement.service';

interface DashboardStats {
  vendors: {
    total: number;
    active: number;
    top_rated: number;
  };
  requisitions: {
    total: number;
    pending_approval: number;
    approved: number;
  };
  purchase_orders: {
    total: number;
    open: number;
    value: number;
  };
  pending_actions: {
    requisitions_to_approve: number;
    pos_to_approve: number;
    invoices_to_approve: number;
    grns_pending: number;
  };
}

export default function ProcurementDashboard() {
  const router = useRouter();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await procurementService.dashboard.getStats();
      if (response.success && response.data) {
        setStats(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      notation: 'compact',
      maximumFractionDigits: 2,
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Procurement Dashboard</h1>
        <p className="text-gray-600 mt-1">
          Overview of procurement activities and key metrics
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Vendors */}
        <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => router.push('/procurement/vendors')}>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              Total Vendors
            </CardTitle>
            <Users className="w-5 h-5 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{stats?.vendors.total || 0}</div>
            <div className="flex items-center gap-2 mt-2">
              <Badge className="bg-green-100 text-green-800">
                {stats?.vendors.active || 0} Active
              </Badge>
              <Badge className="bg-yellow-100 text-yellow-800 flex items-center gap-1">
                <Star className="w-3 h-3" />
                {stats?.vendors.top_rated || 0} Top
              </Badge>
            </div>
          </CardContent>
        </Card>

        {/* Requisitions */}
        <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => router.push('/procurement/requisitions')}>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              Requisitions
            </CardTitle>
            <FileText className="w-5 h-5 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{stats?.requisitions.total || 0}</div>
            <div className="flex items-center gap-2 mt-2">
              <Badge className="bg-blue-100 text-blue-800 flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {stats?.requisitions.pending_approval || 0} Pending
              </Badge>
              <Badge className="bg-green-100 text-green-800">
                {stats?.requisitions.approved || 0} Approved
              </Badge>
            </div>
          </CardContent>
        </Card>

        {/* Purchase Orders */}
        <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => router.push('/procurement/purchase-orders')}>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              Purchase Orders
            </CardTitle>
            <ShoppingCart className="w-5 h-5 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{stats?.purchase_orders.total || 0}</div>
            <div className="flex items-center gap-2 mt-2">
              <Badge className="bg-blue-100 text-blue-800">
                {stats?.purchase_orders.open || 0} Open
              </Badge>
            </div>
          </CardContent>
        </Card>

        {/* PO Value */}
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              Total PO Value
            </CardTitle>
            <DollarSign className="w-5 h-5 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {formatCurrency(stats?.purchase_orders.value || 0)}
            </div>
            <div className="flex items-center gap-1 mt-2 text-sm text-green-600">
              <TrendingUp className="w-4 h-4" />
              <span>This month</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Pending Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-orange-500" />
            Pending Actions
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div 
              className="p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors cursor-pointer"
              onClick={() => router.push('/procurement/requisitions?status=submitted')}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">
                  Requisitions to Approve
                </span>
                <FileText className="w-5 h-5 text-blue-600" />
              </div>
              <div className="text-2xl font-bold text-blue-600">
                {stats?.pending_actions.requisitions_to_approve || 0}
              </div>
            </div>

            <div 
              className="p-4 bg-green-50 rounded-lg hover:bg-green-100 transition-colors cursor-pointer"
              onClick={() => router.push('/procurement/purchase-orders?status=draft')}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">
                  POs to Approve
                </span>
                <ShoppingCart className="w-5 h-5 text-green-600" />
              </div>
              <div className="text-2xl font-bold text-green-600">
                {stats?.pending_actions.pos_to_approve || 0}
              </div>
            </div>

            <div className="p-4 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors cursor-pointer">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">
                  Invoices to Approve
                </span>
                <FileText className="w-5 h-5 text-purple-600" />
              </div>
              <div className="text-2xl font-bold text-purple-600">
                {stats?.pending_actions.invoices_to_approve || 0}
              </div>
            </div>

            <div className="p-4 bg-yellow-50 rounded-lg hover:bg-yellow-100 transition-colors cursor-pointer">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">
                  Pending GRNs
                </span>
                <Package className="w-5 h-5 text-yellow-600" />
              </div>
              <div className="text-2xl font-bold text-yellow-600">
                {stats?.pending_actions.grns_pending || 0}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Recent Activities & Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activities */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="w-5 h-5" />
              Recent Activities
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm font-medium">PO-2024-0123 Approved</p>
                  <p className="text-xs text-gray-600 mt-1">
                    Purchase order for office supplies approved
                  </p>
                  <p className="text-xs text-gray-500 mt-1">2 hours ago</p>
                </div>
              </div>

              <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                <FileText className="w-5 h-5 text-blue-600 mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm font-medium">New Requisition Submitted</p>
                  <p className="text-xs text-gray-600 mt-1">
                    PR-202401-0045 waiting for approval
                  </p>
                  <p className="text-xs text-gray-500 mt-1">4 hours ago</p>
                </div>
              </div>

              <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                <Package className="w-5 h-5 text-yellow-600 mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm font-medium">GRN Created</p>
                  <p className="text-xs text-gray-600 mt-1">
                    Goods received for PO-2024-0120
                  </p>
                  <p className="text-xs text-gray-500 mt-1">Yesterday</p>
                </div>
              </div>

              <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                <Users className="w-5 h-5 text-purple-600 mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm font-medium">New Vendor Added</p>
                  <p className="text-xs text-gray-600 mt-1">
                    ABC Supplies registered as new vendor
                  </p>
                  <p className="text-xs text-gray-500 mt-1">2 days ago</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 gap-3">
              <Button
                variant="outline"
                className="justify-start h-auto py-4"
                onClick={() => router.push('/procurement/requisitions/new')}
              >
                <div className="flex items-center gap-3 w-full">
                  <FileText className="w-5 h-5 text-blue-600" />
                  <div className="flex-1 text-left">
                    <div className="font-medium">Create Requisition</div>
                    <div className="text-xs text-gray-500">
                      Request for new purchase
                    </div>
                  </div>
                  <ArrowRight className="w-4 h-4 text-gray-400" />
                </div>
              </Button>

              <Button
                variant="outline"
                className="justify-start h-auto py-4"
                onClick={() => router.push('/procurement/vendors/new')}
              >
                <div className="flex items-center gap-3 w-full">
                  <Users className="w-5 h-5 text-purple-600" />
                  <div className="flex-1 text-left">
                    <div className="font-medium">Add Vendor</div>
                    <div className="text-xs text-gray-500">
                      Register new vendor
                    </div>
                  </div>
                  <ArrowRight className="w-4 h-4 text-gray-400" />
                </div>
              </Button>

              <Button
                variant="outline"
                className="justify-start h-auto py-4"
                onClick={() => router.push('/procurement/purchase-orders/new')}
              >
                <div className="flex items-center gap-3 w-full">
                  <ShoppingCart className="w-5 h-5 text-green-600" />
                  <div className="flex-1 text-left">
                    <div className="font-medium">Create Purchase Order</div>
                    <div className="text-xs text-gray-500">
                      Generate new PO
                    </div>
                  </div>
                  <ArrowRight className="w-4 h-4 text-gray-400" />
                </div>
              </Button>

              <Button
                variant="outline"
                className="justify-start h-auto py-4"
                onClick={() => router.push('/procurement/rfq/new')}
              >
                <div className="flex items-center gap-3 w-full">
                  <FileText className="w-5 h-5 text-orange-600" />
                  <div className="flex-1 text-left">
                    <div className="font-medium">Create RFQ</div>
                    <div className="text-xs text-gray-500">
                      Request vendor quotes
                    </div>
                  </div>
                  <ArrowRight className="w-4 h-4 text-gray-400" />
                </div>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Top Vendors */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Star className="w-5 h-5 text-yellow-500" />
              Top Performing Vendors
            </CardTitle>
            <Button 
              variant="ghost" 
              size="sm"
              onClick={() => router.push('/procurement/vendors')}
            >
              View All
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Vendor</TableHead>
                <TableHead className="text-center">Orders</TableHead>
                <TableHead className="text-center">On-Time %</TableHead>
                <TableHead className="text-center">Rating</TableHead>
                <TableHead className="text-right">Total Value</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell>
                  <div className="font-medium">ABC Suppliers Ltd.</div>
                  <div className="text-sm text-gray-500">VEN001</div>
                </TableCell>
                <TableCell className="text-center">45</TableCell>
                <TableCell className="text-center">
                  <Badge className="bg-green-100 text-green-800">98%</Badge>
                </TableCell>
                <TableCell className="text-center">
                  <div className="flex items-center justify-center gap-1">
                    <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                    <span className="font-medium">4.8</span>
                  </div>
                </TableCell>
                <TableCell className="text-right font-medium">
                  ₹12.5L
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell>
                  <div className="font-medium">XYZ Enterprises</div>
                  <div className="text-sm text-gray-500">VEN005</div>
                </TableCell>
                <TableCell className="text-center">38</TableCell>
                <TableCell className="text-center">
                  <Badge className="bg-green-100 text-green-800">95%</Badge>
                </TableCell>
                <TableCell className="text-center">
                  <div className="flex items-center justify-center gap-1">
                    <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                    <span className="font-medium">4.6</span>
                  </div>
                </TableCell>
                <TableCell className="text-right font-medium">
                  ₹9.8L
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell>
                  <div className="font-medium">Tech Solutions Inc.</div>
                  <div className="text-sm text-gray-500">VEN012</div>
                </TableCell>
                <TableCell className="text-center">32</TableCell>
                <TableCell className="text-center">
                  <Badge className="bg-green-100 text-green-800">92%</Badge>
                </TableCell>
                <TableCell className="text-center">
                  <div className="flex items-center justify-center gap-1">
                    <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                    <span className="font-medium">4.5</span>
                  </div>
                </TableCell>
                <TableCell className="text-right font-medium">
                  ₹8.2L
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
