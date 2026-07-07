"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { DollarSign, TrendingUp, TrendingDown, Activity, Plus } from "lucide-react";
import Link from "next/link";
import { cashTransactionService, counterService } from "@/services/branchService";
import type { CashTransaction, BranchCounter } from "@/types/branch";
import { TransactionType } from "@/types/branch";
import { format } from "date-fns";

export default function CashManagementPage() {
  const [transactions, setTransactions] = useState<CashTransaction[]>([]);
  const [counters, setCounters] = useState<BranchCounter[]>([]);
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState({
    totalReceipts: 0,
    totalPayments: 0,
    netCashFlow: 0,
    transactionCount: 0,
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [txnData, counterData] = await Promise.all([
        cashTransactionService.list({ limit: 50 }),
        counterService.list({}),
      ]);
      setTransactions(txnData.items);
      setCounters(counterData);

      // Calculate summary
      const receipts = txnData.items
        .filter((t) => t.transaction_type === TransactionType.CASH_RECEIPT)
        .reduce((sum, t) => sum + t.amount, 0);
      const payments = txnData.items
        .filter((t) => t.transaction_type === TransactionType.CASH_PAYMENT)
        .reduce((sum, t) => sum + t.amount, 0);

      setSummary({
        totalReceipts: receipts,
        totalPayments: payments,
        netCashFlow: receipts - payments,
        transactionCount: txnData.items.length,
      });
    } catch (error) {
      console.error("Failed to load data:", error);
    } finally {
      setLoading(false);
    }
  };

  const getTransactionTypeColor = (type: TransactionType) => {
    switch (type) {
      case TransactionType.CASH_RECEIPT:
      case TransactionType.BANK_DEPOSIT:
        return "bg-green-500";
      case TransactionType.CASH_PAYMENT:
      case TransactionType.BANK_WITHDRAWAL:
        return "bg-red-500";
      default:
        return "bg-blue-500";
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Cash Management</h1>
          <p className="text-muted-foreground">
            Track cash transactions, positions, and denominations
          </p>
        </div>
        <Link href="/branch/cash-management/new-transaction">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            New Transaction
          </Button>
        </Link>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Receipts</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ₹{summary.totalReceipts.toLocaleString("en-IN")}
            </div>
            <p className="text-xs text-muted-foreground">Today</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Payments</CardTitle>
            <TrendingDown className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ₹{summary.totalPayments.toLocaleString("en-IN")}
            </div>
            <p className="text-xs text-muted-foreground">Today</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Net Cash Flow</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ₹{summary.netCashFlow.toLocaleString("en-IN")}
            </div>
            <p className="text-xs text-muted-foreground">Today</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Transactions</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summary.transactionCount}</div>
            <p className="text-xs text-muted-foreground">Today</p>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="transactions" className="space-y-4">
        <TabsList>
          <TabsTrigger value="transactions">Transactions</TabsTrigger>
          <TabsTrigger value="counters">Counters</TabsTrigger>
          <TabsTrigger value="position">Cash Position</TabsTrigger>
        </TabsList>

        <TabsContent value="transactions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recent Transactions</CardTitle>
              <CardDescription>Latest cash transactions across all branches</CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-8">Loading...</div>
              ) : transactions.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  No transactions found
                </div>
              ) : (
                <div className="space-y-2">
                  {transactions.map((txn) => (
                    <div
                      key={txn.id}
                      className="flex items-center justify-between p-4 border rounded-lg"
                    >
                      <div className="flex items-center gap-4">
                        <Badge className={getTransactionTypeColor(txn.transaction_type)}>
                          {txn.transaction_type.replace("_", " ")}
                        </Badge>
                        <div>
                          <p className="font-semibold">{txn.transaction_number}</p>
                          <p className="text-sm text-muted-foreground">
                            {format(new Date(txn.transaction_date), "PPpp")}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-lg font-bold">
                          ₹{txn.amount.toLocaleString("en-IN")}
                        </p>
                        <p className="text-sm text-muted-foreground">{txn.narration}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="counters" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Branch Counters</CardTitle>
              <CardDescription>Status of all counters</CardDescription>
            </CardHeader>
            <CardContent>
              {counters.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  No counters configured
                </div>
              ) : (
                <div className="grid gap-4 md:grid-cols-2">
                  {counters.map((counter) => (
                    <Card key={counter.id}>
                      <CardHeader>
                        <div className="flex justify-between items-start">
                          <div>
                            <CardTitle className="text-base">
                              {counter.counter_name}
                            </CardTitle>
                            <CardDescription>{counter.counter_number}</CardDescription>
                          </div>
                          <Badge variant={counter.is_open ? "default" : "secondary"}>
                            {counter.is_open ? "Open" : "Closed"}
                          </Badge>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Current Balance:</span>
                            <span className="font-semibold">
                              ₹{counter.current_balance.toLocaleString("en-IN")}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Transactions:</span>
                            <span>{counter.transaction_count}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Assigned To:</span>
                            <span>{counter.assigned_user_name || "Unassigned"}</span>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="position" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Cash Position</CardTitle>
              <CardDescription>Real-time cash position across branches</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-muted-foreground">
                Cash position tracking available
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
