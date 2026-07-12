/**
 * Invoice Detail Page
 * Displays complete invoice information with 3-way matching and approval workflow
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
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import {
  ArrowLeft,
  CheckCircle,
  XCircle,
  FileText,
  Calendar,
  User,
  DollarSign,
  AlertTriangle,
  Download,
  CreditCard,
} from 'lucide-react';
import { procurementService } from '@/services/procurement.service';
import type { VendorInvoice } from '@/types/procurement';

interface InvoiceDetailPageProps {
  params: {
    id: string;
  };
}

export default function InvoiceDetailPage({ params }: InvoiceDetailPageProps) {
  const router = useRouter();
  const [invoice, setInvoice] = useState<VendorInvoice | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showVerifyDialog, setShowVerifyDialog] = useState(false);
  const [showApproveDialog, setShowApproveDialog] = useState(false);
  const [showRejectDialog, setShowRejectDialog] = useState(false);
  const [showPaymentDialog, setShowPaymentDialog] = useState(false);
  const [rejectionReason, setRejectionReason] = useState('');
  const [paymentAmount, setPaymentAmount] = useState(0);
  const [paymentReference, setPaymentReference] = useState('');
  const [matchingResult, setMatchingResult] = useState<any>(null);

  useEffect(() => {
    fetchInvoiceDetails();
  }, [params.id]);

  const fetchInvoiceDetails = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await procurementService.invoice.getById(params.id);
      if (response.success && response.data) {
        setInvoice(response.data);
        setPaymentAmount(response.data.balance_amount);
        // Fetch matching result
        if (response.data.po_id) {
          fetchMatchingResult(response.data.po_id, response.data.total_amount, response.data.grn_id);
        }
      } else {
        setError(response.message || 'Failed to fetch invoice details');
      }
    } catch (err) {
      setError('An error occurred while fetching invoice details');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchMatchingResult = async (poId: string, amount: number, grnId?: string) => {
    try {
      const response = await procurementService.invoice.match(poId, {
        invoice_amount: amount,
        grn_id: grnId || null,
      });
      if (response.success && response.data) {
        setMatchingResult(response.data);
      }
    } catch (err) {
      console.error('Failed to fetch matching result:', err);
    }
  };

  const handleVerify = async () => {
    if (!invoice) return;

    try {
      setActionLoading(true);
      const response = await procurementService.invoice.verify(invoice.id);
      if (response.success) {
        setShowVerifyDialog(false);
        fetchInvoiceDetails();
      } else {
        setError(response.message || 'Failed to verify invoice');
      }
    } catch (err) {
      setError('An error occurred while verifying the invoice');
      console.error(err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleApprove = async () => {
    if (!invoice) return;

    try {
      setActionLoading(true);
      const response = await procurementService.invoice.approve(invoice.id);
      if (response.success) {
        setShowApproveDialog(false);
        fetchInvoiceDetails();
      } else {
        setError(response.message || 'Failed to approve invoice');
      }
    } catch (err) {
      setError('An error occurred while approving the invoice');
      console.error(err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    if (!invoice || !rejectionReason.trim()) {
      setError('Rejection reason is required');
      return;
    }

    try {
      setActionLoading(true);
      const response = await procurementService.invoice.reject(invoice.id, {
        rejection_reason: rejectionReason,
      });
      if (response.success) {
        setShowRejectDialog(false);
        setRejectionReason('');
        fetchInvoiceDetails();
      } else {
        setError(response.message || 'Failed to reject invoice');
      }
    } catch (err) {
      setError('An error occurred while rejecting the invoice');
      console.error(err);
    } finally {
      setActionLoading(false);
    }
  };

  const handlePayment = async () => {
    if (!invoice || paymentAmount <= 0 || paymentAmount > invoice.balance_amount) {
      setError('Invalid payment amount');
      return;
    }

    try {
      setActionLoading(true);
      const response = await procurementService.invoice.recordPayment(invoice.id, {
        amount: paymentAmount,
        payment_reference: paymentReference,
      });
      if (response.success) {
        setShowPaymentDialog(false);
        setPaymentAmount(0);
        setPaymentReference('');
        fetchInvoiceDetails();
      } else {
        setError(response.message || 'Failed to record payment');
      }
    } catch (err) {
      setError('An error occurred while recording payment');
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
      pending: 'bg-yellow-100 text-yellow-800',
      verified: 'bg-blue-100 text-blue-800',
      approved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
      partially_paid: 'bg-orange-100 text-orange-800',
      paid: 'bg-green-100 text-green-800',
    };
    return statusClasses[status as keyof typeof statusClasses] || 'bg-gray-100 text-gray-800';
  };

  const getMatchingBadgeClass = (status: string) => {
    const statusClasses = {
      not_matched: 'bg-gray-100 text-gray-800',
      matched: 'bg-green-100 text-green-800',
      variance: 'bg-yellow-100 text-yellow-800',
      mismatch: 'bg-red-100 text-red-800',
    };
    return statusClasses[status as keyof typeof statusClasses] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading invoice details...</div>
      </div>
    );
  }

  if (error && !invoice) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
        <Button onClick={() => router.push('/procurement/invoices')} className="mt-4">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Invoices
        </Button>
      </div>
    );
  }

  if (!invoice) return null;

  const canVerify = invoice.status === 'pending';
  const canApprove = invoice.status === 'verified';
  const canReject = ['pending', 'verified'].includes(invoice.status);
  const canPay = invoice.status === 'approved' && invoice.balance_amount > 0;
  const isOverdue = new Date(invoice.due_date) < new Date() && invoice.balance_amount > 0;

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={() => router.push('/procurement/invoices')}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <div>
            <h1 className="text-3xl font-bold">{invoice.invoice_number}</h1>
            <p className="text-gray-600">Vendor Invoice: {invoice.vendor_invoice_number}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {canVerify && (
            <Button onClick={() => setShowVerifyDialog(true)} disabled={actionLoading}>
              <CheckCircle className="w-4 h-4 mr-2" />
              Verify Invoice
            </Button>
          )}
          {canApprove && (
            <Button onClick={() => setShowApproveDialog(true)} disabled={actionLoading}>
              <CheckCircle className="w-4 h-4 mr-2" />
              Approve Invoice
            </Button>
          )}
          {canPay && (
            <Button onClick={() => setShowPaymentDialog(true)} disabled={actionLoading} variant="outline">
              <CreditCard className="w-4 h-4 mr-2" />
              Record Payment
            </Button>
          )}
          {canReject && (
            <Button
              variant="destructive"
              onClick={() => setShowRejectDialog(true)}
              disabled={actionLoading}
            >
              <XCircle className="w-4 h-4 mr-2" />
              Reject
            </Button>
          )}
          <Button variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Download PDF
          </Button>
        </div>
      </div>

      {/* Status and Quick Info */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 mb-2">
              <FileText className="w-4 h-4 text-gray-500" />
              <span className="text-sm text-gray-600">Status</span>
            </div>
            <span
              className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getStatusBadgeClass(
                invoice.status
              )}`}
            >
              {invoice.status.replace(/_/g, ' ').toUpperCase()}
            </span>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 mb-2">
              <AlertTriangle className="w-4 h-4 text-gray-500" />
              <span className="text-sm text-gray-600">Matching Status</span>
            </div>
            <span
              className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getMatchingBadgeClass(
                invoice.matching_status
              )}`}
            >
              {invoice.matching_status.replace(/_/g, ' ').toUpperCase()}
            </span>
          </CardContent>
        </Card>

        <Card className={isOverdue ? 'border-red-500' : ''}>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 mb-2">
              <Calendar className="w-4 h-4 text-gray-500" />
              <span className="text-sm text-gray-600">Due Date</span>
            </div>
            <div className={`text-lg font-semibold ${isOverdue ? 'text-red-600' : ''}`}>
              {formatDate(invoice.due_date)}
              {isOverdue && <div className="text-xs text-red-600 mt-1">OVERDUE</div>}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 mb-2">
              <DollarSign className="w-4 h-4 text-gray-500" />
              <span className="text-sm text-gray-600">Total Amount</span>
            </div>
            <div className="text-lg font-semibold text-blue-600">
              {formatCurrency(invoice.total_amount)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 mb-2">
              <DollarSign className="w-4 h-4 text-gray-500" />
              <span className="text-sm text-gray-600">Balance</span>
            </div>
            <div className={`text-lg font-semibold ${invoice.balance_amount > 0 ? 'text-orange-600' : 'text-green-600'}`}>
              {formatCurrency(invoice.balance_amount)}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 3-Way Matching Result */}
      {matchingResult && (
        <Card className={`mb-6 ${matchingResult.matched ? 'border-green-500' : 'border-yellow-500'}`}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {matchingResult.matched ? (
                <>
                  <CheckCircle className="w-5 h-5 text-green-600" />
                  <span className="text-green-600">3-Way Matching: PASSED</span>
                </>
              ) : (
                <>
                  <AlertTriangle className="w-5 h-5 text-yellow-600" />
                  <span className="text-yellow-600">3-Way Matching: VARIANCE DETECTED</span>
                </>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <div className="text-sm text-gray-600 mb-1">PO Amount Variance</div>
                <div className={`text-2xl font-bold ${
                  matchingResult.po_amount_variance === 0 ? 'text-green-600' : 
                  Math.abs(matchingResult.po_amount_variance) <= (invoice.total_amount * invoice.tolerance_percentage / 100) ? 'text-yellow-600' : 
                  'text-red-600'
                }`}>
                  {formatCurrency(Math.abs(matchingResult.po_amount_variance))}
                  {matchingResult.po_amount_variance !== 0 && (
                    <span className="text-sm ml-2">
                      ({matchingResult.po_amount_variance > 0 ? '+' : '-'}
                      {((Math.abs(matchingResult.po_amount_variance) / invoice.total_amount) * 100).toFixed(2)}%)
                    </span>
                  )}
                </div>
              </div>

              <div>
                <div className="text-sm text-gray-600 mb-1">GRN Quantity Variance</div>
                <div className={`text-2xl font-bold ${
                  matchingResult.grn_quantity_variance === 0 ? 'text-green-600' : 'text-yellow-600'
                }`}>
                  {matchingResult.grn_quantity_variance === 0 ? '✓ Matched' : `${matchingResult.grn_quantity_variance} units`}
                </div>
              </div>

              <div>
                <div className="text-sm text-gray-600 mb-1">Tolerance</div>
                <div className="text-2xl font-bold text-gray-600">
                  {invoice.tolerance_percentage}%
                  <span className="text-sm ml-2">({formatCurrency(invoice.total_amount * invoice.tolerance_percentage / 100)})</span>
                </div>
              </div>
            </div>

            {matchingResult.issues && matchingResult.issues.length > 0 && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded">
                <div className="font-medium text-red-800 mb-2">Issues Found:</div>
                <ul className="list-disc list-inside space-y-1">
                  {matchingResult.issues.map((issue: string, idx: number) => (
                    <li key={idx} className="text-red-700 text-sm">{issue}</li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      <Tabs defaultValue="details" className="space-y-6">
        <TabsList>
          <TabsTrigger value="details">Invoice Details</TabsTrigger>
          <TabsTrigger value="items">Line Items</TabsTrigger>
          <TabsTrigger value="matching">Matching Analysis</TabsTrigger>
          <TabsTrigger value="payments">Payments</TabsTrigger>
          <TabsTrigger value="history">History</TabsTrigger>
        </TabsList>

        {/* Details Tab */}
        <TabsContent value="details" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Invoice Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="w-5 h-5" />
                  Invoice Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <div className="text-sm text-gray-600">Invoice Number</div>
                  <div className="font-medium">{invoice.invoice_number}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">Vendor Invoice Number</div>
                  <div className="font-medium">{invoice.vendor_invoice_number}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">Invoice Date</div>
                  <div className="font-medium">{formatDate(invoice.invoice_date)}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">Due Date</div>
                  <div className={`font-medium ${isOverdue ? 'text-red-600' : ''}`}>
                    {formatDate(invoice.due_date)}
                  </div>
                </div>
                {invoice.gst_number && (
                  <div>
                    <div className="text-sm text-gray-600">GST Number</div>
                    <div className="font-medium">{invoice.gst_number}</div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Reference Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="w-5 h-5" />
                  Reference Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <div className="text-sm text-gray-600">Purchase Order</div>
                  <Link
                    href={`/procurement/purchase-orders/${invoice.po_id}`}
                    className="font-medium text-blue-600 hover:underline"
                  >
                    View Purchase Order
                  </Link>
                </div>
                {invoice.grn_id && (
                  <div>
                    <div className="text-sm text-gray-600">Goods Receipt Note</div>
                    <Link
                      href={`/procurement/grn/${invoice.grn_id}`}
                      className="font-medium text-blue-600 hover:underline"
                    >
                      View GRN
                    </Link>
                  </div>
                )}
                {invoice.verified_at && (
                  <div>
                    <div className="text-sm text-gray-600">Verified At</div>
                    <div className="font-medium">{formatDate(invoice.verified_at)}</div>
                  </div>
                )}
                {invoice.approved_at && (
                  <div>
                    <div className="text-sm text-gray-600">Approved At</div>
                    <div className="font-medium">{formatDate(invoice.approved_at)}</div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Tax Breakdown */}
          {(invoice.cgst_amount > 0 || invoice.sgst_amount > 0 || invoice.igst_amount > 0) && (
            <Card>
              <CardHeader>
                <CardTitle>GST Breakdown</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {invoice.cgst_amount > 0 && (
                    <div>
                      <div className="text-sm text-gray-600">CGST</div>
                      <div className="text-lg font-semibold">{formatCurrency(invoice.cgst_amount)}</div>
                    </div>
                  )}
                  {invoice.sgst_amount > 0 && (
                    <div>
                      <div className="text-sm text-gray-600">SGST</div>
                      <div className="text-lg font-semibold">{formatCurrency(invoice.sgst_amount)}</div>
                    </div>
                  )}
                  {invoice.igst_amount > 0 && (
                    <div>
                      <div className="text-sm text-gray-600">IGST</div>
                      <div className="text-lg font-semibold">{formatCurrency(invoice.igst_amount)}</div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Remarks */}
          {invoice.remarks && (
            <Card>
              <CardHeader>
                <CardTitle>Remarks</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="whitespace-pre-wrap">{invoice.remarks}</div>
              </CardContent>
            </Card>
          )}

          {/* Rejection Reason */}
          {invoice.status === 'rejected' && invoice.rejection_reason && (
            <Card className="border-red-500">
              <CardHeader>
                <CardTitle className="text-red-600">Rejection Reason</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="whitespace-pre-wrap text-red-700">{invoice.rejection_reason}</div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Items Tab */}
        <TabsContent value="items">
          <Card>
            <CardHeader>
              <CardTitle>Invoice Line Items</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-12">#</TableHead>
                      <TableHead>Item Code</TableHead>
                      <TableHead>Item Name</TableHead>
                      <TableHead>Description</TableHead>
                      <TableHead className="text-right">Quantity</TableHead>
                      <TableHead>UOM</TableHead>
                      <TableHead className="text-right">Unit Price</TableHead>
                      <TableHead className="text-right">Total</TableHead>
                      <TableHead className="text-right">Tax %</TableHead>
                      <TableHead className="text-right">Tax Amount</TableHead>
                      <TableHead className="text-right">Discount %</TableHead>
                      <TableHead className="text-right">Net Amount</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {invoice.items?.map((item, index) => (
                      <TableRow key={item.id}>
                        <TableCell className="font-medium">{index + 1}</TableCell>
                        <TableCell>{item.item_code || '-'}</TableCell>
                        <TableCell>
                          <div className="font-medium">{item.item_name}</div>
                        </TableCell>
                        <TableCell className="text-sm">{item.description || '-'}</TableCell>
                        <TableCell className="text-right font-medium">
                          {item.quantity.toFixed(2)}
                        </TableCell>
                        <TableCell>{item.unit_of_measure}</TableCell>
                        <TableCell className="text-right">{formatCurrency(item.unit_price)}</TableCell>
                        <TableCell className="text-right">{formatCurrency(item.total_price)}</TableCell>
                        <TableCell className="text-right">{item.tax_percentage}%</TableCell>
                        <TableCell className="text-right">{formatCurrency(item.tax_amount)}</TableCell>
                        <TableCell className="text-right">{item.discount_percentage}%</TableCell>
                        <TableCell className="text-right font-medium text-green-600">
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
                    <span className="font-medium">{formatCurrency(invoice.subtotal)}</span>
                  </div>
                  {invoice.discount_amount > 0 && (
                    <div className="flex justify-between items-center py-2">
                      <span className="text-gray-600">Discount:</span>
                      <span className="font-medium text-red-600">
                        - {formatCurrency(invoice.discount_amount)}
                      </span>
                    </div>
                  )}
                  {invoice.tax_amount > 0 && (
                    <div className="flex justify-between items-center py-2">
                      <span className="text-gray-600">Tax:</span>
                      <span className="font-medium">+ {formatCurrency(invoice.tax_amount)}</span>
                    </div>
                  )}
                  {invoice.other_charges > 0 && (
                    <div className="flex justify-between items-center py-2">
                      <span className="text-gray-600">Other Charges:</span>
                      <span className="font-medium">+ {formatCurrency(invoice.other_charges)}</span>
                    </div>
                  )}
                  <div className="flex justify-between items-center py-2 border-t-2 border-gray-900">
                    <span className="text-lg font-bold">Total Amount:</span>
                    <span className="text-lg font-bold text-green-600">
                      {formatCurrency(invoice.total_amount)}
                    </span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Matching Analysis Tab */}
        <TabsContent value="matching">
          <Card>
            <CardHeader>
              <CardTitle>3-Way Matching Analysis</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Matching Status Overview */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
                <div>
                  <div className="text-sm text-gray-600 mb-1">Matching Status</div>
                  <span
                    className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getMatchingBadgeClass(
                      invoice.matching_status
                    )}`}
                  >
                    {invoice.matching_status.replace(/_/g, ' ').toUpperCase()}
                  </span>
                </div>
                <div>
                  <div className="text-sm text-gray-600 mb-1">Tolerance Percentage</div>
                  <div className="text-lg font-semibold">{invoice.tolerance_percentage}%</div>
                </div>
              </div>

              {/* Variance Details */}
              <div>
                <h3 className="font-semibold mb-3">Variance Analysis</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Card className={invoice.po_amount_variance === 0 ? 'border-green-500' : 'border-yellow-500'}>
                    <CardHeader>
                      <CardTitle className="text-base">PO Amount Variance</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold mb-2">
                        {formatCurrency(Math.abs(invoice.po_amount_variance))}
                      </div>
                      <div className="text-sm text-gray-600">
                        {invoice.po_amount_variance === 0 ? (
                          <span className="text-green-600">✓ Perfectly matched</span>
                        ) : invoice.po_amount_variance > 0 ? (
                          <span className="text-orange-600">Invoice exceeds PO by {((invoice.po_amount_variance / invoice.total_amount) * 100).toFixed(2)}%</span>
                        ) : (
                          <span className="text-blue-600">Invoice less than PO by {((Math.abs(invoice.po_amount_variance) / invoice.total_amount) * 100).toFixed(2)}%</span>
                        )}
                      </div>
                    </CardContent>
                  </Card>

                  <Card className={invoice.grn_quantity_variance === 0 ? 'border-green-500' : 'border-yellow-500'}>
                    <CardHeader>
                      <CardTitle className="text-base">GRN Quantity Variance</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold mb-2">
                        {invoice.grn_quantity_variance === 0 ? '0' : invoice.grn_quantity_variance} units
                      </div>
                      <div className="text-sm text-gray-600">
                        {invoice.grn_quantity_variance === 0 ? (
                          <span className="text-green-600">✓ Quantities matched</span>
                        ) : (
                          <span className="text-yellow-600">Variance detected in received quantities</span>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>

              {/* Recommendation */}
              <div className="p-4 bg-blue-50 border border-blue-200 rounded">
                <div className="font-medium text-blue-800 mb-2">Recommendation:</div>
                <div className="text-blue-700 text-sm">
                  {invoice.matching_status === 'matched' && (
                    <p>✓ All checks passed. Invoice can be approved for payment.</p>
                  )}
                  {invoice.matching_status === 'variance' && (
                    <p>⚠ Minor variances detected within tolerance. Review and approve if acceptable.</p>
                  )}
                  {invoice.matching_status === 'mismatch' && (
                    <p>✗ Significant mismatches detected. Investigate discrepancies before approval.</p>
                  )}
                  {invoice.matching_status === 'not_matched' && (
                    <p>Matching not performed. Run 3-way matching to validate invoice.</p>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Payments Tab */}
        <TabsContent value="payments">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Payment Information</CardTitle>
                {canPay && (
                  <Button onClick={() => setShowPaymentDialog(true)} size="sm">
                    <CreditCard className="w-4 h-4 mr-2" />
                    Record Payment
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Payment Summary */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg">
                <div>
                  <div className="text-sm text-gray-600 mb-1">Total Invoice Amount</div>
                  <div className="text-2xl font-bold text-blue-600">
                    {formatCurrency(invoice.total_amount)}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-600 mb-1">Paid Amount</div>
                  <div className="text-2xl font-bold text-green-600">
                    {formatCurrency(invoice.paid_amount)}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-600 mb-1">Balance Due</div>
                  <div className={`text-2xl font-bold ${invoice.balance_amount > 0 ? 'text-orange-600' : 'text-green-600'}`}>
                    {formatCurrency(invoice.balance_amount)}
                  </div>
                </div>
              </div>

              {/* Payment Status */}
              <div>
                <div className="text-sm font-medium text-gray-600 mb-3">Payment Status</div>
                <div className="relative">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm">
                      {invoice.paid_amount === 0 && 'Not Paid'}
                      {invoice.paid_amount > 0 && invoice.balance_amount > 0 && 'Partially Paid'}
                      {invoice.balance_amount === 0 && 'Fully Paid'}
                    </span>
                    <span className="text-sm font-medium">
                      {((invoice.paid_amount / invoice.total_amount) * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className={`h-3 rounded-full ${
                        invoice.balance_amount === 0 ? 'bg-green-600' : 'bg-orange-600'
                      }`}
                      style={{ width: `${(invoice.paid_amount / invoice.total_amount) * 100}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* Payment Instructions */}
              {invoice.balance_amount > 0 && (
                <div className="p-4 bg-yellow-50 border border-yellow-200 rounded">
                  <div className="font-medium text-yellow-800 mb-1">Pending Payment</div>
                  <div className="text-yellow-700 text-sm">
                    {isOverdue ? (
                      <p>⚠ Payment is overdue. Please process immediately.</p>
                    ) : (
                      <p>Payment due by {formatDate(invoice.due_date)}</p>
                    )}
                  </div>
                </div>
              )}

              {invoice.balance_amount === 0 && (
                <div className="p-4 bg-green-50 border border-green-200 rounded">
                  <div className="font-medium text-green-800 mb-1">Payment Complete</div>
                  <div className="text-green-700 text-sm">
                    ✓ This invoice has been fully paid.
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* History Tab */}
        <TabsContent value="history">
          <Card>
            <CardHeader>
              <CardTitle>Invoice History</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-start gap-4 pb-4 border-b">
                  <div className="w-2 h-2 bg-blue-600 rounded-full mt-2" />
                  <div className="flex-1">
                    <div className="font-medium">Invoice Created</div>
                    <div className="text-sm text-gray-600">
                      {formatDate(invoice.created_at)} at{' '}
                      {new Date(invoice.created_at).toLocaleTimeString('en-IN')}
                    </div>
                  </div>
                </div>

                {invoice.verified_at && (
                  <div className="flex items-start gap-4 pb-4 border-b">
                    <div className="w-2 h-2 bg-blue-600 rounded-full mt-2" />
                    <div className="flex-1">
                      <div className="font-medium">Invoice Verified</div>
                      <div className="text-sm text-gray-600">
                        {formatDate(invoice.verified_at)} at{' '}
                        {new Date(invoice.verified_at).toLocaleTimeString('en-IN')}
                      </div>
                      {invoice.verified_by && (
                        <div className="text-xs text-gray-500 mt-1">
                          Verified by: User ID {invoice.verified_by}
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {invoice.approved_at && (
                  <div className="flex items-start gap-4 pb-4 border-b">
                    <div className="w-2 h-2 bg-green-600 rounded-full mt-2" />
                    <div className="flex-1">
                      <div className="font-medium">Invoice Approved</div>
                      <div className="text-sm text-gray-600">
                        {formatDate(invoice.approved_at)} at{' '}
                        {new Date(invoice.approved_at).toLocaleTimeString('en-IN')}
                      </div>
                      {invoice.approved_by && (
                        <div className="text-xs text-gray-500 mt-1">
                          Approved by: User ID {invoice.approved_by}
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {invoice.status === 'rejected' && invoice.rejection_reason && (
                  <div className="flex items-start gap-4 pb-4 border-b">
                    <div className="w-2 h-2 bg-red-600 rounded-full mt-2" />
                    <div className="flex-1">
                      <div className="font-medium text-red-600">Invoice Rejected</div>
                      <div className="text-sm text-gray-600">
                        {formatDate(invoice.updated_at)}
                      </div>
                      <div className="text-sm text-red-700 mt-2 p-2 bg-red-50 rounded">
                        {invoice.rejection_reason}
                      </div>
                    </div>
                  </div>
                )}

                <div className="flex items-start gap-4">
                  <div className="w-2 h-2 bg-gray-400 rounded-full mt-2" />
                  <div className="flex-1">
                    <div className="font-medium">Last Updated</div>
                    <div className="text-sm text-gray-600">
                      {formatDate(invoice.updated_at)} at{' '}
                      {new Date(invoice.updated_at).toLocaleTimeString('en-IN')}
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Verify Dialog */}
      <AlertDialog open={showVerifyDialog} onOpenChange={setShowVerifyDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Verify Invoice</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to verify this invoice? This confirms that the invoice has been
              reviewed and all details are correct.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={actionLoading}>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleVerify} disabled={actionLoading}>
              {actionLoading ? 'Verifying...' : 'Verify Invoice'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Approve Dialog */}
      <AlertDialog open={showApproveDialog} onOpenChange={setShowApproveDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Approve Invoice</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to approve this invoice for payment? Once approved, the invoice
              will be ready for payment processing.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={actionLoading}>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleApprove} disabled={actionLoading}>
              {actionLoading ? 'Approving...' : 'Approve Invoice'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Reject Dialog */}
      <AlertDialog open={showRejectDialog} onOpenChange={setShowRejectDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Reject Invoice</AlertDialogTitle>
            <AlertDialogDescription>
              Please provide a reason for rejecting this invoice. This action will prevent the
              invoice from being processed for payment.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <div className="py-4">
            <Label htmlFor="rejection_reason">
              Rejection Reason <span className="text-red-500">*</span>
            </Label>
            <Textarea
              id="rejection_reason"
              value={rejectionReason}
              onChange={(e) => setRejectionReason(e.target.value)}
              placeholder="Enter reason for rejection..."
              rows={4}
              className="mt-2"
            />
          </div>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={actionLoading}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleReject}
              disabled={actionLoading || !rejectionReason.trim()}
              className="bg-red-600 hover:bg-red-700"
            >
              {actionLoading ? 'Rejecting...' : 'Reject Invoice'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Payment Dialog */}
      <AlertDialog open={showPaymentDialog} onOpenChange={setShowPaymentDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Record Payment</AlertDialogTitle>
            <AlertDialogDescription>
              Record a payment made for this invoice. You can record partial or full payment.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <div className="py-4 space-y-4">
            <div>
              <Label htmlFor="payment_amount">
                Payment Amount <span className="text-red-500">*</span>
              </Label>
              <Input
                id="payment_amount"
                type="number"
                value={paymentAmount}
                onChange={(e) => setPaymentAmount(parseFloat(e.target.value) || 0)}
                min="0"
                max={invoice?.balance_amount}
                step="0.01"
                className="mt-2"
              />
              <div className="text-sm text-gray-600 mt-1">
                Maximum: {formatCurrency(invoice?.balance_amount || 0)}
              </div>
            </div>

            <div>
              <Label htmlFor="payment_reference">Payment Reference</Label>
              <Input
                id="payment_reference"
                value={paymentReference}
                onChange={(e) => setPaymentReference(e.target.value)}
                placeholder="Transaction ID or check number"
                className="mt-2"
              />
            </div>
          </div>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={actionLoading}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handlePayment}
              disabled={actionLoading || paymentAmount <= 0 || paymentAmount > (invoice?.balance_amount || 0)}
            >
              {actionLoading ? 'Recording...' : 'Record Payment'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
