"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { assetService, type AssetCategory, type DepreciationMethod } from '@/services/accounting.service';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { toast } from '@/components/ui/use-toast';
import { ArrowLeft, Save, Calculator } from 'lucide-react';

export default function NewAssetPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    asset_name: '',
    category: '' as AssetCategory,
    purchase_date: new Date().toISOString().split('T')[0],
    purchase_cost: 0,
    depreciation_method: 'STRAIGHT_LINE' as DepreciationMethod,
    depreciation_rate: 0,
    useful_life_years: 5,
    useful_life_months: 0,
    salvage_value: 0,
    description: '',
    location: '',
    department: '',
    custodian: '',
    vendor_name: '',
    invoice_number: ''
  });

  const [calculating, setCalculating] = useState(false);

  const handleCalculateDepreciation = () => {
    if (!formData.purchase_cost || !formData.useful_life_years) {
      toast({
        title: "Validation Error",
        description: "Please enter purchase cost and useful life",
        variant: "destructive"
      });
      return;
    }

    setCalculating(true);
    
    if (formData.depreciation_method === 'STRAIGHT_LINE') {
      // SLM: (Cost - Salvage) / Life
      const depreciableAmount = formData.purchase_cost - formData.salvage_value;
      const totalMonths = formData.useful_life_years * 12 + formData.useful_life_months;
      const annualDepreciation = (depreciableAmount / totalMonths) * 12;
      const rate = (annualDepreciation / formData.purchase_cost) * 100;
      setFormData({ ...formData, depreciation_rate: Math.round(rate * 100) / 100 });
    } else {
      // Common WDV rates
      const suggestedRates: Record<string, number> = {
        'BUILDING': 5,
        'PLANT_MACHINERY': 15,
        'FURNITURE_FIXTURES': 10,
        'OFFICE_EQUIPMENT': 15,
        'COMPUTERS': 40,
        'VEHICLES': 15,
        'SOFTWARE': 60
      };
      const rate = suggestedRates[formData.category] || 10;
      setFormData({ ...formData, depreciation_rate: rate });
    }

    setCalculating(false);
    toast({
      title: "Success",
      description: "Depreciation rate calculated"
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.category) {
      toast({
        title: "Validation Error",
        description: "Please select asset category",
        variant: "destructive"
      });
      return;
    }

    if (formData.purchase_cost <= 0) {
      toast({
        title: "Validation Error",
        description: "Purchase cost must be greater than zero",
        variant: "destructive"
      });
      return;
    }

    if (formData.depreciation_rate <= 0) {
      toast({
        title: "Validation Error",
        description: "Please calculate or enter depreciation rate",
        variant: "destructive"
      });
      return;
    }

    try {
      await assetService.createAsset(formData);
      toast({
        title: "Success",
        description: "Asset created successfully"
      });
      router.push('/accounting/assets/list');
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create asset",
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
          <h1 className="text-3xl font-bold">Add New Asset</h1>
          <p className="text-muted-foreground">Create a new fixed asset record</p>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="grid gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Basic Information</CardTitle>
              <CardDescription>Asset identification and category</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="asset_name">Asset Name *</Label>
                  <Input
                    id="asset_name"
                    value={formData.asset_name}
                    onChange={(e) => setFormData({ ...formData, asset_name: e.target.value })}
                    placeholder="e.g., Dell Laptop - XPS 15"
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="category">Category *</Label>
                  <Select
                    value={formData.category}
                    onValueChange={(value: AssetCategory) => setFormData({ ...formData, category: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select category" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="LAND">Land</SelectItem>
                      <SelectItem value="BUILDING">Building</SelectItem>
                      <SelectItem value="PLANT_MACHINERY">Plant & Machinery</SelectItem>
                      <SelectItem value="FURNITURE_FIXTURES">Furniture & Fixtures</SelectItem>
                      <SelectItem value="OFFICE_EQUIPMENT">Office Equipment</SelectItem>
                      <SelectItem value="COMPUTERS">Computers</SelectItem>
                      <SelectItem value="VEHICLES">Vehicles</SelectItem>
                      <SelectItem value="SOFTWARE">Software</SelectItem>
                      <SelectItem value="INTANGIBLE">Intangible Assets</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Brief description of the asset"
                  rows={2}
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Purchase Details</CardTitle>
              <CardDescription>Cost and vendor information</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="purchase_date">Purchase Date *</Label>
                  <Input
                    id="purchase_date"
                    type="date"
                    value={formData.purchase_date}
                    onChange={(e) => setFormData({ ...formData, purchase_date: e.target.value })}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="purchase_cost">Purchase Cost (₹) *</Label>
                  <Input
                    id="purchase_cost"
                    type="number"
                    step="0.01"
                    value={formData.purchase_cost}
                    onChange={(e) => setFormData({ ...formData, purchase_cost: parseFloat(e.target.value) || 0 })}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="salvage_value">Salvage Value (₹)</Label>
                  <Input
                    id="salvage_value"
                    type="number"
                    step="0.01"
                    value={formData.salvage_value}
                    onChange={(e) => setFormData({ ...formData, salvage_value: parseFloat(e.target.value) || 0 })}
                  />
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="vendor_name">Vendor Name</Label>
                  <Input
                    id="vendor_name"
                    value={formData.vendor_name}
                    onChange={(e) => setFormData({ ...formData, vendor_name: e.target.value })}
                    placeholder="Supplier name"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="invoice_number">Invoice Number</Label>
                  <Input
                    id="invoice_number"
                    value={formData.invoice_number}
                    onChange={(e) => setFormData({ ...formData, invoice_number: e.target.value })}
                    placeholder="Purchase invoice number"
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Depreciation Setup</CardTitle>
              <CardDescription>Configure depreciation calculation</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="depreciation_method">Depreciation Method *</Label>
                  <Select
                    value={formData.depreciation_method}
                    onValueChange={(value: DepreciationMethod) => setFormData({ ...formData, depreciation_method: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="STRAIGHT_LINE">Straight Line Method (SLM)</SelectItem>
                      <SelectItem value="WRITTEN_DOWN_VALUE">Written Down Value (WDV)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="depreciation_rate">Depreciation Rate (%) *</Label>
                  <Input
                    id="depreciation_rate"
                    type="number"
                    step="0.01"
                    value={formData.depreciation_rate}
                    onChange={(e) => setFormData({ ...formData, depreciation_rate: parseFloat(e.target.value) || 0 })}
                    required
                  />
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="useful_life_years">Useful Life (Years) *</Label>
                  <Input
                    id="useful_life_years"
                    type="number"
                    value={formData.useful_life_years}
                    onChange={(e) => setFormData({ ...formData, useful_life_years: parseInt(e.target.value) || 0 })}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="useful_life_months">Additional Months</Label>
                  <Input
                    id="useful_life_months"
                    type="number"
                    min="0"
                    max="11"
                    value={formData.useful_life_months}
                    onChange={(e) => setFormData({ ...formData, useful_life_months: parseInt(e.target.value) || 0 })}
                  />
                </div>
              </div>
              <div className="flex justify-end">
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleCalculateDepreciation}
                  disabled={calculating}
                >
                  <Calculator className="mr-2 h-4 w-4" />
                  {calculating ? 'Calculating...' : 'Calculate Rate'}
                </Button>
              </div>
              <div className="p-4 bg-muted rounded-lg">
                <p className="text-sm text-muted-foreground mb-2">Estimated Annual Depreciation:</p>
                <p className="text-2xl font-bold">
                  ₹{((formData.purchase_cost - formData.salvage_value) * formData.depreciation_rate / 100).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Location & Assignment</CardTitle>
              <CardDescription>Where is this asset located and who manages it</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="location">Location</Label>
                  <Input
                    id="location"
                    value={formData.location}
                    onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                    placeholder="e.g., Head Office, Branch 1"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="department">Department</Label>
                  <Input
                    id="department"
                    value={formData.department}
                    onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                    placeholder="e.g., IT, Finance, Operations"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="custodian">Custodian</Label>
                  <Input
                    id="custodian"
                    value={formData.custodian}
                    onChange={(e) => setFormData({ ...formData, custodian: e.target.value })}
                    placeholder="Person responsible"
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="flex justify-end gap-4">
            <Button type="button" variant="outline" onClick={() => router.back()}>
              Cancel
            </Button>
            <Button type="submit" disabled={!formData.depreciation_rate}>
              <Save className="mr-2 h-4 w-4" />
              Create Asset
            </Button>
          </div>
        </div>
      </form>
    </div>
  );
}
