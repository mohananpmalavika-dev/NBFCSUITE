"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Plus, Building2, Users, TrendingUp, DollarSign, Activity } from "lucide-react";
import Link from "next/link";
import { branchService, performanceService } from "@/services/branchService";
import type { Branch, BranchDashboard } from "@/types/branch";

export default function BranchManagementPage() {
  const [branches, setBranches] = useState<Branch[]>([]);
  const [dashboards, setDashboards] = useState<Record<string, BranchDashboard>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadBranches();
  }, []);

  const loadBranches = async () => {
    try {
      setLoading(true);
      const { items } = await branchService.list({ limit: 10 });
      setBranches(items);

      // Load dashboard for each branch
      const dashboardPromises = items.map((branch) =>
        branchService.getDashboard(branch.id).catch(() => null)
      );
      const dashboardResults = await Promise.all(dashboardPromises);

      const dashboardMap: Record<string, BranchDashboard> = {};
      dashboardResults.forEach((dashboard, index) => {
        if (dashboard) {
          dashboardMap[items[index].id] = dashboard;
        }
      });
      setDashboards(dashboardMap);
    } catch (error) {
      console.error("Failed to load branches:", error);
    } finally {
      setLoading(false);
    }
  };

  const getDayStatusColor = (status: string) => {
    switch (status) {
      case "IN_PROGRESS":
        return "bg-green-500";
      case "COMPLETED":
        return "bg-blue-500";
      case "NOT_STARTED":
        return "bg-gray-500";
      default:
        return "bg-yellow-500";
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Branch & Operations Management</h1>
          <p className="text-muted-foreground">
            Manage organizational hierarchy, branches, and daily operations
          </p>
        </div>
        <div className="flex gap-2">
          <Link href="/branch/organizations">
            <Button variant="outline">
              <Building2 className="mr-2 h-4 w-4" />
              Organizations
            </Button>
          </Link>
          <Link href="/branch/create">
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Create Branch
            </Button>
          </Link>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Branches</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{branches.length}</div>
            <p className="text-xs text-muted-foreground">Active branches</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Day Operations</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {Object.values(dashboards).filter((d) => d.day_status === "IN_PROGRESS").length}
            </div>
            <p className="text-xs text-muted-foreground">In progress today</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Transactions</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {Object.values(dashboards).reduce(
                (sum, d) => sum + d.total_transactions_today,
                0
              )}
            </div>
            <p className="text-xs text-muted-foreground">Across all branches</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Cash Balance</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ₹
              {Object.values(dashboards)
                .reduce((sum, d) => sum + d.cash_balance, 0)
                .toLocaleString("en-IN")}
            </div>
            <p className="text-xs text-muted-foreground">Total cash in hand</p>
          </CardContent>
        </Card>
      </div>

      {/* Branch List */}
      <div className="space-y-4">
        <h2 className="text-2xl font-bold">Branches</h2>

        {loading ? (
          <div className="text-center py-8">Loading branches...</div>
        ) : branches.length === 0 ? (
          <Card>
            <CardContent className="text-center py-8">
              <Building2 className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No branches found</h3>
              <p className="text-muted-foreground mb-4">
                Create your first branch to get started
              </p>
              <Link href="/branch/create">
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  Create Branch
                </Button>
              </Link>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {branches.map((branch) => {
              const dashboard = dashboards[branch.id];
              return (
                <Card key={branch.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle>{branch.branch_name}</CardTitle>
                        <CardDescription>{branch.branch_code}</CardDescription>
                      </div>
                      {dashboard && (
                        <Badge className={getDayStatusColor(dashboard.day_status)}>
                          {dashboard.day_status.replace("_", " ")}
                        </Badge>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">Type</p>
                        <p className="font-medium">{branch.branch_type.replace("_", " ")}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Manager</p>
                        <p className="font-medium truncate">
                          {branch.branch_manager_name || "Not assigned"}
                        </p>
                      </div>
                    </div>

                    {dashboard && (
                      <div className="grid grid-cols-3 gap-2 text-sm border-t pt-4">
                        <div>
                          <p className="text-muted-foreground text-xs">Transactions</p>
                          <p className="font-bold">{dashboard.total_transactions_today}</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground text-xs">Counters</p>
                          <p className="font-bold">{dashboard.active_counters}</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground text-xs">Staff</p>
                          <p className="font-bold">{dashboard.staff_present}</p>
                        </div>
                      </div>
                    )}

                    <div className="flex gap-2">
                      <Link href={`/branch/${branch.id}`} className="flex-1">
                        <Button variant="outline" className="w-full">
                          View Details
                        </Button>
                      </Link>
                      <Link href={`/branch/${branch.id}/operations`} className="flex-1">
                        <Button className="w-full">Operations</Button>
                      </Link>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </div>

      {/* Quick Links */}
      <div className="grid gap-4 md:grid-cols-3">
        <Link href="/branch/day-operations">
          <Card className="hover:bg-accent cursor-pointer transition-colors">
            <CardHeader>
              <CardTitle className="text-lg">Day Operations</CardTitle>
              <CardDescription>Manage day begin/end processes</CardDescription>
            </CardHeader>
          </Card>
        </Link>

        <Link href="/branch/cash-management">
          <Card className="hover:bg-accent cursor-pointer transition-colors">
            <CardHeader>
              <CardTitle className="text-lg">Cash Management</CardTitle>
              <CardDescription>Track cash transactions and positions</CardDescription>
            </CardHeader>
          </Card>
        </Link>

        <Link href="/branch/performance">
          <Card className="hover:bg-accent cursor-pointer transition-colors">
            <CardHeader>
              <CardTitle className="text-lg">Performance Tracking</CardTitle>
              <CardDescription>View branch performance and targets</CardDescription>
            </CardHeader>
          </Card>
        </Link>
      </div>
    </div>
  );
}
