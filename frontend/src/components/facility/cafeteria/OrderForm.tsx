"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ShoppingCart, Plus, Minus, Trash2, Leaf } from "lucide-react";
import { cafeteriaService } from "@/services/facility/cafeteriaService";
import type { MenuItem, OrderItem, OrderFormData } from "@/services/facility/types";
import { useToast } from "@/components/ui/use-toast";

interface OrderFormProps {
  onClose: () => void;
  onSuccess: () => void;
}

export default function OrderForm({ onClose, onSuccess }: OrderFormProps) {
  const [menuItems, setMenuItems] = useState<MenuItem[]>([]);
  const [cart, setCart] = useState<Map<number, { item: MenuItem; quantity: number; instructions?: string }>>(
    new Map()
  );
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [filterMealType, setFilterMealType] = useState<string>("all");
  const { toast } = useToast();

  const [orderDetails, setOrderDetails] = useState({
    employee_id: 0,
    meal_type: "lunch",
    delivery_location: "",
  });

  useEffect(() => {
    loadMenuItems();
  }, [filterMealType]);

  const loadMenuItems = async () => {
    try {
      setLoading(true);
      const params: any = { limit: 100, is_available: true };
      if (filterMealType !== "all") params.meal_type = filterMealType;

      const response = await cafeteriaService.getMenuItems(params);
      setMenuItems(response.items);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load menu items",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const addToCart = (item: MenuItem) => {
    const newCart = new Map(cart);
    const existing = newCart.get(item.id);
    if (existing) {
      newCart.set(item.id, { ...existing, quantity: existing.quantity + 1 });
    } else {
      newCart.set(item.id, { item, quantity: 1 });
    }
    setCart(newCart);
  };

  const updateQuantity = (itemId: number, delta: number) => {
    const newCart = new Map(cart);
    const existing = newCart.get(itemId);
    if (existing) {
      const newQuantity = existing.quantity + delta;
      if (newQuantity <= 0) {
        newCart.delete(itemId);
      } else {
        newCart.set(itemId, { ...existing, quantity: newQuantity });
      }
      setCart(newCart);
    }
  };

  const removeFromCart = (itemId: number) => {
    const newCart = new Map(cart);
    newCart.delete(itemId);
    setCart(newCart);
  };

  const calculateTotal = () => {
    let total = 0;
    cart.forEach(({ item, quantity }) => {
      const price = item.employee_price && item.employee_price > 0 ? item.employee_price : item.price;
      total += price * quantity;
    });
    return total;
  };

  const handleSubmit = async () => {
    if (cart.size === 0) {
      toast({
        title: "Error",
        description: "Please add at least one item to your order",
        variant: "destructive",
      });
      return;
    }

    if (!orderDetails.employee_id) {
      toast({
        title: "Error",
        description: "Please enter employee ID",
        variant: "destructive",
      });
      return;
    }

    setSubmitting(true);

    try {
      const items: OrderItem[] = Array.from(cart.values()).map(({ item, quantity, instructions }) => ({
        menu_item_id: item.id,
        quantity,
        special_instructions: instructions,
      }));

      const orderData: OrderFormData = {
        employee_id: orderDetails.employee_id,
        meal_type: orderDetails.meal_type,
        delivery_location: orderDetails.delivery_location || undefined,
        items,
      };

      await cafeteriaService.createOrder(orderData);
      toast({
        title: "Success",
        description: "Order placed successfully",
      });
      onSuccess();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.message || "Failed to place order",
        variant: "destructive",
      });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <ShoppingCart className="h-5 w-5" />
            New Cafeteria Order
          </DialogTitle>
          <DialogDescription>
            Select items from the menu and place your order
          </DialogDescription>
        </DialogHeader>

        <div className="grid grid-cols-3 gap-6 py-4">
          {/* Menu Items (2/3 width) */}
          <div className="col-span-2 space-y-4">
            <div className="flex gap-4">
              <Select value={filterMealType} onValueChange={setFilterMealType}>
                <SelectTrigger>
                  <SelectValue placeholder="Filter by meal" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Meals</SelectItem>
                  <SelectItem value="breakfast">Breakfast</SelectItem>
                  <SelectItem value="lunch">Lunch</SelectItem>
                  <SelectItem value="dinner">Dinner</SelectItem>
                  <SelectItem value="snacks">Snacks</SelectItem>
                  <SelectItem value="beverages">Beverages</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="grid grid-cols-2 gap-3 max-h-96 overflow-y-auto">
              {loading ? (
                <div className="col-span-2 text-center py-8">Loading menu...</div>
              ) : menuItems.length === 0 ? (
                <div className="col-span-2 text-center py-8 text-gray-500">
                  No items available
                </div>
              ) : (
                menuItems.map((item) => (
                  <Card key={item.id} className="hover:shadow-md transition-shadow">
                    <CardContent className="p-3">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1">
                          <div className="font-semibold">{item.item_name}</div>
                          <div className="text-xs text-gray-500">{item.category}</div>
                        </div>
                        {item.is_vegetarian && (
                          <Leaf className="h-4 w-4 text-green-600" />
                        )}
                      </div>
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-bold">₹{item.price}</div>
                          {item.employee_price && item.employee_price > 0 && (
                            <div className="text-xs text-green-600">
                              Emp: ₹{item.employee_price}
                            </div>
                          )}
                        </div>
                        <Button size="sm" onClick={() => addToCart(item)}>
                          <Plus className="h-4 w-4" />
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </div>

          {/* Cart & Order Details (1/3 width) */}
          <div className="space-y-4">
            {/* Order Details */}
            <Card>
              <CardContent className="p-4 space-y-3">
                <h3 className="font-semibold">Order Details</h3>
                <div className="space-y-2">
                  <Label htmlFor="employee_id">Employee ID *</Label>
                  <Input
                    id="employee_id"
                    type="number"
                    value={orderDetails.employee_id || ""}
                    onChange={(e) =>
                      setOrderDetails({
                        ...orderDetails,
                        employee_id: parseInt(e.target.value) || 0,
                      })
                    }
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="meal_type">Meal Type</Label>
                  <Select
                    value={orderDetails.meal_type}
                    onValueChange={(value) =>
                      setOrderDetails({ ...orderDetails, meal_type: value })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="breakfast">Breakfast</SelectItem>
                      <SelectItem value="lunch">Lunch</SelectItem>
                      <SelectItem value="dinner">Dinner</SelectItem>
                      <SelectItem value="snacks">Snacks</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="delivery_location">Delivery Location</Label>
                  <Input
                    id="delivery_location"
                    value={orderDetails.delivery_location}
                    onChange={(e) =>
                      setOrderDetails({
                        ...orderDetails,
                        delivery_location: e.target.value,
                      })
                    }
                    placeholder="Optional"
                  />
                </div>
              </CardContent>
            </Card>

            {/* Cart */}
            <Card>
              <CardContent className="p-4">
                <h3 className="font-semibold mb-3">
                  Cart ({cart.size} {cart.size === 1 ? "item" : "items"})
                </h3>
                {cart.size === 0 ? (
                  <div className="text-center py-6 text-gray-500 text-sm">
                    Cart is empty
                  </div>
                ) : (
                  <div className="space-y-3 max-h-64 overflow-y-auto">
                    {Array.from(cart.values()).map(({ item, quantity }) => {
                      const price =
                        item.employee_price && item.employee_price > 0
                          ? item.employee_price
                          : item.price;
                      return (
                        <div key={item.id} className="border-b pb-2">
                          <div className="flex items-start justify-between mb-1">
                            <div className="text-sm font-medium">{item.item_name}</div>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-6 w-6 p-0"
                              onClick={() => removeFromCart(item.id)}
                            >
                              <Trash2 className="h-3 w-3 text-red-500" />
                            </Button>
                          </div>
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <Button
                                variant="outline"
                                size="sm"
                                className="h-6 w-6 p-0"
                                onClick={() => updateQuantity(item.id, -1)}
                              >
                                <Minus className="h-3 w-3" />
                              </Button>
                              <span className="text-sm font-semibold w-8 text-center">
                                {quantity}
                              </span>
                              <Button
                                variant="outline"
                                size="sm"
                                className="h-6 w-6 p-0"
                                onClick={() => updateQuantity(item.id, 1)}
                              >
                                <Plus className="h-3 w-3" />
                              </Button>
                            </div>
                            <div className="text-sm font-semibold">
                              ₹{(price * quantity).toFixed(2)}
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}

                {cart.size > 0 && (
                  <div className="mt-4 pt-3 border-t">
                    <div className="flex items-center justify-between font-bold text-lg">
                      <span>Total:</span>
                      <span>₹{calculateTotal().toFixed(2)}</span>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>

        <DialogFooter>
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={submitting || cart.size === 0}>
            {submitting ? "Placing Order..." : "Place Order"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
