'use client';

import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import {
  getVaultLocations,
  createVaultLocation,
  getVaultInventory,
  checkInToVault,
  checkOutFromVault,
  createVaultTransfer,
  getVaultCapacity,
  performVaultAudit,
  type VaultLocation,
  type VaultInventory,
  type VaultTransfer
} from '@/services/gold-loan.service';
import { formatDate, formatDateTime } from '@/lib/utils';

export default function VaultManagementPage() {
  const [activeTab, setActiveTab] = useState('locations');
  const [vaultLocations, setVaultLocations] = useState<VaultLocation[]>([]);
  const [inventory, setInventory] = useState<VaultInventory[]>([]);
  const [loading, setLoading] = useState(true);
  const [showLocationForm, setShowLocationForm] = useState(false);
  const [showCheckInForm, setShowCheckInForm] = useState(false);
  const [showTransferForm, setShowTransferForm] = useState(false);
  const [selectedVault, setSelectedVault] = useState<string>('');
  const [error, setError] = useState<string | null>(null);

  // Location form state
  const [locationForm, setLocationForm] = useState({
    vault_code: '',
    vault_name: '',
    vault_type: 'Main',
    location_type: 'Branch',
    branch_id: '',
    address_line1: '',
    city: '',
    state: '',
    pincode: '',
    max_capacity_items: '',
    max_capacity_weight_kg: '',
    security_level: 'High',
    insurance_value: '',
    insurance_policy_number: ''
  });

  // Check-in form state
  const [checkInForm, setCheckInForm] = useState({
    vault_location_id: '',
    gold_loan_id: '',
    customer_id: '',
    ornament_id: '',
    barcode: '',
    rfid_tag: '',
    seal_number: '',
    rack_number: '',
    shelf_number: '',
    slot_number: '',
    remarks: ''
  });

  // Transfer form state
  const [transferForm, setTransferForm] = useState({
    from_vault_id: '',
    to_vault_id: '',
    inventory_ids: [] as string[],
    reason: '',
    remarks: ''
  });

  useEffect(() => {
    loadVaultLocations();
  }, []);

  useEffect(() => {
    if (selectedVault) {
      loadInventory(selectedVault);
    }
  }, [selectedVault]);

  const loadVaultLocations = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getVaultLocations({ is_active: true });
      setVaultLocations(data.locations || []);
    } catch (error: any) {
      console.error('Failed to load vault locations:', error);
      setError(error.response?.data?.error?.message || 'Failed to load vault locations');
    } finally {
      setLoading(false);
    }
  };

  const loadInventory = async (vaultId: string) => {
    try {
      setLoading(true);
      const data = await getVaultInventory({ vault_location_id: vaultId, status: 'checked_in' });
      setInventory(data.inventory || []);
    } catch (error: any) {
      console.error('Failed to load inventory:', error);
      setError(error.response?.data?.error?.message || 'Failed to load inventory');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateLocation = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setError(null);
      await createVaultLocation({
        ...locationForm,
        max_capacity_items: parseInt(locationForm.max_capacity_items),
        max_capacity_weight_kg: parseFloat(locationForm.max_capacity_weight_kg),
        insurance_value: locationForm.insurance_value ? parseFloat(locationForm.insurance_value) : undefined,
        is_active: true
      });
      setShowLocationForm(false);
      setLocationForm({
        vault_code: '',
        vault_name: '',
        vault_type: 'Main',
        location_type: 'Branch',
        branch_id: '',
        address_line1: '',
        city: '',
        state: '',
        pincode: '',
        max_capacity_items: '',
        max_capacity_weight_kg: '',
        security_level: 'High',
        insurance_value: '',
        insurance_policy_number: ''
      });
      await loadVaultLocations();
      alert('Vault location created successfully');
    } catch (error: any) {
      console.error('Failed to create location:', error);
      setError(error.response?.data?.error?.message || 'Failed to create vault location');
    }
  };

  const handleCheckIn = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setError(null);
      await checkInToVault(checkInForm);
      setShowCheckInForm(false);
      setCheckInForm({
        vault_location_id: '',
        gold_loan_id: '',
        customer_id: '',
        ornament_id: '',
        barcode: '',
        rfid_tag: '',
        seal_number: '',
        rack_number: '',
        shelf_number: '',
        slot_number: '',
        remarks: ''
      });
      if (selectedVault) {
        await loadInventory(selectedVault);
      }
      alert('Ornament checked in successfully');
    } catch (error: any) {
      console.error('Failed to check in:', error);
      setError(error.response?.data?.error?.message || 'Failed to check in ornament');
    }
  };

  const handleCheckOut = async (inventoryId: string) => {
    if (!confirm('Are you sure you want to check out this ornament?')) return;
    try {
      setError(null);
      await checkOutFromVault(inventoryId);
      if (selectedVault) {
        await loadInventory(selectedVault);
      }
      alert('Ornament checked out successfully');
    } catch (error: any) {
      console.error('Failed to check out:', error);
      setError(error.response?.data?.error?.message || 'Failed to check out ornament');
    }
  };

  const handleTransfer = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setError(null);
      await createVaultTransfer(transferForm);
      setShowTransferForm(false);
      setTransferForm({
        from_vault_id: '',
        to_vault_id: '',
        inventory_ids: [],
        reason: '',
        remarks: ''
      });
      alert('Transfer request created successfully');
    } catch (error: any) {
      console.error('Failed to create transfer:', error);
      setError(error.response?.data?.error?.message || 'Failed to create transfer');
    }
  };

  const getCapacityColor = (percentage: number) => {
    if (percentage >= 90) return 'text-red-600';
    if (percentage >= 75) return 'text-orange-600';
    if (percentage >= 50) return 'text-yellow-600';
    return 'text-green-600';
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
            <h1 className="text-3xl font-bold">Vault Management</h1>
            <p className="text-muted-foreground">Manage vault locations, inventory, and transfers</p>
          </div>
          <div className="flex gap-2">
            <Button onClick={() => setShowCheckInForm(true)} variant="outline">
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Check In
            </Button>
            <Button onClick={() => setShowTransferForm(true)} variant="outline">
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
              </svg>
              Transfer
            </Button>
            <Button onClick={() => setShowLocationForm(true)}>
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              New Vault Location
            </Button>
          </div>
        </div>

        {/* Create Location Modal */}
        {showLocationForm && (
          <Card className="border-2 border-blue-200">
            <CardHeader>
              <CardTitle>Create Vault Location</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleCreateLocation} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Vault Code *</label>
                    <Input
                      value={locationForm.vault_code}
                      onChange={(e) => setLocationForm({ ...locationForm, vault_code: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Vault Name *</label>
                    <Input
                      value={locationForm.vault_name}
                      onChange={(e) => setLocationForm({ ...locationForm, vault_name: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Vault Type</label>
                    <select
                      value={locationForm.vault_type}
                      onChange={(e) => setLocationForm({ ...locationForm, vault_type: e.target.value })}
                      className="w-full px-3 py-2 border rounded-md"
                    >
                      <option value="Main">Main</option>
                      <option value="Branch">Branch</option>
                      <option value="Off-site">Off-site</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Security Level</label>
                    <select
                      value={locationForm.security_level}
                      onChange={(e) => setLocationForm({ ...locationForm, security_level: e.target.value })}
                      className="w-full px-3 py-2 border rounded-md"
                    >
                      <option value="High">High</option>
                      <option value="Medium">Medium</option>
                      <option value="Standard">Standard</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Max Capacity (Items) *</label>
                    <Input
                      type="number"
                      value={locationForm.max_capacity_items}
                      onChange={(e) => setLocationForm({ ...locationForm, max_capacity_items: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Max Capacity (Weight KG) *</label>
                    <Input
                      type="number"
                      step="0.01"
                      value={locationForm.max_capacity_weight_kg}
                      onChange={(e) => setLocationForm({ ...locationForm, max_capacity_weight_kg: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">City</label>
                    <Input
                      value={locationForm.city}
                      onChange={(e) => setLocationForm({ ...locationForm, city: e.target.value })}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">State</label>
                    <Input
                      value={locationForm.state}
                      onChange={(e) => setLocationForm({ ...locationForm, state: e.target.value })}
                    />
                  </div>
                </div>
                <div className="flex justify-end gap-2">
                  <Button type="button" variant="outline" onClick={() => setShowLocationForm(false)}>
                    Cancel
                  </Button>
                  <Button type="submit">Create Location</Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {/* Check-In Modal */}
        {showCheckInForm && (
          <Card className="border-2 border-green-200">
            <CardHeader>
              <CardTitle>Check In Ornament</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleCheckIn} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Vault Location *</label>
                    <select
                      value={checkInForm.vault_location_id}
                      onChange={(e) => setCheckInForm({ ...checkInForm, vault_location_id: e.target.value })}
                      className="w-full px-3 py-2 border rounded-md"
                      required
                    >
                      <option value="">Select vault...</option>
                      {vaultLocations.map(v => (
                        <option key={v.id} value={v.id}>{v.vault_name} ({v.vault_code})</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Gold Loan ID *</label>
                    <Input
                      value={checkInForm.gold_loan_id}
                      onChange={(e) => setCheckInForm({ ...checkInForm, gold_loan_id: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Customer ID *</label>
                    <Input
                      value={checkInForm.customer_id}
                      onChange={(e) => setCheckInForm({ ...checkInForm, customer_id: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Ornament ID *</label>
                    <Input
                      value={checkInForm.ornament_id}
                      onChange={(e) => setCheckInForm({ ...checkInForm, ornament_id: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Barcode</label>
                    <Input
                      value={checkInForm.barcode}
                      onChange={(e) => setCheckInForm({ ...checkInForm, barcode: e.target.value })}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">RFID Tag</label>
                    <Input
                      value={checkInForm.rfid_tag}
                      onChange={(e) => setCheckInForm({ ...checkInForm, rfid_tag: e.target.value })}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Seal Number</label>
                    <Input
                      value={checkInForm.seal_number}
                      onChange={(e) => setCheckInForm({ ...checkInForm, seal_number: e.target.value })}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Rack Number</label>
                    <Input
                      value={checkInForm.rack_number}
                      onChange={(e) => setCheckInForm({ ...checkInForm, rack_number: e.target.value })}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Shelf Number</label>
                    <Input
                      value={checkInForm.shelf_number}
                      onChange={(e) => setCheckInForm({ ...checkInForm, shelf_number: e.target.value })}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Slot Number</label>
                    <Input
                      value={checkInForm.slot_number}
                      onChange={(e) => setCheckInForm({ ...checkInForm, slot_number: e.target.value })}
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Remarks</label>
                  <Input
                    value={checkInForm.remarks}
                    onChange={(e) => setCheckInForm({ ...checkInForm, remarks: e.target.value })}
                  />
                </div>
                <div className="flex justify-end gap-2">
                  <Button type="button" variant="outline" onClick={() => setShowCheckInForm(false)}>
                    Cancel
                  </Button>
                  <Button type="submit">Check In</Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {/* Main Content - Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList>
            <TabsTrigger value="locations">Vault Locations</TabsTrigger>
            <TabsTrigger value="inventory">Inventory</TabsTrigger>
          </TabsList>

          {/* Vault Locations Tab */}
          <TabsContent value="locations">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {vaultLocations.map((vault) => {
                const itemCapacity = (vault.current_item_count / vault.max_capacity_items) * 100;
                const weightCapacity = (vault.current_weight_kg / vault.max_capacity_weight_kg) * 100;
                
                return (
                  <Card key={vault.id} className="hover:shadow-lg transition-shadow">
                    <CardHeader>
                      <div className="flex justify-between items-start">
                        <div>
                          <CardTitle className="text-lg">{vault.vault_name}</CardTitle>
                          <Badge variant="outline" className="mt-2">{vault.vault_code}</Badge>
                        </div>
                        <Badge 
                          variant={vault.security_level === 'High' ? 'default' : 'secondary'}
                          className={vault.security_level === 'High' ? 'bg-green-600' : ''}
                        >
                          {vault.security_level}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span>Item Capacity</span>
                          <span className={getCapacityColor(itemCapacity)}>
                            {vault.current_item_count} / {vault.max_capacity_items}
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${
                              itemCapacity >= 90 ? 'bg-red-600' : 
                              itemCapacity >= 75 ? 'bg-orange-600' : 
                              itemCapacity >= 50 ? 'bg-yellow-600' : 'bg-green-600'
                            }`}
                            style={{ width: `${Math.min(itemCapacity, 100)}%` }}
                          />
                        </div>
                      </div>
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span>Weight Capacity</span>
                          <span className={getCapacityColor(weightCapacity)}>
                            {vault.current_weight_kg.toFixed(2)} / {vault.max_capacity_weight_kg} kg
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${
                              weightCapacity >= 90 ? 'bg-red-600' : 
                              weightCapacity >= 75 ? 'bg-orange-600' : 
                              weightCapacity >= 50 ? 'bg-yellow-600' : 'bg-green-600'
                            }`}
                            style={{ width: `${Math.min(weightCapacity, 100)}%` }}
                          />
                        </div>
                      </div>
                      <div className="flex gap-2 pt-2">
                        <Button 
                          size="sm" 
                          variant="outline" 
                          className="flex-1"
                          onClick={() => {
                            setSelectedVault(vault.id);
                            setActiveTab('inventory');
                          }}
                        >
                          View Items
                        </Button>
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => {
                            setCheckInForm({ ...checkInForm, vault_location_id: vault.id });
                            setShowCheckInForm(true);
                          }}
                        >
                          Check In
                        </Button>
                      </div>
                      {vault.city && vault.state && (
                        <div className="text-xs text-muted-foreground border-t pt-2">
                          <div className="flex items-center gap-1">
                            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                            </svg>
                            {vault.city}, {vault.state}
                          </div>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </TabsContent>

          {/* Inventory Tab */}
          <TabsContent value="inventory">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <CardTitle>Vault Inventory</CardTitle>
                  <div className="flex gap-2">
                    <select
                      value={selectedVault}
                      onChange={(e) => setSelectedVault(e.target.value)}
                      className="px-3 py-2 border rounded-md"
                    >
                      <option value="">Select vault...</option>
                      {vaultLocations.map(v => (
                        <option key={v.id} value={v.id}>{v.vault_name}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {!selectedVault ? (
                  <div className="text-center py-12 text-muted-foreground">
                    Please select a vault location to view inventory
                  </div>
                ) : inventory.length === 0 ? (
                  <div className="text-center py-12 text-muted-foreground">
                    No items in this vault
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-muted/50">
                        <tr>
                          <th className="text-left p-4 font-medium">Loan ID</th>
                          <th className="text-left p-4 font-medium">Ornament ID</th>
                          <th className="text-left p-4 font-medium">Barcode/RFID</th>
                          <th className="text-left p-4 font-medium">Location</th>
                          <th className="text-left p-4 font-medium">Weight</th>
                          <th className="text-left p-4 font-medium">Check-In Date</th>
                          <th className="text-center p-4 font-medium">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y">
                        {inventory.map((item) => (
                          <tr key={item.id} className="hover:bg-muted/50">
                            <td className="p-4">{item.gold_loan_id}</td>
                            <td className="p-4">{item.ornament_id}</td>
                            <td className="p-4">
                              <div className="space-y-1">
                                {item.barcode && (
                                  <div className="text-sm flex items-center gap-1">
                                    <Badge variant="outline" className="text-xs">BC</Badge>
                                    {item.barcode}
                                  </div>
                                )}
                                {item.rfid_tag && (
                                  <div className="text-sm flex items-center gap-1">
                                    <Badge variant="outline" className="text-xs">RFID</Badge>
                                    {item.rfid_tag}
                                  </div>
                                )}
                              </div>
                            </td>
                            <td className="p-4 text-sm">
                              {item.rack_number && `R${item.rack_number}`}
                              {item.shelf_number && `-S${item.shelf_number}`}
                              {item.slot_number && `-SL${item.slot_number}`}
                            </td>
                            <td className="p-4">{item.weight_grams}g</td>
                            <td className="p-4 text-sm">{formatDateTime(item.check_in_date)}</td>
                            <td className="p-4 text-center">
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleCheckOut(item.id)}
                              >
                                Check Out
                              </Button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  );
}
