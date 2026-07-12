"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Plus, Car, Search, Edit, Trash2 } from "lucide-react";
import { transportService } from "@/services/facility/transportService";
import type { Vehicle } from "@/services/facility/types";
import { useToast } from "@/components/ui/use-toast";

export default function VehicleList() {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [filterType, setFilterType] = useState<string>("all");
  const { toast } = useToast();

  useEffect(() => {
    loadVehicles();
  }, []);

  const loadVehicles = async () => {
    try {
      setLoading(true);
      const params: any = { limit: 100 };
      if (filterStatus !== "all") params.status = filterStatus;
      if (filterType !== "all") params.vehicle_type = filterType;

      const response = await transportService.getVehicles(params);
      setVehicles(response.items);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load vehicles",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadVehicles();
  }, [filterStatus, filterType]);

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      available: "bg-green-500",
      in_use: "bg-blue-500",
      maintenance: "bg-orange-500",
      out_of_service: "bg-red-500",
    };
    return colors[status] || "bg-gray-500";
  };

  const getVehicleTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      car: "Car",
      suv: "SUV",
      van: "Van",
      bus: "Bus",
      truck: "Truck",
      two_wheeler: "Two Wheeler",
    };
    return labels[type] || type;
  };

  const filteredVehicles = vehicles.filter(
    (vehicle) =>
      vehicle.vehicle_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (vehicle.make_model &&
        vehicle.make_model.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const availableCount = vehicles.filter((v) => v.status === "available").length;
  const inUseCount = vehicles.filter((v) => v.status === "in_use").length;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Car className="h-5 w-5" />
              Vehicle Fleet Management
            </CardTitle>
            <CardDescription>Manage company vehicles and fleet</CardDescription>
          </div>
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Add Vehicle
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {/* Statistics */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          <Card>
            <CardContent className="pt-6">
              <div className="text-2xl font-bold">{vehicles.length}</div>
              <div className="text-sm text-gray-500">Total Vehicles</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="text-2xl font-bold text-green-600">{availableCount}</div>
              <div className="text-sm text-gray-500">Available</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="text-2xl font-bold text-blue-600">{inUseCount}</div>
              <div className="text-sm text-gray-500">In Use</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="text-2xl font-bold text-orange-600">
                {vehicles.filter((v) => v.status === "maintenance").length}
              </div>
              <div className="text-sm text-gray-500">Maintenance</div>
            </CardContent>
          </Card>
        </div>

        {/* Filters */}
        <div className="flex gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search vehicles..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          <Select value={filterType} onValueChange={setFilterType}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="Vehicle Type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Types</SelectItem>
              <SelectItem value="car">Car</SelectItem>
              <SelectItem value="suv">SUV</SelectItem>
              <SelectItem value="van">Van</SelectItem>
              <SelectItem value="bus">Bus</SelectItem>
              <SelectItem value="truck">Truck</SelectItem>
              <SelectItem value="two_wheeler">Two Wheeler</SelectItem>
            </SelectContent>
          </Select>
          <Select value={filterStatus} onValueChange={setFilterStatus}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="available">Available</SelectItem>
              <SelectItem value="in_use">In Use</SelectItem>
              <SelectItem value="maintenance">Maintenance</SelectItem>
              <SelectItem value="out_of_service">Out of Service</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Vehicles Table */}
        {loading ? (
          <div className="text-center py-8">Loading...</div>
        ) : filteredVehicles.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No vehicles found. Add your first vehicle to get started.
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Vehicle Number</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Make/Model</TableHead>
                <TableHead>Capacity</TableHead>
                <TableHead>Mileage (km)</TableHead>
                <TableHead>Fuel Type</TableHead>
                <TableHead>Ownership</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredVehicles.map((vehicle) => (
                <TableRow key={vehicle.id}>
                  <TableCell className="font-medium">
                    {vehicle.vehicle_number}
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">
                      {getVehicleTypeLabel(vehicle.vehicle_type)}
                    </Badge>
                  </TableCell>
                  <TableCell>{vehicle.make_model || "-"}</TableCell>
                  <TableCell>
                    {vehicle.seating_capacity
                      ? `${vehicle.seating_capacity} seats`
                      : "-"}
                  </TableCell>
                  <TableCell>
                    {vehicle.current_mileage_km.toLocaleString()} km
                  </TableCell>
                  <TableCell>{vehicle.fuel_type || "-"}</TableCell>
                  <TableCell>
                    <Badge variant="secondary">{vehicle.ownership}</Badge>
                  </TableCell>
                  <TableCell>
                    <Badge
                      className={`${getStatusColor(vehicle.status)} text-white`}
                    >
                      {vehicle.status.replace("_", " ").toUpperCase()}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-2">
                      <Button variant="ghost" size="sm">
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="sm">
                        <Trash2 className="h-4 w-4 text-red-500" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
