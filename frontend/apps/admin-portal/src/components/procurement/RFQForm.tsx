/**
 * RFQ Form Component
 * Form for creating and editing RFQs with items and vendor selection
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Save, X, Plus, Trash2, Calendar, Users } from 'lucide-react';
import { procurementService } from '@/services/procurement.service';
import type { RFQ, Vendor, PurchaseRequisitionItem } from '@/types/procurement';

interface RFQFormProps {
  rfq?: RFQ;
  onSuccess?: () => void;
  onCancel?: () => void;
}

interface RFQItemData {
  requisition_item_id?: string;
  item_code: string;
  item_description: string;
  specification: string;
  quantity: number;
  uom: string;
  estimated_rate: number;
  estimated_amount: number;
}

interface RFQFormData {
  title: string;
  description: string;
  rfq_date: string;
  quote_deadline: string;
  items: RFQItemData[];
  vendor_ids: string[];
}

export default function RFQForm({ rfq, onSuccess, onCancel }: RFQFormProps) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [loadingVendors, setLoadingVendors] = useState(true);

  const today = new Date().toISOString().split('T')[0];
  const defaultDeadline = new Date(Date.now() + 14 * 24 * 60 * 60 * 1000)
    .toISOString()
    .split('T')[0];

  const [formData, setFormData] = useState<RFQFormData>({
    title: rfq?.title || '',
    description: rfq?.description || '',
    rfq_date: rfq?.rfq_date
      ? new Date(rfq.rfq_date).toISOString().split('T')[0]
      : today,
    quote_deadline: rfq?.quote_deadline
      ? new Date(rfq.quote_deadline).toISOString().split('T')[0]
      : defaultDeadline,
    items:
      rfq?.items?.map((item) => ({
        requisition_item_id: item.requisition_item_id,
        item_code: item.item_code,
        item_description: item.item_description,
        specification: item.specification || '',
        quantity: item.quantity,
        uom: item.uom,
        estimated_rate: item.estimated_rate,
        estimated_amount: item.estimated_amount,
      })) || [],
    vendor_ids: rfq?.vendors?.map((v) => v.vendor_id) || [],
  });

  useEffect(() => {
    fetchVendors();
    if (formData.items.length === 0 && !rfq) {
      addItem();
    }
  }, []);

  const fetchVendors = async () => {
    try {
      setLoadingVendors(true);
      const response = await procurementService.vendor.getAll({ status: 'active' });
      if (response.success && response.data) {
        setVendors(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch vendors:', error);
    } finally {
      setLoadingVendors(false);
    }
  };

  const handleChange = (field: keyof RFQFormData, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const handleItemChange = (index: number, field: keyof RFQItemData, value: any) => {
    setFormData((prev) => {
      const newItems = [...prev.items];
      newItems[index] = { ...newItems[index], [field]: value };

      if (field === 'quantity' || field === 'estimated_rate') {
        const quantity = field === 'quantity' ? value : newItems[index].quantity;
        const rate = field === 'estimated_rate' ? value : newItems[index].estimated_rate;
        newItems[index].estimated_amount = quantity * rate;
      }

      return { ...prev, items: newItems };
    });
  };

  const addItem = () => {
    setFormData((prev) => ({
      ...prev,
      items: [
        ...prev.items,
        {
          item_code: '',
          item_description: '',
          specification: '',
          quantity: 1,
          uom: 'PCS',
          estimated_rate: 0,
          estimated_amount: 0,
        },
      ],
    }));
  };

  const removeItem = (index: number) => {
    if (formData.items.length === 1) {
      setErrors({ items: 'At least one item is required' });
      return;
    }
    setFormData((prev) => ({
      ...prev,
      items: prev.items.filter((_, i) => i !== index),
    }));
  };

  const toggleVendor = (vendorId: string) => {
    setFormData((prev) => ({
      ...prev,
      vendor_ids: prev.vendor_ids.includes(vendorId)
        ? prev.vendor_ids.filter((id) => id !== vendorId)
        : [...prev.vendor_ids, vendorId],
    }));
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    }
    if (!formData.rfq_date) {
      newErrors.rfq_date = 'RFQ date is required';
    }
    if (!formData.quote_deadline) {
      newErrors.quote_deadline = 'Quote deadline is required';
    }
    if (
      formData.rfq_date &&
      formData.quote_deadline &&
      new Date(formData.quote_deadline) <= new Date(formData.rfq_date)
    ) {
      newErrors.quote_deadline = 'Quote deadline must be after RFQ date';
    }
    if (formData.items.length === 0) {
      newErrors.items = 'At least one item is required';
    }
    if (formData.vendor_ids.length === 0) {
      newErrors.vendors = 'At least one vendor must be selected';
    }

    formData.items.forEach((item, index) => {
      if (!item.item_code.trim()) {
        newErrors[`items.${index}.item_code`] = 'Item code is required';
      }
      if (!item.item_description.trim()) {
        newErrors[`items.${index}.item_description`] = 'Description is required';
      }
      if (item.quantity <= 0) {
        newErrors[`items.${index}.quantity`] = 'Quantity must be greater than 0';
      }
    });

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
      const payload = {
        ...formData,
        total_amount: calculateTotalAmount(),
      };

      let response;
      if (rfq?.id) {
        response = await procurementService.rfq.update(rfq.id, payload);
      } else {
        response = await procurementService.rfq.create(payload);
      }

      if (response.success) {
        if (onSuccess) {
          onSuccess();
        } else {
          router.push('/procurement/rfq');
        }
      } else {
        setErrors({ submit: response.message || 'Failed to save RFQ' });
      }
    } catch (error) {
      console.error('Failed to save RFQ:', error);
      setErrors({ submit: 'An error occurred while saving the RFQ' });
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    if (onCancel) {
      onCancel();
    } else {
      router.push('/procurement/rfq');
    }
  };

  const calculateTotalAmount = (): number => {
    return formData.items.reduce((sum, item) => sum + item.estimated_amount, 0);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2,
    }).format(amount);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {errors.submit && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {errors.submit}
        </div>
      )}

      {/* Header Information */}
      <Card>
        <CardHeader>
          <CardTitle>RFQ Information</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2 md:col-span-2">
            <Label htmlFor="title">
              Title <span className="text-red-500">*</span>
            </Label>
            <Input
              id="title"
              value={formData.title}
              onChange={(e) => handleChange('title', e.target.value)}
              placeholder="Brief title for the RFQ"
              className={errors.title ? 'border-red-500' : ''}
            />
            {errors.title && <p className="text-sm text-red-500">{errors.title}</p>}
          </div>

          <div className="space-y-2 md:col-span-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => handleChange('description', e.target.value)}
              placeholder="Detailed description of the RFQ"
              rows={3}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="rfq_date">
              RFQ Date <span className="text-red-500">*</span>
            </Label>
            <div className="relative">
              <Input
                id="rfq_date"
                type="date"
                value={formData.rfq_date}
                onChange={(e) => handleChange('rfq_date', e.target.value)}
                className={errors.rfq_date ? 'border-red-500' : ''}
              />
              <Calendar className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4 pointer-events-none" />
            </div>
            {errors.rfq_date && <p className="text-sm text-red-500">{errors.rfq_date}</p>}
          </div>

          <div className="space-y-2">
            <Label htmlFor="quote_deadline">
              Quote Deadline <span className="text-red-500">*</span>
            </Label>
            <div className="relative">
              <Input
                id="quote_deadline"
                type="date"
                value={formData.quote_deadline}
                onChange={(e) => handleChange('quote_deadline', e.target.value)}
                min={formData.rfq_date}
                className={errors.quote_deadline ? 'border-red-500' : ''}
              />
              <Calendar className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4 pointer-events-none" />
            </div>
            {errors.quote_deadline && (
              <p className="text-sm text-red-500">{errors.quote_deadline}</p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Line Items */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>RFQ Items</CardTitle>
            <Button type="button" onClick={addItem} size="sm" variant="outline">
              <Plus className="w-4 h-4 mr-2" />
              Add Item
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {errors.items && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
              {errors.items}
            </div>
          )}

          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-12">#</TableHead>
                  <TableHead className="min-w-[120px]">Item Code *</TableHead>
                  <TableHead className="min-w-[200px]">Description *</TableHead>
                  <TableHead className="min-w-[150px]">Specification</TableHead>
                  <TableHead className="min-w-[100px]">Quantity *</TableHead>
                  <TableHead className="min-w-[80px]">UOM</TableHead>
                  <TableHead className="min-w-[120px]">Est. Rate</TableHead>
                  <TableHead className="min-w-[120px]">Amount</TableHead>
                  <TableHead className="w-12"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {formData.items.map((item, index) => (
                  <TableRow key={index}>
                    <TableCell className="font-medium">{index + 1}</TableCell>
                    <TableCell>
                      <Input
                        value={item.item_code}
                        onChange={(e) =>
                          handleItemChange(index, 'item_code', e.target.value)
                        }
                        placeholder="Item code"
                        className={
                          errors[`items.${index}.item_code`] ? 'border-red-500' : ''
                        }
                      />
                    </TableCell>
                    <TableCell>
                      <Input
                        value={item.item_description}
                        onChange={(e) =>
                          handleItemChange(index, 'item_description', e.target.value)
                        }
                        placeholder="Description"
                        className={
                          errors[`items.${index}.item_description`]
                            ? 'border-red-500'
                            : ''
                        }
                      />
                    </TableCell>
                    <TableCell>
                      <Input
                        value={item.specification}
                        onChange={(e) =>
                          handleItemChange(index, 'specification', e.target.value)
                        }
                        placeholder="Specification"
                      />
                    </TableCell>
                    <TableCell>
                      <Input
                        type="number"
                        value={item.quantity}
                        onChange={(e) =>
                          handleItemChange(
                            index,
                            'quantity',
                            parseFloat(e.target.value) || 0
                          )
                        }
                        min="0"
                        step="0.01"
                        className={
                          errors[`items.${index}.quantity`] ? 'border-red-500' : ''
                        }
                      />
                    </TableCell>
                    <TableCell>
                      <Input
                        value={item.uom}
                        onChange={(e) => handleItemChange(index, 'uom', e.target.value)}
                        placeholder="UOM"
                      />
                    </TableCell>
                    <TableCell>
                      <Input
                        type="number"
                        value={item.estimated_rate}
                        onChange={(e) =>
                          handleItemChange(
                            index,
                            'estimated_rate',
                            parseFloat(e.target.value) || 0
                          )
                        }
                        min="0"
                        step="0.01"
                      />
                    </TableCell>
                    <TableCell>
                      <div className="font-medium text-right">
                        {formatCurrency(item.estimated_amount)}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => removeItem(index)}
                        disabled={formData.items.length === 1}
                      >
                        <Trash2 className="w-4 h-4 text-red-600" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          <div className="mt-4 flex justify-end">
            <div className="w-64 space-y-2">
              <div className="flex justify-between items-center py-2 border-t-2 border-gray-900">
                <span className="text-lg font-bold">Total Est. Amount:</span>
                <span className="text-lg font-bold">
                  {formatCurrency(calculateTotalAmount())}
                </span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Vendor Selection */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Users className="w-5 h-5" />
              Select Vendors
              <span className="text-sm font-normal text-gray-500">
                ({formData.vendor_ids.length} selected)
              </span>
            </CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          {errors.vendors && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
              {errors.vendors}
            </div>
          )}

          {loadingVendors ? (
            <div className="text-center py-8 text-gray-500">Loading vendors...</div>
          ) : vendors.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No active vendors found. Please add vendors first.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 max-h-96 overflow-y-auto">
              {vendors.map((vendor) => (
                <div
                  key={vendor.id}
                  className={`flex items-start gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50 ${
                    formData.vendor_ids.includes(vendor.id)
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200'
                  }`}
                  onClick={() => toggleVendor(vendor.id)}
                >
                  <Checkbox
                    checked={formData.vendor_ids.includes(vendor.id)}
                    onCheckedChange={() => toggleVendor(vendor.id)}
                  />
                  <div className="flex-1">
                    <div className="font-medium">{vendor.vendor_name}</div>
                    <div className="text-sm text-gray-500">{vendor.vendor_code}</div>
                    {vendor.email && (
                      <div className="text-xs text-gray-400 mt-1">{vendor.email}</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
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
          {loading ? 'Saving...' : rfq ? 'Update RFQ' : 'Create RFQ'}
        </Button>
      </div>
    </form>
  );
}
