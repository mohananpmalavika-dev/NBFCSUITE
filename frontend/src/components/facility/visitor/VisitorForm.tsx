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
import { visitorService } from "@/services/facility/visitorService";
import type { Visitor, VisitorFormData } from "@/services/facility/types";
import { useToast } from "@/components/ui/use-toast";

interface VisitorFormProps {
  visitor?: Visitor | null;
  onClose: () => void;
  onSuccess: () => void;
}

export default function VisitorForm({ visitor, onClose, onSuccess }: VisitorFormProps) {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);

  const [formData, setFormData] = useState<VisitorFormData>({
    visitor_name: "",
    visitor_type: "customer",
    company_name: "",
    mobile_number: "",
    email: "",
    purpose: "meeting",
    host_employee_id: 0,
    visit_date: new Date().toISOString().split("T")[0],
    expected_in_time: "",
    id_proof_type: "",
    id_proof_number: "",
  });

  useEffect(() => {
    if (visitor) {
      setFormData({
        visitor_name: visitor.visitor_name,
        visitor_type: visitor.visitor_type,
        company_name: visitor.company_name || "",
        mobile_number: visitor.mobile_number,
        email: visitor.email || "",
        purpose: visitor.purpose,
        host_employee_id: visitor.host_employee_id,
        visit_date: visitor.visit_date.split("T")[0],
      });
    }
  }, [visitor]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.host_employee_id) {
      toast({
        title: "Validation Error",
        description: "Please enter host employee ID",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);

    try {
      await visitorService.createVisitor(formData);
      toast({
        title: "Success",
        description: `Visitor ${visitor ? "updated" : "registered"} successfully`,
      });
      onSuccess();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.message || "Failed to register visitor",
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
            {visitor ? "Edit Visitor" : "Register New Visitor"}
          </DialogTitle>
          <DialogDescription>
            Enter visitor details for registration
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            {/* Visitor Information */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="visitor_name">Visitor Name *</Label>
                <Input
                  id="visitor_name"
                  value={formData.visitor_name}
                  onChange={(e) =>
                    setFormData({ ...formData, visitor_name: e.target.value })
                  }
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="visitor_type">Visitor Type *</Label>
                <Select
                  value={formData.visitor_type}
                  onValueChange={(value) =>
                    setFormData({ ...formData, visitor_type: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="customer">Customer</SelectItem>
                    <SelectItem value="vendor">Vendor</SelectItem>
                    <SelectItem value="candidate">Candidate</SelectItem>
                    <SelectItem value="contractor">Contractor</SelectItem>
                    <SelectItem value="guest">Guest</SelectItem>
                    <SelectItem value="official">Official</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="company_name">Company Name</Label>
              <Input
                id="company_name"
                value={formData.company_name}
                onChange={(e) =>
                  setFormData({ ...formData, company_name: e.target.value })
                }
              />
            </div>

            {/* Contact Information */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="mobile_number">Mobile Number *</Label>
                <Input
                  id="mobile_number"
                  type="tel"
                  value={formData.mobile_number}
                  onChange={(e) =>
                    setFormData({ ...formData, mobile_number: e.target.value })
                  }
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) =>
                    setFormData({ ...formData, email: e.target.value })
                  }
                />
              </div>
            </div>

            {/* Visit Details */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="purpose">Purpose *</Label>
                <Select
                  value={formData.purpose}
                  onValueChange={(value) =>
                    setFormData({ ...formData, purpose: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="meeting">Meeting</SelectItem>
                    <SelectItem value="interview">Interview</SelectItem>
                    <SelectItem value="delivery">Delivery</SelectItem>
                    <SelectItem value="maintenance">Maintenance</SelectItem>
                    <SelectItem value="training">Training</SelectItem>
                    <SelectItem value="audit">Audit</SelectItem>
                    <SelectItem value="inspection">Inspection</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="host_employee_id">Host Employee ID *</Label>
                <Input
                  id="host_employee_id"
                  type="number"
                  min="1"
                  value={formData.host_employee_id || ""}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      host_employee_id: parseInt(e.target.value) || 0,
                    })
                  }
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="visit_date">Visit Date *</Label>
                <Input
                  id="visit_date"
                  type="date"
                  value={formData.visit_date}
                  onChange={(e) =>
                    setFormData({ ...formData, visit_date: e.target.value })
                  }
                  required
                  min={new Date().toISOString().split("T")[0]}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="expected_in_time">Expected Time</Label>
                <Input
                  id="expected_in_time"
                  type="time"
                  value={formData.expected_in_time}
                  onChange={(e) =>
                    setFormData({ ...formData, expected_in_time: e.target.value })
                  }
                />
              </div>
            </div>

            {/* ID Proof */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="id_proof_type">ID Proof Type</Label>
                <Select
                  value={formData.id_proof_type}
                  onValueChange={(value) =>
                    setFormData({ ...formData, id_proof_type: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select ID type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="aadhar">Aadhar Card</SelectItem>
                    <SelectItem value="pan">PAN Card</SelectItem>
                    <SelectItem value="driving_license">Driving License</SelectItem>
                    <SelectItem value="passport">Passport</SelectItem>
                    <SelectItem value="voter_id">Voter ID</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="id_proof_number">ID Proof Number</Label>
                <Input
                  id="id_proof_number"
                  value={formData.id_proof_number}
                  onChange={(e) =>
                    setFormData({ ...formData, id_proof_number: e.target.value })
                  }
                />
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? "Saving..." : visitor ? "Update" : "Register"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
