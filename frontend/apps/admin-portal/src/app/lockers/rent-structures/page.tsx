"use client";

import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "@/components/ui/use-toast";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Plus,
  Calculator,
  TrendingUp,
  DollarSign,
  Percent,
  Edit,
  Eye,
  XCircle,
} from "lucide-react";
import {
  lockerCustomerService,
  LockerSize,
  CustomerCategory,
  type LockerRentStructure,
  type RentCalculation,
} from "@/services/locker.service";
import { format } from "date-fns";

export default function RentStructuresPage() {
  const router = useRouter();
  const queryClient = useQueryClient();

  const [showCalculator, setShowCalculator] = useState(false);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [sizeFilter, setSizeFilter] = useState<string>("all");
  const [categoryFilter, setCategoryFilter] = useState<string>("all");

  // Calculator state
  const [calcForm, setCalcForm] = useState({
    locker_size: LockerSize.MEDIUM,
    customer_category: CustomerCategory.REGULAR,
    rent_frequency: "annual",
    period_from: format(new Date(), "yyyy-MM-dd"),
    period_to: format(
      new Date(new Date().setFullYear(new Date().getFullYear() + 1)),
      "yyyy-MM-dd"
    ),
    advance_payment: false,
  });

  // Create structure form
  const [structureForm, setStructureForm] = useState({
    locker_size: LockerSize.SMALL,
    customer_category: CustomerCategory.REGULAR,
    location_type: "standard",
    base_rent_annual: "5000",
    security_deposit_amount: "10000",
    gst_applicable: true,
    gst_rate: "18.0",
    gst_on_rent: true,
    gst_on_deposit: false,
    discount_percentage: "0",
    advance_payment_discount: "0",
    late_payment_penalty_applicable: true,
    late_payment_grace_days: "15",
    late_payment_penalty_percentage: "2.0",
    penalty_calculation_method: "percentage",
    duplicate_key_charges: "500",
    locker_breaking_charges: "2000",
    transfer_charges: "500",
    closure_charges: "0",
    minimum_rent_period_months: "12",
    effective_from: format(new Date(), "yyyy-MM-dd"),
    is_active: true,
  });

  // Fetch rent structures
  const { data: structuresData, isLoading } = useQuery({
    queryKey: ["rent-structures", sizeFilter, categoryFilter],
    queryFn: () =>
      lockerCustomerService.listRentStructures({
        locker_size: sizeFilter !== "all" ? (sizeFilter as LockerSize) : undefined,
        customer_category:
          categoryFilter !== "all"
            ? (categoryFilter as CustomerCategory)
            : undefined,
      }),
  });

  // Calculate rent
  const { data: calculation, isLoading: calculating } = useQuery({
    queryKey: ["rent-calculation", calcForm],
    queryFn: () => lockerCustomerService.calculateRent(calcForm),
    enabled: false, // Manual trigger
  });

  // Create rent structure
  const createStructure = useMutation({
    mutationFn: (data: any) => lockerCustomerService.createRentStructure(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["rent-structures"] });
      toast({
        title: "Rent Structure Created",
        description: "New rent structure has been created successfully.",
      });
      setShowCreateDialog(false);
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to create rent structure",
        variant: "destructive",
      });
    },
  });

  const handleCalculate = () => {
    queryClient.fetchQuery({
      queryKey: ["rent-calculation", calcForm],
      queryFn: () => lockerCustomerService.calculateRent(calcForm),
    });
  };

  const handleCreateSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createStructure.mutate({
      ...structureForm,
      base_rent_annual: parseFloat(structureForm.base_rent_annual),
      security_deposit_amount: parseFloat(structureForm.security_deposit_amount),
      gst_rate: parseFloat(structureForm.gst_rate),
      discount_percentage: parseFloat(structureForm.discount_percentage),
      advance_payment_discount: parseFloat(structureForm.advance_payment_discount),
      late_payment_grace_days: parseInt(structureForm.late_payment_grace_days),
      late_payment_penalty_percentage: parseFloat(
        structureForm.late_payment_penalty_percentage
      ),
      duplicate_key_charges: parseFloat(structureForm.duplicate_key_charges),
      locker_breaking_charges: parseFloat(structureForm.locker_breaking_charges),
      transfer_charges: parseFloat(structureForm.transfer_charges),
      closure_charges: parseFloat(structureForm.closure_charges),
      minimum_rent_period_months: parseInt(structureForm.minimum_rent_period_months),
    });
  };

  const structures = structuresData?.data?.structures || [];

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Rent Structures</h1>
          <p className="text-muted-foreground">
            Manage locker pricing and rent calculation
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setShowCalculator(true)}>
            <Calculator className="mr-2 h-4 w-4" />
            Rent Calculator
          </Button>
          <Button onClick={() => setShowCreateDialog(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Create Structure
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <Label>Locker Size</Label>
              <Select value={sizeFilter} onValueChange={setSizeFilter}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Sizes</SelectItem>
                  <SelectItem value={LockerSize.SMALL}>Small</SelectItem>
                  <SelectItem value={LockerSize.MEDIUM}>Medium</SelectItem>
                  <SelectItem value={LockerSize.LARGE}>Large</SelectItem>
                  <SelectItem value={LockerSize.EXTRA_LARGE}>Extra Large</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Customer Category</Label>
              <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Categories</SelectItem>
                  <SelectItem value={CustomerCategory.REGULAR}>Regular</SelectItem>
                  <SelectItem value={CustomerCategory.PREMIUM}>Premium</SelectItem>
                  <SelectItem value={CustomerCategory.SENIOR_CITIZEN}>
                    Senior Citizen
                  </SelectItem>
                  <SelectItem value={CustomerCategory.STAFF}>Staff</SelectItem>
                  <SelectItem value={CustomerCategory.VIP}>VIP</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Rent Structures Table */}
      <Card>
        <CardHeader>
          <CardTitle>Configured Rent Structures</CardTitle>
          <CardDescription>
            {structures.length} structure(s) found
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Size</TableHead>
                <TableHead>Category</TableHead>
                <TableHead>Annual Rent</TableHead>
                <TableHead>Security Deposit</TableHead>
                <TableHead>GST</TableHead>
                <TableHead>Penalty</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Effective From</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={9} className="text-center">
                    Loading structures...
                  </TableCell>
                </TableRow>
              ) : structures.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={9} className="text-center">
                    No rent structures found
                  </TableCell>
                </TableRow>
              ) : (
                structures.map((structure: LockerRentStructure) => (
                  <TableRow key={structure.id}>
                    <TableCell>
                      <Badge variant="outline">
                        {structure.locker_size.replace("_", " ")}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge>{structure.customer_category.replace("_", " ")}</Badge>
                    </TableCell>
                    <TableCell className="font-medium">
                      ₹{structure.base_rent_annual.toLocaleString()}
                    </TableCell>
                    <TableCell>
                      ₹{structure.security_deposit_amount.toLocaleString()}
                    </TableCell>
                    <TableCell>
                      {structure.gst_applicable ? `${structure.gst_rate}%` : "N/A"}
                    </TableCell>
                    <TableCell>
                      {structure.late_payment_penalty_applicable
                        ? `${structure.late_payment_penalty_percentage}%`
                        : "N/A"}
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={structure.is_active ? "default" : "secondary"}
                      >
                        {structure.is_active ? "Active" : "Inactive"}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {format(new Date(structure.effective_from), "dd MMM yyyy")}
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        <Button variant="ghost" size="sm">
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="sm">
                          <Edit className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Rent Calculator Dialog */}
      <Dialog open={showCalculator} onOpenChange={setShowCalculator}>
        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle>Rent Calculator</DialogTitle>
            <DialogDescription>
              Calculate rent with GST, discounts, and penalties
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-6 md:grid-cols-2">
            {/* Input Form */}
            <div className="space-y-4">
              <h3 className="font-semibold">Parameters</h3>

              <div className="space-y-2">
                <Label>Locker Size *</Label>
                <Select
                  value={calcForm.locker_size}
                  onValueChange={(value) =>
                    setCalcForm({ ...calcForm, locker_size: value as LockerSize })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value={LockerSize.SMALL}>Small</SelectItem>
                    <SelectItem value={LockerSize.MEDIUM}>Medium</SelectItem>
                    <SelectItem value={LockerSize.LARGE}>Large</SelectItem>
                    <SelectItem value={LockerSize.EXTRA_LARGE}>
                      Extra Large
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Customer Category *</Label>
                <Select
                  value={calcForm.customer_category}
                  onValueChange={(value) =>
                    setCalcForm({
                      ...calcForm,
                      customer_category: value as CustomerCategory,
                    })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value={CustomerCategory.REGULAR}>Regular</SelectItem>
                    <SelectItem value={CustomerCategory.PREMIUM}>Premium</SelectItem>
                    <SelectItem value={CustomerCategory.SENIOR_CITIZEN}>
                      Senior Citizen
                    </SelectItem>
                    <SelectItem value={CustomerCategory.STAFF}>Staff</SelectItem>
                    <SelectItem value={CustomerCategory.VIP}>VIP</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Rent Frequency *</Label>
                <Select
                  value={calcForm.rent_frequency}
                  onValueChange={(value) =>
                    setCalcForm({ ...calcForm, rent_frequency: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="annual">Annual</SelectItem>
                    <SelectItem value="semi_annual">Semi-Annual</SelectItem>
                    <SelectItem value="quarterly">Quarterly</SelectItem>
                    <SelectItem value="monthly">Monthly</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label>Period From *</Label>
                  <Input
                    type="date"
                    value={calcForm.period_from}
                    onChange={(e) =>
                      setCalcForm({ ...calcForm, period_from: e.target.value })
                    }
                  />
                </div>

                <div className="space-y-2">
                  <Label>Period To *</Label>
                  <Input
                    type="date"
                    value={calcForm.period_to}
                    onChange={(e) =>
                      setCalcForm({ ...calcForm, period_to: e.target.value })
                    }
                  />
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="advance_payment"
                  checked={calcForm.advance_payment}
                  onCheckedChange={(checked) =>
                    setCalcForm({ ...calcForm, advance_payment: !!checked })
                  }
                />
                <Label htmlFor="advance_payment">Advance Payment (Get Discount)</Label>
              </div>

              <Button onClick={handleCalculate} className="w-full">
                <Calculator className="mr-2 h-4 w-4" />
                Calculate Rent
              </Button>
            </div>

            {/* Calculation Result */}
            <div className="space-y-4">
              <h3 className="font-semibold">Calculation Result</h3>

              {calculation?.data ? (
                <div className="space-y-3 border rounded-lg p-4">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Base Rent:</span>
                    <span className="font-medium">
                      ₹{calculation.data.base_rent.toLocaleString()}
                    </span>
                  </div>

                  {calculation.data.location_premium > 0 && (
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Location Premium:</span>
                      <span className="font-medium">
                        ₹{calculation.data.location_premium.toLocaleString()}
                      </span>
                    </div>
                  )}

                  {calculation.data.discount_amount > 0 && (
                    <div className="flex justify-between text-green-600">
                      <span>Discount ({calculation.data.discount_percentage}%):</span>
                      <span>-₹{calculation.data.discount_amount.toLocaleString()}</span>
                    </div>
                  )}

                  <div className="flex justify-between border-t pt-2">
                    <span className="text-muted-foreground">Subtotal:</span>
                    <span className="font-medium">
                      ₹{calculation.data.subtotal.toLocaleString()}
                    </span>
                  </div>

                  <div className="flex justify-between">
                    <span className="text-muted-foreground">
                      GST ({calculation.data.gst_rate}%):
                    </span>
                    <span className="font-medium">
                      ₹{calculation.data.gst_amount.toLocaleString()}
                    </span>
                  </div>

                  <div className="flex justify-between font-bold text-lg border-t pt-2">
                    <span>Total Rent:</span>
                    <span>₹{calculation.data.total_amount.toLocaleString()}</span>
                  </div>

                  <div className="flex justify-between border-t pt-2">
                    <span className="text-muted-foreground">Security Deposit:</span>
                    <span className="font-medium">
                      ₹{calculation.data.security_deposit.toLocaleString()}
                    </span>
                  </div>

                  <div className="flex justify-between font-bold text-xl border-t pt-2 text-blue-600">
                    <span>Total Payable:</span>
                    <span>₹{calculation.data.total_payable.toLocaleString()}</span>
                  </div>

                  <div className="text-sm text-muted-foreground border-t pt-2">
                    Period: {calculation.data.period_months} months ({" "}
                    {calculation.data.rent_frequency})
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <Calculator className="mx-auto h-12 w-12 mb-4 opacity-50" />
                  <p>Click calculate to see results</p>
                </div>
              )}
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Create Structure Dialog - Simplified version */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Create Rent Structure</DialogTitle>
            <DialogDescription>
              Configure rent pricing for locker category
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handleCreateSubmit} className="space-y-6">
            {/* Basic Configuration */}
            <div className="space-y-4">
              <h3 className="font-semibold">Basic Configuration</h3>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label>Locker Size *</Label>
                  <Select
                    value={structureForm.locker_size}
                    onValueChange={(value) =>
                      setStructureForm({
                        ...structureForm,
                        locker_size: value as LockerSize,
                      })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value={LockerSize.SMALL}>Small</SelectItem>
                      <SelectItem value={LockerSize.MEDIUM}>Medium</SelectItem>
                      <SelectItem value={LockerSize.LARGE}>Large</SelectItem>
                      <SelectItem value={LockerSize.EXTRA_LARGE}>
                        Extra Large
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Customer Category *</Label>
                  <Select
                    value={structureForm.customer_category}
                    onValueChange={(value) =>
                      setStructureForm({
                        ...structureForm,
                        customer_category: value as CustomerCategory,
                      })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value={CustomerCategory.REGULAR}>Regular</SelectItem>
                      <SelectItem value={CustomerCategory.PREMIUM}>Premium</SelectItem>
                      <SelectItem value={CustomerCategory.SENIOR_CITIZEN}>
                        Senior Citizen
                      </SelectItem>
                      <SelectItem value={CustomerCategory.STAFF}>Staff</SelectItem>
                      <SelectItem value={CustomerCategory.VIP}>VIP</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Annual Rent *</Label>
                  <Input
                    type="number"
                    step="0.01"
                    value={structureForm.base_rent_annual}
                    onChange={(e) =>
                      setStructureForm({
                        ...structureForm,
                        base_rent_annual: e.target.value,
                      })
                    }
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label>Security Deposit *</Label>
                  <Input
                    type="number"
                    step="0.01"
                    value={structureForm.security_deposit_amount}
                    onChange={(e) =>
                      setStructureForm({
                        ...structureForm,
                        security_deposit_amount: e.target.value,
                      })
                    }
                    required
                  />
                </div>
              </div>
            </div>

            {/* GST Configuration */}
            <div className="space-y-4">
              <h3 className="font-semibold">GST Configuration</h3>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="gst_applicable"
                    checked={structureForm.gst_applicable}
                    onCheckedChange={(checked) =>
                      setStructureForm({
                        ...structureForm,
                        gst_applicable: !!checked,
                      })
                    }
                  />
                  <Label htmlFor="gst_applicable">GST Applicable</Label>
                </div>

                <div className="space-y-2">
                  <Label>GST Rate (%)</Label>
                  <Input
                    type="number"
                    step="0.01"
                    value={structureForm.gst_rate}
                    onChange={(e) =>
                      setStructureForm({ ...structureForm, gst_rate: e.target.value })
                    }
                  />
                </div>
              </div>
            </div>

            {/* Penalty Configuration */}
            <div className="space-y-4">
              <h3 className="font-semibold">Late Payment Penalty</h3>
              <div className="grid gap-4 md:grid-cols-3">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="penalty_applicable"
                    checked={structureForm.late_payment_penalty_applicable}
                    onCheckedChange={(checked) =>
                      setStructureForm({
                        ...structureForm,
                        late_payment_penalty_applicable: !!checked,
                      })
                    }
                  />
                  <Label htmlFor="penalty_applicable">Penalty Applicable</Label>
                </div>

                <div className="space-y-2">
                  <Label>Grace Days</Label>
                  <Input
                    type="number"
                    value={structureForm.late_payment_grace_days}
                    onChange={(e) =>
                      setStructureForm({
                        ...structureForm,
                        late_payment_grace_days: e.target.value,
                      })
                    }
                  />
                </div>

                <div className="space-y-2">
                  <Label>Penalty Rate (%)</Label>
                  <Input
                    type="number"
                    step="0.01"
                    value={structureForm.late_payment_penalty_percentage}
                    onChange={(e) =>
                      setStructureForm({
                        ...structureForm,
                        late_payment_penalty_percentage: e.target.value,
                      })
                    }
                  />
                </div>
              </div>
            </div>

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => setShowCreateDialog(false)}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={createStructure.isPending}>
                {createStructure.isPending ? "Creating..." : "Create Structure"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
