"use client";

/**
 * Customer List Page
 * Advanced customer listing with search, filters, pagination, and bulk actions
 */

import { Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import {
  Search,
  Filter,
  Download,
  UserPlus,
  Eye,
  Edit,
  Trash2,
  MoreVertical,
  RefreshCw,
  X,
} from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/components/ui/use-toast";
import customerService from "@/services/customer.service";
import { KYCStatusEnum, RiskRatingEnum } from "@/types/customer.types";
import type { CustomerFilters } from "@/types/customer.types";

export default function CustomerListPage() {
  return (
    <Suspense fallback={<div className="p-6 text-sm text-muted-foreground">Loading customers...</div>}>
      <CustomerListContent />
    </Suspense>
  );
}

function CustomerListContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { toast } = useToast();

  // Initialize filters from URL params
  const [filters, setFilters] = useState<CustomerFilters>({
    search: searchParams.get("search") || "",
    kyc_status: (searchParams.get("kyc_status") as KYCStatusEnum) || undefined,
    risk_rating: (searchParams.get("risk_rating") as RiskRatingEnum) || undefined,
    is_active: searchParams.get("is_active") ? searchParams.get("is_active") === "true" : undefined,
    page: parseInt(searchParams.get("page") || "1"),
    page_size: parseInt(searchParams.get("page_size") || "20"),
  });

  const [showFilters, setShowFilters] = useState(false);

  // Fetch customers with filters
  const {
    data: customersData,
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ["customers", filters],
    queryFn: () => customerService.getCustomers(filters),
  });

  const handleSearch = (search: string) => {
    setFilters({ ...filters, search, page: 1 });
  };

  const handleFilterChange = (key: keyof CustomerFilters, value: any) => {
    setFilters({ ...filters, [key]: value, page: 1 });
  };

  const handleClearFilters = () => {
    setFilters({
      search: "",
      page: 1,
      page_size: 20,
    });
    setShowFilters(false);
  };

  const handlePageChange = (newPage: number) => {
    setFilters({ ...filters, page: newPage });
  };

  const handleViewCustomer = (customerId: number) => {
    router.push(`/customers/${customerId}`);
  };

  const handleEditCustomer = (customerId: number) => {
    router.push(`/customers/${customerId}/edit`);
  };

  const handleDeleteCustomer = async (customerId: number) => {
    if (!confirm("Are you sure you want to delete this customer?")) return;

    try {
      await customerService.deleteCustomer(customerId);
      toast({
        title: "Customer deleted",
        description: "Customer has been successfully deleted.",
      });
      refetch();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to delete customer",
        variant: "destructive",
      });
    }
  };

  const handleExport = async () => {
    try {
      const blob = await customerService.exportCustomers(filters);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `customers-${new Date().toISOString().split("T")[0]}.xlsx`;
      a.click();
      toast({
        title: "Export successful",
        description: "Customer data has been exported to Excel.",
      });
    } catch (error: any) {
      toast({
        title: "Export failed",
        description: error.message || "Failed to export data",
        variant: "destructive",
      });
    }
  };

  const getKYCBadge = (status: KYCStatusEnum) => {
    const variants: Record<KYCStatusEnum, "default" | "secondary" | "outline" | "destructive"> = {
      [KYCStatusEnum.COMPLETED]: "default",
      [KYCStatusEnum.IN_PROGRESS]: "secondary",
      [KYCStatusEnum.PENDING]: "outline",
      [KYCStatusEnum.REJECTED]: "destructive",
    };
    return <Badge variant={variants[status]}>{status.toUpperCase()}</Badge>;
  };

  const getRiskBadge = (risk: RiskRatingEnum) => {
    const variants: Record<RiskRatingEnum, "default" | "secondary" | "outline" | "destructive"> = {
      [RiskRatingEnum.LOW]: "default",
      [RiskRatingEnum.MEDIUM]: "secondary",
      [RiskRatingEnum.HIGH]: "outline",
      [RiskRatingEnum.VERY_HIGH]: "destructive",
    };
    const colors: Record<RiskRatingEnum, string> = {
      [RiskRatingEnum.LOW]: "text-green-600",
      [RiskRatingEnum.MEDIUM]: "text-yellow-600",
      [RiskRatingEnum.HIGH]: "text-orange-600",
      [RiskRatingEnum.VERY_HIGH]: "text-red-600",
    };
    return (
      <Badge variant={variants[risk]} className={colors[risk]}>
        {risk.toUpperCase()}
      </Badge>
    );
  };

  const activeFiltersCount = [
    filters.search,
    filters.kyc_status,
    filters.risk_rating,
    filters.is_active !== undefined,
  ].filter(Boolean).length;

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">All Customers</h1>
          <p className="text-muted-foreground">
            {customersData?.total || 0} customers found
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => refetch()}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Refresh
          </Button>
          <Button variant="outline" size="sm" onClick={handleExport}>
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
          <Button onClick={() => router.push("/customers/create")}>
            <UserPlus className="mr-2 h-4 w-4" />
            New Customer
          </Button>
        </div>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Search & Filter</CardTitle>
              <CardDescription>Find customers using various criteria</CardDescription>
            </div>
            {activeFiltersCount > 0 && (
              <Button variant="ghost" size="sm" onClick={handleClearFilters}>
                <X className="mr-2 h-4 w-4" />
                Clear Filters ({activeFiltersCount})
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Search Bar */}
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search by name, mobile, email, PAN, customer code..."
                value={filters.search}
                onChange={(e) => handleSearch(e.target.value)}
                className="pl-10"
              />
            </div>
            <Button
              variant="outline"
              onClick={() => setShowFilters(!showFilters)}
            >
              <Filter className="mr-2 h-4 w-4" />
              Filters
              {activeFiltersCount > 0 && (
                <Badge variant="secondary" className="ml-2">
                  {activeFiltersCount}
                </Badge>
              )}
            </Button>
          </div>

          {/* Advanced Filters */}
          {showFilters && (
            <div className="grid gap-4 md:grid-cols-4 rounded-lg border p-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">KYC Status</label>
                <Select
                  value={filters.kyc_status}
                  onValueChange={(value) =>
                    handleFilterChange("kyc_status", value as KYCStatusEnum)
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="All statuses" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Statuses</SelectItem>
                    <SelectItem value={KYCStatusEnum.PENDING}>Pending</SelectItem>
                    <SelectItem value={KYCStatusEnum.IN_PROGRESS}>In Progress</SelectItem>
                    <SelectItem value={KYCStatusEnum.COMPLETED}>Completed</SelectItem>
                    <SelectItem value={KYCStatusEnum.REJECTED}>Rejected</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Risk Rating</label>
                <Select
                  value={filters.risk_rating}
                  onValueChange={(value) =>
                    handleFilterChange("risk_rating", value as RiskRatingEnum)
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="All ratings" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Ratings</SelectItem>
                    <SelectItem value={RiskRatingEnum.LOW}>Low</SelectItem>
                    <SelectItem value={RiskRatingEnum.MEDIUM}>Medium</SelectItem>
                    <SelectItem value={RiskRatingEnum.HIGH}>High</SelectItem>
                    <SelectItem value={RiskRatingEnum.VERY_HIGH}>Very High</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Account Status</label>
                <Select
                  value={filters.is_active === undefined ? "all" : filters.is_active.toString()}
                  onValueChange={(value) =>
                    handleFilterChange(
                      "is_active",
                      value === "all" ? undefined : value === "true"
                    )
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="All" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All</SelectItem>
                    <SelectItem value="true">Active</SelectItem>
                    <SelectItem value="false">Inactive</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Page Size</label>
                <Select
                  value={filters.page_size?.toString()}
                  onValueChange={(value) =>
                    handleFilterChange("page_size", parseInt(value))
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="10">10 per page</SelectItem>
                    <SelectItem value="20">20 per page</SelectItem>
                    <SelectItem value="50">50 per page</SelectItem>
                    <SelectItem value="100">100 per page</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Customer Table */}
      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Customer Code</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Mobile</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>KYC Status</TableHead>
                  <TableHead>Risk Rating</TableHead>
                  <TableHead>CIBIL Score</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading ? (
                  // Loading skeleton
                  Array.from({ length: 5 }).map((_, i) => (
                    <TableRow key={i}>
                      <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                      <TableCell><Skeleton className="h-4 w-32" /></TableCell>
                      <TableCell><Skeleton className="h-4 w-28" /></TableCell>
                      <TableCell><Skeleton className="h-4 w-36" /></TableCell>
                      <TableCell><Skeleton className="h-6 w-20" /></TableCell>
                      <TableCell><Skeleton className="h-6 w-16" /></TableCell>
                      <TableCell><Skeleton className="h-4 w-12" /></TableCell>
                      <TableCell><Skeleton className="h-6 w-16" /></TableCell>
                      <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                      <TableCell><Skeleton className="h-8 w-8" /></TableCell>
                    </TableRow>
                  ))
                ) : customersData?.items && customersData.items.length > 0 ? (
                  customersData.items.map((customer) => (
                    <TableRow
                      key={customer.id}
                      className="cursor-pointer hover:bg-muted/50"
                      onClick={() => handleViewCustomer(customer.id)}
                    >
                      <TableCell className="font-mono text-sm">
                        {customer.customer_code}
                      </TableCell>
                      <TableCell className="font-medium">
                        {customer.full_name}
                      </TableCell>
                      <TableCell>{customer.mobile}</TableCell>
                      <TableCell className="text-muted-foreground">
                        {customer.email || "—"}
                      </TableCell>
                      <TableCell>{getKYCBadge(customer.kyc_status)}</TableCell>
                      <TableCell>{getRiskBadge(customer.risk_rating)}</TableCell>
                      <TableCell>
                        {customer.cibil_score ? (
                          <span className="font-semibold">{customer.cibil_score}</span>
                        ) : (
                          <span className="text-muted-foreground">—</span>
                        )}
                      </TableCell>
                      <TableCell>
                        <Badge variant={customer.is_active ? "default" : "secondary"}>
                          {customer.is_active ? "Active" : "Inactive"}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {new Date(customer.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell className="text-right" onClick={(e) => e.stopPropagation()}>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="sm">
                              <MoreVertical className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuLabel>Actions</DropdownMenuLabel>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem onClick={() => handleViewCustomer(customer.id)}>
                              <Eye className="mr-2 h-4 w-4" />
                              View Details
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleEditCustomer(customer.id)}>
                              <Edit className="mr-2 h-4 w-4" />
                              Edit
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem
                              onClick={() => handleDeleteCustomer(customer.id)}
                              className="text-red-600"
                            >
                              <Trash2 className="mr-2 h-4 w-4" />
                              Delete
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={10} className="h-32 text-center">
                      <div className="flex flex-col items-center justify-center text-muted-foreground">
                        <Search className="mb-2 h-8 w-8" />
                        <p>No customers found</p>
                        <p className="text-sm">Try adjusting your search or filters</p>
                      </div>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      {/* Pagination */}
      {customersData && customersData.pages > 1 && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-muted-foreground">
            Showing {((filters.page || 1) - 1) * (filters.page_size || 20) + 1} to{" "}
            {Math.min((filters.page || 1) * (filters.page_size || 20), customersData.total)} of{" "}
            {customersData.total} customers
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={filters.page === 1}
              onClick={() => handlePageChange((filters.page || 1) - 1)}
            >
              Previous
            </Button>
            <div className="flex items-center gap-1">
              {Array.from({ length: Math.min(5, customersData.pages) }, (_, i) => {
                const page = i + 1;
                return (
                  <Button
                    key={page}
                    variant={filters.page === page ? "default" : "outline"}
                    size="sm"
                    onClick={() => handlePageChange(page)}
                  >
                    {page}
                  </Button>
                );
              })}
              {customersData.pages > 5 && <span className="px-2">...</span>}
            </div>
            <Button
              variant="outline"
              size="sm"
              disabled={filters.page === customersData.pages}
              onClick={() => handlePageChange((filters.page || 1) + 1)}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
