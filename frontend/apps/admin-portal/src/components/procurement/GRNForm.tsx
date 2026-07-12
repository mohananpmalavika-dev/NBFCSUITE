/**
 * GRN Form Component
 * Form for creating Goods Receipt Notes from Purchase Orders
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
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
import { Save, X, Calendar, Package, Truck, FileText } from 'lucide-react';
import { procurementService } from '@/services/procurement.service';
import type { GoodsReceiptNote, PurchaseOrder } from '@/types/procurement';

interface GRNFormProps {
  grn?: GoodsReceiptNote;
  onSuccess?: () => void;
  onCancel?: () => void;
}

interface GRNItemData {
  po_item_id: string;
  item_code: string;
  item_name: string;
  ordered_quantity: number;
  received_quantity: number;
  accepted_quantity: number;
  rejected_quantity: number;
  unit_of_measure: string;
  quality_status: string;
  quality_remarks: string;
  batch_number: string;
  serial_numbers: string;
  remarks: string;
}

interface GRNFormData {
  po_id: string;
  receipt_date: string;
  challan_number: string;
  challan_date: string;
  transporter_name: string;
  vehicle_number: string;
  lr_number: string;
  quality_check_required: boolean;
  warehouse_location: string;
  remarks: string;
  items: GRNItemData[];
}

export default function GRNForm({ grn, onSuccess, onCancel }: GRNFormProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const poIdFromQuery = searchParams.get('po_id');

  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [purchaseOrders, setPurchaseOrders] = useState<PurchaseOrder[]>([]);
  const [selectedPO, setSelectedPO] = useState<PurchaseOrder | null>(null);
  const [loadingPOs, setLoadingPOs] = useState(true);

  const today = new Date().toISOString().split('T')[0];

  const [formData, setFormData] = useState<GRNFormData>({
    po_id: grn?.po_id || poIdFromQuery || '',
    receipt_date: grn?.receipt_date
      ? new Date(grn.receipt_date).toISOString().split('T')[0]
      : today,
    challan_number: grn?.challan_number || '',
    challan_date: grn?.challan_date
      ? new Date(grn.challan_date).toISOString().split('T')[0]
      : '',
    transporter_name: grn?.transporter_name || '',
    vehicle_number: grn?.vehicle_number || '',
    lr_number: grn?.lr_number || '',
    quality_check_required: grn?.quality_check_required ?? true,
    warehouse_location: grn?.warehouse_location || '',
    remarks: grn?.remarks || '',
    items: grn?.items?.map((item) => ({
      po_item_id: item.po_item_id,
      item_code: item.item_code || '',
      item_name: item.item_name,
      ordered_quantity: item.ordered_quantity,
      received_quantity: item.received_quantity,
      accepted_quantity: item.accepted_quantity,
      rejected_quantity: item.rejected_quantity,
      unit_of_measure: item.unit_of_measure,
      quality_status: item.quality_status || 'pending',
      quality_remarks: item.quality_remarks || '',
      batch_number: item.batch_number || '',
      serial_numbers: item.serial_numbers || '',
      remarks: item.remarks || '',
    })) || [],
  });

  useEffect(() => {
    fetchPurchaseOrders();
  }, []);

  useEffect(() => {
    if (formData.po_id) {
      fetchPODetails(formData.po_id);
    }
  }, [formData.po_id]);

  const fetchPurchaseOrders = async () => {
    try {
      setLoadingPOs(true);
      // Fetch POs that are approved, sent, or acknowledged
      const response = await procurementService.purchaseOrder.getAll({
        status: 'approved,sent,acknowledged',
      });
      if (response.success && response.data) {
        setPurchaseOrders(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch purchase orders:', error);
    } finally {
      setLoadingPOs(false);
    }
  };

  const fetchPODetails = async (poId: string) => {
    try {
      const response = await procurementService.purchaseOrder.getById(poId);
      if (response.success && response.data) {
        setSelectedPO(response.data);
        // Initialize items from PO if not editing existing GRN
        if (!grn && response.data.items) {
          setFormData((prev) => ({
            ...prev,
            items: response.data.items.map((poItem) => ({
              po_item_id: poItem.id,
              item_code: poItem.item_code || '',
              item_name: poItem.item_name,
              ordered_quantity: poItem.ordered_quantity,
              received_quantity: 0,
              accepted_quantity: 0,
              rejected_quantity: 0,
              unit_of_measure: poItem.unit_of_measure,
              quality_status: 'pending',
              quality_remarks: '',
              batch_number: '',
              serial_numbers: '',
              remarks: '',
            })),
          }));
        }
      }
    } catch (error) {
      console.error('Failed to fetch PO details:', error);
    }
  };

  const handleChange = (field: keyof GRNFormData, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const handleItemChange = (index: number, field: keyof GRNItemData, value: any) => {
    setFormData((prev) => {
      const newItems = [...prev.items];
      newItems[index] = { ...newItems[index], [field]: value };

      // Auto-calculate accepted and rejected quantities
      if (field === 'received_quantity') {
        const item = newItems[index];
        // By default, set accepted = received, rejected = 0
        item.accepted_quantity = value;
        item.rejected_quantity = 0;
      }

      // Validate: accepted + rejected should = received
      if (field === 'accepted_quantity' || field === 'rejected_quantity') {
        const item = newItems[index];
        const total = item.accepted_quantity + item.rejected_quantity;
        if (total !== item.received_quantity) {
          // Auto-adjust the other field
          if (field === 'accepted_quantity') {
            item.rejected_quantity = item.received_quantity - item.accepted_quantity;
          } else {
            item.accepted_quantity = item.received_quantity - item.rejected_quantity;
          }
        }
      }

      return { ...prev, items: newItems };
    });
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.po_id) {
      newErrors.po_id = 'Purchase Order is required';
    }
    if (!formData.receipt_date) {
      newErrors.receipt_date = 'Receipt date is required';
    }
    if (formData.items.length === 0) {
      newErrors.items = 'At least one item is required';
    }

    formData.items.forEach((item, index) => {
      if (item.received_quantity <= 0) {
        newErrors[`items.${index}.received_quantity`] = 'Received quantity must be greater than 0';
      }
      if (item.received_quantity > item.ordered_quantity) {
        newErrors[`items.${index}.received_quantity`] =
          'Received quantity cannot exceed ordered quantity';
      }
      const total = item.accepted_quantity + item.rejected_quantity;
      if (total !== item.received_quantity) {
        newErrors[`items.${index}.quantities`] =
          'Accepted + Rejected must equal Received quantity';
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

      let response;
      if (grn?.id) {
        response = await procurementService.grn.update(grn.id, formData);
      } else {
        response = await procurementService.grn.create(formData);
      }

      if (response.success) {
        if (onSuccess) {
          onSuccess();
        } else {
          router.push('/procurement/grn');
        }
      } else {
        setErrors({ submit: response.message || 'Failed to save GRN' });
      }
    } catch (error) {
      console.error('Failed to save GRN:', error);
      setErrors({ submit: 'An error occurred while saving the GRN' });
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    if (onCancel) {
      onCancel();
    } else {
      router.push('/procurement/grn');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {errors.submit && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {errors.submit}
        </div>
      )}

      {/* Purchase Order Selection */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Purchase Order
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <Label htmlFor="po_id">
              Select Purchase Order <span className="text-red-500">*</span>
            </Label>
            <Select
              value={formData.po_id}
              onValueChange={(value) => handleChange('po_id', value)}
              disabled={!!grn}
            >
              <SelectTrigger className={errors.po_id ? 'border-red-500' : ''}>
                <SelectValue placeholder="Select a purchase order" />
              </SelectTrigger>
              <SelectContent>
                {loadingPOs ? (
                  <SelectItem value="loading" disabled>
                    Loading purchase orders...
                  </SelectItem>
                ) : purchaseOrders.length === 0 ? (
                  <SelectItem value="none" disabled>
                    No approved purchase orders found
                  </SelectItem>
                ) : (
                  purchaseOrders.map((po) => (
                    <SelectItem key={po.id} value={po.id}>
                      {po.po_number} - {new Date(po.po_date).toLocaleDateString()}
                    </SelectItem>
                  ))
                )}
              </SelectContent>
            </Select>
            {errors.po_id && <p className="text-sm text-red-500">{errors.po_id}</p>}
            {selectedPO && (
              <div className="mt-2 p-3 bg-gray-50 rounded text-sm">
                <div>
                  <span className="font-medium">PO Number:</span> {selectedPO.po_number}
                </div>
                <div>
                  <span className="font-medium">Expected Delivery:</span>{' '}
                  {new Date(selectedPO.expected_delivery_date).toLocaleDateString()}
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Receipt Information */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Package className="w-5 h-5" />
            Receipt Information
          </CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="receipt_date">
              Receipt Date <span className="text-red-500">*</span>
            </Label>
            <div className="relative">
              <Input
                id="receipt_date"
                type="date"
                value={formData.receipt_date}
                onChange={(e) => handleChange('receipt_date', e.target.value)}
                max={today}
                className={errors.receipt_date ? 'border-red-500' : ''}
              />
              <Calendar className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4 pointer-events-none" />
            </div>
            {errors.receipt_date && <p className="text-sm text-red-500">{errors.receipt_date}</p>}
          </div>

          <div className="space-y-2">
            <Label htmlFor="challan_number">Challan Number</Label>
            <Input
              id="challan_number"
              value={formData.challan_number}
              onChange={(e) => handleChange('challan_number', e.target.value)}
              placeholder="Vendor challan number"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="challan_date">Challan Date</Label>
            <div className="relative">
              <Input
                id="challan_date"
                type="date"
                value={formData.challan_date}
                onChange={(e) => handleChange('challan_date', e.target.value)}
                max={today}
              />
              <Calendar className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4 pointer-events-none" />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="warehouse_location">Warehouse Location</Label>
            <Input
              id="warehouse_location"
              value={formData.warehouse_location}
              onChange={(e) => handleChange('warehouse_location', e.target.value)}
              placeholder="Warehouse or storage location"
            />
          </div>

          <div className="space-y-2 md:col-span-2">
            <div className="flex items-center gap-2">
              <Checkbox
                id="quality_check_required"
                checked={formData.quality_check_required}
                onCheckedChange={(checked) =>
                  handleChange('quality_check_required', checked === true)
                }
              />
              <Label htmlFor="quality_check_required" className="cursor-pointer">
                Quality Check Required
              </Label>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Transport Information */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Truck className="w-5 h-5" />
            Transport Information
          </CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="space-y-2">
            <Label htmlFor="transporter_name">Transporter Name</Label>
            <Input
              id="transporter_name"
              value={formData.transporter_name}
              onChange={(e) => handleChange('transporter_name', e.target.value)}
              placeholder="Transport company name"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="vehicle_number">Vehicle Number</Label>
            <Input
              id="vehicle_number"
              value={formData.vehicle_number}
              onChange={(e) => handleChange('vehicle_number', e.target.value)}
              placeholder="Vehicle registration number"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="lr_number">LR Number</Label>
            <Input
              id="lr_number"
              value={formData.lr_number}
              onChange={(e) => handleChange('lr_number', e.target.value)}
              placeholder="Lorry receipt number"
            />
          </div>
        </CardContent>
      </Card>

      {/* Items */}
      {formData.items.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Receipt Items</CardTitle>
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
                    <TableHead>Item Code</TableHead>
                    <TableHead>Item Name</TableHead>
                    <TableHead className="text-right">Ordered Qty</TableHead>
                    <TableHead className="text-right">Received Qty *</TableHead>
                    <TableHead className="text-right">Accepted Qty</TableHead>
                    <TableHead className="text-right">Rejected Qty</TableHead>
                    <TableHead>UOM</TableHead>
                    <TableHead>Batch No.</TableHead>
                    <TableHead>Remarks</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {formData.items.map((item, index) => (
                    <TableRow key={index}>
                      <TableCell className="font-medium">{index + 1}</TableCell>
                      <TableCell className="text-sm">{item.item_code || '-'}</TableCell>
                      <TableCell className="font-medium">{item.item_name}</TableCell>
                      <TableCell className="text-right">{item.ordered_quantity.toFixed(2)}</TableCell>
                      <TableCell>
                        <Input
                          type="number"
                          value={item.received_quantity}
                          onChange={(e) =>
                            handleItemChange(index, 'received_quantity', parseFloat(e.target.value) || 0)
                          }
                          min="0"
                          max={item.ordered_quantity}
                          step="0.01"
                          className={
                            errors[`items.${index}.received_quantity`] ? 'border-red-500' : ''
                          }
                        />
                      </TableCell>
                      <TableCell>
                        <Input
                          type="number"
                          value={item.accepted_quantity}
                          onChange={(e) =>
                            handleItemChange(index, 'accepted_quantity', parseFloat(e.target.value) || 0)
                          }
                          min="0"
                          max={item.received_quantity}
                          step="0.01"
                          className="bg-green-50"
                        />
                      </TableCell>
                      <TableCell>
                        <Input
                          type="number"
                          value={item.rejected_quantity}
                          onChange={(e) =>
                            handleItemChange(index, 'rejected_quantity', parseFloat(e.target.value) || 0)
                          }
                          min="0"
                          max={item.received_quantity}
                          step="0.01"
                          className="bg-red-50"
                        />
                      </TableCell>
                      <TableCell>{item.unit_of_measure}</TableCell>
                      <TableCell>
                        <Input
                          value={item.batch_number}
                          onChange={(e) => handleItemChange(index, 'batch_number', e.target.value)}
                          placeholder="Batch"
                        />
                      </TableCell>
                      <TableCell>
                        <Input
                          value={item.remarks}
                          onChange={(e) => handleItemChange(index, 'remarks', e.target.value)}
                          placeholder="Remarks"
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Remarks */}
      <Card>
        <CardHeader>
          <CardTitle>Additional Information</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <Label htmlFor="remarks">Remarks</Label>
            <Textarea
              id="remarks"
              value={formData.remarks}
              onChange={(e) => handleChange('remarks', e.target.value)}
              placeholder="Any additional remarks or observations"
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
          {loading ? 'Saving...' : grn ? 'Update GRN' : 'Create GRN'}
        </Button>
      </div>
    </form>
  );
}
