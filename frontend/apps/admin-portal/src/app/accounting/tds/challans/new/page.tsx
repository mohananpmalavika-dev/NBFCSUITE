"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { tdsService } from '@/services/accounting.service';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from '@/components/ui/use-toast';
import { ArrowLeft, Save } from 'lucide-react';

export default function NewTDSChallanPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    financial_year: new Date().getFullYear().toString(),
    assessment_year: (new Date().getFullYear() + 1).toString(),
    quarter: 'Q1',
    payment_date: new Date().toISOString().split('T')[0],
    challan_number: '',
    bsr_code: '',
    bank_name: '',
    amount_paid: 0,
    interest: 0,
    late_fee: 0,
    total_amount: 0,
    section_code: '194A',
    nature_of_payment: '',
    remarks: '',
    status: 'paid'
  });

  const handleAmountChange = (field: 'amount_paid' | 'interest' | 'late_fee', value: number) => {
    const updated = { ...formData, [field]: value };
    updated.total_amount = updated.amount_paid + updated.interest + updated.late_fee;
    setFormData(updated);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    if (!formData.challan_number || formData.challan_number.length !== 5) {
      toast({
        title: "Validation Error",
        description: "Challan number must be 5 digits",
        variant: "destructive"
      });
      return;
    }

    if (!formData.bsr_code || formData.bsr_code.length !== 7) {
      toast({
        title: "Validation Error",
        description: "BSR code must be 7 digits",
        variant: "destructive"
      });
      return;
    }

    if (formData.amount_paid <= 0) {
      toast({
        title: "Validation Error",
        description: "Amount paid must be greater than zero",
        variant: "destructive"
      });
      return;
    }

    try {
      await tdsService.createChallan(formData);
      toast({
        title: "Success",
        description: "TDS challan recorded successfully"
      });
      router.push('/accounting/tds/challans');
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to record TDS challan",
        variant: "destructive"
      });
    }
  };

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" onClick={() => router.back()}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold">Record TDS Challan</h1>
          <p className="text-muted-foreground">Record TDS payment challan (Form 281)</p>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="grid gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Period Details</CardTitle>
              <CardDescription>Tax period for this payment</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
                  <Label htmlFor="assessment_year">Assessment Year *</Label>
                  <Select
                    value={formData.assessment_year}
                    onValueChange={(value) => setFormData({ ...formData, assessment_year: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="2025">AY 2025-26</SelectItem>
                      <SelectItem value="2024">AY 2024-25</SelectItem>
                      <SelectItem value="2023">AY 2023-24</SelectItem>
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
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Challan Details</CardTitle>
              <CardDescription>Bank challan information from Form 281</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="payment_date">Payment Date *</Label>
                  <Input
                    id="payment_date"
                    type="date"
                    value={formData.payment_date}
                    onChange={(e) => setFormData({ ...formData, payment_date: e.target.value })}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="challan_number">Challan Serial No. *</Label>
                  <Input
                    id="challan_number"
                    value={formData.challan_number}
                    onChange={(e) => setFormData({ ...formData, challan_number: e.target.value })}
                    placeholder="5-digit number"
                    maxLength={5}
                    required
                  />
                  <p className="text-xs text-muted-foreground">Last 5 digits of challan</p>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="bsr_code">BSR Code *</Label>
                  <Input
                    id="bsr_code"
                    value={formData.bsr_code}
                    onChange={(e) => setFormData({ ...formData, bsr_code: e.target.value })}
                    placeholder="7-digit code"
                    maxLength={7}
                    required
                  />
                  <p className="text-xs text-muted-foreground">Bank BSR code</p>
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="bank_name">Bank Name *</Label>
                <Input
                  id="bank_name"
                  value={formData.bank_name}
                  onChange={(e) => setFormData({ ...formData, bank_name: e.target.value })}
                  placeholder="Name of the bank"
                  required
                />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="section_code">TDS Section *</Label>
                  <Select
                    value={formData.section_code}
                    onValueChange={(value) => setFormData({ ...formData, section_code: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="194A">194A - Interest</SelectItem>
                      <SelectItem value="194C">194C - Contractor</SelectItem>
                      <SelectItem value="194H">194H - Commission</SelectItem>
                      <SelectItem value="194I">194I - Rent</SelectItem>
                      <SelectItem value="194J">194J - Professional Fees</SelectItem>
                      <SelectItem value="OTHER">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="nature_of_payment">Nature of Payment</Label>
                  <Input
                    id="nature_of_payment"
                    value={formData.nature_of_payment}
                    onChange={(e) => setFormData({ ...formData, nature_of_payment: e.target.value })}
                    placeholder="e.g., Interest on loan"
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Payment Amount</CardTitle>
              <CardDescription>Breakdown of payment</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="amount_paid">TDS Amount (₹) *</Label>
                  <Input
                    id="amount_paid"
                    type="number"
                    step="0.01"
                    value={formData.amount_paid}
                    onChange={(e) => handleAmountChange('amount_paid', parseFloat(e.target.value) || 0)}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="interest">Interest (₹)</Label>
                  <Input
                    id="interest"
                    type="number"
                    step="0.01"
                    value={formData.interest}
                    onChange={(e) => handleAmountChange('interest', parseFloat(e.target.value) || 0)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="late_fee">Late Fee (₹)</Label>
                  <Input
                    id="late_fee"
                    type="number"
                    step="0.01"
                    value={formData.late_fee}
                    onChange={(e) => handleAmountChange('late_fee', parseFloat(e.target.value) || 0)}
                  />
                </div>
              </div>

              <div className="p-4 bg-primary/10 rounded-lg">
                <div className="flex justify-between items-center">
                  <span className="text-lg font-semibold">Total Amount Paid</span>
                  <span className="text-2xl font-bold text-primary">
                    ₹{formData.total_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </span>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="remarks">Remarks</Label>
                <Input
                  id="remarks"
                  value={formData.remarks}
                  onChange={(e) => setFormData({ ...formData, remarks: e.target.value })}
                  placeholder="Any additional notes"
                />
              </div>
            </CardContent>
          </Card>

          <div className="flex justify-end gap-4">
            <Button type="button" variant="outline" onClick={() => router.back()}>
              Cancel
            </Button>
            <Button type="submit">
              <Save className="mr-2 h-4 w-4" />
              Record Challan
            </Button>
          </div>
        </div>
      </form>
    </div>
  );
}
