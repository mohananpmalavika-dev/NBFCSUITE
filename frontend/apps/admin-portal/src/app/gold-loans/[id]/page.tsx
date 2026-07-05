'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Skeleton } from '@/components/ui/skeleton';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import {
  getGoldLoan,
  recordPayment,
  createReleaseRequest,
  type GoldLoanAccount,
  type GoldOrnament
} from '@/services/gold-loan.service';
import { formatCurrency, formatDate } from '@/lib/utils';

export default function GoldLoanDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { toast } = useToast();
  const loanId = params.id as string;

  const [loan, setLoan] = useState<GoldLoanAccount | null>(null);
  const [ornaments, setOrnaments] = useState<GoldOrnament[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('details');

  // Payment form state
  const [paymentAmount, setPaymentAmount] = useState('');
  const [paymentMode, setPaymentMode] = useState('Cash');
  const [paymentReference, setPaymentReference] = useState('');
  const [processingPayment, setProcessingPayment] = useState(false);

  useEffect(() => {
    loadLoanDetails();
  }, [loanId]);

  const loadLoanDetails = async () => {
    try {
      setLoading(true);
      const data = await getGoldLoan(loanId);
      if (data) {
        setLoan(data.loan);
        setOrnaments(data.ornaments);
      }
    } catch (error) {
      console.error('Failed to load gold loan:', error);
      toast({
        title: 'Error',
        description: 'Failed to load gold loan details',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const handlePayment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!loan) return;

    try {
      setProcessingPayment(true);
      const amount = parseFloat(paymentAmount);
      
      await recordPayment(loanId, {
        transaction_type: 'Payment',
        amount,
        principal_amount: amount,
        interest_amount: 0,
        penal_interest_amount: 0,
        charges_amount: 0,
        payment_mode: paymentMode,
        payment_reference: paymentReference
      });

      toast({
        title: 'Success',
        description: 'Payment recorded successfully'
      });

      // Reload loan details
      await loadLoanDetails();
      
      // Reset form
      setPaymentAmount('');
      setPaymentReference('');
      
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to record payment',
        variant: 'destructive'
      });
    } finally {
      setProcessingPayment(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, 'default' | 'success' | 'warning' | 'error'> = {
      'Active': 'success',
      'Overdue': 'warning',
      'NPA': 'error',
      'Closed': 'default',
      'Foreclosed': 'error'
    };
    return <Badge variant={variants[status] || 'default'}>{status}</Badge>;
  };

  if (loading || !loan) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-12 w-64" />
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
        <Skeleton className="h-96" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <div className="flex items-center gap-4 mb-2">
            <Link href="/gold-loans">
              <Button variant="ghost" size="sm">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                Back
              </Button>
            </Link>
            <h1 className="text-3xl font-bold">{loan.loan_account_number}</h1>
            {getStatusBadge(loan.status)}
            {loan.is_npa && <Badge variant="error">NPA</Badge>}
          </div>
          <p className="text-muted-foreground">
            Created on {formatDate(loan.application_date)}
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Download Statement
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-sm text-muted-foreground">Loan Amount</div>
            <div className="text-2xl font-bold">{formatCurrency(loan.sanctioned_amount)}</div>
            <div className="text-sm text-blue-600 mt-1">
              Disbursed: {formatCurrency(loan.disbursed_amount)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-sm text-muted-foreground">Total Outstanding</div>
            <div className="text-2xl font-bold">{formatCurrency(loan.total_outstanding)}</div>
            <div className="text-sm text-orange-600 mt-1">
              Principal: {formatCurrency(loan.principal_outstanding)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-sm text-muted-foreground">Gold Weight</div>
            <div className="text-2xl font-bold">{loan.total_gold_weight_grams.toFixed(2)}g</div>
            <div className="text-sm text-yellow-600 mt-1">
              Value: {formatCurrency(loan.total_gold_value)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-sm text-muted-foreground">LTV Ratio</div>
            <div className="text-2xl font-bold">{loan.ltv_ratio.toFixed(1)}%</div>
            <div className="text-sm text-green-600 mt-1">
              Rate: {loan.interest_rate.toFixed(2)}% p.a.
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="details">Loan Details</TabsTrigger>
          <TabsTrigger value="ornaments">Gold Ornaments ({ornaments.length})</TabsTrigger>
          <TabsTrigger value="payments">Payments</TabsTrigger>
          <TabsTrigger value="releases">Release Requests</TabsTrigger>
        </TabsList>

        {/* Loan Details Tab */}
        <TabsContent value="details">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Loan Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-muted-foreground">Account Number</Label>
                    <div className="font-medium">{loan.loan_account_number}</div>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Customer ID</Label>
                    <div className="font-medium">{loan.customer_id}</div>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Sanctioned Amount</Label>
                    <div className="font-medium">{formatCurrency(loan.sanctioned_amount)}</div>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Disbursed Amount</Label>
                    <div className="font-medium">{formatCurrency(loan.disbursed_amount)}</div>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Interest Rate</Label>
                    <div className="font-medium">{loan.interest_rate.toFixed(2)}% p.a.</div>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Tenure</Label>
                    <div className="font-medium">{loan.tenure_months} months</div>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Start Date</Label>
                    <div className="font-medium">{formatDate(loan.start_date)}</div>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Maturity Date</Label>
                    <div className="font-medium">{formatDate(loan.maturity_date)}</div>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Repayment Frequency</Label>
                    <div className="font-medium">{loan.repayment_frequency}</div>
                  </div>
                  {loan.emi_amount && (
                    <div>
                      <Label className="text-muted-foreground">EMI Amount</Label>
                      <div className="font-medium">{formatCurrency(loan.emi_amount)}</div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Outstanding Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex justify-between items-center pb-2 border-b">
                    <span className="text-muted-foreground">Principal Outstanding</span>
                    <span className="font-medium">{formatCurrency(loan.principal_outstanding)}</span>
                  </div>
                  <div className="flex justify-between items-center pb-2 border-b">
                    <span className="text-muted-foreground">Interest Outstanding</span>
                    <span className="font-medium">{formatCurrency(loan.interest_outstanding)}</span>
                  </div>
                  <div className="flex justify-between items-center pb-2 border-b">
                    <span className="text-muted-foreground">Penal Interest</span>
                    <span className="font-medium text-red-600">
                      {formatCurrency(loan.penal_interest_outstanding)}
                    </span>
                  </div>
                  <div className="flex justify-between items-center pt-2">
                    <span className="font-semibold">Total Outstanding</span>
                    <span className="text-xl font-bold">{formatCurrency(loan.total_outstanding)}</span>
                  </div>
                </div>

                {loan.days_past_due > 0 && (
                  <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
                    <div className="flex items-center gap-2 text-red-800">
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                      </svg>
                      <span className="font-medium">Overdue: {loan.days_past_due} days</span>
                    </div>
                    <div className="mt-1 text-sm text-red-700">
                      Overdue Amount: {formatCurrency(loan.overdue_amount)}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Gold Ornaments Tab */}
        <TabsContent value="ornaments">
          <Card>
            <CardHeader>
              <CardTitle>Pledged Gold Ornaments</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-muted/50">
                    <tr>
                      <th className="text-left p-4 font-medium">Item #</th>
                      <th className="text-left p-4 font-medium">Type</th>
                      <th className="text-left p-4 font-medium">Description</th>
                      <th className="text-center p-4 font-medium">Purity</th>
                      <th className="text-right p-4 font-medium">Gross Weight</th>
                      <th className="text-right p-4 font-medium">Net Weight</th>
                      <th className="text-right p-4 font-medium">Rate/g</th>
                      <th className="text-right p-4 font-medium">Value</th>
                      <th className="text-center p-4 font-medium">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {ornaments.map((ornament) => (
                      <tr key={ornament.id} className="hover:bg-muted/50">
                        <td className="p-4">{ornament.item_number}</td>
                        <td className="p-4 font-medium">{ornament.ornament_type}</td>
                        <td className="p-4 text-sm">{ornament.ornament_description || '-'}</td>
                        <td className="p-4 text-center">
                          <Badge variant="warning">{ornament.purity_karat}K</Badge>
                        </td>
                        <td className="p-4 text-right">{ornament.gross_weight_grams.toFixed(3)}g</td>
                        <td className="p-4 text-right font-medium">{ornament.net_weight_grams.toFixed(3)}g</td>
                        <td className="p-4 text-right">₹{ornament.gold_rate_per_gram.toFixed(0)}</td>
                        <td className="p-4 text-right font-medium">{formatCurrency(ornament.appraised_value)}</td>
                        <td className="p-4 text-center">
                          <Badge variant={ornament.status === 'Pledged' ? 'success' : 'default'}>
                            {ornament.status}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                  <tfoot className="bg-muted/50 font-bold">
                    <tr>
                      <td colSpan={5} className="p-4 text-right">Total:</td>
                      <td className="p-4 text-right">{loan.total_gold_weight_grams.toFixed(3)}g</td>
                      <td className="p-4 text-right">₹{loan.average_gold_rate.toFixed(0)}</td>
                      <td className="p-4 text-right">{formatCurrency(loan.total_gold_value)}</td>
                      <td></td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Payments Tab */}
        <TabsContent value="payments">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card className="lg:col-span-1">
              <CardHeader>
                <CardTitle>Record Payment</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handlePayment} className="space-y-4">
                  <div>
                    <Label htmlFor="amount">Payment Amount</Label>
                    <Input
                      id="amount"
                      type="number"
                      step="0.01"
                      value={paymentAmount}
                      onChange={(e) => setPaymentAmount(e.target.value)}
                      placeholder="Enter amount"
                      required
                    />
                    <p className="text-sm text-muted-foreground mt-1">
                      Outstanding: {formatCurrency(loan.total_outstanding)}
                    </p>
                  </div>

                  <div>
                    <Label htmlFor="mode">Payment Mode</Label>
                    <select
                      id="mode"
                      value={paymentMode}
                      onChange={(e) => setPaymentMode(e.target.value)}
                      className="w-full px-3 py-2 border rounded-md"
                    >
                      <option value="Cash">Cash</option>
                      <option value="Cheque">Cheque</option>
                      <option value="NEFT">NEFT</option>
                      <option value="RTGS">RTGS</option>
                      <option value="UPI">UPI</option>
                    </select>
                  </div>

                  <div>
                    <Label htmlFor="reference">Reference Number (Optional)</Label>
                    <Input
                      id="reference"
                      value={paymentReference}
                      onChange={(e) => setPaymentReference(e.target.value)}
                      placeholder="Cheque/Transaction number"
                    />
                  </div>

                  <Button type="submit" className="w-full" disabled={processingPayment}>
                    {processingPayment ? 'Processing...' : 'Record Payment'}
                  </Button>
                </form>
              </CardContent>
            </Card>

            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>Payment History</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center py-12 text-muted-foreground">
                  <svg className="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <p>Payment history will be displayed here</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Release Requests Tab */}
        <TabsContent value="releases">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <CardTitle>Release Requests</CardTitle>
                <Button>
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  New Release Request
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12 text-muted-foreground">
                <svg className="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                </svg>
                <p>No release requests yet</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
