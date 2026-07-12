/**
 * Purchase Order Detail Page
 * Displays complete PO information with approval and lifecycle actions
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import {
  ArrowLeft,
  Edit,
  Check,
  X,
  FileText,
  Package,
  Clock,
  MapPin,
  User,
  Phone,
  Mail,
  Calendar,
  Download,
  Send,
} from 'lucide-react';
import { procurementService } from '@/services/procurement.service';
import type { PurchaseOrder, GoodsReceiptNote } from '@/types/procurement';

interface PurchaseOrderDetailPageProps {
  params: {
    id: string;
  };
}

export default function PurchaseOrderDetailPage({ params }: PurchaseOrderDetailPageProps) {
  const router = useRouter();
  const [po, setPo] = useState<PurchaseOrder | null>(null);
  const [grns, setGrns] = useState<GoodsReceiptNote[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showApproveDialog, setShowApproveDialog] = useState(false);
  const [showCancelDialog, setShowCancelDialog] = useState(false);

  useEffect(() => {
    fetchPODetails();
    fetchGRNs();
  }, [params.id]);

  const fetchPODetails = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await procurementService.purchaseOrder.getById(params.id);
      if (response.success && response.data) {
        setPo(response.data);
      } else {
        setError(response.message || 'Failed to fetch purchase order details');
      }
    } catch (err) {
      setError('An error occurred while fetching purchase order details');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchGRNs = async () => {
    try {
      const response = await procurementService.grn.getAll({ po_id: params.id });
      if (response.success && response.data) {
        setGrns(response.data);
      }
    } catch (err) {
      console.error('Failed to fetch GRNs:', err);
    }
  };

  const handleApprove = async () => {
    if (!po) return;

    try {
      setActionLoading(true);
      const response = await procurementService.purchaseOrder.approve(po.id);
      if (response.success) {
        setShowApproveDialog(false);
        fetchPODetails();
      } else {
        setError(response.message || 'Failed to approve purchase order');
      }
    } catch (err) {
      setError('An error occurred while approving the purchase order');
      console.error(err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleCancel = async () => {
    if (!po) return;

    try {
      setActionLoading(true);
      const response = await procurementService.purchaseOrder.cancel(po.id);
      if (response.success) {
        setShowCancelDialog(false);
        fetchPODetails();
      } else {
        setError(response.message || 'Failed to cancel purchase order');
      }
    } catch (err) {
      setError('An error occurred while canceling the purchase order');
      console.error(err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleSendToVendor = async () => {
    if (!po) return;

    try {
      setActionLoading(true);
      const response = await procurementService.purchaseOrder.send(po.id);
      if (response.success) {
        alert('Purchase Order sent to vendor successfully');
        fetchPODetails();
      } else {
        setError(response.message || 'Failed to send purchase order');
      }
    } catch (err) {
      setError('An error occurred while sending the purchase order');
      console.error(err);
    } finally {
      setActionLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2,
    }).format(amount);
  };

  const formatDate = (date: string | Date) => {
    return new Date(date).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const getStatusBadgeClass = (status: string) => {
    const statusClasses = {
      draft: 'bg-gray-100 text-gray-800',
      pending_approval: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-green-100 text-green-800',
      sent: 'bg-blue-100 text-blue-800',
      acknowledged: 'bg-blue-100 text-blue-800',
      partially_received: 'bg-orange-100 text-orange-800',
      fully_received: 'bg-green-100 text-green-800',
      completed: 'bg-green-100 text-green-800',
      cancelled: 'bg-red-100 text-red-800',
    };
    return statusClasses[status as keyof typeof statusClasses] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading purchase order details...</div>
      </div>
    );
  }

  if (error || !po) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error || 'Purchase order not found'}
        </div>
        <Button onClick={() => router.push('/procurement/purchase-orders')} className="mt-4">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Purchase Orders
        </Button>
      </div>
    );
  }

  const canApprove = po.status === 'pending_approval';
  const canEdit = po.status === 'draft' || po.status === 'pending_approval';
  const canCancel = ['draft', 'pending_approval', 'approved'].includes(po.status);
  const canSend = po.status === 'approved';

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.push('/procurement/purchase-orders')}
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <div>
            <h1 className="text-3xl font-bold">{po.po_number}</h1>
            <p className="text-gray-600">Purchase Order Details</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {canEdit && (
            <Button
              variant="outline"
              onClick={() => router.push(`/procurement/purchase-orders/${po.id}/edit`)}
            >
              <Edit className="w-4 h-4 mr-2" />
              Edit
            </Button>
          )}
          {canSend && (
            <Button variant="outline" onClick={handleSendToVendor} disabled={actionLoading}>
              <Send className="w-4 h-4 mr-2" />
              Send to Vendor
            </Button>
          )}
          {canApprove && (
            <Button onClick={() => setShowApproveDialog(true)} disabled={actionLoading}>
              <Check className="w-4 h-4 mr-2" />
              Approve
            </Button>
          )}
          {canCancel && (
            <Button
              variant="destructive"
              onClick={() => setShowCancelDialog(true)}
              disabled={actionLoading}
            >
              <X className="w-4 h-4 mr-2" />
              Cancel PO
            </Button>
          )}
          <Button variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Download PDF
          </Button>
        </div>
      </div>

      {/* Status and Quick Info */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 mb-2">
              <FileText className="w-4 h-4 text-gray-500" />
              <span className="text-sm text-gray-600">Status</span>
            </div>
            <span
              className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getStatusBadgeClass(
                po.status
              )}`}
            >
              {po.status.replace(/_/g, ' ').toUpperCase()}
            </span>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 mb-2">
              <Calendar className="w-4 h-4 text-gray-500" />
              <span className="text-sm text-gray-600">PO Date</span>
            </div>
            <div className="text-lg font-semibold">{formatDate(po.po_date)}</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 mb-2">
              <Clock className="w-4 h-4 text-gray-500" />
              <span className="text-sm text-gray-600">Expected Delivery</span>
            </div>
            <div className="text-lg font-semibold">
              {formatDate(po.expected_delivery_date)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 mb-2">
              <Package className="w-4 h-4 text-gray-500" />
              <span className="text-sm text-gray-600">Total Amount</span>
            </div>
            <div className="text-lg font-semibold text-green-600">
              {formatCurrency(po.total_amount)}
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="details" className="space-y-6">
        <TabsList>
          <TabsTrigger value="details">PO Details</TabsTrigger>
          <TabsTrigger value="items">Line Items</TabsTrigger>
          <TabsTrigger value="delivery">Delivery Info</TabsTrigger>
          <TabsTrigger value="grns">
            GRNs <span className="ml-2 text-xs">({grns.length})</span>
          </TabsTrigger>
          <TabsTrigger value="history">History</TabsTrigger>
        </TabsList>

        {/* Details Tab */}
        <TabsContent value="details" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Vendor Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="w-5 h-5" />
                  Vendor Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <div className="text-sm text-gray-600">Vendor Name</div>
                  <Link
                    href={`/procurement/vendors/${po.vendor_id}`}
                    className="font-medium text-blue-600 hover:underline"
                  >
                    Vendor Name
                  </Link>
                </div>
                <div>
                  <div className="text-sm text-gray-600">Payment Terms</div>
                  <div className="font-medium">
                    {po.payment_terms.replace(/_/g, ' ').toUpperCase()}
                  </div>
                </div>
                {po.advance_payment_percentage > 0 && (
                  <div>
                    <div className="text-sm text-gray-600">Advance Payment</div>
                    <div className="font-medium">
                      {po.advance_payment_percentage}% ({formatCurrency(po.advance_payment_amount)})
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Reference Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="w-5 h-5" />
                  Reference Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {po.rfq_id && (
                  <div>
                    <div className="text-sm text-gray-600">Related RFQ</div>
                    <Link
                      href={`/procurement/rfq/${po.rfq_id}`}
                      className="font-medium text-blue-600 hover:underline"
                    >
                      View RFQ
                    </Link>
                  </div>
                )}
                {po.requisition_id && (
                  <div>
                    <div className="text-sm text-gray-600">Related Requisition</div>
                    <Link
                      href={`/procurement/requisitions/${po.requisition_id}`}
                      className="font-medium text-blue-600 hover:underline"
                    >
                      View Requisition
                    </Link>
                  </div>
                )}
                {po.approved_at && (
                  <div>
                    <div className="text-sm text-gray-600">Approved At</div>
                    <div className="font-medium">{formatDate(po.approved_at)}</div>
                  </div>
                )}
                {po.acknowledged_by_vendor && (
                  <div>
                    <div className="text-sm text-gray-600">Vendor Acknowledged</div>
                    <div className="font-medium text-green-600">
                      ✓ {po.acknowledged_at && formatDate(po.acknowledged_at)}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Terms and Conditions */}
          {po.terms_and_conditions && (
            <Card>
              <CardHeader>
                <CardTitle>Terms & Conditions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="whitespace-pre-wrap">{po.terms_and_conditions}</div>
              </CardContent>
            </Card>
          )}

          {/* Special Instructions */}
          {po.special_instructions && (
            <Card>
              <CardHeader>
                <CardTitle>Special Instructions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="whitespace-pre-wrap">{po.special_instructions}</div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Items Tab */}
        <TabsContent value="items">
          <Card>
            <CardHeader>
              <CardTitle>Purchase Order Items</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-12">#</TableHead>
                      <TableHead>Item Code</TableHead>
                      <TableHead>Item Name</TableHead>
                      <TableHead>Specification</TableHead>
                      <TableHead className="text-right">Ordered Qty</TableHead>
                      <TableHead className="text-right">Received Qty</TableHead>
                      <TableHead>UOM</TableHead>
                      <TableHead className="text-right">Unit Price</TableHead>
                      <TableHead className="text-right">Tax %</TableHead>
                      <TableHead className="text-right">Discount %</TableHead>
                      <TableHead className="text-right">Net Amount</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {po.items?.map((item, index) => (
                      <TableRow key={item.id}>
                        <TableCell className="font-medium">{index + 1}</TableCell>
                        <TableCell>{item.item_code || '-'}</TableCell>
                        <TableCell>
                          <div className="font-medium">{item.item_name}</div>
                          {item.description && (
                            <div className="text-sm text-gray-500">{item.description}</div>
                          )}
                        </TableCell>
                        <TableCell className="text-sm">{item.specification || '-'}</TableCell>
                        <TableCell className="text-right font-medium">
                          {item.ordered_quantity.toFixed(2)}
                        </TableCell>
                        <TableCell className="text-right">
                          <span
                            className={
                              item.received_quantity >= item.ordered_quantity
                                ? 'text-green-600 font-medium'
                                : 'text-orange-600'
                            }
                          >
                            {item.received_quantity.toFixed(2)}
                          </span>
                        </TableCell>
                        <TableCell>{item.unit_of_measure}</TableCell>
                        <TableCell className="text-right">
                          {formatCurrency(item.unit_price)}
                        </TableCell>
                        <TableCell className="text-right">{item.tax_percentage}%</TableCell>
                        <TableCell className="text-right">{item.discount_percentage}%</TableCell>
                        <TableCell className="text-right font-medium">
                          {formatCurrency(item.net_amount)}
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
                    <span className="font-medium">{formatCurrency(po.subtotal)}</span>
                  </div>
                  {po.discount_amount > 0 && (
                    <div className="flex justify-between items-center py-2">
                      <span className="text-gray-600">Discount:</span>
                      <span className="font-medium text-red-600">
                        - {formatCurrency(po.discount_amount)}
                      </span>
                    </div>
                  )}
                  {po.tax_amount > 0 && (
                    <div className="flex justify-between items-center py-2">
                      <span className="text-gray-600">Tax:</span>
                      <span className="font-medium">+ {formatCurrency(po.tax_amount)}</span>
                    </div>
                  )}
                  <div className="flex justify-between items-center py-2 border-t-2 border-gray-900">
                    <span className="text-lg font-bold">Total Amount:</span>
                    <span className="text-lg font-bold text-green-600">
                      {formatCurrency(po.total_amount)}
                    </span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Delivery Info Tab */}
        <TabsContent value="delivery">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MapPin className="w-5 h-5" />
                Delivery Information
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="text-sm text-gray-600 mb-1">Delivery Address</div>
                <div className="font-medium">
                  {po.delivery_address_line1}
                  {po.delivery_address_line2 && <>, {po.delivery_address_line2}</>}
                </div>
                <div className="text-gray-600">
                  {po.delivery_city}, {po.delivery_state} - {po.delivery_pincode}
                </div>
                <div className="text-gray-600">{po.delivery_country}</div>
              </div>

              {po.delivery_contact_person && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t">
                  <div>
                    <div className="text-sm text-gray-600 mb-1 flex items-center gap-2">
                      <User className="w-4 h-4" />
                      Contact Person
                    </div>
                    <div className="font-medium">{po.delivery_contact_person}</div>
                  </div>
                  {po.delivery_contact_phone && (
                    <div>
                      <div className="text-sm text-gray-600 mb-1 flex items-center gap-2">
                        <Phone className="w-4 h-4" />
                        Contact Phone
                      </div>
                      <div className="font-medium">{po.delivery_contact_phone}</div>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* GRNs Tab */}
        <TabsContent value="grns">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Goods Receipt Notes</CardTitle>
                {po.status === 'sent' ||
                po.status === 'acknowledged' ||
                po.status === 'partially_received' ? (
                  <Button onClick={() => router.push(`/procurement/grn/new?po_id=${po.id}`)}>
                    <Package className="w-4 h-4 mr-2" />
                    Create GRN
                  </Button>
                ) : null}
              </div>
            </CardHeader>
            <CardContent>
              {grns.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <Package className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                  <p>No goods receipt notes found for this purchase order.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {grns.map((grn) => (
                    <div
                      key={grn.id}
                      className="border rounded-lg p-4 hover:bg-gray-50 cursor-pointer"
                      onClick={() => router.push(`/procurement/grn/${grn.id}`)}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="font-medium">{grn.grn_number}</div>
                        <span
                          className={`px-3 py-1 rounded-full text-sm ${getStatusBadgeClass(
                            grn.status
                          )}`}
                        >
                          {grn.status.replace(/_/g, ' ').toUpperCase()}
                        </span>
                      </div>
                      <div className="text-sm text-gray-600">
                        Receipt Date: {formatDate(grn.receipt_date)}
                      </div>
                      {grn.challan_number && (
                        <div className="text-sm text-gray-600">
                          Challan: {grn.challan_number}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* History Tab */}
        <TabsContent value="history">
          <Card>
            <CardHeader>
              <CardTitle>Purchase Order History</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-start gap-4 pb-4 border-b">
                  <div className="w-2 h-2 bg-blue-600 rounded-full mt-2" />
                  <div className="flex-1">
                    <div className="font-medium">PO Created</div>
                    <div className="text-sm text-gray-600">
                      {formatDate(po.created_at)} at{' '}
                      {new Date(po.created_at).toLocaleTimeString('en-IN')}
                    </div>
                  </div>
                </div>

                {po.approved_at && (
                  <div className="flex items-start gap-4 pb-4 border-b">
                    <div className="w-2 h-2 bg-green-600 rounded-full mt-2" />
                    <div className="flex-1">
                      <div className="font-medium">PO Approved</div>
                      <div className="text-sm text-gray-600">
                        {formatDate(po.approved_at)} at{' '}
                        {new Date(po.approved_at).toLocaleTimeString('en-IN')}
                      </div>
                    </div>
                  </div>
                )}

                {po.acknowledged_at && (
                  <div className="flex items-start gap-4 pb-4 border-b">
                    <div className="w-2 h-2 bg-blue-600 rounded-full mt-2" />
                    <div className="flex-1">
                      <div className="font-medium">Vendor Acknowledged</div>
                      <div className="text-sm text-gray-600">
                        {formatDate(po.acknowledged_at)} at{' '}
                        {new Date(po.acknowledged_at).toLocaleTimeString('en-IN')}
                      </div>
                    </div>
                  </div>
                )}

                <div className="flex items-start gap-4">
                  <div className="w-2 h-2 bg-gray-400 rounded-full mt-2" />
                  <div className="flex-1">
                    <div className="font-medium">Last Updated</div>
                    <div className="text-sm text-gray-600">
                      {formatDate(po.updated_at)} at{' '}
                      {new Date(po.updated_at).toLocaleTimeString('en-IN')}
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Approve Dialog */}
      <AlertDialog open={showApproveDialog} onOpenChange={setShowApproveDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Approve Purchase Order</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to approve this purchase order? This action will allow the PO
              to be sent to the vendor.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={actionLoading}>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleApprove} disabled={actionLoading}>
              {actionLoading ? 'Approving...' : 'Approve'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Cancel Dialog */}
      <AlertDialog open={showCancelDialog} onOpenChange={setShowCancelDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Cancel Purchase Order</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to cancel this purchase order? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={actionLoading}>No, Keep It</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleCancel}
              disabled={actionLoading}
              className="bg-red-600 hover:bg-red-700"
            >
              {actionLoading ? 'Cancelling...' : 'Yes, Cancel PO'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
