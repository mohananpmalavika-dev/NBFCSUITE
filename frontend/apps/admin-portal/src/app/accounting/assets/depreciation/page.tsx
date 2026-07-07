"use client";

import React, { useState, useEffect } from 'react';
import { assetService, type FixedAsset, type DepreciationSchedule } from '@/services/accounting.service';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from '@/components/ui/use-toast';
import { Play, Calculator, Download, FileText } from 'lucide-react';
import { format } from 'date-fns';

export default function DepreciationPage() {
  const [assets, setAssets] = useState<FixedAsset[]>([]);
  const [schedule, setSchedule] = useState<DepreciationSchedule[]>([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [depreciationDate, setDepreciationDate] = useState(new Date().toISOString().split('T')[0]);
  const [preview, setPreview] = useState<any[]>([]);

  useEffect(() => {
    loadAssets();
    loadSchedule();
  }, [selectedMonth, selectedYear]);

  const loadAssets = async () => {
    try {
      setLoading(true);
      const response = await assetService.getAssets({ status: 'ACTIVE' });
      setAssets(response.data.items);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load assets",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const loadSchedule = async () => {
    try {
      const response = await assetService.getDepreciationSchedule({
        financial_year: selectedYear,
        month: selectedMonth
      });
      setSchedule(response.data.schedule);
    } catch (error) {
      console.error('Failed to load schedule', error);
    }
  };

  const handlePreviewDepreciation = async () => {
    if (!depreciationDate) {
      toast({
        title: "Validation Error",
        description: "Please select depreciation date",
        variant: "destructive"
      });
      return;
    }

    setProcessing(true);
    const previews = [];

    try {
      for (const asset of assets) {
        try {
          const result = await assetService.calculateDepreciation(asset.id, depreciationDate);
          previews.push(result);
        } catch (error) {
          console.error(`Failed to calculate for asset ${asset.id}`, error);
        }
      }
      setPreview(previews);
      toast({
        title: "Success",
        description: `Calculated depreciation for ${previews.length} assets`
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to calculate depreciation",
        variant: "destructive"
      });
    } finally {
      setProcessing(false);
    }
  };

  const handlePostDepreciation = async () => {
    if (preview.length === 0) {
      toast({
        title: "Error",
        description: "Please preview depreciation first",
        variant: "destructive"
      });
      return;
    }

    if (!confirm(`Post depreciation for ${preview.length} assets? This action cannot be undone.`)) {
      return;
    }

    setProcessing(true);
    let successCount = 0;
    let errorCount = 0;

    try {
      for (const item of preview) {
        try {
          await assetService.postDepreciation({
            asset_id: item.asset_id,
            depreciation_date: depreciationDate
          });
          successCount++;
        } catch (error) {
          errorCount++;
          console.error(`Failed to post for asset ${item.asset_id}`, error);
        }
      }

      toast({
        title: "Success",
        description: `Posted ${successCount} depreciation entries${errorCount > 0 ? `, ${errorCount} failed` : ''}`
      });

      setPreview([]);
      loadSchedule();
      loadAssets();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to post depreciation",
        variant: "destructive"
      });
    } finally {
      setProcessing(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 2
    }).format(value);
  };

  const totalDepreciation = preview.reduce((sum, item) => sum + item.depreciation_amount, 0);

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Depreciation Management</h1>
        <p className="text-muted-foreground">Calculate and post monthly depreciation</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Active Assets</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{assets.length}</div>
            <p className="text-xs text-muted-foreground">Eligible for depreciation</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Asset Value</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(assets.reduce((sum, a) => sum + a.purchase_cost, 0))}
            </div>
            <p className="text-xs text-muted-foreground">Original cost</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Current WDV</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-primary">
              {formatCurrency(assets.reduce((sum, a) => sum + a.written_down_value, 0))}
            </div>
            <p className="text-xs text-muted-foreground">Written down value</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Posted This Month</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{schedule.filter(s => s.is_posted).length}</div>
            <p className="text-xs text-muted-foreground">Entries</p>
          </CardContent>
        </Card>
      </div>

      {/* Run Depreciation */}
      <Card>
        <CardHeader>
          <CardTitle>Run Monthly Depreciation</CardTitle>
          <CardDescription>Calculate and post depreciation for all active assets</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label>Depreciation Date</Label>
              <Input
                type="date"
                value={depreciationDate}
                onChange={(e) => setDepreciationDate(e.target.value)}
              />
            </div>
            <div className="flex items-end">
              <Button
                onClick={handlePreviewDepreciation}
                disabled={processing || !depreciationDate}
                className="w-full"
              >
                <Calculator className="mr-2 h-4 w-4" />
                {processing ? 'Calculating...' : 'Preview Depreciation'}
              </Button>
            </div>
            <div className="flex items-end">
              <Button
                onClick={handlePostDepreciation}
                disabled={processing || preview.length === 0}
                className="w-full"
                variant="default"
              >
                <Play className="mr-2 h-4 w-4" />
                {processing ? 'Posting...' : 'Post Depreciation'}
              </Button>
            </div>
          </div>

          {preview.length > 0 && (
            <div className="mt-4 p-4 bg-primary/10 rounded-lg">
              <h3 className="font-semibold mb-2">Preview Summary</h3>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Assets</p>
                  <p className="text-xl font-bold">{preview.length}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Total Depreciation</p>
                  <p className="text-xl font-bold">{formatCurrency(totalDepreciation)}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Date</p>
                  <p className="text-xl font-bold">{format(new Date(depreciationDate), 'dd MMM yyyy')}</p>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Preview Table */}
      {preview.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Depreciation Preview</CardTitle>
            <CardDescription>Review before posting</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Asset</TableHead>
                    <TableHead>Method</TableHead>
                    <TableHead className="text-right">Opening WDV</TableHead>
                    <TableHead className="text-right">Depreciation</TableHead>
                    <TableHead className="text-right">Closing WDV</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {preview.map((item) => (
                    <TableRow key={item.asset_id}>
                      <TableCell className="font-medium">{item.asset_name}</TableCell>
                      <TableCell>{item.method}</TableCell>
                      <TableCell className="text-right">{formatCurrency(item.opening_wdv)}</TableCell>
                      <TableCell className="text-right font-semibold text-orange-600">
                        {formatCurrency(item.depreciation_amount)}
                      </TableCell>
                      <TableCell className="text-right font-semibold">
                        {formatCurrency(item.closing_wdv)}
                      </TableCell>
                    </TableRow>
                  ))}
                  <TableRow className="bg-muted/50">
                    <TableCell colSpan={3} className="font-bold">Total</TableCell>
                    <TableCell className="text-right font-bold">{formatCurrency(totalDepreciation)}</TableCell>
                    <TableCell></TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Posted Schedule */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle>Posted Depreciation Schedule</CardTitle>
              <CardDescription>History of posted depreciation</CardDescription>
            </div>
            <div className="flex gap-2">
              <Select
                value={selectedMonth.toString()}
                onValueChange={(value) => setSelectedMonth(parseInt(value))}
              >
                <SelectTrigger className="w-[140px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {Array.from({ length: 12 }, (_, i) => (
                    <SelectItem key={i + 1} value={(i + 1).toString()}>
                      {new Date(2024, i).toLocaleString('default', { month: 'long' })}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Select
                value={selectedYear.toString()}
                onValueChange={(value) => setSelectedYear(parseInt(value))}
              >
                <SelectTrigger className="w-[100px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="2024">2024</SelectItem>
                  <SelectItem value="2023">2023</SelectItem>
                  <SelectItem value="2022">2022</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : schedule.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No depreciation posted for this period
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Asset</TableHead>
                  <TableHead className="text-right">Opening WDV</TableHead>
                  <TableHead className="text-right">Depreciation</TableHead>
                  <TableHead className="text-right">Accumulated</TableHead>
                  <TableHead className="text-right">Closing WDV</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {schedule.map((entry) => (
                  <TableRow key={entry.id}>
                    <TableCell>{format(new Date(entry.depreciation_date), 'dd MMM yyyy')}</TableCell>
                    <TableCell>Asset ID: {entry.asset_id}</TableCell>
                    <TableCell className="text-right">{formatCurrency(entry.opening_wdv)}</TableCell>
                    <TableCell className="text-right">{formatCurrency(entry.depreciation_amount)}</TableCell>
                    <TableCell className="text-right">{formatCurrency(entry.accumulated_depreciation)}</TableCell>
                    <TableCell className="text-right font-semibold">{formatCurrency(entry.closing_wdv)}</TableCell>
                    <TableCell>
                      <Badge variant={entry.is_posted ? 'success' : 'secondary'}>
                        {entry.is_posted ? 'Posted' : 'Draft'}
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
          </CardContent>
        </Card>
      )}

      {/* Information */}
      <Card>
        <CardHeader>
          <CardTitle>Depreciation Process</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-muted-foreground">
          <div className="flex items-start gap-2">
            <span className="font-bold text-foreground">1.</span>
            <span>Select the depreciation date (usually last day of month)</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="font-bold text-foreground">2.</span>
            <span>Click "Preview Depreciation" to calculate for all active assets</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="font-bold text-foreground">3.</span>
            <span>Review the preview table to verify amounts</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="font-bold text-foreground">4.</span>
            <span>Click "Post Depreciation" to finalize (creates journal entries)</span>
          </div>
          <div className="flex items-start gap-2 text-orange-600">
            <span className="font-bold">⚠️</span>
            <span>Posted depreciation cannot be reversed - ensure preview is correct</span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
