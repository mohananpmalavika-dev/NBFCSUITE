"use client";

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { tdsService, type TDSChallan } from '@/services/accounting.service';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from '@/components/ui/use-toast';
import { Plus, Search, CheckCircle, XCircle } from 'lucide-react';
import { format } from 'date-fns';

export default function TDSChallansPage() {
  const router = useRouter();
  const [challans, setChallans] = useState<TDSChallan[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    search: '',
    status: 'all',
    financial_year: new Date().getFullYear().toString()
  });

  useEffect(() => {
    loadChallans();
  }, [filters]);

  const loadChallans = async () => {
    try {
      setLoading(true);
      // getChallans method doesn't exist in tdsService yet
      // Using empty array as placeholder - API endpoint needs to be implemented
      toast({
        title: "Info",
        description: "TDS Challans API is not yet implemented. Showing empty list.",
        variant: "default"
      });
      setChallans([]);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load TDS challans",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyChallan = async (id: number) => {
    try {
      // updateChallan method doesn't exist yet - placeholder
      toast({
        title: "Not Implemented",
        description: "Challan verification API endpoint needs to be implemented",
        variant: "default"
      });
      // await tdsService.updateChallan(id, { status: 'verified' });
      // loadChallans();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to verify challan",
        variant: "destructive"
      });
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, any> = {
      'paid': 'default',
      'verified': 'success',
      'pending': 'secondary',
      'cancelled': 'destructive'
    };
    return <Badge variant={variants[status] || 'default'}>{status.toUpperCase()}</Badge>;
  };

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">TDS Challans</h1>
          <p className="text-muted-foreground">Track TDS payment challans (Form 281)</p>
        </div>
        <Button onClick={() => router.push('/accounting/tds/challans/new')}>
          <Plus className="mr-2 h-4 w-4" />
          Record Challan
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="relative">
              <Search className="absolute left-2 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by challan no, BSR..."
                value={filters.search}
                onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                className="pl-8"
              />
            </div>
            <Select
              value={filters.financial_year}
              onValueChange={(value) => setFilters({ ...filters, financial_year: value })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Financial Year" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Years</SelectItem>
                <SelectItem value="2024">FY 2024-25</SelectItem>
                <SelectItem value="2023">FY 2023-24</SelectItem>
                <SelectItem value="2022">FY 2022-23</SelectItem>
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
                <SelectItem value="paid">Paid</SelectItem>
                <SelectItem value="verified">Verified</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="cancelled">Cancelled</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" onClick={loadChallans}>
              Refresh
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Challans List</CardTitle>
          <CardDescription>All TDS payment challans</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Payment Date</TableHead>
                  <TableHead>Challan No.</TableHead>
                  <TableHead>BSR Code</TableHead>
                  <TableHead>Bank</TableHead>
                  <TableHead>Period</TableHead>
                  <TableHead className="text-right">Amount (₹)</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {challans.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center text-muted-foreground py-8">
                      No challans found. Click "Record Challan" to create one.
                    </TableCell>
                  </TableRow>
                ) : (
                  challans.map((challan) => (
                    <TableRow key={challan.id}>
                      <TableCell>
                        {format(new Date(challan.payment_date), 'dd MMM yyyy')}
                      </TableCell>
                      <TableCell className="font-medium">{challan.challan_number}</TableCell>
                      <TableCell>{challan.bsr_code}</TableCell>
                      <TableCell>{challan.bank_name}</TableCell>
                      <TableCell>
                        {/* Challan type doesn't have these properties yet */}
                        N/A
                      </TableCell>
                      <TableCell className="text-right">
                        ₹{challan.total_tds_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </TableCell>
                      <TableCell>{getStatusBadge(challan.payment_status)}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          {challan.payment_status === 'paid' && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleVerifyChallan(challan.id)}
                              title="Verify with TRACES"
                            >
                              <CheckCircle className="h-4 w-4 text-green-600" />
                            </Button>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Payment Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-muted-foreground">Total Challans</p>
              <p className="text-2xl font-bold">{challans.length}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Total Paid</p>
              <p className="text-2xl font-bold">
                ₹{challans.reduce((sum, c) => sum + c.total_tds_amount, 0).toLocaleString('en-IN')}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Verified</p>
              <p className="text-2xl font-bold text-green-600">
                {challans.filter(c => c.payment_status === 'verified').length}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Pending Verification</p>
              <p className="text-2xl font-bold text-orange-600">
                {challans.filter(c => c.payment_status === 'paid').length}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
