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
import { Package, Search, AlertTriangle } from "lucide-react";
import type { HousekeepingSupply } from "@/services/facility/types";
import { useToast } from "@/components/ui/use-toast";

export default function SupplyInventory() {
  const [supplies, setSupplies] = useState<HousekeepingSupply[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const { toast } = useToast();

  useEffect(() => {
    loadSupplies();
  }, []);

  const loadSupplies = async () => {
    try {
      setLoading(true);
      // Mock data for demonstration
      // In production, replace with: const response = await housekeepingService.getSupplies();
      const mockSupplies: HousekeepingSupply[] = [
        {
          id: 1,
          item_code: "SUP001",
          item_name: "Floor Cleaner",
          category: "Cleaning Agents",
          unit_of_measure: "Liters",
          current_stock: 45,
          minimum_stock: 20,
          reorder_quantity: 50,
          unit_price: 150,
          supplier_name: "CleanPro Supplies",
        },
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
          id: 4,
          item_code: "SUP004",
          item_name: "Disinfectant Spray",
          category: "Cleaning Agents",
          unit_of_measure: "Bottles",
          current_stock: 60,
          minimum_stock: 25,
          reorder_quantity: 50,
          unit_price: 200,
          supplier_name: "SafeClean Ltd",
        },
        {
          id: 5,
          item_code: "SUP005",
          item_name: "Garbage Bags (Large)",
          category: "Waste Management",
          unit_of_measure: "Pieces",
          current_stock: 120,
          minimum_stock: 100,
          reorder_quantity: 200,
          unit_price: 15,
          supplier_name: "EcoBag Solutions",
        },
      ];
      setSupplies(mockSupplies);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load supplies",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const isLowStock = (supply: HousekeepingSupply) => {
    return supply.current_stock <= supply.minimum_stock;
  };

  const getStockStatus = (supply: HousekeepingSupply) => {
    const percentage = (supply.current_stock / supply.minimum_stock) * 100;
    if (percentage <= 50) return { label: "Critical", color: "bg-red-500" };
    if (percentage <= 100) return { label: "Low Stock", color: "bg-orange-500" };
    return { label: "In Stock", color: "bg-green-500" };
  };

  const filteredSupplies = supplies.filter(
    (supply) =>
      supply.item_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      supply.item_code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      supply.category.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const lowStockCount = supplies.filter(isLowStock).length;
  const totalValue = supplies.reduce(
    (sum, item) => sum + item.current_stock * item.unit_price,
    0
  );

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Package className="h-5 w-5" />
              Supply Inventory
            </CardTitle>
            <CardDescription>
              Manage housekeeping supplies and stock levels
            </CardDescription>
          </div>
          {lowStockCount > 0 && (
            <Badge variant="destructive" className="flex items-center gap-1">
              <AlertTriangle className="h-3 w-3" />
              {lowStockCount} Low Stock Items
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent>
        {/* Summary Statistics */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <Card>
            <CardContent className="pt-6">
              <div className="text-2xl font-bold">{supplies.length}</div>
              <div className="text-sm text-gray-500">Total Items</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="text-2xl font-bold text-orange-600">
                {lowStockCount}
              </div>
              <div className="text-sm text-gray-500">Low Stock Items</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="text-2xl font-bold">₹{totalValue.toLocaleString()}</div>
              <div className="text-sm text-gray-500">Total Inventory Value</div>
            </CardContent>
          </Card>
        </div>

        {/* Search */}
        <div className="flex gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search supplies..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        {/* Supplies Table */}
        {loading ? (
          <div className="text-center py-8">Loading...</div>
        ) : filteredSupplies.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No supplies found.
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Item Code</TableHead>
                <TableHead>Item Name</TableHead>
                <TableHead>Category</TableHead>
                <TableHead>Current Stock</TableHead>
                <TableHead>Min Stock</TableHead>
                <TableHead>Reorder Qty</TableHead>
                <TableHead>Unit Price</TableHead>
                <TableHead>Total Value</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Supplier</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredSupplies.map((supply) => {
                const status = getStockStatus(supply);
                return (
                  <TableRow
                    key={supply.id}
                    className={isLowStock(supply) ? "bg-red-50" : ""}
                  >
                    <TableCell className="font-medium">
                      {supply.item_code}
                    </TableCell>
                    <TableCell>
                      <div className="font-medium">{supply.item_name}</div>
                      <div className="text-xs text-gray-500">
                        {supply.unit_of_measure}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{supply.category}</Badge>
                    </TableCell>
                    <TableCell>
                      <div className="font-semibold">{supply.current_stock}</div>
                    </TableCell>
                    <TableCell>{supply.minimum_stock}</TableCell>
                    <TableCell>{supply.reorder_quantity}</TableCell>
                    <TableCell>₹{supply.unit_price}</TableCell>
                    <TableCell className="font-semibold">
                      ₹{(supply.current_stock * supply.unit_price).toLocaleString()}
                    </TableCell>
                    <TableCell>
                      <Badge className={`${status.color} text-white`}>
                        {status.label}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-sm">{supply.supplier_name}</TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
