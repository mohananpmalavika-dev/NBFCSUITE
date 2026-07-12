"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Download, FileText, Eye } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

export default function Payslips() {
  const [payslips, setPayslips] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPayslips();
  }, []);

  const fetchPayslips = async () => {
    try {
      setLoading(true);
      // TODO: Replace with actual API call
      setPayslips([
        {
          id: 1,
          month: "June 2026",
          pay_period: "2026-06",
          gross_salary: 75000,
          net_salary: 65000,
          deductions: 10000,
          status: "Processed",
          generated_date: "2026-07-01"
        },
        {
          id: 2,
          month: "May 2026",
          pay_period: "2026-05",
          gross_salary: 75000,
          net_salary: 65000,
          deductions: 10000,
          status: "Processed",
          generated_date: "2026-06-01"
        },
        {
          id: 3,
          month: "April 2026",
          pay_period: "2026-04",
          gross_salary: 75000,
          net_salary: 65000,
          deductions: 10000,
          status: "Processed",
          generated_date: "2026-05-01"
        }
      ]);
    } catch (error) {
      console.error("Failed to fetch payslips", error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = (payslipId: number) => {
    // TODO: Implement download functionality
    console.log("Download payslip", payslipId);
  };

  const handleView = (payslipId: number) => {
    // TODO: Implement view functionality
    console.log("View payslip", payslipId);
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
          <h1 className="text-3xl font-bold">Payslips</h1>
          <p className="text-muted-foreground">
            View and download your salary statements
          </p>
        </div>
      </div>

      {/* Current Month Payslip */}
      {payslips.length > 0 && (
        <Card className="border-2 border-primary">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Latest Payslip - {(payslips[0] as any).month}</CardTitle>
                <CardDescription>
                  Generated on {new Date((payslips[0] as any).generated_date).toLocaleDateString()}
                </CardDescription>
              </div>
              <Badge variant="default">Latest</Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-3">
              <div>
                <p className="text-sm text-muted-foreground">Gross Salary</p>
                <p className="text-2xl font-bold">{formatCurrency((payslips[0] as any).gross_salary)}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Deductions</p>
                <p className="text-2xl font-bold text-red-600">{formatCurrency((payslips[0] as any).deductions)}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Net Salary</p>
                <p className="text-2xl font-bold text-green-600">{formatCurrency((payslips[0] as any).net_salary)}</p>
              </div>
            </div>
            <div className="flex gap-2 mt-4">
              <Button onClick={() => handleView((payslips[0] as any).id)}>
                <Eye className="h-4 w-4 mr-2" />
                View Details
              </Button>
              <Button variant="outline" onClick={() => handleDownload((payslips[0] as any).id)}>
                <Download className="h-4 w-4 mr-2" />
                Download PDF
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Payslip History */}
      <Card>
        <CardHeader>
          <CardTitle>Payslip History</CardTitle>
          <CardDescription>
            All your previous salary statements
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-muted-foreground">
              Loading...
            </div>
          ) : payslips.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No payslips found
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Month/Year</TableHead>
                  <TableHead>Pay Period</TableHead>
                  <TableHead>Gross Salary</TableHead>
                  <TableHead>Deductions</TableHead>
                  <TableHead>Net Salary</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {payslips.map((payslip: any) => (
                  <TableRow key={payslip.id}>
                    <TableCell className="font-medium">
                      <div className="flex items-center gap-2">
                        <FileText className="h-4 w-4 text-muted-foreground" />
                        {payslip.month}
                      </div>
                    </TableCell>
                    <TableCell>{payslip.pay_period}</TableCell>
                    <TableCell>{formatCurrency(payslip.gross_salary)}</TableCell>
                    <TableCell className="text-red-600">{formatCurrency(payslip.deductions)}</TableCell>
                    <TableCell className="font-semibold text-green-600">{formatCurrency(payslip.net_salary)}</TableCell>
                    <TableCell>
                      <Badge variant="default">{payslip.status}</Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-1">
                        <Button variant="ghost" size="sm" onClick={() => handleView(payslip.id)}>
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="sm" onClick={() => handleDownload(payslip.id)}>
                          <Download className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
