"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { UserPlus, CheckCircle } from "lucide-react";
import { visitorService } from "@/services/facility/visitorService";
import type { VisitorFormData } from "@/services/facility/types";
import { useToast } from "@/components/ui/use-toast";

export default function VisitorKiosk() {
  const [step, setStep] = useState<"form" | "success">("form");
  const [loading, setLoading] = useState(false);
  const [passNumber, setPassNumber] = useState("");
  const { toast } = useToast();

  const [formData, setFormData] = useState<VisitorFormData>({
    visitor_name: "",
    visitor_type: "customer",
    company_name: "",
    mobile_number: "",
    email: "",
    purpose: "meeting",
    host_employee_id: 0,
    visit_date: new Date().toISOString().split("T")[0],
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const visitor = await visitorService.createVisitor(formData);
      setPassNumber(visitor.visitor_pass_number);
      setStep("success");
      toast({
        title: "Success",
        description: "Visitor registered successfully",
      });
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.message || "Failed to register",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      visitor_name: "",
      visitor_type: "customer",
      company_name: "",
      mobile_number: "",
      email: "",
      purpose: "meeting",
      host_employee_id: 0,
      visit_date: new Date().toISOString().split("T")[0],
    });
    setStep("form");
    setPassNumber("");
  };

  if (step === "success") {
    return (
      <Card className="max-w-2xl mx-auto">
        <CardContent className="pt-12 pb-12 text-center">
          <CheckCircle className="h-20 w-20 mx-auto text-green-500 mb-6" />
          <h2 className="text-3xl font-bold mb-4">Registration Successful!</h2>
          <div className="text-xl mb-6">
            Your Visitor Pass Number:
            <div className="text-4xl font-bold text-blue-600 mt-2">{passNumber}</div>
          </div>
          <div className="text-gray-600 mb-8">
            Please proceed to the reception desk to collect your badge
          </div>
          <Button size="lg" onClick={resetForm}>
            Register Another Visitor
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="text-center text-2xl flex items-center justify-center gap-2">
          <UserPlus className="h-6 w-6" />
          Visitor Self-Registration Kiosk
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit}>
          <div className="grid gap-6">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="visitor_name">Your Name *</Label>
                <Input
                  id="visitor_name"
                  value={formData.visitor_name}
                  onChange={(e) =>
                    setFormData({ ...formData, visitor_name: e.target.value })
                  }
                  required
                  className="text-lg p-6"
                />
              </div>
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
                  className="text-lg p-6"
                />
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
                className="text-lg p-6"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="visitor_type">Visitor Type *</Label>
                <Select
                  value={formData.visitor_type}
                  onValueChange={(value) =>
                    setFormData({ ...formData, visitor_type: value })
                  }
                >
                  <SelectTrigger className="text-lg p-6">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="customer">Customer</SelectItem>
                    <SelectItem value="vendor">Vendor</SelectItem>
                    <SelectItem value="guest">Guest</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="purpose">Purpose of Visit *</Label>
                <Select
                  value={formData.purpose}
                  onValueChange={(value) =>
                    setFormData({ ...formData, purpose: value })
                  }
                >
                  <SelectTrigger className="text-lg p-6">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="meeting">Meeting</SelectItem>
                    <SelectItem value="delivery">Delivery</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="host_employee_id">Host Employee ID *</Label>
              <Input
                id="host_employee_id"
                type="number"
                value={formData.host_employee_id || ""}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    host_employee_id: parseInt(e.target.value) || 0,
                  })
                }
                required
                className="text-lg p-6"
              />
            </div>

            <Button type="submit" size="lg" disabled={loading} className="text-lg p-6">
              {loading ? "Registering..." : "Register & Get Pass Number"}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
