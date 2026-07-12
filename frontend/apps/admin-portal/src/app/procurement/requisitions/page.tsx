/**
 * Purchase Requisitions List Page
 * Displays all purchase requisitions with filters and search
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
  XCircle,
  Filter,
  Eye,
} from 'lucide-react';
import { procurementService } from '@/services/procurement.service';
import type { PurchaseRequisition, RequisitionStatus } from '@/types/procurement';

export default function RequisitionsListPage() {
  const router = useRouter();
  const [requisitions, setRequisitions] = useState<PurchaseRequisition[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<RequisitionStatus | 'all'>('all');
  const [stats, setStats] = useState({
    total: 0,
    draft: 0,
    submitted: 0,
    approved: 0,
    rejected: 0,
    partially_converted: 0,
    fully_converted: 0,
    cancelled: 0,
  });

  useEffect(() => {
    fetchRequisitions();
  }, [statusFilter]);

  const fetchRequisitions = async () => {
    try {
      setLoading(true);
      const params: any = {};
      if (statusFilter !== 'all') {
        params.status = statusFilter;
      }

      const response = await procurementService.requisition.getAll(params);
      if (response.success && response.data) {
        setRequisitions(response.data);
        calculateStats(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch requisitions:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = (data: PurchaseRequisition[]) => {
    setStats({
      total: data.length,
      draft: data.filter((r) => r.status === 'draft').length,
      submitted: data.filter((r) => r.status === 'submitted').length,
      approved: data.filter((r) => r.status === 'approved').length,
      rejected: data.filter((r) => r.status === 'rejected').length,
      partially_converted: data.filter((r) => r.status === 'partially_converted').length,
      fully_converted: data.filter((r) => r.status === 'fully_converted').length,
      cancelled: data.filter((r) => r.status === 'cancelled').length,
    });
  };

  const filteredRequisitions = requisitions.filter((requisition) => {
    const matchesSearch =
      searchTerm === '' ||
      requisition.requisition_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      requisition.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      requisition.requested_by?.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  });

  const getStatusBadge = (status: RequisitionStatus) => {
    const configs = {
      draft: { color: 'bg-gray-100 text-gray-800', icon: FileText },
      submitted: { color: 'bg-blue-100 text-blue-800', icon: Clock },
      approved: { color: 'bg-green-100 text-green-800', icon: CheckCircle },
      rejected: { color: 'bg-red-100 text-red-800', icon: XCircle },
      partially_converted: { color: 'bg-yellow-100 text-yellow-800', icon: Clock },
      fully_converted: { color: 'bg-purple-100 text-purple-800', icon: CheckCircle },
      cancelled: { color: 'bg-gray-100 text-gray-800', icon: XCircle },
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
          <h1 className="text-3xl font-bold">Purchase Requisitions</h1>
          <p className="text-gray-600 mt-1">Manage purchase requisition requests</p>
        </div>
        <Button
          onClick={() => router.push('/procurement/requisitions/new')}
          className="flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          New Requisition
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
            <CardTitle className="text-xs font-medium text-gray-500">
              Submitted
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{stats.submitted}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-medium text-gray-500">
              Approved
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats.approved}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-medium text-gray-500">
              Rejected
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{stats.rejected}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-medium text-gray-500">
              Partial PO
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">
              {stats.partially_converted}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-medium text-gray-500">
              Full PO
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">
              {stats.fully_converted}
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
            <div className="text-2xl font-bold text-gray-600">{stats.cancelled}</div>
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
                placeholder="Search by requisition number, title, or requester..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <div className="flex gap-2">
              <Select
                value={statusFilter}
                onValueChange={(value) => setStatusFilter(value as RequisitionStatus | 'all')}
              >
                <SelectTrigger className="w-[180px]">
                  <Filter className="w-4 h-4 mr-2" />
                  <SelectValue placeholder="Filter by status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="draft">Draft</SelectItem>
                  <SelectItem value="submitted">Submitted</SelectItem>
                  <SelectItem value="approved">Approved</SelectItem>
                  <SelectItem value="rejected">Rejected</SelectItem>
                  <SelectItem value="partially_converted">Partially Converted</SelectItem>
                  <SelectItem value="fully_converted">Fully Converted</SelectItem>
                  <SelectItem value="cancelled">Cancelled</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Requisitions Table */}
      <Card>
        <CardHeader>
          <CardTitle>Requisitions List</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
              <p className="mt-4 text-gray-600">Loading requisitions...</p>
            </div>
          ) : filteredRequisitions.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                No Requisitions Found
              </h3>
              <p className="text-gray-600 mb-4">
                {searchTerm || statusFilter !== 'all'
                  ? 'Try adjusting your filters'
                  : 'Create your first purchase requisition'}
              </p>
              {!searchTerm && statusFilter === 'all' && (
                <Button onClick={() => router.push('/procurement/requisitions/new')}>
                  <Plus className="w-4 h-4 mr-2" />
                  Create Requisition
                </Button>
              )}
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Requisition No.</TableHead>
                    <TableHead>Title</TableHead>
                    <TableHead>Requested By</TableHead>
                    <TableHead>Department</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead>Required By</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Total Amount</TableHead>
                    <TableHead className="text-center">Items</TableHead>
                    <TableHead className="text-center">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredRequisitions.map((requisition) => (
                    <TableRow
                      key={requisition.id}
                      className="cursor-pointer hover:bg-gray-50"
                      onClick={() =>
                        router.push(`/procurement/requisitions/${requisition.id}`)
                      }
                    >
                      <TableCell className="font-medium">
                        {requisition.requisition_number}
                      </TableCell>
                      <TableCell>
                        <div className="max-w-xs">
                          <div className="font-medium truncate">{requisition.title}</div>
                          {requisition.description && (
                            <div className="text-sm text-gray-500 truncate">
                              {requisition.description}
                            </div>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>{requisition.requested_by || '-'}</TableCell>
                      <TableCell>{requisition.department || '-'}</TableCell>
                      <TableCell>{formatDate(requisition.requisition_date)}</TableCell>
                      <TableCell>{formatDate(requisition.required_by_date)}</TableCell>
                      <TableCell>{getStatusBadge(requisition.status)}</TableCell>
                      <TableCell className="text-right font-medium">
                        {formatCurrency(requisition.total_amount)}
                      </TableCell>
                      <TableCell className="text-center">
                        <Badge variant="outline">{requisition.items?.length || 0}</Badge>
                      </TableCell>
                      <TableCell className="text-center">
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={(e) => {
                            e.stopPropagation();
                            router.push(`/procurement/requisitions/${requisition.id}`);
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
