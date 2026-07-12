/**
 * Vendor Form Component
 * Form for creating and editing vendor information
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Save, X } from 'lucide-react';
import { procurementService } from '@/services/procurement.service';
import type { Vendor, VendorType, VendorStatus, PaymentTerms } from '@/types/procurement';

interface VendorFormProps {
  vendor?: Vendor;
  onSuccess?: () => void;
  onCancel?: () => void;
}

interface VendorFormData {
  vendor_name: string;
  vendor_type: VendorType;
  contact_person: string;
  email: string;
  phone: string;
  mobile: string;
  website: string;
  address_line1: string;
  address_line2: string;
  city: string;
  state: string;
  country: string;
  pincode: string;
  gst_number: string;
  pan_number: string;
  tan_number: string;
  msme_registration: string;
  credit_limit: number;
  credit_period_days: number;
  payment_terms: PaymentTerms;
  bank_name: string;
  bank_branch: string;
  account_number: string;
  ifsc_code: string;
  account_holder_name: string;
  products_services: string;
  notes: string;
  status: VendorStatus;
}

export default function VendorForm({ vendor, onSuccess, onCancel }: VendorFormProps) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const [formData, setFormData] = useState<VendorFormData>({
    vendor_name: vendor?.vendor_name || '',
    vendor_type: vendor?.vendor_type || 'goods',
    contact_person: vendor?.contact_person || '',
    email: vendor?.email || '',
    phone: vendor?.phone || '',
    mobile: vendor?.mobile || '',
    website: vendor?.website || '',
    address_line1: vendor?.address_line1 || '',
    address_line2: vendor?.address_line2 || '',
    city: vendor?.city || '',
    state: vendor?.state || '',
    country: vendor?.country || 'India',
    pincode: vendor?.pincode || '',
    gst_number: vendor?.gst_number || '',
    pan_number: vendor?.pan_number || '',
    tan_number: vendor?.tan_number || '',
    msme_registration: vendor?.msme_registration || '',
    credit_limit: vendor?.credit_limit || 0,
    credit_period_days: vendor?.credit_period_days || 30,
    payment_terms: vendor?.payment_terms || 'net_30',
    bank_name: vendor?.bank_name || '',
    bank_branch: vendor?.bank_branch || '',
    account_number: vendor?.account_number || '',
    ifsc_code: vendor?.ifsc_code || '',
    account_holder_name: vendor?.account_holder_name || '',
    products_services: vendor?.products_services || '',
    notes: vendor?.notes || '',
    status: vendor?.status || 'active',
  });

  const handleChange = (
    field: keyof VendorFormData,
    value: string | number
  ) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear error for this field
    if (errors[field]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.vendor_name.trim()) {
      newErrors.vendor_name = 'Vendor name is required';
    }
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Invalid email format';
    }
    if (!formData.phone.trim()) {
      newErrors.phone = 'Phone is required';
    }
    if (formData.gst_number && !/^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/.test(formData.gst_number)) {
      newErrors.gst_number = 'Invalid GST number format';
    }
    if (formData.pan_number && !/^[A-Z]{5}[0-9]{4}[A-Z]{1}$/.test(formData.pan_number)) {
      newErrors.pan_number = 'Invalid PAN number format';
    }
    if (formData.credit_limit < 0) {
      newErrors.credit_limit = 'Credit limit cannot be negative';
    }
    if (formData.credit_period_days < 0) {
      newErrors.credit_period_days = 'Credit period cannot be negative';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      setLoading(true);
      let response;

      if (vendor?.id) {
        // Update existing vendor
        response = await procurementService.vendor.update(vendor.id, formData);
      } else {
        // Create new vendor
        response = await procurementService.vendor.create(formData);
      }

      if (response.success) {
        if (onSuccess) {
          onSuccess();
        } else {
          router.push('/procurement/vendors');
        }
      } else {
        setErrors({ submit: response.message || 'Failed to save vendor' });
      }
    } catch (error) {
      console.error('Failed to save vendor:', error);
      setErrors({ submit: 'An error occurred while saving the vendor' });
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    if (onCancel) {
      onCancel();
    } else {
      router.push('/procurement/vendors');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {errors.submit && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {errors.submit}
        </div>
      )}

      {/* Basic Information */}
      <Card>
        <CardHeader>
          <CardTitle>Basic Information</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="vendor_name">
              Vendor Name <span className="text-red-500">*</span>
            </Label>
            <Input
              id="vendor_name"
              value={formData.vendor_name}
              onChange={(e) => handleChange('vendor_name', e.target.value)}
              placeholder="Enter vendor name"
              className={errors.vendor_name ? 'border-red-500' : ''}
            />
            {errors.vendor_name && (
              <p className="text-sm text-red-500">{errors.vendor_name}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="vendor_type">Vendor Type</Label>
            <Select
              value={formData.vendor_type}
              onValueChange={(value) => handleChange('vendor_type', value)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="goods">Goods</SelectItem>
                <SelectItem value="services">Services</SelectItem>
                <SelectItem value="both">Both</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="status">Status</Label>
            <Select
              value={formData.status}
              onValueChange={(value) => handleChange('status', value)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="inactive">Inactive</SelectItem>
                <SelectItem value="under_review">Under Review</SelectItem>
                <SelectItem value="suspended">Suspended</SelectItem>
                <SelectItem value="blacklisted">Blacklisted</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="products_services">Products/Services</Label>
            <Input
              id="products_services"
              value={formData.products_services}
              onChange={(e) => handleChange('products_services', e.target.value)}
              placeholder="Brief description"
            />
          </div>
        </CardContent>
      </Card>

      {/* Contact Information */}
      <Card>
        <CardHeader>
          <CardTitle>Contact Information</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="contact_person">Contact Person</Label>
            <Input
              id="contact_person"
              value={formData.contact_person}
              onChange={(e) => handleChange('contact_person', e.target.value)}
              placeholder="Contact person name"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="email">
              Email <span className="text-red-500">*</span>
            </Label>
            <Input
              id="email"
              type="email"
              value={formData.email}
              onChange={(e) => handleChange('email', e.target.value)}
              placeholder="vendor@example.com"
              className={errors.email ? 'border-red-500' : ''}
            />
            {errors.email && (
              <p className="text-sm text-red-500">{errors.email}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="phone">
              Phone <span className="text-red-500">*</span>
            </Label>
            <Input
              id="phone"
              value={formData.phone}
              onChange={(e) => handleChange('phone', e.target.value)}
              placeholder="+91-XXX-XXXXXXX"
              className={errors.phone ? 'border-red-500' : ''}
            />
            {errors.phone && (
              <p className="text-sm text-red-500">{errors.phone}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="mobile">Mobile</Label>
            <Input
              id="mobile"
              value={formData.mobile}
              onChange={(e) => handleChange('mobile', e.target.value)}
              placeholder="+91-XXXXXXXXXX"
            />
          </div>

          <div className="space-y-2 md:col-span-2">
            <Label htmlFor="website">Website</Label>
            <Input
              id="website"
              type="url"
              value={formData.website}
              onChange={(e) => handleChange('website', e.target.value)}
              placeholder="https://www.example.com"
            />
          </div>
        </CardContent>
      </Card>

      {/* Address */}
      <Card>
        <CardHeader>
          <CardTitle>Address</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2 md:col-span-2">
            <Label htmlFor="address_line1">Address Line 1</Label>
            <Input
              id="address_line1"
              value={formData.address_line1}
              onChange={(e) => handleChange('address_line1', e.target.value)}
              placeholder="Street address"
            />
          </div>

          <div className="space-y-2 md:col-span-2">
            <Label htmlFor="address_line2">Address Line 2</Label>
            <Input
              id="address_line2"
              value={formData.address_line2}
              onChange={(e) => handleChange('address_line2', e.target.value)}
              placeholder="Apartment, suite, etc. (optional)"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="city">City</Label>
            <Input
              id="city"
              value={formData.city}
              onChange={(e) => handleChange('city', e.target.value)}
              placeholder="City"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="state">State</Label>
            <Input
              id="state"
              value={formData.state}
              onChange={(e) => handleChange('state', e.target.value)}
              placeholder="State"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="pincode">Pincode</Label>
            <Input
              id="pincode"
              value={formData.pincode}
              onChange={(e) => handleChange('pincode', e.target.value)}
              placeholder="XXXXXX"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="country">Country</Label>
            <Input
              id="country"
              value={formData.country}
              onChange={(e) => handleChange('country', e.target.value)}
              placeholder="Country"
            />
          </div>
        </CardContent>
      </Card>

      {/* Tax & Compliance */}
      <Card>
        <CardHeader>
          <CardTitle>Tax & Compliance</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="gst_number">GST Number</Label>
            <Input
              id="gst_number"
              value={formData.gst_number}
              onChange={(e) => handleChange('gst_number', e.target.value.toUpperCase())}
              placeholder="22AAAAA0000A1Z5"
              maxLength={15}
              className={errors.gst_number ? 'border-red-500' : ''}
            />
            {errors.gst_number && (
              <p className="text-sm text-red-500">{errors.gst_number}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="pan_number">PAN Number</Label>
            <Input
              id="pan_number"
              value={formData.pan_number}
              onChange={(e) => handleChange('pan_number', e.target.value.toUpperCase())}
              placeholder="AAAAA0000A"
              maxLength={10}
              className={errors.pan_number ? 'border-red-500' : ''}
            />
            {errors.pan_number && (
              <p className="text-sm text-red-500">{errors.pan_number}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="tan_number">TAN Number</Label>
            <Input
              id="tan_number"
              value={formData.tan_number}
              onChange={(e) => handleChange('tan_number', e.target.value.toUpperCase())}
              placeholder="AAAA00000A"
              maxLength={10}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="msme_registration">MSME Registration</Label>
            <Input
              id="msme_registration"
              value={formData.msme_registration}
              onChange={(e) => handleChange('msme_registration', e.target.value)}
              placeholder="MSME Registration Number"
            />
          </div>
        </CardContent>
      </Card>

      {/* Payment Terms */}
      <Card>
        <CardHeader>
          <CardTitle>Payment Terms</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="space-y-2">
            <Label htmlFor="payment_terms">Payment Terms</Label>
            <Select
              value={formData.payment_terms}
              onValueChange={(value) => handleChange('payment_terms', value)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="immediate">Immediate</SelectItem>
                <SelectItem value="net_15">Net 15</SelectItem>
                <SelectItem value="net_30">Net 30</SelectItem>
                <SelectItem value="net_45">Net 45</SelectItem>
                <SelectItem value="net_60">Net 60</SelectItem>
                <SelectItem value="net_90">Net 90</SelectItem>
                <SelectItem value="cod">Cash on Delivery</SelectItem>
                <SelectItem value="advance">Advance Payment</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="credit_limit">Credit Limit (₹)</Label>
            <Input
              id="credit_limit"
              type="number"
              value={formData.credit_limit}
              onChange={(e) => handleChange('credit_limit', parseFloat(e.target.value) || 0)}
              placeholder="0.00"
              min="0"
              step="0.01"
              className={errors.credit_limit ? 'border-red-500' : ''}
            />
            {errors.credit_limit && (
              <p className="text-sm text-red-500">{errors.credit_limit}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="credit_period_days">Credit Period (Days)</Label>
            <Input
              id="credit_period_days"
              type="number"
              value={formData.credit_period_days}
              onChange={(e) => handleChange('credit_period_days', parseInt(e.target.value) || 0)}
              placeholder="30"
              min="0"
              className={errors.credit_period_days ? 'border-red-500' : ''}
            />
            {errors.credit_period_days && (
              <p className="text-sm text-red-500">{errors.credit_period_days}</p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Banking Details */}
      <Card>
        <CardHeader>
          <CardTitle>Banking Details</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="bank_name">Bank Name</Label>
            <Input
              id="bank_name"
              value={formData.bank_name}
              onChange={(e) => handleChange('bank_name', e.target.value)}
              placeholder="Bank name"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="bank_branch">Branch</Label>
            <Input
              id="bank_branch"
              value={formData.bank_branch}
              onChange={(e) => handleChange('bank_branch', e.target.value)}
              placeholder="Branch name"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="account_number">Account Number</Label>
            <Input
              id="account_number"
              value={formData.account_number}
              onChange={(e) => handleChange('account_number', e.target.value)}
              placeholder="Account number"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="ifsc_code">IFSC Code</Label>
            <Input
              id="ifsc_code"
              value={formData.ifsc_code}
              onChange={(e) => handleChange('ifsc_code', e.target.value.toUpperCase())}
              placeholder="ABCD0123456"
              maxLength={11}
            />
          </div>

          <div className="space-y-2 md:col-span-2">
            <Label htmlFor="account_holder_name">Account Holder Name</Label>
            <Input
              id="account_holder_name"
              value={formData.account_holder_name}
              onChange={(e) => handleChange('account_holder_name', e.target.value)}
              placeholder="As per bank records"
            />
          </div>
        </CardContent>
      </Card>

      {/* Notes */}
      <Card>
        <CardHeader>
          <CardTitle>Additional Notes</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <Label htmlFor="notes">Notes</Label>
            <Textarea
              id="notes"
              value={formData.notes}
              onChange={(e) => handleChange('notes', e.target.value)}
              placeholder="Any additional notes or remarks about the vendor"
              rows={4}
            />
          </div>
        </CardContent>
      </Card>

      {/* Form Actions */}
      <div className="flex items-center justify-end gap-3">
        <Button
          type="button"
          variant="outline"
          onClick={handleCancel}
          disabled={loading}
        >
          <X className="w-4 h-4 mr-2" />
          Cancel
        </Button>
        <Button type="submit" disabled={loading}>
          <Save className="w-4 h-4 mr-2" />
          {loading ? 'Saving...' : vendor ? 'Update Vendor' : 'Create Vendor'}
        </Button>
      </div>
    </form>
  );
}
