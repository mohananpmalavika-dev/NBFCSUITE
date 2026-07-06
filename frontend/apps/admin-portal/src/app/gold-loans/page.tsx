'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
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
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, [page, statusFilter]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Load loans
      const loansData = await getGoldLoans({
        page,
        page_size: 20,
        status: statusFilter || undefined,
        search: searchTerm || undefined
      });
      
      if (loansData) {
        setLoans(loansData.loans || []);
        setTotalPages(loansData.total_pages || 1);
      }

      // Load statistics
      const statsData = await getGoldLoanStatistics();
      
      if (statsData) {
        setStatistics(statsData);
      }
      
    } catch (error: any) {
      console.error('Failed to load gold loans:', error);
      
      // Check if it's a network/database error
      if (error.code === 'ERR_NETWORK' || error.message?.includes('Network Error')) {
        setError('Cannot connect to the server. Please check if the backend is running.');
      } else if (error.response?.status === 500) {
        setError('Database connection error. Please ensure PostgreSQL is running or configure a cloud database.');
      } else {
        setError(error.response?.data?.error?.message || 'Failed to load gold loans data. Please try again.');
      }
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
    <DashboardLayout>
      <div className="space-y-6">
        {/* Error Alert */}
        {error && (
          <Card className="border-red-200 bg-red-50">
            <CardContent className="pt-6">
              <div className="flex items-start gap-3">
                <svg className="w-6 h-6 text-red-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div className="flex-1">
                  <h3 className="text-red-800 font-medium mb-1">Connection Error</h3>
                  <p className="text-red-700 text-sm mb-3">{error}</p>
                  <div className="text-xs text-red-600 bg-red-100 p-3 rounded border border-red-200">
                    <p className="font-medium mb-1">To fix this:</p>
                    <ol className="list-decimal list-inside space-y-1">
                      <li>Set up a free PostgreSQL database (Render.com, Railway.app, or Supabase.com)</li>
                      <li>Update DATABASE_URL in backend/.env file</li>
                      <li>Restart the backend server</li>
                    </ol>
                  </div>
                </div>
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => {
                    setError(null);
                    loadData();
                  }}
                  className="border-red-300 text-red-700 hover:bg-red-100"
                >
                  Retry
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
        
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

      {/* Quick Access Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Link href="/gold-loans/gold-rates">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer border-yellow-200 bg-gradient-to-br from-yellow-50 to-yellow-100">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-yellow-900">Gold Rates</h3>
                  <p className="text-xs text-yellow-700">Live rates & calculator</p>
                </div>
                <svg className="w-10 h-10 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </CardContent>
          </Card>
        </Link>

        <Link href="/gold-loans/vault-management">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer border-blue-200 bg-gradient-to-br from-blue-50 to-blue-100">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-blue-900">Vault Management</h3>
                  <p className="text-xs text-blue-700">Track & transfer inventory</p>
                </div>
                <svg className="w-10 h-10 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
            </CardContent>
          </Card>
        </Link>

        <Link href="/gold-loans/purity-testing">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer border-green-200 bg-gradient-to-br from-green-50 to-green-100">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-green-900">Purity Testing</h3>
                  <p className="text-xs text-green-700">XRF, Fire Assay & more</p>
                </div>
                <svg className="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
              </div>
            </CardContent>
          </Card>
        </Link>

        <Link href="/gold-loans/appraisals">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer border-purple-200 bg-gradient-to-br from-purple-50 to-purple-100">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-purple-900">Appraisals</h3>
                  <p className="text-xs text-purple-700">Professional valuations</p>
                </div>
                <svg className="w-10 h-10 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
            </CardContent>
          </Card>
        </Link>

        <Link href="/gold-loans/auctions">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer border-red-200 bg-gradient-to-br from-red-50 to-red-100">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-red-900">Auctions</h3>
                  <p className="text-xs text-red-700">Manage bidding & sales</p>
                </div>
                <svg className="w-10 h-10 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" />
                </svg>
              </div>
            </CardContent>
          </Card>
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
    </DashboardLayout>
  );
}
