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
import { Textarea } from "@/components/ui/textarea";
import { PlayCircle, StopCircle, Calendar, Clock } from "lucide-react";
import { branchService, dayOperationService } from "@/services/branchService";
import type { Branch, BranchDayOperation } from "@/types/branch";
import { DayStatus } from "@/types/branch";
import { useToast } from "@/components/ui/use-toast";
import { format } from "date-fns";

export default function DayOperationsPage() {
  const [branches, setBranches] = useState<Branch[]>([]);
  const [operations, setOperations] = useState<BranchDayOperation[]>([]);
  const [loading, setLoading] = useState(true);
  const [showBeginDialog, setShowBeginDialog] = useState(false);
  const [showEndDialog, setShowEndDialog] = useState(false);
  const [selectedBranch, setSelectedBranch] = useState<string>("");
  const { toast } = useToast();

  const [beginFormData, setBeginFormData] = useState({
    opening_cash_balance: 0,
    opening_bank_balance: 0,
    remarks: "",
  });

  const [endFormData, setEndFormData] = useState({
    closing_cash_balance: 0,
    closing_bank_balance: 0,
    remarks: "",
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [branchesData, operationsData] = await Promise.all([
        branchService.list({ limit: 100 }),
        dayOperationService.list({ limit: 100 }),
      ]);
      setBranches(branchesData.items);
      setOperations(operationsData.items);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load data",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDayBegin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await dayOperationService.dayBegin({
        branch_id: selectedBranch,
        business_date: new Date().toISOString(),
        opening_cash_balance: beginFormData.opening_cash_balance,
        opening_bank_balance: beginFormData.opening_bank_balance,
        remarks: beginFormData.remarks,
      });

      toast({
        title: "Success",
        description: "Day operations started successfully",
      });
      setShowBeginDialog(false);
      loadData();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.message || "Failed to start day operations",
        variant: "destructive",
      });
    }
  };

  const handleDayEnd = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await dayOperationService.dayEnd({
        branch_id: selectedBranch,
        business_date: new Date().toISOString(),
        closing_cash_balance: endFormData.closing_cash_balance,
        closing_bank_balance: endFormData.closing_bank_balance,
        remarks: endFormData.remarks,
      });

      toast({
        title: "Success",
        description: "Day operations completed successfully",
      });
      setShowEndDialog(false);
      loadData();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.message || "Failed to complete day operations",
        variant: "destructive",
      });
    }
  };

  const getStatusColor = (status: DayStatus) => {
    switch (status) {
      case DayStatus.IN_PROGRESS:
        return "bg-green-500";
      case DayStatus.COMPLETED:
        return "bg-blue-500";
      case DayStatus.NOT_STARTED:
        return "bg-gray-500";
      case DayStatus.SUSPENDED:
        return "bg-red-500";
      default:
        return "bg-gray-500";
    }
  };

  const getTodayOperations = () => {
    const today = format(new Date(), "yyyy-MM-dd");
    return operations.filter(
      (op) => format(new Date(op.business_date), "yyyy-MM-dd") === today
    );
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Day Operations</h1>
          <p className="text-muted-foreground">
            Manage day begin and day end processes for branches
          </p>
        </div>
      </div>


      {/* Quick Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Branches</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{branches.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Not Started</CardTitle>
            <Clock className="h-4 w-4 text-gray-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {getTodayOperations().filter((op) => op.status === DayStatus.NOT_STARTED).length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">In Progress</CardTitle>
            <PlayCircle className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {getTodayOperations().filter((op) => op.status === DayStatus.IN_PROGRESS).length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completed</CardTitle>
            <StopCircle className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {getTodayOperations().filter((op) => op.status === DayStatus.COMPLETED).length}
            </div>
          </CardContent>
        </Card>
      </div>


      {/* Today's Operations */}
      <Card>
        <CardHeader>
          <CardTitle>Today's Operations</CardTitle>
          <CardDescription>
            {format(new Date(), "EEEE, MMMM d, yyyy")}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : (
            <div className="space-y-3">
              {branches.map((branch) => {
                const todayOp = getTodayOperations().find(
                  (op) => op.branch_id === branch.id
                );
                const status = todayOp?.status || DayStatus.NOT_STARTED;

                return (
                  <div
                    key={branch.id}
                    className="flex items-center justify-between p-4 border rounded-lg"
                  >
                    <div className="flex items-center gap-4">
                      <div>
                        <p className="font-semibold">{branch.branch_name}</p>
                        <p className="text-sm text-muted-foreground">{branch.branch_code}</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-4">
                      <Badge className={getStatusColor(status)}>
                        {status.replace("_", " ")}
                      </Badge>

                      {todayOp && (
                        <div className="text-sm text-muted-foreground">
                          {todayOp.transaction_count} transactions • ₹
                          {(todayOp.total_receipts - todayOp.total_payments).toLocaleString(
                            "en-IN"
                          )}
                        </div>
                      )}

                      <div className="flex gap-2">
                        {status === DayStatus.NOT_STARTED && (
                          <Button
                            size="sm"
                            onClick={() => {
                              setSelectedBranch(branch.id);
                              setShowBeginDialog(true);
                            }}
                          >
                            <PlayCircle className="mr-2 h-4 w-4" />
                            Begin Day
                          </Button>
                        )}

                        {status === DayStatus.IN_PROGRESS && (
                          <Button
                            size="sm"
                            variant="destructive"
                            onClick={() => {
                              setSelectedBranch(branch.id);
                              setShowEndDialog(true);
                            }}
                          >
                            <StopCircle className="mr-2 h-4 w-4" />
                            End Day
                          </Button>
                        )}

                        {status === DayStatus.COMPLETED && (
                          <Button size="sm" variant="outline" disabled>
                            Completed
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>


      {/* Day Begin Dialog */}
      <Dialog open={showBeginDialog} onOpenChange={setShowBeginDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Begin Day Operations</DialogTitle>
            <DialogDescription>
              Enter opening balances to start the day
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handleDayBegin} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="opening_cash">Opening Cash Balance (₹) *</Label>
              <Input
                id="opening_cash"
                type="number"
                step="0.01"
                value={beginFormData.opening_cash_balance}
                onChange={(e) =>
                  setBeginFormData({
                    ...beginFormData,
                    opening_cash_balance: Number(e.target.value),
                  })
                }
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="opening_bank">Opening Bank Balance (₹)</Label>
              <Input
                id="opening_bank"
                type="number"
                step="0.01"
                value={beginFormData.opening_bank_balance}
                onChange={(e) =>
                  setBeginFormData({
                    ...beginFormData,
                    opening_bank_balance: Number(e.target.value),
                  })
                }
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="begin_remarks">Remarks</Label>
              <Textarea
                id="begin_remarks"
                value={beginFormData.remarks}
                onChange={(e) =>
                  setBeginFormData({ ...beginFormData, remarks: e.target.value })
                }
                placeholder="Any notes for day begin..."
              />
            </div>

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => setShowBeginDialog(false)}
              >
                Cancel
              </Button>
              <Button type="submit">Begin Day</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Day End Dialog */}
      <Dialog open={showEndDialog} onOpenChange={setShowEndDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>End Day Operations</DialogTitle>
            <DialogDescription>
              Enter closing balances to complete the day
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handleDayEnd} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="closing_cash">Closing Cash Balance (₹) *</Label>
              <Input
                id="closing_cash"
                type="number"
                step="0.01"
                value={endFormData.closing_cash_balance}
                onChange={(e) =>
                  setEndFormData({
                    ...endFormData,
                    closing_cash_balance: Number(e.target.value),
                  })
                }
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="closing_bank">Closing Bank Balance (₹)</Label>
              <Input
                id="closing_bank"
                type="number"
                step="0.01"
                value={endFormData.closing_bank_balance}
                onChange={(e) =>
                  setEndFormData({
                    ...endFormData,
                    closing_bank_balance: Number(e.target.value),
                  })
                }
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="end_remarks">Remarks</Label>
              <Textarea
                id="end_remarks"
                value={endFormData.remarks}
                onChange={(e) =>
                  setEndFormData({ ...endFormData, remarks: e.target.value })
                }
                placeholder="Any notes for day end..."
              />
            </div>

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => setShowEndDialog(false)}
              >
                Cancel
              </Button>
              <Button type="submit">End Day</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
