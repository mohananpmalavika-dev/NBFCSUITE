"use client";

import { X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";

interface TicketFiltersProps {
  filters: {
    status: string[];
    priority: string[];
    category: string[];
    channel: string[];
    sla_status: string[];
  };
  onFilterChange: (filters: any) => void;
  onClose: () => void;
}

export function TicketFilters({ filters, onFilterChange, onClose }: TicketFiltersProps) {
  const statusOptions = ["New", "Open", "In Progress", "Resolved", "Closed"];
  const priorityOptions = ["Low", "Medium", "High", "Critical"];
  const categoryOptions = [
    "General Inquiry",
    "Technical Support",
    "Billing",
    "Product Information",
    "Complaint",
    "Feature Request",
    "Other"
  ];
  const channelOptions = ["Email", "Phone", "Chat", "Web Form", "Social Media"];
  const slaStatusOptions = ["Within SLA", "Approaching SLA", "Breached SLA"];

  const handleFilterToggle = (filterType: keyof typeof filters, value: string) => {
    const currentValues = filters[filterType];
    const newValues = currentValues.includes(value)
      ? currentValues.filter((v) => v !== value)
      : [...currentValues, value];

    onFilterChange({
      ...filters,
      [filterType]: newValues
    });
  };

  const handleClearAll = () => {
    onFilterChange({
      status: [],
      priority: [],
      category: [],
      channel: [],
      sla_status: []
    });
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <CardTitle>Filters</CardTitle>
        <div className="flex gap-2">
          <Button variant="ghost" size="sm" onClick={handleClearAll}>
            Clear All
          </Button>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-5">
          {/* Status Filter */}
          <div className="space-y-3">
            <Label className="font-semibold">Status</Label>
            {statusOptions.map((status) => (
              <div key={status} className="flex items-center space-x-2">
                <Checkbox
                  id={`status-${status}`}
                  checked={filters.status.includes(status)}
                  onCheckedChange={() => handleFilterToggle("status", status)}
                />
                <label
                  htmlFor={`status-${status}`}
                  className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                >
                  {status}
                </label>
              </div>
            ))}
          </div>

          {/* Priority Filter */}
          <div className="space-y-3">
            <Label className="font-semibold">Priority</Label>
            {priorityOptions.map((priority) => (
              <div key={priority} className="flex items-center space-x-2">
                <Checkbox
                  id={`priority-${priority}`}
                  checked={filters.priority.includes(priority)}
                  onCheckedChange={() => handleFilterToggle("priority", priority)}
                />
                <label
                  htmlFor={`priority-${priority}`}
                  className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                >
                  {priority}
                </label>
              </div>
            ))}
          </div>

          {/* Category Filter */}
          <div className="space-y-3">
            <Label className="font-semibold">Category</Label>
            {categoryOptions.map((category) => (
              <div key={category} className="flex items-center space-x-2">
                <Checkbox
                  id={`category-${category}`}
                  checked={filters.category.includes(category)}
                  onCheckedChange={() => handleFilterToggle("category", category)}
                />
                <label
                  htmlFor={`category-${category}`}
                  className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                >
                  {category}
                </label>
              </div>
            ))}
          </div>

          {/* Channel Filter */}
          <div className="space-y-3">
            <Label className="font-semibold">Channel</Label>
            {channelOptions.map((channel) => (
              <div key={channel} className="flex items-center space-x-2">
                <Checkbox
                  id={`channel-${channel}`}
                  checked={filters.channel.includes(channel)}
                  onCheckedChange={() => handleFilterToggle("channel", channel)}
                />
                <label
                  htmlFor={`channel-${channel}`}
                  className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                >
                  {channel}
                </label>
              </div>
            ))}
          </div>

          {/* SLA Status Filter */}
          <div className="space-y-3">
            <Label className="font-semibold">SLA Status</Label>
            {slaStatusOptions.map((slaStatus) => (
              <div key={slaStatus} className="flex items-center space-x-2">
                <Checkbox
                  id={`sla-${slaStatus}`}
                  checked={filters.sla_status.includes(slaStatus)}
                  onCheckedChange={() => handleFilterToggle("sla_status", slaStatus)}
                />
                <label
                  htmlFor={`sla-${slaStatus}`}
                  className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                >
                  {slaStatus}
                </label>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
