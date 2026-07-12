"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ChefHat, Clock, CheckCircle, AlertCircle, Bell } from "lucide-react";
import { cafeteriaService } from "@/services/facility/cafeteriaService";
import type { CafeteriaOrder } from "@/services/facility/types";
import { useToast } from "@/components/ui/use-toast";

export default function KitchenDisplay() {
  const [orders, setOrders] = useState<CafeteriaOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>("all");
  const { toast } = useToast();

  useEffect(() => {
    loadOrders();
    // Auto-refresh every 5 seconds for real-time updates
    const interval = setInterval(loadOrders, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadOrders = async () => {
    try {
      const response = await cafeteriaService.getOrders({ limit: 50 });
      // Filter to show only active kitchen orders
      const activeOrders = response.items.filter(
        (order) => !["served", "cancelled"].includes(order.status)
      );
      setOrders(activeOrders);
      setLoading(false);
    } catch (error) {
      if (!loading) {
        toast({
          title: "Error",
          description: "Failed to load orders",
          variant: "destructive",
        });
      }
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (orderId: number, newStatus: string) => {
    try {
      await cafeteriaService.updateOrderStatus(orderId, newStatus);
      toast({
        title: "Success",
        description: `Order status updated to ${newStatus}`,
      });
      loadOrders();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.message || "Failed to update order status",
        variant: "destructive",
      });
    }
  };

  const getOrderAge = (orderDate: string, orderTime: string) => {
    const orderDateTime = new Date(`${orderDate}T${orderTime}`);
    const now = new Date();
    const diffMs = now.getTime() - orderDateTime.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    return diffMins;
  };

  const getUrgencyColor = (age: number) => {
    if (age > 20) return "border-red-500 bg-red-50";
    if (age > 10) return "border-orange-500 bg-orange-50";
    return "border-blue-500 bg-blue-50";
  };

  const filteredOrders = orders.filter((order) => {
    if (filter === "all") return true;
    return order.status === filter;
  });

  const pendingCount = orders.filter((o) => o.status === "pending").length;
  const confirmingCount = orders.filter((o) => o.status === "confirmed").length;
  const preparingCount = orders.filter((o) => o.status === "preparing").length;
  const readyCount = orders.filter((o) => o.status === "ready").length;

  return (
    <div className="space-y-6">
      {/* Header with Stats */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <ChefHat className="h-6 w-6" />
            Kitchen Display System
          </h2>
          <p className="text-gray-500">Manage and track orders in real-time</p>
        </div>
        <div className="flex items-center gap-2">
          <Bell className="h-5 w-5 text-gray-400" />
          <span className="text-sm text-gray-500">
            Last updated: {new Date().toLocaleTimeString()}
          </span>
        </div>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-4 gap-4">
        <Card
          className={`cursor-pointer transition-all ${
            filter === "pending" ? "ring-2 ring-gray-500" : ""
          }`}
          onClick={() => setFilter(filter === "pending" ? "all" : "pending")}
        >
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-3xl font-bold text-gray-700">{pendingCount}</div>
                <div className="text-sm text-gray-500">New Orders</div>
              </div>
              <Clock className="h-8 w-8 text-gray-400" />
            </div>
          </CardContent>
        </Card>

        <Card
          className={`cursor-pointer transition-all ${
            filter === "confirmed" ? "ring-2 ring-blue-500" : ""
          }`}
          onClick={() => setFilter(filter === "confirmed" ? "all" : "confirmed")}
        >
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-3xl font-bold text-blue-700">{confirmingCount}</div>
                <div className="text-sm text-gray-500">Confirmed</div>
              </div>
              <CheckCircle className="h-8 w-8 text-blue-400" />
            </div>
          </CardContent>
        </Card>

        <Card
          className={`cursor-pointer transition-all ${
            filter === "preparing" ? "ring-2 ring-orange-500" : ""
          }`}
          onClick={() => setFilter(filter === "preparing" ? "all" : "preparing")}
        >
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-3xl font-bold text-orange-700">{preparingCount}</div>
                <div className="text-sm text-gray-500">In Preparation</div>
              </div>
              <ChefHat className="h-8 w-8 text-orange-400" />
            </div>
          </CardContent>
        </Card>

        <Card
          className={`cursor-pointer transition-all ${
            filter === "ready" ? "ring-2 ring-green-500" : ""
          }`}
          onClick={() => setFilter(filter === "ready" ? "all" : "ready")}
        >
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-3xl font-bold text-green-700">{readyCount}</div>
                <div className="text-sm text-gray-500">Ready</div>
              </div>
              <CheckCircle className="h-8 w-8 text-green-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Orders Grid */}
      {loading ? (
        <div className="text-center py-12">Loading orders...</div>
      ) : filteredOrders.length === 0 ? (
        <Card>
          <CardContent className="py-12">
            <div className="text-center">
              <ChefHat className="h-12 w-12 mx-auto text-gray-400 mb-3" />
              <div className="text-lg font-semibold text-gray-600 mb-1">
                No Active Orders
              </div>
              <div className="text-sm text-gray-500">
                {filter === "all"
                  ? "All orders have been completed"
                  : `No orders in ${filter} status`}
              </div>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-3 gap-4">
          {filteredOrders.map((order) => {
            const age = getOrderAge(order.order_date, order.order_time);
            const urgencyColor = getUrgencyColor(age);

            return (
              <Card
                key={order.id}
                className={`border-2 ${urgencyColor} transition-all hover:shadow-lg`}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-lg">{order.order_number}</CardTitle>
                      <div className="text-sm text-gray-600 mt-1">
                        {order.employee_name}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="flex items-center gap-1 text-sm font-semibold">
                        <Clock className="h-4 w-4" />
                        {age} min
                      </div>
                      {age > 15 && (
                        <Badge variant="destructive" className="mt-1">
                          URGENT
                        </Badge>
                      )}
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  {/* Order Info */}
                  <div className="space-y-1">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-500">Meal:</span>
                      <Badge variant="outline">
                        {order.meal_type.charAt(0).toUpperCase() + order.meal_type.slice(1)}
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-500">Time:</span>
                      <span className="font-medium">{order.order_time}</span>
                    </div>
                    {order.delivery_location && (
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-500">Location:</span>
                        <span className="font-medium">{order.delivery_location}</span>
                      </div>
                    )}
                  </div>

                  {/* Current Status */}
                  <div className="p-2 bg-white rounded-md">
                    <div className="text-xs text-gray-500 mb-1">Current Status</div>
                    <Badge
                      className={`w-full justify-center ${
                        order.status === "pending"
                          ? "bg-gray-500"
                          : order.status === "confirmed"
                          ? "bg-blue-500"
                          : order.status === "preparing"
                          ? "bg-orange-500"
                          : "bg-green-500"
                      } text-white`}
                    >
                      {order.status.toUpperCase()}
                    </Badge>
                  </div>

                  {/* Action Buttons */}
                  <div className="space-y-2 pt-2">
                    {order.status === "pending" && (
                      <Button
                        className="w-full"
                        onClick={() => handleStatusUpdate(order.id, "confirmed")}
                      >
                        <CheckCircle className="h-4 w-4 mr-2" />
                        Confirm Order
                      </Button>
                    )}

                    {order.status === "confirmed" && (
                      <Button
                        className="w-full bg-orange-500 hover:bg-orange-600"
                        onClick={() => handleStatusUpdate(order.id, "preparing")}
                      >
                        <ChefHat className="h-4 w-4 mr-2" />
                        Start Preparing
                      </Button>
                    )}

                    {order.status === "preparing" && (
                      <Button
                        className="w-full bg-green-500 hover:bg-green-600"
                        onClick={() => handleStatusUpdate(order.id, "ready")}
                      >
                        <CheckCircle className="h-4 w-4 mr-2" />
                        Mark as Ready
                      </Button>
                    )}

                    {order.status === "ready" && (
                      <Button
                        className="w-full bg-green-600 hover:bg-green-700"
                        onClick={() => handleStatusUpdate(order.id, "served")}
                      >
                        <CheckCircle className="h-4 w-4 mr-2" />
                        Mark as Served
                      </Button>
                    )}

                    {order.status !== "ready" && order.status !== "served" && (
                      <Button
                        variant="outline"
                        className="w-full text-red-500 hover:text-red-600"
                        onClick={() => handleStatusUpdate(order.id, "cancelled")}
                      >
                        <AlertCircle className="h-4 w-4 mr-2" />
                        Cancel Order
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
