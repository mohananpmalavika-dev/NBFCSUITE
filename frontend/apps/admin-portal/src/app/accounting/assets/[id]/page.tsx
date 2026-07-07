"use client";

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { assetService, type FixedAsset, type DepreciationSchedule, type AssetMaintenance } from '@/services/accounting.service';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { toast } from '@/components/ui/use-toast';
import { ArrowLeft, Edit, Trash2, ArrowRightLeft, Wrench, Package } from 'lucide-react';
import { format } from 'date-fns';

export default function AssetDetailsPage() {
  const router = useRouter();
  const params = useParams();
  const assetId = parseInt(params.id as string);

  const [asset, setAsset] = useState<FixedAsset | null>(null);
  const [schedule, setSchedule] = useState<DepreciationSchedule[]>([]);
  const [maintenance, setMaintenance] = useState<AssetMaintenance[]>([]);
  const [loading, setLoading] = useState(true);
  const [isTransferOpen, setIsTransferOpen] = useState(false);
  const [isMaintenanceOpen, setIsMaintenanceOpen] = useState(false);
  const [isDisposeOpen, setIsDisposeOpen] = useState(false);

  const [transferData, setTransferData] = useState({
    to_location: '',
    to_department: '',
    to_custodian: '',
    transfer_reason: ''
  });

  const [maintenanceData, setMaintenanceData] = useState({
    maintenance_date: new Date().toISOString().split('T')[0],
    maintenance_type: '',
    description: '',
    cost: 0,
    vendor_name: ''
  });

  const [disposeData, setDisposeData] = useState({
    disposal_date: new Date().toISOString().split('T')[0],
    disposal_amount: 0,
    disposal_reason: ''
  });

  useEffect(() => {
    loadAsset();
    loadDepreciationSchedule();
    loadMaintenance();
  }, [assetId]);

  const loadAsset = async () => {
    try {
      setLoading(true);
      const data = await assetService.getAsset(assetId.toString());
      setAsset(data);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load asset details",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const loadDepreciationSchedule = async () => {
    try {
      const data = await assetService.getDepreciationSchedule({ asset_id: assetId.toString() });
      setSchedule(data.schedule);
    } catch (error) {
      console.error('Failed to load depreciation schedule', error);
    }
  };

  const loadMaintenance = async () => {
    try {
      const data = await assetService.getMaintenanceHistory(assetId.toString());
      setMaintenance(data.maintenance);
    } catch (error) {
      console.error('Failed to load maintenance records', error);
    }
  };

  const handleTransfer = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await assetService.transferAsset(assetId.toString(), transferData);
      toast({
        title: "Success",
        description: "Asset transferred successfully"
      });
      setIsTransferOpen(false);
      loadAsset();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to transfer asset",
        variant: "destructive"
      });
    }
  };

  const handleMaintenance = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await assetService.recordMaintenance(assetId.toString(), maintenanceData);
      toast({
        title: "Success",
        description: "Maintenance recorded successfully"
      });
      setIsMaintenanceOpen(false);
      loadMaintenance();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to record maintenance",
        variant: "destructive"
      });
    }
  };

  const handleDispose = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!confirm('Are you sure you want to dispose this asset? This action cannot be undone.')) return;

    try {
      await assetService.disposeAsset(assetId.toString(), disposeData);
      toast({
        title: "Success",
        description: "Asset disposed successfully"
      });
      setIsDisposeOpen(false);
      loadAsset();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to dispose asset",
        variant: "destructive"
      });
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 2
    }).format(value);
  };

  if (loading) {
    return <div className="container mx-auto py-6">Loading...</div>;
  }

  if (!asset) {
    return <div className="container mx-auto py-6">Asset not found</div>;
  }

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">{asset.asset_name}</h1>
            <p className="text-muted-foreground">Asset Code: {asset.asset_code}</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Dialog open={isTransferOpen} onOpenChange={setIsTransferOpen}>
            <DialogTrigger asChild>
              <Button variant="outline">
                <ArrowRightLeft className="mr-2 h-4 w-4" />
                Transfer
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Transfer Asset</DialogTitle>
                <DialogDescription>Move asset to new location or department</DialogDescription>
              </DialogHeader>
              <form onSubmit={handleTransfer}>
                <div className="grid gap-4 py-4">
                  <div className="space-y-2">
                    <Label>To Location</Label>
                    <Input
                      value={transferData.to_location}
                      onChange={(e) => setTransferData({ ...transferData, to_location: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>To Department</Label>
                    <Input
                      value={transferData.to_department}
                      onChange={(e) => setTransferData({ ...transferData, to_department: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>To Custodian</Label>
                    <Input
                      value={transferData.to_custodian}
                      onChange={(e) => setTransferData({ ...transferData, to_custodian: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Reason</Label>
                    <Textarea
                      value={transferData.transfer_reason}
                      onChange={(e) => setTransferData({ ...transferData, transfer_reason: e.target.value })}
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button type="button" variant="outline" onClick={() => setIsTransferOpen(false)}>
                    Cancel
                  </Button>
                  <Button type="submit">Transfer</Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>

          <Dialog open={isMaintenanceOpen} onOpenChange={setIsMaintenanceOpen}>
            <DialogTrigger asChild>
              <Button variant="outline">
                <Wrench className="mr-2 h-4 w-4" />
                Maintenance
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Record Maintenance</DialogTitle>
                <DialogDescription>Add maintenance or repair record</DialogDescription>
              </DialogHeader>
              <form onSubmit={handleMaintenance}>
                <div className="grid gap-4 py-4">
                  <div className="space-y-2">
                    <Label>Date *</Label>
                    <Input
                      type="date"
                      value={maintenanceData.maintenance_date}
                      onChange={(e) => setMaintenanceData({ ...maintenanceData, maintenance_date: e.target.value })}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Type *</Label>
                    <Input
                      value={maintenanceData.maintenance_type}
                      onChange={(e) => setMaintenanceData({ ...maintenanceData, maintenance_type: e.target.value })}
                      placeholder="e.g., Repair, Service, Upgrade"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Description *</Label>
                    <Textarea
                      value={maintenanceData.description}
                      onChange={(e) => setMaintenanceData({ ...maintenanceData, description: e.target.value })}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Cost (₹) *</Label>
                    <Input
                      type="number"
                      step="0.01"
                      value={maintenanceData.cost}
                      onChange={(e) => setMaintenanceData({ ...maintenanceData, cost: parseFloat(e.target.value) || 0 })}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Vendor</Label>
                    <Input
                      value={maintenanceData.vendor_name}
                      onChange={(e) => setMaintenanceData({ ...maintenanceData, vendor_name: e.target.value })}
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button type="button" variant="outline" onClick={() => setIsMaintenanceOpen(false)}>
                    Cancel
                  </Button>
                  <Button type="submit">Save</Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>

          {asset.status === 'ACTIVE' && (
            <Dialog open={isDisposeOpen} onOpenChange={setIsDisposeOpen}>
              <DialogTrigger asChild>
                <Button variant="destructive">
                  <Trash2 className="mr-2 h-4 w-4" />
                  Dispose
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Dispose Asset</DialogTitle>
                  <DialogDescription>Mark asset as disposed or sold</DialogDescription>
                </DialogHeader>
                <form onSubmit={handleDispose}>
                  <div className="grid gap-4 py-4">
                    <div className="space-y-2">
                      <Label>Disposal Date *</Label>
                      <Input
                        type="date"
                        value={disposeData.disposal_date}
                        onChange={(e) => setDisposeData({ ...disposeData, disposal_date: e.target.value })}
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Disposal Amount (₹) *</Label>
                      <Input
                        type="number"
                        step="0.01"
                        value={disposeData.disposal_amount}
                        onChange={(e) => setDisposeData({ ...disposeData, disposal_amount: parseFloat(e.target.value) || 0 })}
                        required
                      />
                      <p className="text-xs text-muted-foreground">
                        Current WDV: {formatCurrency(asset.written_down_value)}
                      </p>
                    </div>
                    <div className="space-y-2">
                      <Label>Reason *</Label>
                      <Textarea
                        value={disposeData.disposal_reason}
                        onChange={(e) => setDisposeData({ ...disposeData, disposal_reason: e.target.value })}
                        required
                      />
                    </div>
                  </div>
                  <DialogFooter>
                    <Button type="button" variant="outline" onClick={() => setIsDisposeOpen(false)}>
                      Cancel
                    </Button>
                    <Button type="submit" variant="destructive">Dispose</Button>
                  </DialogFooter>
                </form>
              </DialogContent>
            </Dialog>
          )}
        </div>
      </div>

      {/* Asset Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Purchase Cost</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(asset.purchase_cost)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Written Down Value</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-primary">{formatCurrency(asset.written_down_value)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Accumulated Depreciation</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">{formatCurrency(asset.accumulated_depreciation)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Status</CardTitle>
          </CardHeader>
          <CardContent>
            <Badge variant={asset.status === 'ACTIVE' ? 'success' : 'secondary'} className="text-lg">
              {asset.status}
            </Badge>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="details" className="space-y-4">
        <TabsList>
          <TabsTrigger value="details">Details</TabsTrigger>
          <TabsTrigger value="depreciation">Depreciation</TabsTrigger>
          <TabsTrigger value="maintenance">Maintenance</TabsTrigger>
        </TabsList>

        <TabsContent value="details">
          <Card>
            <CardHeader>
              <CardTitle>Asset Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Category</p>
                    <p className="font-medium">{asset.category.replace(/_/g, ' ')}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Purchase Date</p>
                    <p className="font-medium">{format(new Date(asset.purchase_date), 'dd MMM yyyy')}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Location</p>
                    <p className="font-medium">{asset.location || '-'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Department</p>
                    <p className="font-medium">{asset.department || '-'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Custodian</p>
                    <p className="font-medium">{asset.custodian || '-'}</p>
                  </div>
                </div>
                <div className="space-y-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Depreciation Method</p>
                    <p className="font-medium">{asset.depreciation_method.replace(/_/g, ' ')}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Depreciation Rate</p>
                    <p className="font-medium">{asset.depreciation_rate}% per annum</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Useful Life</p>
                    <p className="font-medium">{asset.useful_life_years} years</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Salvage Value</p>
                    <p className="font-medium">{formatCurrency(asset.salvage_value)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Last Depreciation</p>
                    <p className="font-medium">
                      {asset.last_depreciation_date 
                        ? format(new Date(asset.last_depreciation_date), 'dd MMM yyyy')
                        : 'Not yet depreciated'}
                    </p>
                  </div>
                </div>
              </div>
              {asset.description && (
                <div className="mt-6">
                  <p className="text-sm text-muted-foreground">Description</p>
                  <p className="mt-1">{asset.description}</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="depreciation">
          <Card>
            <CardHeader>
              <CardTitle>Depreciation Schedule</CardTitle>
              <CardDescription>{schedule.length} entries</CardDescription>
            </CardHeader>
            <CardContent>
              {schedule.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  No depreciation posted yet
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Date</TableHead>
                      <TableHead>FY</TableHead>
                      <TableHead className="text-right">Opening WDV</TableHead>
                      <TableHead className="text-right">Depreciation</TableHead>
                      <TableHead className="text-right">Accumulated</TableHead>
                      <TableHead className="text-right">Closing WDV</TableHead>
                      <TableHead>Posted</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {schedule.map((entry) => (
                      <TableRow key={entry.id}>
                        <TableCell>{format(new Date(entry.depreciation_date), 'dd MMM yyyy')}</TableCell>
                        <TableCell>{entry.financial_year}</TableCell>
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
        </TabsContent>

        <TabsContent value="maintenance">
          <Card>
            <CardHeader>
              <CardTitle>Maintenance History</CardTitle>
              <CardDescription>{maintenance.length} records</CardDescription>
            </CardHeader>
            <CardContent>
              {maintenance.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  No maintenance records
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Date</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead>Description</TableHead>
                      <TableHead>Vendor</TableHead>
                      <TableHead className="text-right">Cost</TableHead>
                      <TableHead>Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {maintenance.map((record) => (
                      <TableRow key={record.id}>
                        <TableCell>{format(new Date(record.maintenance_date), 'dd MMM yyyy')}</TableCell>
                        <TableCell>{record.maintenance_type}</TableCell>
                        <TableCell className="max-w-xs truncate">{record.description}</TableCell>
                        <TableCell>{record.vendor_name || '-'}</TableCell>
                        <TableCell className="text-right">{formatCurrency(record.maintenance_cost)}</TableCell>
                        <TableCell>
                          <Badge variant={record.is_completed ? 'success' : 'warning'}>
                            {record.is_completed ? 'Completed' : 'Pending'}
                          </Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
