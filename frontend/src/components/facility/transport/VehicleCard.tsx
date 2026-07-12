"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Car, Users, Gauge, Fuel, Calendar, Edit } from "lucide-react";
import type { Vehicle } from "@/services/facility/types";

interface VehicleCardProps {
  vehicle: Vehicle;
  onEdit?: () => void;
  onSelect?: (vehicle: Vehicle) => void;
  showActions?: boolean;
}

export default function VehicleCard({ vehicle, onEdit, onSelect, showActions = true }: VehicleCardProps) {
  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      available: "bg-green-500",
      in_use: "bg-blue-500",
      maintenance: "bg-orange-500",
      out_of_service: "bg-red-500",
    };
    return colors[status] || "bg-gray-500";
  };

  const getVehicleIcon = (type: string) => {
    // Could return different icons based on type
    return Car;
  };

  const VehicleIcon = getVehicleIcon(vehicle.vehicle_type);

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardContent className="p-4">
        <div className="space-y-3">
          {/* Header */}
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <VehicleIcon className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <div className="font-bold text-lg">{vehicle.vehicle_number}</div>
                <div className="text-sm text-gray-500">
                  {vehicle.make_model || vehicle.vehicle_type.toUpperCase()}
                </div>
              </div>
            </div>
            <Badge className={`${getStatusColor(vehicle.status)} text-white`}>
              {vehicle.status.replace("_", " ").toUpperCase()}
            </Badge>
          </div>

          {/* Vehicle Details */}
          <div className="space-y-2 pt-2 border-t">
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2 text-gray-600">
                <Users className="h-4 w-4" />
                <span>Capacity</span>
              </div>
              <span className="font-semibold">
                {vehicle.seating_capacity || "N/A"}
              </span>
            </div>

            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2 text-gray-600">
                <Gauge className="h-4 w-4" />
                <span>Mileage</span>
              </div>
              <span className="font-semibold">
                {vehicle.current_mileage_km.toLocaleString()} km
              </span>
            </div>

            {vehicle.fuel_type && (
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2 text-gray-600">
                  <Fuel className="h-4 w-4" />
                  <span>Fuel Type</span>
                </div>
                <span className="font-semibold">{vehicle.fuel_type}</span>
              </div>
            )}

            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2 text-gray-600">
                <Badge variant="outline" className="text-xs">
                  {vehicle.ownership}
                </Badge>
              </div>
            </div>
          </div>

          {/* Vehicle Type Badge */}
          <div className="pt-2">
            <Badge variant="secondary">
              {vehicle.vehicle_type.replace("_", " ").toUpperCase()}
            </Badge>
          </div>

          {/* Actions */}
          {showActions && (
            <div className="flex gap-2 pt-2">
              {onEdit && (
                <Button variant="outline" size="sm" onClick={onEdit} className="flex-1">
                  <Edit className="h-3 w-3 mr-1" />
                  Edit
                </Button>
              )}
              {onSelect && vehicle.status === "available" && (
                <Button size="sm" onClick={() => onSelect(vehicle)} className="flex-1">
                  Select
                </Button>
              )}
            </div>
          )}

          {/* Availability Indicator */}
          {vehicle.status === "available" && (
            <div className="text-xs text-green-600 text-center pt-2 border-t">
              ✓ Available for booking
            </div>
          )}
          {vehicle.status === "maintenance" && (
            <div className="text-xs text-orange-600 text-center pt-2 border-t">
              ⚠ Under maintenance
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
