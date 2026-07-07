'use client';

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Activity, AlertTriangle, TrendingUp } from 'lucide-react';
import { amlService, type TransactionMonitoring } from '@/services/aml.service';
import { format } from 'date-fns';

export default function TransactionMonitoringPage() {
  const [transactions, setTransactions] = useState<TransactionMonitoring[]>([]);
  const [loading, setLoading] = useState(true);
  const [riskFilter, setRiskFilter] = useState<string>('');

  useEffect(() => {
    loadTransactions();
  }, [riskFilter]);

  const loadTransactions = async () => {
    try {
      setLoading(true);
      const params: any = {};
      if (riskFilter) params.risk_level = riskFilter;
      
      const data = await amlService.getTransactions(params);
      setTransactions(data);
    } catch (error) {
      console.error('Failed to load transactions:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'critical': return 'destructive';
      case 'high': return 'destructive';
      case 'medium': return 'warning';
      case 'low': return 'secondary';
      default: return 'default';
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Transaction Monitoring</h1>
          <p className="text-muted-foreground">Real-time AML transaction monitoring</p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Monitored</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{transactions.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">High Risk</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-500">
              {transactions.filter(t => t.risk_level === 'high' || t.risk_level === 'critical').length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Requires Review</CardTitle>
            <TrendingUp className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-500">
              {transactions.filter(t => t.requires_review).length}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>Monitored Transactions</CardTitle>
            <Select value={riskFilter} onValueChange={setRiskFilter}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="All Risk Levels" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Risk Levels</SelectItem>
                <SelectItem value="critical">Critical</SelectItem>
                <SelectItem value="high">High</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="low">Low</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Transaction ID</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Customer</TableHead>
                  <TableHead>Amount</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Risk Level</TableHead>
                  <TableHead>Risk Score</TableHead>
                  <TableHead>Flags</TableHead>
                  <TableHead>Alerts</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {transactions.map((txn) => (
                  <TableRow key={txn.id}>
                    <TableCell className="font-mono text-sm">{txn.transaction_id}</TableCell>
                    <TableCell>{format(new Date(txn.transaction_date), 'PPp')}</TableCell>
                    <TableCell>
                      <div>
                        <div className="font-medium">{txn.customer_name}</div>
                        {txn.customer_is_pep && (
                          <Badge variant="warning" className="text-xs mt-1">PEP</Badge>
                        )}
                      </div>
                    </TableCell>
                    <TableCell className="font-semibold">
                      ₹{txn.transaction_amount.toLocaleString('en-IN')}
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{txn.transaction_type}</Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant={getRiskColor(txn.risk_level)}>
                        {txn.risk_level.toUpperCase()}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <span className="font-mono">{txn.risk_score.toFixed(2)}</span>
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-col gap-1">
                        {txn.is_cash_transaction && (
                          <Badge variant="secondary" className="text-xs">Cash</Badge>
                        )}
                        {txn.is_cross_border && (
                          <Badge variant="secondary" className="text-xs">Cross-Border</Badge>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      {txn.alerts_generated > 0 && (
                        <Badge variant="destructive">{txn.alerts_generated} Alert(s)</Badge>
                      )}
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
