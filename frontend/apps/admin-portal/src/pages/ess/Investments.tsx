"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Plus, TrendingUp, CheckCircle, Clock, XCircle } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

export default function Investments() {
  const [investments, setInvestments] = useState([]);
  const [taxSavings, setTaxSavings] = useState({
    declared: 150000,
    limit: 150000,
    remaining: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchInvestments();
  }, []);

  const fetchInvestments = async () => {
    try {
      setLoading(true);
      // TODO: Replace with actual API call
      setInvestments([
        {
          id: 1,
          section: "80C",
          investment_type: "PPF",
          amount: 50000,
          proof_submitted: true,
          status: "Approved",
          submitted_date: "2026-04-15"
        },
        {
          id: 2,
          section: "80C",
          investment_type: "LIC Premium",
          amount: 75000,
          proof_submitted: true,
          status: "Pending",
          submitted_date: "2026-05-20"
        },
        {
          id: 3,
          section: "80D",
          investment_type: "Health Insurance",
          amount: 25000,
          proof_submitted: false,
          status: "Draft",
          submitted_date: null
        }
      ]);
      setTaxSavings({
        declared: 150000,
        limit: 150000,
        remaining: 0
      });
    } catch (error) {
      console.error("Failed to fetch investments", error);
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
      Draft: TrendingUp
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
          <h1 className="text-3xl font-bold">Tax Investments</h1>
          <p className="text-muted-foreground">
            Declare your tax-saving investments
          </p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Declare Investment
        </Button>
      </div>

      {/* Tax Savings Summary */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Declared</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{formatCurrency(taxSavings.declared)}</div>
            <p className="text-xs text-muted-foreground">
              Investment amount
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Section 80C Limit</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(taxSavings.limit)}</div>
            <p className="text-xs text-muted-foreground">
              Maximum allowed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Remaining</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${taxSavings.remaining > 0 ? 'text-orange-600' : 'text-green-600'}`}>
              {formatCurrency(taxSavings.remaining)}
            </div>
            <p className="text-xs text-muted-foreground">
              {taxSavings.remaining > 0 ? 'Can still declare' : 'Limit reached'}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Investment Declarations */}
      <Card>
        <CardHeader>
          <CardTitle>Investment Declarations</CardTitle>
          <CardDescription>
            Your tax-saving investment declarations
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-muted-foreground">
              Loading...
            </div>
          ) : investments.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No investment declarations found
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Section</TableHead>
                  <TableHead>Investment Type</TableHead>
                  <TableHead>Amount</TableHead>
                  <TableHead>Proof Submitted</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Submitted Date</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {investments.map((investment: any) => (
                  <TableRow key={investment.id}>
                    <TableCell className="font-medium">{investment.section}</TableCell>
                    <TableCell>{investment.investment_type}</TableCell>
                    <TableCell className="font-semibold">{formatCurrency(investment.amount)}</TableCell>
                    <TableCell>
                      {investment.proof_submitted ? (
                        <Badge variant="default" className="flex items-center gap-1 w-fit">
                          <CheckCircle className="h-3 w-3" />
                          Yes
                        </Badge>
                      ) : (
                        <Badge variant="outline" className="flex items-center gap-1 w-fit">
                          <XCircle className="h-3 w-3" />
                          No
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell>{getStatusBadge(investment.status)}</TableCell>
                    <TableCell>
                      {investment.submitted_date 
                        ? new Date(investment.submitted_date).toLocaleDateString()
                        : '-'}
                    </TableCell>
                    <TableCell>
                      <Button variant="ghost" size="sm">
                        Edit
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Information Card */}
      <Card className="border-blue-200 bg-blue-50">
        <CardHeader>
          <CardTitle className="text-blue-900">Tax Saving Tips</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-blue-800">
          <ul className="list-disc list-inside space-y-1">
            <li>Section 80C allows deduction up to ₹1,50,000 for investments like PPF, LIC, ELSS, etc.</li>
            <li>Section 80D allows deduction for health insurance premiums</li>
            <li>Submit proof documents before the deadline to avail tax benefits</li>
            <li>Keep all investment receipts and certificates safe for future reference</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
