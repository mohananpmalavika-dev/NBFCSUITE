/**
 * Purchase Orders List Page
 * Displays all purchase orders with filters and search
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Plus,
  Search,
  FileText,
  Clock,
  CheckCircle,
  Send,
  Truck,
  XCircle,
  Filter,
  Eye,
} from 'lucide-react';
import { procurementService } from '@/services/procurement.service';
import type { PurchaseOrder, POStatus } from '@/types/procurement';

export default function PurchaseOrdersListPage() {
  const router = useRouter();
  const [orders, setOrders] = useState<PurchaseOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<POStatus | 'all'>('all');
  const [stats, setStats] = useState({
    total: 0,
    draft: 0,
    approved: 0,
    sent: 0,
    acknowledged: 0,
    partially_received: 0,
    fully_received: 0,
    cancelled: 0,
  });

  useEffect(() => {
    fetchOrders();
  }, [statusFilter]);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const response = await procurementService.purchaseOrder.getAll(
        statusFilter !== 'all' ? { status: statusFilter } : {}
      );
      if (response.success && response.data) {
        setOrders(response.data);
        calculateStats(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch purchase orders:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = (data: PurchaseOrder[]) => {
    setStats({
      total: data.length,
      draft: data.filter((o) => o.status === 'draft').length,
      approved: data.filter((o) => o.status === 'approved').length,
      sent: data.filter((o) => o.status === 'sent').length,
      acknowledged: data.filter((o) => o.status === 'acknowledged').length,
      partially_received: data.filter((o) => o.status === 'partially_received').length,
      fully_received: data.filter((o) => o.status === 'fully_received').length,
      cancelled: data.filter((o) => o.status === 'cancelled').length,
    });
  };

  const filteredOrders = orders.filter((order) => {
    const matchesSearch =
      searchTerm === '' ||
      order.po_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      order.vendor_name?.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  });

  const getStatusBadge = (status: POStatus) => {
    const configs = {
      draft: { color: 'bg-gray-100 text-gray-800', icon: FileText },
      approved: { color: 'bg-green-100 text-green-800', icon: CheckCircle },
      sent: { color: 'bg-blue-100 text-blue-800', icon: Send },
      acknowledged: { color: 'bg-purple-100 text-purple-800', icon: CheckCircle },
      partially_received: { color: 'bg-yellow-100 text-yellow-800', icon: Truck },
      fully_received: { color: 'bg-green-100 text-green-800', icon: CheckCircle },
      cancelled: { color: 'bg-red-100 text-red-800', icon: XCircle },
    };
    const config = configs[status];
    const Icon = config.icon;
    return (
      <Badge className={`${config.color} flex items-center gap-1`}>
        <Icon className="w-3 h-3" />
        {status.replace(/_/g, ' ').toUpperCase()}
      </Badge>
    );
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2,
    }).format(amount);
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Purchase Orders</h1>
          <p className="text-gray-600 mt-1">Manage purchase orders and deliveries</p>
        </div>
        <Button
          onClick={() => router.push('/procurement/purchase-orders/new')}
          className="flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          New Purchase Order
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-medium text-gray-500">Total</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-medium text-gray-500">Draft</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-600">{stats.draft}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-medium text-gray-500">Approved</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats.approved}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-medium text-gray-500">Sent</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{stats.sent}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-medium text-gray-500">
              Acknowledged
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">
              {stats.acknowledged}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-medium text-gray-500">
              Partial GRN
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">
              {stats.partially_received}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-medium text-gray-500">
              Full GRN
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {stats.fully_received}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-medium text-gray-500">
              Cancelled
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{stats.cancelled}</div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input
                placeholder="Search by PO number or vendor name..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <div className="flex gap-2">
              <Select
                value={statusFilter}
                onValueChange={(value) => setStatusFilter(value as POStatus | 'all')}
              >
                <SelectTrigger className="w-[200px]">
                  <Filter className="w-4 h-4 mr-2" />
                  <SelectValue placeholder="Filter by status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="draft">Draft</SelectItem>
                  <SelectItem value="approved">Approved</SelectItem>
                  <SelectItem value="sent">Sent</SelectItem>
                  <SelectItem value="acknowledged">Acknowledged</SelectItem>
                  <SelectItem value="partially_received">Partially Received</SelectItem>
                  <SelectItem value="fully_received">Fully Received</SelectItem>
                  <SelectItem value="cancelled">Cancelled</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Orders Table */}
      <Card>
        <CardHeader>
          <CardTitle>Purchase Orders List</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
              <p className="mt-4 text-gray-600">Loading purchase orders...</p>
            </div>
          ) : filteredOrders.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                No Purchase Orders Found
              </h3>
              <p className="text-gray-600 mb-4">
                {searchTerm || statusFilter !== 'all'
                  ? 'Try adjusting your filters'
                  : 'Create your first purchase order'}
              </p>
              {!searchTerm && statusFilter === 'all' && (
                <Button onClick={() => router.push('/procurement/purchase-orders/new')}>
                  <Plus className="w-4 h-4 mr-2" />
                  Create Purchase Order
                </Button>
              )}
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>PO Number</TableHead>
                    <TableHead>Vendor</TableHead>
                    <TableHead>PO Date</TableHead>
                    <TableHead>Delivery Date</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-center">Items</TableHead>
                    <TableHead className="text-right">Total Amount</TableHead>
                    <TableHead className="text-center">GRN Status</TableHead>
                    <TableHead className="text-center">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredOrders.map((order) => (
                    <TableRow
                      key={order.id}
                      className="cursor-pointer hover:bg-gray-50"
                      onClick={() =>
                        router.push(`/procurement/purchase-orders/${order.id}`)
                      }
                    >
                      <TableCell className="font-medium">{order.po_number}</TableCell>
                      <TableCell>
                        <div className="max-w-xs">
                          <div className="font-medium">{order.vendor_name}</div>
                          <div className="text-sm text-gray-500">
                            {order.vendor_code}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>{formatDate(order.po_date)}</TableCell>
                      <TableCell>{formatDate(order.expected_delivery_date)}</TableCell>
                      <TableCell>{getStatusBadge(order.status)}</TableCell>
                      <TableCell className="text-center">
                        <Badge variant="outline">{order.items?.length || 0}</Badge>
                      </TableCell>
                      <TableCell className="text-right font-medium">
                        {formatCurrency(order.total_amount)}
                      </TableCell>
                      <TableCell className="text-center">
                        {order.items && order.items.length > 0 && (
                          <Badge
                            variant={
                              order.items.every((i) => i.received_quantity >= i.quantity)
                                ? 'default'
                                : order.items.some((i) => i.received_quantity > 0)
                                ? 'secondary'
                                : 'outline'
                            }
                          >
                            {order.items.filter((i) => i.received_quantity >= i.quantity)
                              .length}{' '}
                            / {order.items.length}
                          </Badge>
                        )}
                      </TableCell>
                      <TableCell className="text-center">
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={(e) => {
                            e.stopPropagation();
                            router.push(`/procurement/purchase-orders/${order.id}`);
                          }}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
