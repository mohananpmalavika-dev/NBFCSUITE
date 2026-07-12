/**
 * GRN List Page
 * Displays all Goods Receipt Notes with filtering
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Package,
  Plus,
  Search,
  Calendar,
  FileText,
  TrendingUp,
  CheckCircle,
  XCircle,
  Clock,
} from 'lucide-react';
import { procurementService } from '@/services/procurement.service';
import type { GoodsReceiptNote } from '@/types/procurement';

export default function GRNListPage() {
  const router = useRouter();
  const [grns, setGrns] = useState<GoodsReceiptNote[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [stats, setStats] = useState({
    total: 0,
    pending: 0,
    quality_check: 0,
    accepted: 0,
    rejected: 0,
  });

  useEffect(() => {
    fetchGRNs();
    fetchStats();
  }, [statusFilter]);

  const fetchGRNs = async () => {
    try {
      setLoading(true);
      const params: any = {};
      if (statusFilter !== 'all') {
        params.status = statusFilter;
      }
      const response = await procurementService.grn.getAll(params);
      if (response.success && response.data) {
        setGrns(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch GRNs:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await procurementService.grn.getStats();
      if (response.success && response.data) {
        setStats(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch GRN stats:', error);
    }
  };

  const formatDate = (date: string | Date) => {
    return new Date(date).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const getStatusBadgeClass = (status: string) => {
    const statusClasses = {
      pending: 'bg-yellow-100 text-yellow-800',
      quality_check: 'bg-blue-100 text-blue-800',
      partially_accepted: 'bg-orange-100 text-orange-800',
      accepted: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
    };
    return statusClasses[status as keyof typeof statusClasses] || 'bg-gray-100 text-gray-800';
  };

  const filteredGRNs = grns.filter((grn) => {
    const matchesSearch =
      searchTerm === '' ||
      grn.grn_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      grn.challan_number?.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  });

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">Goods Receipt Notes</h1>
          <p className="text-gray-600">Manage goods receipts and quality checks</p>
        </div>
        <Button onClick={() => router.push('/procurement/grn/new')}>
          <Plus className="w-4 h-4 mr-2" />
          Create GRN
        </Button>
      </div>

      {/* Breadcrumb */}
      <nav className="flex mb-6 text-sm text-gray-600">
        <Link href="/procurement/dashboard" className="hover:text-blue-600">
          Procurement
        </Link>
        <span className="mx-2">/</span>
        <span className="text-gray-900">GRNs</span>
      </nav>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 mb-2">
              <Package className="w-4 h-4 text-gray-500" />
              <span className="text-sm text-gray-600">Total GRNs</span>
            </div>
            <div className="text-2xl font-bold">{stats.total}</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 mb-2">
              <Clock className="w-4 h-4 text-yellow-500" />
              <span className="text-sm text-gray-600">Pending</span>
            </div>
            <div className="text-2xl font-bold text-yellow-600">{stats.pending}</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 mb-2">
              <Search className="w-4 h-4 text-blue-500" />
              <span className="text-sm text-gray-600">Quality Check</span>
            </div>
            <div className="text-2xl font-bold text-blue-600">{stats.quality_check}</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle className="w-4 h-4 text-green-500" />
              <span className="text-sm text-gray-600">Accepted</span>
            </div>
            <div className="text-2xl font-bold text-green-600">{stats.accepted}</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 mb-2">
              <XCircle className="w-4 h-4 text-red-500" />
              <span className="text-sm text-gray-600">Rejected</span>
            </div>
            <div className="text-2xl font-bold text-red-600">{stats.rejected}</div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card className="mb-6">
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input
                placeholder="Search by GRN number or challan number..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full md:w-48">
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="quality_check">Quality Check</SelectItem>
                <SelectItem value="partially_accepted">Partially Accepted</SelectItem>
                <SelectItem value="accepted">Accepted</SelectItem>
                <SelectItem value="rejected">Rejected</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* GRN Table */}
      <Card>
        <CardHeader>
          <CardTitle>All Goods Receipt Notes ({filteredGRNs.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-12">
              <div className="text-lg text-gray-500">Loading GRNs...</div>
            </div>
          ) : filteredGRNs.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <Package className="w-12 h-12 mx-auto mb-4 text-gray-400" />
              <p className="text-lg mb-2">No goods receipt notes found</p>
              <p className="text-sm">
                {searchTerm || statusFilter !== 'all'
                  ? 'Try adjusting your filters'
                  : 'Create your first GRN to get started'}
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>GRN Number</TableHead>
                    <TableHead>GRN Date</TableHead>
                    <TableHead>PO Number</TableHead>
                    <TableHead>Challan Number</TableHead>
                    <TableHead>Receipt Date</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Quality Check</TableHead>
                    <TableHead>Items</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredGRNs.map((grn) => (
                    <TableRow
                      key={grn.id}
                      className="cursor-pointer hover:bg-gray-50"
                      onClick={() => router.push(`/procurement/grn/${grn.id}`)}
                    >
                      <TableCell className="font-medium">{grn.grn_number}</TableCell>
                      <TableCell>{formatDate(grn.grn_date)}</TableCell>
                      <TableCell>
                        <Link
                          href={`/procurement/purchase-orders/${grn.po_id}`}
                          className="text-blue-600 hover:underline"
                          onClick={(e) => e.stopPropagation()}
                        >
                          View PO
                        </Link>
                      </TableCell>
                      <TableCell>{grn.challan_number || '-'}</TableCell>
                      <TableCell>{formatDate(grn.receipt_date)}</TableCell>
                      <TableCell>
                        <span
                          className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getStatusBadgeClass(
                            grn.status
                          )}`}
                        >
                          {grn.status.replace(/_/g, ' ').toUpperCase()}
                        </span>
                      </TableCell>
                      <TableCell>
                        {grn.quality_check_required ? (
                          grn.quality_checked_at ? (
                            <span className="text-green-600 text-sm">
                              ✓ {formatDate(grn.quality_checked_at)}
                            </span>
                          ) : (
                            <span className="text-yellow-600 text-sm">Pending</span>
                          )
                        ) : (
                          <span className="text-gray-400 text-sm">Not Required</span>
                        )}
                      </TableCell>
                      <TableCell>{grn.items?.length || 0}</TableCell>
                      <TableCell className="text-right">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            router.push(`/procurement/grn/${grn.id}`);
                          }}
                        >
                          View Details
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
