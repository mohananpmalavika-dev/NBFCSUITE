"use client";

import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import {
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  Download,
  Calendar,
  DollarSign,
  Percent,
  Grid3x3,
  Users,
  Lock,
} from "lucide-react";
import { lockerService, LockerSize, LockerStatus } from "@/services/locker.service";
import { format } from "date-fns";

const COLORS = {
  primary: "#3b82f6",
  success: "#10b981",
  warning: "#f59e0b",
  danger: "#ef4444",
  purple: "#8b5cf6",
  teal: "#14b8a6",
};

const SIZE_COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444"];
const STATUS_COLORS = ["#10b981", "#3b82f6", "#f59e0b", "#ef4444"];

export default function LockerDashboardPage() {
  const [selectedBranch, setSelectedBranch] = useState("all");
  const [dateRange, setDateRange] = useState("this_year");

  // Fetch dashboard data
  const { data: dashboard, isLoading } = useQuery({
    queryKey: ["locker-dashboard"],
    queryFn: () => lockerService.getDashboard(),
  });

  // Fetch occupancy stats
  const { data: occupancyStats } = useQuery({
    queryKey: ["locker-occupancy-stats", selectedBranch],
    queryFn: () =>
      lockerService.getOccupancyStats(
        selectedBranch !== "all" ? selectedBranch : undefined
      ),
  });

  // Fetch revenue stats
  const { data: revenueStats } = useQuery({
    queryKey: ["locker-revenue-stats", dateRange],
    queryFn: () => lockerService.getRevenueStats(),
  });

  if (isLoading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center h-64">
          <p>Loading dashboard...</p>
        </div>
      </div>
    );
  }

  // Prepare chart data
  const occupancyBySize = occupancyStats?.by_size
    ? Object.entries(occupancyStats.by_size).map(([size, data]: [string, any]) => ({
        name: size,
        occupied: data.occupied,
        available: data.available,
        occupancy: data.occupancy_rate,
      }))
    : [];

  const occupancyByStatus = occupancyStats?.by_status
    ? Object.entries(occupancyStats.by_status).map(([status, count]) => ({
        name: status,
        value: count,
      }))
    : [];

  const revenueByMonth = revenueStats?.monthly_trend || [];

  const occupancyPieData = [
    { name: "Allocated", value: dashboard?.total_allocated || 0 },
    { name: "Available", value: dashboard?.total_available || 0 },
  ];

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Locker Management Dashboard</h1>
          <p className="text-muted-foreground">
            Overview of locker occupancy, revenue, and performance
          </p>
        </div>
        <Button>
          <Download className="mr-2 h-4 w-4" />
          Export Report
        </Button>
      </div>

      {/* Alert Section */}
      {(dashboard?.expiring_soon > 0 || dashboard?.overdue_payments > 0) && (
        <div className="grid gap-4 md:grid-cols-2">
          {dashboard?.expiring_soon > 0 && (
            <Alert>
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                {dashboard.expiring_soon} locker allocation(s) expiring within 30 days
              </AlertDescription>
            </Alert>
          )}
          {dashboard?.overdue_payments > 0 && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                {dashboard.overdue_payments} locker(s) have overdue rent payments
              </AlertDescription>
            </Alert>
          )}
        </div>
      )}

      {/* Key Metrics Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Lockers</CardTitle>
            <Lock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboard?.total_lockers || 0}</div>
            <p className="text-xs text-muted-foreground">
              Across all branches
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Occupancy Rate</CardTitle>
            <Percent className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {dashboard?.occupancy_rate?.toFixed(1) || 0}%
            </div>
            <p className="text-xs text-muted-foreground">
              {dashboard?.total_allocated} allocated
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ₹{revenueStats?.total_collected?.toLocaleString() || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              This financial year
            </p>
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
            <p className="text-xs text-muted-foreground">
              Efficiency metric
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="occupancy">Occupancy Analytics</TabsTrigger>
          <TabsTrigger value="revenue">Revenue Analytics</TabsTrigger>
          <TabsTrigger value="recent">Recent Activity</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            {/* Occupancy Pie Chart */}
            <Card>
              <CardHeader>
                <CardTitle>Locker Occupancy</CardTitle>
                <CardDescription>Current allocation status</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={occupancyPieData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) =>
                        `${name}: ${(percent * 100).toFixed(0)}%`
                      }
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {occupancyPieData.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={index === 0 ? COLORS.success : COLORS.primary}
                        />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
                <div className="mt-4 grid grid-cols-2 gap-4 text-center">
                  <div>
                    <p className="text-2xl font-bold text-green-600">
                      {dashboard?.total_allocated}
                    </p>
                    <p className="text-sm text-muted-foreground">Allocated</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-blue-600">
                      {dashboard?.total_available}
                    </p>
                    <p className="text-sm text-muted-foreground">Available</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Revenue Trend Chart */}
            <Card>
              <CardHeader>
                <CardTitle>Revenue Trend</CardTitle>
                <CardDescription>Monthly collection performance</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={revenueByMonth}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="amount"
                      stroke={COLORS.success}
                      strokeWidth={2}
                      name="Revenue (₹)"
                    />
                  </LineChart>
                </ResponsiveContainer>
                <div className="mt-4 flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">This Month</p>
                    <p className="text-xl font-bold">
                      ₹{revenueStats?.current_month_collection?.toLocaleString() || 0}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-muted-foreground">Outstanding</p>
                    <p className="text-xl font-bold text-orange-600">
                      ₹{revenueStats?.outstanding_amount?.toLocaleString() || 0}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Occupancy by Size */}
          <Card>
            <CardHeader>
              <CardTitle>Occupancy by Locker Size</CardTitle>
              <CardDescription>Allocation distribution across sizes</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={occupancyBySize}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="occupied" fill={COLORS.success} name="Occupied" />
                  <Bar dataKey="available" fill={COLORS.primary} name="Available" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Occupancy Analytics Tab */}
        <TabsContent value="occupancy" className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Occupancy Analytics</h2>
            <Select value={selectedBranch} onValueChange={setSelectedBranch}>
              <SelectTrigger className="w-[200px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Branches</SelectItem>
                <SelectItem value="main">Main Branch</SelectItem>
                <SelectItem value="north">North Branch</SelectItem>
                <SelectItem value="south">South Branch</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Total Lockers</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">
                  {occupancyStats?.total_lockers || 0}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Occupied</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-green-600">
                  {occupancyStats?.occupied_lockers || 0}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Available</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-blue-600">
                  {occupancyStats?.available_lockers || 0}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Occupancy by Status */}
          <Card>
            <CardHeader>
              <CardTitle>Locker Status Distribution</CardTitle>
              <CardDescription>Breakdown by operational status</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={occupancyByStatus}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value }) => `${name}: ${value}`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {occupancyByStatus.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={STATUS_COLORS[index % STATUS_COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Size-wise Occupancy Table */}
          <Card>
            <CardHeader>
              <CardTitle>Size-wise Occupancy Details</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Size</TableHead>
                    <TableHead>Total</TableHead>
                    <TableHead>Occupied</TableHead>
                    <TableHead>Available</TableHead>
                    <TableHead>Occupancy Rate</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {occupancyBySize.map((row) => (
                    <TableRow key={row.name}>
                      <TableCell className="font-medium">{row.name}</TableCell>
                      <TableCell>{row.occupied + row.available}</TableCell>
                      <TableCell>{row.occupied}</TableCell>
                      <TableCell>{row.available}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-green-600 h-2 rounded-full"
                              style={{ width: `${row.occupancy}%` }}
                            />
                          </div>
                          <span className="text-sm font-medium">
                            {row.occupancy.toFixed(1)}%
                          </span>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Revenue Analytics Tab */}
        <TabsContent value="revenue" className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Revenue Analytics</h2>
            <Select value={dateRange} onValueChange={setDateRange}>
              <SelectTrigger className="w-[200px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="this_month">This Month</SelectItem>
                <SelectItem value="this_quarter">This Quarter</SelectItem>
                <SelectItem value="this_year">This Year</SelectItem>
                <SelectItem value="last_year">Last Year</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="grid gap-4 md:grid-cols-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Total Collected</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  ₹{revenueStats?.total_collected?.toLocaleString() || 0}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Outstanding</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-orange-600">
                  ₹{revenueStats?.outstanding_amount?.toLocaleString() || 0}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Overdue Count</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">
                  {revenueStats?.overdue_count || 0}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Avg. Per Locker</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  ₹{revenueStats?.average_rent?.toLocaleString() || 0}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Monthly Revenue Trend */}
          <Card>
            <CardHeader>
              <CardTitle>Monthly Revenue Trend</CardTitle>
              <CardDescription>Collection performance over time</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={350}>
                <LineChart data={revenueByMonth}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip
                    formatter={(value: any) => `₹${value.toLocaleString()}`}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="amount"
                    stroke={COLORS.success}
                    strokeWidth={3}
                    name="Revenue"
                    dot={{ r: 4 }}
                    activeDot={{ r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Revenue by Payment Type */}
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Collection Efficiency</CardTitle>
                <CardDescription>Payment collection performance</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Efficiency Rate</span>
                    <span className="text-2xl font-bold">
                      {revenueStats?.collection_efficiency?.toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-4">
                    <div
                      className="bg-green-600 h-4 rounded-full transition-all"
                      style={{
                        width: `${revenueStats?.collection_efficiency || 0}%`,
                      }}
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4 pt-4">
                    <div>
                      <p className="text-sm text-muted-foreground">Expected</p>
                      <p className="text-xl font-bold">
                        ₹
                        {(
                          (revenueStats?.total_collected || 0) +
                          (revenueStats?.outstanding_amount || 0)
                        ).toLocaleString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Collected</p>
                      <p className="text-xl font-bold text-green-600">
                        ₹{revenueStats?.total_collected?.toLocaleString() || 0}
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Payment Statistics</CardTitle>
                <CardDescription>This financial year</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between items-center p-2 bg-blue-50 rounded">
                    <span className="text-sm">Total Transactions</span>
                    <span className="font-bold">
                      {revenueStats?.total_transactions || 0}
                    </span>
                  </div>
                  <div className="flex justify-between items-center p-2 bg-green-50 rounded">
                    <span className="text-sm">Rent Collected</span>
                    <span className="font-bold">
                      ₹{revenueStats?.rent_collected?.toLocaleString() || 0}
                    </span>
                  </div>
                  <div className="flex justify-between items-center p-2 bg-purple-50 rounded">
                    <span className="text-sm">Deposits Received</span>
                    <span className="font-bold">
                      ₹{revenueStats?.deposit_collected?.toLocaleString() || 0}
                    </span>
                  </div>
                  <div className="flex justify-between items-center p-2 bg-orange-50 rounded">
                    <span className="text-sm">Penalties Collected</span>
                    <span className="font-bold">
                      ₹{revenueStats?.penalty_collected?.toLocaleString() || 0}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Recent Activity Tab */}
        <TabsContent value="recent" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            {/* Recent Allocations */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Allocations</CardTitle>
                <CardDescription>Latest locker assignments</CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Locker</TableHead>
                      <TableHead>Customer</TableHead>
                      <TableHead>Date</TableHead>
                      <TableHead>Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {dashboard?.recent_allocations?.slice(0, 5).map((allocation: any) => (
                      <TableRow key={allocation.id}>
                        <TableCell className="font-medium">
                          {allocation.locker_number}
                        </TableCell>
                        <TableCell>{allocation.customer_name}</TableCell>
                        <TableCell>
                          {format(new Date(allocation.allocation_date), "dd MMM")}
                        </TableCell>
                        <TableCell>
                          <Badge variant="secondary">{allocation.status}</Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                    {!dashboard?.recent_allocations?.length && (
                      <TableRow>
                        <TableCell colSpan={4} className="text-center text-muted-foreground">
                          No recent allocations
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>

            {/* Recent Payments */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Payments</CardTitle>
                <CardDescription>Latest rent collections</CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Receipt</TableHead>
                      <TableHead>Customer</TableHead>
                      <TableHead>Date</TableHead>
                      <TableHead className="text-right">Amount</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {dashboard?.recent_payments?.slice(0, 5).map((payment: any) => (
                      <TableRow key={payment.id}>
                        <TableCell className="font-medium">
                          {payment.receipt_number}
                        </TableCell>
                        <TableCell>{payment.customer_name}</TableCell>
                        <TableCell>
                          {format(new Date(payment.payment_date), "dd MMM")}
                        </TableCell>
                        <TableCell className="text-right font-medium">
                          ₹{payment.amount?.toLocaleString()}
                        </TableCell>
                      </TableRow>
                    ))}
                    {!dashboard?.recent_payments?.length && (
                      <TableRow>
                        <TableCell colSpan={4} className="text-center text-muted-foreground">
                          No recent payments
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </div>

          {/* Expiring Soon */}
          <Card>
            <CardHeader>
              <CardTitle>Expiring Allocations</CardTitle>
              <CardDescription>Allocations expiring within 30 days</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Locker</TableHead>
                    <TableHead>Customer</TableHead>
                    <TableHead>Contact</TableHead>
                    <TableHead>End Date</TableHead>
                    <TableHead>Days Left</TableHead>
                    <TableHead>Annual Rent</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {dashboard?.expiring_allocations?.map((allocation: any) => {
                    const daysLeft = Math.ceil(
                      (new Date(allocation.end_date).getTime() - new Date().getTime()) /
                        (1000 * 60 * 60 * 24)
                    );
                    return (
                      <TableRow key={allocation.id}>
                        <TableCell className="font-medium">
                          {allocation.locker_number}
                        </TableCell>
                        <TableCell>{allocation.customer_name}</TableCell>
                        <TableCell>{allocation.customer_contact}</TableCell>
                        <TableCell>
                          {format(new Date(allocation.end_date), "dd MMM yyyy")}
                        </TableCell>
                        <TableCell>
                          <Badge
                            variant={daysLeft <= 7 ? "destructive" : "warning"}
                          >
                            {daysLeft} days
                          </Badge>
                        </TableCell>
                        <TableCell>₹{allocation.annual_rent?.toLocaleString()}</TableCell>
                      </TableRow>
                    );
                  })}
                  {!dashboard?.expiring_allocations?.length && (
                    <TableRow>
                      <TableCell colSpan={6} className="text-center text-muted-foreground">
                        No allocations expiring soon
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
