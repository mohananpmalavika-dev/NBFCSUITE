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
import { Plus, ClipboardList, Search, Edit, User } from "lucide-react";
import { housekeepingService } from "@/services/facility/housekeepingService";
import type { HousekeepingTask } from "@/services/facility/types";
import { useToast } from "@/components/ui/use-toast";
import TaskForm from "./TaskForm";

export default function TaskList() {
  const [tasks, setTasks] = useState<HousekeepingTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [selectedTask, setSelectedTask] = useState<HousekeepingTask | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [filterPriority, setFilterPriority] = useState<string>("all");
  const { toast } = useToast();

  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      setLoading(true);
      const params: any = { limit: 100 };
      if (filterStatus !== "all") params.status = filterStatus;
      if (filterPriority !== "all") params.priority = filterPriority;

      const response = await housekeepingService.getTasks(params);
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

  useEffect(() => {
    loadTasks();
  }, [filterStatus, filterPriority]);

  const handleEdit = (task: HousekeepingTask) => {
    setSelectedTask(task);
    setShowForm(true);
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

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: "bg-gray-500",
      in_progress: "bg-blue-500",
      completed: "bg-green-500",
      cancelled: "bg-red-500",
      on_hold: "bg-yellow-500",
    };
    return colors[status] || "bg-gray-500";
  };

  const filteredTasks = tasks.filter(
    (task) =>
      task.task_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      task.task_code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      task.task_type.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <>
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <ClipboardList className="h-5 w-5" />
                Housekeeping Tasks
              </CardTitle>
              <CardDescription>
                Manage all housekeeping tasks
              </CardDescription>
            </div>
            <Button onClick={() => setShowForm(true)}>
              <Plus className="h-4 w-4 mr-2" />
              New Task
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {/* Filters */}
          <div className="flex gap-4 mb-6">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search tasks..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select value={filterStatus} onValueChange={setFilterStatus}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="in_progress">In Progress</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="on_hold">On Hold</SelectItem>
                <SelectItem value="cancelled">Cancelled</SelectItem>
              </SelectContent>
            </Select>
            <Select value={filterPriority} onValueChange={setFilterPriority}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Priority" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Priorities</SelectItem>
                <SelectItem value="urgent">Urgent</SelectItem>
                <SelectItem value="high">High</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="low">Low</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Tasks Table */}
          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : filteredTasks.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No tasks found. Create your first task to get started.
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Task Code</TableHead>
                  <TableHead>Task Name</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Location</TableHead>
                  <TableHead>Scheduled</TableHead>
                  <TableHead>Priority</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Assigned To</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredTasks.map((task) => (
                  <TableRow key={task.id}>
                    <TableCell className="font-medium">
                      {task.task_code}
                    </TableCell>
                    <TableCell>{task.task_name}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{task.task_type}</Badge>
                    </TableCell>
                    <TableCell className="text-sm">
                      Building: {task.building_id}
                      {task.room_id && `, Room: ${task.room_id}`}
                    </TableCell>
                    <TableCell className="text-sm">
                      {new Date(task.scheduled_date).toLocaleDateString()}
                      {task.scheduled_time && (
                        <div className="text-xs text-gray-500">
                          {task.scheduled_time}
                        </div>
                      )}
                    </TableCell>
                    <TableCell>
                      <Badge
                        className={`${getPriorityColor(task.priority)} text-white`}
                      >
                        {task.priority.toUpperCase()}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge
                        className={`${getStatusColor(task.status)} text-white`}
                      >
                        {task.status.replace("_", " ").toUpperCase()}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {task.assigned_to_employee_id ? (
                        <div className="flex items-center gap-2 text-sm">
                          <User className="h-4 w-4" />
                          ID: {task.assigned_to_employee_id}
                        </div>
                      ) : (
                        <span className="text-gray-400 text-sm">Unassigned</span>
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleEdit(task)}
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

      {/* Task Form Dialog */}
      {showForm && (
        <TaskForm
          task={selectedTask}
          onClose={() => {
            setShowForm(false);
            setSelectedTask(null);
          }}
          onSuccess={() => {
            setShowForm(false);
            setSelectedTask(null);
            loadTasks();
          }}
        />
      )}
    </>
  );
}
