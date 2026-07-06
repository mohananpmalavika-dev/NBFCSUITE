'use client';

import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import {
  createPurityTest,
  bulkTestLoan,
  getPurityTests,
  generatePurityCertificate,
  flagPurityDiscrepancy,
  getPurityTestStatistics,
  type PurityTest,
  type PurityTestStatistics
} from '@/services/gold-loan.service';
import { formatDate, formatDateTime } from '@/lib/utils';

export default function PurityTestingPage() {
  const [tests, setTests] = useState<PurityTest[]>([]);
  const [statistics, setStatistics] = useState<PurityTestStatistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [showTestForm, setShowTestForm] = useState(false);
  const [showBulkForm, setShowBulkForm] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Test form state
  const [testForm, setTestForm] = useState({
    gold_loan_id: '',
    ornament_id: '',
    test_method: 'XRF',
    claimed_purity_karat: '22',
    claimed_purity_percentage: '91.67',
    tested_purity_karat: '22',
    tested_purity_percentage: '',
    equipment_id: '',
    equipment_calibration_date: '',
    tester_name: '',
    tester_license: '',
    lab_name: '',
    remarks: ''
  });

  // Bulk test form
  const [bulkForm, setBulkForm] = useState({
    loan_id: '',
    test_method: 'XRF',
    tester_name: '',
    equipment_id: '',
    tester_license: ''
  });

  useEffect(() => {
    loadData();
  }, [page]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [testsData, statsData] = await Promise.all([
        getPurityTests({ page, page_size: 20 }),
        getPurityTestStatistics()
      ]);
      setTests(testsData.tests || []);
      setTotalPages(Math.ceil((testsData.total || 0) / 20));
      setStatistics(statsData);
    } catch (error: any) {
      console.error('Failed to load purity tests:', error);
      setError(error.response?.data?.error?.message || 'Failed to load purity tests');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTest = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setError(null);
      await createPurityTest({
        gold_loan_id: testForm.gold_loan_id,
        ornament_id: testForm.ornament_id,
        test_method: testForm.test_method,
        claimed_purity_karat: parseFloat(testForm.claimed_purity_karat),
        claimed_purity_percentage: parseFloat(testForm.claimed_purity_percentage),
        tested_purity_karat: parseFloat(testForm.tested_purity_karat),
        tested_purity_percentage: parseFloat(testForm.tested_purity_percentage),
        equipment_id: testForm.equipment_id || undefined,
        equipment_calibration_date: testForm.equipment_calibration_date || undefined,
        tester_name: testForm.tester_name,
        tester_license: testForm.tester_license || undefined,
        lab_name: testForm.lab_name || undefined,
        remarks: testForm.remarks || undefined
      });
      setShowTestForm(false);
      setTestForm({
        gold_loan_id: '',
        ornament_id: '',
        test_method: 'XRF',
        claimed_purity_karat: '22',
        claimed_purity_percentage: '91.67',
        tested_purity_karat: '22',
        tested_purity_percentage: '',
        equipment_id: '',
        equipment_calibration_date: '',
        tester_name: '',
        tester_license: '',
        lab_name: '',
        remarks: ''
      });
      await loadData();
      alert('Purity test created successfully');
    } catch (error: any) {
      console.error('Failed to create test:', error);
      setError(error.response?.data?.error?.message || 'Failed to create purity test');
    }
  };

  const handleBulkTest = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setError(null);
      const result = await bulkTestLoan(bulkForm.loan_id, {
        test_method: bulkForm.test_method,
        tester_name: bulkForm.tester_name,
        equipment_id: bulkForm.equipment_id || undefined,
        tester_license: bulkForm.tester_license || undefined
      });
      setShowBulkForm(false);
      setBulkForm({
        loan_id: '',
        test_method: 'XRF',
        tester_name: '',
        equipment_id: '',
        tester_license: ''
      });
      await loadData();
      alert(`Bulk test completed. ${result.total_tests} tests created.`);
    } catch (error: any) {
      console.error('Failed to bulk test:', error);
      setError(error.response?.data?.error?.message || 'Failed to perform bulk test');
    }
  };

  const handleGenerateCertificate = async (testId: string) => {
    try {
      const result = await generatePurityCertificate(testId);
      alert(`Certificate generated: ${result.certificate_url}`);
      window.open(result.certificate_url, '_blank');
    } catch (error: any) {
      console.error('Failed to generate certificate:', error);
      alert('Failed to generate certificate');
    }
  };

  const handleFlagDiscrepancy = async (testId: string) => {
    const action = prompt('Enter action (Retest/Adjust Value/Reject Ornament):');
    if (!action) return;
    const remarks = prompt('Enter remarks:');
    try {
      await flagPurityDiscrepancy(testId, { action, remarks: remarks || undefined });
      await loadData();
      alert('Discrepancy flagged successfully');
    } catch (error: any) {
      console.error('Failed to flag discrepancy:', error);
      alert('Failed to flag discrepancy');
    }
  };

  const getTestResultBadge = (result: string) => {
    switch (result) {
      case 'Pass':
        return <Badge className="bg-green-600">Pass</Badge>;
      case 'Acceptable Variance':
        return <Badge className="bg-yellow-600">Acceptable Variance</Badge>;
      case 'Fail':
        return <Badge className="bg-red-600">Fail</Badge>;
      case 'Major Discrepancy':
        return <Badge className="bg-red-800">Major Discrepancy</Badge>;
      default:
        return <Badge variant="outline">{result}</Badge>;
    }
  };

  const getTestMethodInfo = (method: string) => {
    const info: Record<string, { variance: string; description: string }> = {
      'XRF': { variance: '±1.0%', description: 'X-Ray Fluorescence' },
      'Touchstone': { variance: '±2.0%', description: 'Traditional Touchstone Test' },
      'Fire Assay': { variance: '±0.5%', description: 'Fire Assay (Most Accurate)' },
      'Acid Test': { variance: '±2.5%', description: 'Acid Testing' },
      'Electronic Tester': { variance: '±1.5%', description: 'Electronic Testing' }
    };
    return info[method] || { variance: 'N/A', description: method };
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
                <Button variant="outline" size="sm" onClick={() => setError(null)} className="border-red-300">
                  Dismiss
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">Purity Testing</h1>
            <p className="text-muted-foreground">Test gold purity, generate certificates, and track results</p>
          </div>
          <div className="flex gap-2">
            <Button onClick={() => setShowBulkForm(true)} variant="outline">
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              Bulk Test
            </Button>
            <Button onClick={() => setShowTestForm(true)}>
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              New Test
            </Button>
          </div>
        </div>

        {/* Statistics */}
        {statistics && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="pt-6">
                <p className="text-sm text-muted-foreground mb-1">Total Tests</p>
                <div className="text-3xl font-bold">{statistics.total_tests}</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <p className="text-sm text-muted-foreground mb-1">Pass Rate</p>
                <div className="text-3xl font-bold text-green-600">
                  {statistics.total_tests > 0 
                    ? ((statistics.pass_count / statistics.total_tests) * 100).toFixed(1)
                    : 0}%
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <p className="text-sm text-muted-foreground mb-1">Failed Tests</p>
                <div className="text-3xl font-bold text-red-600">{statistics.fail_count}</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <p className="text-sm text-muted-foreground mb-1">Avg Variance</p>
                <div className="text-3xl font-bold text-blue-600">
                  {statistics.average_variance.toFixed(2)}%
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Test Form */}
        {showTestForm && (
          <Card className="border-2 border-blue-200">
            <CardHeader>
              <CardTitle>Create Purity Test</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleCreateTest} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Gold Loan ID *</label>
                    <Input
                      value={testForm.gold_loan_id}
                      onChange={(e) => setTestForm({ ...testForm, gold_loan_id: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Ornament ID *</label>
                    <Input
                      value={testForm.ornament_id}
                      onChange={(e) => setTestForm({ ...testForm, ornament_id: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Test Method *</label>
                    <select
                      value={testForm.test_method}
                      onChange={(e) => setTestForm({ ...testForm, test_method: e.target.value })}
                      className="w-full px-3 py-2 border rounded-md"
                      required
                    >
                      <option value="XRF">XRF (±1.0%)</option>
                      <option value="Touchstone">Touchstone (±2.0%)</option>
                      <option value="Fire Assay">Fire Assay (±0.5%)</option>
                      <option value="Acid Test">Acid Test (±2.5%)</option>
                      <option value="Electronic Tester">Electronic Tester (±1.5%)</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Claimed Karat *</label>
                    <select
                      value={testForm.claimed_purity_karat}
                      onChange={(e) => {
                        const karat = e.target.value;
                        const percentage = karat === '24' ? '100' : karat === '22' ? '91.67' : '75';
                        setTestForm({ ...testForm, claimed_purity_karat: karat, claimed_purity_percentage: percentage });
                      }}
                      className="w-full px-3 py-2 border rounded-md"
                      required
                    >
                      <option value="24">24K (100%)</option>
                      <option value="22">22K (91.67%)</option>
                      <option value="18">18K (75%)</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Claimed Purity % *</label>
                    <Input
                      type="number"
                      step="0.01"
                      value={testForm.claimed_purity_percentage}
                      onChange={(e) => setTestForm({ ...testForm, claimed_purity_percentage: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Tested Karat *</label>
                    <Input
                      type="number"
                      step="0.01"
                      value={testForm.tested_purity_karat}
                      onChange={(e) => setTestForm({ ...testForm, tested_purity_karat: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Tested Purity % *</label>
                    <Input
                      type="number"
                      step="0.01"
                      value={testForm.tested_purity_percentage}
                      onChange={(e) => setTestForm({ ...testForm, tested_purity_percentage: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Tester Name *</label>
                    <Input
                      value={testForm.tester_name}
                      onChange={(e) => setTestForm({ ...testForm, tester_name: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Tester License</label>
                    <Input
                      value={testForm.tester_license}
                      onChange={(e) => setTestForm({ ...testForm, tester_license: e.target.value })}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Equipment ID</label>
                    <Input
                      value={testForm.equipment_id}
                      onChange={(e) => setTestForm({ ...testForm, equipment_id: e.target.value })}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Lab Name</label>
                    <Input
                      value={testForm.lab_name}
                      onChange={(e) => setTestForm({ ...testForm, lab_name: e.target.value })}
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Remarks</label>
                  <Input
                    value={testForm.remarks}
                    onChange={(e) => setTestForm({ ...testForm, remarks: e.target.value })}
                  />
                </div>
                <div className="flex justify-end gap-2">
                  <Button type="button" variant="outline" onClick={() => setShowTestForm(false)}>
                    Cancel
                  </Button>
                  <Button type="submit">Create Test</Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {/* Bulk Test Form */}
        {showBulkForm && (
          <Card className="border-2 border-green-200">
            <CardHeader>
              <CardTitle>Bulk Test All Ornaments in Loan</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleBulkTest} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Gold Loan ID *</label>
                    <Input
                      value={bulkForm.loan_id}
                      onChange={(e) => setBulkForm({ ...bulkForm, loan_id: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Test Method *</label>
                    <select
                      value={bulkForm.test_method}
                      onChange={(e) => setBulkForm({ ...bulkForm, test_method: e.target.value })}
                      className="w-full px-3 py-2 border rounded-md"
                      required
                    >
                      <option value="XRF">XRF (±1.0%)</option>
                      <option value="Touchstone">Touchstone (±2.0%)</option>
                      <option value="Fire Assay">Fire Assay (±0.5%)</option>
                      <option value="Acid Test">Acid Test (±2.5%)</option>
                      <option value="Electronic Tester">Electronic Tester (±1.5%)</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Tester Name *</label>
                    <Input
                      value={bulkForm.tester_name}
                      onChange={(e) => setBulkForm({ ...bulkForm, tester_name: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Equipment ID</label>
                    <Input
                      value={bulkForm.equipment_id}
                      onChange={(e) => setBulkForm({ ...bulkForm, equipment_id: e.target.value })}
                    />
                  </div>
                </div>
                <div className="flex justify-end gap-2">
                  <Button type="button" variant="outline" onClick={() => setShowBulkForm(false)}>
                    Cancel
                  </Button>
                  <Button type="submit">Start Bulk Test</Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {/* Test Results Table */}
        <Card>
          <CardHeader>
            <CardTitle>Test Results</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-center py-12">Loading...</div>
            ) : tests.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground">
                No purity tests found
              </div>
            ) : (
              <>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-muted/50">
                      <tr>
                        <th className="text-left p-4 font-medium">Test #</th>
                        <th className="text-left p-4 font-medium">Loan ID</th>
                        <th className="text-left p-4 font-medium">Method</th>
                        <th className="text-left p-4 font-medium">Claimed</th>
                        <th className="text-left p-4 font-medium">Tested</th>
                        <th className="text-left p-4 font-medium">Variance</th>
                        <th className="text-center p-4 font-medium">Result</th>
                        <th className="text-left p-4 font-medium">Tester</th>
                        <th className="text-center p-4 font-medium">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {tests.map((test) => (
                        <tr key={test.id} className="hover:bg-muted/50">
                          <td className="p-4">
                            <div className="font-medium">{test.test_number}</div>
                            <div className="text-xs text-muted-foreground">
                              {formatDate(test.test_date)}
                            </div>
                          </td>
                          <td className="p-4">
                            <div>{test.gold_loan_id}</div>
                            <div className="text-xs text-muted-foreground">{test.ornament_id}</div>
                          </td>
                          <td className="p-4">
                            <Badge variant="outline">{test.test_method}</Badge>
                            <div className="text-xs text-muted-foreground mt-1">
                              {getTestMethodInfo(test.test_method).variance}
                            </div>
                          </td>
                          <td className="p-4">
                            <div>{test.claimed_purity_karat}K</div>
                            <div className="text-xs text-muted-foreground">
                              {test.claimed_purity_percentage.toFixed(2)}%
                            </div>
                          </td>
                          <td className="p-4">
                            <div>{test.tested_purity_karat.toFixed(2)}K</div>
                            <div className="text-xs text-muted-foreground">
                              {test.tested_purity_percentage.toFixed(2)}%
                            </div>
                          </td>
                          <td className="p-4">
                            <span className={
                              Math.abs(test.variance_percentage) <= 1 ? 'text-green-600' :
                              Math.abs(test.variance_percentage) <= 2 ? 'text-yellow-600' :
                              'text-red-600'
                            }>
                              {test.variance_percentage > 0 ? '+' : ''}{test.variance_percentage.toFixed(2)}%
                            </span>
                          </td>
                          <td className="p-4 text-center">
                            {getTestResultBadge(test.test_result)}
                          </td>
                          <td className="p-4">
                            <div className="text-sm">{test.tester_name}</div>
                            {test.lab_name && (
                              <div className="text-xs text-muted-foreground">{test.lab_name}</div>
                            )}
                          </td>
                          <td className="p-4">
                            <div className="flex gap-2 justify-center">
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleGenerateCertificate(test.id)}
                                title="Generate Certificate"
                              >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                </svg>
                              </Button>
                              {test.test_result !== 'Pass' && (
                                <Button
                                  size="sm"
                                  variant="outline"
                                  className="border-red-300 text-red-600"
                                  onClick={() => handleFlagDiscrepancy(test.id)}
                                  title="Flag Discrepancy"
                                >
                                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9" />
                                  </svg>
                                </Button>
                              )}
                            </div>
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
