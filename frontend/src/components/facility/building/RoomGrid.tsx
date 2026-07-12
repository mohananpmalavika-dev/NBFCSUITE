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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Plus, DoorOpen, Edit } from "lucide-react";
import { buildingService } from "@/services/facility/buildingService";
import type { Floor, Room, RoomFormData } from "@/services/facility/types";
import { useToast } from "@/components/ui/use-toast";

interface RoomGridProps {
  buildingId: number;
  floors: Floor[];
  rooms: Room[];
  onUpdate: () => void;
}

export default function RoomGrid({ buildingId, floors, rooms, onUpdate }: RoomGridProps) {
  const [showForm, setShowForm] = useState(false);
  const [editingRoom, setEditingRoom] = useState<Room | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedFloor, setSelectedFloor] = useState<number | null>(
    floors.length > 0 ? floors[0].id : null
  );
  const { toast } = useToast();

  const [formData, setFormData] = useState<RoomFormData & { floor_id: number }>({
    room_number: "",
    room_name: "",
    room_type: "office",
    status: "available",
    area_sqft: 0,
    seating_capacity: 0,
    floor_id: floors.length > 0 ? floors[0].id : 0,
  });

  const handleAdd = () => {
    if (!selectedFloor) {
      toast({
        title: "Error",
        description: "Please select a floor first",
        variant: "destructive",
      });
      return;
    }

    setEditingRoom(null);
    setFormData({
      room_number: "",
      room_name: "",
      room_type: "office",
      status: "available",
      area_sqft: 0,
      seating_capacity: 0,
      floor_id: selectedFloor,
    });
    setShowForm(true);
  };

  const handleEdit = (room: Room) => {
    setEditingRoom(room);
    setFormData({
      room_number: room.room_number,
      room_name: room.room_name || "",
      room_type: room.room_type,
      status: room.status,
      area_sqft: room.area_sqft || 0,
      seating_capacity: room.seating_capacity || 0,
      floor_id: room.floor_id,
    });
    setShowForm(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await buildingService.createRoom(buildingId, formData.floor_id, formData);
      toast({
        title: "Success",
        description: `Room ${editingRoom ? "updated" : "created"} successfully`,
      });
      setShowForm(false);
      onUpdate();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.message || "Failed to save room",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (roomId: number, newStatus: string) => {
    try {
      await buildingService.updateRoomStatus(roomId, newStatus);
      toast({
        title: "Success",
        description: "Room status updated successfully",
      });
      onUpdate();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.message || "Failed to update room status",
        variant: "destructive",
      });
    }
  };

  const getRoomTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      office: "Office",
      conference_room: "Conference Room",
      cabin: "Cabin",
      cubicle: "Cubicle",
      meeting_room: "Meeting Room",
      cafeteria: "Cafeteria",
      restroom: "Restroom",
      storage: "Storage",
      server_room: "Server Room",
      reception: "Reception",
      lobby: "Lobby",
      pantry: "Pantry",
      other: "Other",
    };
    return labels[type] || type;
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      available: "bg-green-500",
      occupied: "bg-blue-500",
      under_maintenance: "bg-orange-500",
      reserved: "bg-purple-500",
      out_of_service: "bg-red-500",
    };
    return colors[status] || "bg-gray-500";
  };

  const filteredRooms = selectedFloor
    ? rooms.filter((r) => r.floor_id === selectedFloor)
    : rooms;

  return (
    <>
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-base flex items-center gap-2">
                <DoorOpen className="h-4 w-4" />
                Room Management
              </CardTitle>
              <CardDescription>
                Manage rooms across all floors
              </CardDescription>
            </div>
            <Button size="sm" onClick={handleAdd} disabled={floors.length === 0}>
              <Plus className="h-4 w-4 mr-2" />
              Add Room
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {floors.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No floors available. Please add floors first.
            </div>
          ) : (
            <>
              {/* Floor Selector */}
              <div className="mb-4">
                <Label>Select Floor</Label>
                <Select
                  value={selectedFloor?.toString()}
                  onValueChange={(value) => setSelectedFloor(parseInt(value))}
                >
                  <SelectTrigger className="w-64">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {floors.map((floor) => (
                      <SelectItem key={floor.id} value={floor.id.toString()}>
                        {floor.floor_name || `Floor ${floor.floor_number}`} ({" "}
                        {rooms.filter((r) => r.floor_id === floor.id).length} rooms)
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Rooms Grid */}
              {filteredRooms.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  No rooms on this floor. Add your first room to get started.
                </div>
              ) : (
                <div className="grid grid-cols-3 gap-4">
                  {filteredRooms.map((room) => (
                    <Card key={room.id} className="hover:shadow-md transition-shadow">
                      <CardHeader className="pb-3">
                        <div className="flex items-start justify-between">
                          <div>
                            <CardTitle className="text-sm font-medium">
                              {room.room_number}
                            </CardTitle>
                            <CardDescription className="text-xs mt-1">
                              {room.room_name || getRoomTypeLabel(room.room_type)}
                            </CardDescription>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleEdit(room)}
                            className="h-7 w-7 p-0"
                          >
                            <Edit className="h-3 w-3" />
                          </Button>
                        </div>
                      </CardHeader>
                      <CardContent className="space-y-2">
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-gray-500">Type:</span>
                          <Badge variant="outline" className="text-xs">
                            {getRoomTypeLabel(room.room_type)}
                          </Badge>
                        </div>
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-gray-500">Status:</span>
                          <Select
                            value={room.status}
                            onValueChange={(value) =>
                              handleStatusChange(room.id, value)
                            }
                          >
                            <SelectTrigger className="h-7 text-xs">
                              <Badge
                                className={`${getStatusColor(room.status)} text-white text-xs`}
                              >
                                {room.status.replace("_", " ").toUpperCase()}
                              </Badge>
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="available">Available</SelectItem>
                              <SelectItem value="occupied">Occupied</SelectItem>
                              <SelectItem value="under_maintenance">
                                Under Maintenance
                              </SelectItem>
                              <SelectItem value="reserved">Reserved</SelectItem>
                              <SelectItem value="out_of_service">
                                Out of Service
                              </SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        {room.area_sqft && (
                          <div className="flex items-center justify-between text-xs">
                            <span className="text-gray-500">Area:</span>
                            <span>{room.area_sqft} sqft</span>
                          </div>
                        )}
                        {room.seating_capacity && (
                          <div className="flex items-center justify-between text-xs">
                            <span className="text-gray-500">Capacity:</span>
                            <span>{room.seating_capacity} seats</span>
                          </div>
                        )}
                        <div className="flex gap-1 pt-1">
                          {room.has_ac && (
                            <Badge variant="secondary" className="text-xs">
                              AC
                            </Badge>
                          )}
                          {room.has_projector && (
                            <Badge variant="secondary" className="text-xs">
                              Projector
                            </Badge>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>

      {/* Room Form Dialog */}
      {showForm && (
        <Dialog open={true} onOpenChange={() => setShowForm(false)}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>
                {editingRoom ? "Edit Room" : "Add New Room"}
              </DialogTitle>
              <DialogDescription>
                Enter room details
              </DialogDescription>
            </DialogHeader>

            <form onSubmit={handleSubmit}>
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="floor_id">Floor *</Label>
                    <Select
                      value={formData.floor_id.toString()}
                      onValueChange={(value) =>
                        setFormData({ ...formData, floor_id: parseInt(value) })
                      }
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {floors.map((floor) => (
                          <SelectItem key={floor.id} value={floor.id.toString()}>
                            {floor.floor_name || `Floor ${floor.floor_number}`}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="room_number">Room Number *</Label>
                    <Input
                      id="room_number"
                      value={formData.room_number}
                      onChange={(e) =>
                        setFormData({ ...formData, room_number: e.target.value })
                      }
                      required
                      placeholder="e.g., R101"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="room_name">Room Name</Label>
                  <Input
                    id="room_name"
                    value={formData.room_name}
                    onChange={(e) =>
                      setFormData({ ...formData, room_name: e.target.value })
                    }
                    placeholder="e.g., Executive Meeting Room"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="room_type">Room Type *</Label>
                    <Select
                      value={formData.room_type}
                      onValueChange={(value) =>
                        setFormData({ ...formData, room_type: value })
                      }
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="office">Office</SelectItem>
                        <SelectItem value="conference_room">Conference Room</SelectItem>
                        <SelectItem value="cabin">Cabin</SelectItem>
                        <SelectItem value="cubicle">Cubicle</SelectItem>
                        <SelectItem value="meeting_room">Meeting Room</SelectItem>
                        <SelectItem value="cafeteria">Cafeteria</SelectItem>
                        <SelectItem value="restroom">Restroom</SelectItem>
                        <SelectItem value="storage">Storage</SelectItem>
                        <SelectItem value="server_room">Server Room</SelectItem>
                        <SelectItem value="reception">Reception</SelectItem>
                        <SelectItem value="lobby">Lobby</SelectItem>
                        <SelectItem value="pantry">Pantry</SelectItem>
                        <SelectItem value="other">Other</SelectItem>
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
                        <SelectItem value="available">Available</SelectItem>
                        <SelectItem value="occupied">Occupied</SelectItem>
                        <SelectItem value="under_maintenance">
                          Under Maintenance
                        </SelectItem>
                        <SelectItem value="reserved">Reserved</SelectItem>
                        <SelectItem value="out_of_service">Out of Service</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="area_sqft">Area (sqft)</Label>
                    <Input
                      id="area_sqft"
                      type="number"
                      min="0"
                      value={formData.area_sqft}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          area_sqft: parseFloat(e.target.value) || 0,
                        })
                      }
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="seating_capacity">Seating Capacity</Label>
                    <Input
                      id="seating_capacity"
                      type="number"
                      min="0"
                      value={formData.seating_capacity}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          seating_capacity: parseInt(e.target.value) || 0,
                        })
                      }
                    />
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
                  {loading ? "Saving..." : editingRoom ? "Update" : "Create"}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      )}
    </>
  );
}
