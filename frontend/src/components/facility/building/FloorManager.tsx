"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
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
import { Checkbox } from "@/components/ui/checkbox";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Plus, Layers, Edit, Trash2 } from "lucide-react";
import { buildingService } from "@/services/facility/buildingService";
import type { Floor, FloorFormData } from "@/services/facility/types";
import { useToast } from "@/components/ui/use-toast";

interface FloorManagerProps {
  buildingId: number;
  floors: Floor[];
  onUpdate: () => void;
}

export default function FloorManager({ buildingId, floors, onUpdate }: FloorManagerProps) {
  const [showForm, setShowForm] = useState(false);
  const [editingFloor, setEditingFloor] = useState<Floor | null>(null);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const [formData, setFormData] = useState<FloorFormData>({
    floor_number: 1,
    floor_name: "",
    floor_area_sqft: 0,
    has_restroom: false,
    has_pantry: false,
  });

  const handleAdd = () => {
    setEditingFloor(null);
    setFormData({
      floor_number: floors.length + 1,
      floor_name: "",
      floor_area_sqft: 0,
      has_restroom: false,
      has_pantry: false,
    });
    setShowForm(true);
  };

  const handleEdit = (floor: Floor) => {
    setEditingFloor(floor);
    setFormData({
      floor_number: floor.floor_number,
      floor_name: floor.floor_name || "",
      floor_area_sqft: floor.floor_area_sqft || 0,
      has_restroom: floor.has_restroom,
      has_pantry: floor.has_pantry,
    });
    setShowForm(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await buildingService.createFloor(buildingId, formData);
      toast({
        title: "Success",
        description: `Floor ${editingFloor ? "updated" : "created"} successfully`,
      });
      setShowForm(false);
      onUpdate();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.message || "Failed to save floor",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-base flex items-center gap-2">
                <Layers className="h-4 w-4" />
                Floor Management
              </CardTitle>
              <CardDescription>
                Manage floors in this building
              </CardDescription>
            </div>
            <Button size="sm" onClick={handleAdd}>
              <Plus className="h-4 w-4 mr-2" />
              Add Floor
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {floors.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No floors added yet. Add your first floor to get started.
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Floor Number</TableHead>
                  <TableHead>Floor Name</TableHead>
                  <TableHead>Area (sqft)</TableHead>
                  <TableHead>Total Rooms</TableHead>
                  <TableHead>Facilities</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {floors.map((floor) => (
                  <TableRow key={floor.id}>
                    <TableCell className="font-medium">
                      {floor.floor_number}
                    </TableCell>
                    <TableCell>
                      {floor.floor_name || `Floor ${floor.floor_number}`}
                    </TableCell>
                    <TableCell>
                      {floor.floor_area_sqft
                        ? floor.floor_area_sqft.toLocaleString()
                        : "-"}
                    </TableCell>
                    <TableCell>{floor.total_rooms}</TableCell>
                    <TableCell>
                      <div className="flex gap-1">
                        {floor.has_restroom && (
                          <Badge variant="secondary" className="text-xs">
                            Restroom
                          </Badge>
                        )}
                        {floor.has_pantry && (
                          <Badge variant="secondary" className="text-xs">
                            Pantry
                          </Badge>
                        )}
                        {!floor.has_restroom && !floor.has_pantry && "-"}
                      </div>
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleEdit(floor)}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Floor Form Dialog */}
      {showForm && (
        <Dialog open={true} onOpenChange={() => setShowForm(false)}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>
                {editingFloor ? "Edit Floor" : "Add New Floor"}
              </DialogTitle>
              <DialogDescription>
                Enter floor details
              </DialogDescription>
            </DialogHeader>

            <form onSubmit={handleSubmit}>
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="floor_number">Floor Number *</Label>
                    <Input
                      id="floor_number"
                      type="number"
                      min="1"
                      value={formData.floor_number}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          floor_number: parseInt(e.target.value) || 1,
                        })
                      }
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="floor_name">Floor Name</Label>
                    <Input
                      id="floor_name"
                      value={formData.floor_name}
                      onChange={(e) =>
                        setFormData({ ...formData, floor_name: e.target.value })
                      }
                      placeholder="e.g., Ground Floor"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="floor_area_sqft">Floor Area (sqft)</Label>
                  <Input
                    id="floor_area_sqft"
                    type="number"
                    min="0"
                    value={formData.floor_area_sqft}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        floor_area_sqft: parseFloat(e.target.value) || 0,
                      })
                    }
                  />
                </div>

                <div className="space-y-3">
                  <Label>Facilities</Label>
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="has_restroom"
                      checked={formData.has_restroom}
                      onCheckedChange={(checked) =>
                        setFormData({
                          ...formData,
                          has_restroom: checked as boolean,
                        })
                      }
                    />
                    <Label htmlFor="has_restroom" className="cursor-pointer">
                      Has Restroom
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="has_pantry"
                      checked={formData.has_pantry}
                      onCheckedChange={(checked) =>
                        setFormData({
                          ...formData,
                          has_pantry: checked as boolean,
                        })
                      }
                    />
                    <Label htmlFor="has_pantry" className="cursor-pointer">
                      Has Pantry
                    </Label>
                  </div>
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
                  {loading ? "Saving..." : editingFloor ? "Update" : "Create"}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      )}
    </>
  );
}
