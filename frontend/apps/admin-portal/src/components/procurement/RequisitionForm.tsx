/**
 * Requisition Form Component
 * Form for creating and editing purchase requisitions with line items
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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Save, X, Plus, Trash2, Calendar } from 'lucide-react';
import { procurementService } from '@/services/procurement.service';
import type { PurchaseRequisition } from '@/types/procurement';

interface RequisitionFormProps {
  requisition?: PurchaseRequisition;
  onSuccess?: () => void;
  onCancel?: () => void;
}

interface RequisitionItemData {
  id?: string;
  item_code: string;
  item_description: string;
  specification: string;
  quantity: number;
  uom: string;
  estimated_rate: number;
  estimated_amount: number;
  required_by_date: string;
}

interface RequisitionFormData {
  title: string;
  description: string;
  requested_by: string;
  department: string;
  requisition_date: string;
  required_by_date: string;
  items: RequisitionItemData[];
}

export default function RequisitionForm({
  requisition,
  onSuccess,
  onCancel,
}: RequisitionFormProps) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const today = new Date().toISOString().split('T')[0];
  const defaultRequiredDate = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
    .toISOString()
    .split('T')[0];

  const [formData, setFormData] = useState<RequisitionFormData>({
    title: requisition?.title || '',
    description: requisition?.description || '',
    requested_by: requisition?.requested_by || '',
    department: requisition?.department || '',
    requisition_date: requisition?.requisition_date
      ? new Date(requisition.requisition_date).toISOString().split('T')[0]
      : today,
    required_by_date: requisition?.required_by_date
      ? new Date(requisition.required_by_date).toISOString().split('T')[0]
      : defaultRequiredDate,
    items:
      requisition?.items?.map((item) => ({
        id: item.id,
        item_code: item.item_code,
        item_description: item.item_description,
        specification: item.specification || '',
        quantity: item.quantity,
        uom: item.uom,
        estimated_rate: item.estimated_rate,
        estimated_amount: item.estimated_amount,
        required_by_date: item.required_by_date
          ? new Date(item.required_by_date).toISOString().split('T')[0]
          : defaultRequiredDate,
      })) || [],
  });

  useEffect(() => {
    // Initialize with one empty item if no items exist
    if (formData.items.length === 0 && !requisition) {
      addItem();
    }
  }, []);

  const handleChange = (field: keyof RequisitionFormData, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const handleItemChange = (
    index: number,
    field: keyof RequisitionItemData,
    value: any
  ) => {
    setFormData((prev) => {
      const newItems = [...prev.items];
      newItems[index] = { ...newItems[index], [field]: value };

      // Auto-calculate amount when quantity or rate changes
      if (field === 'quantity' || field === 'estimated_rate') {
        const quantity = field === 'quantity' ? value : newItems[index].quantity;
        const rate = field === 'estimated_rate' ? value : newItems[index].estimated_rate;
        newItems[index].estimated_amount = quantity * rate;
      }

      return { ...prev, items: newItems };
    });

    // Clear item-specific errors
    const errorKey = `items.${index}.${field}`;
    if (errors[errorKey]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[errorKey];
        return newErrors;
      });
    }
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
          required_by_date: formData.required_by_date,
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

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    // Validate header fields
    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    }
    if (!formData.requested_by.trim()) {
      newErrors.requested_by = 'Requested by is required';
    }
    if (!formData.department.trim()) {
      newErrors.department = 'Department is required';
    }
    if (!formData.requisition_date) {
      newErrors.requisition_date = 'Requisition date is required';
    }
    if (!formData.required_by_date) {
      newErrors.required_by_date = 'Required by date is required';
    }
    if (
      formData.requisition_date &&
      formData.required_by_date &&
      new Date(formData.required_by_date) < new Date(formData.requisition_date)
    ) {
      newErrors.required_by_date =
        'Required by date must be after requisition date';
    }

    // Validate items
    if (formData.items.length === 0) {
      newErrors.items = 'At least one item is required';
    } else {
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
        if (!item.uom.trim()) {
          newErrors[`items.${index}.uom`] = 'UOM is required';
        }
        if (item.estimated_rate < 0) {
          newErrors[`items.${index}.estimated_rate`] = 'Rate cannot be negative';
        }
        if (!item.required_by_date) {
          newErrors[`items.${index}.required_by_date`] = 'Required date is required';
        }
      });
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
      const payload = {
        ...formData,
        total_amount: calculateTotalAmount(),
      };

      let response;
      if (requisition?.id) {
        // Update existing requisition
        response = await procurementService.requisition.update(
          requisition.id,
          payload
        );
      } else {
        // Create new requisition
        response = await procurementService.requisition.create(payload);
      }

      if (response.success) {
        if (onSuccess) {
          onSuccess();
        } else {
          router.push('/procurement/requisitions');
        }
      } else {
        setErrors({ submit: response.message || 'Failed to save requisition' });
      }
    } catch (error) {
      console.error('Failed to save requisition:', error);
      setErrors({ submit: 'An error occurred while saving the requisition' });
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    if (onCancel) {
      onCancel();
    } else {
      router.push('/procurement/requisitions');
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
          <CardTitle>Requisition Information</CardTitle>
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
              placeholder="Brief title for the requisition"
              className={errors.title ? 'border-red-500' : ''}
            />
            {errors.title && (
              <p className="text-sm text-red-500">{errors.title}</p>
            )}
          </div>

          <div className="space-y-2 md:col-span-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => handleChange('description', e.target.value)}
              placeholder="Detailed description of the requisition"
              rows={3}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="requested_by">
              Requested By <span className="text-red-500">*</span>
            </Label>
            <Input
              id="requested_by"
              value={formData.requested_by}
              onChange={(e) => handleChange('requested_by', e.target.value)}
              placeholder="Name of the requester"
              className={errors.requested_by ? 'border-red-500' : ''}
            />
            {errors.requested_by && (
              <p className="text-sm text-red-500">{errors.requested_by}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="department">
              Department <span className="text-red-500">*</span>
            </Label>
            <Input
              id="department"
              value={formData.department}
              onChange={(e) => handleChange('department', e.target.value)}
              placeholder="Department name"
              className={errors.department ? 'border-red-500' : ''}
            />
            {errors.department && (
              <p className="text-sm text-red-500">{errors.department}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="requisition_date">
              Requisition Date <span className="text-red-500">*</span>
            </Label>
            <div className="relative">
              <Input
                id="requisition_date"
                type="date"
                value={formData.requisition_date}
                onChange={(e) => handleChange('requisition_date', e.target.value)}
                className={errors.requisition_date ? 'border-red-500' : ''}
              />
              <Calendar className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4 pointer-events-none" />
            </div>
            {errors.requisition_date && (
              <p className="text-sm text-red-500">{errors.requisition_date}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="required_by_date">
              Required By Date <span className="text-red-500">*</span>
            </Label>
            <div className="relative">
              <Input
                id="required_by_date"
                type="date"
                value={formData.required_by_date}
                onChange={(e) => handleChange('required_by_date', e.target.value)}
                min={formData.requisition_date}
                className={errors.required_by_date ? 'border-red-500' : ''}
              />
              <Calendar className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4 pointer-events-none" />
            </div>
            {errors.required_by_date && (
              <p className="text-sm text-red-500">{errors.required_by_date}</p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Line Items */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Requisition Items</CardTitle>
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
                  <TableHead className="min-w-[120px]">
                    Item Code <span className="text-red-500">*</span>
                  </TableHead>
                  <TableHead className="min-w-[200px]">
                    Description <span className="text-red-500">*</span>
                  </TableHead>
                  <TableHead className="min-w-[150px]">Specification</TableHead>
                  <TableHead className="min-w-[100px]">
                    Quantity <span className="text-red-500">*</span>
                  </TableHead>
                  <TableHead className="min-w-[80px]">
                    UOM <span className="text-red-500">*</span>
                  </TableHead>
                  <TableHead className="min-w-[120px]">Est. Rate</TableHead>
                  <TableHead className="min-w-[120px]">Amount</TableHead>
                  <TableHead className="min-w-[140px]">Required By</TableHead>
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
                          errors[`items.${index}.item_code`]
                            ? 'border-red-500'
                            : ''
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
                        onChange={(e) =>
                          handleItemChange(index, 'uom', e.target.value)
                        }
                        placeholder="UOM"
                        className={
                          errors[`items.${index}.uom`] ? 'border-red-500' : ''
                        }
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
                        className={
                          errors[`items.${index}.estimated_rate`]
                            ? 'border-red-500'
                            : ''
                        }
                      />
                    </TableCell>
                    <TableCell>
                      <div className="font-medium text-right">
                        {formatCurrency(item.estimated_amount)}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Input
                        type="date"
                        value={item.required_by_date}
                        onChange={(e) =>
                          handleItemChange(index, 'required_by_date', e.target.value)
                        }
                        min={formData.requisition_date}
                        className={
                          errors[`items.${index}.required_by_date`]
                            ? 'border-red-500'
                            : ''
                        }
                      />
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

          {/* Total */}
          <div className="mt-4 flex justify-end">
            <div className="w-64 space-y-2">
              <div className="flex justify-between items-center py-2 border-t-2 border-gray-900">
                <span className="text-lg font-bold">Total Amount:</span>
                <span className="text-lg font-bold">
                  {formatCurrency(calculateTotalAmount())}
                </span>
              </div>
            </div>
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
          {loading
            ? 'Saving...'
            : requisition
            ? 'Update Requisition'
            : 'Create Requisition'}
        </Button>
      </div>
    </form>
  );
}
