"use client";

import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
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
import { toast } from "@/components/ui/use-toast";
import {
  Search,
  Plus,
  Eye,
  Edit,
  CheckCircle,
  XCircle,
  AlertCircle,
  UserPlus,
  FileText,
  Shield,
} from "lucide-react";
import {
  lockerCustomerService,
  CustomerCategory,
  VerificationStatus,
  type LockerCustomer,
} from "@/services/locker.service";
import { format } from "date-fns";

export default function LockerCustomersPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  
  // Search and filter state
  const [searchQuery, setSearchQuery] = useState("");
  const [categoryFilter, setCategoryFilter] = useState<string>("all");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [verificationFilter, setVerificationFilter] = useState<string>("all");
  const [page, setPage] = useState(1);
  const pageSize = 20;

  // Dialog state
  const [showVerifyDialog, setShowVerifyDialog] = useState(false);
  const [selectedCustomer, setSelectedCustomer] = useState<LockerCustomer | null>(null);
  const [verificationStatus, setVerificationStatus] = useState<VerificationStatus>(
    VerificationStatus.VERIFIED
  );
  const [verificationRemarks, setVerificationRemarks] = useState("");

  // Fetch customers with search
  const { data: customersData, isLoading } = useQuery({
    queryKey: [
      "locker-customers",
      searchQuery,
      categoryFilter,
      statusFilter,
      verificationFilter,
      page,
    ],
    queryFn: () =>
      lockerCustomerService.searchCustomers({
        search_query: searchQuery || undefined,
        customer_category:
          categoryFilter !== "all"
            ? (categoryFilter as CustomerCategory)
            : undefined,
        status: statusFilter !== "all" ? statusFilter : undefined,
        verification_status:
          verificationFilter !== "all"
            ? (verificationFilter as VerificationStatus)
            : undefined,
        page,
        page_size: pageSize,
      }),
  });

  // Fetch analytics
  const { data: analytics } = useQuery({
    queryKey: ["locker-customer-analytics"],
    queryFn: () => lockerCustomerService.getCustomerAnalytics(),
  });

  // Verify customer mutation
  const verifyCustomer = useMutation({
    mutationFn: (data: {
      customerId: string;
      status: VerificationStatus;
      remarks?: string;
    }) =>
      lockerCustomerService.verifyCustomer(
        data.customerId,
        data.status,
        data.remarks
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["locker-customers"] });
      queryClient.invalidateQueries({ queryKey: ["locker-customer-analytics"] });
      toast({
        title: "Customer Verified",
        description: "Customer verification status updated successfully.",
      });
      setShowVerifyDialog(false);
      setSelectedCustomer(null);
      setVerificationRemarks("");
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to verify customer",
        variant: "destructive",
      });
    },
  });

  const handleVerify = (customer: LockerCustomer) => {
    setSelectedCustomer(customer);
    setVerificationStatus(VerificationStatus.VERIFIED);
    setShowVerifyDialog(true);
  };

  const handleVerifySubmit = () => {
    if (!selectedCustomer) return;
    verifyCustomer.mutate({
      customerId: selectedCustomer.id,
      status: verificationStatus,
      remarks: verificationRemarks || undefined,
    });
  };

  const getVerificationStatusBadge = (status: string) => {
    switch (status) {
      case "verified":
        return <Badge className="bg-green-500">Verified</Badge>;
      case "pending":
        return <Badge variant="secondary">Pending</Badge>;
      case "rejected":
        return <Badge variant="destructive">Rejected</Badge>;
      case "expired":
        return <Badge variant="outline">Expired</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const getCategoryBadge = (category: string) => {
    const colors: Record<string, string> = {
      premium: "bg-purple-500",
      senior_citizen: "bg-blue-500",
      staff: "bg-orange-500",
      vip: "bg-pink-500",
      regular: "bg-gray-500",
    };
    return (
      <Badge className={colors[category] || "bg-gray-500"}>
        {category.replace("_", " ")}
      </Badge>
    );
  };

  const customers = customersData?.data?.customers || [];
  const total = customersData?.data?.total || 0;

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Locker Customers</h1>
          <p className="text-muted-foreground">
            Manage customer profiles and KYC verification
          </p>
        </div>
        <Button onClick={() => router.push("/lockers/customers/new")}>
          <Plus className="mr-2 h-4 w-4" />
          Add Customer
        </Button>
      </div>

      {/* Analytics Cards */}
      {analytics?.data && (
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Customers</CardTitle>
              <UserPlus className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {analytics.data.total_customers}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">KYC Pending</CardTitle>
              <AlertCircle className="h-4 w-4 text-orange-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {analytics.data.kyc_pending}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">KYC Completed</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {analytics.data.kyc_completed}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Premium Customers</CardTitle>
              <Shield className="h-4 w-4 text-purple-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {analytics.data.premium_customers}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Search and Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Search & Filter</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-5">
            <div className="relative md:col-span-2">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by name, mobile, email, PAN..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-8"
              />
            </div>

            <Select value={categoryFilter} onValueChange={setCategoryFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Category" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                <SelectItem value={CustomerCategory.REGULAR}>Regular</SelectItem>
                <SelectItem value={CustomerCategory.PREMIUM}>Premium</SelectItem>
                <SelectItem value={CustomerCategory.SENIOR_CITIZEN}>
                  Senior Citizen
                </SelectItem>
                <SelectItem value={CustomerCategory.STAFF}>Staff</SelectItem>
                <SelectItem value={CustomerCategory.VIP}>VIP</SelectItem>
              </SelectContent>
            </Select>

            <Select value={verificationFilter} onValueChange={setVerificationFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Verification" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value={VerificationStatus.VERIFIED}>Verified</SelectItem>
                <SelectItem value={VerificationStatus.PENDING}>Pending</SelectItem>
                <SelectItem value={VerificationStatus.REJECTED}>Rejected</SelectItem>
              </SelectContent>
            </Select>

            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="inactive">Inactive</SelectItem>
                <SelectItem value="blocked">Blocked</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Customer List */}
      <Card>
        <CardHeader>
          <CardTitle>Customers</CardTitle>
          <CardDescription>
            {total} customer{total !== 1 ? "s" : ""} found
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Customer ID</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Mobile</TableHead>
                  <TableHead>Category</TableHead>
                  <TableHead>Verification</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading ? (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center">
                      Loading customers...
                    </TableCell>
                  </TableRow>
                ) : customers.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center">
                      No customers found
                    </TableCell>
                  </TableRow>
                ) : (
                  customers.map((customer: LockerCustomer) => (
                    <TableRow key={customer.id}>
                      <TableCell className="font-medium">
                        {customer.locker_customer_id}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {customer.full_name}
                          {customer.is_senior_citizen && (
                            <Badge variant="outline" className="text-xs">
                              Senior
                            </Badge>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>{customer.mobile_number}</TableCell>
                      <TableCell>{getCategoryBadge(customer.customer_category)}</TableCell>
                      <TableCell>
                        {getVerificationStatusBadge(customer.verification_status)}
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant={customer.status === "active" ? "default" : "secondary"}
                        >
                          {customer.status}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {format(new Date(customer.created_at), "dd MMM yyyy")}
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() =>
                              router.push(`/lockers/customers/${customer.id}`)
                            }
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          {customer.verification_status === "pending" && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleVerify(customer)}
                            >
                              <CheckCircle className="h-4 w-4" />
                            </Button>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>

          {/* Pagination */}
          {total > pageSize && (
            <div className="flex items-center justify-between mt-4">
              <div className="text-sm text-muted-foreground">
                Showing {(page - 1) * pageSize + 1} to{" "}
                {Math.min(page * pageSize, total)} of {total} customers
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                >
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((p) => p + 1)}
                  disabled={page * pageSize >= total}
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Verify Dialog */}
      <Dialog open={showVerifyDialog} onOpenChange={setShowVerifyDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Verify Customer</DialogTitle>
            <DialogDescription>
              Update customer verification status
            </DialogDescription>
          </DialogHeader>

          {selectedCustomer && (
            <div className="space-y-4">
              <div>
                <p className="text-sm font-medium">Customer</p>
                <p className="text-sm text-muted-foreground">
                  {selectedCustomer.full_name} ({selectedCustomer.locker_customer_id})
                </p>
              </div>

              <div className="space-y-2">
                <Label>Verification Status</Label>
                <Select
                  value={verificationStatus}
                  onValueChange={(value) =>
                    setVerificationStatus(value as VerificationStatus)
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value={VerificationStatus.VERIFIED}>
                      Verified
                    </SelectItem>
                    <SelectItem value={VerificationStatus.REJECTED}>
                      Rejected
                    </SelectItem>
                    <SelectItem value={VerificationStatus.RESUBMISSION_REQUIRED}>
                      Resubmission Required
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Remarks</Label>
                <Input
                  placeholder="Add verification remarks..."
                  value={verificationRemarks}
                  onChange={(e) => setVerificationRemarks(e.target.value)}
                />
              </div>
            </div>
          )}

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setShowVerifyDialog(false);
                setSelectedCustomer(null);
                setVerificationRemarks("");
              }}
            >
              Cancel
            </Button>
            <Button
              onClick={handleVerifySubmit}
              disabled={verifyCustomer.isPending}
            >
              {verifyCustomer.isPending ? "Updating..." : "Update Status"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
