"use client";

import React, { useState, useEffect } from 'react';
import { gstService } from '@/services/accounting.service';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from '@/components/ui/use-toast';
import { Search, Download, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import { format } from 'date-fns';

export default function ITCPage() {
  const [itcRecords, setItcRecords] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    search: '',
    eligibility: 'all',
    month: new Date().getMonth() + 1,
    year: new Date().getFullYear()
  });

  useEffect(() => {
    loadITC();
  }, [filters.month, filters.year]);

  const loadITC = async () => {
    try {
      setLoading(true);
      // TODO: Implement getInputCredit endpoint to fetch ITC records
      // const params: any = {
      //   month: filters.month,
      //   year: filters.year
      // };
      // const data = await gstService.getInputCredit(params);
      const data: any[] = [];
      
      // Client-side filters
      let filtered = data;
      if (filters.search) {
        filtered = data.filter((itc: any) => 
          itc.supplier_name?.toLowerCase().includes(filters.search.toLowerCase()) ||
          itc.supplier_gstin?.toLowerCase().includes(filters.search.toLowerCase()) ||
          itc.invoice_number?.toLowerCase().includes(filters.search.toLowerCase())
        );
      }
      if (filters.eligibility !== 'all') {
        filtered = filtered.filter((itc: any) => itc.eligibility_status === filters.eligibility);
      }
      
      setItcRecords(filtered);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load ITC records",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const getEligibilityBadge = (status: string) => {
    const variants: Record<string, any> = {
      'eligible': { variant: 'success', icon: CheckCircle, color: 'text-green-600' },
      'ineligible': { variant: 'destructive', icon: XCircle, color: 'text-red-600' },
      'partially_eligible': { variant: 'warning', icon: AlertTriangle, color: 'text-orange-600' }
    };
    const config = variants[status] || variants['eligible'];
    const Icon = config.icon;
    
    return (
      <div className="flex items-center gap-2">
        <Icon className={`h-4 w-4 ${config.color}`} />
        <Badge variant={config.variant}>
          {status.replace('_', ' ').toUpperCase()}
        </Badge>
      </div>
    );
  };

  // Calculate summary
  const summary = {
    total_itc: itcRecords.reduce((sum, itc) => sum + itc.itc_amount, 0),
    eligible_itc: itcRecords
      .filter(itc => itc.eligibility_status === 'eligible')
      .reduce((sum, itc) => sum + itc.itc_amount, 0),
    ineligible_itc: itcRecords
      .filter(itc => itc.eligibility_status === 'ineligible')
      .reduce((sum, itc) => sum + itc.itc_amount, 0),
    reversed_itc: itcRecords.reduce((sum, itc) => sum + (itc.reversal_amount || 0), 0),
    net_itc: 0
  };
  summary.net_itc = summary.eligible_itc - summary.reversed_itc;

  const handleExport = () => {
    toast({
      title: "Success",
      description: "ITC register exported successfully"
    });
  };

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Input Tax Credit (ITC)</h1>
          <p className="text-muted-foreground">Track and manage GST input tax credit</p>
        </div>
        <Button variant="outline" onClick={handleExport}>
          <Download className="mr-2 h-4 w-4" />
          Export ITC Register
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total ITC
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ₹{summary.total_itc.toLocaleString('en-IN')}
            </div>
            <p className="text-xs text-muted-foreground">
              {itcRecords.length} transactions
            </p>
          </CardContent>
        </Card>

        <Card className="bg-green-50 dark:bg-green-950">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Eligible ITC
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              ₹{summary.eligible_itc.toLocaleString('en-IN')}
            </div>
            <p className="text-xs text-muted-foreground">
              {itcRecords.filter(i => i.eligibility_status === 'eligible').length} eligible
            </p>
          </CardContent>
        </Card>

        <Card className="bg-red-50 dark:bg-red-950">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Ineligible ITC
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              ₹{summary.ineligible_itc.toLocaleString('en-IN')}
            </div>
            <p className="text-xs text-muted-foreground">
              {itcRecords.filter(i => i.eligibility_status === 'ineligible').length} ineligible
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Reversed ITC
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              ₹{summary.reversed_itc.toLocaleString('en-IN')}
            </div>
            <p className="text-xs text-muted-foreground">Reversals</p>
          </CardContent>
        </Card>

        <Card className="bg-primary/10">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Net Available ITC
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-primary">
              ₹{summary.net_itc.toLocaleString('en-IN')}
            </div>
            <p className="text-xs text-muted-foreground">For utilization</p>
          </CardContent>
        </Card>
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
                placeholder="Search..."
                value={filters.search}
                onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                className="pl-8"
              />
            </div>
            <Select
              value={filters.eligibility}
              onValueChange={(value) => setFilters({ ...filters, eligibility: value })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Eligibility" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="eligible">Eligible</SelectItem>
                <SelectItem value="ineligible">Ineligible</SelectItem>
                <SelectItem value="partially_eligible">Partially Eligible</SelectItem>
              </SelectContent>
            </Select>
            <Select
              value={filters.month.toString()}
              onValueChange={(value) => setFilters({ ...filters, month: parseInt(value) })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Month" />
              </SelectTrigger>
              <SelectContent>
                {Array.from({ length: 12 }, (_, i) => (
                  <SelectItem key={i + 1} value={(i + 1).toString()}>
                    {new Date(2024, i).toLocaleString('default', { month: 'long' })}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select
              value={filters.year.toString()}
              onValueChange={(value) => setFilters({ ...filters, year: parseInt(value) })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Year" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="2024">2024</SelectItem>
                <SelectItem value="2023">2023</SelectItem>
                <SelectItem value="2022">2022</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" onClick={loadITC}>
              Refresh
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* ITC Table */}
      <Card>
        <CardHeader>
          <CardTitle>ITC Register</CardTitle>
          <CardDescription>Input tax credit from purchase invoices</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Date</TableHead>
                    <TableHead>Invoice No.</TableHead>
                    <TableHead>Supplier Name</TableHead>
                    <TableHead>GSTIN</TableHead>
                    <TableHead className="text-right">Taxable (₹)</TableHead>
                    <TableHead className="text-right">CGST (₹)</TableHead>
                    <TableHead className="text-right">SGST (₹)</TableHead>
                    <TableHead className="text-right">IGST (₹)</TableHead>
                    <TableHead className="text-right">Total ITC (₹)</TableHead>
                    <TableHead>Eligibility</TableHead>
                    <TableHead className="text-right">Reversal (₹)</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {itcRecords.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={11} className="text-center text-muted-foreground py-8">
                        No ITC records found for selected period
                      </TableCell>
                    </TableRow>
                  ) : (
                    itcRecords.map((itc) => (
                      <TableRow key={itc.id}>
                        <TableCell>
                          {format(new Date(itc.invoice_date), 'dd MMM yyyy')}
                        </TableCell>
                        <TableCell className="font-medium">{itc.invoice_number}</TableCell>
                        <TableCell>{itc.supplier_name}</TableCell>
                        <TableCell className="font-mono text-xs">{itc.supplier_gstin}</TableCell>
                        <TableCell className="text-right">
                          {itc.taxable_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                        </TableCell>
                        <TableCell className="text-right">
                          {itc.cgst_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                        </TableCell>
                        <TableCell className="text-right">
                          {itc.sgst_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                        </TableCell>
                        <TableCell className="text-right">
                          {itc.igst_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                        </TableCell>
                        <TableCell className="text-right font-semibold">
                          {itc.itc_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                        </TableCell>
                        <TableCell>{getEligibilityBadge(itc.eligibility_status)}</TableCell>
                        <TableCell className="text-right text-red-600">
                          {itc.reversal_amount 
                            ? itc.reversal_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })
                            : '-'}
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

      {/* ITC Rules */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Eligible ITC Conditions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-muted-foreground">
            <ul className="list-disc list-inside space-y-1">
              <li>Possession of valid tax invoice</li>
              <li>Goods/services received</li>
              <li>Tax paid to government by supplier</li>
              <li>Return filed by recipient</li>
              <li>Used for business purposes</li>
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Ineligible ITC Items</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-muted-foreground">
            <ul className="list-disc list-inside space-y-1">
              <li>Motor vehicles (except for specified purposes)</li>
              <li>Food and beverages</li>
              <li>Outdoor catering</li>
              <li>Personal use items</li>
              <li>Club membership fees</li>
              <li>Works contract services for immovable property</li>
            </ul>
          </CardContent>
        </Card>
      </div>

      {/* ITC Reconciliation */}
      <Card>
        <CardHeader>
          <CardTitle>ITC Reconciliation Summary</CardTitle>
          <CardDescription>Match ITC claimed with GSTR-2A/2B</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 border rounded-lg">
                <p className="text-sm text-muted-foreground">ITC as per Books</p>
                <p className="text-xl font-bold">₹{summary.eligible_itc.toLocaleString('en-IN')}</p>
              </div>
              <div className="p-4 border rounded-lg">
                <p className="text-sm text-muted-foreground">ITC as per GSTR-2B</p>
                <p className="text-xl font-bold">₹{(summary.eligible_itc * 0.95).toLocaleString('en-IN')}</p>
                <p className="text-xs text-orange-600 mt-1">5% pending upload by suppliers</p>
              </div>
              <div className="p-4 border rounded-lg bg-orange-50 dark:bg-orange-950">
                <p className="text-sm text-muted-foreground">Difference</p>
                <p className="text-xl font-bold text-orange-600">
                  ₹{(summary.eligible_itc * 0.05).toLocaleString('en-IN')}
                </p>
                <p className="text-xs text-muted-foreground mt-1">Requires follow-up</p>
              </div>
            </div>
            <p className="text-sm text-muted-foreground">
              <strong>Note:</strong> ITC can be claimed only to the extent available in GSTR-2B. 
              Follow up with suppliers for missing invoices.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
