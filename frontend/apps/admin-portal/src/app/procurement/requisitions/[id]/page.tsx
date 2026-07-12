/**
 * Purchase Requisition Detail Page
 * Displays complete requisition information with items and approval workflow
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  ArrowLeft,
  Edit,
  Send,
  CheckCircle,
  XCircle,
  FileText,
  User,
  Calendar,
  Building,
  Package,
  AlertCircle,
  Trash2,
} from 'lucide-react';
import { procurementService } from '@/services/procurement.service';
import type { PurchaseRequisition, RequisitionStatus } from '@/types/procurement';

export default function RequisitionDetailPage() {
  const router = useRouter();
  const params = useParams();
  const requisitionId = params?.id as string;

  const [requisition, setRequisition] = useState<PurchaseRequisition | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  
  // Dialog states
  const [submitDialogOpen, setSubmitDialogOpen] = useState(false);
  const [approveDialogOpen, setApproveDialogOpen] = useState(false);
  const [rejectDialogOpen, setRejectDialogOpen] = useState(false);
  const [cancelDialogOpen, setCancelDialogOpen] = useState(false);
  const [remarks, setRemarks] = useState('');

  useEffect(() => {
    if (requisitionId) {
      fetchRequisitionDetails();
    }
  }, [requisitionId]);

  const fetchRequisitionDetails = async () => {
    try {
      setLoading(true);
      const response = await procurementService.requisition.getById(requisitionId);
      if (response.success && response.data) {
        setRequisition(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch requisition details:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!requisition) return;
    
    try {
      setActionLoading(true);
      const response = await procurementService.requisition.submit(requisition.id);
      if (response.success) {
        setSubmitDialogOpen(false);
        fetchRequisitionDetails();
      }
    } catch (error) {
      console.error('Failed to submit requisition:', error);
    } finally {
      setActionLoading(false);
    }
  };

  const handleApprove = async () => {
    if (!requisition) return;
    
    try {
      setActionLoading(true);
      const response = await procurementService.requisition.approve(
        requisition.id,
        true,
        remarks || undefined
      );
      if (response.success) {
        setApproveDialogOpen(false);
        setRemarks('');
        fetchRequisitionDetails();
      }
    } catch (error) {
      console.error('Failed to approve requisition:', error);
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    if (!requisition || !remarks.trim()) return;
    
    try {
      setActionLoading(true);
      const response = await procurementService.requisition.approve(
        requisition.id,
        false,
        remarks
      );
      if (response.success) {
        setRejectDialogOpen(false);
        setRemarks('');
        fetchRequisitionDetails();
      }
    } catch (error) {
      console.error('Failed to reject requisition:', error);
    } finally {
      setActionLoading(false);
    }
  };

  const handleCancel = async () => {
    if (!requisition || !remarks.trim()) return;
    
    try {
      setActionLoading(true);
      const response = await procurementService.requisition.cancel(
        requisition.id,
        remarks
      );
      if (response.success) {
        setCancelDialogOpen(false);
        setRemarks('');
        fetchRequisitionDetails();
      }
    } catch (error) {
      console.error('Failed to cancel requisition:', error);
    } finally {
      setActionLoading(false);
    }
  };

  const getStatusBadge = (status: RequisitionStatus) => {
    const configs = {
      draft: { color: 'bg-gray-100 text-gray-800', icon: FileText },
      submitted: { color: 'bg-blue-100 text-blue-800', icon: Send },
      approved: { color: 'bg-green-100 text-green-800', icon: CheckCircle },
      rejected: { color: 'bg-red-100 text-red-800', icon: XCircle },
      partially_converted: { color: 'bg-yellow-100 text-yellow-800', icon: Package },
      fully_converted: { color: 'bg-purple-100 text-purple-800', icon: CheckCircle },
      cancelled: { color: 'bg-gray-100 text-gray-800', icon: XCircle },
    };
    const config = configs[status];
    const Icon = config.icon;
    return (
      <Badge className={`${config.color} flex items-center gap-1`}>
        <Icon className="w-3 h-3" />
        {status.replace(/_/g, ' ').toUpperCase()}
      </Badge>
    );
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2,
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading requisition details...</p>
        </div>
      </div>
    );
  }

  if (!requisition) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Requisition Not Found
          </h2>
          <p className="text-gray-600 mb-4">
            The requested requisition could not be found.
          </p>
          <Button onClick={() => router.push('/procurement/requisitions')}>
            Back to Requisitions
          </Button>
        </div>
      </div>
    );
  }

  const canEdit = requisition.status === 'draft';
  const canSubmit = requisition.status === 'draft';
  const canApprove = requisition.status === 'submitted';
  const canCancel = ['draft', 'submitted', 'approved'].includes(requisition.status);

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => router.push('/procurement/requisitions')}
          >
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">{requisition.requisition_number}</h1>
            <div className="flex items-center gap-3 mt-2">
              <span className="text-gray-600">{requisition.title}</span>
              {getStatusBadge(requisition.status)}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {canEdit && (
            <Button
              variant="outline"
              onClick={() =>
                router.push(`/procurement/requisitions/${requisitionId}/edit`)
              }
            >
              <Edit className="w-4 h-4 mr-2" />
              Edit
            </Button>
          )}
          {canSubmit && (
            <Button onClick={() => setSubmitDialogOpen(true)}>
              <Send className="w-4 h-4 mr-2" />
              Submit for Approval
            </Button>
          )}
          {canApprove && (
            <>
              <Button
                variant="outline"
                onClick={() => setRejectDialogOpen(true)}
                className="border-red-300 text-red-600 hover:bg-red-50"
              >
                <XCircle className="w-4 h-4 mr-2" />
                Reject
              </Button>
              <Button onClick={() => setApproveDialogOpen(true)}>
                <CheckCircle className="w-4 h-4 mr-2" />
                Approve
              </Button>
            </>
          )}
          {canCancel && (
            <Button
              variant="outline"
              onClick={() => setCancelDialogOpen(true)}
              className="border-gray-300 text-gray-600"
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Cancel
            </Button>
          )}
        </div>
      </div>

      {/* Basic Information */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-500 flex items-center gap-2">
              <User className="w-4 h-4" />
              Requested By
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="font-medium">{requisition.requested_by || '-'}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-500 flex items-center gap-2">
              <Building className="w-4 h-4" />
              Department
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="font-medium">{requisition.department || '-'}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-500 flex items-center gap-2">
              <Calendar className="w-4 h-4" />
              Requisition Date
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="font-medium">
              {formatDate(requisition.requisition_date)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-500 flex items-center gap-2">
              <Calendar className="w-4 h-4" />
              Required By
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="font-medium">
              {formatDate(requisition.required_by_date)}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Description */}
      {requisition.description && (
        <Card>
          <CardHeader>
            <CardTitle>Description</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700 whitespace-pre-wrap">
              {requisition.description}
            </p>
          </CardContent>
        </Card>
      )}

      {/* Items Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Package className="w-5 h-5" />
              Requisition Items
            </CardTitle>
            <Badge variant="outline" className="text-base">
              {requisition.items?.length || 0} Items
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-12">#</TableHead>
                  <TableHead>Item Code</TableHead>
                  <TableHead>Description</TableHead>
                  <TableHead>Specification</TableHead>
                  <TableHead className="text-right">Quantity</TableHead>
                  <TableHead>UOM</TableHead>
                  <TableHead className="text-right">Est. Rate</TableHead>
                  <TableHead className="text-right">Amount</TableHead>
                  <TableHead className="text-right">Converted Qty</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {requisition.items && requisition.items.length > 0 ? (
                  requisition.items.map((item, index) => (
                    <TableRow key={item.id}>
                      <TableCell className="font-medium">{index + 1}</TableCell>
                      <TableCell className="font-mono">{item.item_code}</TableCell>
                      <TableCell>
                        <div className="max-w-xs">
                          <div className="font-medium">{item.item_description}</div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="max-w-xs text-sm text-gray-600">
                          {item.specification || '-'}
                        </div>
                      </TableCell>
                      <TableCell className="text-right font-medium">
                        {item.quantity}
                      </TableCell>
                      <TableCell>{item.uom}</TableCell>
                      <TableCell className="text-right">
                        {formatCurrency(item.estimated_rate)}
                      </TableCell>
                      <TableCell className="text-right font-medium">
                        {formatCurrency(item.estimated_amount)}
                      </TableCell>
                      <TableCell className="text-right">
                        <Badge
                          variant={
                            item.converted_quantity >= item.quantity
                              ? 'default'
                              : item.converted_quantity > 0
                              ? 'secondary'
                              : 'outline'
                          }
                        >
                          {item.converted_quantity} / {item.quantity}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={9} className="text-center py-8 text-gray-500">
                      No items in this requisition
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>

          {/* Total */}
          <div className="mt-4 flex justify-end">
            <div className="w-64 space-y-2">
              <div className="flex justify-between items-center py-2 border-t-2 border-gray-900">
                <span className="text-lg font-bold">Total Amount:</span>
                <span className="text-lg font-bold">
                  {formatCurrency(requisition.total_amount)}
                </span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Approval Information */}
      {(requisition.approved_by || requisition.approval_remarks || requisition.cancellation_reason) && (
        <Card>
          <CardHeader>
            <CardTitle>Workflow Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {requisition.approved_by && (
              <div>
                <label className="text-sm font-medium text-gray-500">Approved By</label>
                <p className="text-base font-medium">{requisition.approved_by}</p>
                {requisition.approval_date && (
                  <p className="text-sm text-gray-600">
                    {formatDate(requisition.approval_date)}
                  </p>
                )}
              </div>
            )}
            {requisition.approval_remarks && (
              <div>
                <label className="text-sm font-medium text-gray-500">
                  Approval Remarks
                </label>
                <p className="text-base">{requisition.approval_remarks}</p>
              </div>
            )}
            {requisition.cancellation_reason && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <label className="text-sm font-medium text-red-700">
                  Cancellation Reason
                </label>
                <p className="text-base text-red-900">
                  {requisition.cancellation_reason}
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Submit Dialog */}
      <Dialog open={submitDialogOpen} onOpenChange={setSubmitDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Submit Requisition for Approval</DialogTitle>
            <DialogDescription>
              Are you sure you want to submit this requisition for approval? Once
              submitted, you will not be able to edit it.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setSubmitDialogOpen(false)}
              disabled={actionLoading}
            >
              Cancel
            </Button>
            <Button onClick={handleSubmit} disabled={actionLoading}>
              {actionLoading ? 'Submitting...' : 'Submit'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Approve Dialog */}
      <Dialog open={approveDialogOpen} onOpenChange={setApproveDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Approve Requisition</DialogTitle>
            <DialogDescription>
              Approve this requisition to allow PO creation.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Remarks (Optional)</label>
              <Textarea
                value={remarks}
                onChange={(e) => setRemarks(e.target.value)}
                placeholder="Add any approval remarks..."
                rows={3}
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setApproveDialogOpen(false);
                setRemarks('');
              }}
              disabled={actionLoading}
            >
              Cancel
            </Button>
            <Button onClick={handleApprove} disabled={actionLoading}>
              {actionLoading ? 'Approving...' : 'Approve'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Reject Dialog */}
      <Dialog open={rejectDialogOpen} onOpenChange={setRejectDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Reject Requisition</DialogTitle>
            <DialogDescription>
              Please provide a reason for rejecting this requisition.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">
                Rejection Reason <span className="text-red-500">*</span>
              </label>
              <Textarea
                value={remarks}
                onChange={(e) => setRemarks(e.target.value)}
                placeholder="Reason for rejection..."
                rows={3}
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setRejectDialogOpen(false);
                setRemarks('');
              }}
              disabled={actionLoading}
            >
              Cancel
            </Button>
            <Button
              onClick={handleReject}
              disabled={actionLoading || !remarks.trim()}
              className="bg-red-600 hover:bg-red-700"
            >
              {actionLoading ? 'Rejecting...' : 'Reject'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Cancel Dialog */}
      <Dialog open={cancelDialogOpen} onOpenChange={setCancelDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Cancel Requisition</DialogTitle>
            <DialogDescription>
              Please provide a reason for cancelling this requisition.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">
                Cancellation Reason <span className="text-red-500">*</span>
              </label>
              <Textarea
                value={remarks}
                onChange={(e) => setRemarks(e.target.value)}
                placeholder="Reason for cancellation..."
                rows={3}
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setCancelDialogOpen(false);
                setRemarks('');
              }}
              disabled={actionLoading}
            >
              Cancel
            </Button>
            <Button
              onClick={handleCancel}
              disabled={actionLoading || !remarks.trim()}
              variant="destructive"
            >
              {actionLoading ? 'Cancelling...' : 'Cancel Requisition'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
