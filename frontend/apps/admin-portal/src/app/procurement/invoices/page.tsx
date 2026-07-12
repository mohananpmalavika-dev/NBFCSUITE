/**
 * Invoice List Page
 * Displays all Vendor Invoices with filtering
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
  FileText,
  Plus,
  Search,
  Calendar,
  TrendingUp,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  DollarSign,
} from 'lucide-react';
import { procurementService } from '@/services/procurement.service';
import type { VendorInvoice } from '@/types/procurement';

export default function InvoiceListPage() {
  const router = useRouter();
  const [invoices, setInvoices] = useState<VendorInvoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [matchingFilter, setMatchingFilter] = useState<string>('all');
  const [stats, setStats] = useState({
    total: 0,
    pending: 0,
    approved: 0,
    rejected: 0,
    paid: 0,
    total_amount: 0,
    pending_amount: 0,
  });

  useEffect(() => {
    fetchInvoices();
    fetchStats();
  }, [statusFilter, matchingFilter]);

  const fetchInvoices = async () => {
    try {
      setLoading(true);
      const params: any = {};
      if (statusFilter !== 'all') {
        params.status = statusFilter;
      }
      if (matchingFilter !== 'all') {
        params.matching_status = matchingFilter;
      }
      const response = await procurementService.invoice.getAll(params);
      if (response.success && response.data) {
        setInvoices(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch invoices:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await procurementService.invoice.getStats();
      if (response.success && response.data) {
        setStats(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch invoice stats:', error);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2,
    }).format(amount);
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
      draft: 'bg-gray-100 text-gray-800',
      pending: 'bg-yellow-100 text-yellow-800',
      verified: 'bg-blue-100 text-blue-800',
      approved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
      partially_paid: 'bg-orange-100 text-orange-800',
      paid: 'bg-green-100 text-green-800',
    };
    return statusClasses[status as keyof typeof statusClasses] || 'bg-gray-100 text-gray-800';
  };

  const getMatchingBadgeClass = (status: string) => {
    const statusClasses = {
      not_matched: 'bg-gray-100 text-gray-800',
      matched: 'bg-green-100 text-green-800',
      variance: 'bg-yellow-100 text-yellow-800',
      mismatch: 'bg-red-100 text-red-800',
    };
    return statusClasses[status as keyof typeof statusClasses] || 'bg-gray-100 text-gray-800';
  };

  const filteredInvoices = invoices.filter((invoice) => {
    const matchesSearch =
      searchTerm === '' ||
      invoice.invoice_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      invoice.vendor_invoice_number.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  });

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">Vendor Invoices</h1>
          <p className="text-gray-600">Manage vendor invoices and payments</p>
        </div>
        <Button onClick={() => router.push('/procurement/invoices/new')}>
          <Plus className="w-4 h-4 mr-2" />
          Create Invoice
        </Button>
      </div>

      {/* Breadcrumb */}
      <nav className="flex mb-6 text-sm text-gray-600">
        <Link href="/procurement/dashboard" className="hover:text-blue-600">
          Procurement
        </Link>
        <span className="mx-2">/</span>
        <span className="text-gray-900">Invoices</span>
      </nav>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 mb-2">
              <FileText className="w-4 h-4 text-gray-500" />
              <span className="text-sm text-gray-600">Total Invoices</span>
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
              <CheckCircle className="w-4 h-4 text-green-500" />
              <span className="text-sm text-gray-600">Approved</span>
            </div>
            <div className="text-2xl font-bold text-green-600">{stats.approved}</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 mb-2">
              <DollarSign className="w-4 h-4 text-blue-500" />
              <span className="text-sm text-gray-600">Pending Amount</span>
            </div>
            <div className="text-2xl font-bold text-blue-600">
              {formatCurrency(stats.pending_amount)}
            </div>
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
                placeholder="Search by invoice number or vendor invoice number..."
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
                <SelectItem value="draft">Draft</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="verified">Verified</SelectItem>
                <SelectItem value="approved">Approved</SelectItem>
                <SelectItem value="rejected">Rejected</SelectItem>
                <SelectItem value="partially_paid">Partially Paid</SelectItem>
                <SelectItem value="paid">Paid</SelectItem>
              </SelectContent>
            </Select>
            <Select value={matchingFilter} onValueChange={setMatchingFilter}>
              <SelectTrigger className="w-full md:w-48">
                <SelectValue placeholder="Filter by matching" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Matching</SelectItem>
                <SelectItem value="matched">Matched</SelectItem>
                <SelectItem value="variance">Variance</SelectItem>
                <SelectItem value="mismatch">Mismatch</SelectItem>
                <SelectItem value="not_matched">Not Matched</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Invoice Table */}
      <Card>
        <CardHeader>
          <CardTitle>All Vendor Invoices ({filteredInvoices.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-12">
              <div className="text-lg text-gray-500">Loading invoices...</div>
            </div>
          ) : filteredInvoices.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <FileText className="w-12 h-12 mx-auto mb-4 text-gray-400" />
              <p className="text-lg mb-2">No vendor invoices found</p>
              <p className="text-sm">
                {searchTerm || statusFilter !== 'all' || matchingFilter !== 'all'
                  ? 'Try adjusting your filters'
                  : 'Create your first invoice to get started'}
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Invoice Number</TableHead>
                    <TableHead>Vendor Invoice</TableHead>
                    <TableHead>Invoice Date</TableHead>
                    <TableHead>Due Date</TableHead>
                    <TableHead>PO Number</TableHead>
                    <TableHead className="text-right">Total Amount</TableHead>
                    <TableHead className="text-right">Paid Amount</TableHead>
                    <TableHead className="text-right">Balance</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Matching</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredInvoices.map((invoice) => (
                    <TableRow
                      key={invoice.id}
                      className="cursor-pointer hover:bg-gray-50"
                      onClick={() => router.push(`/procurement/invoices/${invoice.id}`)}
                    >
                      <TableCell className="font-medium">{invoice.invoice_number}</TableCell>
                      <TableCell>{invoice.vendor_invoice_number}</TableCell>
                      <TableCell>{formatDate(invoice.invoice_date)}</TableCell>
                      <TableCell>
                        <span
                          className={
                            new Date(invoice.due_date) < new Date() &&
                            invoice.balance_amount > 0
                              ? 'text-red-600 font-medium'
                              : ''
                          }
                        >
                          {formatDate(invoice.due_date)}
                        </span>
                      </TableCell>
                      <TableCell>
                        <Link
                          href={`/procurement/purchase-orders/${invoice.po_id}`}
                          className="text-blue-600 hover:underline"
                          onClick={(e) => e.stopPropagation()}
                        >
                          View PO
                        </Link>
                      </TableCell>
                      <TableCell className="text-right font-medium">
                        {formatCurrency(invoice.total_amount)}
                      </TableCell>
                      <TableCell className="text-right text-green-600">
                        {formatCurrency(invoice.paid_amount)}
                      </TableCell>
                      <TableCell className="text-right font-medium">
                        {invoice.balance_amount > 0 ? (
                          <span className="text-orange-600">
                            {formatCurrency(invoice.balance_amount)}
                          </span>
                        ) : (
                          <span className="text-gray-400">-</span>
                        )}
                      </TableCell>
                      <TableCell>
                        <span
                          className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getStatusBadgeClass(
                            invoice.status
                          )}`}
                        >
                          {invoice.status.replace(/_/g, ' ').toUpperCase()}
                        </span>
                      </TableCell>
                      <TableCell>
                        <span
                          className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getMatchingBadgeClass(
                            invoice.matching_status
                          )}`}
                        >
                          {invoice.matching_status.replace(/_/g, ' ').toUpperCase()}
                        </span>
                      </TableCell>
                      <TableCell className="text-right">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            router.push(`/procurement/invoices/${invoice.id}`);
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
