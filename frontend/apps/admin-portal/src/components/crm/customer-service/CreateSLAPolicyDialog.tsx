"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
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
import { Switch } from "@/components/ui/switch";
import { customerServiceApi } from "@/lib/api/customer-service";
import { useToast } from "@/hooks/use-toast";

interface CreateSLAPolicyDialogProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function CreateSLAPolicyDialog({
  open,
  onClose,
  onSuccess,
}: CreateSLAPolicyDialogProps) {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    priority: "medium",
    category: "general",
    channel: "email",
    first_response_time_minutes: 60,
    resolution_time_minutes: 480,
    business_hours_only: true,
    escalation_time_minutes: 240,
    is_active: true,
  });

  const { toast } = useToast();

  const handleChange = (field: string, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name) {
      toast({
        title: "Validation Error",
        description: "Please provide a policy name",
        variant: "destructive",
      });
      return;
    }

    try {
      setLoading(true);
      await customerServiceApi.createSLAPolicy(formData);
      onSuccess();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to create SLA policy",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Create SLA Policy</DialogTitle>
          <DialogDescription>
            Define service level agreement for ticket handling
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">
              Policy Name <span className="text-red-500">*</span>
            </Label>
            <Input
              id="name"
              value={formData.name}
              onChange={(e) => handleChange("name", e.target.value)}
              placeholder="Critical Tickets - Email Channel"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="priority">Priority Level</Label>
              <Select
                value={formData.priority}
                onValueChange={(value) => handleChange("priority", value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="critical">Critical</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="low">Low</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="category">Category</Label>
              <Select
                value={formData.category}
                onValueChange={(value) => handleChange("category", value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="general">General</SelectItem>
                  <SelectItem value="technical">Technical</SelectItem>
                  <SelectItem value="billing">Billing</SelectItem>
                  <SelectItem value="account">Account</SelectItem>
                  <SelectItem value="loan">Loan</SelectItem>
                  <SelectItem value="deposit">Deposit</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="channel">Communication Channel</Label>
            <Select
              value={formData.channel}
              onValueChange={(value) => handleChange("channel", value)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="email">Email</SelectItem>
                <SelectItem value="phone">Phone</SelectItem>
                <SelectItem value="chat">Live Chat</SelectItem>
                <SelectItem value="portal">Self-Service Portal</SelectItem>
                <SelectItem value="social">Social Media</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="first_response">
                First Response Time (minutes)
              </Label>
              <Input
                id="first_response"
                type="number"
                value={formData.first_response_time_minutes}
                onChange={(e) =>
                  handleChange(
                    "first_response_time_minutes",
                    parseInt(e.target.value)
                  )
                }
                min="1"
              />
              <p className="text-xs text-muted-foreground">
                {Math.floor(formData.first_response_time_minutes / 60)}h{" "}
                {formData.first_response_time_minutes % 60}m
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="resolution">Resolution Time (minutes)</Label>
              <Input
                id="resolution"
                type="number"
                value={formData.resolution_time_minutes}
                onChange={(e) =>
                  handleChange(
                    "resolution_time_minutes",
                    parseInt(e.target.value)
                  )
                }
                min="1"
              />
              <p className="text-xs text-muted-foreground">
                {Math.floor(formData.resolution_time_minutes / 60)}h{" "}
                {formData.resolution_time_minutes % 60}m
              </p>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="escalation">
              Escalation Time (minutes, optional)
            </Label>
            <Input
              id="escalation"
              type="number"
              value={formData.escalation_time_minutes}
              onChange={(e) =>
                handleChange("escalation_time_minutes", parseInt(e.target.value))
              }
              min="1"
            />
            <p className="text-xs text-muted-foreground">
              Auto-escalate ticket if not responded within this time
            </p>
          </div>

          <div className="flex items-center justify-between space-x-2">
            <div className="space-y-0.5">
              <Label htmlFor="business_hours">Business Hours Only</Label>
              <p className="text-xs text-muted-foreground">
                Count only business hours (Mon-Fri, 9 AM - 6 PM)
              </p>
            </div>
            <Switch
              id="business_hours"
              checked={formData.business_hours_only}
              onCheckedChange={(checked) =>
                handleChange("business_hours_only", checked)
              }
            />
          </div>

          <div className="flex items-center justify-between space-x-2">
            <div className="space-y-0.5">
              <Label htmlFor="is_active">Active</Label>
              <p className="text-xs text-muted-foreground">
                Enable this policy immediately
              </p>
            </div>
            <Switch
              id="is_active"
              checked={formData.is_active}
              onCheckedChange={(checked) => handleChange("is_active", checked)}
            />
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? "Creating..." : "Create Policy"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
