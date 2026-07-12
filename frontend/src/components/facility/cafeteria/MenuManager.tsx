"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
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
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Plus, Utensils, Search, Edit, Trash2 } from "lucide-react";
import { cafeteriaService } from "@/services/facility/cafeteriaService";
import type { MenuItem, MenuItemFormData } from "@/services/facility/types";
import { useToast } from "@/components/ui/use-toast";
import MenuCard from "./MenuCard";

export default function MenuManager() {
  const [menuItems, setMenuItems] = useState<MenuItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingItem, setEditingItem] = useState<MenuItem | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterMealType, setFilterMealType] = useState<string>("all");
  const [filterCategory, setFilterCategory] = useState<string>("all");
  const { toast } = useToast();

  const [formData, setFormData] = useState<MenuItemFormData>({
    item_code: "",
    item_name: "",
    meal_type: "breakfast",
    category: "main_course",
    price: 0,
    employee_price: 0,
    is_vegetarian: true,
  });

  useEffect(() => {
    loadMenuItems();
  }, []);

  const loadMenuItems = async () => {
    try {
      setLoading(true);
      const params: any = { limit: 100 };
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

  useEffect(() => {
    loadMenuItems();
  }, [filterMealType]);

  const handleAdd = () => {
    setEditingItem(null);
    setFormData({
      item_code: "",
      item_name: "",
      meal_type: "breakfast",
      category: "main_course",
      price: 0,
      employee_price: 0,
      is_vegetarian: true,
    });
    setShowForm(true);
  };

  const handleEdit = (item: MenuItem) => {
    setEditingItem(item);
    setFormData({
      item_code: item.item_code,
      item_name: item.item_name,
      meal_type: item.meal_type,
      category: item.category,
      price: item.price,
      employee_price: item.employee_price,
      is_vegetarian: item.is_vegetarian,
    });
    setShowForm(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await cafeteriaService.createMenuItem(formData);
      toast({
        title: "Success",
        description: `Menu item ${editingItem ? "updated" : "created"} successfully`,
      });
      setShowForm(false);
      loadMenuItems();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.message || "Failed to save menu item",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const filteredItems = menuItems.filter((item) => {
    const matchesSearch =
      item.item_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.item_code.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory =
      filterCategory === "all" || item.category === filterCategory;
    return matchesSearch && matchesCategory;
  });

  const categories = Array.from(new Set(menuItems.map((item) => item.category)));

  return (
    <>
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Utensils className="h-5 w-5" />
                Menu Management
              </CardTitle>
              <CardDescription>
                Manage cafeteria menu items and pricing
              </CardDescription>
            </div>
            <Button onClick={handleAdd}>
              <Plus className="h-4 w-4 mr-2" />
              Add Menu Item
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {/* Filters */}
          <div className="flex gap-4 mb-6">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search menu items..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select value={filterMealType} onValueChange={setFilterMealType}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Meal Type" />
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
            <Select value={filterCategory} onValueChange={setFilterCategory}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Category" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                {categories.map((cat) => (
                  <SelectItem key={cat} value={cat}>
                    {cat.replace("_", " ")}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Menu Items Grid */}
          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : filteredItems.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No menu items found. Add your first item to get started.
            </div>
          ) : (
            <div className="grid grid-cols-3 gap-4">
              {filteredItems.map((item) => (
                <MenuCard
                  key={item.id}
                  item={item}
                  onEdit={() => handleEdit(item)}
                />
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Menu Item Form Dialog */}
      {showForm && (
        <Dialog open={true} onOpenChange={() => setShowForm(false)}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>
                {editingItem ? "Edit Menu Item" : "Add New Menu Item"}
              </DialogTitle>
              <DialogDescription>
                Enter menu item details
              </DialogDescription>
            </DialogHeader>

            <form onSubmit={handleSubmit}>
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="item_code">Item Code *</Label>
                    <Input
                      id="item_code"
                      value={formData.item_code}
                      onChange={(e) =>
                        setFormData({ ...formData, item_code: e.target.value })
                      }
                      required
                      disabled={!!editingItem}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="item_name">Item Name *</Label>
                    <Input
                      id="item_name"
                      value={formData.item_name}
                      onChange={(e) =>
                        setFormData({ ...formData, item_name: e.target.value })
                      }
                      required
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="meal_type">Meal Type *</Label>
                    <Select
                      value={formData.meal_type}
                      onValueChange={(value) =>
                        setFormData({ ...formData, meal_type: value })
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
                        <SelectItem value="beverages">Beverages</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="category">Category</Label>
                    <Input
                      id="category"
                      value={formData.category}
                      onChange={(e) =>
                        setFormData({ ...formData, category: e.target.value })
                      }
                      placeholder="e.g., main_course, dessert"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="price">Regular Price *</Label>
                    <Input
                      id="price"
                      type="number"
                      min="0"
                      step="0.01"
                      value={formData.price}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          price: parseFloat(e.target.value) || 0,
                        })
                      }
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="employee_price">Employee Price</Label>
                    <Input
                      id="employee_price"
                      type="number"
                      min="0"
                      step="0.01"
                      value={formData.employee_price}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          employee_price: parseFloat(e.target.value) || 0,
                        })
                      }
                    />
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="is_vegetarian"
                    checked={formData.is_vegetarian}
                    onCheckedChange={(checked) =>
                      setFormData({
                        ...formData,
                        is_vegetarian: checked as boolean,
                      })
                    }
                  />
                  <Label htmlFor="is_vegetarian" className="cursor-pointer">
                    Vegetarian
                  </Label>
                </div>
              </div>

              <DialogFooter>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setShowForm(false)}
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={loading}>
                  {loading ? "Saving..." : editingItem ? "Update" : "Create"}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      )}
    </>
  );
}
