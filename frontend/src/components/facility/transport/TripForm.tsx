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
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { transportService } from "@/services/facility/transportService";
import type { Trip, TripFormData, Vehicle } from "@/services/facility/types";
import { useToast } from "@/components/ui/use-toast";

interface TripFormProps {
  trip?: Trip | null;
  onClose: () => void;
  onSuccess: () => void;
}

export default function TripForm({ trip, onClose, onSuccess }: TripFormProps) {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [availableVehicles, setAvailableVehicles] = useState<Vehicle[]>([]);

  const [formData, setFormData] = useState<TripFormData>({
    vehicle_id: 0,
    driver_id: 0,
    trip_date: new Date().toISOString().split("T")[0],
    start_location: "",
    end_location: "",
    purpose: "",
    passenger_count: 1,
  });

  useEffect(() => {
    if (trip) {
      setFormData({
        vehicle_id: trip.vehicle_id,
        driver_id: trip.driver_id,
        trip_date: trip.trip_date.split("T")[0],
        start_location: trip.start_location,
        end_location: trip.end_location,
        purpose: trip.purpose || "",
        passenger_count: trip.passenger_count,
      });
    }
  }, [trip]);

  useEffect(() => {
    if (formData.trip_date) {
      loadAvailableVehicles(formData.trip_date);
    }
  }, [formData.trip_date]);

  const loadAvailableVehicles = async (date: string) => {
    try {
      const vehicles = await transportService.getAvailableVehicles(date);
      setAvailableVehicles(vehicles);
    } catch (error) {
      // Fallback to all vehicles if available vehicles endpoint fails
      const response = await transportService.getVehicles({ status: "available" });
      setAvailableVehicles(response.items);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.vehicle_id || !formData.driver_id) {
      toast({
        title: "Validation Error",
        description: "Please select vehicle and driver",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);

    try {
      await transportService.createTrip(formData);
      toast({
        title: "Success",
        description: `Trip ${trip ? "updated" : "created"} successfully`,
      });
      onSuccess();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.message || "Failed to save trip",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {trip ? "Edit Trip" : "Schedule New Trip"}
          </DialogTitle>
          <DialogDescription>
            {trip
              ? "Update trip information"
              : "Enter trip details to schedule a new trip"}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            {/* Trip Date */}
            <div className="space-y-2">
              <Label htmlFor="trip_date">Trip Date *</Label>
              <Input
                id="trip_date"
                type="date"
                value={formData.trip_date}
                onChange={(e) =>
                  setFormData({ ...formData, trip_date: e.target.value })
                }
                required
                min={new Date().toISOString().split("T")[0]}
              />
            </div>

            {/* Vehicle & Driver Selection */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="vehicle_id">Vehicle *</Label>
                <Select
                  value={formData.vehicle_id.toString()}
                  onValueChange={(value) =>
                    setFormData({ ...formData, vehicle_id: parseInt(value) })
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select vehicle" />
                  </SelectTrigger>
                  <SelectContent>
                    {availableVehicles.length === 0 ? (
                      <SelectItem value="0" disabled>
                        No vehicles available
                      </SelectItem>
                    ) : (
                      availableVehicles.map((vehicle) => (
                        <SelectItem key={vehicle.id} value={vehicle.id.toString()}>
                          {vehicle.vehicle_number} - {vehicle.vehicle_type}
                        </SelectItem>
                      ))
                    )}
                  </SelectContent>
                </Select>
                <div className="text-xs text-gray-500">
                  {availableVehicles.length} vehicle(s) available
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="driver_id">Driver ID *</Label>
                <Input
                  id="driver_id"
                  type="number"
                  min="1"
                  value={formData.driver_id || ""}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      driver_id: parseInt(e.target.value) || 0,
                    })
                  }
                  required
                  placeholder="Enter driver employee ID"
                />
              </div>
            </div>

            {/* Locations */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="start_location">Start Location *</Label>
                <Input
                  id="start_location"
                  value={formData.start_location}
                  onChange={(e) =>
                    setFormData({ ...formData, start_location: e.target.value })
                  }
                  required
                  placeholder="e.g., Office HQ"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="end_location">End Location *</Label>
                <Input
                  id="end_location"
                  value={formData.end_location}
                  onChange={(e) =>
                    setFormData({ ...formData, end_location: e.target.value })
                  }
                  required
                  placeholder="e.g., Client Site"
                />
              </div>
            </div>

            {/* Passenger Count */}
            <div className="space-y-2">
              <Label htmlFor="passenger_count">Passenger Count</Label>
              <Input
                id="passenger_count"
                type="number"
                min="1"
                value={formData.passenger_count}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    passenger_count: parseInt(e.target.value) || 1,
                  })
                }
              />
            </div>

            {/* Purpose */}
            <div className="space-y-2">
              <Label htmlFor="purpose">Purpose</Label>
              <Textarea
                id="purpose"
                value={formData.purpose}
                onChange={(e) =>
                  setFormData({ ...formData, purpose: e.target.value })
                }
                placeholder="Enter trip purpose or description"
                rows={3}
              />
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? "Saving..." : trip ? "Update" : "Schedule Trip"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
