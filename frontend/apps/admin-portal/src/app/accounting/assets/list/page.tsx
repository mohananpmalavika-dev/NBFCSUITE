"use client";

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { assetService, type FixedAsset, type AssetCategory, type AssetStatus } from '@/services/accounting.service';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from '@/components/ui/use-toast';
import { Plus, Search, Eye } from 'lucide-react';
import { format } from 'date-fns';

export default function AssetsListPage() {
  const router = useRouter();
  const [assets, setAssets] = useState<FixedAsset[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    search: '',
    category: 'all',
    status: 'all',
    location: ''
  });

  useEffect(() => {
    loadAssets();
  }, [filters.category, filters.status]);

  const loadAssets = async () => {
    try {
      setLoading(true);
      const params: any = {};
      if (filters.category !== 'all') params.category = filters.category;
      if (filters.status !== 'all') params.status = filters.status;
      if (filters.location) params.location = filters.location;

      const response = await assetService.getAssets(params);
      
      // Client-side search
      let filtered = response.data.items;
      if (filters.search) {
        filtered = response.data.items.filter((asset: FixedAsset) =>
          asset.asset_name.toLowerCase().includes(filters.search.toLowerCase()) ||
          asset.asset_code.toLowerCase().includes(filters.search.toLowerCase()) ||
          asset.location?.toLowerCase().includes(filters.search.toLowerCase())
        );
      }

      setAssets(filtered);
      setTotal(filtered.length);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load assets",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, any> = {
      'ACTIVE': 'success',
      'UNDER_MAINTENANCE': 'warning',
      'DISPOSED': 'secondary',
      'SOLD': 'secondary'
    };
    return <Badge variant={variants[status] || 'default'}>{status.replace('_', ' ')}</Badge>;
  };

  const getCategoryLabel = (category: string) => {
    return category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(value);
  };

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Fixed Assets</h1>
          <p className="text-muted-foreground">Complete list of all fixed assets</p>
        </div>
        <Button onClick={() => router.push('/accounting/assets/new')}>
          <Plus className="mr-2 h-4 w-4" />
          Add Asset
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="relative">
              <Search className="absolute left-2 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search assets..."
                value={filters.search}
                onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                className="pl-8"
              />
            </div>
            <Select
              value={filters.category}
              onValueChange={(value) => setFilters({ ...filters, category: value })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Category" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                <SelectItem value="LAND">Land</SelectItem>
                <SelectItem value="BUILDING">Building</SelectItem>
                <SelectItem value="PLANT_MACHINERY">Plant & Machinery</SelectItem>
                <SelectItem value="FURNITURE_FIXTURES">Furniture & Fixtures</SelectItem>
                <SelectItem value="OFFICE_EQUIPMENT">Office Equipment</SelectItem>
                <SelectItem value="COMPUTERS">Computers</SelectItem>
                <SelectItem value="VEHICLES">Vehicles</SelectItem>
                <SelectItem value="SOFTWARE">Software</SelectItem>
              </SelectContent>
            </Select>
            <Select
              value={filters.status}
              onValueChange={(value) => setFilters({ ...filters, status: value })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="ACTIVE">Active</SelectItem>
                <SelectItem value="UNDER_MAINTENANCE">Under Maintenance</SelectItem>
                <SelectItem value="DISPOSED">Disposed</SelectItem>
                <SelectItem value="SOLD">Sold</SelectItem>
              </SelectContent>
            </Select>
            <Input
              placeholder="Location"
              value={filters.location}
              onChange={(e) => setFilters({ ...filters, location: e.target.value })}
            />
            <Button variant="outline" onClick={loadAssets}>
              Refresh
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Assets Table */}
      <Card>
        <CardHeader>
          <CardTitle>Assets List</CardTitle>
          <CardDescription>{total} assets found</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Asset Code</TableHead>
                    <TableHead>Asset Name</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead>Purchase Date</TableHead>
                    <TableHead className="text-right">Cost (₹)</TableHead>
                    <TableHead className="text-right">WDV (₹)</TableHead>
                    <TableHead>Location</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {assets.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={9} className="text-center text-muted-foreground py-8">
                        No assets found. Click "Add Asset" to create one.
                      </TableCell>
                    </TableRow>
                  ) : (
                    assets.map((asset) => (
                      <TableRow key={asset.id}>
                        <TableCell className="font-medium font-mono text-xs">
                          {asset.asset_code}
                        </TableCell>
                        <TableCell>{asset.asset_name}</TableCell>
                        <TableCell>{getCategoryLabel(asset.category)}</TableCell>
                        <TableCell>
                          {format(new Date(asset.purchase_date), 'dd MMM yyyy')}
                        </TableCell>
                        <TableCell className="text-right">
                          {formatCurrency(asset.purchase_cost)}
                        </TableCell>
                        <TableCell className="text-right font-semibold">
                          {formatCurrency(asset.written_down_value)}
                        </TableCell>
                        <TableCell>{asset.location || '-'}</TableCell>
                        <TableCell>{getStatusBadge(asset.status)}</TableCell>
                        <TableCell className="text-right">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => router.push(`/accounting/assets/${asset.id}`)}
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-muted-foreground">Total Assets</p>
              <p className="text-2xl font-bold">{total}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Total Purchase Cost</p>
              <p className="text-2xl font-bold">
                {formatCurrency(assets.reduce((sum, a) => sum + a.purchase_cost, 0))}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Current WDV</p>
              <p className="text-2xl font-bold">
                {formatCurrency(assets.reduce((sum, a) => sum + a.written_down_value, 0))}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Total Depreciation</p>
              <p className="text-2xl font-bold">
                {formatCurrency(assets.reduce((sum, a) => sum + a.accumulated_depreciation, 0))}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
