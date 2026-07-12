/**
 * Purchase Order Form Component
 * Form for creating and editing Purchase Orders
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Save, X, Plus, Trash2, Calendar, User, MapPin } from 'lucide-react';
import { procurementService } from '@/services/procurement.service';
import type { PurchaseOrder, Vendor, PaymentTermsEnum } from '@/types/procurement';

interface POFormProps {
  po?: PurchaseOrder;
  onSuccess?: () => void;
  onCancel?: () => void;
}

interface POItemData {
  item_code: string;
  item_name: string;
  description: string;
  specification: string;
  ordered_quantity: number;
  unit_of_measure: string;
  unit_price: number;
  total_price: number;
  tax_percentage: number;
  tax_amount: number;
  discount_percentage: number;
  discount_amount: number;
  net_amount: number;
  rfq_item_id?: string;
  requisition_item_id?: string;
}

interface POFormData {
  vendor_id: string;
  rfq_id?: string;
  requisition_id?: string;
  expected_delivery_date: string;
  payment_terms: PaymentTermsEnum;
  advance_payment_percentage: number;
  advance_payment_amount: number;
  delivery_address_line1: string;
  delivery_address_line2: string;
  delivery_city: string;
  delivery_state: string;
  delivery_pincode: string;
  delivery_country: string;
  delivery_contact_person: string;
  delivery_contact_phone: string;
  terms_and_conditions: string;
  special_instructions: string;
  items: POItemData[];
}

export default function POForm({ po, onSuccess, onCancel }: POFormProps) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [loadingVendors, setLoadingVendors] = useState(true);

  const minDeliveryDate = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
    .toISOString()
    .split('T')[0];

  const [formData, setFormData] = useState<POFormData>({
    vendor_id: po?.vendor_id || '',
    rfq_id: po?.rfq_id,
    requisition_id: po?.requisition_id,
    expected_delivery_date: po?.expected_delivery_date
      ? new Date(po.expected_delivery_date).toISOString().split('T')[0]
      : minDeliveryDate,
    payment_terms: po?.payment_terms || 'net_30',
    advance_payment_percentage: po?.advance_payment_percentage || 0,
    advance_payment_amount: po?.advance_payment_amount || 0,
    delivery_address_line1: po?.delivery_address_line1 || '',
    delivery_address_line2: po?.delivery_address_line2 || '',
    delivery_city: po?.delivery_city || '',
    delivery_state: po?.delivery_state || '',
    delivery_pincode: po?.delivery_pincode || '',
    delivery_country: po?.delivery_country || 'India',
    delivery_contact_person: po?.delivery_contact_person || '',
    delivery_contact_phone: po?.delivery_contact_phone || '',
    terms_and_conditions: po?.terms_and_conditions || '',
    special_instructions: po?.special_instructions || '',
    items:
      po?.items?.map((item) => ({
        item_code: item.item_code || '',
        item_name: item.item_name,
        description: item.description || '',
        specification: item.specification || '',
        ordered_quantity: item.ordered_quantity,
        unit_of_measure: item.unit_of_measure,
        unit_price: item.unit_price,
        total_price: item.total_price,
        tax_percentage: item.tax_percentage,
        tax_amount: item.tax_amount,
        discount_percentage: item.discount_percentage,
        discount_amount: item.discount_amount,
        net_amount: item.net_amount,
        rfq_item_id: item.rfq_item_id,
        requisition_item_id: item.requisition_item_id,
      })) || [],
  });

  useEffect(() => {
    fetchVendors();
    if (formData.items.length === 0 && !po) {
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

  const handleChange = (field: keyof POFormData, value: any) => {
    setFormData((prev) => {
      const newData = { ...prev, [field]: value };

      // Auto-calculate advance payment amount
      if (field === 'advance_payment_percentage') {
        const totalAmount = calculateTotals().total_amount;
        newData.advance_payment_amount = (totalAmount * value) / 100;
      }

      return newData;
    });

    if (errors[field]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const handleItemChange = (index: number, field: keyof POItemData, value: any) => {
    setFormData((prev) => {
      const newItems = [...prev.items];
      newItems[index] = { ...newItems[index], [field]: value };

      // Auto-calculate amounts
      const item = newItems[index];
      const quantity = item.ordered_quantity;
      const unitPrice = item.unit_price;

      // Total price = quantity × unit price
      item.total_price = quantity * unitPrice;

      // Tax amount = total price × tax percentage / 100
      item.tax_amount = (item.total_price * item.tax_percentage) / 100;

      // Discount amount = total price × discount percentage / 100
      item.discount_amount = (item.total_price * item.discount_percentage) / 100;

      // Net amount = total price + tax - discount
      item.net_amount = item.total_price + item.tax_amount - item.discount_amount;

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
          item_name: '',
          description: '',
          specification: '',
          ordered_quantity: 1,
          unit_of_measure: 'PCS',
          unit_price: 0,
          total_price: 0,
          tax_percentage: 18,
          tax_amount: 0,
          discount_percentage: 0,
          discount_amount: 0,
          net_amount: 0,
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

  const calculateTotals = () => {
    const subtotal = formData.items.reduce((sum, item) => sum + item.total_price, 0);
    const tax_amount = formData.items.reduce((sum, item) => sum + item.tax_amount, 0);
    const discount_amount = formData.items.reduce((sum, item) => sum + item.discount_amount, 0);
    const total_amount = formData.items.reduce((sum, item) => sum + item.net_amount, 0);

    return { subtotal, tax_amount, discount_amount, total_amount };
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.vendor_id) {
      newErrors.vendor_id = 'Vendor is required';
    }
    if (!formData.expected_delivery_date) {
      newErrors.expected_delivery_date = 'Expected delivery date is required';
    }
    if (!formData.delivery_address_line1.trim()) {
      newErrors.delivery_address_line1 = 'Delivery address is required';
    }
    if (!formData.delivery_city.trim()) {
      newErrors.delivery_city = 'Delivery city is required';
    }
    if (!formData.delivery_state.trim()) {
      newErrors.delivery_state = 'Delivery state is required';
    }
    if (!formData.delivery_pincode.trim()) {
      newErrors.delivery_pincode = 'Delivery pincode is required';
    }
    if (formData.items.length === 0) {
      newErrors.items = 'At least one item is required';
    }

    formData.items.forEach((item, index) => {
      if (!item.item_name.trim()) {
        newErrors[`items.${index}.item_name`] = 'Item name is required';
      }
      if (item.ordered_quantity <= 0) {
        newErrors[`items.${index}.ordered_quantity`] = 'Quantity must be greater than 0';
      }
      if (item.unit_price <= 0) {
        newErrors[`items.${index}.unit_price`] = 'Unit price must be greater than 0';
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
      const totals = calculateTotals();
      const payload = {
        ...formData,
        ...totals,
      };

      let response;
      if (po?.id) {
        response = await procurementService.purchaseOrder.update(po.id, payload);
      } else {
        response = await procurementService.purchaseOrder.create(payload);
      }

      if (response.success) {
        if (onSuccess) {
          onSuccess();
        } else {
          router.push('/procurement/purchase-orders');
        }
      } else {
        setErrors({ submit: response.message || 'Failed to save purchase order' });
      }
    } catch (error) {
      console.error('Failed to save purchase order:', error);
      setErrors({ submit: 'An error occurred while saving the purchase order' });
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    if (onCancel) {
      onCancel();
    } else {
      router.push('/procurement/purchase-orders');
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2,
    }).format(amount);
  };

  const totals = calculateTotals();

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {errors.submit && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {errors.submit}
        </div>
      )}

      {/* Vendor and Basic Information */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="w-5 h-5" />
            Vendor & Basic Information
          </CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="vendor_id">
              Vendor <span className="text-red-500">*</span>
            </Label>
            <Select
              value={formData.vendor_id}
              onValueChange={(value) => handleChange('vendor_id', value)}
            >
              <SelectTrigger className={errors.vendor_id ? 'border-red-500' : ''}>
                <SelectValue placeholder="Select vendor" />
              </SelectTrigger>
              <SelectContent>
                {loadingVendors ? (
                  <SelectItem value="loading" disabled>
                    Loading vendors...
                  </SelectItem>
                ) : vendors.length === 0 ? (
                  <SelectItem value="none" disabled>
                    No active vendors found
                  </SelectItem>
                ) : (
                  vendors.map((vendor) => (
                    <SelectItem key={vendor.id} value={vendor.id}>
                      {vendor.vendor_name} ({vendor.vendor_code})
                    </SelectItem>
                  ))
                )}
              </SelectContent>
            </Select>
            {errors.vendor_id && <p className="text-sm text-red-500">{errors.vendor_id}</p>}
          </div>

          <div className="space-y-2">
            <Label htmlFor="expected_delivery_date">
              Expected Delivery Date <span className="text-red-500">*</span>
            </Label>
            <div className="relative">
              <Input
                id="expected_delivery_date"
                type="date"
                value={formData.expected_delivery_date}
                onChange={(e) => handleChange('expected_delivery_date', e.target.value)}
                min={minDeliveryDate}
                className={errors.expected_delivery_date ? 'border-red-500' : ''}
              />
              <Calendar className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4 pointer-events-none" />
            </div>
            {errors.expected_delivery_date && (
              <p className="text-sm text-red-500">{errors.expected_delivery_date}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="payment_terms">Payment Terms</Label>
            <Select
              value={formData.payment_terms}
              onValueChange={(value: PaymentTermsEnum) => handleChange('payment_terms', value)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="net_15">Net 15 Days</SelectItem>
                <SelectItem value="net_30">Net 30 Days</SelectItem>
                <SelectItem value="net_45">Net 45 Days</SelectItem>
                <SelectItem value="net_60">Net 60 Days</SelectItem>
                <SelectItem value="advance_100">100% Advance</SelectItem>
                <SelectItem value="advance_50">50% Advance</SelectItem>
                <SelectItem value="cod">Cash on Delivery</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="advance_payment_percentage">Advance Payment %</Label>
            <Input
              id="advance_payment_percentage"
              type="number"
              value={formData.advance_payment_percentage}
              onChange={(e) =>
                handleChange('advance_payment_percentage', parseFloat(e.target.value) || 0)
              }
              min="0"
              max="100"
              step="0.01"
            />
            {formData.advance_payment_percentage > 0 && (
              <p className="text-sm text-gray-600">
                Advance Amount: {formatCurrency(formData.advance_payment_amount)}
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Line Items */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Purchase Order Items</CardTitle>
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
                  <TableHead className="min-w-[120px]">Item Code</TableHead>
                  <TableHead className="min-w-[150px]">Item Name *</TableHead>
                  <TableHead className="min-w-[150px]">Description</TableHead>
                  <TableHead className="min-w-[100px]">Quantity *</TableHead>
                  <TableHead className="min-w-[80px]">UOM</TableHead>
                  <TableHead className="min-w-[120px]">Unit Price *</TableHead>
                  <TableHead className="min-w-[100px]">Tax %</TableHead>
                  <TableHead className="min-w-[100px]">Disc. %</TableHead>
                  <TableHead className="min-w-[120px]">Net Amount</TableHead>
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
                        onChange={(e) => handleItemChange(index, 'item_code', e.target.value)}
                        placeholder="Code"
                      />
                    </TableCell>
                    <TableCell>
                      <Input
                        value={item.item_name}
                        onChange={(e) => handleItemChange(index, 'item_name', e.target.value)}
                        placeholder="Item name"
                        className={errors[`items.${index}.item_name`] ? 'border-red-500' : ''}
                      />
                    </TableCell>
                    <TableCell>
                      <Input
                        value={item.description}
                        onChange={(e) => handleItemChange(index, 'description', e.target.value)}
                        placeholder="Description"
                      />
                    </TableCell>
                    <TableCell>
                      <Input
                        type="number"
                        value={item.ordered_quantity}
                        onChange={(e) =>
                          handleItemChange(index, 'ordered_quantity', parseFloat(e.target.value) || 0)
                        }
                        min="0"
                        step="0.01"
                        className={
                          errors[`items.${index}.ordered_quantity`] ? 'border-red-500' : ''
                        }
                      />
                    </TableCell>
                    <TableCell>
                      <Input
                        value={item.unit_of_measure}
                        onChange={(e) => handleItemChange(index, 'unit_of_measure', e.target.value)}
                        placeholder="UOM"
                      />
                    </TableCell>
                    <TableCell>
                      <Input
                        type="number"
                        value={item.unit_price}
                        onChange={(e) =>
                          handleItemChange(index, 'unit_price', parseFloat(e.target.value) || 0)
                        }
                        min="0"
                        step="0.01"
                        className={errors[`items.${index}.unit_price`] ? 'border-red-500' : ''}
                      />
                    </TableCell>
                    <TableCell>
                      <Input
                        type="number"
                        value={item.tax_percentage}
                        onChange={(e) =>
                          handleItemChange(index, 'tax_percentage', parseFloat(e.target.value) || 0)
                        }
                        min="0"
                        max="100"
                        step="0.01"
                      />
                    </TableCell>
                    <TableCell>
                      <Input
                        type="number"
                        value={item.discount_percentage}
                        onChange={(e) =>
                          handleItemChange(
                            index,
                            'discount_percentage',
                            parseFloat(e.target.value) || 0
                          )
                        }
                        min="0"
                        max="100"
                        step="0.01"
                      />
                    </TableCell>
                    <TableCell>
                      <div className="font-medium text-right">{formatCurrency(item.net_amount)}</div>
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

          {/* Totals */}
          <div className="mt-6 flex justify-end">
            <div className="w-80 space-y-2">
              <div className="flex justify-between items-center py-2">
                <span className="text-gray-600">Subtotal:</span>
                <span className="font-medium">{formatCurrency(totals.subtotal)}</span>
              </div>
              {totals.discount_amount > 0 && (
                <div className="flex justify-between items-center py-2">
                  <span className="text-gray-600">Discount:</span>
                  <span className="font-medium text-red-600">
                    - {formatCurrency(totals.discount_amount)}
                  </span>
                </div>
              )}
              {totals.tax_amount > 0 && (
                <div className="flex justify-between items-center py-2">
                  <span className="text-gray-600">Tax:</span>
                  <span className="font-medium">+ {formatCurrency(totals.tax_amount)}</span>
                </div>
              )}
              <div className="flex justify-between items-center py-2 border-t-2 border-gray-900">
                <span className="text-lg font-bold">Total Amount:</span>
                <span className="text-lg font-bold text-green-600">
                  {formatCurrency(totals.total_amount)}
                </span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Delivery Information */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MapPin className="w-5 h-5" />
            Delivery Information
          </CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2 md:col-span-2">
            <Label htmlFor="delivery_address_line1">
              Address Line 1 <span className="text-red-500">*</span>
            </Label>
            <Input
              id="delivery_address_line1"
              value={formData.delivery_address_line1}
              onChange={(e) => handleChange('delivery_address_line1', e.target.value)}
              placeholder="Street address"
              className={errors.delivery_address_line1 ? 'border-red-500' : ''}
            />
            {errors.delivery_address_line1 && (
              <p className="text-sm text-red-500">{errors.delivery_address_line1}</p>
            )}
          </div>

          <div className="space-y-2 md:col-span-2">
            <Label htmlFor="delivery_address_line2">Address Line 2</Label>
            <Input
              id="delivery_address_line2"
              value={formData.delivery_address_line2}
              onChange={(e) => handleChange('delivery_address_line2', e.target.value)}
              placeholder="Apartment, suite, etc."
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="delivery_city">
              City <span className="text-red-500">*</span>
            </Label>
            <Input
              id="delivery_city"
              value={formData.delivery_city}
              onChange={(e) => handleChange('delivery_city', e.target.value)}
              placeholder="City"
              className={errors.delivery_city ? 'border-red-500' : ''}
            />
            {errors.delivery_city && (
              <p className="text-sm text-red-500">{errors.delivery_city}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="delivery_state">
              State <span className="text-red-500">*</span>
            </Label>
            <Input
              id="delivery_state"
              value={formData.delivery_state}
              onChange={(e) => handleChange('delivery_state', e.target.value)}
              placeholder="State"
              className={errors.delivery_state ? 'border-red-500' : ''}
            />
            {errors.delivery_state && (
              <p className="text-sm text-red-500">{errors.delivery_state}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="delivery_pincode">
              Pincode <span className="text-red-500">*</span>
            </Label>
            <Input
              id="delivery_pincode"
              value={formData.delivery_pincode}
              onChange={(e) => handleChange('delivery_pincode', e.target.value)}
              placeholder="Pincode"
              className={errors.delivery_pincode ? 'border-red-500' : ''}
            />
            {errors.delivery_pincode && (
              <p className="text-sm text-red-500">{errors.delivery_pincode}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="delivery_country">Country</Label>
            <Input
              id="delivery_country"
              value={formData.delivery_country}
              onChange={(e) => handleChange('delivery_country', e.target.value)}
              placeholder="Country"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="delivery_contact_person">Contact Person</Label>
            <Input
              id="delivery_contact_person"
              value={formData.delivery_contact_person}
              onChange={(e) => handleChange('delivery_contact_person', e.target.value)}
              placeholder="Contact person name"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="delivery_contact_phone">Contact Phone</Label>
            <Input
              id="delivery_contact_phone"
              value={formData.delivery_contact_phone}
              onChange={(e) => handleChange('delivery_contact_phone', e.target.value)}
              placeholder="Contact phone number"
            />
          </div>
        </CardContent>
      </Card>

      {/* Terms and Instructions */}
      <Card>
        <CardHeader>
          <CardTitle>Terms & Instructions</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="terms_and_conditions">Terms & Conditions</Label>
            <Textarea
              id="terms_and_conditions"
              value={formData.terms_and_conditions}
              onChange={(e) => handleChange('terms_and_conditions', e.target.value)}
              placeholder="Enter terms and conditions"
              rows={4}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="special_instructions">Special Instructions</Label>
            <Textarea
              id="special_instructions"
              value={formData.special_instructions}
              onChange={(e) => handleChange('special_instructions', e.target.value)}
              placeholder="Any special instructions for the vendor"
              rows={3}
            />
          </div>
        </CardContent>
      </Card>

      {/* Form Actions */}
      <div className="flex items-center justify-end gap-3">
        <Button type="button" variant="outline" onClick={handleCancel} disabled={loading}>
          <X className="w-4 h-4 mr-2" />
          Cancel
        </Button>
        <Button type="submit" disabled={loading}>
          <Save className="w-4 h-4 mr-2" />
          {loading ? 'Saving...' : po ? 'Update Purchase Order' : 'Create Purchase Order'}
        </Button>
      </div>
    </form>
  );
}
