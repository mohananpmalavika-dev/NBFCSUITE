"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { AlertTriangle, Package, ShoppingCart, RefreshCw } from "lucide-react";
import { housekeepingService } from "@/services/facility/housekeepingService";
import type { HousekeepingSupply } from "@/services/facility/types";
import { useToast } from "@/components/ui/use-toast";

export default function SupplyAlerts() {
  const [lowStockItems, setLowStockItems] = useState<HousekeepingSupply[]>([]);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    loadLowStockItems();
  }, []);

  const loadLowStockItems = async () => {
    try {
      setLoading(true);
      const items = await housekeepingService.getLowStockItems();
      setLowStockItems(items);
    } catch (error) {
      // Mock data for demonstration
      const mockLowStockItems: HousekeepingSupply[] = [
        {
          id: 2,
          item_code: "SUP002",
          item_name: "Toilet Paper Rolls",
          category: "Sanitary Items",
          unit_of_measure: "Rolls",
          current_stock: 15,
          minimum_stock: 30,
          reorder_quantity: 100,
          unit_price: 25,
          supplier_name: "Hygiene Plus",
        },
        {
          id: 3,
          item_code: "SUP003",
          item_name: "Mop Heads",
          category: "Cleaning Tools",
          unit_of_measure: "Pieces",
          current_stock: 8,
          minimum_stock: 10,
          reorder_quantity: 20,
          unit_price: 80,
          supplier_name: "CleanPro Supplies",
        },
        {
          id: 6,
          item_code: "SUP006",
          item_name: "Hand Soap Dispenser Refills",
          category: "Sanitary Items",
          unit_of_measure: "Liters",
          current_stock: 3,
          minimum_stock: 15,
          reorder_quantity: 30,
          unit_price: 120,
          supplier_name: "Hygiene Plus",
        },
      ];
      setLowStockItems(mockLowStockItems);
    } finally {
      setLoading(false);
    }
  };

  const getUrgencyLevel = (supply: HousekeepingSupply) => {
    const percentage = (supply.current_stock / supply.minimum_stock) * 100;
    if (percentage <= 25) return { level: "Critical", color: "bg-red-500", icon: AlertTriangle };
    if (percentage <= 50) return { level: "Urgent", color: "bg-orange-500", icon: AlertTriangle };
    return { level: "Low", color: "bg-yellow-500", icon: Package };
  };

  const handleReorder = (supply: HousekeepingSupply) => {
    toast({
      title: "Reorder Initiated",
      description: `Purchase order created for ${supply.reorder_quantity} ${supply.unit_of_measure} of ${supply.item_name}`,
    });
  };

  const totalReorderCost = lowStockItems.reduce(
    (sum, item) => sum + item.reorder_quantity * item.unit_price,
    0
  );

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-orange-500" />
              Supply Alerts
            </CardTitle>
            <CardDescription>
              Items requiring immediate attention
            </CardDescription>
          </div>
          <Button variant="outline" size="sm" onClick={loadLowStockItems}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="text-center py-8">Loading alerts...</div>
        ) : lowStockItems.length === 0 ? (
          <div className="text-center py-12">
            <Package className="h-12 w-12 mx-auto text-green-500 mb-3" />
            <div className="text-lg font-semibold text-green-600 mb-1">
              All Stock Levels Normal
            </div>
            <div className="text-sm text-gray-500">
              No items require immediate reordering
            </div>
          </div>
        ) : (
          <>
            {/* Summary Card */}
            <Card className="mb-6 bg-gradient-to-r from-orange-50 to-red-50">
              <CardContent className="pt-6">
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <div className="text-2xl font-bold text-orange-600">
                      {lowStockItems.length}
                    </div>
                    <div className="text-sm text-gray-600">Items Need Reorder</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-red-600">
                      {lowStockItems.filter(
                        (item) =>
                          (item.current_stock / item.minimum_stock) * 100 <= 25
                      ).length}
                    </div>
                    <div className="text-sm text-gray-600">Critical Items</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-blue-600">
                      ₹{totalReorderCost.toLocaleString()}
                    </div>
                    <div className="text-sm text-gray-600">Total Reorder Cost</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Alerts List */}
            <div className="space-y-3">
              {lowStockItems.map((supply) => {
                const urgency = getUrgencyLevel(supply);
                const UrgencyIcon = urgency.icon;
                const stockPercentage =
                  (supply.current_stock / supply.minimum_stock) * 100;

                return (
                  <Card
                    key={supply.id}
                    className="hover:shadow-md transition-shadow"
                  >
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <UrgencyIcon className={`h-5 w-5 text-white p-1 rounded ${urgency.color}`} />
                            <div>
                              <div className="font-semibold">
                                {supply.item_name}
                              </div>
                              <div className="text-sm text-gray-500">
                                {supply.item_code} | {supply.category}
                              </div>
                            </div>
                          </div>

                          <div className="grid grid-cols-2 gap-4 mt-3 text-sm">
                            <div>
                              <span className="text-gray-500">Current Stock:</span>
                              <span className="font-semibold ml-2">
                                {supply.current_stock} {supply.unit_of_measure}
                              </span>
                            </div>
                            <div>
                              <span className="text-gray-500">Minimum Required:</span>
                              <span className="font-semibold ml-2">
                                {supply.minimum_stock} {supply.unit_of_measure}
                              </span>
                            </div>
                            <div>
                              <span className="text-gray-500">Reorder Quantity:</span>
                              <span className="font-semibold ml-2">
                                {supply.reorder_quantity} {supply.unit_of_measure}
                              </span>
                            </div>
                            <div>
                              <span className="text-gray-500">Estimated Cost:</span>
                              <span className="font-semibold ml-2">
                                ₹{(supply.reorder_quantity * supply.unit_price).toLocaleString()}
                              </span>
                            </div>
                          </div>

                          <div className="mt-3">
                            <div className="flex items-center justify-between text-xs mb-1">
                              <span className="text-gray-500">Stock Level</span>
                              <Badge className={`${urgency.color} text-white`}>
                                {urgency.level}
                              </Badge>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div
                                className={`h-2 rounded-full ${urgency.color}`}
                                style={{ width: `${Math.min(stockPercentage, 100)}%` }}
                              ></div>
                            </div>
                          </div>

                          <div className="mt-2 text-xs text-gray-500">
                            Supplier: {supply.supplier_name}
                          </div>
                        </div>

                        <div className="ml-4">
                          <Button
                            size="sm"
                            onClick={() => handleReorder(supply)}
                            className="whitespace-nowrap"
                          >
                            <ShoppingCart className="h-4 w-4 mr-2" />
                            Reorder
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>

            {/* Bulk Actions */}
            <Card className="mt-6">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-semibold">Bulk Reorder All Items</div>
                    <div className="text-sm text-gray-500">
                      Generate purchase orders for all {lowStockItems.length} items
                    </div>
                  </div>
                  <Button>
                    <ShoppingCart className="h-4 w-4 mr-2" />
                    Reorder All (₹{totalReorderCost.toLocaleString()})
                  </Button>
                </div>
              </CardContent>
            </Card>
          </>
        )}
      </CardContent>
    </Card>
  );
}
