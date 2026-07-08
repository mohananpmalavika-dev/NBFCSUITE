"use client";

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { tdsService, type TDSDeduction } from '@/services/accounting.service';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from '@/components/ui/use-toast';
import { Plus, Eye, FileText, Search } from 'lucide-react';
import { format } from 'date-fns';

export default function TDSDeductionsPage() {
  const router = useRouter();
  const [deductions, setDeductions] = useState<TDSDeduction[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    search: '',
    status: 'all',
    financial_year: new Date().getFullYear().toString()
  });

  useEffect(() => {
    loadDeductions();
  }, [filters]);

  const loadDeductions = async () => {
    try {
      setLoading(true);
      const params: any = {};
      if (filters.financial_year !== 'all') {
        params.financial_year = filters.financial_year;
      }
      if (filters.status !== 'all') {
        params.status = filters.status;
      }
      const response = await tdsService.getDeductions(params);
      const data = response.data.items || [];
      
      // Client-side search filter
      let filtered = data;
      if (filters.search) {
        filtered = data.filter((d: TDSDeduction) => 
          d.deductee_name?.toLowerCase().includes(filters.search.toLowerCase()) ||
          d.deductee_pan?.toLowerCase().includes(filters.search.toLowerCase()) ||
          d.deduction_number?.toLowerCase().includes(filters.search.toLowerCase())
        );
      }
      
      setDeductions(filtered);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load TDS deductions",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
      'deducted': 'default',
      'paid': 'default',
      'deposited': 'default',
      'pending': 'secondary'
    };
    return <Badge variant={variants[status] || 'default'}>{status.toUpperCase()}</Badge>;
  };

  const handleViewDetails = (id: number) => {
    router.push(`/accounting/tds/deductions/${id}`);
  };

  const handleGenerateCertificate = async (deduction: TDSDeduction) => {
    try {
      // Extract financial year and quarter from deduction date
      const deductionDate = new Date(deduction.deduction_date);
      const financial_year = deductionDate.getMonth() >= 3 
        ? deductionDate.getFullYear() 
        : deductionDate.getFullYear() - 1;
      const quarter = Math.floor((deductionDate.getMonth() + 9) % 12 / 3) + 1;

      const certificateData = {
        financial_year,
        quarter,
        deductee_id: deduction.id,
        deductee_type: 'vendor', // Default type, adjust as needed
        deductee_name: deduction.deductee_name,
        deductee_pan: deduction.deductee_pan || '',
        deductee_address: '', // Not available in TDSDeduction
        deductor_tan: '', // These should come from company settings
        deductor_pan: '',
        deductor_name: ''
      };

      const pdfBlob = await tdsService.generateCertificate(certificateData);
      const url = window.URL.createObjectURL(pdfBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `Form16A_${deduction.deductee_pan}_${format(new Date(deduction.deduction_date), 'yyyyMMdd')}.pdf`;
      link.click();
      window.URL.revokeObjectURL(url);
      toast({
        title: "Success",
        description: "Certificate generated successfully"
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to generate certificate",
        variant: "destructive"
      });
    }
  };

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">TDS Deductions</h1>
          <p className="text-muted-foreground">Track and manage TDS deductions</p>
        </div>
        <Button onClick={() => router.push('/accounting/tds/deductions/new')}>
          <Plus className="mr-2 h-4 w-4" />
          Record Deduction
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
          <CardDescription>Filter TDS deductions by various criteria</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="relative">
              <Search className="absolute left-2 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by name, PAN, voucher..."
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
                <SelectItem value="deducted">Deducted</SelectItem>
                <SelectItem value="deposited">Deposited</SelectItem>
                <SelectItem value="paid">Paid</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" onClick={loadDeductions}>
              Refresh
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Deductions List</CardTitle>
          <CardDescription>All TDS deductions for the selected period</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Voucher No.</TableHead>
                  <TableHead>Deductee</TableHead>
                  <TableHead>PAN</TableHead>
                  <TableHead>Section</TableHead>
                  <TableHead className="text-right">Taxable Amount</TableHead>
                  <TableHead className="text-right">TDS Amount</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {deductions.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={9} className="text-center text-muted-foreground py-8">
                      No TDS deductions found. Click "Record Deduction" to create one.
                    </TableCell>
                  </TableRow>
                ) : (
                  deductions.map((deduction) => (
                    <TableRow key={deduction.id}>
                      <TableCell>
                        {format(new Date(deduction.deduction_date), 'dd MMM yyyy')}
                      </TableCell>
                      <TableCell className="font-medium">{deduction.voucher_number}</TableCell>
                      <TableCell>{deduction.deductee_name}</TableCell>
                      <TableCell>{deduction.deductee_pan}</TableCell>
                      <TableCell>{deduction.section_code}</TableCell>
                      <TableCell className="text-right">
                        ₹{deduction.taxable_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </TableCell>
                      <TableCell className="text-right">
                        ₹{deduction.tds_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </TableCell>
                      <TableCell>{getStatusBadge(deduction.status)}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleViewDetails(deduction.id)}
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          {deduction.status === 'deposited' && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleGenerateCertificate(deduction)}
                              title="Generate Form 16A"
                            >
                              <FileText className="h-4 w-4" />
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
          <CardTitle>Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-muted-foreground">Total Deductions</p>
              <p className="text-2xl font-bold">{deductions.length}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Total Taxable Amount</p>
              <p className="text-2xl font-bold">
                ₹{deductions.reduce((sum, d) => sum + d.taxable_amount, 0).toLocaleString('en-IN')}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Total TDS Deducted</p>
              <p className="text-2xl font-bold">
                ₹{deductions.reduce((sum, d) => sum + d.tds_amount, 0).toLocaleString('en-IN')}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Pending Deposit</p>
              <p className="text-2xl font-bold">
                ₹{deductions
                  .filter(d => d.status === 'deducted')
                  .reduce((sum, d) => sum + d.tds_amount, 0)
                  .toLocaleString('en-IN')}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
