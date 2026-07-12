/**
 * Invoice Form Component
 * Form for creating and editing Vendor Invoices
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
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
import { Save, X, Plus, Trash2, Calendar, FileText, User, AlertTriangle } from 'lucide-react';
import { procurementService } from '@/services/procurement.service';
import type { VendorInvoice, PurchaseOrder, Vendor, GoodsReceiptNote } from '@/types/procurement';

interface InvoiceFormProps {
  invoice?: VendorInvoice;
  onSuccess?: () => void;
  onCancel?: () => void;
}

interface InvoiceItemData {
  po_item_id: string;
  item_code: string;
  item_name: string;
  description: string;
  quantity: number;
  unit_of_measure: string;
  unit_price: number;
  total_price: number;
  tax_percentage: number;
  tax_amount: number;
  discount_percentage: number;
  discount_amount: number;
  net_amount: number;
}

interface InvoiceFormData {
  vendor_invoice_number: string;
  invoice_date: string;
  due_date: string;
  po_id: string;
  grn_id: string;
  vendor_id: string;
  gst_number: string;
  cgst_amount: number;
  sgst_amount: number;
  igst_amount: number;
  other_charges: number;
  tolerance_percentage: number;
  invoice_file_url: string;
  supporting_documents: string;
  remarks: string;
  items: InvoiceItemData[];
}

export default function InvoiceForm({ invoice, onSuccess, onCancel }: InvoiceFormProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const poIdFromQuery = searchParams.get('po_id');
  const grnIdFromQuery = searchParams.get('grn_id');

  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [purchaseOrders, setPurchaseOrders] = useState<PurchaseOrder[]>([]);
  const [grns, setGrns] = useState<GoodsReceiptNote[]>([]);
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [selectedPO, setSelectedPO] = useState<PurchaseOrder | null>(null);
  const [selectedGRN, setSelectedGRN] = useState<GoodsReceiptNote | null>(null);
  const [loadingPOs, setLoadingPOs] = useState(true);
  const [matchingResult, setMatchingResult] = useState<any>(null);

  const today = new Date().toISOString().split('T')[0];
  const defaultDueDate = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)
    .toISOString()
    .split('T')[0];

  const [formData, setFormData] = useState<InvoiceFormData>({
    vendor_invoice_number: invoice?.vendor_invoice_number || '',
    invoice_date: invoice?.invoice_date
      ? new Date(invoice.invoice_date).toISOString().split('T')[0]
      : today,
    due_date: invoice?.due_date
      ? new Date(invoice.due_date).toISOString().split('T')[0]
      : defaultDueDate,
    po_id: invoice?.po_id || poIdFromQuery || '',
    grn_id: invoice?.grn_id || grnIdFromQuery || '',
    vendor_id: invoice?.vendor_id || '',
    gst_number: invoice?.gst_number || '',
    cgst_amount: invoice?.cgst_amount || 0,
    sgst_amount: invoice?.sgst_amount || 0,
    igst_amount: invoice?.igst_amount || 0,
    other_charges: invoice?.other_charges || 0,
    tolerance_percentage: invoice?.tolerance_percentage || 5,
    invoice_file_url: invoice?.invoice_file_url || '',
    supporting_documents: invoice?.supporting_documents || '',
    remarks: invoice?.remarks || '',
    items:
      invoice?.items?.map((item) => ({
        po_item_id: item.po_item_id || '',
        item_code: item.item_code || '',
        item_name: item.item_name,
        description: item.description || '',
        quantity: item.quantity,
        unit_of_measure: item.unit_of_measure,
        unit_price: item.unit_price,
        total_price: item.total_price,
        tax_percentage: item.tax_percentage,
        tax_amount: item.tax_amount,
        discount_percentage: item.discount_percentage,
        discount_amount: item.discount_amount,
        net_amount: item.net_amount,
      })) || [],
  });

  useEffect(() => {
    fetchPurchaseOrders();
    fetchVendors();
  }, []);

  useEffect(() => {
    if (formData.po_id) {
      fetchPODetails(formData.po_id);
      fetchGRNsForPO(formData.po_id);
    }
  }, [formData.po_id]);

  useEffect(() => {
    if (formData.grn_id) {
      fetchGRNDetails(formData.grn_id);
    }
  }, [formData.grn_id]);

  const fetchPurchaseOrders = async () => {
    try {
      setLoadingPOs(true);
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

  const fetchVendors = async () => {
    try {
      const response = await procurementService.vendor.getAll({ status: 'active' });
      if (response.success && response.data) {
        setVendors(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch vendors:', error);
    }
  };

  const fetchPODetails = async (poId: string) => {
    try {
      const response = await procurementService.purchaseOrder.getById(poId);
      if (response.success && response.data) {
        setSelectedPO(response.data);
        setFormData((prev) => ({ ...prev, vendor_id: response.data.vendor_id }));
        if (!invoice && response.data.items) {
          setFormData((prev) => ({
            ...prev,
            items: response.data.items.map((poItem) => ({
              po_item_id: poItem.id,
              item_code: poItem.item_code || '',
              item_name: poItem.item_name,
              description: poItem.description || '',
              quantity: poItem.ordered_quantity,
              unit_of_measure: poItem.unit_of_measure,
              unit_price: poItem.unit_price,
              total_price: poItem.total_price,
              tax_percentage: poItem.tax_percentage,
              tax_amount: poItem.tax_amount,
              discount_percentage: poItem.discount_percentage,
              discount_amount: poItem.discount_amount,
              net_amount: poItem.net_amount,
            })),
          }));
        }
      }
    } catch (error) {
      console.error('Failed to fetch PO details:', error);
    }
  };

  const fetchGRNsForPO = async (poId: string) => {
    try {
      const response = await procurementService.grn.getAll({ po_id: poId, status: 'accepted' });
      if (response.success && response.data) {
        setGrns(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch GRNs:', error);
    }
  };

  const fetchGRNDetails = async (grnId: string) => {
    try {
      const response = await procurementService.grn.getById(grnId);
      if (response.success && response.data) {
        setSelectedGRN(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch GRN details:', error);
    }
  };

  const handleChange = (field: keyof InvoiceFormData, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const handleItemChange = (index: number, field: keyof InvoiceItemData, value: any) => {
    setFormData((prev) => {
      const newItems = [...prev.items];
      newItems[index] = { ...newItems[index], [field]: value };

      const item = newItems[index];
      const quantity = item.quantity;
      const unitPrice = item.unit_price;

      item.total_price = quantity * unitPrice;
      item.tax_amount = (item.total_price * item.tax_percentage) / 100;
      item.discount_amount = (item.total_price * item.discount_percentage) / 100;
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
          po_item_id: '',
          item_code: '',
          item_name: '',
          description: '',
          quantity: 1,
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
    const items_net = formData.items.reduce((sum, item) => sum + item.net_amount, 0);
    const total_amount = items_net + formData.other_charges;

    return { subtotal, tax_amount, discount_amount, total_amount };
  };

  const performMatching = async () => {
    if (!formData.po_id) {
      setErrors({ po_id: 'Please select a PO to perform matching' });
      return;
    }

    try {
      const totals = calculateTotals();
      const response = await procurementService.invoice.match(formData.po_id, {
        invoice_amount: totals.total_amount,
        grn_id: formData.grn_id || null,
      });
      if (response.success && response.data) {
        setMatchingResult(response.data);
      }
    } catch (error) {
      console.error('Failed to perform matching:', error);
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.vendor_invoice_number.trim()) {
      newErrors.vendor_invoice_number = 'Vendor invoice number is required';
    }
    if (!formData.invoice_date) {
      newErrors.invoice_date = 'Invoice date is required';
    }
    if (!formData.due_date) {
      newErrors.due_date = 'Due date is required';
    }
    if (formData.invoice_date && formData.due_date && 
        new Date(formData.due_date) <= new Date(formData.invoice_date)) {
      newErrors.due_date = 'Due date must be after invoice date';
    }
    if (!formData.po_id) {
      newErrors.po_id = 'Purchase Order is required';
    }
    if (!formData.vendor_id) {
      newErrors.vendor_id = 'Vendor is required';
    }
    if (formData.items.length === 0) {
      newErrors.items = 'At least one item is required';
    }

    formData.items.forEach((item, index) => {
      if (!item.item_name.trim()) {
        newErrors[`items.${index}.item_name`] = 'Item name is required';
      }
      if (item.quantity <= 0) {
        newErrors[`items.${index}.quantity`] = 'Quantity must be greater than 0';
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
        subtotal: totals.subtotal,
        tax_amount: totals.tax_amount,
        discount_amount: totals.discount_amount,
        total_amount: totals.total_amount,
      };

      let response;
      if (invoice?.id) {
        response = await procurementService.invoice.update(invoice.id, payload);
      } else {
        response = await procurementService.invoice.create(payload);
      }

      if (response.success) {
        if (onSuccess) {
          onSuccess();
        } else {
          router.push('/procurement/invoices');
        }
      } else {
        setErrors({ submit: response.message || 'Failed to save invoice' });
      }
    } catch (error) {
      console.error('Failed to save invoice:', error);
      setErrors({ submit: 'An error occurred while saving the invoice' });
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    if (onCancel) {
      onCancel();
    } else {
      router.push('/procurement/invoices');
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

      {/* Matching Result */}
      {matchingResult && (
        <Card className={matchingResult.matched ? 'border-green-500' : 'border-yellow-500'}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {matchingResult.matched ? (
                <span className="text-green-600">✓ 3-Way Matching: PASSED</span>
              ) : (
                <span className="text-yellow-600">⚠ 3-Way Matching: ISSUES FOUND</span>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div>
                <span className="font-medium">Status:</span> {matchingResult.matching_status.replace(/_/g, ' ').toUpperCase()}
              </div>
              {matchingResult.po_amount_variance !== 0 && (
                <div className="text-yellow-700">
                  <span className="font-medium">PO Amount Variance:</span> {formatCurrency(matchingResult.po_amount_variance)}
                </div>
              )}
              {matchingResult.grn_quantity_variance !== 0 && (
                <div className="text-yellow-700">
                  <span className="font-medium">GRN Quantity Variance:</span> {matchingResult.grn_quantity_variance}
                </div>
              )}
              {matchingResult.issues && matchingResult.issues.length > 0 && (
                <div className="mt-3">
                  <div className="font-medium mb-1">Issues:</div>
                  <ul className="list-disc list-inside space-y-1 text-sm">
                    {matchingResult.issues.map((issue: string, idx: number) => (
                      <li key={idx} className="text-red-600">{issue}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Invoice Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Invoice Information
          </CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="vendor_invoice_number">
              Vendor Invoice Number <span className="text-red-500">*</span>
            </Label>
            <Input
              id="vendor_invoice_number"
              value={formData.vendor_invoice_number}
              onChange={(e) => handleChange('vendor_invoice_number', e.target.value)}
              placeholder="Enter vendor's invoice number"
              className={errors.vendor_invoice_number ? 'border-red-500' : ''}
            />
            {errors.vendor_invoice_number && (
              <p className="text-sm text-red-500">{errors.vendor_invoice_number}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="gst_number">GST Number</Label>
            <Input
              id="gst_number"
              value={formData.gst_number}
              onChange={(e) => handleChange('gst_number', e.target.value)}
              placeholder="Vendor GST number"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="invoice_date">
              Invoice Date <span className="text-red-500">*</span>
            </Label>
            <div className="relative">
              <Input
                id="invoice_date"
                type="date"
                value={formData.invoice_date}
                onChange={(e) => handleChange('invoice_date', e.target.value)}
                max={today}
                className={errors.invoice_date ? 'border-red-500' : ''}
              />
              <Calendar className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4 pointer-events-none" />
            </div>
            {errors.invoice_date && <p className="text-sm text-red-500">{errors.invoice_date}</p>}
          </div>

          <div className="space-y-2">
            <Label htmlFor="due_date">
              Due Date <span className="text-red-500">*</span>
            </Label>
            <div className="relative">
              <Input
                id="due_date"
                type="date"
                value={formData.due_date}
                onChange={(e) => handleChange('due_date', e.target.value)}
                min={formData.invoice_date}
                className={errors.due_date ? 'border-red-500' : ''}
              />
              <Calendar className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4 pointer-events-none" />
            </div>
            {errors.due_date && <p className="text-sm text-red-500">{errors.due_date}</p>}
          </div>
        </CardContent>
      </Card>

      {/* PO and Vendor Selection */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="w-5 h-5" />
            Reference Information
          </CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="po_id">
              Purchase Order <span className="text-red-500">*</span>
            </Label>
            <Select
              value={formData.po_id}
              onValueChange={(value) => handleChange('po_id', value)}
              disabled={!!invoice}
            >
              <SelectTrigger className={errors.po_id ? 'border-red-500' : ''}>
                <SelectValue placeholder="Select purchase order" />
              </SelectTrigger>
              <SelectContent>
                {loadingPOs ? (
                  <SelectItem value="loading" disabled>Loading POs...</SelectItem>
                ) : purchaseOrders.length === 0 ? (
                  <SelectItem value="none" disabled>No POs found</SelectItem>
                ) : (
                  purchaseOrders.map((po) => (
                    <SelectItem key={po.id} value={po.id}>
                      {po.po_number} - {formatCurrency(po.total_amount)}
                    </SelectItem>
                  ))
                )}
              </SelectContent>
            </Select>
            {errors.po_id && <p className="text-sm text-red-500">{errors.po_id}</p>}
          </div>

          <div className="space-y-2">
            <Label htmlFor="grn_id">GRN (Optional)</Label>
            <Select
              value={formData.grn_id}
              onValueChange={(value) => handleChange('grn_id', value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select GRN (optional)" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">No GRN</SelectItem>
                {grns.map((grn) => (
                  <SelectItem key={grn.id} value={grn.id}>
                    {grn.grn_number} - {new Date(grn.grn_date).toLocaleDateString()}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="vendor_id">
              Vendor <span className="text-red-500">*</span>
            </Label>
            <Select
              value={formData.vendor_id}
              onValueChange={(value) => handleChange('vendor_id', value)}
              disabled={!!selectedPO}
            >
              <SelectTrigger className={errors.vendor_id ? 'border-red-500' : ''}>
                <SelectValue placeholder="Select vendor" />
              </SelectTrigger>
              <SelectContent>
                {vendors.map((vendor) => (
                  <SelectItem key={vendor.id} value={vendor.id}>
                    {vendor.vendor_name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.vendor_id && <p className="text-sm text-red-500">{errors.vendor_id}</p>}
          </div>

          <div className="space-y-2">
            <Label htmlFor="tolerance_percentage">Tolerance %</Label>
            <Input
              id="tolerance_percentage"
              type="number"
              value={formData.tolerance_percentage}
              onChange={(e) => handleChange('tolerance_percentage', parseFloat(e.target.value) || 0)}
              min="0"
              max="100"
              step="0.01"
            />
          </div>

          {formData.po_id && (
            <div className="md:col-span-2">
              <Button type="button" onClick={performMatching} variant="outline" className="w-full">
                <AlertTriangle className="w-4 h-4 mr-2" />
                Perform 3-Way Matching
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Invoice Items */}
      {formData.items.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Invoice Items</CardTitle>
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
                          type="number"
                          value={item.quantity}
                          onChange={(e) => handleItemChange(index, 'quantity', parseFloat(e.target.value) || 0)}
                          min="0"
                          step="0.01"
                          className={errors[`items.${index}.quantity`] ? 'border-red-500' : ''}
                        />
                      </TableCell>
                      <TableCell>
                        <Input
                          value={item.unit_of_measure}
                          onChange={(e) => handleItemChange(index, 'unit_of_measure', e.target.value)}
                        />
                      </TableCell>
                      <TableCell>
                        <Input
                          type="number"
                          value={item.unit_price}
                          onChange={(e) => handleItemChange(index, 'unit_price', parseFloat(e.target.value) || 0)}
                          min="0"
                          step="0.01"
                          className={errors[`items.${index}.unit_price`] ? 'border-red-500' : ''}
                        />
                      </TableCell>
                      <TableCell>
                        <Input
                          type="number"
                          value={item.tax_percentage}
                          onChange={(e) => handleItemChange(index, 'tax_percentage', parseFloat(e.target.value) || 0)}
                          min="0"
                          max="100"
                          step="0.01"
                        />
                      </TableCell>
                      <TableCell>
                        <Input
                          type="number"
                          value={item.discount_percentage}
                          onChange={(e) => handleItemChange(index, 'discount_percentage', parseFloat(e.target.value) || 0)}
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
                    <span className="font-medium text-red-600">- {formatCurrency(totals.discount_amount)}</span>
                  </div>
                )}
                {totals.tax_amount > 0 && (
                  <div className="flex justify-between items-center py-2">
                    <span className="text-gray-600">Tax:</span>
                    <span className="font-medium">+ {formatCurrency(totals.tax_amount)}</span>
                  </div>
                )}
                <div className="flex justify-between items-center py-2">
                  <span className="text-gray-600">Other Charges:</span>
                  <Input
                    type="number"
                    value={formData.other_charges}
                    onChange={(e) => handleChange('other_charges', parseFloat(e.target.value) || 0)}
                    min="0"
                    step="0.01"
                    className="w-32 text-right"
                  />
                </div>
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
      )}

      {/* Additional Information */}
      <Card>
        <CardHeader>
          <CardTitle>Additional Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="invoice_file_url">Invoice File URL</Label>
            <Input
              id="invoice_file_url"
              value={formData.invoice_file_url}
              onChange={(e) => handleChange('invoice_file_url', e.target.value)}
              placeholder="URL to invoice PDF or image"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="supporting_documents">Supporting Documents</Label>
            <Textarea
              id="supporting_documents"
              value={formData.supporting_documents}
              onChange={(e) => handleChange('supporting_documents', e.target.value)}
              placeholder="URLs or references to supporting documents"
              rows={2}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="remarks">Remarks</Label>
            <Textarea
              id="remarks"
              value={formData.remarks}
              onChange={(e) => handleChange('remarks', e.target.value)}
              placeholder="Any additional remarks"
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
          {loading ? 'Saving...' : invoice ? 'Update Invoice' : 'Create Invoice'}
        </Button>
      </div>
    </form>
  );
}
