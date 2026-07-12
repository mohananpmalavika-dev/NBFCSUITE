"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Edit, Leaf } from "lucide-react";
import type { MenuItem } from "@/services/facility/types";

interface MenuCardProps {
  item: MenuItem;
  onEdit?: () => void;
  onAddToCart?: (item: MenuItem) => void;
  showActions?: boolean;
}

export default function MenuCard({ item, onEdit, onAddToCart, showActions = true }: MenuCardProps) {
  const getMealTypeColor = (mealType: string) => {
    const colors: Record<string, string> = {
      breakfast: "bg-yellow-100 text-yellow-700",
      lunch: "bg-orange-100 text-orange-700",
      dinner: "bg-purple-100 text-purple-700",
      snacks: "bg-pink-100 text-pink-700",
      beverages: "bg-blue-100 text-blue-700",
    };
    return colors[mealType] || "bg-gray-100 text-gray-700";
  };

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardContent className="p-4">
        <div className="space-y-3">
          {/* Header */}
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="font-semibold text-lg">{item.item_name}</div>
              <div className="text-xs text-gray-500">{item.item_code}</div>
            </div>
            {item.is_vegetarian && (
              <div className="ml-2">
                <Leaf className="h-5 w-5 text-green-600" />
              </div>
            )}
          </div>

          {/* Badges */}
          <div className="flex gap-2">
            <Badge className={getMealTypeColor(item.meal_type)}>
              {item.meal_type.charAt(0).toUpperCase() + item.meal_type.slice(1)}
            </Badge>
            <Badge variant="outline" className="text-xs">
              {item.category.replace("_", " ")}
            </Badge>
          </div>

          {/* Image Placeholder */}
          {item.image_url ? (
            <img
              src={item.image_url}
              alt={item.item_name}
              className="w-full h-32 object-cover rounded-md"
            />
          ) : (
            <div className="w-full h-32 bg-gradient-to-br from-gray-100 to-gray-200 rounded-md flex items-center justify-center">
              <Leaf className="h-12 w-12 text-gray-400" />
            </div>
          )}

          {/* Pricing */}
          <div className="space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">Regular Price:</span>
              <span className="font-bold text-lg">₹{item.price}</span>
            </div>
            {item.employee_price && item.employee_price > 0 && (
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">Employee Price:</span>
                <span className="font-semibold text-green-600">
                  ₹{item.employee_price}
                </span>
              </div>
            )}
          </div>

          {/* Nutrition Info */}
          {item.calories && (
            <div className="text-xs text-gray-500">
              Calories: {item.calories} kcal
            </div>
          )}

          {/* Availability */}
          <Badge
            variant={item.is_available ? "default" : "secondary"}
            className={item.is_available ? "bg-green-500" : "bg-gray-400"}
          >
            {item.is_available ? "Available" : "Not Available"}
          </Badge>

          {/* Actions */}
          {showActions && (
            <div className="flex gap-2 pt-2">
              {onEdit && (
                <Button variant="outline" size="sm" onClick={onEdit} className="flex-1">
                  <Edit className="h-3 w-3 mr-1" />
                  Edit
                </Button>
              )}
              {onAddToCart && item.is_available && (
                <Button size="sm" onClick={() => onAddToCart(item)} className="flex-1">
                  Add to Cart
                </Button>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
