"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Calendar, FileText, Wallet, User, Clock, TrendingUp } from "lucide-react";
import { useRouter } from "next/navigation";

export default function ESSDashboard() {
  const router = useRouter();
  const [dashboardData, setDashboardData] = useState({
    leaveBalance: 0,
    pendingReimbursements: 0,
    upcomingPayslips: 0,
    pendingApprovals: 0
  });

  useEffect(() => {
    // Fetch dashboard data
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      // TODO: Replace with actual API call
      setDashboardData({
        leaveBalance: 15,
        pendingReimbursements: 3,
        upcomingPayslips: 1,
        pendingApprovals: 2
      });
    } catch (error) {
      console.error("Failed to fetch dashboard data", error);
    }
  };

  const quickActions = [
    {
      title: "Apply Leave",
      description: "Request time off",
      icon: Calendar,
      onClick: () => router.push("/hrms/ess/leaves"),
      color: "text-blue-600"
    },
    {
      title: "View Payslips",
      description: "Access pay statements",
      icon: FileText,
      onClick: () => router.push("/hrms/ess/payslips"),
      color: "text-green-600"
    },
    {
      title: "Submit Reimbursement",
      description: "Claim expenses",
      icon: Wallet,
      onClick: () => router.push("/hrms/ess/reimbursements"),
      color: "text-purple-600"
    },
    {
      title: "Update Profile",
      description: "Edit personal info",
      icon: User,
      onClick: () => router.push("/hrms/ess/profile"),
      color: "text-orange-600"
    }
  ];

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Employee Self Service</h1>
        <p className="text-muted-foreground">
          Manage your HR information and requests
        </p>
      </div>

      {/* Statistics Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Leave Balance</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData.leaveBalance} days</div>
            <p className="text-xs text-muted-foreground">
              Available leave balance
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Reimbursements</CardTitle>
            <Wallet className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData.pendingReimbursements}</div>
            <p className="text-xs text-muted-foreground">
              Awaiting approval
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Recent Payslips</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData.upcomingPayslips}</div>
            <p className="text-xs text-muted-foreground">
              New payslip available
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Actions</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData.pendingApprovals}</div>
            <p className="text-xs text-muted-foreground">
              Items need attention
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>
            Common tasks and operations
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {quickActions.map((action, index) => {
              const Icon = action.icon;
              return (
                <Card key={index} className="cursor-pointer hover:shadow-md transition-shadow" onClick={action.onClick}>
                  <CardContent className="pt-6">
                    <div className="flex flex-col items-center text-center space-y-2">
                      <Icon className={`h-8 w-8 ${action.color}`} />
                      <h3 className="font-semibold">{action.title}</h3>
                      <p className="text-sm text-muted-foreground">{action.description}</p>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>
            Your recent HR transactions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center">
              <Calendar className="h-4 w-4 mr-2 text-blue-600" />
              <div className="flex-1">
                <p className="text-sm font-medium">Leave Application Approved</p>
                <p className="text-xs text-muted-foreground">2 days ago</p>
              </div>
            </div>
            <div className="flex items-center">
              <FileText className="h-4 w-4 mr-2 text-green-600" />
              <div className="flex-1">
                <p className="text-sm font-medium">Payslip Generated</p>
                <p className="text-xs text-muted-foreground">5 days ago</p>
              </div>
            </div>
            <div className="flex items-center">
              <Wallet className="h-4 w-4 mr-2 text-purple-600" />
              <div className="flex-1">
                <p className="text-sm font-medium">Reimbursement Processed</p>
                <p className="text-xs text-muted-foreground">1 week ago</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
