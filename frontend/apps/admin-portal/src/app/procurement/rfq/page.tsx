/**
 * RFQ (Request for Quotation) List Page
 * Displays all RFQs with filters and search
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
  Send,
  CheckCircle,
  XCircle,
  Filter,
  Eye,
  Users,
} from 'lucide-react';
import { procurementService } from '@/services/procurement.service';
import type { RFQ, RFQStatus } from '@/types/procurement';

export default function RFQListPage() {
  const router = useRouter();
  const [rfqs, setRfqs] = useState<RFQ[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<RFQStatus | 'all'>('all');
  const [stats, setStats] = useState({
    total: 0,
    draft: 0,
    sent: 0,
    quoted: 0,
    closed: 0,
    cancelled: 0,
  });

  useEffect(() => {
    fetchRFQs();
  }, [statusFilter]);

  const fetchRFQs = async () => {
    try {
      setLoading(true);
      // API call would be made here
      // const response = await procurementService.rfq.getAll({ status: statusFilter !== 'all' ? statusFilter : undefined });
      // For now, setting empty array
      setRfqs([]);
      calculateStats([]);
    } catch (error) {
      console.error('Failed to fetch RFQs:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = (data: RFQ[]) => {
    setStats({
      total: data.length,
      draft: data.filter((r) => r.status === 'draft').length,
      sent: data.filter((r) => r.status === 'sent').length,
      quoted: data.filter((r) => r.status === 'quoted').length,
      closed: data.filter((r) => r.status === 'closed').length,
      cancelled: data.filter((r) => r.status === 'cancelled').length,
    });
  };

  const filteredRFQs = rfqs.filter((rfq) => {
    const matchesSearch =
      searchTerm === '' ||
      rfq.rfq_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      rfq.title?.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  });

  const getStatusBadge = (status: RFQStatus) => {
    const configs = {
      draft: { color: 'bg-gray-100 text-gray-800', icon: FileText },
      sent: { color: 'bg-blue-100 text-blue-800', icon: Send },
      quoted: { color: 'bg-yellow-100 text-yellow-800', icon: Clock },
      closed: { color: 'bg-green-100 text-green-800', icon: CheckCircle },
      cancelled: { color: 'bg-red-100 text-red-800', icon: XCircle },
    };
    const config = configs[status];
    const Icon = config.icon;
    return (
      <Badge className={`${config.color} flex items-center gap-1`}>
        <Icon className="w-3 h-3" />
        {status.toUpperCase()}
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
          <h1 className="text-3xl font-bold">Request for Quotation (RFQ)</h1>
          <p className="text-gray-600 mt-1">Manage RFQs and vendor quotations</p>
        </div>
        <Button
          onClick={() => router.push('/procurement/rfq/new')}
          className="flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          New RFQ
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
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
            <CardTitle className="text-xs font-medium text-gray-500">Sent</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{stats.sent}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-medium text-gray-500">Quoted</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{stats.quoted}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-medium text-gray-500">Closed</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats.closed}</div>
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
                placeholder="Search by RFQ number or title..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <div className="flex gap-2">
              <Select
                value={statusFilter}
                onValueChange={(value) => setStatusFilter(value as RFQStatus | 'all')}
              >
                <SelectTrigger className="w-[180px]">
                  <Filter className="w-4 h-4 mr-2" />
                  <SelectValue placeholder="Filter by status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="draft">Draft</SelectItem>
                  <SelectItem value="sent">Sent</SelectItem>
                  <SelectItem value="quoted">Quoted</SelectItem>
                  <SelectItem value="closed">Closed</SelectItem>
                  <SelectItem value="cancelled">Cancelled</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* RFQ Table */}
      <Card>
        <CardHeader>
          <CardTitle>RFQ List</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
              <p className="mt-4 text-gray-600">Loading RFQs...</p>
            </div>
          ) : filteredRFQs.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No RFQs Found</h3>
              <p className="text-gray-600 mb-4">
                {searchTerm || statusFilter !== 'all'
                  ? 'Try adjusting your filters'
                  : 'Create your first RFQ'}
              </p>
              {!searchTerm && statusFilter === 'all' && (
                <Button onClick={() => router.push('/procurement/rfq/new')}>
                  <Plus className="w-4 h-4 mr-2" />
                  Create RFQ
                </Button>
              )}
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>RFQ No.</TableHead>
                    <TableHead>Title</TableHead>
                    <TableHead>RFQ Date</TableHead>
                    <TableHead>Quote Deadline</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-center">Items</TableHead>
                    <TableHead className="text-center">Vendors</TableHead>
                    <TableHead className="text-center">Quotes</TableHead>
                    <TableHead className="text-right">Est. Amount</TableHead>
                    <TableHead className="text-center">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredRFQs.map((rfq) => (
                    <TableRow
                      key={rfq.id}
                      className="cursor-pointer hover:bg-gray-50"
                      onClick={() => router.push(`/procurement/rfq/${rfq.id}`)}
                    >
                      <TableCell className="font-medium">{rfq.rfq_number}</TableCell>
                      <TableCell>
                        <div className="max-w-xs">
                          <div className="font-medium truncate">{rfq.title}</div>
                          {rfq.description && (
                            <div className="text-sm text-gray-500 truncate">
                              {rfq.description}
                            </div>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>{formatDate(rfq.rfq_date)}</TableCell>
                      <TableCell>{formatDate(rfq.quote_deadline)}</TableCell>
                      <TableCell>{getStatusBadge(rfq.status)}</TableCell>
                      <TableCell className="text-center">
                        <Badge variant="outline">{rfq.items?.length || 0}</Badge>
                      </TableCell>
                      <TableCell className="text-center">
                        <Badge variant="outline" className="flex items-center gap-1 w-fit mx-auto">
                          <Users className="w-3 h-3" />
                          {rfq.vendors?.length || 0}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-center">
                        <Badge
                          variant={
                            (rfq.quotes_received || 0) > 0 ? 'default' : 'outline'
                          }
                        >
                          {rfq.quotes_received || 0}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right font-medium">
                        {formatCurrency(rfq.total_amount || 0)}
                      </TableCell>
                      <TableCell className="text-center">
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={(e) => {
                            e.stopPropagation();
                            router.push(`/procurement/rfq/${rfq.id}`);
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
