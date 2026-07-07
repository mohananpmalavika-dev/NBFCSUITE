"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { Download, RefreshCw, FileText, CheckCircle, Clock, XCircle, Send, Eye } from "lucide-react";
import { almService } from '@/services/almService';
import type { QuarterlyReturnResponse } from '@/types/alm';
import { formatCurrency } from '@/lib/utils';

export default function QuarterlyReturnsPage() {
  const [loading, setLoading] = useState(true);
  const [returns, setReturns] = useState<QuarterlyReturnResponse[]>([]);
  const [selectedReturn, setSelectedReturn] = useState<QuarterlyReturnResponse | null>(null);
  const [showSubmitDialog, setShowSubmitDialog] = useState(false);
  const [showApproveDialog, setShowApproveDialog] = useState(false);
  const [showRejectDialog, setShowRejectDialog] = useState(false);
  const [comments, setComments] = useState('');

  useEffect(() => {
    fetchReturns();
  }, []);

  const fetchReturns = async () => {
    try {
      setLoading(true);
      const response = await almService.getQuarterlyReturns();
      setReturns(response);
    } catch (error) {
      console.error('Failed to fetch quarterly returns:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateReturn = async () => {
    try {
      const currentDate = new Date();
      const quarter = Math.floor(currentDate.getMonth() / 3) + 1;
      const year = currentDate.getFullYear();
      
      const newReturn = await almService.createQuarterlyReturn({
        quarter,
        year,
        return_type: 'sls'
      });
      
      await fetchReturns();
    } catch (error) {
      console.error('Failed to create return:', error);
    }
  };

  const handleSubmitReturn = async () => {
    if (!selectedReturn) return;
    
    try {
      await almService.submitQuarterlyReturn(selectedReturn.id, comments);
      await fetchReturns();
      setShowSubmitDialog(false);
      setComments('');
    } catch (error) {
      console.error('Failed to submit return:', error);
    }
  };

  const handleApproveReturn = async () => {
    if (!selectedReturn) return;
    
    try {
      await almService.approveQuarterlyReturn(selectedReturn.id, comments);
      await fetchReturns();
      setShowApproveDialog(false);
      setComments('');
    } catch (error) {
      console.error('Failed to approve return:', error);
    }
  };

  const handleRejectReturn = async () => {
    if (!selectedReturn) return;
    
    try {
      await almService.rejectQuarterlyReturn(selectedReturn.id, comments);
      await fetchReturns();
      setShowRejectDialog(false);
      setComments('');
    } catch (error) {
      console.error('Failed to reject return:', error);
    }
  };

  const handleExport = async (returnId: number) => {
    try {
      await almService.exportQuarterlyReturn(returnId, 'excel');
    } catch (error) {
      console.error('Failed to export return:', error);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'draft':
        return <Badge variant="secondary"><Clock className="h-3 w-3 mr-1" />Draft</Badge>;
      case 'submitted':
        return <Badge variant="default"><Send className="h-3 w-3 mr-1" />Submitted</Badge>;
      case 'approved':
        return <Badge variant="default" className="bg-green-600"><CheckCircle className="h-3 w-3 mr-1" />Approved</Badge>;
      case 'rejected':
        return <Badge variant="destructive"><XCircle className="h-3 w-3 mr-1" />Rejected</Badge>;
      default:
        return <Badge>{status}</Badge>;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <RefreshCw className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Quarterly Returns</h1>
          <p className="text-muted-foreground">
            SLS/IRS statements management and regulatory submissions
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={fetchReturns}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button onClick={handleCreateReturn}>
            <FileText className="h-4 w-4 mr-2" />
            Create New Return
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Returns</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{returns.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Submission</CardTitle>
            <Clock className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {returns.filter(r => r.status === 'draft').length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Submitted</CardTitle>
            <Send className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {returns.filter(r => r.status === 'submitted').length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Approved</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {returns.filter(r => r.status === 'approved').length}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Returns List */}
      <Card>
        <CardHeader>
          <CardTitle>Quarterly Returns</CardTitle>
          <CardDescription>List of all quarterly regulatory returns</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {returns.map((ret) => (
              <div key={ret.id} className="border rounded-lg p-4 hover:bg-muted/50">
                <div className="flex items-start justify-between">
                  <div className="space-y-2 flex-1">
                    <div className="flex items-center gap-3">
                      <h3 className="font-semibold text-lg">
                        Q{ret.quarter} {ret.year} - {ret.return_type.toUpperCase()}
                      </h3>
                      {getStatusBadge(ret.status)}
                    </div>
                    
                    <div className="grid gap-2 md:grid-cols-4">
                      <div>
                        <p className="text-sm text-muted-foreground">Reporting Date</p>
                        <p className="font-medium">{new Date(ret.reporting_date).toLocaleDateString()}</p>
                      </div>
                      {ret.submission_date && (
                        <div>
                          <p className="text-sm text-muted-foreground">Submission Date</p>
                          <p className="font-medium">{new Date(ret.submission_date).toLocaleDateString()}</p>
                        </div>
                      )}
                      {ret.approval_date && (
                        <div>
                          <p className="text-sm text-muted-foreground">Approval Date</p>
                          <p className="font-medium">{new Date(ret.approval_date).toLocaleDateString()}</p>
                        </div>
                      )}
                      <div>
                        <p className="text-sm text-muted-foreground">Version</p>
                        <p className="font-medium">v{ret.version}</p>
                      </div>
                    </div>

                    {ret.submitted_by && (
                      <div>
                        <p className="text-sm text-muted-foreground">Submitted By</p>
                        <p className="text-sm">{ret.submitted_by}</p>
                      </div>
                    )}

                    {ret.approved_by && (
                      <div>
                        <p className="text-sm text-muted-foreground">Approved By</p>
                        <p className="text-sm">{ret.approved_by}</p>
                      </div>
                    )}

                    {ret.comments && (
                      <div>
                        <p className="text-sm text-muted-foreground">Comments</p>
                        <p className="text-sm">{ret.comments}</p>
                      </div>
                    )}
                  </div>

                  <div className="flex gap-2 ml-4">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setSelectedReturn(ret);
                        // Navigate to detail view
                      }}
                    >
                      <Eye className="h-4 w-4 mr-1" />
                      View
                    </Button>
                    
                    {ret.status === 'draft' && (
                      <Button
                        variant="default"
                        size="sm"
                        onClick={() => {
                          setSelectedReturn(ret);
                          setShowSubmitDialog(true);
                        }}
                      >
                        <Send className="h-4 w-4 mr-1" />
                        Submit
                      </Button>
                    )}
                    
                    {ret.status === 'submitted' && (
                      <>
                        <Button
                          variant="default"
                          size="sm"
                          onClick={() => {
                            setSelectedReturn(ret);
                            setShowApproveDialog(true);
                          }}
                        >
                          <CheckCircle className="h-4 w-4 mr-1" />
                          Approve
                        </Button>
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={() => {
                            setSelectedReturn(ret);
                            setShowRejectDialog(true);
                          }}
                        >
                          <XCircle className="h-4 w-4 mr-1" />
                          Reject
                        </Button>
                      </>
                    )}
                    
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleExport(ret.id)}
                    >
                      <Download className="h-4 w-4 mr-1" />
                      Export
                    </Button>
                  </div>
                </div>
              </div>
            ))}

            {returns.length === 0 && (
              <div className="text-center py-12">
                <FileText className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <p className="text-muted-foreground">No quarterly returns found</p>
                <Button className="mt-4" onClick={handleCreateReturn}>
                  Create First Return
                </Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Information Card */}
      <Card>
        <CardHeader>
          <CardTitle>About Quarterly Returns</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <h4 className="font-semibold mb-2">SLS Return (Supervisory Liquidity Statement)</h4>
              <p className="text-sm text-muted-foreground">
                Quarterly report on liquidity position including maturity ladder, gap analysis, and liquidity ratios.
                Required for regulatory compliance and monitoring of liquidity risk management.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-2">IRS Return (Interest Rate Sensitivity)</h4>
              <p className="text-sm text-muted-foreground">
                Quarterly report on interest rate risk exposure including repricing gap analysis, duration gap,
                and interest rate shock scenarios.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-2">Submission Workflow</h4>
              <ol className="list-decimal list-inside text-sm text-muted-foreground space-y-1">
                <li>Create quarterly return (Draft status)</li>
                <li>Review and validate data</li>
                <li>Submit for approval</li>
                <li>Senior management reviews and approves/rejects</li>
                <li>Export and submit to regulatory authority</li>
              </ol>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Submit Dialog */}
      <Dialog open={showSubmitDialog} onOpenChange={setShowSubmitDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Submit Quarterly Return</DialogTitle>
            <DialogDescription>
              Submit this return for approval. Once submitted, it cannot be edited until approved or rejected.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <label className="text-sm font-medium">Comments (Optional)</label>
              <Textarea
                placeholder="Add any comments or notes..."
                value={comments}
                onChange={(e) => setComments(e.target.value)}
                rows={4}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowSubmitDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleSubmitReturn}>
              Submit Return
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Approve Dialog */}
      <Dialog open={showApproveDialog} onOpenChange={setShowApproveDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Approve Quarterly Return</DialogTitle>
            <DialogDescription>
              Approve this return for regulatory submission.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <label className="text-sm font-medium">Approval Comments</label>
              <Textarea
                placeholder="Add approval comments..."
                value={comments}
                onChange={(e) => setComments(e.target.value)}
                rows={4}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowApproveDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleApproveReturn} className="bg-green-600 hover:bg-green-700">
              Approve Return
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Reject Dialog */}
      <Dialog open={showRejectDialog} onOpenChange={setShowRejectDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Reject Quarterly Return</DialogTitle>
            <DialogDescription>
              Reject this return and send it back for revision. Please provide a reason.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <label className="text-sm font-medium">Rejection Reason (Required)</label>
              <Textarea
                placeholder="Please explain why this return is being rejected..."
                value={comments}
                onChange={(e) => setComments(e.target.value)}
                rows={4}
                required
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowRejectDialog(false)}>
              Cancel
            </Button>
            <Button 
              onClick={handleRejectReturn} 
              variant="destructive"
              disabled={!comments.trim()}
            >
              Reject Return
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
