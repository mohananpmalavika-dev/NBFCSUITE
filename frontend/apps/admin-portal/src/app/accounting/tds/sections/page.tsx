"use client";

import React, { useState, useEffect } from 'react';
import { tdsService, type TDSSection } from '@/services/accounting.service';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { toast } from '@/components/ui/use-toast';
import { Plus, Edit, Trash2, Save, X } from 'lucide-react';

export default function TDSSectionsPage() {
  const [sections, setSections] = useState<TDSSection[]>([]);
  const [loading, setLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingSection, setEditingSection] = useState<TDSSection | null>(null);
  const [formData, setFormData] = useState({
    section_code: '',
    section_name: '',
    description: '',
    rate_percentage: 0,
    threshold_amount: 0,
    is_active: true
  });

  useEffect(() => {
    loadSections();
  }, []);

  const loadSections = async () => {
    try {
      setLoading(true);
      const data = await tdsService.getSections();
      setSections(data);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load TDS sections",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingSection) {
        await tdsService.updateSection(editingSection.id, formData);
        toast({
          title: "Success",
          description: "TDS section updated successfully"
        });
      } else {
        await tdsService.createSection(formData);
        toast({
          title: "Success",
          description: "TDS section created successfully"
        });
      }
      setIsDialogOpen(false);
      resetForm();
      loadSections();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to save TDS section",
        variant: "destructive"
      });
    }
  };

  const handleEdit = (section: TDSSection) => {
    setEditingSection(section);
    setFormData({
      section_code: section.section_code,
      section_name: section.section_name,
      description: section.description || '',
      rate_percentage: section.rate_percentage,
      threshold_amount: section.threshold_amount || 0,
      is_active: section.is_active
    });
    setIsDialogOpen(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this TDS section?')) return;
    
    try {
      await tdsService.deleteSection(id);
      toast({
        title: "Success",
        description: "TDS section deleted successfully"
      });
      loadSections();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete TDS section",
        variant: "destructive"
      });
    }
  };

  const resetForm = () => {
    setFormData({
      section_code: '',
      section_name: '',
      description: '',
      rate_percentage: 0,
      threshold_amount: 0,
      is_active: true
    });
    setEditingSection(null);
  };

  const handleDialogClose = () => {
    setIsDialogOpen(false);
    resetForm();
  };

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">TDS Sections</h1>
          <p className="text-muted-foreground">Manage TDS section master data</p>
        </div>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={() => resetForm()}>
              <Plus className="mr-2 h-4 w-4" />
              Add Section
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>{editingSection ? 'Edit' : 'Add'} TDS Section</DialogTitle>
              <DialogDescription>
                {editingSection ? 'Update' : 'Create'} TDS section configuration
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmit}>
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="section_code">Section Code *</Label>
                    <Input
                      id="section_code"
                      value={formData.section_code}
                      onChange={(e) => setFormData({ ...formData, section_code: e.target.value })}
                      placeholder="e.g., 194A"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="rate_percentage">Rate (%) *</Label>
                    <Input
                      id="rate_percentage"
                      type="number"
                      step="0.01"
                      value={formData.rate_percentage}
                      onChange={(e) => setFormData({ ...formData, rate_percentage: parseFloat(e.target.value) })}
                      required
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="section_name">Section Name *</Label>
                  <Input
                    id="section_name"
                    value={formData.section_name}
                    onChange={(e) => setFormData({ ...formData, section_name: e.target.value })}
                    placeholder="e.g., Interest on Securities"
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="description">Description</Label>
                  <Input
                    id="description"
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    placeholder="Brief description"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="threshold_amount">Threshold Amount (₹)</Label>
                  <Input
                    id="threshold_amount"
                    type="number"
                    step="0.01"
                    value={formData.threshold_amount}
                    onChange={(e) => setFormData({ ...formData, threshold_amount: parseFloat(e.target.value) })}
                  />
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
          <CardTitle>TDS Section Master</CardTitle>
          <CardDescription>Configure TDS sections as per Income Tax Act</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Section Code</TableHead>
                  <TableHead>Section Name</TableHead>
                  <TableHead>Description</TableHead>
                  <TableHead className="text-right">Rate (%)</TableHead>
                  <TableHead className="text-right">Threshold (₹)</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {sections.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center text-muted-foreground py-8">
                      No TDS sections found. Click "Add Section" to create one.
                    </TableCell>
                  </TableRow>
                ) : (
                  sections.map((section) => (
                    <TableRow key={section.id}>
                      <TableCell className="font-medium">{section.section_code}</TableCell>
                      <TableCell>{section.section_name}</TableCell>
                      <TableCell className="max-w-xs truncate">{section.description}</TableCell>
                      <TableCell className="text-right">{section.rate_percentage.toFixed(2)}%</TableCell>
                      <TableCell className="text-right">
                        {section.threshold_amount?.toLocaleString('en-IN') || '-'}
                      </TableCell>
                      <TableCell>
                        <Badge variant={section.is_active ? "success" : "secondary"}>
                          {section.is_active ? 'Active' : 'Inactive'}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleEdit(section)}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDelete(section.id)}
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
    </div>
  );
}
