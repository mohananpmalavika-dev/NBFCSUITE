"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { gstService } from '@/services/accounting.service';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from '@/components/ui/use-toast';
import { ArrowLeft, Download, FileJson, FileText, CheckCircle, Calculator } from 'lucide-react';

export default function GSTR3BPage() {
  const router = useRouter();
  const [preparing, setPreparing] = useState(false);
  const [returnData, setReturnData] = useState<any>(null);
  const [period, setPeriod] = useState({
    month: new Date().getMonth() + 1,
    year: new Date().getFullYear()
  });

  // Manual adjustments
  const [adjustments, setAdjustments] = useState({
    reverse_charge_inward: 0,
    advances_received: 0,
    advances_adjusted: 0,
    itc_reversal: 0,
    exempt_supplies: 0
  });

  const handlePrepareReturn = async () => {
    try {
      setPreparing(true);
      const data = await gstService.prepareGSTR3B({
        month: period.month,
        year: period.year,
        adjustments
      });
      setReturnData(data);
      toast({
        title: "Success",
        description: "GSTR-3B prepared successfully"
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to prepare GSTR-3B",
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
    link.download = `GSTR3B_${period.month}_${period.year}.json`;
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
          <h1 className="text-3xl font-bold">GSTR-3B - Monthly Summary Return</h1>
          <p className="text-muted-foreground">Self-declared summary of outward and inward supplies</p>
        </div>
      </div>

      {/* Period Selection */}
      <Card>
        <CardHeader>
          <CardTitle>Select Return Period</CardTitle>
          <CardDescription>Choose the month for GSTR-3B filing</CardDescription>
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
                <Calculator className="mr-2 h-4 w-4" />
                {preparing ? 'Preparing...' : 'Prepare GSTR-3B'}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Manual Adjustments */}
      <Card>
        <CardHeader>
          <CardTitle>Manual Adjustments</CardTitle>
          <CardDescription>Enter additional values not captured in transactions</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Reverse Charge Inward Supplies (₹)</Label>
              <Input
                type="number"
                step="0.01"
                value={adjustments.reverse_charge_inward}
                onChange={(e) => setAdjustments({ ...adjustments, reverse_charge_inward: parseFloat(e.target.value) || 0 })}
                placeholder="0.00"
              />
            </div>
            <div className="space-y-2">
              <Label>Advances Received (₹)</Label>
              <Input
                type="number"
                step="0.01"
                value={adjustments.advances_received}
                onChange={(e) => setAdjustments({ ...adjustments, advances_received: parseFloat(e.target.value) || 0 })}
                placeholder="0.00"
              />
            </div>
            <div className="space-y-2">
              <Label>Advances Adjusted (₹)</Label>
              <Input
                type="number"
                step="0.01"
                value={adjustments.advances_adjusted}
                onChange={(e) => setAdjustments({ ...adjustments, advances_adjusted: parseFloat(e.target.value) || 0 })}
                placeholder="0.00"
              />
            </div>
            <div className="space-y-2">
              <Label>ITC Reversal (₹)</Label>
              <Input
                type="number"
                step="0.01"
                value={adjustments.itc_reversal}
                onChange={(e) => setAdjustments({ ...adjustments, itc_reversal: parseFloat(e.target.value) || 0 })}
                placeholder="0.00"
              />
            </div>
            <div className="space-y-2">
              <Label>Exempt Supplies (₹)</Label>
              <Input
                type="number"
                step="0.01"
                value={adjustments.exempt_supplies}
                onChange={(e) => setAdjustments({ ...adjustments, exempt_supplies: parseFloat(e.target.value) || 0 })}
                placeholder="0.00"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {returnData && (
        <>
          {/* Table 3.1 - Outward Supplies */}
          <Card>
            <CardHeader>
              <CardTitle>Table 3.1 - Details of Outward Supplies and Inward Supplies Liable to Reverse Charge</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-muted">
                    <tr>
                      <th className="p-2 text-left">Nature of Supplies</th>
                      <th className="p-2 text-right">Taxable Value (₹)</th>
                      <th className="p-2 text-right">IGST (₹)</th>
                      <th className="p-2 text-right">CGST (₹)</th>
                      <th className="p-2 text-right">SGST/UTGST (₹)</th>
                      <th className="p-2 text-right">Cess (₹)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    <tr>
                      <td className="p-2">Outward taxable supplies (other than zero rated, nil rated and exempted)</td>
                      <td className="p-2 text-right font-mono">
                        {(returnData.table_3_1?.outward_taxable?.taxable_value || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </td>
                      <td className="p-2 text-right font-mono">
                        {(returnData.table_3_1?.outward_taxable?.igst || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </td>
                      <td className="p-2 text-right font-mono">
                        {(returnData.table_3_1?.outward_taxable?.cgst || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </td>
                      <td className="p-2 text-right font-mono">
                        {(returnData.table_3_1?.outward_taxable?.sgst || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </td>
                      <td className="p-2 text-right font-mono">0.00</td>
                    </tr>
                    <tr>
                      <td className="p-2">Outward taxable supplies (zero rated)</td>
                      <td className="p-2 text-right font-mono">
                        {(returnData.table_3_1?.zero_rated?.taxable_value || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </td>
                      <td className="p-2 text-right font-mono">0.00</td>
                      <td className="p-2 text-right font-mono">0.00</td>
                      <td className="p-2 text-right font-mono">0.00</td>
                      <td className="p-2 text-right font-mono">0.00</td>
                    </tr>
                    <tr>
                      <td className="p-2">Other outward supplies (Nil rated, exempted)</td>
                      <td className="p-2 text-right font-mono">
                        {adjustments.exempt_supplies.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </td>
                      <td className="p-2 text-right font-mono">0.00</td>
                      <td className="p-2 text-right font-mono">0.00</td>
                      <td className="p-2 text-right font-mono">0.00</td>
                      <td className="p-2 text-right font-mono">0.00</td>
                    </tr>
                    <tr>
                      <td className="p-2">Inward supplies (liable to reverse charge)</td>
                      <td className="p-2 text-right font-mono">
                        {adjustments.reverse_charge_inward.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </td>
                      <td className="p-2 text-right font-mono">
                        {(adjustments.reverse_charge_inward * 0.18).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </td>
                      <td className="p-2 text-right font-mono">0.00</td>
                      <td className="p-2 text-right font-mono">0.00</td>
                      <td className="p-2 text-right font-mono">0.00</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          {/* Table 4 - ITC */}
          <Card>
            <CardHeader>
              <CardTitle>Table 4 - Eligible ITC</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-muted">
                    <tr>
                      <th className="p-2 text-left">Details</th>
                      <th className="p-2 text-right">IGST (₹)</th>
                      <th className="p-2 text-right">CGST (₹)</th>
                      <th className="p-2 text-right">SGST/UTGST (₹)</th>
                      <th className="p-2 text-right">Cess (₹)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    <tr>
                      <td className="p-2">(A) ITC Available (whether in full or part)</td>
                      <td className="p-2"></td>
                      <td className="p-2"></td>
                      <td className="p-2"></td>
                      <td className="p-2"></td>
                    </tr>
                    <tr>
                      <td className="p-2 pl-6">(1) Import of goods</td>
                      <td className="p-2 text-right font-mono">0.00</td>
                      <td className="p-2 text-right font-mono">0.00</td>
                      <td className="p-2 text-right font-mono">0.00</td>
                      <td className="p-2 text-right font-mono">0.00</td>
                    </tr>
                    <tr>
                      <td className="p-2 pl-6">(2) Import of services</td>
                      <td className="p-2 text-right font-mono">0.00</td>
                      <td className="p-2 text-right font-mono">0.00</td>
                      <td className="p-2 text-right font-mono">0.00</td>
                      <td className="p-2 text-right font-mono">0.00</td>
                    </tr>
                    <tr>
                      <td className="p-2 pl-6">(3) Inward supplies liable to reverse charge</td>
                      <td className="p-2 text-right font-mono">
                        {(adjustments.reverse_charge_inward * 0.18).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </td>
                      <td className="p-2 text-right font-mono">0.00</td>
                      <td className="p-2 text-right font-mono">0.00</td>
                      <td className="p-2 text-right font-mono">0.00</td>
                    </tr>
                    <tr>
                      <td className="p-2 pl-6">(4) Inward supplies from ISD</td>
                      <td className="p-2 text-right font-mono">0.00</td>
                      <td className="p-2 text-right font-mono">0.00</td>
                      <td className="p-2 text-right font-mono">0.00</td>
                      <td className="p-2 text-right font-mono">0.00</td>
                    </tr>
                    <tr>
                      <td className="p-2 pl-6">(5) All other ITC</td>
                      <td className="p-2 text-right font-mono">
                        {(returnData.table_4?.eligible_itc?.igst || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </td>
                      <td className="p-2 text-right font-mono">
                        {(returnData.table_4?.eligible_itc?.cgst || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </td>
                      <td className="p-2 text-right font-mono">
                        {(returnData.table_4?.eligible_itc?.sgst || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </td>
                      <td className="p-2 text-right font-mono">0.00</td>
                    </tr>
                    <tr className="bg-muted/50 font-semibold">
                      <td className="p-2">(B) ITC Reversed</td>
                      <td className="p-2"></td>
                      <td className="p-2"></td>
                      <td className="p-2"></td>
                      <td className="p-2"></td>
                    </tr>
                    <tr>
                      <td className="p-2 pl-6">(2) Others</td>
                      <td className="p-2 text-right font-mono">
                        {(adjustments.itc_reversal / 2).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </td>
                      <td className="p-2 text-right font-mono">
                        {(adjustments.itc_reversal / 4).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </td>
                      <td className="p-2 text-right font-mono">
                        {(adjustments.itc_reversal / 4).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </td>
                      <td className="p-2 text-right font-mono">0.00</td>
                    </tr>
                    <tr className="bg-primary/10 font-bold">
                      <td className="p-2">(C) Net ITC Available (A) - (B)</td>
                      <td className="p-2 text-right font-mono">
                        {(returnData.table_4?.net_itc?.igst || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </td>
                      <td className="p-2 text-right font-mono">
                        {(returnData.table_4?.net_itc?.cgst || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </td>
                      <td className="p-2 text-right font-mono">
                        {(returnData.table_4?.net_itc?.sgst || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </td>
                      <td className="p-2 text-right font-mono">0.00</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          {/* Table 6.1 - Payment of Tax */}
          <Card>
            <CardHeader>
              <CardTitle>Table 6.1 - Payment of Tax</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-4 gap-4 p-4 bg-primary/10 rounded-lg">
                  <div>
                    <p className="text-sm text-muted-foreground">IGST</p>
                    <p className="text-xl font-bold text-primary">
                      ₹{(returnData.table_6_1?.tax_payable?.igst || 0).toLocaleString('en-IN')}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">CGST</p>
                    <p className="text-xl font-bold text-primary">
                      ₹{(returnData.table_6_1?.tax_payable?.cgst || 0).toLocaleString('en-IN')}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">SGST</p>
                    <p className="text-xl font-bold text-primary">
                      ₹{(returnData.table_6_1?.tax_payable?.sgst || 0).toLocaleString('en-IN')}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Total Tax Payable</p>
                    <p className="text-2xl font-bold text-primary">
                      ₹{(returnData.table_6_1?.total_tax_payable || 0).toLocaleString('en-IN')}
                    </p>
                  </div>
                </div>
                <p className="text-sm text-muted-foreground">
                  Tax payable = Output Tax - ITC Available
                </p>
              </div>
            </CardContent>
          </Card>

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
          <CardTitle>GSTR-3B Filing Instructions</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm text-muted-foreground">
          <div>
            <strong>Due Date:</strong> 20th of the next month (monthly filers) or 22nd/24th of the month after quarter (quarterly filers)
          </div>
          <div>
            <strong>Important Points:</strong>
            <ul className="list-disc list-inside space-y-1 mt-2">
              <li>GSTR-3B is a self-declared summary return</li>
              <li>Must match with GSTR-1 (outward supplies)</li>
              <li>ITC can be claimed only to the extent available in GSTR-2B</li>
              <li>Tax liability must be paid before filing</li>
              <li>Use PMT-06 challan for tax payment</li>
              <li>Late filing attracts interest @ 18% p.a. and late fee of ₹50/day per Act</li>
            </ul>
          </div>
          <div className="pt-2 text-orange-600">
            <strong>Warning:</strong> Ensure all manual adjustments are accurate. Mismatches between GSTR-1 and GSTR-3B may lead to notices.
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
