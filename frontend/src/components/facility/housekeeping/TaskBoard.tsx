"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Plus, Clock, CheckCircle2, AlertCircle, XCircle, User } from "lucide-react";
import { housekeepingService } from "@/services/facility/housekeepingService";
import type { HousekeepingTask } from "@/services/facility/types";
import { useToast } from "@/components/ui/use-toast";
import TaskForm from "./TaskForm";

export default function TaskBoard() {
  const [tasks, setTasks] = useState<HousekeepingTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      setLoading(true);
      const response = await housekeepingService.getTasks({ limit: 100 });
      setTasks(response.items);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load tasks",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (taskId: number, newStatus: string) => {
    try {
      await housekeepingService.updateTaskStatus(taskId, newStatus);
      toast({
        title: "Success",
        description: "Task status updated successfully",
      });
      loadTasks();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.message || "Failed to update task status",
        variant: "destructive",
      });
    }
  };

  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      urgent: "bg-red-500",
      high: "bg-orange-500",
      medium: "bg-yellow-500",
      low: "bg-blue-500",
    };
    return colors[priority] || "bg-gray-500";
  };

  const getStatusIcon = (status: string) => {
    const icons: Record<string, any> = {
      pending: Clock,
      in_progress: AlertCircle,
      completed: CheckCircle2,
      cancelled: XCircle,
      on_hold: Clock,
    };
    return icons[status] || Clock;
  };

  const columns = [
    { id: "pending", label: "Pending", status: "pending", color: "bg-gray-100" },
    { id: "in_progress", label: "In Progress", status: "in_progress", color: "bg-blue-100" },
    { id: "completed", label: "Completed", status: "completed", color: "bg-green-100" },
    { id: "on_hold", label: "On Hold", status: "on_hold", color: "bg-yellow-100" },
  ];

  return (
    <>
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">Housekeeping Task Board</h2>
            <p className="text-gray-500">Kanban-style task management</p>
          </div>
          <Button onClick={() => setShowForm(true)}>
            <Plus className="h-4 w-4 mr-2" />
            New Task
          </Button>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12">Loading tasks...</div>
      ) : (
        <div className="grid grid-cols-4 gap-4">
          {columns.map((column) => {
            const columnTasks = tasks.filter((task) => task.status === column.status);

            return (
              <div key={column.id} className="space-y-3">
                <Card className={column.color}>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm font-semibold flex items-center justify-between">
                      {column.label}
                      <Badge variant="secondary">{columnTasks.length}</Badge>
                    </CardTitle>
                  </CardHeader>
                </Card>

                <div className="space-y-3">
                  {columnTasks.length === 0 ? (
                    <div className="text-center py-8 text-gray-400 text-sm">
                      No tasks
                    </div>
                  ) : (
                    columnTasks.map((task) => {
                      const StatusIcon = getStatusIcon(task.status);
                      return (
                        <Card
                          key={task.id}
                          className="hover:shadow-md transition-shadow cursor-pointer"
                        >
                          <CardContent className="p-4">
                            <div className="space-y-3">
                              {/* Task Header */}
                              <div className="flex items-start justify-between">
                                <div className="flex-1">
                                  <div className="font-semibold text-sm">
                                    {task.task_name}
                                  </div>
                                  <div className="text-xs text-gray-500 mt-1">
                                    {task.task_code}
                                  </div>
                                </div>
                                <Badge
                                  className={`${getPriorityColor(task.priority)} text-white text-xs`}
                                >
                                  {task.priority.toUpperCase()}
                                </Badge>
                              </div>

                              {/* Task Type */}
                              <Badge variant="outline" className="text-xs">
                                {task.task_type}
                              </Badge>

                              {/* Location */}
                              {task.room_id && (
                                <div className="text-xs text-gray-600">
                                  Building ID: {task.building_id}, Room ID: {task.room_id}
                                </div>
                              )}

                              {/* Schedule */}
                              <div className="flex items-center gap-2 text-xs text-gray-600">
                                <Clock className="h-3 w-3" />
                                {new Date(task.scheduled_date).toLocaleDateString()}
                                {task.scheduled_time && ` at ${task.scheduled_time}`}
                              </div>

                              {/* Assigned To */}
                              {task.assigned_to_employee_id && (
                                <div className="flex items-center gap-2 text-xs text-gray-600">
                                  <User className="h-3 w-3" />
                                  Employee ID: {task.assigned_to_employee_id}
                                </div>
                              )}

                              {/* Description */}
                              {task.description && (
                                <p className="text-xs text-gray-600 line-clamp-2">
                                  {task.description}
                                </p>
                              )}

                              {/* Action Buttons */}
                              <div className="flex gap-2 pt-2">
                                {task.status === "pending" && (
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    className="flex-1 text-xs h-7"
                                    onClick={() => handleStatusChange(task.id, "in_progress")}
                                  >
                                    Start
                                  </Button>
                                )}
                                {task.status === "in_progress" && (
                                  <>
                                    <Button
                                      size="sm"
                                      variant="outline"
                                      className="flex-1 text-xs h-7"
                                      onClick={() => handleStatusChange(task.id, "completed")}
                                    >
                                      Complete
                                    </Button>
                                    <Button
                                      size="sm"
                                      variant="outline"
                                      className="flex-1 text-xs h-7"
                                      onClick={() => handleStatusChange(task.id, "on_hold")}
                                    >
                                      Hold
                                    </Button>
                                  </>
                                )}
                                {task.status === "on_hold" && (
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    className="flex-1 text-xs h-7"
                                    onClick={() => handleStatusChange(task.id, "in_progress")}
                                  >
                                    Resume
                                  </Button>
                                )}
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      );
                    })
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Task Form Dialog */}
      {showForm && (
        <TaskForm
          onClose={() => setShowForm(false)}
          onSuccess={() => {
            setShowForm(false);
            loadTasks();
          }}
        />
      )}
    </>
  );
}
