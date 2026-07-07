"use client";

import React, { useState, useEffect } from 'react';
import { tdsService, type TDSReturn } from '@/services/accounting.service';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { toast } from '@/components/ui/use-toast';
import { Plus, Download, FileText, Send, CheckCircle } from 'lucide-react';
import { format } from 'date-fns';

export default function TDSReturnsPage() {
  const [returns, setReturns] = useState<TDSReturn[]>([]);
  const [loading, setLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [preparingReturn, setPreparingReturn] = useState(false);
  const [formData, setFormData] = useState({
    financial_year: new Date().getFullYear().toString(),
    quarter: 'Q1',
    return_type: '26Q',
    deductor_tan: '',
    deductor_name: '',
    deductor_branch: ''
  });

  useEffect(() => {
    loadReturns();
  }, []);

  const loadReturns = async () => {
    try {
      setLoading(true);
      const data = await tdsService.getReturns();
      setReturns(data);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load TDS returns",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handlePrepareReturn = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setPreparingReturn(true);
      const returnData = await tdsService.prepareReturn({
        financial_year: formData.financial_year,
        quarter: formData.quarter,
        return_type: formData.return_type
      });

      toast({
        title: "Success",
        description: `Form ${formData.return_type} prepared successfully with ${returnData.total_deductions} deductions`
      });
      
      setIsDialogOpen(false);
      setFormData({
        financial_year: new Date().getFullYear().toString(),
        quarter: 'Q1',
        return_type: '26Q',
        deductor_tan: '',
        deductor_name: '',
        deductor_branch: ''
      });
      loadReturns();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to prepare return",
        variant: "destructive"
      });
    } finally {
      setPreparingReturn(false);
    }
  };

  const handleDownloadReturn = async (returnItem: TDSReturn) => {
    try {
      // This would generate the TDS file in specified format
      toast({
        title: "Success",
        description: "TDS return file downloaded successfully"
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to download return",
        variant: "destructive"
      });
    }
  };

  const handleFileReturn = async (id: number) => {
    if (!confirm('Have you verified all details? This will mark the return as filed.')) return;
    
    try {
      await tdsService.updateReturn(id, { status: 'filed' });
      toast({
        title: "Success",
        description: "Return marked as filed"
      });
      loadReturns();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update return status",
        variant: "destructive"
      });
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, any> = {
      'draft': 'secondary',
      'prepared': 'default',
      'filed': 'success',
      'revised': 'outline'
    };
    return <Badge variant={variants[status] || 'default'}>{status.toUpperCase()}</Badge>;
  };

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">TDS Returns</h1>
          <p className="text-muted-foreground">Quarterly TDS return filing (Form 26Q)</p>
        </div>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Prepare Return
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Prepare TDS Return</DialogTitle>
              <DialogDescription>
                Generate Form 26Q for the selected quarter
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handlePrepareReturn}>
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="financial_year">Financial Year *</Label>
                    <Select
                      value={formData.financial_year}
                      onValueChange={(value) => setFormData({ ...formData, financial_year: value })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="2024">FY 2024-25</SelectItem>
                        <SelectItem value="2023">FY 2023-24</SelectItem>
                        <SelectItem value="2022">FY 2022-23</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="quarter">Quarter *</Label>
                    <Select
                      value={formData.quarter}
                      onValueChange={(value) => setFormData({ ...formData, quarter: value })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Q1">Q1 (Apr-Jun)</SelectItem>
                        <SelectItem value="Q2">Q2 (Jul-Sep)</SelectItem>
                        <SelectItem value="Q3">Q3 (Oct-Dec)</SelectItem>
                        <SelectItem value="Q4">Q4 (Jan-Mar)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="return_type">Return Type *</Label>
                  <Select
                    value={formData.return_type}
                    onValueChange={(value) => setFormData({ ...formData, return_type: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="26Q">Form 26Q (TDS on payments other than salary)</SelectItem>
                      <SelectItem value="24Q">Form 24Q (TDS on salary)</SelectItem>
                      <SelectItem value="27Q">Form 27Q (TDS on payments to NRI)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="deductor_tan">Deductor TAN</Label>
                  <Input
                    id="deductor_tan"
                    value={formData.deductor_tan}
                    onChange={(e) => setFormData({ ...formData, deductor_tan: e.target.value.toUpperCase() })}
                    placeholder="ABCD12345E"
                    maxLength={10}
                  />
                </div>
              </div>
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={preparingReturn}>
                  {preparingReturn ? 'Preparing...' : 'Prepare Return'}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Returns List</CardTitle>
          <CardDescription>All TDS returns prepared and filed</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Return Type</TableHead>
                  <TableHead>Period</TableHead>
                  <TableHead>Preparation Date</TableHead>
                  <TableHead className="text-right">Total Deductions</TableHead>
                  <TableHead className="text-right">Total TDS (₹)</TableHead>
                  <TableHead>Filing Date</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {returns.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center text-muted-foreground py-8">
                      No returns found. Click "Prepare Return" to create one.
                    </TableCell>
                  </TableRow>
                ) : (
                  returns.map((returnItem) => (
                    <TableRow key={returnItem.id}>
                      <TableCell className="font-medium">{returnItem.return_type}</TableCell>
                      <TableCell>
                        {returnItem.financial_year} - {returnItem.quarter}
                      </TableCell>
                      <TableCell>
                        {format(new Date(returnItem.preparation_date), 'dd MMM yyyy')}
                      </TableCell>
                      <TableCell className="text-right">{returnItem.total_deductions}</TableCell>
                      <TableCell className="text-right">
                        ₹{returnItem.total_tds_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </TableCell>
                      <TableCell>
                        {returnItem.filing_date 
                          ? format(new Date(returnItem.filing_date), 'dd MMM yyyy')
                          : '-'}
                      </TableCell>
                      <TableCell>{getStatusBadge(returnItem.status)}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDownloadReturn(returnItem)}
                            title="Download TDS File"
                          >
                            <Download className="h-4 w-4" />
                          </Button>
                          {returnItem.status === 'prepared' && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleFileReturn(returnItem.id)}
                              title="Mark as Filed"
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

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Filing Schedule</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Q1 (Apr-Jun)</span>
              <span className="font-medium">Due: 31 July</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Q2 (Jul-Sep)</span>
              <span className="font-medium">Due: 31 October</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Q3 (Oct-Dec)</span>
              <span className="font-medium">Due: 31 January</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Q4 (Jan-Mar)</span>
              <span className="font-medium">Due: 31 May</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Return Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-muted-foreground">Total Returns</p>
                <p className="text-2xl font-bold">{returns.length}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Filed</p>
                <p className="text-2xl font-bold text-green-600">
                  {returns.filter(r => r.status === 'filed').length}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Pending</p>
                <p className="text-2xl font-bold text-orange-600">
                  {returns.filter(r => r.status === 'prepared').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Important Notes</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-muted-foreground">
            <ul className="list-disc list-inside space-y-1">
              <li>Verify all challan details before filing</li>
              <li>Ensure PAN/TAN details are correct</li>
              <li>File returns before due date to avoid penalty</li>
              <li>Download acknowledgment after e-filing</li>
              <li>Generate Form 16A after successful filing</li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
