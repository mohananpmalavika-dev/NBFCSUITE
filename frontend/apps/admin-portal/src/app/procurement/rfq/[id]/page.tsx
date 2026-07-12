/**
 * RFQ Detail Page
 * Displays complete RFQ information with items, vendors, and quotes
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
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
  Calendar,
  Package,
  Users,
  AlertCircle,
  Star,
  TrendingDown,
  Clock,
} from 'lucide-react';
import { procurementService } from '@/services/procurement.service';
import type { RFQ, RFQStatus, VendorQuote } from '@/types/procurement';

export default function RFQDetailPage() {
  const router = useRouter();
  const params = useParams();
  const rfqId = params?.id as string;

  const [rfq, setRfq] = useState<RFQ | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  
  // Dialog states
  const [sendDialogOpen, setSendDialogOpen] = useState(false);
  const [closeDialogOpen, setCloseDialogOpen] = useState(false);

  useEffect(() => {
    if (rfqId) {
      fetchRFQDetails();
    }
  }, [rfqId]);

  const fetchRFQDetails = async () => {
    try {
      setLoading(true);
      // API call would be made here
      // const response = await procurementService.rfq.getById(rfqId);
      // For now, setting null
      setRfq(null);
    } catch (error) {
      console.error('Failed to fetch RFQ details:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSendRFQ = async () => {
    if (!rfq) return;
    
    try {
      setActionLoading(true);
      // API call: await procurementService.rfq.send(rfq.id);
      setSendDialogOpen(false);
      fetchRFQDetails();
    } catch (error) {
      console.error('Failed to send RFQ:', error);
    } finally {
      setActionLoading(false);
    }
  };

  const handleCloseRFQ = async () => {
    if (!rfq) return;
    
    try {
      setActionLoading(true);
      // API call: await procurementService.rfq.close(rfq.id);
      setCloseDialogOpen(false);
      fetchRFQDetails();
    } catch (error) {
      console.error('Failed to close RFQ:', error);
    } finally {
      setActionLoading(false);
    }
  };

  const getStatusBadge = (status: RFQStatus) => {
    const configs = {
      draft: { color: 'bg-gray-100 text-gray-800', icon: FileText },
      sent: { color: 'bg-blue-100 text-blue-800', icon: Send },
      quoted: { color: 'bg-yellow-100 text-yellow-800', icon: Clock },
      closed: { color: 'bg-green-100 text-green-800', icon: CheckCircle },
      cancelled: { color: 'bg-red-100 text-red-800', icon: XCircle },
    };
    const config = configs[status];
    const Icon = config.icon;
    return (
      <Badge className={`${config.color} flex items-center gap-1`}>
        <Icon className="w-3 h-3" />
        {status.toUpperCase()}
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

  const getBestQuote = (itemId: string, quotes?: VendorQuote[]) => {
    if (!quotes || quotes.length === 0) return null;
    
    // Find quotes with this item and get the lowest rate
    const itemQuotes = quotes
      .filter((q) => q.items?.some((i) => i.rfq_item_id === itemId))
      .map((q) => ({
        vendor: q.vendor_name,
        rate: q.items?.find((i) => i.rfq_item_id === itemId)?.quoted_rate || 0,
      }));
    
    if (itemQuotes.length === 0) return null;
    
    return itemQuotes.reduce((best, current) =>
      current.rate < best.rate ? current : best
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading RFQ details...</p>
        </div>
      </div>
    );
  }

  if (!rfq) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">RFQ Not Found</h2>
          <p className="text-gray-600 mb-4">The requested RFQ could not be found.</p>
          <Button onClick={() => router.push('/procurement/rfq')}>
            Back to RFQ List
          </Button>
        </div>
      </div>
    );
  }

  const canEdit = rfq.status === 'draft';
  const canSend = rfq.status === 'draft';
  const canClose = rfq.status === 'quoted';

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => router.push('/procurement/rfq')}
          >
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">{rfq.rfq_number}</h1>
            <div className="flex items-center gap-3 mt-2">
              <span className="text-gray-600">{rfq.title}</span>
              {getStatusBadge(rfq.status)}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {canEdit && (
            <Button
              variant="outline"
              onClick={() => router.push(`/procurement/rfq/${rfqId}/edit`)}
            >
              <Edit className="w-4 h-4 mr-2" />
              Edit
            </Button>
          )}
          {canSend && (
            <Button onClick={() => setSendDialogOpen(true)}>
              <Send className="w-4 h-4 mr-2" />
              Send to Vendors
            </Button>
          )}
          {canClose && (
            <Button onClick={() => setCloseDialogOpen(true)}>
              <CheckCircle className="w-4 h-4 mr-2" />
              Close RFQ
            </Button>
          )}
        </div>
      </div>

      {/* Basic Information */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-500 flex items-center gap-2">
              <Calendar className="w-4 h-4" />
              RFQ Date
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="font-medium">{formatDate(rfq.rfq_date)}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-500 flex items-center gap-2">
              <Clock className="w-4 h-4" />
              Quote Deadline
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="font-medium">{formatDate(rfq.quote_deadline)}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-500 flex items-center gap-2">
              <Users className="w-4 h-4" />
              Vendors Invited
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{rfq.vendors?.length || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-500 flex items-center gap-2">
              <FileText className="w-4 h-4" />
              Quotes Received
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {rfq.quotes_received || 0}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Description */}
      {rfq.description && (
        <Card>
          <CardHeader>
            <CardTitle>Description</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700 whitespace-pre-wrap">{rfq.description}</p>
          </CardContent>
        </Card>
      )}

      {/* Tabs */}
      <Tabs defaultValue="items" className="space-y-4">
        <TabsList>
          <TabsTrigger value="items">Items</TabsTrigger>
          <TabsTrigger value="vendors">Vendors</TabsTrigger>
          <TabsTrigger value="quotes">Quotes</TabsTrigger>
          <TabsTrigger value="comparison">Comparison</TabsTrigger>
        </TabsList>

        {/* Items Tab */}
        <TabsContent value="items">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <Package className="w-5 h-5" />
                  RFQ Items
                </CardTitle>
                <Badge variant="outline" className="text-base">
                  {rfq.items?.length || 0} Items
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
                      <TableHead className="text-right">Est. Amount</TableHead>
                      <TableHead className="text-right">Best Quote</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {rfq.items && rfq.items.length > 0 ? (
                      rfq.items.map((item, index) => {
                        const bestQuote = getBestQuote(item.id!, rfq.vendor_quotes);
                        return (
                          <TableRow key={item.id}>
                            <TableCell className="font-medium">{index + 1}</TableCell>
                            <TableCell className="font-mono">{item.item_code}</TableCell>
                            <TableCell>
                              <div className="max-w-xs">
                                <div className="font-medium">
                                  {item.item_description}
                                </div>
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
                              {bestQuote ? (
                                <div className="flex flex-col items-end">
                                  <span className="font-bold text-green-600">
                                    {formatCurrency(bestQuote.rate)}
                                  </span>
                                  <span className="text-xs text-gray-500">
                                    {bestQuote.vendor}
                                  </span>
                                </div>
                              ) : (
                                <span className="text-gray-400">No quotes</span>
                              )}
                            </TableCell>
                          </TableRow>
                        );
                      })
                    ) : (
                      <TableRow>
                        <TableCell colSpan={9} className="text-center py-8 text-gray-500">
                          No items in this RFQ
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
                    <span className="text-lg font-bold">Total Est. Amount:</span>
                    <span className="text-lg font-bold">
                      {formatCurrency(rfq.total_amount || 0)}
                    </span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Vendors Tab */}
        <TabsContent value="vendors">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="w-5 h-5" />
                Invited Vendors
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Vendor Code</TableHead>
                      <TableHead>Vendor Name</TableHead>
                      <TableHead>Contact Person</TableHead>
                      <TableHead>Email</TableHead>
                      <TableHead>Phone</TableHead>
                      <TableHead className="text-center">Quote Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {rfq.vendors && rfq.vendors.length > 0 ? (
                      rfq.vendors.map((vendor) => {
                        const hasQuoted = rfq.vendor_quotes?.some(
                          (q) => q.vendor_id === vendor.vendor_id
                        );
                        return (
                          <TableRow key={vendor.id}>
                            <TableCell className="font-mono">
                              {vendor.vendor_code}
                            </TableCell>
                            <TableCell className="font-medium">
                              {vendor.vendor_name}
                            </TableCell>
                            <TableCell>{vendor.contact_person || '-'}</TableCell>
                            <TableCell>{vendor.email || '-'}</TableCell>
                            <TableCell>{vendor.phone || '-'}</TableCell>
                            <TableCell className="text-center">
                              {hasQuoted ? (
                                <Badge className="bg-green-100 text-green-800">
                                  <CheckCircle className="w-3 h-3 mr-1" />
                                  Quoted
                                </Badge>
                              ) : rfq.status === 'sent' || rfq.status === 'quoted' ? (
                                <Badge className="bg-yellow-100 text-yellow-800">
                                  <Clock className="w-3 h-3 mr-1" />
                                  Pending
                                </Badge>
                              ) : (
                                <Badge variant="outline">Not Sent</Badge>
                              )}
                            </TableCell>
                          </TableRow>
                        );
                      })
                    ) : (
                      <TableRow>
                        <TableCell colSpan={6} className="text-center py-8 text-gray-500">
                          No vendors invited to this RFQ
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Quotes Tab */}
        <TabsContent value="quotes">
          <Card>
            <CardHeader>
              <CardTitle>Vendor Quotations</CardTitle>
            </CardHeader>
            <CardContent>
              {rfq.vendor_quotes && rfq.vendor_quotes.length > 0 ? (
                <div className="space-y-4">
                  {rfq.vendor_quotes.map((quote) => (
                    <Card key={quote.id}>
                      <CardHeader>
                        <div className="flex items-center justify-between">
                          <div>
                            <CardTitle className="text-lg">
                              {quote.vendor_name}
                            </CardTitle>
                            <p className="text-sm text-gray-500 mt-1">
                              Quote Date: {formatDate(quote.quote_date)}
                            </p>
                          </div>
                          <div className="text-right">
                            <div className="text-2xl font-bold text-green-600">
                              {formatCurrency(quote.total_quoted_amount)}
                            </div>
                            <p className="text-sm text-gray-500">Total Amount</p>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <Table>
                          <TableHeader>
                            <TableRow>
                              <TableHead>Item</TableHead>
                              <TableHead className="text-right">Quantity</TableHead>
                              <TableHead className="text-right">Quoted Rate</TableHead>
                              <TableHead className="text-right">Amount</TableHead>
                              <TableHead className="text-right">vs Est.</TableHead>
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {quote.items?.map((item, idx) => {
                              const rfqItem = rfq.items?.find(
                                (ri) => ri.id === item.rfq_item_id
                              );
                              const diff =
                                rfqItem && item.quoted_rate < rfqItem.estimated_rate;
                              return (
                                <TableRow key={idx}>
                                  <TableCell>
                                    {rfqItem?.item_description || 'Unknown Item'}
                                  </TableCell>
                                  <TableCell className="text-right">
                                    {item.quoted_quantity}
                                  </TableCell>
                                  <TableCell className="text-right font-medium">
                                    {formatCurrency(item.quoted_rate)}
                                  </TableCell>
                                  <TableCell className="text-right font-medium">
                                    {formatCurrency(item.quoted_amount)}
                                  </TableCell>
                                  <TableCell className="text-right">
                                    {rfqItem && (
                                      <Badge
                                        variant={diff ? 'default' : 'outline'}
                                        className={
                                          diff
                                            ? 'bg-green-100 text-green-800'
                                            : 'bg-red-100 text-red-800'
                                        }
                                      >
                                        {diff ? (
                                          <TrendingDown className="w-3 h-3 mr-1" />
                                        ) : (
                                          <span className="mr-1">↑</span>
                                        )}
                                        {(
                                          ((item.quoted_rate -
                                            rfqItem.estimated_rate) /
                                            rfqItem.estimated_rate) *
                                          100
                                        ).toFixed(1)}
                                        %
                                      </Badge>
                                    )}
                                  </TableCell>
                                </TableRow>
                              );
                            })}
                          </TableBody>
                        </Table>
                        {quote.remarks && (
                          <div className="mt-4 p-3 bg-gray-50 rounded">
                            <p className="text-sm font-medium text-gray-700">
                              Remarks:
                            </p>
                            <p className="text-sm text-gray-600 mt-1">
                              {quote.remarks}
                            </p>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <p>No quotations received yet</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Comparison Tab */}
        <TabsContent value="comparison">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Star className="w-5 h-5" />
                Quote Comparison
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12 text-gray-500">
                <p>Comparative analysis will be displayed here</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Send RFQ Dialog */}
      <Dialog open={sendDialogOpen} onOpenChange={setSendDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Send RFQ to Vendors</DialogTitle>
            <DialogDescription>
              Are you sure you want to send this RFQ to all invited vendors? They will
              be able to submit quotations until the deadline.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setSendDialogOpen(false)}
              disabled={actionLoading}
            >
              Cancel
            </Button>
            <Button onClick={handleSendRFQ} disabled={actionLoading}>
              {actionLoading ? 'Sending...' : 'Send RFQ'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Close RFQ Dialog */}
      <Dialog open={closeDialogOpen} onOpenChange={setCloseDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Close RFQ</DialogTitle>
            <DialogDescription>
              Closing the RFQ will prevent vendors from submitting new quotations.
              You can then proceed to create purchase orders based on the received
              quotes.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setCloseDialogOpen(false)}
              disabled={actionLoading}
            >
              Cancel
            </Button>
            <Button onClick={handleCloseRFQ} disabled={actionLoading}>
              {actionLoading ? 'Closing...' : 'Close RFQ'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
