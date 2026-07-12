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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { buildingService } from "@/services/facility/buildingService";
import type { Building, BuildingFormData } from "@/services/facility/types";
import { useToast } from "@/components/ui/use-toast";

interface BuildingFormProps {
  building?: Building | null;
  onClose: () => void;
  onSuccess: () => void;
}

export default function BuildingForm({ building, onClose, onSuccess }: BuildingFormProps) {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);

  const [formData, setFormData] = useState<BuildingFormData & {
    total_floors?: number;
    built_year?: number;
    has_elevator?: boolean;
    has_parking?: boolean;
    parking_capacity?: number;
  }>({
    building_code: "",
    building_name: "",
    building_type: "office",
    status: "active",
    address_line1: "",
    address_line2: "",
    city: "",
    state: "",
    pincode: "",
    total_floors: 1,
    total_area_sqft: 0,
    built_year: new Date().getFullYear(),
    has_elevator: false,
    has_parking: false,
    parking_capacity: 0,
    contact_number: "",
  });

  useEffect(() => {
    if (building) {
      setFormData({
        building_code: building.building_code,
        building_name: building.building_name,
        building_type: building.building_type,
        status: building.status,
        address_line1: building.address_line1 || "",
        address_line2: building.address_line2 || "",
        city: building.city || "",
        state: building.state || "",
        pincode: building.pincode || "",
        total_floors: building.total_floors,
        total_area_sqft: building.total_area_sqft || 0,
        built_year: building.built_year || new Date().getFullYear(),
        has_elevator: building.has_elevator,
        has_parking: building.has_parking,
        parking_capacity: building.parking_capacity,
        contact_number: building.contact_number || "",
      });
    }
  }, [building]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (building) {
        await buildingService.updateBuilding(building.id, formData);
        toast({
          title: "Success",
          description: "Building updated successfully",
        });
      } else {
        await buildingService.createBuilding(formData);
        toast({
          title: "Success",
          description: "Building created successfully",
        });
      }
      onSuccess();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.message || "Failed to save building",
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
            {building ? "Edit Building" : "Add New Building"}
          </DialogTitle>
          <DialogDescription>
            {building
              ? "Update building information"
              : "Enter building details to add a new building"}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            {/* Basic Information */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="building_code">Building Code *</Label>
                <Input
                  id="building_code"
                  value={formData.building_code}
                  onChange={(e) =>
                    setFormData({ ...formData, building_code: e.target.value })
                  }
                  required
                  disabled={!!building}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="building_name">Building Name *</Label>
                <Input
                  id="building_name"
                  value={formData.building_name}
                  onChange={(e) =>
                    setFormData({ ...formData, building_name: e.target.value })
                  }
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="building_type">Building Type *</Label>
                <Select
                  value={formData.building_type}
                  onValueChange={(value) =>
                    setFormData({ ...formData, building_type: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="office">Office</SelectItem>
                    <SelectItem value="warehouse">Warehouse</SelectItem>
                    <SelectItem value="factory">Factory</SelectItem>
                    <SelectItem value="retail">Retail</SelectItem>
                    <SelectItem value="residential">Residential</SelectItem>
                    <SelectItem value="mixed_use">Mixed Use</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="status">Status</Label>
                <Select
                  value={formData.status}
                  onValueChange={(value) =>
                    setFormData({ ...formData, status: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="active">Active</SelectItem>
                    <SelectItem value="under_construction">Under Construction</SelectItem>
                    <SelectItem value="maintenance">Maintenance</SelectItem>
                    <SelectItem value="inactive">Inactive</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Address Information */}
            <div className="space-y-2">
              <Label htmlFor="address_line1">Address Line 1</Label>
              <Input
                id="address_line1"
                value={formData.address_line1}
                onChange={(e) =>
                  setFormData({ ...formData, address_line1: e.target.value })
                }
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="address_line2">Address Line 2</Label>
              <Input
                id="address_line2"
                value={formData.address_line2}
                onChange={(e) =>
                  setFormData({ ...formData, address_line2: e.target.value })
                }
              />
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="city">City</Label>
                <Input
                  id="city"
                  value={formData.city}
                  onChange={(e) =>
                    setFormData({ ...formData, city: e.target.value })
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="state">State</Label>
                <Input
                  id="state"
                  value={formData.state}
                  onChange={(e) =>
                    setFormData({ ...formData, state: e.target.value })
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="pincode">Pincode</Label>
                <Input
                  id="pincode"
                  value={formData.pincode}
                  onChange={(e) =>
                    setFormData({ ...formData, pincode: e.target.value })
                  }
                />
              </div>
            </div>

            {/* Building Specifications */}
            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="total_floors">Total Floors</Label>
                <Input
                  id="total_floors"
                  type="number"
                  min="1"
                  value={formData.total_floors}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      total_floors: parseInt(e.target.value) || 1,
                    })
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="total_area_sqft">Total Area (sqft)</Label>
                <Input
                  id="total_area_sqft"
                  type="number"
                  min="0"
                  value={formData.total_area_sqft}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      total_area_sqft: parseFloat(e.target.value) || 0,
                    })
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="built_year">Built Year</Label>
                <Input
                  id="built_year"
                  type="number"
                  min="1900"
                  max={new Date().getFullYear()}
                  value={formData.built_year}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      built_year: parseInt(e.target.value) || new Date().getFullYear(),
                    })
                  }
                />
              </div>
            </div>

            {/* Facilities */}
            <div className="grid grid-cols-3 gap-4">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="has_elevator"
                  checked={formData.has_elevator}
                  onCheckedChange={(checked) =>
                    setFormData({ ...formData, has_elevator: checked as boolean })
                  }
                />
                <Label htmlFor="has_elevator" className="cursor-pointer">
                  Has Elevator
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="has_parking"
                  checked={formData.has_parking}
                  onCheckedChange={(checked) =>
                    setFormData({ ...formData, has_parking: checked as boolean })
                  }
                />
                <Label htmlFor="has_parking" className="cursor-pointer">
                  Has Parking
                </Label>
              </div>
              {formData.has_parking && (
                <div className="space-y-2">
                  <Label htmlFor="parking_capacity">Parking Capacity</Label>
                  <Input
                    id="parking_capacity"
                    type="number"
                    min="0"
                    value={formData.parking_capacity}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        parking_capacity: parseInt(e.target.value) || 0,
                      })
                    }
                  />
                </div>
              )}
            </div>

            {/* Contact */}
            <div className="space-y-2">
              <Label htmlFor="contact_number">Contact Number</Label>
              <Input
                id="contact_number"
                value={formData.contact_number}
                onChange={(e) =>
                  setFormData({ ...formData, contact_number: e.target.value })
                }
              />
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? "Saving..." : building ? "Update" : "Create"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
