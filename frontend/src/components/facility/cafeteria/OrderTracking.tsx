"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Clock, CheckCircle, ChefHat, Package, XCircle } from "lucide-react";
import { cafeteriaService } from "@/services/facility/cafeteriaService";
import type { CafeteriaOrder } from "@/services/facility/types";
import { useToast } from "@/components/ui/use-toast";

interface OrderTrackingProps {
  orderId?: number;
  employeeId?: number;
}

export default function OrderTracking({ orderId, employeeId }: OrderTrackingProps) {
  const [orders, setOrders] = useState<CafeteriaOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    loadOrders();
    // Set up polling for real-time updates
    const interval = setInterval(loadOrders, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, [orderId, employeeId]);

  const loadOrders = async () => {
    try {
      setLoading(true);
      const params: any = { limit: 10 };
      if (orderId) params.order_id = orderId;
      if (employeeId) params.employee_id = employeeId;

      const response = await cafeteriaService.getOrders(params);
      // Filter to show only active orders
      const activeOrders = response.items.filter(
        (order) => !["served", "cancelled"].includes(order.status)
      );
      setOrders(activeOrders);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load orders",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const getStatusInfo = (status: string) => {
    const statusMap: Record<
      string,
      { label: string; icon: any; color: string; bgColor: string }
    > = {
      pending: {
        label: "Order Received",
        icon: Clock,
        color: "text-gray-600",
        bgColor: "bg-gray-100",
      },
      confirmed: {
        label: "Order Confirmed",
        icon: CheckCircle,
        color: "text-blue-600",
        bgColor: "bg-blue-100",
      },
      preparing: {
        label: "Being Prepared",
        icon: ChefHat,
        color: "text-orange-600",
        bgColor: "bg-orange-100",
      },
      ready: {
        label: "Ready for Pickup",
        icon: Package,
        color: "text-green-600",
        bgColor: "bg-green-100",
      },
      served: {
        label: "Served",
        icon: CheckCircle,
        color: "text-green-600",
        bgColor: "bg-green-100",
      },
      cancelled: {
        label: "Cancelled",
        icon: XCircle,
        color: "text-red-600",
        bgColor: "bg-red-100",
      },
    };
    return statusMap[status] || statusMap.pending;
  };

  const getProgressPercentage = (status: string) => {
    const statusProgress: Record<string, number> = {
      pending: 25,
      confirmed: 40,
      preparing: 65,
      ready: 90,
      served: 100,
      cancelled: 0,
    };
    return statusProgress[status] || 0;
  };

  const getEstimatedTime = (status: string) => {
    const timeEstimates: Record<string, string> = {
      pending: "Waiting for confirmation",
      confirmed: "Preparing in 5-10 mins",
      preparing: "Ready in 10-15 mins",
      ready: "Ready for pickup now!",
      served: "Order completed",
      cancelled: "Order cancelled",
    };
    return timeEstimates[status] || "Processing...";
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Package className="h-5 w-5" />
          Order Tracking
        </CardTitle>
        <CardDescription>Track your cafeteria orders in real-time</CardDescription>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="text-center py-8">Loading orders...</div>
        ) : orders.length === 0 ? (
          <div className="text-center py-12">
            <Package className="h-12 w-12 mx-auto text-gray-400 mb-3" />
            <div className="text-lg font-semibold text-gray-600 mb-1">
              No Active Orders
            </div>
            <div className="text-sm text-gray-500">
              Your orders will appear here once placed
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {orders.map((order) => {
              const statusInfo = getStatusInfo(order.status);
              const StatusIcon = statusInfo.icon;
              const progress = getProgressPercentage(order.status);

              return (
                <Card key={order.id} className="overflow-hidden">
                  <CardContent className="p-6">
                    {/* Order Header */}
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <div className="font-bold text-lg">{order.order_number}</div>
                        <div className="text-sm text-gray-500">
                          {new Date(order.order_date).toLocaleDateString()} at{" "}
                          {order.order_time}
                        </div>
                        <div className="text-sm text-gray-600 mt-1">
                          {order.employee_name}
                        </div>
                      </div>
                      <Badge className={`${statusInfo.bgColor} ${statusInfo.color}`}>
                        <StatusIcon className="h-3 w-3 mr-1" />
                        {statusInfo.label}
                      </Badge>
                    </div>

                    {/* Progress Bar */}
                    <div className="mb-4">
                      <div className="flex items-center justify-between text-xs mb-2">
                        <span className="font-medium">{getEstimatedTime(order.status)}</span>
                        <span className="text-gray-500">{progress}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-3">
                        <div
                          className={`h-3 rounded-full transition-all duration-500 ${
                            order.status === "cancelled"
                              ? "bg-red-500"
                              : "bg-gradient-to-r from-blue-500 to-green-500"
                          }`}
                          style={{ width: `${progress}%` }}
                        ></div>
                      </div>
                    </div>

                    {/* Status Timeline */}
                    <div className="grid grid-cols-5 gap-2 mb-4">
                      {["pending", "confirmed", "preparing", "ready", "served"].map(
                        (status, index) => {
                          const info = getStatusInfo(status);
                          const Icon = info.icon;
                          const isActive =
                            ["pending", "confirmed", "preparing", "ready", "served"].indexOf(
                              order.status
                            ) >= index;
                          const isCurrent = order.status === status;

                          return (
                            <div
                              key={status}
                              className={`text-center ${
                                isActive ? "opacity-100" : "opacity-30"
                              }`}
                            >
                              <div
                                className={`mx-auto w-10 h-10 rounded-full flex items-center justify-center mb-1 ${
                                  isCurrent
                                    ? `${info.bgColor} ${info.color} ring-2 ring-offset-2 ring-${info.color.replace(
                                        "text-",
                                        ""
                                      )}`
                                    : isActive
                                    ? `${info.bgColor} ${info.color}`
                                    : "bg-gray-100 text-gray-400"
                                }`}
                              >
                                <Icon className="h-5 w-5" />
                              </div>
                              <div className="text-xs font-medium">
                                {status.charAt(0).toUpperCase() + status.slice(1)}
                              </div>
                            </div>
                          );
                        }
                      )}
                    </div>

                    {/* Order Details */}
                    <div className="border-t pt-4">
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-gray-500">Meal Type:</span>
                          <span className="font-medium ml-2">
                            {order.meal_type.charAt(0).toUpperCase() +
                              order.meal_type.slice(1)}
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-500">Total Amount:</span>
                          <span className="font-bold ml-2">
                            ₹{order.total_amount.toFixed(2)}
                          </span>
                        </div>
                        {order.delivery_location && (
                          <div className="col-span-2">
                            <span className="text-gray-500">Delivery Location:</span>
                            <span className="font-medium ml-2">
                              {order.delivery_location}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Actions */}
                    {order.status === "ready" && (
                      <div className="mt-4 p-3 bg-green-50 rounded-lg border border-green-200">
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="font-semibold text-green-700">
                              Your order is ready!
                            </div>
                            <div className="text-sm text-green-600">
                              Please collect from the cafeteria counter
                            </div>
                          </div>
                          <Package className="h-8 w-8 text-green-600" />
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
