"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Building2, MapPin, Calendar, Edit, Layers, DoorOpen } from "lucide-react";
import { buildingService } from "@/services/facility/buildingService";
import type { Building, Floor, Room } from "@/services/facility/types";
import { useToast } from "@/components/ui/use-toast";
import FloorManager from "./FloorManager";
import RoomGrid from "./RoomGrid";

interface BuildingDetailsProps {
  building: Building;
  onClose: () => void;
  onEdit: () => void;
}

export default function BuildingDetails({ building, onClose, onEdit }: BuildingDetailsProps) {
  const [floors, setFloors] = useState<Floor[]>([]);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    loadBuildingData();
  }, [building.id]);

  const loadBuildingData = async () => {
    try {
      setLoading(true);
      const [floorsData, roomsData] = await Promise.all([
        buildingService.getFloors(building.id),
        buildingService.getRooms({ building_id: building.id, limit: 500 }),
      ]);
      setFloors(floorsData);
      setRooms(roomsData.items);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load building details",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      active: "bg-green-500",
      under_construction: "bg-yellow-500",
      maintenance: "bg-orange-500",
      inactive: "bg-gray-500",
    };
    return colors[status] || "bg-gray-500";
  };

  const getBuildingTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      office: "Office",
      warehouse: "Warehouse",
      factory: "Factory",
      retail: "Retail",
      residential: "Residential",
      mixed_use: "Mixed Use",
    };
    return labels[type] || type;
  };

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="max-w-5xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <div>
              <DialogTitle className="flex items-center gap-2">
                <Building2 className="h-5 w-5" />
                {building.building_name}
              </DialogTitle>
              <DialogDescription>
                Building Code: {building.building_code}
              </DialogDescription>
            </div>
            <Button onClick={onEdit}>
              <Edit className="h-4 w-4 mr-2" />
              Edit
            </Button>
          </div>
        </DialogHeader>

        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="floors">Floors ({floors.length})</TabsTrigger>
            <TabsTrigger value="rooms">Rooms ({rooms.length})</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              {/* Basic Information */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Basic Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div>
                    <div className="text-sm text-gray-500">Building Type</div>
                    <Badge variant="outline" className="mt-1">
                      {getBuildingTypeLabel(building.building_type)}
                    </Badge>
                  </div>
                  <div>
                    <div className="text-sm text-gray-500">Status</div>
                    <Badge className={`${getStatusColor(building.status)} text-white mt-1`}>
                      {building.status.replace("_", " ").toUpperCase()}
                    </Badge>
                  </div>
                  <div>
                    <div className="text-sm text-gray-500">Total Floors</div>
                    <div className="font-medium flex items-center gap-2 mt-1">
                      <Layers className="h-4 w-4" />
                      {building.total_floors}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-500">Total Rooms</div>
                    <div className="font-medium flex items-center gap-2 mt-1">
                      <DoorOpen className="h-4 w-4" />
                      {rooms.length}
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Specifications */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Specifications</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div>
                    <div className="text-sm text-gray-500">Total Area</div>
                    <div className="font-medium mt-1">
                      {building.total_area_sqft
                        ? `${building.total_area_sqft.toLocaleString()} sqft`
                        : "Not specified"}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-500">Built Year</div>
                    <div className="font-medium flex items-center gap-2 mt-1">
                      <Calendar className="h-4 w-4" />
                      {building.built_year || "Not specified"}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-500">Facilities</div>
                    <div className="flex gap-2 mt-1">
                      {building.has_elevator && (
                        <Badge variant="secondary">Elevator</Badge>
                      )}
                      {building.has_parking && (
                        <Badge variant="secondary">
                          Parking ({building.parking_capacity})
                        </Badge>
                      )}
                      {!building.has_elevator && !building.has_parking && (
                        <span className="text-sm text-gray-500">None</span>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Location Information */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2">
                  <MapPin className="h-4 w-4" />
                  Location
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {building.address_line1 && (
                  <div className="text-sm">{building.address_line1}</div>
                )}
                {building.address_line2 && (
                  <div className="text-sm">{building.address_line2}</div>
                )}
                <div className="text-sm">
                  {[building.city, building.state, building.pincode]
                    .filter(Boolean)
                    .join(", ")}
                </div>
                {building.contact_number && (
                  <div className="text-sm mt-2">
                    <span className="text-gray-500">Contact:</span>{" "}
                    {building.contact_number}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Statistics */}
            <div className="grid grid-cols-4 gap-4">
              <Card>
                <CardContent className="pt-6">
                  <div className="text-2xl font-bold">{floors.length}</div>
                  <div className="text-sm text-gray-500">Total Floors</div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="text-2xl font-bold">{rooms.length}</div>
                  <div className="text-sm text-gray-500">Total Rooms</div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="text-2xl font-bold">
                    {rooms.filter((r) => r.status === "available").length}
                  </div>
                  <div className="text-sm text-gray-500">Available Rooms</div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="text-2xl font-bold">
                    {rooms.filter((r) => r.status === "occupied").length}
                  </div>
                  <div className="text-sm text-gray-500">Occupied Rooms</div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Floors Tab */}
          <TabsContent value="floors">
            <FloorManager
              buildingId={building.id}
              floors={floors}
              onUpdate={loadBuildingData}
            />
          </TabsContent>

          {/* Rooms Tab */}
          <TabsContent value="rooms">
            <RoomGrid
              buildingId={building.id}
              floors={floors}
              rooms={rooms}
              onUpdate={loadBuildingData}
            />
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
