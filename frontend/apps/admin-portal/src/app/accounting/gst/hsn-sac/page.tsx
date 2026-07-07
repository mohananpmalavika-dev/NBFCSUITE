"use client";

import React, { useState, useEffect } from 'react';
import { gstService, type HSNSAC } from '@/services/accounting.service';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { toast } from '@/components/ui/use-toast';
import { Plus, Edit, Trash2, Save, X, Search } from 'lucide-react';

export default function HSNSACMasterPage() {
  const [items, setItems] = useState<HSNSAC[]>([]);
  const [loading, setLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<HSNSAC | null>(null);
  const [filters, setFilters] = useState({
    search: '',
    type: 'all'
  });
  const [formData, setFormData] = useState({
    code_type: 'HSN' as 'HSN' | 'SAC',
    code: '',
    description: '',
    cgst_rate: 0,
    sgst_rate: 0,
    igst_rate: 0,
    cess_rate: 0,
    is_active: true
  });

  useEffect(() => {
    loadItems();
  }, []);

  const loadItems = async () => {
    try {
      setLoading(true);
      // TODO: Implement getAllHSNSAC or getHSNSACList endpoint to fetch all codes
      // const data = await gstService.getAllHSNSAC();
      // setItems(data);
      setItems([]);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load HSN/SAC codes",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    if (formData.code_type === 'HSN' && (formData.code.length < 4 || formData.code.length > 8)) {
      toast({
        title: "Validation Error",
        description: "HSN code must be 4-8 digits",
        variant: "destructive"
      });
      return;
    }

    if (formData.code_type === 'SAC' && formData.code.length !== 6) {
      toast({
        title: "Validation Error",
        description: "SAC code must be 6 digits",
        variant: "destructive"
      });
      return;
    }

    try {
      if (editingItem) {
        // TODO: Implement updateHSNSAC endpoint
        // await gstService.updateHSNSAC(editingItem.id, formData);
        toast({
          title: "Info",
          description: "Update endpoint not yet implemented"
        });
      } else {
        await gstService.createHSNSAC(formData);
        toast({
          title: "Success",
          description: "Code created successfully"
        });
      }
      setIsDialogOpen(false);
      resetForm();
      loadItems();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to save code",
        variant: "destructive"
      });
    }
  };

  const handleEdit = (item: HSNSAC) => {
    setEditingItem(item);
    setFormData({
      code_type: item.code_type as "HSN" | "SAC",
      code: item.code,
      description: item.description,
      cgst_rate: item.cgst_rate,
      sgst_rate: item.sgst_rate,
      igst_rate: item.igst_rate,
      cess_rate: 0, // Not in HSNSAC type, default to 0
      is_active: true // Not in HSNSAC type, default to true
    });
    setIsDialogOpen(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this code?')) return;
    
    try {
      // TODO: Implement deleteHSNSAC endpoint
      // await gstService.deleteHSNSAC(id);
      toast({
        title: "Info",
        description: "Delete endpoint not yet implemented"
      });
      // loadItems();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete code",
        variant: "destructive"
      });
    }
  };

  const resetForm = () => {
    setFormData({
      code_type: 'HSN',
      code: '',
      description: '',
      cgst_rate: 0,
      sgst_rate: 0,
      igst_rate: 0,
      cess_rate: 0,
      is_active: true
    });
    setEditingItem(null);
  };

  const handleDialogClose = () => {
    setIsDialogOpen(false);
    resetForm();
  };

  // Filter items
  const filteredItems = items.filter(item => {
    const matchesSearch = !filters.search || 
      item.code.toLowerCase().includes(filters.search.toLowerCase()) ||
      item.description.toLowerCase().includes(filters.search.toLowerCase());
    
    const matchesType = filters.type === 'all' || item.code_type === filters.type;
    
    return matchesSearch && matchesType;
  });

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">HSN/SAC Master</h1>
          <p className="text-muted-foreground">Manage HSN codes for goods and SAC codes for services</p>
        </div>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={() => resetForm()}>
              <Plus className="mr-2 h-4 w-4" />
              Add Code
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>{editingItem ? 'Edit' : 'Add'} HSN/SAC Code</DialogTitle>
              <DialogDescription>
                {editingItem ? 'Update' : 'Create'} HSN/SAC code with GST rates
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmit}>
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="code_type">Type *</Label>
                    <Select
                      value={formData.code_type}
                      onValueChange={(value: 'HSN' | 'SAC') => setFormData({ ...formData, code_type: value })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="HSN">HSN (Goods)</SelectItem>
                        <SelectItem value="SAC">SAC (Services)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="code">Code *</Label>
                    <Input
                      id="code"
                      value={formData.code}
                      onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                      placeholder={formData.code_type === 'HSN' ? '4-8 digits' : '6 digits'}
                      required
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="description">Description *</Label>
                  <Input
                    id="description"
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    placeholder="Brief description"
                    required
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="cgst_rate">CGST Rate (%) *</Label>
                    <Input
                      id="cgst_rate"
                      type="number"
                      step="0.01"
                      value={formData.cgst_rate}
                      onChange={(e) => {
                        const rate = parseFloat(e.target.value) || 0;
                        setFormData({ 
                          ...formData, 
                          cgst_rate: rate,
                          sgst_rate: rate,
                          igst_rate: rate * 2
                        });
                      }}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="sgst_rate">SGST Rate (%) *</Label>
                    <Input
                      id="sgst_rate"
                      type="number"
                      step="0.01"
                      value={formData.sgst_rate}
                      onChange={(e) => setFormData({ ...formData, sgst_rate: parseFloat(e.target.value) || 0 })}
                      required
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="igst_rate">IGST Rate (%) *</Label>
                    <Input
                      id="igst_rate"
                      type="number"
                      step="0.01"
                      value={formData.igst_rate}
                      onChange={(e) => setFormData({ ...formData, igst_rate: parseFloat(e.target.value) || 0 })}
                      required
                    />
                    <p className="text-xs text-muted-foreground">Usually CGST + SGST</p>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="cess_rate">Cess Rate (%)</Label>
                    <Input
                      id="cess_rate"
                      type="number"
                      step="0.01"
                      value={formData.cess_rate}
                      onChange={(e) => setFormData({ ...formData, cess_rate: parseFloat(e.target.value) || 0 })}
                    />
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="is_active"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                    className="h-4 w-4"
                  />
                  <Label htmlFor="is_active">Active</Label>
                </div>
              </div>
              <DialogFooter>
                <Button type="button" variant="outline" onClick={handleDialogClose}>
                  <X className="mr-2 h-4 w-4" />
                  Cancel
                </Button>
                <Button type="submit">
                  <Save className="mr-2 h-4 w-4" />
                  Save
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="relative col-span-2">
              <Search className="absolute left-2 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by code or description..."
                value={filters.search}
                onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                className="pl-8"
              />
            </div>
            <Select
              value={filters.type}
              onValueChange={(value) => setFilters({ ...filters, type: value })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="HSN">HSN Only</SelectItem>
                <SelectItem value="SAC">SAC Only</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>HSN/SAC Codes</CardTitle>
          <CardDescription>Harmonized System of Nomenclature (HSN) for goods and Service Accounting Code (SAC)</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Type</TableHead>
                  <TableHead>Code</TableHead>
                  <TableHead>Description</TableHead>
                  <TableHead className="text-right">CGST %</TableHead>
                  <TableHead className="text-right">SGST %</TableHead>
                  <TableHead className="text-right">IGST %</TableHead>
                  <TableHead className="text-right">Cess %</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredItems.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={9} className="text-center text-muted-foreground py-8">
                      No codes found. Click "Add Code" to create one.
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredItems.map((item) => (
                    <TableRow key={item.id}>
                      <TableCell>
                        <Badge variant={item.code_type === 'HSN' ? 'default' : 'secondary'}>
                          {item.code_type}
                        </Badge>
                      </TableCell>
                      <TableCell className="font-medium">{item.code}</TableCell>
                      <TableCell className="max-w-xs">{item.description}</TableCell>
                      <TableCell className="text-right">{item.cgst_rate}%</TableCell>
                      <TableCell className="text-right">{item.sgst_rate}%</TableCell>
                      <TableCell className="text-right">{item.igst_rate}%</TableCell>
                      <TableCell className="text-right">0%</TableCell>
                      <TableCell>
                        <Badge variant="success">
                          Active
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleEdit(item)}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDelete(item.id)}
                          >
                            <Trash2 className="h-4 w-4 text-destructive" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Total Codes</p>
                <p className="text-2xl font-bold">{items.length}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Active Codes</p>
                <p className="text-2xl font-bold text-green-600">
                  {items.filter(i => i.is_active).length}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">HSN Codes</p>
                <p className="text-2xl font-bold">
                  {items.filter(i => i.code_type === 'HSN').length}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">SAC Codes</p>
                <p className="text-2xl font-bold">
                  {items.filter(i => i.code_type === 'SAC').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>About HSN/SAC</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-muted-foreground">
            <p>
              <strong>HSN (Harmonized System of Nomenclature):</strong> 6-8 digit code for classification of goods
            </p>
            <p>
              <strong>SAC (Service Accounting Code):</strong> 6-digit code for classification of services
            </p>
            <ul className="list-disc list-inside space-y-1 mt-2">
              <li>Required in GST invoices and returns</li>
              <li>Determines applicable GST rates</li>
              <li>Mandatory for annual turnover &gt; ₹5 crore</li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
