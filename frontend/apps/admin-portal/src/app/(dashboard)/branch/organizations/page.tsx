"use client";

import { useState, useEffect } from "react";
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
import { Plus, Building2, Edit, Trash2, ChevronRight } from "lucide-react";
import { organizationService } from "@/services/branchService";
import type { Organization, OrganizationHierarchy, OrganizationFormData } from "@/types/branch";
import { OrganizationLevel, BranchStatus } from "@/types/branch";
import { useToast } from "@/components/ui/use-toast";

export default function OrganizationsPage() {
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [hierarchy, setHierarchy] = useState<OrganizationHierarchy[]>([]);
  const [loading, setLoading] = useState(true);
  const [showDialog, setShowDialog] = useState(false);
  const [editingOrg, setEditingOrg] = useState<Organization | null>(null);
  const { toast } = useToast();

  const [formData, setFormData] = useState<OrganizationFormData>({
    code: "",
    name: "",
    display_name: "",
    level: OrganizationLevel.BRANCH,
    country: "India",
    status: BranchStatus.ACTIVE,
    is_operational: true,
    cash_limit: 0,
    daily_transaction_limit: 0,
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [orgsData, hierarchyData] = await Promise.all([
        organizationService.list({ limit: 100 }),
        organizationService.getHierarchy(),
      ]);
      setOrganizations(orgsData.items);
      setHierarchy(hierarchyData);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load organizations",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingOrg) {
        await organizationService.update(editingOrg.id, formData);
        toast({
          title: "Success",
          description: "Organization updated successfully",
        });
      } else {
        await organizationService.create(formData);
        toast({
          title: "Success",
          description: "Organization created successfully",
        });
      }
      setShowDialog(false);
      resetForm();
      loadData();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.message || "Failed to save organization",
        variant: "destructive",
      });
    }
  };

  const handleEdit = (org: Organization) => {
    setEditingOrg(org);
    setFormData({
      code: org.code,
      name: org.name,
      display_name: org.display_name,
      level: org.level,
      parent_id: org.parent_id,
      manager_id: org.manager_id,
      manager_name: org.manager_name,
      email: org.email,
      phone: org.phone,
      address_line1: org.address_line1,
      address_line2: org.address_line2,
      city: org.city,
      state: org.state,
      pincode: org.pincode,
      country: org.country,
      status: org.status,
      is_operational: org.is_operational,
      cash_limit: org.cash_limit,
      daily_transaction_limit: org.daily_transaction_limit,
    });
    setShowDialog(true);
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this organization?")) return;

    try {
      await organizationService.delete(id);
      toast({
        title: "Success",
        description: "Organization deleted successfully",
      });
      loadData();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.message || "Failed to delete organization",
        variant: "destructive",
      });
    }
  };

  const resetForm = () => {
    setEditingOrg(null);
    setFormData({
      code: "",
      name: "",
      display_name: "",
      level: OrganizationLevel.BRANCH,
      country: "India",
      status: BranchStatus.ACTIVE,
      is_operational: true,
      cash_limit: 0,
      daily_transaction_limit: 0,
    });
  };

  const getLevelColor = (level: OrganizationLevel) => {
    switch (level) {
      case OrganizationLevel.HEAD_OFFICE:
        return "bg-purple-500";
      case OrganizationLevel.ZONE:
        return "bg-blue-500";
      case OrganizationLevel.REGION:
        return "bg-green-500";
      case OrganizationLevel.AREA:
        return "bg-yellow-500";
      case OrganizationLevel.BRANCH:
        return "bg-orange-500";
      default:
        return "bg-gray-500";
    }
  };

  const renderHierarchy = (nodes: OrganizationHierarchy[], depth = 0) => {
    return nodes.map((node) => (
      <div key={node.id} style={{ marginLeft: `${depth * 24}px` }} className="mb-2">
        <Card className="hover:shadow-md transition-shadow">
          <CardHeader className="py-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Building2 className="h-5 w-5 text-muted-foreground" />
                <div>
                  <CardTitle className="text-base">{node.name}</CardTitle>
                  <CardDescription className="text-sm">{node.code}</CardDescription>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Badge className={getLevelColor(node.level)}>
                  {node.level.replace("_", " ")}
                </Badge>
                {node.children.length > 0 && (
                  <Badge variant="secondary">{node.children.length} children</Badge>
                )}
              </div>
            </div>
          </CardHeader>
        </Card>
        {node.children.length > 0 && (
          <div className="mt-2">{renderHierarchy(node.children, depth + 1)}</div>
        )}
      </div>
    ));
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Organizations</h1>
          <p className="text-muted-foreground">
            Manage organizational hierarchy (HO → Zone → Region → Area → Branch)
          </p>
        </div>
        <Button
          onClick={() => {
            resetForm();
            setShowDialog(true);
          }}
        >
          <Plus className="mr-2 h-4 w-4" />
          Create Organization
        </Button>
      </div>

      {/* Hierarchy View */}
      <Card>
        <CardHeader>
          <CardTitle>Organization Hierarchy</CardTitle>
          <CardDescription>Tree view of organizational structure</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : hierarchy.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No organizations found. Create your first organization to get started.
            </div>
          ) : (
            <div className="space-y-2">{renderHierarchy(hierarchy)}</div>
          )}
        </CardContent>
      </Card>

      {/* Organizations List */}
      <Card>
        <CardHeader>
          <CardTitle>All Organizations</CardTitle>
          <CardDescription>List view of all organizations</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {organizations.map((org) => (
              <div
                key={org.id}
                className="flex items-center justify-between p-4 border rounded-lg hover:bg-accent"
              >
                <div className="flex items-center gap-4">
                  <Building2 className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="font-semibold">{org.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {org.code} • {org.level.replace("_", " ")}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge
                    variant={org.status === BranchStatus.ACTIVE ? "default" : "secondary"}
                  >
                    {org.status}
                  </Badge>
                  <Button variant="outline" size="sm" onClick={() => handleEdit(org)}>
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDelete(org.id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Create/Edit Dialog */}
      <Dialog open={showDialog} onOpenChange={setShowDialog}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {editingOrg ? "Edit Organization" : "Create Organization"}
            </DialogTitle>
            <DialogDescription>
              {editingOrg
                ? "Update organization details"
                : "Create a new organizational unit"}
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="code">Code *</Label>
                <Input
                  id="code"
                  value={formData.code}
                  onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                  placeholder="ORG001"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="level">Level *</Label>
                <Select
                  value={formData.level}
                  onValueChange={(value) =>
                    setFormData({ ...formData, level: value as OrganizationLevel })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.values(OrganizationLevel).map((level) => (
                      <SelectItem key={level} value={level}>
                        {level.replace("_", " ")}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="name">Name *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Organization Name"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="display_name">Display Name *</Label>
              <Input
                id="display_name"
                value={formData.display_name}
                onChange={(e) =>
                  setFormData({ ...formData, display_name: e.target.value })
                }
                placeholder="Display Name"
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="parent_id">Parent Organization</Label>
                <Select
                  value={formData.parent_id || ""}
                  onValueChange={(value) =>
                    setFormData({ ...formData, parent_id: value || undefined })
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select parent" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">No Parent</SelectItem>
                    {organizations.map((org) => (
                      <SelectItem key={org.id} value={org.id}>
                        {org.name} ({org.code})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="status">Status</Label>
                <Select
                  value={formData.status}
                  onValueChange={(value) =>
                    setFormData({ ...formData, status: value as BranchStatus })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.values(BranchStatus).map((status) => (
                      <SelectItem key={status} value={status}>
                        {status}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email || ""}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="email@example.com"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="phone">Phone</Label>
                <Input
                  id="phone"
                  value={formData.phone || ""}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  placeholder="+91 9876543210"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="cash_limit">Cash Limit (₹)</Label>
                <Input
                  id="cash_limit"
                  type="number"
                  value={formData.cash_limit}
                  onChange={(e) =>
                    setFormData({ ...formData, cash_limit: Number(e.target.value) })
                  }
                  placeholder="0"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="daily_transaction_limit">Daily Transaction Limit (₹)</Label>
                <Input
                  id="daily_transaction_limit"
                  type="number"
                  value={formData.daily_transaction_limit}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      daily_transaction_limit: Number(e.target.value),
                    })
                  }
                  placeholder="0"
                />
              </div>
            </div>

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => setShowDialog(false)}
              >
                Cancel
              </Button>
              <Button type="submit">
                {editingOrg ? "Update" : "Create"} Organization
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
