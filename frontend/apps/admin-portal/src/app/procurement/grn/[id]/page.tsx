/**
 * GRN Detail Page
 * Displays complete GRN information with quality check actions
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
import {
  ArrowLeft,
  CheckCircle,
  XCircle,
  Package,
  FileText,
  Truck,
  Calendar,
  MapPin,
  User,
} from 'lucide-react';
import { procurementService } from '@/services/procurement.service';
import type { GoodsReceiptNote } from '@/types/procurement';

interface GRNDetailPageProps {
  params: {
    id: string;
  };
}

export default function GRNDetailPage({ params }: GRNDetailPageProps) {
  const router = useRouter();
  const [grn, setGrn] = useState<GoodsReceiptNote | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAcceptDialog, setShowAcceptDialog] = useState(false);
  const [showRejectDialog, setShowRejectDialog] = useState(false);
  const [qualityRemarks, setQualityRemarks] = useState('');
  const [rejectionReason, setRejectionReason] = useState('');

  useEffect(() => {
    fetchGRNDetails();
  }, [params.id]);

  const fetchGRNDetails = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await procurementService.grn.getById(params.id);
      if (response.success && response.data) {
        setGrn(response.data);
      } else {
        setError(response.message || 'Failed to fetch GRN details');
      }
    } catch (err) {
      setError('An error occurred while fetching GRN details');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleQualityCheck = async () => {
    if (!grn) return;

    try {
      setActionLoading(true);
      const response = await procurementService.grn.qualityCheck(grn.id, {
        quality_remarks: qualityRemarks,
      });
      if (response.success) {
        setShowAcceptDialog(false);
        setQualityRemarks('');
        fetchGRNDetails();
      } else {
        setError(response.message || 'Failed to perform quality check');
      }
    } catch (err) {
      setError('An error occurred while performing quality check');
      console.error(err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleAccept = async () => {
    if (!grn) return;

    try {
      setActionLoading(true);
      const response = await procurementService.grn.accept(grn.id);
      if (response.success) {
        setShowAcceptDialog(false);
        fetchGRNDetails();
      } else {
        setError(response.message || 'Failed to accept GRN');
      }
    } catch (err) {
      setError('An error occurred while accepting the GRN');
      console.error(err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    if (!grn || !rejectionReason.trim()) {
      setError('Rejection reason is required');
      return;
    }

    try {
      setActionLoading(true);
      const response = await procurementService.grn.reject(grn.id, {
        rejection_reason: rejectionReason,
      });
      if (response.success) {
        setShowRejectDialog(false);
        setRejectionReason('');
        fetchGRNDetails();
      } else {
        setError(response.message || 'Failed to reject GRN');
      }
    } catch (err) {
      setError('An error occurred while rejecting the GRN');
      console.error(err);
    } finally {
      setActionLoading(false);
    }
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
      pending: 'bg-yellow-100 text-yellow-800',
      quality_check: 'bg-blue-100 text-blue-800',
      partially_accepted: 'bg-orange-100 text-orange-800',
      accepted: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
    };
    return statusClasses[status as keyof typeof statusClasses] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading GRN details...</div>
      </div>
    );
  }

  if (error && !grn) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
        <Button onClick={() => router.push('/procurement/grn')} className="mt-4">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to GRNs
        </Button>
      </div>
    );
  }

  if (!grn) return null;

  const canPerformQualityCheck =
    grn.quality_check_required && grn.status === 'pending' && !grn.quality_checked_at;
  const canAccept = grn.status === 'quality_check' || grn.status === 'partially_accepted';
  const canReject = grn.status === 'pending' || grn.status === 'quality_check';

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
          <Button variant="ghost" size="sm" onClick={() => router.push('/procurement/grn')}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <div>
            <h1 className="text-3xl font-bold">{grn.grn_number}</h1>
            <p className="text-gray-600">Goods Receipt Note Details</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {canPerformQualityCheck && (
            <Button onClick={() => setShowAcceptDialog(true)} disabled={actionLoading}>
              <CheckCircle className="w-4 h-4 mr-2" />
              Perform Quality Check
            </Button>
          )}
          {canAccept && (
            <Button onClick={handleAccept} disabled={actionLoading}>
              <CheckCircle className="w-4 h-4 mr-2" />
              Accept GRN
            </Button>
          )}
          {canReject && (
            <Button
              variant="destructive"
              onClick={() => setShowRejectDialog(true)}
              disabled={actionLoading}
            >
              <XCircle className="w-4 h-4 mr-2" />
              Reject GRN
            </Button>
          )}
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
                grn.status
              )}`}
            >
              {grn.status.replace(/_/g, ' ').toUpperCase()}
            </span>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 mb-2">
              <Calendar className="w-4 h-4 text-gray-500" />
              <span className="text-sm text-gray-600">GRN Date</span>
            </div>
            <div className="text-lg font-semibold">{formatDate(grn.grn_date)}</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 mb-2">
              <Calendar className="w-4 h-4 text-gray-500" />
              <span className="text-sm text-gray-600">Receipt Date</span>
            </div>
            <div className="text-lg font-semibold">{formatDate(grn.receipt_date)}</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 mb-2">
              <Package className="w-4 h-4 text-gray-500" />
              <span className="text-sm text-gray-600">Total Items</span>
            </div>
            <div className="text-lg font-semibold">{grn.items?.length || 0}</div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="details" className="space-y-6">
        <TabsList>
          <TabsTrigger value="details">GRN Details</TabsTrigger>
          <TabsTrigger value="items">Receipt Items</TabsTrigger>
          <TabsTrigger value="quality">Quality Check</TabsTrigger>
          <TabsTrigger value="history">History</TabsTrigger>
        </TabsList>

        {/* Details Tab */}
        <TabsContent value="details" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Purchase Order Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="w-5 h-5" />
                  Purchase Order
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <div className="text-sm text-gray-600">PO Number</div>
                  <Link
                    href={`/procurement/purchase-orders/${grn.po_id}`}
                    className="font-medium text-blue-600 hover:underline"
                  >
                    View Purchase Order
                  </Link>
                </div>
              </CardContent>
            </Card>

            {/* Warehouse Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MapPin className="w-5 h-5" />
                  Warehouse
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <div className="text-sm text-gray-600">Location</div>
                  <div className="font-medium">{grn.warehouse_location || 'Not specified'}</div>
                </div>
                {grn.received_by && (
                  <div>
                    <div className="text-sm text-gray-600">Received By</div>
                    <div className="font-medium">User ID: {grn.received_by}</div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Challan Information */}
            {grn.challan_number && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="w-5 h-5" />
                    Challan Information
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div>
                    <div className="text-sm text-gray-600">Challan Number</div>
                    <div className="font-medium">{grn.challan_number}</div>
                  </div>
                  {grn.challan_date && (
                    <div>
                      <div className="text-sm text-gray-600">Challan Date</div>
                      <div className="font-medium">{formatDate(grn.challan_date)}</div>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Transport Information */}
            {(grn.transporter_name || grn.vehicle_number || grn.lr_number) && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Truck className="w-5 h-5" />
                    Transport Details
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {grn.transporter_name && (
                    <div>
                      <div className="text-sm text-gray-600">Transporter</div>
                      <div className="font-medium">{grn.transporter_name}</div>
                    </div>
                  )}
                  {grn.vehicle_number && (
                    <div>
                      <div className="text-sm text-gray-600">Vehicle Number</div>
                      <div className="font-medium">{grn.vehicle_number}</div>
                    </div>
                  )}
                  {grn.lr_number && (
                    <div>
                      <div className="text-sm text-gray-600">LR Number</div>
                      <div className="font-medium">{grn.lr_number}</div>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </div>

          {/* Remarks */}
          {grn.remarks && (
            <Card>
              <CardHeader>
                <CardTitle>Remarks</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="whitespace-pre-wrap">{grn.remarks}</div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Items Tab */}
        <TabsContent value="items">
          <Card>
            <CardHeader>
              <CardTitle>Receipt Items</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-12">#</TableHead>
                      <TableHead>Item Code</TableHead>
                      <TableHead>Item Name</TableHead>
                      <TableHead className="text-right">Ordered Qty</TableHead>
                      <TableHead className="text-right">Received Qty</TableHead>
                      <TableHead className="text-right">Accepted Qty</TableHead>
                      <TableHead className="text-right">Rejected Qty</TableHead>
                      <TableHead>UOM</TableHead>
                      <TableHead>Batch No.</TableHead>
                      <TableHead>Quality Status</TableHead>
                      <TableHead>Remarks</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {grn.items?.map((item, index) => (
                      <TableRow key={item.id}>
                        <TableCell className="font-medium">{index + 1}</TableCell>
                        <TableCell>{item.item_code || '-'}</TableCell>
                        <TableCell className="font-medium">{item.item_name}</TableCell>
                        <TableCell className="text-right">
                          {item.ordered_quantity.toFixed(2)}
                        </TableCell>
                        <TableCell className="text-right font-medium">
                          {item.received_quantity.toFixed(2)}
                        </TableCell>
                        <TableCell className="text-right text-green-600 font-medium">
                          {item.accepted_quantity.toFixed(2)}
                        </TableCell>
                        <TableCell className="text-right text-red-600 font-medium">
                          {item.rejected_quantity.toFixed(2)}
                        </TableCell>
                        <TableCell>{item.unit_of_measure}</TableCell>
                        <TableCell>{item.batch_number || '-'}</TableCell>
                        <TableCell>
                          {item.quality_status ? (
                            <span
                              className={`inline-block px-2 py-1 rounded text-xs ${
                                item.quality_status === 'accepted'
                                  ? 'bg-green-100 text-green-800'
                                  : item.quality_status === 'rejected'
                                  ? 'bg-red-100 text-red-800'
                                  : 'bg-yellow-100 text-yellow-800'
                              }`}
                            >
                              {item.quality_status.toUpperCase()}
                            </span>
                          ) : (
                            '-'
                          )}
                        </TableCell>
                        <TableCell className="text-sm">{item.remarks || '-'}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Quality Check Tab */}
        <TabsContent value="quality">
          <Card>
            <CardHeader>
              <CardTitle>Quality Check Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="text-sm text-gray-600 mb-1">Quality Check Required</div>
                <div className="font-medium">
                  {grn.quality_check_required ? (
                    <span className="text-green-600">✓ Yes</span>
                  ) : (
                    <span className="text-gray-500">✗ No</span>
                  )}
                </div>
              </div>

              {grn.quality_check_required && (
                <>
                  {grn.quality_checked_at ? (
                    <>
                      <div>
                        <div className="text-sm text-gray-600 mb-1">Quality Checked By</div>
                        <div className="font-medium">User ID: {grn.quality_checked_by}</div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-600 mb-1">Quality Check Date</div>
                        <div className="font-medium">{formatDate(grn.quality_checked_at)}</div>
                      </div>
                      {grn.quality_remarks && (
                        <div>
                          <div className="text-sm text-gray-600 mb-1">Quality Remarks</div>
                          <div className="whitespace-pre-wrap p-3 bg-gray-50 rounded">
                            {grn.quality_remarks}
                          </div>
                        </div>
                      )}
                    </>
                  ) : (
                    <div className="bg-yellow-50 border border-yellow-200 p-4 rounded">
                      <p className="text-yellow-800">Quality check is pending</p>
                    </div>
                  )}
                </>
              )}

              {grn.status === 'rejected' && grn.rejection_reason && (
                <div className="bg-red-50 border border-red-200 p-4 rounded">
                  <div className="text-sm font-medium text-red-800 mb-2">Rejection Reason</div>
                  <div className="text-red-700 whitespace-pre-wrap">{grn.rejection_reason}</div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* History Tab */}
        <TabsContent value="history">
          <Card>
            <CardHeader>
              <CardTitle>GRN History</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-start gap-4 pb-4 border-b">
                  <div className="w-2 h-2 bg-blue-600 rounded-full mt-2" />
                  <div className="flex-1">
                    <div className="font-medium">GRN Created</div>
                    <div className="text-sm text-gray-600">
                      {formatDate(grn.created_at)} at{' '}
                      {new Date(grn.created_at).toLocaleTimeString('en-IN')}
                    </div>
                  </div>
                </div>

                {grn.quality_checked_at && (
                  <div className="flex items-start gap-4 pb-4 border-b">
                    <div className="w-2 h-2 bg-green-600 rounded-full mt-2" />
                    <div className="flex-1">
                      <div className="font-medium">Quality Check Completed</div>
                      <div className="text-sm text-gray-600">
                        {formatDate(grn.quality_checked_at)} at{' '}
                        {new Date(grn.quality_checked_at).toLocaleTimeString('en-IN')}
                      </div>
                    </div>
                  </div>
                )}

                <div className="flex items-start gap-4">
                  <div className="w-2 h-2 bg-gray-400 rounded-full mt-2" />
                  <div className="flex-1">
                    <div className="font-medium">Last Updated</div>
                    <div className="text-sm text-gray-600">
                      {formatDate(grn.updated_at)} at{' '}
                      {new Date(grn.updated_at).toLocaleTimeString('en-IN')}
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Quality Check Dialog */}
      <AlertDialog open={showAcceptDialog} onOpenChange={setShowAcceptDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Perform Quality Check</AlertDialogTitle>
            <AlertDialogDescription>
              Add quality check remarks for this goods receipt.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <div className="py-4">
            <Label htmlFor="quality_remarks">Quality Check Remarks</Label>
            <Textarea
              id="quality_remarks"
              value={qualityRemarks}
              onChange={(e) => setQualityRemarks(e.target.value)}
              placeholder="Enter quality check observations and remarks..."
              rows={4}
              className="mt-2"
            />
          </div>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={actionLoading}>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleQualityCheck} disabled={actionLoading}>
              {actionLoading ? 'Processing...' : 'Complete Quality Check'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Reject Dialog */}
      <AlertDialog open={showRejectDialog} onOpenChange={setShowRejectDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Reject GRN</AlertDialogTitle>
            <AlertDialogDescription>
              Please provide a reason for rejecting this goods receipt. This action cannot be
              undone.
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
              {actionLoading ? 'Rejecting...' : 'Reject GRN'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
