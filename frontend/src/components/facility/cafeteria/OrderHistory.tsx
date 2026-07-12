"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { History, Search, Calendar } from "lucide-react";
import { cafeteriaService } from "@/services/facility/cafeteriaService";
import type { CafeteriaOrder } from "@/services/facility/types";
import { useToast } from "@/components/ui/use-toast";

export default function OrderHistory() {
  const [orders, setOrders] = useState<CafeteriaOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [dateRange, setDateRange] = useState({
    from: "",
    to: "",
  });
  const { toast } = useToast();

  useEffect(() => {
    loadOrders();
  }, []);

  const loadOrders = async () => {
    try {
      setLoading(true);
      const params: any = { limit: 100 };
      if (filterStatus !== "all") params.status = filterStatus;
      if (dateRange.from) params.from_date = dateRange.from;
      if (dateRange.to) params.to_date = dateRange.to;

      const response = await cafeteriaService.getOrders(params);
      setOrders(response.items);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load order history",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadOrders();
  }, [filterStatus, dateRange]);

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: "bg-gray-500",
      confirmed: "bg-blue-500",
      preparing: "bg-orange-500",
      ready: "bg-green-500",
      served: "bg-green-600",
      cancelled: "bg-red-500",
    };
    return colors[status] || "bg-gray-500";
  };

  const filteredOrders = orders.filter(
    (order) =>
      order.order_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      order.employee_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalOrders = filteredOrders.length;
  const totalRevenue = filteredOrders.reduce((sum, order) => sum + order.net_amount, 0);
  const completedOrders = filteredOrders.filter((o) => o.status === "served").length;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <History className="h-5 w-5" />
              Order History
            </CardTitle>
            <CardDescription>View and analyze past cafeteria orders</CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {/* Statistics */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <Card>
            <CardContent className="pt-6">
              <div className="text-2xl font-bold">{totalOrders}</div>
              <div className="text-sm text-gray-500">Total Orders</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="text-2xl font-bold">{completedOrders}</div>
              <div className="text-sm text-gray-500">Completed Orders</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="text-2xl font-bold">₹{totalRevenue.toLocaleString()}</div>
              <div className="text-sm text-gray-500">Total Revenue</div>
            </CardContent>
          </Card>
        </div>

        {/* Filters */}
        <div className="flex gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search by order number or employee..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          <Select value={filterStatus} onValueChange={setFilterStatus}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="pending">Pending</SelectItem>
              <SelectItem value="confirmed">Confirmed</SelectItem>
              <SelectItem value="preparing">Preparing</SelectItem>
              <SelectItem value="ready">Ready</SelectItem>
              <SelectItem value="served">Served</SelectItem>
              <SelectItem value="cancelled">Cancelled</SelectItem>
            </SelectContent>
          </Select>
          <div className="flex gap-2 items-center">
            <Calendar className="h-4 w-4 text-gray-400" />
            <Input
              type="date"
              value={dateRange.from}
              onChange={(e) =>
                setDateRange({ ...dateRange, from: e.target.value })
              }
              className="w-40"
              placeholder="From"
            />
            <span className="text-gray-400">to</span>
            <Input
              type="date"
              value={dateRange.to}
              onChange={(e) =>
                setDateRange({ ...dateRange, to: e.target.value })
              }
              className="w-40"
              placeholder="To"
            />
          </div>
        </div>

        {/* Orders Table */}
        {loading ? (
          <div className="text-center py-8">Loading...</div>
        ) : filteredOrders.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No orders found for the selected criteria.
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Order Number</TableHead>
                <TableHead>Date & Time</TableHead>
                <TableHead>Employee</TableHead>
                <TableHead>Meal Type</TableHead>
                <TableHead>Amount</TableHead>
                <TableHead>Net Amount</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Delivery Location</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredOrders.map((order) => (
                <TableRow key={order.id}>
                  <TableCell className="font-medium">
                    {order.order_number}
                  </TableCell>
                  <TableCell>
                    <div>{new Date(order.order_date).toLocaleDateString()}</div>
                    <div className="text-xs text-gray-500">{order.order_time}</div>
                  </TableCell>
                  <TableCell>
                    <div>{order.employee_name}</div>
                    <div className="text-xs text-gray-500">
                      ID: {order.employee_id}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">
                      {order.meal_type.charAt(0).toUpperCase() +
                        order.meal_type.slice(1)}
                    </Badge>
                  </TableCell>
                  <TableCell>₹{order.total_amount.toFixed(2)}</TableCell>
                  <TableCell className="font-semibold">
                    ₹{order.net_amount.toFixed(2)}
                  </TableCell>
                  <TableCell>
                    <Badge
                      className={`${getStatusColor(order.status)} text-white`}
                    >
                      {order.status.replace("_", " ").toUpperCase()}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-sm">
                    {order.delivery_location || "-"}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
