"use client";

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { gstService, type HSNSAC, type GSTConfiguration } from '@/services/accounting.service';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from '@/components/ui/use-toast';
import { ArrowLeft, Save, Plus, Trash2, Calculator } from 'lucide-react';

interface LineItem {
  description: string;
  hsn_sac_code: string;
  quantity: number;
  rate: number;
  taxable_amount: number;
  cgst_rate: number;
  sgst_rate: number;
  igst_rate: number;
  cgst_amount: number;
  sgst_amount: number;
  igst_amount: number;
  total_amount: number;
}

export default function NewGSTTransactionPage() {
  const router = useRouter();
  const [hsnSacCodes, setHsnSacCodes] = useState<HSNSAC[]>([]);
  const [configuration, setConfiguration] = useState<GSTConfiguration | null>(null);
  const [calculating, setCalculating] = useState(false);
  const [formData, setFormData] = useState({
    transaction_type: 'sale' as 'sale' | 'purchase',
    supply_type: 'B2B' as 'B2B' | 'B2C' | 'export' | 'import',
    invoice_date: new Date().toISOString().split('T')[0],
    invoice_number: '',
    party_name: '',
    party_gstin: '',
    party_state_code: '',
    place_of_supply: '',
    reverse_charge: false,
    taxable_amount: 0,
    cgst_amount: 0,
    sgst_amount: 0,
    igst_amount: 0,
    cess_amount: 0,
    total_amount: 0,
    remarks: ''
  });

  const [lineItems, setLineItems] = useState<LineItem[]>([
    {
      description: '',
      hsn_sac_code: '',
      quantity: 1,
      rate: 0,
      taxable_amount: 0,
      cgst_rate: 0,
      sgst_rate: 0,
      igst_rate: 0,
      cgst_amount: 0,
      sgst_amount: 0,
      igst_amount: 0,
      total_amount: 0
    }
  ]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [codes, configs] = await Promise.all([
        gstService.getHSNSAC(),
        gstService.getConfiguration()
      ]);
      setHsnSacCodes(codes.filter((c: HSNSAC) => c.is_active));
      if (configs.length > 0) {
        setConfiguration(configs[0]);
        setFormData(prev => ({ ...prev, place_of_supply: configs[0].state_code }));
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load configuration",
        variant: "destructive"
      });
    }
  };

  const addLineItem = () => {
    setLineItems([...lineItems, {
      description: '',
      hsn_sac_code: '',
      quantity: 1,
      rate: 0,
      taxable_amount: 0,
      cgst_rate: 0,
      sgst_rate: 0,
      igst_rate: 0,
      cgst_amount: 0,
      sgst_amount: 0,
      igst_amount: 0,
      total_amount: 0
    }]);
  };

  const removeLineItem = (index: number) => {
    if (lineItems.length === 1) {
      toast({
        title: "Warning",
        description: "At least one line item is required",
        variant: "destructive"
      });
      return;
    }
    const updated = lineItems.filter((_, i) => i !== index);
    setLineItems(updated);
    calculateTotals(updated);
  };

  const updateLineItem = (index: number, field: keyof LineItem, value: any) => {
    const updated = [...lineItems];
    updated[index] = { ...updated[index], [field]: value };

    // Auto-calculate when quantity or rate changes
    if (field === 'quantity' || field === 'rate') {
      updated[index].taxable_amount = updated[index].quantity * updated[index].rate;
    }

    // Update rates when HSN/SAC is selected
    if (field === 'hsn_sac_code') {
      const code = hsnSacCodes.find(c => c.code === value);
      if (code) {
        updated[index].cgst_rate = code.cgst_rate;
        updated[index].sgst_rate = code.sgst_rate;
        updated[index].igst_rate = code.igst_rate;
      }
    }

    setLineItems(updated);
  };

  const calculateTaxForLineItem = (item: LineItem, isInterstate: boolean): LineItem => {
    if (isInterstate) {
      // IGST applies
      item.igst_amount = (item.taxable_amount * item.igst_rate) / 100;
      item.cgst_amount = 0;
      item.sgst_amount = 0;
    } else {
      // CGST + SGST applies
      item.cgst_amount = (item.taxable_amount * item.cgst_rate) / 100;
      item.sgst_amount = (item.taxable_amount * item.sgst_rate) / 100;
      item.igst_amount = 0;
    }
    item.total_amount = item.taxable_amount + item.cgst_amount + item.sgst_amount + item.igst_amount;
    return item;
  };

  const calculateTotals = (items: LineItem[]) => {
    if (!configuration) return;

    const isInterstate = formData.party_state_code !== configuration.state_code;
    
    // Calculate tax for each line item
    const calculatedItems = items.map(item => calculateTaxForLineItem({ ...item }, isInterstate));
    setLineItems(calculatedItems);

    // Calculate totals
    const totals = calculatedItems.reduce((acc, item) => ({
      taxable_amount: acc.taxable_amount + item.taxable_amount,
      cgst_amount: acc.cgst_amount + item.cgst_amount,
      sgst_amount: acc.sgst_amount + item.sgst_amount,
      igst_amount: acc.igst_amount + item.igst_amount,
      total_amount: acc.total_amount + item.total_amount
    }), {
      taxable_amount: 0,
      cgst_amount: 0,
      sgst_amount: 0,
      igst_amount: 0,
      total_amount: 0
    });

    setFormData(prev => ({
      ...prev,
      ...totals
    }));
  };

  const handleCalculate = () => {
    if (!configuration) {
      toast({
        title: "Error",
        description: "GST configuration not found",
        variant: "destructive"
      });
      return;
    }

    // Validate line items
    for (let i = 0; i < lineItems.length; i++) {
      if (!lineItems[i].hsn_sac_code || lineItems[i].taxable_amount <= 0) {
        toast({
          title: "Validation Error",
          description: `Please complete line item ${i + 1}`,
          variant: "destructive"
        });
        return;
      }
    }

    calculateTotals(lineItems);
    toast({
      title: "Success",
      description: "GST calculated successfully"
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    if (!formData.party_gstin && formData.supply_type === 'B2B') {
      toast({
        title: "Validation Error",
        description: "GSTIN is required for B2B transactions",
        variant: "destructive"
      });
      return;
    }

    if (formData.total_amount <= 0) {
      toast({
        title: "Validation Error",
        description: "Please calculate GST before saving",
        variant: "destructive"
      });
      return;
    }

    try {
      await gstService.createTransaction({
        ...formData,
        line_items: lineItems
      });
      toast({
        title: "Success",
        description: "GST transaction created successfully"
      });
      router.push('/accounting/gst/transactions');
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create GST transaction",
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
          <h1 className="text-3xl font-bold">New GST Transaction</h1>
          <p className="text-muted-foreground">Create a new GST invoice or purchase entry</p>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="grid gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Transaction Details</CardTitle>
              <CardDescription>Basic invoice information</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="transaction_type">Transaction Type *</Label>
                  <Select
                    value={formData.transaction_type}
                    onValueChange={(value: 'sale' | 'purchase') => setFormData({ ...formData, transaction_type: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="sale">Sale (Outward Supply)</SelectItem>
                      <SelectItem value="purchase">Purchase (Inward Supply)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="supply_type">Supply Type *</Label>
                  <Select
                    value={formData.supply_type}
                    onValueChange={(value: any) => setFormData({ ...formData, supply_type: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="B2B">B2B (Business to Business)</SelectItem>
                      <SelectItem value="B2C">B2C (Business to Consumer)</SelectItem>
                      <SelectItem value="export">Export</SelectItem>
                      <SelectItem value="import">Import</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="invoice_date">Invoice Date *</Label>
                  <Input
                    id="invoice_date"
                    type="date"
                    value={formData.invoice_date}
                    onChange={(e) => setFormData({ ...formData, invoice_date: e.target.value })}
                    required
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="invoice_number">Invoice Number *</Label>
                <Input
                  id="invoice_number"
                  value={formData.invoice_number}
                  onChange={(e) => setFormData({ ...formData, invoice_number: e.target.value })}
                  placeholder="e.g., INV/2024/001"
                  required
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Party Details</CardTitle>
              <CardDescription>Customer or supplier information</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="party_name">Party Name *</Label>
                <Input
                  id="party_name"
                  value={formData.party_name}
                  onChange={(e) => setFormData({ ...formData, party_name: e.target.value })}
                  placeholder="Customer/Supplier name"
                  required
                />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="party_gstin">Party GSTIN {formData.supply_type === 'B2B' && '*'}</Label>
                  <Input
                    id="party_gstin"
                    value={formData.party_gstin}
                    onChange={(e) => {
                      const gstin = e.target.value.toUpperCase();
                      setFormData({ 
                        ...formData, 
                        party_gstin: gstin,
                        party_state_code: gstin.substring(0, 2)
                      });
                    }}
                    placeholder="15-character GSTIN"
                    maxLength={15}
                    required={formData.supply_type === 'B2B'}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="party_state_code">Party State *</Label>
                  <Input
                    id="party_state_code"
                    value={formData.party_state_code}
                    onChange={(e) => setFormData({ ...formData, party_state_code: e.target.value })}
                    placeholder="State code (e.g., 27)"
                    maxLength={2}
                    required
                  />
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="reverse_charge"
                  checked={formData.reverse_charge}
                  onChange={(e) => setFormData({ ...formData, reverse_charge: e.target.checked })}
                  className="h-4 w-4"
                />
                <Label htmlFor="reverse_charge">Reverse Charge Applicable</Label>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Line Items</CardTitle>
              <CardDescription>Add products or services</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {lineItems.map((item, index) => (
                <div key={index} className="p-4 border rounded-lg space-y-3">
                  <div className="flex justify-between items-center">
                    <h4 className="font-semibold">Item {index + 1}</h4>
                    {lineItems.length > 1 && (
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => removeLineItem(index)}
                      >
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    )}
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div className="space-y-2">
                      <Label>Description *</Label>
                      <Input
                        value={item.description}
                        onChange={(e) => updateLineItem(index, 'description', e.target.value)}
                        placeholder="Product/service description"
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>HSN/SAC Code *</Label>
                      <Select
                        value={item.hsn_sac_code}
                        onValueChange={(value) => updateLineItem(index, 'hsn_sac_code', value)}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select code" />
                        </SelectTrigger>
                        <SelectContent>
                          {hsnSacCodes.map((code) => (
                            <SelectItem key={code.id} value={code.code}>
                              {code.code} - {code.description} ({code.cgst_rate + code.sgst_rate}%)
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <div className="space-y-2">
                      <Label>Quantity *</Label>
                      <Input
                        type="number"
                        step="0.01"
                        value={item.quantity}
                        onChange={(e) => updateLineItem(index, 'quantity', parseFloat(e.target.value) || 0)}
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Rate (₹) *</Label>
                      <Input
                        type="number"
                        step="0.01"
                        value={item.rate}
                        onChange={(e) => updateLineItem(index, 'rate', parseFloat(e.target.value) || 0)}
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Taxable Amount</Label>
                      <Input
                        type="number"
                        value={item.taxable_amount.toFixed(2)}
                        readOnly
                        className="bg-muted"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Total</Label>
                      <Input
                        type="number"
                        value={item.total_amount.toFixed(2)}
                        readOnly
                        className="bg-muted font-semibold"
                      />
                    </div>
                  </div>
                </div>
              ))}
              <Button type="button" variant="outline" onClick={addLineItem} className="w-full">
                <Plus className="mr-2 h-4 w-4" />
                Add Line Item
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Tax Calculation</CardTitle>
              <CardDescription>Calculate GST before saving</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-end">
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleCalculate}
                  disabled={calculating}
                >
                  <Calculator className="mr-2 h-4 w-4" />
                  Calculate GST
                </Button>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-5 gap-4 p-4 bg-muted rounded-lg">
                <div>
                  <p className="text-sm text-muted-foreground">Taxable Amount</p>
                  <p className="text-xl font-bold">₹{formData.taxable_amount.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">CGST</p>
                  <p className="text-xl font-bold">₹{formData.cgst_amount.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">SGST</p>
                  <p className="text-xl font-bold">₹{formData.sgst_amount.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">IGST</p>
                  <p className="text-xl font-bold">₹{formData.igst_amount.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Total Amount</p>
                  <p className="text-xl font-bold text-primary">₹{formData.total_amount.toFixed(2)}</p>
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
            <Button type="submit" disabled={!formData.total_amount}>
              <Save className="mr-2 h-4 w-4" />
              Save Transaction
            </Button>
          </div>
        </div>
      </form>
    </div>
  );
}
