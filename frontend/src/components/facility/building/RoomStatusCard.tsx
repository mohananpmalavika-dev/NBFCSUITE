"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { DoorOpen, CheckCircle, Circle, AlertCircle, XCircle } from "lucide-react";
import type { Room } from "@/services/facility/types";

interface RoomStatusCardProps {
  rooms: Room[];
}

export default function RoomStatusCard({ rooms }: RoomStatusCardProps) {
  const stats = {
    total: rooms.length,
    available: rooms.filter((r) => r.status === "available").length,
    occupied: rooms.filter((r) => r.status === "occupied").length,
    maintenance: rooms.filter((r) => r.status === "under_maintenance").length,
    reserved: rooms.filter((r) => r.status === "reserved").length,
    outOfService: rooms.filter((r) => r.status === "out_of_service").length,
  };

  const occupancyRate =
    stats.total > 0
      ? ((stats.occupied / stats.total) * 100).toFixed(1)
      : "0";

  const statusItems = [
    {
      label: "Available",
      count: stats.available,
      icon: CheckCircle,
      color: "text-green-500",
      bgColor: "bg-green-50",
    },
    {
      label: "Occupied",
      count: stats.occupied,
      icon: Circle,
      color: "text-blue-500",
      bgColor: "bg-blue-50",
    },
    {
      label: "Maintenance",
      count: stats.maintenance,
      icon: AlertCircle,
      color: "text-orange-500",
      bgColor: "bg-orange-50",
    },
    {
      label: "Reserved",
      count: stats.reserved,
      icon: Circle,
      color: "text-purple-500",
      bgColor: "bg-purple-50",
    },
    {
      label: "Out of Service",
      count: stats.outOfService,
      icon: XCircle,
      color: "text-red-500",
      bgColor: "bg-red-50",
    },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <DoorOpen className="h-5 w-5" />
          Room Status Overview
        </CardTitle>
        <CardDescription>
          Real-time room availability and status
        </CardDescription>
      </CardHeader>
      <CardContent>
        {/* Summary Stats */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="p-4 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg">
            <div className="text-3xl font-bold text-blue-700">{stats.total}</div>
            <div className="text-sm text-blue-600">Total Rooms</div>
          </div>
          <div className="p-4 bg-gradient-to-br from-green-50 to-green-100 rounded-lg">
            <div className="text-3xl font-bold text-green-700">{occupancyRate}%</div>
            <div className="text-sm text-green-600">Occupancy Rate</div>
          </div>
        </div>

        {/* Status Breakdown */}
        <div className="space-y-3">
          {statusItems.map((item) => (
            <div
              key={item.label}
              className={`flex items-center justify-between p-3 rounded-lg ${item.bgColor}`}
            >
              <div className="flex items-center gap-3">
                <item.icon className={`h-5 w-5 ${item.color}`} />
                <span className="font-medium">{item.label}</span>
              </div>
              <Badge variant="secondary" className="font-semibold">
                {item.count}
              </Badge>
            </div>
          ))}
        </div>

        {/* Status Legend */}
        <div className="mt-6 p-3 bg-gray-50 rounded-lg">
          <div className="text-xs text-gray-600 space-y-1">
            <div className="flex items-center justify-between">
              <span>Utilization Rate:</span>
              <span className="font-semibold">
                {stats.total > 0
                  ? (
                      ((stats.occupied + stats.reserved) / stats.total) *
                      100
                    ).toFixed(1)
                  : "0"}
                %
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span>Available for Booking:</span>
              <span className="font-semibold">{stats.available}</span>
            </div>
            <div className="flex items-center justify-between">
              <span>Requires Attention:</span>
              <span className="font-semibold text-orange-600">
                {stats.maintenance + stats.outOfService}
              </span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
