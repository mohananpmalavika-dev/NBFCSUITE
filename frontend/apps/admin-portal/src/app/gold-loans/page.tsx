'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import {
  getGoldLoans,
  getGoldLoanStatistics,
  type GoldLoanAccount,
  type GoldLoanStatistics
} from '@/services/gold-loan.service';
import { formatCurrency, formatDate } from '@/lib/utils';

export default function GoldLoansPage() {
  const router = useRouter();
  const [loans, setLoans] = useState<GoldLoanAccount[]>([]);
  const [statistics, setStatistics] = useState<GoldLoanStatistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    loadData();
  }, [page, statusFilter]);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Load loans
      const loansData = await getGoldLoans({
        page,
        page_size: 20,
        status: statusFilter || undefined,
        search: searchTerm || undefined
      });
      
      if (loansData) {
        setLoans(loansData.loans);
        setTotalPages(loansData.total_pages);
      }

      // Load statistics
      const statsData = await getGoldLoanStatistics();
      if (statsData) {
        setStatistics(statsData);
      }
      
    } catch (error) {
      console.error('Failed to load gold loans:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    loadData();
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, 'default' | 'secondary' | 'destructive' | 'outline' | 'success' | 'warning' | 'info'> = {
      'Active': 'success',
      'Overdue': 'warning',
      'NPA': 'destructive',
      'Closed': 'default',
      'Foreclosed': 'destructive',
      'Auctioned': 'destructive'
    };
    return <Badge variant={variants[status] || 'default'}>{status}</Badge>;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Gold Loans</h1>
          <p className="text-muted-foreground">Manage gold loan accounts and ornaments</p>
        </div>
        <Link href="/gold-loans/new">
          <Button size="lg">
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            New Gold Loan
          </Button>
        </Link>
      </div>

      {/* Statistics Cards */}
      {loading && !statistics ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {[...Array(5)].map((_, i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      ) : statistics ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <Card>
            <CardContent className="pt-6">
              <div className="text-2xl font-bold">{statistics.total_loans}</div>
              <p className="text-xs text-muted-foreground">Total Loans</p>
              <div className="text-sm text-green-600 mt-2">
                {statistics.active_loans} Active
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="text-2xl font-bold">
                {formatCurrency(statistics.total_disbursed)}
              </div>
              <p className="text-xs text-muted-foreground">Total Disbursed</p>
              <div className="text-sm text-blue-600 mt-2">
                {formatCurrency(statistics.total_outstanding)} Outstanding
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="text-2xl font-bold">
                {statistics.total_gold_weight_kg.toFixed(2)} kg
              </div>
              <p className="text-xs text-muted-foreground">Total Gold Weight</p>
              <div className="text-sm text-yellow-600 mt-2">
                Avg LTV: {statistics.average_ltv_ratio.toFixed(1)}%
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="text-2xl font-bold">{statistics.npa_count}</div>
              <p className="text-xs text-muted-foreground">NPA Loans</p>
              <div className="text-sm text-red-600 mt-2">
                {formatCurrency(statistics.npa_amount)}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="text-2xl font-bold">{statistics.overdue_count}</div>
              <p className="text-xs text-muted-foreground">Overdue Loans</p>
              <div className="text-sm text-orange-600 mt-2">
                {formatCurrency(statistics.overdue_amount)}
              </div>
            </CardContent>
          </Card>
        </div>
      ) : null}

      {/* Filters and Search */}
      <Card>
        <CardContent className="pt-6">
          <form onSubmit={handleSearch} className="flex gap-4">
            <Input
              placeholder="Search by account number, customer..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="flex-1"
            />
            
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setPage(1);
              }}
              className="px-4 py-2 border rounded-md"
            >
              <option value="">All Status</option>
              <option value="Active">Active</option>
              <option value="Overdue">Overdue</option>
              <option value="NPA">NPA</option>
              <option value="Closed">Closed</option>
              <option value="Foreclosed">Foreclosed</option>
            </select>

            <Button type="submit">Search</Button>
          </form>
        </CardContent>
      </Card>

      {/* Loans Table */}
      <Card>
        <CardHeader>
          <CardTitle>Gold Loan Accounts</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-3">
              {[...Array(5)].map((_, i) => (
                <Skeleton key={i} className="h-20" />
              ))}
            </div>
          ) : loans.length === 0 ? (
            <div className="text-center py-12">
              <svg className="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
              <h3 className="text-lg font-medium mb-2">No Gold Loans Found</h3>
              <p className="text-muted-foreground mb-4">
                Get started by creating a new gold loan account
              </p>
              <Link href="/gold-loans/new">
                <Button>Create Gold Loan</Button>
              </Link>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-muted/50">
                    <tr>
                      <th className="text-left p-4 font-medium">Account Number</th>
                      <th className="text-left p-4 font-medium">Customer</th>
                      <th className="text-right p-4 font-medium">Loan Amount</th>
                      <th className="text-right p-4 font-medium">Outstanding</th>
                      <th className="text-right p-4 font-medium">Gold Weight</th>
                      <th className="text-center p-4 font-medium">LTV</th>
                      <th className="text-center p-4 font-medium">Days Overdue</th>
                      <th className="text-center p-4 font-medium">Status</th>
                      <th className="text-center p-4 font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {loans.map((loan) => (
                      <tr key={loan.id} className="hover:bg-muted/50">
                        <td className="p-4">
                          <div>
                            <div className="font-medium">{loan.loan_account_number}</div>
                            <div className="text-sm text-muted-foreground">
                              {formatDate(loan.application_date)}
                            </div>
                          </div>
                        </td>
                        <td className="p-4">
                          <div className="text-sm">{loan.customer_id}</div>
                        </td>
                        <td className="p-4 text-right">
                          <div className="font-medium">{formatCurrency(loan.sanctioned_amount)}</div>
                          <div className="text-sm text-muted-foreground">
                            Disbursed: {formatCurrency(loan.disbursed_amount)}
                          </div>
                        </td>
                        <td className="p-4 text-right">
                          <div className="font-medium">{formatCurrency(loan.total_outstanding)}</div>
                          {loan.is_npa && (
                            <Badge variant="destructive" className="mt-1">NPA</Badge>
                          )}
                        </td>
                        <td className="p-4 text-right">
                          <div className="font-medium">{loan.total_gold_weight_grams.toFixed(2)}g</div>
                          <div className="text-sm text-muted-foreground">
                            ₹{loan.average_gold_rate.toFixed(0)}/g
                          </div>
                        </td>
                        <td className="p-4 text-center">
                          <Badge variant={loan.ltv_ratio <= 75 ? 'success' : 'warning'}>
                            {loan.ltv_ratio.toFixed(1)}%
                          </Badge>
                        </td>
                        <td className="p-4 text-center">
                          {loan.days_past_due > 0 ? (
                            <span className="text-red-600 font-medium">{loan.days_past_due}</span>
                          ) : (
                            <span className="text-muted-foreground">0</span>
                          )}
                        </td>
                        <td className="p-4 text-center">
                          {getStatusBadge(loan.status)}
                        </td>
                        <td className="p-4 text-center">
                          <Link href={`/gold-loans/${loan.id}`}>
                            <Button variant="outline" size="sm">View</Button>
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex justify-center items-center gap-2 mt-6">
                  <Button
                    variant="outline"
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1}
                  >
                    Previous
                  </Button>
                  <span className="text-sm text-muted-foreground">
                    Page {page} of {totalPages}
                  </span>
                  <Button
                    variant="outline"
                    onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                  >
                    Next
                  </Button>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
