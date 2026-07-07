"use client";

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { tdsService, type TDSSection } from '@/services/accounting.service';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from '@/components/ui/use-toast';
import { ArrowLeft, Save, Calculator } from 'lucide-react';

export default function NewTDSDeductionPage() {
  const router = useRouter();
  const [sections, setSections] = useState<TDSSection[]>([]);
  const [selectedSection, setSelectedSection] = useState<TDSSection | null>(null);
  const [calculating, setCalculating] = useState(false);
  const [formData, setFormData] = useState({
    financial_year: new Date().getFullYear().toString(),
    quarter: 'Q1',
    deduction_date: new Date().toISOString().split('T')[0],
    voucher_number: '',
    deductee_name: '',
    deductee_pan: '',
    deductee_tan: '',
    section_id: 0,
    section_code: '',
    taxable_amount: 0,
    tds_rate: 0,
    tds_amount: 0,
    surcharge: 0,
    cess: 0,
    total_tds: 0,
    payment_reference: '',
    remarks: '',
    status: 'deducted'
  });

  useEffect(() => {
    loadSections();
  }, []);

  const loadSections = async () => {
    try {
      const currentYear = new Date().getFullYear();
      const response = await tdsService.getSections(currentYear);
      setSections(response.data.data.sections.filter((s: TDSSection) => s.is_active));
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load TDS sections",
        variant: "destructive"
      });
    }
  };

  const handleSectionChange = (sectionId: string) => {
    const section = sections.find(s => s.id === parseInt(sectionId));
    if (section) {
      setSelectedSection(section);
      setFormData({
        ...formData,
        section_id: section.id,
        section_code: section.section_code,
        tds_rate: section.tds_rate
      });
    }
  };

  const handleCalculateTDS = async () => {
    if (!formData.taxable_amount || !formData.section_code) {
      toast({
        title: "Validation Error",
        description: "Please enter taxable amount and select section",
        variant: "destructive"
      });
      return;
    }

    try {
      setCalculating(true);
      const result = await tdsService.calculateTDS({
        section_code: formData.section_code,
        taxable_amount: formData.taxable_amount,
        deductee_type: 'individual', // Can be made dynamic
        has_pan: !!formData.deductee_pan
      });

      setFormData({
        ...formData,
        tds_amount: result.tds_amount,
        surcharge: result.surcharge || 0,
        cess: result.cess || 0,
        total_tds: result.total_amount
      });

      toast({
        title: "Success",
        description: "TDS calculated successfully"
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to calculate TDS",
        variant: "destructive"
      });
    } finally {
      setCalculating(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    if (!formData.deductee_pan || formData.deductee_pan.length !== 10) {
      toast({
        title: "Validation Error",
        description: "Please enter valid 10-character PAN",
        variant: "destructive"
      });
      return;
    }

    if (formData.taxable_amount <= 0) {
      toast({
        title: "Validation Error",
        description: "Taxable amount must be greater than zero",
        variant: "destructive"
      });
      return;
    }

    try {
      await tdsService.createDeduction(formData);
      toast({
        title: "Success",
        description: "TDS deduction recorded successfully"
      });
      router.push('/accounting/tds/deductions');
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to record TDS deduction",
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
          <h1 className="text-3xl font-bold">Record TDS Deduction</h1>
          <p className="text-muted-foreground">Create a new TDS deduction entry</p>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="grid gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Deduction Details</CardTitle>
              <CardDescription>Enter basic deduction information</CardDescription>
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
                <div className="space-y-2">
                  <Label htmlFor="deduction_date">Deduction Date *</Label>
                  <Input
                    id="deduction_date"
                    type="date"
                    value={formData.deduction_date}
                    onChange={(e) => setFormData({ ...formData, deduction_date: e.target.value })}
                    required
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="voucher_number">Voucher Number *</Label>
                <Input
                  id="voucher_number"
                  value={formData.voucher_number}
                  onChange={(e) => setFormData({ ...formData, voucher_number: e.target.value })}
                  placeholder="e.g., TDS/2024/001"
                  required
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Deductee Information</CardTitle>
              <CardDescription>Details of the person/entity from whom TDS is deducted</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="deductee_name">Deductee Name *</Label>
                <Input
                  id="deductee_name"
                  value={formData.deductee_name}
                  onChange={(e) => setFormData({ ...formData, deductee_name: e.target.value })}
                  placeholder="Full name as per PAN"
                  required
                />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="deductee_pan">PAN *</Label>
                  <Input
                    id="deductee_pan"
                    value={formData.deductee_pan}
                    onChange={(e) => setFormData({ ...formData, deductee_pan: e.target.value.toUpperCase() })}
                    placeholder="ABCDE1234F"
                    maxLength={10}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="deductee_tan">TAN (if applicable)</Label>
                  <Input
                    id="deductee_tan"
                    value={formData.deductee_tan}
                    onChange={(e) => setFormData({ ...formData, deductee_tan: e.target.value.toUpperCase() })}
                    placeholder="ABCD12345E"
                    maxLength={10}
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>TDS Calculation</CardTitle>
              <CardDescription>Calculate TDS based on section and taxable amount</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="section">TDS Section *</Label>
                  <Select
                    value={formData.section_id.toString()}
                    onValueChange={handleSectionChange}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select section" />
                    </SelectTrigger>
                    <SelectContent>
                      {sections.map((section) => (
                        <SelectItem key={section.id} value={section.id.toString()}>
                          {section.section_code} - {section.section_name} ({section.tds_rate}%)
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="taxable_amount">Taxable Amount (₹) *</Label>
                  <Input
                    id="taxable_amount"
                    type="number"
                    step="0.01"
                    value={formData.taxable_amount}
                    onChange={(e) => setFormData({ ...formData, taxable_amount: parseFloat(e.target.value) || 0 })}
                    required
                  />
                </div>
              </div>

              <div className="flex justify-end">
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleCalculateTDS}
                  disabled={calculating || !formData.section_id || !formData.taxable_amount}
                >
                  <Calculator className="mr-2 h-4 w-4" />
                  {calculating ? 'Calculating...' : 'Calculate TDS'}
                </Button>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-muted rounded-lg">
                <div>
                  <p className="text-sm text-muted-foreground">TDS Rate</p>
                  <p className="text-xl font-bold">{formData.tds_rate}%</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">TDS Amount</p>
                  <p className="text-xl font-bold">₹{formData.tds_amount.toLocaleString('en-IN')}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Surcharge + Cess</p>
                  <p className="text-xl font-bold">₹{(formData.surcharge + formData.cess).toLocaleString('en-IN')}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Total TDS</p>
                  <p className="text-xl font-bold text-primary">₹{formData.total_tds.toLocaleString('en-IN')}</p>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="payment_reference">Payment Reference</Label>
                <Input
                  id="payment_reference"
                  value={formData.payment_reference}
                  onChange={(e) => setFormData({ ...formData, payment_reference: e.target.value })}
                  placeholder="Transaction/payment reference"
                />
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
            <Button type="submit" disabled={!formData.total_tds}>
              <Save className="mr-2 h-4 w-4" />
              Record Deduction
            </Button>
          </div>
        </div>
      </form>
    </div>
  );
}
