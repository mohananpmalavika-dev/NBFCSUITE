"use client";

import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { toast } from "@/components/ui/use-toast";
import {
  Calendar,
  DollarSign,
  TrendingUp,
  AlertTriangle,
  Receipt,
  Search,
  Download,
  Filter,
  Plus,
} from "lucide-react";
import { lockerService, PaymentMode, PaymentType } from "@/services/locker.service";
import { format } from "date-fns";

export default function LockerPaymentsPage() {
  const queryClient = useQueryClient();
  const [showPaymentDialog, setShowPaymentDialog] = useState(false);
  const [showReceiptDialog, setShowReceiptDialog] = useState(false);
  const [selectedReceipt, setSelectedReceipt] = useState<any>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [paymentModeFilter, setPaymentModeFilter] = useState<PaymentMode | "all">("all");
  const [paymentTypeFilter, setPaymentTypeFilter] = useState<PaymentType | "all">("all");

  // Payment form state
  const [paymentForm, setPaymentForm] = useState({
    allocation_id: "",
    payment_type: PaymentType.RENT,
    payment_mode: PaymentMode.CASH,
    amount: "",
    payment_date: format(new Date(), "yyyy-MM-dd"),
    period_from: "",
    period_to: "",
    cheque_number: "",
    cheque_date: "",
    bank_name: "",
    transaction_reference: "",
    remarks: "",
  });

  // Fetch revenue statistics
  const { data: revenueStats } = useQuery({
    queryKey: ["locker-revenue-stats"],
    queryFn: () => lockerService.getRevenueStats(),
  });

  // Fetch payment history with filters
  const { data: payments, isLoading: paymentsLoading } = useQuery({
    queryKey: [
      "locker-payments",
      dateFrom,
      dateTo,
      paymentModeFilter,
      paymentTypeFilter,
    ],
    queryFn: () =>
      lockerService.getPayments({
        date_from: dateFrom || undefined,
        date_to: dateTo || undefined,
        payment_mode: paymentModeFilter !== "all" ? paymentModeFilter : undefined,
        payment_type: paymentTypeFilter !== "all" ? paymentTypeFilter : undefined,
      }),
  });

  // Fetch allocations for dropdown
  const { data: allocations } = useQuery({
    queryKey: ["locker-allocations-active"],
    queryFn: () => lockerService.getAllocations({ status: "active" }),
  });

  // Create payment mutation
  const createPayment = useMutation({
    mutationFn: (data: any) => lockerService.recordPayment(data.allocation_id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["locker-payments"] });
      queryClient.invalidateQueries({ queryKey: ["locker-revenue-stats"] });
      queryClient.invalidateQueries({ queryKey: ["locker-allocations"] });
      toast({
        title: "Payment Recorded",
        description: "Payment has been recorded successfully.",
      });
      setShowPaymentDialog(false);
      resetPaymentForm();
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to record payment",
        variant: "destructive",
      });
    },
  });

  const resetPaymentForm = () => {
    setPaymentForm({
      allocation_id: "",
      payment_type: PaymentType.RENT,
      payment_mode: PaymentMode.CASH,
      amount: "",
      payment_date: format(new Date(), "yyyy-MM-dd"),
      period_from: "",
      period_to: "",
      cheque_number: "",
      cheque_date: "",
      bank_name: "",
      transaction_reference: "",
      remarks: "",
    });
  };

  const handlePaymentSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const payload: any = {
      allocation_id: parseInt(paymentForm.allocation_id),
      payment_type: paymentForm.payment_type,
      payment_mode: paymentForm.payment_mode,
      amount: parseFloat(paymentForm.amount),
      payment_date: paymentForm.payment_date,
      remarks: paymentForm.remarks || undefined,
    };

    if (paymentForm.payment_type === PaymentType.RENT) {
      payload.period_from = paymentForm.period_from;
      payload.period_to = paymentForm.period_to;
    }

    if (paymentForm.payment_mode === PaymentMode.CHEQUE) {
      payload.cheque_number = paymentForm.cheque_number;
      payload.cheque_date = paymentForm.cheque_date;
      payload.bank_name = paymentForm.bank_name;
    }

    if ([PaymentMode.NEFT, PaymentMode.RTGS, PaymentMode.UPI].includes(paymentForm.payment_mode)) {
      payload.transaction_reference = paymentForm.transaction_reference;
    }

    createPayment.mutate(payload);
  };

  const handleQuickPayment = (allocation: any) => {
    setPaymentForm({
      ...paymentForm,
      allocation_id: allocation.id.toString(),
      amount: allocation.annual_rent?.toString() || "",
    });
    setShowPaymentDialog(true);
  };

  const handleViewReceipt = (payment: any) => {
    setSelectedReceipt(payment);
    setShowReceiptDialog(true);
  };

  // Calculate outstanding days
  const getOutstandingDays = (dueDate: string) => {
    const due = new Date(dueDate);
    const today = new Date();
    const diffTime = today.getTime() - due.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays > 0 ? diffDays : 0;
  };

  // Filter payments by search
  const filteredPayments = payments?.filter((payment: any) => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      payment.customer_name?.toLowerCase().includes(query) ||
      payment.locker_number?.toLowerCase().includes(query) ||
      payment.receipt_number?.toLowerCase().includes(query)
    );
  });

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Locker Rent Collection</h1>
          <p className="text-muted-foreground">
            Record payments and track outstanding rent
          </p>
        </div>
        <Button onClick={() => setShowPaymentDialog(true)}>
          <Plus className="mr-2 h-4 w-4" />
          Record Payment
        </Button>
      </div>

      {/* Statistics Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Collected</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ₹{revenueStats?.total_collected?.toLocaleString() || 0}
            </div>
            <p className="text-xs text-muted-foreground">This financial year</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Outstanding</CardTitle>
            <AlertTriangle className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ₹{revenueStats?.outstanding_amount?.toLocaleString() || 0}
            </div>
            <p className="text-xs text-muted-foreground">Pending collection</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Collection Rate</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {revenueStats?.collection_efficiency?.toFixed(1) || 0}%
            </div>
            <p className="text-xs text-muted-foreground">Efficiency metric</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">This Month</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ₹{revenueStats?.current_month_collection?.toLocaleString() || 0}
            </div>
            <p className="text-xs text-muted-foreground">Collections</p>
          </CardContent>
        </Card>
      </div>

      {/* Outstanding Rent Alert */}
      {revenueStats?.overdue_count > 0 && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            {revenueStats.overdue_count} locker(s) have overdue rent payments totaling ₹
            {revenueStats.outstanding_amount?.toLocaleString()}
          </AlertDescription>
        </Alert>
      )}

      {/* Main Content Tabs */}
      <Tabs defaultValue="payments" className="space-y-4">
        <TabsList>
          <TabsTrigger value="payments">Payment History</TabsTrigger>
          <TabsTrigger value="outstanding">Outstanding Rent</TabsTrigger>
        </TabsList>

        {/* Payment History Tab */}
        <TabsContent value="payments" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Payment History</CardTitle>
              <CardDescription>
                View and manage all locker rent payments
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Filters */}
              <div className="grid gap-4 md:grid-cols-5">
                <div className="relative">
                  <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search payments..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-8"
                  />
                </div>
                <Input
                  type="date"
                  placeholder="From Date"
                  value={dateFrom}
                  onChange={(e) => setDateFrom(e.target.value)}
                />
                <Input
                  type="date"
                  placeholder="To Date"
                  value={dateTo}
                  onChange={(e) => setDateTo(e.target.value)}
                />
                <Select
                  value={paymentModeFilter}
                  onValueChange={(value) => setPaymentModeFilter(value as any)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Payment Mode" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Modes</SelectItem>
                    <SelectItem value={PaymentMode.CASH}>Cash</SelectItem>
                    <SelectItem value={PaymentMode.CHEQUE}>Cheque</SelectItem>
                    <SelectItem value={PaymentMode.NEFT}>NEFT</SelectItem>
                    <SelectItem value={PaymentMode.RTGS}>RTGS</SelectItem>
                    <SelectItem value={PaymentMode.UPI}>UPI</SelectItem>
                    <SelectItem value={PaymentMode.CARD}>Card</SelectItem>
                  </SelectContent>
                </Select>
                <Select
                  value={paymentTypeFilter}
                  onValueChange={(value) => setPaymentTypeFilter(value as any)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Payment Type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Types</SelectItem>
                    <SelectItem value={PaymentType.RENT}>Rent</SelectItem>
                    <SelectItem value={PaymentType.SECURITY_DEPOSIT}>
                      Security Deposit
                    </SelectItem>
                    <SelectItem value={PaymentType.PENALTY}>Penalty</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Payment History Table */}
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Receipt No.</TableHead>
                      <TableHead>Date</TableHead>
                      <TableHead>Customer</TableHead>
                      <TableHead>Locker</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead>Mode</TableHead>
                      <TableHead>Period</TableHead>
                      <TableHead className="text-right">Amount</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {paymentsLoading ? (
                      <TableRow>
                        <TableCell colSpan={9} className="text-center">
                          Loading payments...
                        </TableCell>
                      </TableRow>
                    ) : filteredPayments?.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={9} className="text-center">
                          No payments found
                        </TableCell>
                      </TableRow>
                    ) : (
                      filteredPayments?.map((payment: any) => (
                        <TableRow key={payment.id}>
                          <TableCell className="font-medium">
                            {payment.receipt_number}
                          </TableCell>
                          <TableCell>
                            {format(new Date(payment.payment_date), "dd MMM yyyy")}
                          </TableCell>
                          <TableCell>{payment.customer_name}</TableCell>
                          <TableCell>{payment.locker_number}</TableCell>
                          <TableCell>
                            <Badge variant="outline">
                              {payment.payment_type.replace("_", " ")}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <Badge>
                              {payment.payment_mode}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            {payment.period_from && payment.period_to
                              ? `${format(new Date(payment.period_from), "dd MMM")} - ${format(new Date(payment.period_to), "dd MMM yy")}`
                              : "-"}
                          </TableCell>
                          <TableCell className="text-right font-medium">
                            ₹{payment.amount?.toLocaleString()}
                          </TableCell>
                          <TableCell>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleViewReceipt(payment)}
                            >
                              <Receipt className="h-4 w-4" />
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Outstanding Rent Tab */}
        <TabsContent value="outstanding" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Outstanding Rent</CardTitle>
              <CardDescription>
                Lockers with pending rent payments
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Locker</TableHead>
                      <TableHead>Customer</TableHead>
                      <TableHead>Annual Rent</TableHead>
                      <TableHead>Last Payment</TableHead>
                      <TableHead>Due Date</TableHead>
                      <TableHead>Days Overdue</TableHead>
                      <TableHead className="text-right">Outstanding</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {allocations
                      ?.filter((alloc: any) => alloc.status === "active")
                      ?.map((allocation: any) => {
                        const daysOverdue = getOutstandingDays(allocation.next_rent_due_date || "");
                        return (
                          <TableRow key={allocation.id}>
                            <TableCell className="font-medium">
                              {allocation.locker_number}
                            </TableCell>
                            <TableCell>{allocation.customer_name}</TableCell>
                            <TableCell>₹{allocation.annual_rent?.toLocaleString()}</TableCell>
                            <TableCell>
                              {allocation.last_payment_date
                                ? format(new Date(allocation.last_payment_date), "dd MMM yyyy")
                                : "No payment"}
                            </TableCell>
                            <TableCell>
                              {allocation.next_rent_due_date
                                ? format(new Date(allocation.next_rent_due_date), "dd MMM yyyy")
                                : "-"}
                            </TableCell>
                            <TableCell>
                              {daysOverdue > 0 ? (
                                <Badge variant="destructive">{daysOverdue} days</Badge>
                              ) : (
                                <Badge variant="secondary">Current</Badge>
                              )}
                            </TableCell>
                            <TableCell className="text-right font-medium">
                              ₹{allocation.outstanding_rent?.toLocaleString() || 0}
                            </TableCell>
                            <TableCell>
                              <Button
                                size="sm"
                                onClick={() => handleQuickPayment(allocation)}
                                disabled={daysOverdue === 0}
                              >
                                Pay Now
                              </Button>
                            </TableCell>
                          </TableRow>
                        );
                      })}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Payment Entry Dialog */}
      <Dialog open={showPaymentDialog} onOpenChange={setShowPaymentDialog}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Record Payment</DialogTitle>
            <DialogDescription>
              Enter payment details to record rent collection
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handlePaymentSubmit} className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              {/* Allocation Selection */}
              <div className="space-y-2 md:col-span-2">
                <Label htmlFor="allocation_id">Locker Allocation *</Label>
                <Select
                  value={paymentForm.allocation_id}
                  onValueChange={(value) =>
                    setPaymentForm({ ...paymentForm, allocation_id: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select locker allocation" />
                  </SelectTrigger>
                  <SelectContent>
                    {allocations?.map((allocation: any) => (
                      <SelectItem key={allocation.id} value={allocation.id.toString()}>
                        {allocation.locker_number} - {allocation.customer_name} (₹
                        {allocation.annual_rent?.toLocaleString()}/year)
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Payment Type */}
              <div className="space-y-2">
                <Label htmlFor="payment_type">Payment Type *</Label>
                <Select
                  value={paymentForm.payment_type}
                  onValueChange={(value) =>
                    setPaymentForm({ ...paymentForm, payment_type: value as PaymentType })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value={PaymentType.RENT}>Rent</SelectItem>
                    <SelectItem value={PaymentType.SECURITY_DEPOSIT}>
                      Security Deposit
                    </SelectItem>
                    <SelectItem value={PaymentType.PENALTY}>Penalty</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Payment Mode */}
              <div className="space-y-2">
                <Label htmlFor="payment_mode">Payment Mode *</Label>
                <Select
                  value={paymentForm.payment_mode}
                  onValueChange={(value) =>
                    setPaymentForm({ ...paymentForm, payment_mode: value as PaymentMode })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value={PaymentMode.CASH}>Cash</SelectItem>
                    <SelectItem value={PaymentMode.CHEQUE}>Cheque</SelectItem>
                    <SelectItem value={PaymentMode.NEFT}>NEFT</SelectItem>
                    <SelectItem value={PaymentMode.RTGS}>RTGS</SelectItem>
                    <SelectItem value={PaymentMode.UPI}>UPI</SelectItem>
                    <SelectItem value={PaymentMode.CARD}>Card</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Amount */}
              <div className="space-y-2">
                <Label htmlFor="amount">Amount *</Label>
                <Input
                  id="amount"
                  type="number"
                  step="0.01"
                  placeholder="Enter amount"
                  value={paymentForm.amount}
                  onChange={(e) =>
                    setPaymentForm({ ...paymentForm, amount: e.target.value })
                  }
                  required
                />
              </div>

              {/* Payment Date */}
              <div className="space-y-2">
                <Label htmlFor="payment_date">Payment Date *</Label>
                <Input
                  id="payment_date"
                  type="date"
                  value={paymentForm.payment_date}
                  onChange={(e) =>
                    setPaymentForm({ ...paymentForm, payment_date: e.target.value })
                  }
                  required
                />
              </div>

              {/* Period Fields (for Rent payments) */}
              {paymentForm.payment_type === PaymentType.RENT && (
                <>
                  <div className="space-y-2">
                    <Label htmlFor="period_from">Period From *</Label>
                    <Input
                      id="period_from"
                      type="date"
                      value={paymentForm.period_from}
                      onChange={(e) =>
                        setPaymentForm({ ...paymentForm, period_from: e.target.value })
                      }
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="period_to">Period To *</Label>
                    <Input
                      id="period_to"
                      type="date"
                      value={paymentForm.period_to}
                      onChange={(e) =>
                        setPaymentForm({ ...paymentForm, period_to: e.target.value })
                      }
                      required
                    />
                  </div>
                </>
              )}

              {/* Cheque Details */}
              {paymentForm.payment_mode === PaymentMode.CHEQUE && (
                <>
                  <div className="space-y-2">
                    <Label htmlFor="cheque_number">Cheque Number *</Label>
                    <Input
                      id="cheque_number"
                      placeholder="Enter cheque number"
                      value={paymentForm.cheque_number}
                      onChange={(e) =>
                        setPaymentForm({ ...paymentForm, cheque_number: e.target.value })
                      }
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="cheque_date">Cheque Date *</Label>
                    <Input
                      id="cheque_date"
                      type="date"
                      value={paymentForm.cheque_date}
                      onChange={(e) =>
                        setPaymentForm({ ...paymentForm, cheque_date: e.target.value })
                      }
                      required
                    />
                  </div>
                  <div className="space-y-2 md:col-span-2">
                    <Label htmlFor="bank_name">Bank Name *</Label>
                    <Input
                      id="bank_name"
                      placeholder="Enter bank name"
                      value={paymentForm.bank_name}
                      onChange={(e) =>
                        setPaymentForm({ ...paymentForm, bank_name: e.target.value })
                      }
                      required
                    />
                  </div>
                </>
              )}

              {/* Transaction Reference (for digital payments) */}
              {[PaymentMode.NEFT, PaymentMode.RTGS, PaymentMode.UPI].includes(
                paymentForm.payment_mode
              ) && (
                <div className="space-y-2 md:col-span-2">
                  <Label htmlFor="transaction_reference">
                    Transaction Reference / UTR Number *
                  </Label>
                  <Input
                    id="transaction_reference"
                    placeholder="Enter transaction reference"
                    value={paymentForm.transaction_reference}
                    onChange={(e) =>
                      setPaymentForm({
                        ...paymentForm,
                        transaction_reference: e.target.value,
                      })
                    }
                    required
                  />
                </div>
              )}

              {/* Remarks */}
              <div className="space-y-2 md:col-span-2">
                <Label htmlFor="remarks">Remarks</Label>
                <Input
                  id="remarks"
                  placeholder="Additional notes (optional)"
                  value={paymentForm.remarks}
                  onChange={(e) =>
                    setPaymentForm({ ...paymentForm, remarks: e.target.value })
                  }
                />
              </div>
            </div>

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setShowPaymentDialog(false);
                  resetPaymentForm();
                }}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={createPayment.isPending}>
                {createPayment.isPending ? "Recording..." : "Record Payment"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Receipt Preview Dialog */}
      <Dialog open={showReceiptDialog} onOpenChange={setShowReceiptDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Payment Receipt</DialogTitle>
            <DialogDescription>Receipt preview and download</DialogDescription>
          </DialogHeader>

          {selectedReceipt && (
            <div className="space-y-4 p-6 border rounded-lg bg-white">
              {/* Receipt Header */}
              <div className="text-center border-b pb-4">
                <h2 className="text-2xl font-bold">Payment Receipt</h2>
                <p className="text-sm text-muted-foreground">
                  Receipt No: {selectedReceipt.receipt_number}
                </p>
              </div>

              {/* Receipt Details */}
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Date</p>
                  <p className="font-medium">
                    {format(new Date(selectedReceipt.payment_date), "dd MMMM yyyy")}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Payment Mode</p>
                  <p className="font-medium">{selectedReceipt.payment_mode}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Customer Name</p>
                  <p className="font-medium">{selectedReceipt.customer_name}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Locker Number</p>
                  <p className="font-medium">{selectedReceipt.locker_number}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Payment Type</p>
                  <p className="font-medium">
                    {selectedReceipt.payment_type.replace("_", " ")}
                  </p>
                </div>
                {selectedReceipt.period_from && selectedReceipt.period_to && (
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Period</p>
                    <p className="font-medium">
                      {format(new Date(selectedReceipt.period_from), "dd MMM yyyy")} to{" "}
                      {format(new Date(selectedReceipt.period_to), "dd MMM yyyy")}
                    </p>
                  </div>
                )}
              </div>

              {/* Instrument Details */}
              {selectedReceipt.cheque_number && (
                <div className="border-t pt-4">
                  <h3 className="font-semibold mb-2">Cheque Details</h3>
                  <div className="grid gap-2 md:grid-cols-2">
                    <div>
                      <p className="text-sm text-muted-foreground">Cheque Number</p>
                      <p className="font-medium">{selectedReceipt.cheque_number}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Cheque Date</p>
                      <p className="font-medium">
                        {format(new Date(selectedReceipt.cheque_date), "dd MMM yyyy")}
                      </p>
                    </div>
                    <div className="md:col-span-2">
                      <p className="text-sm text-muted-foreground">Bank Name</p>
                      <p className="font-medium">{selectedReceipt.bank_name}</p>
                    </div>
                  </div>
                </div>
              )}

              {selectedReceipt.transaction_reference && (
                <div className="border-t pt-4">
                  <h3 className="font-semibold mb-2">Transaction Details</h3>
                  <div>
                    <p className="text-sm text-muted-foreground">Reference / UTR Number</p>
                    <p className="font-medium">{selectedReceipt.transaction_reference}</p>
                  </div>
                </div>
              )}

              {/* Amount Section */}
              <div className="border-t border-b py-4">
                <div className="flex justify-between items-center">
                  <span className="text-lg font-semibold">Amount Paid</span>
                  <span className="text-2xl font-bold">
                    ₹{selectedReceipt.amount?.toLocaleString()}
                  </span>
                </div>
              </div>

              {/* Remarks */}
              {selectedReceipt.remarks && (
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Remarks</p>
                  <p className="text-sm">{selectedReceipt.remarks}</p>
                </div>
              )}

              {/* Footer */}
              <div className="text-center text-sm text-muted-foreground border-t pt-4">
                <p>This is a computer-generated receipt</p>
                <p>Generated on {format(new Date(), "dd MMMM yyyy, hh:mm a")}</p>
              </div>
            </div>
          )}

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowReceiptDialog(false)}
            >
              Close
            </Button>
            <Button onClick={() => window.print()}>
              <Download className="mr-2 h-4 w-4" />
              Print Receipt
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
