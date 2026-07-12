"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Plus, Wallet, CheckCircle, Clock, XCircle, Upload } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

export default function Reimbursements() {
  const [reimbursements, setReimbursements] = useState([]);
  const [summary, setSummary] = useState({
    total_claimed: 0,
    approved: 0,
    pending: 0,
    rejected: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchReimbursements();
  }, []);

  const fetchReimbursements = async () => {
    try {
      setLoading(true);
      // TODO: Replace with actual API call
      setReimbursements([
        {
          id: 1,
          claim_type: "Travel",
          description: "Client visit - Mumbai",
          amount: 8500,
          claim_date: "2026-07-01",
          status: "Approved",
          approved_amount: 8500,
          receipt_attached: true
        },
        {
          id: 2,
          claim_type: "Medical",
          description: "Health checkup",
          amount: 3500,
          claim_date: "2026-07-05",
          status: "Pending",
          approved_amount: null,
          receipt_attached: true
        },
        {
          id: 3,
          claim_type: "Internet",
          description: "Monthly internet bill",
          amount: 1500,
          claim_date: "2026-07-08",
          status: "Approved",
          approved_amount: 1500,
          receipt_attached: true
        },
        {
          id: 4,
          claim_type: "Travel",
          description: "Local conveyance",
          amount: 2000,
          claim_date: "2026-07-10",
          status: "Rejected",
          approved_amount: 0,
          receipt_attached: false
        }
      ]);
      setSummary({
        total_claimed: 15500,
        approved: 10000,
        pending: 3500,
        rejected: 2000
      });
    } catch (error) {
      console.error("Failed to fetch reimbursements", error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, any> = {
      Approved: "default",
      Pending: "secondary",
      Rejected: "destructive",
      Draft: "outline"
    };
    
    const icons: Record<string, any> = {
      Approved: CheckCircle,
      Pending: Clock,
      Rejected: XCircle,
      Draft: Wallet
    };

    const Icon = icons[status] || Clock;

    return (
      <Badge variant={variants[status] || "secondary"} className="flex items-center gap-1 w-fit">
        <Icon className="h-3 w-3" />
        {status}
      </Badge>
    );
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount);
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Reimbursements</h1>
          <p className="text-muted-foreground">
            Submit and track your expense claims
          </p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          New Claim
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Claimed</CardTitle>
            <Wallet className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(summary.total_claimed)}</div>
            <p className="text-xs text-muted-foreground">
              All claims
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Approved</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{formatCurrency(summary.approved)}</div>
            <p className="text-xs text-muted-foreground">
              Will be paid
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending</CardTitle>
            <Clock className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{formatCurrency(summary.pending)}</div>
            <p className="text-xs text-muted-foreground">
              Under review
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Rejected</CardTitle>
            <XCircle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{formatCurrency(summary.rejected)}</div>
            <p className="text-xs text-muted-foreground">
              Not approved
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Reimbursement Claims */}
      <Card>
        <CardHeader>
          <CardTitle>Reimbursement Claims</CardTitle>
          <CardDescription>
            Your expense claim history
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-muted-foreground">
              Loading...
            </div>
          ) : reimbursements.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No reimbursement claims found
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Claim ID</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Description</TableHead>
                  <TableHead>Claimed Amount</TableHead>
                  <TableHead>Approved Amount</TableHead>
                  <TableHead>Receipt</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {reimbursements.map((claim: any) => (
                  <TableRow key={claim.id}>
                    <TableCell className="font-medium">#{claim.id}</TableCell>
                    <TableCell>{claim.claim_type}</TableCell>
                    <TableCell>{claim.description}</TableCell>
                    <TableCell className="font-semibold">{formatCurrency(claim.amount)}</TableCell>
                    <TableCell>
                      {claim.approved_amount !== null 
                        ? <span className="font-semibold text-green-600">{formatCurrency(claim.approved_amount)}</span>
                        : '-'}
                    </TableCell>
                    <TableCell>
                      {claim.receipt_attached ? (
                        <Badge variant="default" className="flex items-center gap-1 w-fit">
                          <Upload className="h-3 w-3" />
                          Yes
                        </Badge>
                      ) : (
                        <Badge variant="outline" className="flex items-center gap-1 w-fit">
                          <XCircle className="h-3 w-3" />
                          No
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell>{getStatusBadge(claim.status)}</TableCell>
                    <TableCell>{new Date(claim.claim_date).toLocaleDateString()}</TableCell>
                    <TableCell>
                      <Button variant="ghost" size="sm">
                        View
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Guidelines Card */}
      <Card className="border-blue-200 bg-blue-50">
        <CardHeader>
          <CardTitle className="text-blue-900">Reimbursement Guidelines</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-blue-800">
          <ul className="list-disc list-inside space-y-1">
            <li>Attach original receipts/bills for all claims</li>
            <li>Submit claims within 30 days of expense</li>
            <li>Travel claims require prior approval from manager</li>
            <li>Medical reimbursements require prescription and bills</li>
            <li>Internet/phone bills are reimbursed up to ₹1,500/month</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
