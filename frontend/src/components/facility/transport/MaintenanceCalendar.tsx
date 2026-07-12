"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Calendar, Wrench, AlertTriangle, CheckCircle } from "lucide-react";
import { transportService } from "@/services/facility/transportService";
import type { Vehicle } from "@/services/facility/types";
import { useToast } from "@/components/ui/use-toast";

export default function MaintenanceCalendar() {
  const [upcomingMaintenance, setUpcomingMaintenance] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    loadUpcomingMaintenance();
  }, []);

  const loadUpcomingMaintenance = async () => {
    try {
      setLoading(true);
      const vehicles = await transportService.getUpcomingMaintenance(30);
      setUpcomingMaintenance(vehicles);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load maintenance schedule",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const getMaintenancePriority = (vehicle: Vehicle) => {
    // Simple logic based on mileage
    if (vehicle.current_mileage_km > 100000) {
      return { level: "High", color: "bg-red-500", icon: AlertTriangle };
    } else if (vehicle.current_mileage_km > 50000) {
      return { level: "Medium", color: "bg-orange-500", icon: Wrench };
    }
    return { level: "Low", color: "bg-blue-500", icon: CheckCircle };
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Maintenance Schedule
            </CardTitle>
            <CardDescription>
              Upcoming vehicle maintenance and service
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="text-center py-8">Loading schedule...</div>
        ) : upcomingMaintenance.length === 0 ? (
          <div className="text-center py-12">
            <CheckCircle className="h-12 w-12 mx-auto text-green-500 mb-3" />
            <div className="text-lg font-semibold text-green-600 mb-1">
              All Vehicles Up to Date
            </div>
            <div className="text-sm text-gray-500">
              No maintenance scheduled for the next 30 days
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            {upcomingMaintenance.map((vehicle) => {
              const priority = getMaintenancePriority(vehicle);
              const PriorityIcon = priority.icon;

              return (
                <Card
                  key={vehicle.id}
                  className="hover:shadow-md transition-shadow"
                >
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <div
                            className={`p-2 ${priority.color} text-white rounded-lg`}
                          >
                            <PriorityIcon className="h-5 w-5" />
                          </div>
                          <div>
                            <div className="font-bold text-lg">
                              {vehicle.vehicle_number}
                            </div>
                            <div className="text-sm text-gray-500">
                              {vehicle.make_model || vehicle.vehicle_type}
                            </div>
                          </div>
                        </div>

                        <div className="grid grid-cols-3 gap-4 mt-3 text-sm">
                          <div>
                            <div className="text-xs text-gray-500">Current Mileage</div>
                            <div className="font-semibold">
                              {vehicle.current_mileage_km.toLocaleString()} km
                            </div>
                          </div>
                          <div>
                            <div className="text-xs text-gray-500">Fuel Type</div>
                            <div className="font-semibold">
                              {vehicle.fuel_type || "N/A"}
                            </div>
                          </div>
                          <div>
                            <div className="text-xs text-gray-500">Priority</div>
                            <Badge className={`${priority.color} text-white`}>
                              {priority.level}
                            </Badge>
                          </div>
                        </div>

                        <div className="mt-3 p-2 bg-orange-50 rounded text-xs text-orange-700">
                          <Wrench className="h-3 w-3 inline mr-1" />
                          Scheduled maintenance due based on mileage
                        </div>
                      </div>
                    </div>
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
