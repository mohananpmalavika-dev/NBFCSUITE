"use client";

/**
 * Customer Dashboard Page
 * Main landing page for Customer 360 module with statistics and quick actions
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import {
  Users,
  UserCheck,
  UserX,
  AlertTriangle,
  Ban,
  UserPlus,
  TrendingUp,
  CreditCard,
  Search,
  Filter,
  Download,
  RefreshCw,
} from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import customerService from "@/services/customer.service";
import type { CustomerDashboardStats, CustomerListItem } from "@/types/customer.types";

export default function CustomerDashboardPage() {
  const router = useRouter();
  const [searchTerm, setSearchTerm] = useState("");

  // Fetch dashboard statistics
  const { data: stats, isLoading: statsLoading, refetch: refetchStats } = useQuery({
    queryKey: ["customer-stats"],
    queryFn: customerService.getCustomerStats,
  });

  // Fetch recent customers
  const { data: recentCustomers, isLoading: customersLoading } = useQuery({
    queryKey: ["recent-customers"],
    queryFn: () => customerService.getCustomers({ page: 1, page_size: 5 }),
  });

  const handleSearch = () => {
    if (searchTerm.trim()) {
      router.push(`/customers/list?search=${encodeURIComponent(searchTerm)}`);
    }
  };

  const handleCreateCustomer = () => {
    router.push("/customers/create");
  };

  const handleViewAllCustomers = () => {
    router.push("/customers/list");
  };

  const handleViewCustomer = (customerId: number) => {
    router.push(`/customers/${customerId}`);
  };

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Customer 360</h1>
          <p className="text-muted-foreground">
            Complete customer information and relationship management
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => refetchStats()}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Refresh
          </Button>
          <Button onClick={handleCreateCustomer}>
            <UserPlus className="mr-2 h-4 w-4" />
            New Customer
          </Button>
        </div>
      </div>

      {/* Quick Search */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Search</CardTitle>
          <CardDescription>
            Search customers by name, mobile, email, PAN, or customer code
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search customers..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleSearch()}
                className="pl-10"
              />
            </div>
            <Button onClick={handleSearch}>
              <Search className="mr-2 h-4 w-4" />
              Search
            </Button>
            <Button variant="outline" onClick={handleViewAllCustomers}>
              <Filter className="mr-2 h-4 w-4" />
              Advanced
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Statistics Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {/* Total Customers */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Customers</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {statsLoading ? (
              <Skeleton className="h-8 w-20" />
            ) : (
              <>
                <div className="text-2xl font-bold">
                  {stats?.total_customers.toLocaleString() || 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  {stats?.active_customers || 0} active
                </p>
              </>
            )}
          </CardContent>
        </Card>

        {/* KYC Pending */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">KYC Pending</CardTitle>
            <UserX className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            {statsLoading ? (
              <Skeleton className="h-8 w-20" />
            ) : (
              <>
                <div className="text-2xl font-bold text-orange-600">
                  {stats?.kyc_pending.toLocaleString() || 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  {stats?.kyc_completed || 0} completed
                </p>
              </>
            )}
          </CardContent>
        </Card>

        {/* High Risk */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">High Risk</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            {statsLoading ? (
              <Skeleton className="h-8 w-20" />
            ) : (
              <>
                <div className="text-2xl font-bold text-red-600">
                  {stats?.high_risk_customers.toLocaleString() || 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  Requires attention
                </p>
              </>
            )}
          </CardContent>
        </Card>

        {/* New This Month */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">New This Month</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            {statsLoading ? (
              <Skeleton className="h-8 w-20" />
            ) : (
              <>
                <div className="text-2xl font-bold text-green-600">
                  {stats?.new_this_month.toLocaleString() || 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  This month
                </p>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Secondary Stats */}
      <div className="grid gap-4 md:grid-cols-3">
        {/* Average CIBIL */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average CIBIL Score</CardTitle>
            <CreditCard className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {statsLoading ? (
              <Skeleton className="h-8 w-20" />
            ) : (
              <>
                <div className="text-2xl font-bold">
                  {stats?.avg_cibil_score || "N/A"}
                </div>
                <p className="text-xs text-muted-foreground">
                  Portfolio average
                </p>
              </>
            )}
          </CardContent>
        </Card>

        {/* Blacklisted */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Blacklisted</CardTitle>
            <Ban className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            {statsLoading ? (
              <Skeleton className="h-8 w-20" />
            ) : (
              <>
                <div className="text-2xl font-bold text-red-600">
                  {stats?.blacklisted_customers.toLocaleString() || 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  Not eligible for loans
                </p>
              </>
            )}
          </CardContent>
        </Card>

        {/* KYC Completed */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">KYC Completed</CardTitle>
            <UserCheck className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            {statsLoading ? (
              <Skeleton className="h-8 w-20" />
            ) : (
              <>
                <div className="text-2xl font-bold text-green-600">
                  {stats?.kyc_completed.toLocaleString() || 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  Verified customers
                </p>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Recent Customers */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Recent Customers</CardTitle>
              <CardDescription>Latest customer registrations</CardDescription>
            </div>
            <Button variant="outline" size="sm" onClick={handleViewAllCustomers}>
              View All
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {customersLoading ? (
            <div className="space-y-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="flex items-center gap-4">
                  <Skeleton className="h-10 w-10 rounded-full" />
                  <div className="flex-1 space-y-2">
                    <Skeleton className="h-4 w-[200px]" />
                    <Skeleton className="h-3 w-[150px]" />
                  </div>
                </div>
              ))}
            </div>
          ) : recentCustomers?.items && recentCustomers.items.length > 0 ? (
            <div className="space-y-4">
              {recentCustomers.items.map((customer) => (
                <div
                  key={customer.id}
                  className="flex items-center justify-between gap-4 rounded-lg border p-4 transition-colors hover:bg-muted/50 cursor-pointer"
                  onClick={() => handleViewCustomer(customer.id)}
                >
                  <div className="flex items-center gap-4">
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
                      <Users className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <div className="font-medium">{customer.full_name}</div>
                      <div className="text-sm text-muted-foreground">
                        {customer.customer_code} • {customer.mobile}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge
                      variant={
                        customer.kyc_status === "completed"
                          ? "default"
                          : customer.kyc_status === "in_progress"
                          ? "secondary"
                          : "outline"
                      }
                    >
                      {customer.kyc_status.toUpperCase()}
                    </Badge>
                    <Badge
                      variant={
                        customer.risk_rating === "low"
                          ? "default"
                          : customer.risk_rating === "medium"
                          ? "secondary"
                          : "destructive"
                      }
                    >
                      {customer.risk_rating.toUpperCase()}
                    </Badge>
                    {customer.cibil_score && (
                      <Badge variant="outline">
                        CIBIL: {customer.cibil_score}
                      </Badge>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <Users className="mb-4 h-12 w-12 text-muted-foreground" />
              <h3 className="mb-2 text-lg font-medium">No customers yet</h3>
              <p className="mb-4 text-sm text-muted-foreground">
                Get started by creating your first customer
              </p>
              <Button onClick={handleCreateCustomer}>
                <UserPlus className="mr-2 h-4 w-4" />
                Create Customer
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Common customer management tasks</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Button
              variant="outline"
              className="h-auto flex-col gap-2 py-4"
              onClick={handleCreateCustomer}
            >
              <UserPlus className="h-6 w-6" />
              <span>New Customer</span>
            </Button>
            <Button
              variant="outline"
              className="h-auto flex-col gap-2 py-4"
              onClick={() => router.push("/customers/list?kyc_status=pending")}
            >
              <UserX className="h-6 w-6" />
              <span>Pending KYC</span>
            </Button>
            <Button
              variant="outline"
              className="h-auto flex-col gap-2 py-4"
              onClick={() => router.push("/customers/list?risk_rating=high")}
            >
              <AlertTriangle className="h-6 w-6" />
              <span>High Risk</span>
            </Button>
            <Button
              variant="outline"
              className="h-auto flex-col gap-2 py-4"
              onClick={async () => {
                const blob = await customerService.exportCustomers();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = `customers-${new Date().toISOString().split("T")[0]}.xlsx`;
                a.click();
              }}
            >
              <Download className="h-6 w-6" />
              <span>Export Data</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
