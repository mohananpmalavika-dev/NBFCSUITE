"use client";

import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
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
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { toast } from "@/components/ui/use-toast";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  ArrowLeft,
  Plus,
  Edit,
  UserPlus,
  Shield,
  CheckCircle,
  XCircle,
  Info,
  Users,
} from "lucide-react";
import {
  lockerCustomerService,
  OperationMode,
  HolderType,
  type LockerJointHolder,
} from "@/services/locker.service";
import { format } from "date-fns";

export default function JointHoldersPage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const allocationId = params.allocationId as string;

  const [showAddDialog, setShowAddDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [selectedHolder, setSelectedHolder] = useState<LockerJointHolder | null>(null);
  
  const [holderForm, setHolderForm] = useState({
    locker_customer_id: "",
    customer_id: "",
    holder_type: HolderType.SECONDARY,
    holder_sequence: 2,
    operation_mode: OperationMode.EITHER_OR_SURVIVOR,
    can_operate_alone: true,
    requires_joint_operation: false,
    can_deposit: true,
    can_retrieve: true,
    can_make_payments: true,
    can_surrender: false,
    can_add_nominee: false,
    survivorship_rights: true,
    inheritance_percentage: 0,
    agreement_accepted: false,
  });

  // Fetch joint holders
  const { data: holdersData, isLoading } = useQuery({
    queryKey: ["locker-joint-holders", allocationId],
    queryFn: () => lockerCustomerService.getAllocationJointHolders(allocationId),
  });

  // Add joint holder mutation
  const addJointHolder = useMutation({
    mutationFn: (data: any) =>
      lockerCustomerService.addJointHolder({
        allocation_id: allocationId,
        ...data,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["locker-joint-holders"] });
      toast({
        title: "Joint Holder Added",
        description: "Joint holder has been added successfully.",
      });
      setShowAddDialog(false);
      resetForm();
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to add joint holder",
        variant: "destructive",
      });
    },
  });

  // Update joint holder mutation
  const updateJointHolder = useMutation({
    mutationFn: (data: { id: string; updates: any }) =>
      lockerCustomerService.updateJointHolder(data.id, data.updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["locker-joint-holders"] });
      toast({
        title: "Joint Holder Updated",
        description: "Joint holder details updated successfully.",
      });
      setShowEditDialog(false);
      setSelectedHolder(null);
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to update joint holder",
        variant: "destructive",
      });
    },
  });

  // Deactivate joint holder mutation
  const deactivateHolder = useMutation({
    mutationFn: (data: { id: string; reason: string }) =>
      lockerCustomerService.deactivateJointHolder(data.id, data.reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["locker-joint-holders"] });
      toast({
        title: "Joint Holder Deactivated",
        description: "Joint holder has been deactivated.",
      });
    },
  });

  const resetForm = () => {
    setHolderForm({
      locker_customer_id: "",
      customer_id: "",
      holder_type: HolderType.SECONDARY,
      holder_sequence: 2,
      operation_mode: OperationMode.EITHER_OR_SURVIVOR,
      can_operate_alone: true,
      requires_joint_operation: false,
      can_deposit: true,
      can_retrieve: true,
      can_make_payments: true,
      can_surrender: false,
      can_add_nominee: false,
      survivorship_rights: true,
      inheritance_percentage: 0,
      agreement_accepted: false,
    });
  };

  const handleAddSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    addJointHolder.mutate(holderForm);
  };

  const handleEditSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedHolder) return;
    
    updateJointHolder.mutate({
      id: selectedHolder.id,
      updates: {
        operation_mode: holderForm.operation_mode,
        can_operate_alone: holderForm.can_operate_alone,
        can_deposit: holderForm.can_deposit,
        can_retrieve: holderForm.can_retrieve,
        can_make_payments: holderForm.can_make_payments,
        can_surrender: holderForm.can_surrender,
        can_add_nominee: holderForm.can_add_nominee,
      },
    });
  };

  const getOperationModeInfo = (mode: string) => {
    const info: Record<string, { title: string; description: string; icon: string }> = {
      either_or_survivor: {
        title: "Either or Survivor",
        description: "Any holder can operate independently. On death, survivor gets full rights.",
        icon: "👥",
      },
      former_or_survivor: {
        title: "Former or Survivor",
        description: "Primary holder operates first. On death, secondary holder gets rights.",
        icon: "1️⃣",
      },
      latter_or_survivor: {
        title: "Latter or Survivor",
        description: "Secondary holder operates. On death, primary holder gets rights.",
        icon: "2️⃣",
      },
      joint: {
        title: "Joint Operation",
        description: "All holders must sign together for any operation.",
        icon: "🤝",
      },
      anyone: {
        title: "Anyone",
        description: "Any single holder can operate independently.",
        icon: "✅",
      },
    };
    return info[mode] || info.either_or_survivor;
  };

  const holders = holdersData?.data || [];

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">Joint Holders</h1>
            <p className="text-muted-foreground">
              Manage joint locker holders and operation modes
            </p>
          </div>
        </div>
        <Button onClick={() => setShowAddDialog(true)}>
          <Plus className="mr-2 h-4 w-4" />
          Add Joint Holder
        </Button>
      </div>

      {/* Operation Mode Explanation */}
      <Card className="border-blue-200 bg-blue-50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-blue-900">
            <Info className="h-5 w-5" />
            Operation Modes Explained
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 md:grid-cols-2">
            {Object.entries(OperationMode).map(([key, value]) => {
              const info = getOperationModeInfo(value);
              return (
                <div key={value} className="flex gap-3 p-3 bg-white rounded-lg">
                  <div className="text-2xl">{info.icon}</div>
                  <div>
                    <h4 className="font-semibold text-sm">{info.title}</h4>
                    <p className="text-xs text-muted-foreground">{info.description}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Joint Holders List */}
      <Card>
        <CardHeader>
          <CardTitle>Current Joint Holders</CardTitle>
          <CardDescription>{holders.length} joint holder(s)</CardDescription>
        </CardHeader>
        <CardContent>
          {holders.length === 0 ? (
            <div className="text-center py-8">
              <Users className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-muted-foreground">No joint holders added yet</p>
              <Button
                className="mt-4"
                variant="outline"
                onClick={() => setShowAddDialog(true)}
              >
                <Plus className="mr-2 h-4 w-4" />
                Add First Joint Holder
              </Button>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Holder ID</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Sequence</TableHead>
                  <TableHead>Operation Mode</TableHead>
                  <TableHead>Permissions</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {holders.map((holder: LockerJointHolder) => (
                  <TableRow key={holder.id}>
                    <TableCell className="font-medium">
                      {holder.joint_holder_id}
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{holder.holder_type}</Badge>
                    </TableCell>
                    <TableCell>{holder.holder_sequence}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <span className="text-lg">
                          {getOperationModeInfo(holder.operation_mode).icon}
                        </span>
                        <span className="text-sm">
                          {holder.operation_mode.replace(/_/g, " ")}
                        </span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-1">
                        {holder.can_deposit && (
                          <Badge variant="outline" className="text-xs">
                            Deposit
                          </Badge>
                        )}
                        {holder.can_retrieve && (
                          <Badge variant="outline" className="text-xs">
                            Retrieve
                          </Badge>
                        )}
                        {holder.can_make_payments && (
                          <Badge variant="outline" className="text-xs">
                            Pay
                          </Badge>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={holder.status === "active" ? "default" : "secondary"}
                      >
                        {holder.status}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            setSelectedHolder(holder);
                            setHolderForm({
                              ...holderForm,
                              operation_mode: holder.operation_mode,
                              can_operate_alone: holder.can_operate_alone,
                              can_deposit: holder.can_deposit,
                              can_retrieve: holder.can_retrieve,
                              can_make_payments: holder.can_make_payments,
                              can_surrender: holder.can_surrender,
                              can_add_nominee: holder.can_add_nominee,
                            });
                            setShowEditDialog(true);
                          }}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        {holder.status === "active" && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() =>
                              deactivateHolder.mutate({
                                id: holder.id,
                                reason: "Requested by customer",
                              })
                            }
                          >
                            <XCircle className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Add Joint Holder Dialog */}
      <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Add Joint Holder</DialogTitle>
            <DialogDescription>
              Add a new joint holder to this locker allocation
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handleAddSubmit} className="space-y-6">
            {/* Basic Information */}
            <div className="space-y-4">
              <h3 className="font-semibold">Basic Information</h3>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label>Customer ID *</Label>
                  <Input
                    placeholder="Enter customer ID"
                    value={holderForm.customer_id}
                    onChange={(e) =>
                      setHolderForm({ ...holderForm, customer_id: e.target.value })
                    }
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label>Locker Customer ID *</Label>
                  <Input
                    placeholder="Enter locker customer ID"
                    value={holderForm.locker_customer_id}
                    onChange={(e) =>
                      setHolderForm({
                        ...holderForm,
                        locker_customer_id: e.target.value,
                      })
                    }
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label>Holder Type *</Label>
                  <Select
                    value={holderForm.holder_type}
                    onValueChange={(value) =>
                      setHolderForm({ ...holderForm, holder_type: value as HolderType })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value={HolderType.PRIMARY}>Primary</SelectItem>
                      <SelectItem value={HolderType.SECONDARY}>Secondary</SelectItem>
                      <SelectItem value={HolderType.TERTIARY}>Tertiary</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Sequence *</Label>
                  <Input
                    type="number"
                    min="1"
                    value={holderForm.holder_sequence}
                    onChange={(e) =>
                      setHolderForm({
                        ...holderForm,
                        holder_sequence: parseInt(e.target.value),
                      })
                    }
                    required
                  />
                </div>
              </div>
            </div>

            {/* Operation Mode */}
            <div className="space-y-4">
              <h3 className="font-semibold">Operation Mode</h3>
              <div className="space-y-2">
                <Label>Select Operation Mode *</Label>
                <Select
                  value={holderForm.operation_mode}
                  onValueChange={(value) =>
                    setHolderForm({
                      ...holderForm,
                      operation_mode: value as OperationMode,
                    })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(OperationMode).map(([key, value]) => {
                      const info = getOperationModeInfo(value);
                      return (
                        <SelectItem key={value} value={value}>
                          <div className="flex items-center gap-2">
                            <span>{info.icon}</span>
                            <span>{info.title}</span>
                          </div>
                        </SelectItem>
                      );
                    })}
                  </SelectContent>
                </Select>
                <Alert>
                  <Info className="h-4 w-4" />
                  <AlertDescription>
                    {getOperationModeInfo(holderForm.operation_mode).description}
                  </AlertDescription>
                </Alert>
              </div>
            </div>

            {/* Permissions Matrix */}
            <div className="space-y-4">
              <h3 className="font-semibold">Permissions</h3>
              <div className="grid gap-3 md:grid-cols-2 border rounded-lg p-4">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="can_deposit"
                    checked={holderForm.can_deposit}
                    onCheckedChange={(checked) =>
                      setHolderForm({ ...holderForm, can_deposit: !!checked })
                    }
                  />
                  <Label htmlFor="can_deposit" className="cursor-pointer">
                    Can deposit items
                  </Label>
                </div>

                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="can_retrieve"
                    checked={holderForm.can_retrieve}
                    onCheckedChange={(checked) =>
                      setHolderForm({ ...holderForm, can_retrieve: !!checked })
                    }
                  />
                  <Label htmlFor="can_retrieve" className="cursor-pointer">
                    Can retrieve items
                  </Label>
                </div>

                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="can_make_payments"
                    checked={holderForm.can_make_payments}
                    onCheckedChange={(checked) =>
                      setHolderForm({ ...holderForm, can_make_payments: !!checked })
                    }
                  />
                  <Label htmlFor="can_make_payments" className="cursor-pointer">
                    Can make rent payments
                  </Label>
                </div>

                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="can_surrender"
                    checked={holderForm.can_surrender}
                    onCheckedChange={(checked) =>
                      setHolderForm({ ...holderForm, can_surrender: !!checked })
                    }
                  />
                  <Label htmlFor="can_surrender" className="cursor-pointer">
                    Can surrender locker
                  </Label>
                </div>

                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="can_add_nominee"
                    checked={holderForm.can_add_nominee}
                    onCheckedChange={(checked) =>
                      setHolderForm({ ...holderForm, can_add_nominee: !!checked })
                    }
                  />
                  <Label htmlFor="can_add_nominee" className="cursor-pointer">
                    Can add/modify nominee
                  </Label>
                </div>

                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="can_operate_alone"
                    checked={holderForm.can_operate_alone}
                    onCheckedChange={(checked) =>
                      setHolderForm({ ...holderForm, can_operate_alone: !!checked })
                    }
                  />
                  <Label htmlFor="can_operate_alone" className="cursor-pointer">
                    Can operate independently
                  </Label>
                </div>
              </div>
            </div>

            {/* Survivorship Rights */}
            <div className="space-y-4">
              <h3 className="font-semibold">Survivorship Rights</h3>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="survivorship_rights"
                    checked={holderForm.survivorship_rights}
                    onCheckedChange={(checked) =>
                      setHolderForm({ ...holderForm, survivorship_rights: !!checked })
                    }
                  />
                  <Label htmlFor="survivorship_rights" className="cursor-pointer">
                    Has survivorship rights
                  </Label>
                </div>

                <div className="space-y-2">
                  <Label>Inheritance Percentage</Label>
                  <Input
                    type="number"
                    min="0"
                    max="100"
                    value={holderForm.inheritance_percentage}
                    onChange={(e) =>
                      setHolderForm({
                        ...holderForm,
                        inheritance_percentage: parseFloat(e.target.value),
                      })
                    }
                  />
                </div>
              </div>
            </div>

            {/* Agreement */}
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="agreement_accepted"
                  checked={holderForm.agreement_accepted}
                  onCheckedChange={(checked) =>
                    setHolderForm({ ...holderForm, agreement_accepted: !!checked })
                  }
                  required
                />
                <Label htmlFor="agreement_accepted" className="cursor-pointer">
                  I accept the joint holder agreement terms and conditions *
                </Label>
              </div>
            </div>

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setShowAddDialog(false);
                  resetForm();
                }}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={addJointHolder.isPending}>
                {addJointHolder.isPending ? "Adding..." : "Add Joint Holder"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Edit Dialog */}
      <Dialog open={showEditDialog} onOpenChange={setShowEditDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Edit Joint Holder</DialogTitle>
            <DialogDescription>
              Update operation mode and permissions
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handleEditSubmit} className="space-y-6">
            {/* Operation Mode */}
            <div className="space-y-2">
              <Label>Operation Mode</Label>
              <Select
                value={holderForm.operation_mode}
                onValueChange={(value) =>
                  setHolderForm({
                    ...holderForm,
                    operation_mode: value as OperationMode,
                  })
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {Object.entries(OperationMode).map(([key, value]) => (
                    <SelectItem key={value} value={value}>
                      {getOperationModeInfo(value).title}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Permissions */}
            <div className="space-y-4">
              <h3 className="font-semibold">Permissions</h3>
              <div className="grid gap-3 md:grid-cols-2">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="edit_can_deposit"
                    checked={holderForm.can_deposit}
                    onCheckedChange={(checked) =>
                      setHolderForm({ ...holderForm, can_deposit: !!checked })
                    }
                  />
                  <Label htmlFor="edit_can_deposit">Can deposit items</Label>
                </div>

                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="edit_can_retrieve"
                    checked={holderForm.can_retrieve}
                    onCheckedChange={(checked) =>
                      setHolderForm({ ...holderForm, can_retrieve: !!checked })
                    }
                  />
                  <Label htmlFor="edit_can_retrieve">Can retrieve items</Label>
                </div>

                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="edit_can_make_payments"
                    checked={holderForm.can_make_payments}
                    onCheckedChange={(checked) =>
                      setHolderForm({ ...holderForm, can_make_payments: !!checked })
                    }
                  />
                  <Label htmlFor="edit_can_make_payments">Can make payments</Label>
                </div>

                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="edit_can_surrender"
                    checked={holderForm.can_surrender}
                    onCheckedChange={(checked) =>
                      setHolderForm({ ...holderForm, can_surrender: !!checked })
                    }
                  />
                  <Label htmlFor="edit_can_surrender">Can surrender locker</Label>
                </div>
              </div>
            </div>

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setShowEditDialog(false);
                  setSelectedHolder(null);
                }}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={updateJointHolder.isPending}>
                {updateJointHolder.isPending ? "Updating..." : "Update"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
