"use client";

import { Edit, Trash2, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

interface SLAPolicy {
  id: string;
  name: string;
  priority: string;
  category: string;
  channel: string;
  first_response_time_minutes: number;
  resolution_time_minutes: number;
  business_hours_only: boolean;
  is_active: boolean;
}

interface SLAPolicyListProps {
  policies: SLAPolicy[];
  loading: boolean;
  onRefresh: () => void;
}

export function SLAPolicyList({
  policies,
  loading,
  onRefresh,
}: SLAPolicyListProps) {
  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-muted-foreground">Loading SLA policies...</div>
      </div>
    );
  }

  if (policies.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-center">
        <p className="text-muted-foreground mb-4">No SLA policies configured</p>
        <Button onClick={onRefresh} variant="outline">
          Refresh
        </Button>
      </div>
    );
  }

  const getPriorityBadge = (priority: string) => {
    const colors: Record<string, string> = {
      critical: "bg-red-100 text-red-800",
      high: "bg-orange-100 text-orange-800",
      medium: "bg-yellow-100 text-yellow-800",
      low: "bg-blue-100 text-blue-800",
    };

    return colors[priority] || "bg-gray-100 text-gray-800";
  };

  const formatTime = (minutes: number): string => {
    if (minutes < 60) {
      return `${minutes} min`;
    } else {
      const hours = Math.floor(minutes / 60);
      const remainingMinutes = minutes % 60;
      if (remainingMinutes === 0) {
        return `${hours} hr`;
      }
      return `${hours}h ${remainingMinutes}m`;
    }
  };

  return (
    <div className="space-y-4">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Policy Name</TableHead>
            <TableHead>Priority</TableHead>
            <TableHead>Category</TableHead>
            <TableHead>Channel</TableHead>
            <TableHead className="text-right">First Response</TableHead>
            <TableHead className="text-right">Resolution Time</TableHead>
            <TableHead>Business Hours</TableHead>
            <TableHead>Status</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {policies.map((policy) => (
            <TableRow key={policy.id}>
              <TableCell className="font-medium">{policy.name}</TableCell>
              <TableCell>
                <Badge className={getPriorityBadge(policy.priority)}>
                  {policy.priority}
                </Badge>
              </TableCell>
              <TableCell>
                <Badge variant="outline">
                  {policy.category.replace("_", " ")}
                </Badge>
              </TableCell>
              <TableCell>
                <Badge variant="outline">
                  {policy.channel.replace("_", " ")}
                </Badge>
              </TableCell>
              <TableCell className="text-right">
                <div className="flex items-center justify-end gap-1">
                  <Clock className="h-3 w-3 text-muted-foreground" />
                  {formatTime(policy.first_response_time_minutes)}
                </div>
              </TableCell>
              <TableCell className="text-right">
                <div className="flex items-center justify-end gap-1">
                  <Clock className="h-3 w-3 text-muted-foreground" />
                  {formatTime(policy.resolution_time_minutes)}
                </div>
              </TableCell>
              <TableCell>
                {policy.business_hours_only ? (
                  <Badge variant="secondary">Business Hours</Badge>
                ) : (
                  <Badge variant="outline">24/7</Badge>
                )}
              </TableCell>
              <TableCell>
                {policy.is_active ? (
                  <Badge className="bg-green-100 text-green-800">Active</Badge>
                ) : (
                  <Badge variant="secondary">Inactive</Badge>
                )}
              </TableCell>
              <TableCell className="text-right">
                <div className="flex items-center justify-end gap-2">
                  <Button variant="ghost" size="sm">
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="sm">
                    <Trash2 className="h-4 w-4 text-red-600" />
                  </Button>
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
