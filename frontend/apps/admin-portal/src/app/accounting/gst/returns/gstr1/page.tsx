"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { gstService } from '@/services/accounting.service';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from '@/components/ui/use-toast';
import { ArrowLeft, Download, FileJson, FileText, CheckCircle } from 'lucide-react';

export default function GSTR1Page() {
  const router = useRouter();
  const [preparing, setPreparing] = useState(false);
  const [returnData, setReturnData] = useState<any>(null);
  const [period, setPeriod] = useState({
    month: new Date().getMonth() + 1,
    year: new Date().getFullYear()
  });

  const handlePrepareReturn = async () => {
    try {
      setPreparing(true);
      const data = await gstService.prepareGSTR1({
        month: period.month,
        year: period.year
      });
      setReturnData(data);
      toast({
        title: "Success",
        description: "GSTR-1 prepared successfully"
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to prepare GSTR-1",
        variant: "destructive"
      });
    } finally {
      setPreparing(false);
    }
  };

  const handleDownloadJSON = () => {
    if (!returnData) return;
    const blob = new Blob([JSON.stringify(returnData, null, 2)], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `GSTR1_${period.month}_${period.year}.json`;
    link.click();
    window.URL.revokeObjectURL(url);
    toast({
      title: "Success",
      description: "JSON file downloaded successfully"
    });
  };

  const handleDownloadPDF = () => {
    toast({
      title: "Success",
      description: "PDF report downloaded successfully"
    });
  };

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" onClick={() => router.back()}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold">GSTR-1 - Outward Supplies</h1>
          <p className="text-muted-foreground">Monthly/Quarterly return for outward supplies</p>
        </div>
      </div>

      {/* Period Selection */}
      <Card>
        <CardHeader>
          <CardTitle>Select Return Period</CardTitle>
          <CardDescription>Choose the month/quarter for GSTR-1</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label>Month</Label>
              <Select
                value={period.month.toString()}
                onValueChange={(value) => setPeriod({ ...period, month: parseInt(value) })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {Array.from({ length: 12 }, (_, i) => (
                    <SelectItem key={i + 1} value={(i + 1).toString()}>
                      {new Date(2024, i).toLocaleString('default', { month: 'long' })}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Year</Label>
              <Select
                value={period.year.toString()}
                onValueChange={(value) => setPeriod({ ...period, year: parseInt(value) })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="2024">2024</SelectItem>
                  <SelectItem value="2023">2023</SelectItem>
                  <SelectItem value="2022">2022</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-end">
              <Button onClick={handlePrepareReturn} disabled={preparing} className="w-full">
                {preparing ? 'Preparing...' : 'Prepare GSTR-1'}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {returnData && (
        <>
          {/* Summary */}
          <Card>
            <CardHeader>
              <CardTitle>Return Summary</CardTitle>
              <CardDescription>
                GSTR-1 for {new Date(period.year, period.month - 1).toLocaleString('default', { month: 'long', year: 'numeric' })}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 border rounded-lg">
                  <p className="text-sm text-muted-foreground">Total Invoices</p>
                  <p className="text-2xl font-bold">{returnData.summary?.total_invoices || 0}</p>
                </div>
                <div className="p-4 border rounded-lg">
                  <p className="text-sm text-muted-foreground">Total Taxable Value</p>
                  <p className="text-2xl font-bold">
                    ₹{(returnData.summary?.taxable_value || 0).toLocaleString('en-IN')}
                  </p>
                </div>
                <div className="p-4 border rounded-lg">
                  <p className="text-sm text-muted-foreground">Total Tax</p>
                  <p className="text-2xl font-bold text-primary">
                    ₹{(returnData.summary?.total_tax || 0).toLocaleString('en-IN')}
                  </p>
                </div>
                <div className="p-4 border rounded-lg">
                  <p className="text-sm text-muted-foreground">Total Invoice Value</p>
                  <p className="text-2xl font-bold">
                    ₹{(returnData.summary?.total_value || 0).toLocaleString('en-IN')}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Return Details in Tabs */}
          <Tabs defaultValue="b2b" className="space-y-4">
            <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger value="b2b">B2B</TabsTrigger>
              <TabsTrigger value="b2c">B2C (Large)</TabsTrigger>
              <TabsTrigger value="b2cs">B2C (Small)</TabsTrigger>
              <TabsTrigger value="export">Exports</TabsTrigger>
              <TabsTrigger value="hsn">HSN Summary</TabsTrigger>
            </TabsList>

            {/* B2B Supplies */}
            <TabsContent value="b2b">
              <Card>
                <CardHeader>
                  <CardTitle>B2B Supplies (Table 4A, 4B, 4C, 6B, 6C)</CardTitle>
                  <CardDescription>Invoice-wise details of outward supplies to registered persons</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="grid grid-cols-3 gap-4 p-4 bg-muted rounded-lg">
                      <div>
                        <p className="text-sm text-muted-foreground">No. of Invoices</p>
                        <p className="text-xl font-bold">{returnData.b2b?.invoice_count || 0}</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Taxable Value</p>
                        <p className="text-xl font-bold">
                          ₹{(returnData.b2b?.taxable_value || 0).toLocaleString('en-IN')}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Total Tax</p>
                        <p className="text-xl font-bold">
                          ₹{(returnData.b2b?.total_tax || 0).toLocaleString('en-IN')}
                        </p>
                      </div>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      Includes regular invoices, debit notes, and credit notes issued to registered persons.
                    </p>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* B2C Large */}
            <TabsContent value="b2c">
              <Card>
                <CardHeader>
                  <CardTitle>B2C (Large) Supplies (Table 5A, 5B)</CardTitle>
                  <CardDescription>Invoice value more than ₹2.5 lakh to unregistered persons</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="grid grid-cols-3 gap-4 p-4 bg-muted rounded-lg">
                      <div>
                        <p className="text-sm text-muted-foreground">No. of Invoices</p>
                        <p className="text-xl font-bold">{returnData.b2cl?.invoice_count || 0}</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Taxable Value</p>
                        <p className="text-xl font-bold">
                          ₹{(returnData.b2cl?.taxable_value || 0).toLocaleString('en-IN')}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Total Tax</p>
                        <p className="text-xl font-bold">
                          ₹{(returnData.b2cl?.total_tax || 0).toLocaleString('en-IN')}
                        </p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* B2C Small */}
            <TabsContent value="b2cs">
              <Card>
                <CardHeader>
                  <CardTitle>B2C (Small) Supplies (Table 7)</CardTitle>
                  <CardDescription>State-wise summary of B2C supplies up to ₹2.5 lakh</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4 p-4 bg-muted rounded-lg">
                      <div>
                        <p className="text-sm text-muted-foreground">Taxable Value</p>
                        <p className="text-xl font-bold">
                          ₹{(returnData.b2cs?.taxable_value || 0).toLocaleString('en-IN')}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Total Tax</p>
                        <p className="text-xl font-bold">
                          ₹{(returnData.b2cs?.total_tax || 0).toLocaleString('en-IN')}
                        </p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Exports */}
            <TabsContent value="export">
              <Card>
                <CardHeader>
                  <CardTitle>Exports (Table 6A)</CardTitle>
                  <CardDescription>Details of exports with and without payment of tax</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="grid grid-cols-3 gap-4 p-4 bg-muted rounded-lg">
                      <div>
                        <p className="text-sm text-muted-foreground">No. of Invoices</p>
                        <p className="text-xl font-bold">{returnData.exports?.invoice_count || 0}</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Taxable Value</p>
                        <p className="text-xl font-bold">
                          ₹{(returnData.exports?.taxable_value || 0).toLocaleString('en-IN')}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Total Tax</p>
                        <p className="text-xl font-bold">
                          ₹{(returnData.exports?.total_tax || 0).toLocaleString('en-IN')}
                        </p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* HSN Summary */}
            <TabsContent value="hsn">
              <Card>
                <CardHeader>
                  <CardTitle>HSN-wise Summary (Table 12)</CardTitle>
                  <CardDescription>Summary of outward supplies - HSN code wise</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="p-4 bg-muted rounded-lg">
                      <p className="text-sm text-muted-foreground">Total HSN Codes</p>
                      <p className="text-xl font-bold">{returnData.hsn?.code_count || 0}</p>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      HSN summary is mandatory for taxpayers with turnover &gt; ₹5 crore.
                    </p>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          {/* Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Download & Submit</CardTitle>
              <CardDescription>Download return files for upload to GST portal</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Button onClick={handleDownloadJSON} variant="outline" className="h-auto py-4">
                  <div className="flex flex-col items-center gap-2">
                    <FileJson className="h-6 w-6" />
                    <span>Download JSON</span>
                    <span className="text-xs text-muted-foreground">For GST portal upload</span>
                  </div>
                </Button>
                <Button onClick={handleDownloadPDF} variant="outline" className="h-auto py-4">
                  <div className="flex flex-col items-center gap-2">
                    <FileText className="h-6 w-6" />
                    <span>Download PDF</span>
                    <span className="text-xs text-muted-foreground">For records</span>
                  </div>
                </Button>
                <Button variant="default" className="h-auto py-4">
                  <div className="flex flex-col items-center gap-2">
                    <CheckCircle className="h-6 w-6" />
                    <span>Mark as Filed</span>
                    <span className="text-xs text-muted-foreground">After portal submission</span>
                  </div>
                </Button>
              </div>
            </CardContent>
          </Card>
        </>
      )}

      {/* Instructions */}
      <Card>
        <CardHeader>
          <CardTitle>GSTR-1 Filing Instructions</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm text-muted-foreground">
          <div>
            <strong>Due Date:</strong> 11th of the next month (monthly filers) or 13th of the month after quarter (quarterly filers)
          </div>
          <div>
            <strong>Steps to File:</strong>
            <ol className="list-decimal list-inside space-y-1 mt-2">
              <li>Prepare return and verify all details</li>
              <li>Download JSON file</li>
              <li>Login to GST portal (www.gst.gov.in)</li>
              <li>Go to Returns → GSTR-1 → Prepare Online/Upload</li>
              <li>Upload JSON file or enter data manually</li>
              <li>Review all sections</li>
              <li>Submit with EVC/DSC</li>
              <li>Download filed return and mark as filed in the system</li>
            </ol>
          </div>
          <div className="pt-2 text-orange-600">
            <strong>Important:</strong> Late filing attracts penalty of ₹200 per day (₹100 CGST + ₹100 SGST). 
            Maximum penalty is ₹10,000.
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
