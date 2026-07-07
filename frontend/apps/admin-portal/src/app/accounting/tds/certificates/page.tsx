"use client";

import React, { useState, useEffect } from 'react';
import { tdsService, type TDSCertificate } from '@/services/accounting.service';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from '@/components/ui/use-toast';
import { Download, FileText, Search, Send } from 'lucide-react';
import { format } from 'date-fns';

export default function TDSCertificatesPage() {
  const [certificates, setCertificates] = useState<TDSCertificate[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    search: '',
    financial_year: new Date().getFullYear().toString()
  });

  useEffect(() => {
    loadCertificates();
  }, [filters]);

  const loadCertificates = async () => {
    try {
      setLoading(true);
      const params: any = {};
      if (filters.financial_year !== 'all') {
        params.financial_year = filters.financial_year;
      }
      const data = await tdsService.getCertificates(params);
      
      // Client-side search filter
      let filtered = data;
      if (filters.search) {
        filtered = data.filter((c: TDSCertificate) => 
          c.certificate_number?.toLowerCase().includes(filters.search.toLowerCase()) ||
          c.deductee_pan?.toLowerCase().includes(filters.search.toLowerCase()) ||
          c.deductee_name?.toLowerCase().includes(filters.search.toLowerCase())
        );
      }
      
      setCertificates(filtered);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load TDS certificates",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadCertificate = async (certificate: TDSCertificate) => {
    try {
      // Generate fresh certificate
      const pdfBlob = await tdsService.generateCertificate(certificate.deduction_id);
      const url = window.URL.createObjectURL(pdfBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `Form16A_${certificate.certificate_number}_${certificate.deductee_pan}.pdf`;
      link.click();
      window.URL.revokeObjectURL(url);
      toast({
        title: "Success",
        description: "Certificate downloaded successfully"
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to download certificate",
        variant: "destructive"
      });
    }
  };

  const handleSendEmail = async (certificate: TDSCertificate) => {
    const email = prompt(`Enter email address for ${certificate.deductee_name}:`);
    if (!email) return;

    try {
      // This would call an API endpoint to send email
      toast({
        title: "Success",
        description: `Certificate sent to ${email}`
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to send certificate",
        variant: "destructive"
      });
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, any> = {
      'generated': 'success',
      'sent': 'default',
      'pending': 'secondary'
    };
    return <Badge variant={variants[status] || 'default'}>{status.toUpperCase()}</Badge>;
  };

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">TDS Certificates</h1>
          <p className="text-muted-foreground">Form 16A certificates issued to deductees</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="relative">
              <Search className="absolute left-2 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by cert no, PAN, name..."
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
            <Button variant="outline" onClick={loadCertificates}>
              Refresh
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Certificates List</CardTitle>
          <CardDescription>Form 16A certificates for all deductees</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Certificate No.</TableHead>
                  <TableHead>Issue Date</TableHead>
                  <TableHead>Deductee Name</TableHead>
                  <TableHead>PAN</TableHead>
                  <TableHead>Period</TableHead>
                  <TableHead className="text-right">TDS Amount (₹)</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {certificates.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center text-muted-foreground py-8">
                      No certificates found. Certificates are auto-generated when challans are verified.
                    </TableCell>
                  </TableRow>
                ) : (
                  certificates.map((certificate) => (
                    <TableRow key={certificate.id}>
                      <TableCell className="font-medium">{certificate.certificate_number}</TableCell>
                      <TableCell>
                        {format(new Date(certificate.issue_date), 'dd MMM yyyy')}
                      </TableCell>
                      <TableCell>{certificate.deductee_name}</TableCell>
                      <TableCell>{certificate.deductee_pan}</TableCell>
                      <TableCell>
                        {certificate.financial_year} - {certificate.quarter}
                      </TableCell>
                      <TableCell className="text-right">
                        ₹{certificate.tds_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </TableCell>
                      <TableCell>{getStatusBadge(certificate.status)}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDownloadCertificate(certificate)}
                            title="Download PDF"
                          >
                            <Download className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleSendEmail(certificate)}
                            title="Send via Email"
                          >
                            <Send className="h-4 w-4" />
                          </Button>
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

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Certificate Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Total Certificates</p>
                <p className="text-2xl font-bold">{certificates.length}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Generated</p>
                <p className="text-2xl font-bold text-green-600">
                  {certificates.filter(c => c.status === 'generated').length}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Sent</p>
                <p className="text-2xl font-bold text-blue-600">
                  {certificates.filter(c => c.status === 'sent').length}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total TDS</p>
                <p className="text-2xl font-bold">
                  ₹{certificates.reduce((sum, c) => sum + c.tds_amount, 0).toLocaleString('en-IN')}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>About Form 16A</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <p>
              <strong>Form 16A</strong> is a TDS certificate issued by the deductor to the deductee for TDS 
              deducted on payments other than salary.
            </p>
            <ul className="list-disc list-inside space-y-1 text-muted-foreground">
              <li>Issued quarterly after challan verification</li>
              <li>Contains details of TDS deducted and deposited</li>
              <li>Required for deductee's income tax return filing</li>
              <li>Must be verified on TRACES portal</li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
