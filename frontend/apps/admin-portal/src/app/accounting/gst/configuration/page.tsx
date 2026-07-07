"use client";

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { gstService, type GSTConfiguration } from '@/services/accounting.service';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from '@/components/ui/use-toast';
import { ArrowLeft, Save, CheckCircle, AlertCircle } from 'lucide-react';

export default function GSTConfigurationPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [configurations, setConfigurations] = useState<GSTConfiguration[]>([]);
  const [formData, setFormData] = useState({
    gstin: '',
    legal_name: '',
    trade_name: '',
    registration_date: '',
    state_code: '',
    state_name: '',
    business_type: 'regular',
    composition_scheme: false,
    is_active: true,
    gst_portal_username: '',
    filing_frequency: 'monthly'
  });

  useEffect(() => {
    loadConfiguration();
  }, []);

  const loadConfiguration = async () => {
    try {
      setLoading(true);
      const data = await gstService.getConfiguration();
      setConfigurations(data);
      
      // Load first active configuration if exists
      if (data.length > 0) {
        const active = data.find((c: GSTConfiguration) => c.is_active) || data[0];
        setFormData({
          gstin: active.gstin,
          legal_name: active.legal_name,
          trade_name: active.trade_name || '',
          registration_date: active.registration_date.split('T')[0],
          state_code: active.state_code,
          state_name: active.state_name,
          business_type: active.business_type,
          composition_scheme: active.composition_scheme,
          is_active: active.is_active,
          gst_portal_username: active.gst_portal_username || '',
          filing_frequency: active.filing_frequency
        });
      }
    } catch (error) {
      console.error('Failed to load configuration', error);
    } finally {
      setLoading(false);
    }
  };

  const validateGSTIN = (gstin: string): boolean => {
    const gstinRegex = /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/;
    return gstinRegex.test(gstin);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    if (!validateGSTIN(formData.gstin)) {
      toast({
        title: "Validation Error",
        description: "Please enter a valid 15-character GSTIN",
        variant: "destructive"
      });
      return;
    }

    if (!formData.legal_name || !formData.state_code) {
      toast({
        title: "Validation Error",
        description: "Please fill all required fields",
        variant: "destructive"
      });
      return;
    }

    try {
      setSaving(true);
      if (configurations.length > 0) {
        await gstService.updateConfiguration(configurations[0].id, formData);
        toast({
          title: "Success",
          description: "GST configuration updated successfully"
        });
      } else {
        await gstService.createConfiguration(formData);
        toast({
          title: "Success",
          description: "GST configuration created successfully"
        });
      }
      loadConfiguration();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to save GST configuration",
        variant: "destructive"
      });
    } finally {
      setSaving(false);
    }
  };

  const stateOptions = [
    { code: '01', name: 'Jammu and Kashmir' },
    { code: '02', name: 'Himachal Pradesh' },
    { code: '03', name: 'Punjab' },
    { code: '04', name: 'Chandigarh' },
    { code: '05', name: 'Uttarakhand' },
    { code: '06', name: 'Haryana' },
    { code: '07', name: 'Delhi' },
    { code: '08', name: 'Rajasthan' },
    { code: '09', name: 'Uttar Pradesh' },
    { code: '10', name: 'Bihar' },
    { code: '19', name: 'West Bengal' },
    { code: '20', name: 'Jharkhand' },
    { code: '21', name: 'Odisha' },
    { code: '22', name: 'Chhattisgarh' },
    { code: '23', name: 'Madhya Pradesh' },
    { code: '24', name: 'Gujarat' },
    { code: '27', name: 'Maharashtra' },
    { code: '29', name: 'Karnataka' },
    { code: '32', name: 'Kerala' },
    { code: '33', name: 'Tamil Nadu' },
    { code: '36', name: 'Telangana' },
    { code: '37', name: 'Andhra Pradesh' }
  ];

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" onClick={() => router.back()}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold">GST Configuration</h1>
          <p className="text-muted-foreground">Configure your GST registration details</p>
        </div>
      </div>

      {configurations.length > 0 && (
        <Card className="bg-green-50 dark:bg-green-950 border-green-200">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <span className="font-semibold text-green-900 dark:text-green-100">
                GST Configuration Active
              </span>
            </div>
            <p className="text-sm text-green-700 dark:text-green-300 mt-1">
              GSTIN: {configurations[0].gstin} - {configurations[0].legal_name}
            </p>
          </CardContent>
        </Card>
      )}

      <form onSubmit={handleSubmit}>
        <div className="grid gap-6">
          <Card>
            <CardHeader>
              <CardTitle>GST Registration Details</CardTitle>
              <CardDescription>Your GST registration information</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="gstin">GSTIN *</Label>
                <Input
                  id="gstin"
                  value={formData.gstin}
                  onChange={(e) => setFormData({ ...formData, gstin: e.target.value.toUpperCase() })}
                  placeholder="15-character GSTIN (e.g., 27AABCT1234C1Z5)"
                  maxLength={15}
                  required
                />
                {formData.gstin && !validateGSTIN(formData.gstin) && (
                  <p className="text-sm text-destructive flex items-center gap-1">
                    <AlertCircle className="h-3 w-3" />
                    Invalid GSTIN format
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="legal_name">Legal Name *</Label>
                <Input
                  id="legal_name"
                  value={formData.legal_name}
                  onChange={(e) => setFormData({ ...formData, legal_name: e.target.value })}
                  placeholder="Legal name as per GST certificate"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="trade_name">Trade Name</Label>
                <Input
                  id="trade_name"
                  value={formData.trade_name}
                  onChange={(e) => setFormData({ ...formData, trade_name: e.target.value })}
                  placeholder="Trade name (if different)"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="registration_date">Registration Date *</Label>
                  <Input
                    id="registration_date"
                    type="date"
                    value={formData.registration_date}
                    onChange={(e) => setFormData({ ...formData, registration_date: e.target.value })}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="state">State *</Label>
                  <Select
                    value={formData.state_code}
                    onValueChange={(value) => {
                      const state = stateOptions.find(s => s.code === value);
                      setFormData({ 
                        ...formData, 
                        state_code: value,
                        state_name: state?.name || ''
                      });
                    }}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select state" />
                    </SelectTrigger>
                    <SelectContent>
                      {stateOptions.map((state) => (
                        <SelectItem key={state.code} value={state.code}>
                          {state.code} - {state.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Business Configuration</CardTitle>
              <CardDescription>GST compliance settings</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="business_type">Business Type *</Label>
                  <Select
                    value={formData.business_type}
                    onValueChange={(value) => setFormData({ ...formData, business_type: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="regular">Regular</SelectItem>
                      <SelectItem value="composition">Composition</SelectItem>
                      <SelectItem value="casual">Casual Taxable Person</SelectItem>
                      <SelectItem value="sez">SEZ Unit</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="filing_frequency">Filing Frequency *</Label>
                  <Select
                    value={formData.filing_frequency}
                    onValueChange={(value) => setFormData({ ...formData, filing_frequency: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="monthly">Monthly</SelectItem>
                      <SelectItem value="quarterly">Quarterly</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="composition_scheme"
                  checked={formData.composition_scheme}
                  onChange={(e) => setFormData({ ...formData, composition_scheme: e.target.checked })}
                  className="h-4 w-4"
                />
                <Label htmlFor="composition_scheme">Under Composition Scheme</Label>
              </div>

              <div className="space-y-2">
                <Label htmlFor="gst_portal_username">GST Portal Username</Label>
                <Input
                  id="gst_portal_username"
                  value={formData.gst_portal_username}
                  onChange={(e) => setFormData({ ...formData, gst_portal_username: e.target.value })}
                  placeholder="Username for GST portal"
                />
                <p className="text-xs text-muted-foreground">
                  For future integration with GST portal APIs
                </p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Important Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm text-muted-foreground">
              <div className="flex items-start gap-2">
                <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                <p>
                  Ensure all details match exactly with your GST certificate to avoid compliance issues.
                </p>
              </div>
              <div className="flex items-start gap-2">
                <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                <p>
                  GSTIN format: First 2 digits (State Code) + Next 10 digits (PAN) + Next 2 digits (Entity Number) + Check digit
                </p>
              </div>
              <div className="flex items-start gap-2">
                <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                <p>
                  Changes to state code or GSTIN may require re-validation of existing transactions.
                </p>
              </div>
            </CardContent>
          </Card>

          <div className="flex justify-end gap-4">
            <Button type="button" variant="outline" onClick={() => router.back()}>
              Cancel
            </Button>
            <Button type="submit" disabled={saving || !validateGSTIN(formData.gstin)}>
              <Save className="mr-2 h-4 w-4" />
              {saving ? 'Saving...' : 'Save Configuration'}
            </Button>
          </div>
        </div>
      </form>
    </div>
  );
}
