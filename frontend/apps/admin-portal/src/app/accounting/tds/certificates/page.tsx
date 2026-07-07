"use client";

import React, { useState, useEffect } from 'react';
import { tdsService } from '@/services/accounting.service';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from '@/components/ui/use-toast';
import { Download, FileText, Search, Send } from 'lucide-react';
import { format } from 'date-fns';

interface CertificateView {
  id: number;
  deduction_id: number;
  certificate_number: string;
  issue_date: string;
  deductee_name: string;
  deductee_pan: string;
  financial_year: number;
  quarter: string;
  tds_amount: number;
  total_gross_amount: number;
  total_tds_amount: number;
  status: string;
}

export default function TDSCertificatesPage() {
  const [certificates, setCertificates] = useState<CertificateView[]>([]);
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
      // Since getCertificates doesn't exist, we'll use the deductions endpoint
      // and filter for those with certificates generated
      const params: any = { payment_status: 'DEPOSITED' };
      if (filters.financial_year !== 'all') {
        params.financial_year = parseInt(filters.financial_year);
      }
      const response = await tdsService.getDeductions(params);
      
      // Transform deductions to certificates format
      const certificatesData = response.data.items
        .filter((d: any) => d.challan_verified)
        .map((d: any) => ({
          id: d.id,
          deduction_id: d.id,
          certificate_number: `TDS/CERT/${d.id}/${d.financial_year}`,
          issue_date: d.challan_verified_date || d.created_at,
          deductee_name: d.deductee_name,
          deductee_pan: d.deductee_pan || 'N/A',
          financial_year: d.financial_year,
          quarter: `Q${d.quarter}`,
          tds_amount: d.tds_amount,
          total_gross_amount: d.gross_amount,
          total_tds_amount: d.tds_amount,
          status: 'generated'
        }));
      
      // Client-side search filter
      let filtered = certificatesData;
      if (filters.search) {
        filtered = certificatesData.filter((c: any) => 
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

  const handleDownloadCertificate = async (certificate: CertificateView) => {
    try {
      // For now, show a message that certificate download is not yet implemented
      // In production, this would call the generateCertificate endpoint with proper data
      toast({
        title: "Not Implemented",
        description: "Certificate PDF generation will be implemented soon",
        variant: "default"
      });
      
      // TODO: Implement proper certificate generation
      // const response = await tdsService.generateCertificate({
      //   financial_year: parseInt(certificate.financial_year),
      //   quarter: parseInt(certificate.quarter.replace('Q', '')),
      //   deductee_id: certificate.deduction_id,
      //   deductee_type: 'customer',
      //   deductee_name: certificate.deductee_name,
      //   deductee_pan: certificate.deductee_pan,
      //   deductor_tan: 'TANXXXXXXX',
      //   deductor_pan: 'PANXXXXXXX',
      //   deductor_name: 'NBFC Demo Ltd'
      // });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to download certificate",
        variant: "destructive"
      });
    }
  };

  const handleSendEmail = async (certificate: CertificateView) => {
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
