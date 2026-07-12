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
import { housekeepingService } from "@/services/facility/housekeepingService";
import type { HousekeepingTask, TaskFormData } from "@/services/facility/types";
import { useToast } from "@/components/ui/use-toast";

interface TaskFormProps {
  task?: HousekeepingTask | null;
  onClose: () => void;
  onSuccess: () => void;
}

export default function TaskForm({ task, onClose, onSuccess }: TaskFormProps) {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);

  const [formData, setFormData] = useState<TaskFormData & { assigned_to_employee_id?: number }>({
    task_type: "cleaning",
    task_name: "",
    building_id: 0,
    floor_id: undefined,
    room_id: undefined,
    scheduled_date: new Date().toISOString().split("T")[0],
    scheduled_time: "",
    priority: "medium",
    description: "",
    assigned_to_employee_id: undefined,
  });

  useEffect(() => {
    if (task) {
      setFormData({
        task_type: task.task_type,
        task_name: task.task_name,
        building_id: task.building_id,
        floor_id: task.floor_id,
        room_id: task.room_id,
        scheduled_date: task.scheduled_date.split("T")[0],
        scheduled_time: task.scheduled_time || "",
        priority: task.priority,
        description: task.description || "",
        assigned_to_employee_id: task.assigned_to_employee_id,
      });
    }
  }, [task]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.building_id) {
      toast({
        title: "Validation Error",
        description: "Please select a building",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);

    try {
      await housekeepingService.createTask(formData);
      toast({
        title: "Success",
        description: `Task ${task ? "updated" : "created"} successfully`,
      });
      onSuccess();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.message || "Failed to save task",
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
            {task ? "Edit Task" : "Create New Task"}
          </DialogTitle>
          <DialogDescription>
            {task
              ? "Update task information"
              : "Enter task details to create a new housekeeping task"}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            {/* Task Type & Name */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="task_type">Task Type *</Label>
                <Select
                  value={formData.task_type}
                  onValueChange={(value) =>
                    setFormData({ ...formData, task_type: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="cleaning">Cleaning</SelectItem>
                    <SelectItem value="maintenance">Maintenance</SelectItem>
                    <SelectItem value="inspection">Inspection</SelectItem>
                    <SelectItem value="sanitization">Sanitization</SelectItem>
                    <SelectItem value="waste_disposal">Waste Disposal</SelectItem>
                    <SelectItem value="pest_control">Pest Control</SelectItem>
                    <SelectItem value="deep_cleaning">Deep Cleaning</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="priority">Priority *</Label>
                <Select
                  value={formData.priority}
                  onValueChange={(value) =>
                    setFormData({ ...formData, priority: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                    <SelectItem value="urgent">Urgent</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="task_name">Task Name *</Label>
              <Input
                id="task_name"
                value={formData.task_name}
                onChange={(e) =>
                  setFormData({ ...formData, task_name: e.target.value })
                }
                required
                placeholder="e.g., Daily Office Cleaning"
              />
            </div>

            {/* Location Details */}
            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="building_id">Building ID *</Label>
                <Input
                  id="building_id"
                  type="number"
                  min="1"
                  value={formData.building_id || ""}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      building_id: parseInt(e.target.value) || 0,
                    })
                  }
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="floor_id">Floor ID</Label>
                <Input
                  id="floor_id"
                  type="number"
                  min="1"
                  value={formData.floor_id || ""}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      floor_id: e.target.value ? parseInt(e.target.value) : undefined,
                    })
                  }
                  placeholder="Optional"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="room_id">Room ID</Label>
                <Input
                  id="room_id"
                  type="number"
                  min="1"
                  value={formData.room_id || ""}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      room_id: e.target.value ? parseInt(e.target.value) : undefined,
                    })
                  }
                  placeholder="Optional"
                />
              </div>
            </div>

            {/* Schedule */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="scheduled_date">Scheduled Date *</Label>
                <Input
                  id="scheduled_date"
                  type="date"
                  value={formData.scheduled_date}
                  onChange={(e) =>
                    setFormData({ ...formData, scheduled_date: e.target.value })
                  }
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="scheduled_time">Scheduled Time</Label>
                <Input
                  id="scheduled_time"
                  type="time"
                  value={formData.scheduled_time}
                  onChange={(e) =>
                    setFormData({ ...formData, scheduled_time: e.target.value })
                  }
                />
              </div>
            </div>

            {/* Assigned To */}
            <div className="space-y-2">
              <Label htmlFor="assigned_to">Assign to Employee ID</Label>
              <Input
                id="assigned_to"
                type="number"
                min="1"
                value={formData.assigned_to_employee_id || ""}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    assigned_to_employee_id: e.target.value
                      ? parseInt(e.target.value)
                      : undefined,
                  })
                }
                placeholder="Leave empty to assign later"
              />
            </div>

            {/* Description */}
            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
                placeholder="Enter task details, special instructions, etc."
                rows={4}
              />
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? "Saving..." : task ? "Update" : "Create"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
