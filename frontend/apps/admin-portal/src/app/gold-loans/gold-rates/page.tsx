'use client';

import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import {
  getCurrentGoldRates,
  updateLiveGoldRates,
  createManualGoldRate,
  getGoldRateHistory,
  getGoldRateStatistics,
  calculateGoldValue,
  type GoldRate,
  type GoldRateStatistics
} from '@/services/gold-loan.service';
import { formatCurrency, formatDate, formatDateTime } from '@/lib/utils';

export default function GoldRatesPage() {
  const [currentRate, setCurrentRate] = useState<GoldRate | null>(null);
  const [statistics, setStatistics] = useState<GoldRateStatistics | null>(null);
  const [rateHistory, setRateHistory] = useState<GoldRate[]>([]);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [showManualForm, setShowManualForm] = useState(false);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [error, setError] = useState<string | null>(null);

  // Calculator state
  const [calcWeight, setCalcWeight] = useState('');
  const [calcKarat, setCalcKarat] = useState('22');
  const [calcResult, setCalcResult] = useState<number | null>(null);

  // Manual rate form
  const [manualForm, setManualForm] = useState({
    gold_24k: '',
    gold_22k: '',
    gold_18k: '',
    source: 'Manual',
    remarks: ''
  });

  useEffect(() => {
    loadData();
  }, [page]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [rateData, statsData, historyData] = await Promise.all([
        getCurrentGoldRates(),
        getGoldRateStatistics(),
        getGoldRateHistory({ page, page_size: 20 })
      ]);

      setCurrentRate(rateData);
      setStatistics(statsData);
      setRateHistory(historyData.rates || []);
      setTotalPages(Math.ceil((historyData.total || 0) / 20));
    } catch (error: any) {
      console.error('Failed to load gold rates:', error);
      setError(error.response?.data?.error?.message || 'Failed to load gold rates');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateLiveRates = async (source: string = 'IBJA') => {
    try {
      setUpdating(true);
      setError(null);
      const updatedRate = await updateLiveGoldRates(source);
      setCurrentRate(updatedRate);
      await loadData();
      alert(`Gold rates updated successfully from ${source}`);
    } catch (error: any) {
      console.error('Failed to update rates:', error);
      setError(error.response?.data?.error?.message || 'Failed to update live rates');
    } finally {
      setUpdating(false);
    }
  };

  const handleManualRateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setUpdating(true);
      setError(null);
      await createManualGoldRate({
        gold_24k_per_gram: parseFloat(manualForm.gold_24k),
        gold_22k_per_gram: parseFloat(manualForm.gold_22k),
        gold_18k_per_gram: parseFloat(manualForm.gold_18k),
        source: manualForm.source,
        remarks: manualForm.remarks || undefined
      });
      setShowManualForm(false);
      setManualForm({ gold_24k: '', gold_22k: '', gold_18k: '', source: 'Manual', remarks: '' });
      await loadData();
      alert('Manual gold rate created successfully');
    } catch (error: any) {
      console.error('Failed to create manual rate:', error);
      setError(error.response?.data?.error?.message || 'Failed to create manual rate');
    } finally {
      setUpdating(false);
    }
  };

  const handleCalculate = async () => {
    if (!calcWeight || !calcKarat) return;
    try {
      const result = await calculateGoldValue({
        weight_grams: parseFloat(calcWeight),
        karat: parseInt(calcKarat)
      });
      setCalcResult(result.gold_value);
    } catch (error: any) {
      console.error('Calculation error:', error);
      alert('Failed to calculate gold value');
    }
  };

  const getTrendIcon = (change: number) => {
    if (change > 0) {
      return (
        <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
        </svg>
      );
    } else if (change < 0) {
      return (
        <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
        </svg>
      );
    }
    return null;
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
                  <h3 className="text-red-800 font-medium mb-1">Error</h3>
                  <p className="text-red-700 text-sm">{error}</p>
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
            <h1 className="text-3xl font-bold">Gold Rates Management</h1>
            <p className="text-muted-foreground">Live gold rates, updates, and historical tracking</p>
          </div>
          <div className="flex gap-2">
            <Button
              onClick={() => setShowManualForm(!showManualForm)}
              variant="outline"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              Manual Entry
            </Button>
            <Button
              onClick={() => handleUpdateLiveRates('IBJA')}
              disabled={updating}
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              {updating ? 'Updating...' : 'Update Live Rates'}
            </Button>
          </div>
        </div>

        {/* Manual Rate Entry Form */}
        {showManualForm && (
          <Card>
            <CardHeader>
              <CardTitle>Manual Rate Entry</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleManualRateSubmit} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">24K Gold (₹/gram)</label>
                    <Input
                      type="number"
                      step="0.01"
                      value={manualForm.gold_24k}
                      onChange={(e) => setManualForm({ ...manualForm, gold_24k: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">22K Gold (₹/gram)</label>
                    <Input
                      type="number"
                      step="0.01"
                      value={manualForm.gold_22k}
                      onChange={(e) => setManualForm({ ...manualForm, gold_22k: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">18K Gold (₹/gram)</label>
                    <Input
                      type="number"
                      step="0.01"
                      value={manualForm.gold_18k}
                      onChange={(e) => setManualForm({ ...manualForm, gold_18k: e.target.value })}
                      required
                    />
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Source</label>
                    <Input
                      value={manualForm.source}
                      onChange={(e) => setManualForm({ ...manualForm, source: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Remarks (Optional)</label>
                    <Input
                      value={manualForm.remarks}
                      onChange={(e) => setManualForm({ ...manualForm, remarks: e.target.value })}
                    />
                  </div>
                </div>
                <div className="flex justify-end gap-2">
                  <Button type="button" variant="outline" onClick={() => setShowManualForm(false)}>
                    Cancel
                  </Button>
                  <Button type="submit" disabled={updating}>
                    {updating ? 'Creating...' : 'Create Rate'}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {/* Current Rates */}
        {loading && !currentRate ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[...Array(3)].map((_, i) => (
              <Skeleton key={i} className="h-48" />
            ))}
          </div>
        ) : currentRate ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card className="bg-gradient-to-br from-yellow-50 to-yellow-100 border-yellow-200">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <p className="text-sm text-yellow-800">24 Karat Gold</p>
                    <div className="text-3xl font-bold text-yellow-900">
                      ₹{currentRate.gold_24k_per_gram.toFixed(2)}
                    </div>
                    <p className="text-xs text-yellow-700">per gram</p>
                  </div>
                  <svg className="w-12 h-12 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                {statistics && (
                  <div className="flex items-center gap-2 text-sm">
                    {getTrendIcon(statistics.change_amount)}
                    <span className={statistics.change_amount >= 0 ? 'text-green-600' : 'text-red-600'}>
                      ₹{Math.abs(statistics.change_amount).toFixed(2)} ({statistics.change_percentage.toFixed(2)}%)
                    </span>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-amber-50 to-amber-100 border-amber-200">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <p className="text-sm text-amber-800">22 Karat Gold</p>
                    <div className="text-3xl font-bold text-amber-900">
                      ₹{currentRate.gold_22k_per_gram.toFixed(2)}
                    </div>
                    <p className="text-xs text-amber-700">per gram</p>
                  </div>
                  <svg className="w-12 h-12 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                  </svg>
                </div>
                <Badge variant="default" className="bg-amber-600">Most Common</Badge>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <p className="text-sm text-orange-800">18 Karat Gold</p>
                    <div className="text-3xl font-bold text-orange-900">
                      ₹{currentRate.gold_18k_per_gram.toFixed(2)}
                    </div>
                    <p className="text-xs text-orange-700">per gram</p>
                  </div>
                  <svg className="w-12 h-12 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v13m0-13V6a2 2 0 112 2h-2zm0 0V5.5A2.5 2.5 0 109.5 8H12zm-7 4h14M5 12a2 2 0 110-4h14a2 2 0 110 4M5 12v7a2 2 0 002 2h10a2 2 0 002-2v-7" />
                  </svg>
                </div>
                <div className="text-xs text-orange-700">
                  Updated: {formatDateTime(currentRate.created_at)}
                </div>
              </CardContent>
            </Card>
          </div>
        ) : null}

        {/* Statistics */}
        {statistics && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardContent className="pt-6">
                <p className="text-sm text-muted-foreground mb-1">30-Day High</p>
                <div className="text-2xl font-bold text-green-600">
                  ₹{statistics.highest_rate_30_days.toFixed(2)}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <p className="text-sm text-muted-foreground mb-1">30-Day Low</p>
                <div className="text-2xl font-bold text-red-600">
                  ₹{statistics.lowest_rate_30_days.toFixed(2)}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <p className="text-sm text-muted-foreground mb-1">30-Day Average</p>
                <div className="text-2xl font-bold text-blue-600">
                  ₹{statistics.average_rate_30_days.toFixed(2)}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Gold Value Calculator */}
        <Card>
          <CardHeader>
            <CardTitle>Gold Value Calculator</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Weight (grams)</label>
                <Input
                  type="number"
                  step="0.01"
                  value={calcWeight}
                  onChange={(e) => setCalcWeight(e.target.value)}
                  placeholder="Enter weight"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Karat</label>
                <select
                  value={calcKarat}
                  onChange={(e) => setCalcKarat(e.target.value)}
                  className="w-full px-3 py-2 border rounded-md"
                >
                  <option value="24">24K</option>
                  <option value="22">22K</option>
                  <option value="18">18K</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">&nbsp;</label>
                <Button onClick={handleCalculate} className="w-full">Calculate</Button>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Estimated Value</label>
                <div className="text-2xl font-bold text-green-600">
                  {calcResult !== null ? formatCurrency(calcResult) : '₹0.00'}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Rate History */}
        <Card>
          <CardHeader>
            <CardTitle>Rate History</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-3">
                {[...Array(5)].map((_, i) => (
                  <Skeleton key={i} className="h-16" />
                ))}
              </div>
            ) : rateHistory.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground">
                No rate history available
              </div>
            ) : (
              <>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-muted/50">
                      <tr>
                        <th className="text-left p-4 font-medium">Date & Time</th>
                        <th className="text-left p-4 font-medium">Source</th>
                        <th className="text-right p-4 font-medium">24K Gold</th>
                        <th className="text-right p-4 font-medium">22K Gold</th>
                        <th className="text-right p-4 font-medium">18K Gold</th>
                        <th className="text-center p-4 font-medium">Status</th>
                        <th className="text-left p-4 font-medium">Created By</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {rateHistory.map((rate) => (
                        <tr key={rate.id} className="hover:bg-muted/50">
                          <td className="p-4">
                            <div className="font-medium">{formatDate(rate.rate_date)}</div>
                            <div className="text-sm text-muted-foreground">
                              {formatDateTime(rate.created_at)}
                            </div>
                          </td>
                          <td className="p-4">
                            <Badge variant="outline">{rate.source}</Badge>
                          </td>
                          <td className="p-4 text-right font-medium">
                            ₹{rate.gold_24k_per_gram.toFixed(2)}
                          </td>
                          <td className="p-4 text-right font-medium">
                            ₹{rate.gold_22k_per_gram.toFixed(2)}
                          </td>
                          <td className="p-4 text-right font-medium">
                            ₹{rate.gold_18k_per_gram.toFixed(2)}
                          </td>
                          <td className="p-4 text-center">
                            {rate.is_current ? (
                              <Badge variant="success">Current</Badge>
                            ) : (
                              <Badge variant="secondary">Historical</Badge>
                            )}
                          </td>
                          <td className="p-4 text-sm">{rate.created_by}</td>
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
