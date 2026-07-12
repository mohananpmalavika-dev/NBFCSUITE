/**
 * Vendor List Page
 * Displays all vendors with search, filter, and CRUD operations
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
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
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Plus, Search, Filter, Star, Phone, Mail, MapPin } from 'lucide-react';
import { procurementService } from '@/services/procurement.service';
import type { Vendor, VendorStatus, VendorType } from '@/types/procurement';

export default function VendorsPage() {
  const router = useRouter();
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<VendorStatus | ''>('');
  const [typeFilter, setTypeFilter] = useState<VendorType | ''>('');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 20;

  // Fetch vendors
  useEffect(() => {
    fetchVendors();
  }, [page, statusFilter, typeFilter, search]);

  const fetchVendors = async () => {
    try {
      setLoading(true);
      const response = await procurementService.vendor.list({
        status: statusFilter || undefined,
        vendor_type: typeFilter || undefined,
        search: search || undefined,
        page,
        page_size: pageSize,
      });

      if (response.success && response.data) {
        setVendors(response.data.data);
        setTotal(response.data.total);
      }
    } catch (error) {
      console.error('Failed to fetch vendors:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: VendorStatus) => {
    const colors = {
      active: 'bg-green-100 text-green-800',
      inactive: 'bg-gray-100 text-gray-800',
      blacklisted: 'bg-red-100 text-red-800',
      suspended: 'bg-yellow-100 text-yellow-800',
      under_review: 'bg-blue-100 text-blue-800',
    };
    return (
      <Badge className={colors[status]}>
        {status.replace('_', ' ').toUpperCase()}
      </Badge>
    );
  };

  const formatRating = (rating: number) => {
    return (
      <div className="flex items-center gap-1">
        <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
        <span className="font-medium">{rating.toFixed(1)}</span>
      </div>
    );
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Vendors</h1>
          <p className="text-gray-500 mt-1">
            Manage your vendor master data
          </p>
        </div>
        <Button
          onClick={() => router.push('/procurement/vendors/new')}
          className="flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Add Vendor
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              Total Vendors
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{total}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              Active
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {vendors.filter((v) => v.status === 'active').length}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              Avg Rating
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold flex items-center gap-1">
              <Star className="w-5 h-5 fill-yellow-400 text-yellow-400" />
              {vendors.length > 0
                ? (
                    vendors.reduce((sum, v) => sum + v.overall_rating, 0) /
                    vendors.length
                  ).toFixed(1)
                : '0.0'}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              Total Orders
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {vendors.reduce((sum, v) => sum + v.total_orders, 0)}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
              <Input
                placeholder="Search vendors..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select
              value={statusFilter}
              onValueChange={(value) => setStatusFilter(value as VendorStatus | '')}
            >
              <SelectTrigger>
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Statuses</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="inactive">Inactive</SelectItem>
                <SelectItem value="suspended">Suspended</SelectItem>
                <SelectItem value="blacklisted">Blacklisted</SelectItem>
              </SelectContent>
            </Select>
            <Select
              value={typeFilter}
              onValueChange={(value) => setTypeFilter(value as VendorType | '')}
            >
              <SelectTrigger>
                <SelectValue placeholder="Filter by type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Types</SelectItem>
                <SelectItem value="supplier">Supplier</SelectItem>
                <SelectItem value="contractor">Contractor</SelectItem>
                <SelectItem value="manufacturer">Manufacturer</SelectItem>
                <SelectItem value="service_provider">Service Provider</SelectItem>
              </SelectContent>
            </Select>
            <Button
              variant="outline"
              onClick={fetchVendors}
              className="flex items-center gap-2"
            >
              <Filter className="w-4 h-4" />
              Apply Filters
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Vendors Table */}
      <Card>
        <CardContent className="pt-6">
          {loading ? (
            <div className="text-center py-8">Loading vendors...</div>
          ) : vendors.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No vendors found. Create your first vendor to get started.
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Vendor Code</TableHead>
                  <TableHead>Vendor Name</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Contact</TableHead>
                  <TableHead>Location</TableHead>
                  <TableHead>Rating</TableHead>
                  <TableHead>Orders</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {vendors.map((vendor) => (
                  <TableRow
                    key={vendor.id}
                    className="cursor-pointer hover:bg-gray-50"
                    onClick={() =>
                      router.push(`/procurement/vendors/${vendor.id}`)
                    }
                  >
                    <TableCell className="font-medium">
                      {vendor.vendor_code}
                    </TableCell>
                    <TableCell>
                      <div>
                        <div className="font-medium">{vendor.vendor_name}</div>
                        {vendor.gst_number && (
                          <div className="text-sm text-gray-500">
                            GST: {vendor.gst_number}
                          </div>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">
                        {vendor.vendor_type.replace('_', ' ')}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="space-y-1 text-sm">
                        {vendor.phone && (
                          <div className="flex items-center gap-1">
                            <Phone className="w-3 h-3" />
                            {vendor.phone}
                          </div>
                        )}
                        {vendor.email && (
                          <div className="flex items-center gap-1">
                            <Mail className="w-3 h-3" />
                            {vendor.email}
                          </div>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      {vendor.city && (
                        <div className="flex items-center gap-1 text-sm">
                          <MapPin className="w-3 h-3" />
                          {vendor.city}, {vendor.state}
                        </div>
                      )}
                    </TableCell>
                    <TableCell>{formatRating(vendor.overall_rating)}</TableCell>
                    <TableCell>
                      <div className="text-center">
                        <div className="font-medium">{vendor.total_orders}</div>
                        <div className="text-xs text-gray-500">
                          {vendor.on_time_deliveries} on-time
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>{getStatusBadge(vendor.status)}</TableCell>
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          router.push(`/procurement/vendors/${vendor.id}`);
                        }}
                      >
                        View
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}

          {/* Pagination */}
          {total > pageSize && (
            <div className="flex justify-between items-center mt-4 pt-4 border-t">
              <div className="text-sm text-gray-500">
                Showing {(page - 1) * pageSize + 1} to{' '}
                {Math.min(page * pageSize, total)} of {total} vendors
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(page - 1)}
                  disabled={page === 1}
                >
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(page + 1)}
                  disabled={page * pageSize >= total}
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
