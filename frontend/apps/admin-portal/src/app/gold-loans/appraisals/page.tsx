'use client';

import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import {
  createAppraisal,
  submitAppraisal,
  verifyAppraisal,
  generateAppraisalCertificate,
  reappraise,
  getAppraisals,
  type AppraisalReport
} from '@/services/gold-loan.service';
import { formatCurrency, formatDate, formatDateTime } from '@/lib/utils';

export default function AppraisalsPage() {
  const [appraisals, setAppraisals] = useState<AppraisalReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [selectedAppraisal, setSelectedAppraisal] = useState<AppraisalReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const [form, setForm] = useState({
    customer_id: '',
    gold_loan_id: '',
    ornament_id: '',
    appraisal_type: 'Initial',
    ornament_type: '',
    ornament_description: '',
    verified_karat: '22',
    purity_percentage: '91.67',
    gross_weight_grams: '',
    net_weight_grams: '',
    condition: 'Excellent',
    condition_notes: '',
    appraiser_name: '',
    appraiser_license: '',
    appraiser_experience_years: '',
    remarks: ''
  });

  useEffect(() => {
    loadAppraisals();
  }, [page]);

  const loadAppraisals = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getAppraisals({ page, page_size: 20 });
      setAppraisals(data.appraisals || []);
      setTotalPages(Math.ceil((data.total || 0) / 20));
    } catch (error: any) {
      console.error('Failed to load appraisals:', error);
      setError(error.response?.data?.error?.message || 'Failed to load appraisals');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAppraisal = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setError(null);
      await createAppraisal({
        customer_id: form.customer_id,
        gold_loan_id: form.gold_loan_id || undefined,
        ornament_id: form.ornament_id || undefined,
        appraisal_type: form.appraisal_type,
        ornament_type: form.ornament_type,
        ornament_description: form.ornament_description || undefined,
        verified_karat: parseFloat(form.verified_karat),
        purity_percentage: parseFloat(form.purity_percentage),
        gross_weight_grams: parseFloat(form.gross_weight_grams),
        net_weight_grams: parseFloat(form.net_weight_grams),
        condition: form.condition,
        condition_notes: form.condition_notes || undefined,
        appraiser_name: form.appraiser_name,
        appraiser_license: form.appraiser_license || undefined,
        appraiser_experience_years: form.appraiser_experience_years ? parseInt(form.appraiser_experience_years) : undefined,
        remarks: form.remarks || undefined
      });
      setShowForm(false);
      await loadAppraisals();
      alert('Appraisal created successfully');
    } catch (error: any) {
      console.error('Failed to create appraisal:', error);
      setError(error.response?.data?.error?.message || 'Failed to create appraisal');
    }
  };

  const handleSubmit = async (id: string) => {
    if (!confirm('Submit this appraisal for verification?')) return;
    try {
      await submitAppraisal(id);
      await loadAppraisals();
      alert('Appraisal submitted for verification');
    } catch (error: any) {
      alert('Failed to submit appraisal');
    }
  };

  const handleVerify = async (id: string, approved: boolean) => {
    const remarks = prompt(approved ? 'Enter approval remarks:' : 'Enter rejection reason:');
    try {
      await verifyAppraisal(id, { approved, remarks: remarks || undefined });
      await loadAppraisals();
      alert(approved ? 'Appraisal approved' : 'Appraisal rejected');
    } catch (error: any) {
      alert('Failed to verify appraisal');
    }
  };

  const handleGenerateCertificate = async (id: string) => {
    try {
      const result = await generateAppraisalCertificate(id);
      window.open(result.certificate_url, '_blank');
    } catch (error: any) {
      alert('Failed to generate certificate');
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'Draft': return <Badge variant="secondary">Draft</Badge>;
      case 'Submitted': return <Badge className="bg-blue-600">Submitted</Badge>;
      case 'Verified': return <Badge className="bg-green-600">Verified</Badge>;
      case 'Approved': return <Badge className="bg-green-700">Approved</Badge>;
      case 'Rejected': return <Badge className="bg-red-600">Rejected</Badge>;
      default: return <Badge variant="outline">{status}</Badge>;
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {error && (
          <Card className="border-red-200 bg-red-50">
            <CardContent className="pt-6">
              <div className="flex items-start gap-3">
                <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div className="flex-1">
                  <h3 className="text-red-800 font-medium">Error</h3>
                  <p className="text-red-700 text-sm">{error}</p>
                </div>
                <Button variant="outline" size="sm" onClick={() => setError(null)}>Dismiss</Button>
              </div>
            </CardContent>
          </Card>
        )}

        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">Appraisal Management</h1>
            <p className="text-muted-foreground">Professional ornament appraisal workflow</p>
          </div>
          <Button onClick={() => setShowForm(true)}>
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            New Appraisal
          </Button>
        </div>

        {showForm && (
          <Card className="border-2 border-blue-200">
            <CardHeader>
              <CardTitle>Create Appraisal Report</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleCreateAppraisal} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Customer ID *</label>
                    <Input value={form.customer_id} onChange={(e) => setForm({ ...form, customer_id: e.target.value })} required />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Gold Loan ID</label>
                    <Input value={form.gold_loan_id} onChange={(e) => setForm({ ...form, gold_loan_id: e.target.value })} />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Ornament Type *</label>
                    <select value={form.ornament_type} onChange={(e) => setForm({ ...form, ornament_type: e.target.value })} className="w-full px-3 py-2 border rounded-md" required>
                      <option value="">Select type...</option>
                      <option value="Necklace">Necklace</option>
                      <option value="Ring">Ring</option>
                      <option value="Bracelet">Bracelet</option>
                      <option value="Earrings">Earrings</option>
                      <option value="Chain">Chain</option>
                      <option value="Bangle">Bangle</option>
                      <option value="Coin">Coin</option>
                      <option value="Bar">Bar</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Appraisal Type *</label>
                    <select value={form.appraisal_type} onChange={(e) => setForm({ ...form, appraisal_type: e.target.value })} className="w-full px-3 py-2 border rounded-md" required>
                      <option value="Initial">Initial</option>
                      <option value="Re-appraisal">Re-appraisal</option>
                      <option value="Pre-auction">Pre-auction</option>
                      <option value="Insurance">Insurance</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Verified Karat *</label>
                    <select value={form.verified_karat} onChange={(e) => setForm({ ...form, verified_karat: e.target.value, purity_percentage: e.target.value === '24' ? '100' : e.target.value === '22' ? '91.67' : '75' })} className="w-full px-3 py-2 border rounded-md" required>
                      <option value="24">24K</option>
                      <option value="22">22K</option>
                      <option value="18">18K</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Purity % *</label>
                    <Input type="number" step="0.01" value={form.purity_percentage} onChange={(e) => setForm({ ...form, purity_percentage: e.target.value })} required />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Gross Weight (g) *</label>
                    <Input type="number" step="0.01" value={form.gross_weight_grams} onChange={(e) => setForm({ ...form, gross_weight_grams: e.target.value })} required />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Net Weight (g) *</label>
                    <Input type="number" step="0.01" value={form.net_weight_grams} onChange={(e) => setForm({ ...form, net_weight_grams: e.target.value })} required />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Condition *</label>
                    <select value={form.condition} onChange={(e) => setForm({ ...form, condition: e.target.value })} className="w-full px-3 py-2 border rounded-md" required>
                      <option value="Excellent">Excellent</option>
                      <option value="Good">Good</option>
                      <option value="Fair">Fair</option>
                      <option value="Poor">Poor</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Appraiser Name *</label>
                    <Input value={form.appraiser_name} onChange={(e) => setForm({ ...form, appraiser_name: e.target.value })} required />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Appraiser License</label>
                    <Input value={form.appraiser_license} onChange={(e) => setForm({ ...form, appraiser_license: e.target.value })} />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Experience (Years)</label>
                    <Input type="number" value={form.appraiser_experience_years} onChange={(e) => setForm({ ...form, appraiser_experience_years: e.target.value })} />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Ornament Description</label>
                  <Input value={form.ornament_description} onChange={(e) => setForm({ ...form, ornament_description: e.target.value })} />
                </div>
                <div className="flex justify-end gap-2">
                  <Button type="button" variant="outline" onClick={() => setShowForm(false)}>Cancel</Button>
                  <Button type="submit">Create Appraisal</Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        <Card>
          <CardHeader>
            <CardTitle>Appraisal Reports</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-center py-12">Loading...</div>
            ) : appraisals.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground">No appraisals found</div>
            ) : (
              <>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-muted/50">
                      <tr>
                        <th className="text-left p-4 font-medium">Appraisal #</th>
                        <th className="text-left p-4 font-medium">Customer/Loan</th>
                        <th className="text-left p-4 font-medium">Ornament</th>
                        <th className="text-left p-4 font-medium">Weight/Purity</th>
                        <th className="text-right p-4 font-medium">Values</th>
                        <th className="text-center p-4 font-medium">Status</th>
                        <th className="text-left p-4 font-medium">Appraiser</th>
                        <th className="text-center p-4 font-medium">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {appraisals.map((appraisal) => (
                        <tr key={appraisal.id} className="hover:bg-muted/50">
                          <td className="p-4">
                            <div className="font-medium">{appraisal.appraisal_number}</div>
                            <div className="text-xs text-muted-foreground">{formatDate(appraisal.appraisal_date)}</div>
                          </td>
                          <td className="p-4">
                            <div className="text-sm">{appraisal.customer_id}</div>
                            {appraisal.gold_loan_id && <div className="text-xs text-muted-foreground">{appraisal.gold_loan_id}</div>}
                          </td>
                          <td className="p-4">
                            <div className="font-medium">{appraisal.ornament_type}</div>
                            <Badge variant="outline" className="mt-1">{appraisal.appraisal_type}</Badge>
                          </td>
                          <td className="p-4">
                            <div>{appraisal.net_weight_grams}g</div>
                            <div className="text-xs text-muted-foreground">{appraisal.verified_karat}K ({appraisal.purity_percentage}%)</div>
                          </td>
                          <td className="p-4 text-right">
                            <div className="font-medium">{formatCurrency(appraisal.appraised_value)}</div>
                            <div className="text-xs text-muted-foreground">Market: {formatCurrency(appraisal.market_value)}</div>
                          </td>
                          <td className="p-4 text-center">{getStatusBadge(appraisal.status)}</td>
                          <td className="p-4">
                            <div className="text-sm">{appraisal.appraiser_name}</div>
                            {appraisal.appraiser_license && <div className="text-xs text-muted-foreground">{appraisal.appraiser_license}</div>}
                          </td>
                          <td className="p-4">
                            <div className="flex gap-1 justify-center">
                              {appraisal.status === 'Draft' && (
                                <Button size="sm" variant="outline" onClick={() => handleSubmit(appraisal.id)}>Submit</Button>
                              )}
                              {appraisal.status === 'Submitted' && (
                                <>
                                  <Button size="sm" className="bg-green-600" onClick={() => handleVerify(appraisal.id, true)}>Approve</Button>
                                  <Button size="sm" variant="outline" className="border-red-300" onClick={() => handleVerify(appraisal.id, false)}>Reject</Button>
                                </>
                              )}
                              {(appraisal.status === 'Verified' || appraisal.status === 'Approved') && (
                                <Button size="sm" variant="outline" onClick={() => handleGenerateCertificate(appraisal.id)}>
                                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
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
                {totalPages > 1 && (
                  <div className="flex justify-center items-center gap-2 mt-6">
                    <Button variant="outline" onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>Previous</Button>
                    <span className="text-sm">Page {page} of {totalPages}</span>
                    <Button variant="outline" onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages}>Next</Button>
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
