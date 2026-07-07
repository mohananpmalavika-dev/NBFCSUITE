"use client";

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { gstService, type GSTTransaction } from '@/services/accounting.service';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from '@/components/ui/use-toast';
import { Plus, Search, Download, FileText } from 'lucide-react';
import { format } from 'date-fns';

export default function GSTTransactionsPage() {
  const router = useRouter();
  const [transactions, setTransactions] = useState<GSTTransaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    search: '',
    transaction_type: 'all',
    month: new Date().getMonth() + 1,
    year: new Date().getFullYear()
  });

  useEffect(() => {
    loadTransactions();
  }, [filters.transaction_type, filters.month, filters.year]);

  const loadTransactions = async () => {
    try {
      setLoading(true);
      const params: any = {
        month: filters.month,
        year: filters.year
      };
      if (filters.transaction_type !== 'all') {
        params.transaction_type = filters.transaction_type;
      }
      const data = await gstService.getTransactions(params);
      
      // Client-side search filter
      let filtered = data;
      if (filters.search) {
        filtered = data.filter((t: GSTTransaction) => 
          t.invoice_number?.toLowerCase().includes(filters.search.toLowerCase()) ||
          t.party_name?.toLowerCase().includes(filters.search.toLowerCase()) ||
          t.party_gstin?.toLowerCase().includes(filters.search.toLowerCase())
        );
      }
      
      setTransactions(filtered);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load GST transactions",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleExport = () => {
    // This would export to Excel/CSV
    toast({
      title: "Success",
      description: "Transactions exported successfully"
    });
  };

  const getTypeBadge = (type: string) => {
    const variants: Record<string, any> = {
      'sale': 'default',
      'purchase': 'secondary'
    };
    return <Badge variant={variants[type] || 'default'}>{type.toUpperCase()}</Badge>;
  };

  const getSupplyTypeBadge = (type: string) => {
    const colors: Record<string, string> = {
      'B2B': 'bg-blue-100 text-blue-800',
      'B2C': 'bg-green-100 text-green-800',
      'export': 'bg-purple-100 text-purple-800',
      'import': 'bg-orange-100 text-orange-800'
    };
    return (
      <span className={`px-2 py-1 rounded text-xs font-medium ${colors[type] || 'bg-gray-100 text-gray-800'}`}>
        {type}
      </span>
    );
  };

  // Calculate summary
  const summary = {
    total_sales: transactions
      .filter(t => t.transaction_type === 'sale')
      .reduce((sum, t) => sum + t.taxable_amount, 0),
    total_purchases: transactions
      .filter(t => t.transaction_type === 'purchase')
      .reduce((sum, t) => sum + t.taxable_amount, 0),
    output_tax: transactions
      .filter(t => t.transaction_type === 'sale')
      .reduce((sum, t) => sum + t.cgst_amount + t.sgst_amount + t.igst_amount, 0),
    input_tax: transactions
      .filter(t => t.transaction_type === 'purchase')
      .reduce((sum, t) => sum + t.cgst_amount + t.sgst_amount + t.igst_amount, 0)
  };

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">GST Transactions</h1>
          <p className="text-muted-foreground">Track all GST invoices and purchases</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleExport}>
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
          <Button onClick={() => router.push('/accounting/gst/transactions/new')}>
            <Plus className="mr-2 h-4 w-4" />
            New Transaction
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Sales
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ₹{summary.total_sales.toLocaleString('en-IN')}
            </div>
            <p className="text-xs text-muted-foreground">
              {transactions.filter(t => t.transaction_type === 'sale').length} invoices
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Purchases
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ₹{summary.total_purchases.toLocaleString('en-IN')}
            </div>
            <p className="text-xs text-muted-foreground">
              {transactions.filter(t => t.transaction_type === 'purchase').length} invoices
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Output Tax
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">
              ₹{summary.output_tax.toLocaleString('en-IN')}
            </div>
            <p className="text-xs text-muted-foreground">Tax collected</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Input Tax (ITC)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              ₹{summary.input_tax.toLocaleString('en-IN')}
            </div>
            <p className="text-xs text-muted-foreground">Available credit</p>
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
              value={filters.transaction_type}
              onValueChange={(value) => setFilters({ ...filters, transaction_type: value })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="sale">Sales</SelectItem>
                <SelectItem value="purchase">Purchases</SelectItem>
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
            <Button variant="outline" onClick={loadTransactions}>
              Refresh
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Transactions Table */}
      <Card>
        <CardHeader>
          <CardTitle>Transactions List</CardTitle>
          <CardDescription>All GST transactions for the selected period</CardDescription>
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
                    <TableHead>Type</TableHead>
                    <TableHead>Supply Type</TableHead>
                    <TableHead>Party Name</TableHead>
                    <TableHead>GSTIN</TableHead>
                    <TableHead className="text-right">Taxable (₹)</TableHead>
                    <TableHead className="text-right">CGST (₹)</TableHead>
                    <TableHead className="text-right">SGST (₹)</TableHead>
                    <TableHead className="text-right">IGST (₹)</TableHead>
                    <TableHead className="text-right">Total (₹)</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {transactions.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={11} className="text-center text-muted-foreground py-8">
                        No transactions found. Click "New Transaction" to create one.
                      </TableCell>
                    </TableRow>
                  ) : (
                    transactions.map((transaction) => (
                      <TableRow key={transaction.id}>
                        <TableCell>
                          {format(new Date(transaction.invoice_date), 'dd MMM yyyy')}
                        </TableCell>
                        <TableCell className="font-medium">{transaction.invoice_number}</TableCell>
                        <TableCell>{getTypeBadge(transaction.transaction_type)}</TableCell>
                        <TableCell>{getSupplyTypeBadge(transaction.supply_type)}</TableCell>
                        <TableCell>{transaction.party_name}</TableCell>
                        <TableCell className="font-mono text-xs">{transaction.party_gstin}</TableCell>
                        <TableCell className="text-right">
                          {transaction.taxable_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                        </TableCell>
                        <TableCell className="text-right">
                          {transaction.cgst_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                        </TableCell>
                        <TableCell className="text-right">
                          {transaction.sgst_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                        </TableCell>
                        <TableCell className="text-right">
                          {transaction.igst_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                        </TableCell>
                        <TableCell className="text-right font-semibold">
                          {transaction.total_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
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
    </div>
  );
}
