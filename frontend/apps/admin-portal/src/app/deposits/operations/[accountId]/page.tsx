'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useParams } from 'next/navigation';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { depositService } from '@/services/deposit.service';
import { useToast } from '@/hooks/use-toast';
import {
  Snowflake as FreezeIcon,
  Lock as LockIcon,
  ArrowRightLeft as TransferIcon,
  Users as UsersIcon,
  AlertTriangle as AlertTriangleIcon,
  CheckCircle as CheckCircleIcon,
  XCircle as XCircleIcon,
  Info as InfoIcon,
} from 'lucide-react';

export default function AdvancedOperationsPage() {
  const params = useParams();
  const accountId = parseInt(params.accountId as string);
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState('freeze');

  // Fetch account details
  const { data: account, isLoading: accountLoading } = useQuery({
    queryKey: ['deposit-account', accountId],
    queryFn: () => depositService.getAccount(accountId.toString()),
  });

  // Freeze/Unfreeze Account
  const [freezeData, setFreezeData] = useState({
    reason: '',
    notes: '',
  });

  const freezeMutation = useMutation({
    mutationFn: (data: any) => depositService.freezeAccount(accountId, data),
    onSuccess: () => {
      toast({
        title: 'Success',
        description: 'Account frozen successfully',
      });
      queryClient.invalidateQueries({ queryKey: ['deposit-account', accountId] });
      setFreezeData({ reason: '', notes: '' });
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to freeze account',
        variant: 'destructive',
      });
    },
  });

  const unfreezeMutation = useMutation({
    mutationFn: (data: { release_reason: string }) => depositService.unfreezeAccount(accountId, data),
    onSuccess: () => {
      toast({
        title: 'Success',
        description: 'Account unfrozen successfully',
      });
      queryClient.invalidateQueries({ queryKey: ['deposit-account', accountId] });
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to unfreeze account',
        variant: 'destructive',
      });
    },
  });

  // Lien Management
  const [lienData, setLienData] = useState({
    amount: '',
    reason: '',
    reference_number: '',
    expiry_date: '',
    notes: '',
  });

  const createLienMutation = useMutation({
    mutationFn: (data: any) => depositService.markLien(accountId, data),
    onSuccess: () => {
      toast({
        title: 'Success',
        description: 'Lien created successfully',
      });
      queryClient.invalidateQueries({ queryKey: ['deposit-account', accountId] });
      setLienData({ amount: '', reason: '', reference_number: '', expiry_date: '', notes: '' });
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to create lien',
        variant: 'destructive',
      });
    },
  });

  const releaseLienMutation = useMutation({
    mutationFn: (lienId: number) => depositService.releaseLien(accountId, lienId, {}),
    onSuccess: () => {
      toast({
        title: 'Success',
        description: 'Lien released successfully',
      });
      queryClient.invalidateQueries({ queryKey: ['deposit-account', accountId] });
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to release lien',
        variant: 'destructive',
      });
    },
  });

  // Transfer Account
  const [transferData, setTransferData] = useState({
    new_customer_id: '',
    reason: '',
    effective_date: '',
    notes: '',
  });

  const transferMutation = useMutation({
    mutationFn: (data: any) => depositService.transferAccount(accountId, data),
    onSuccess: () => {
      toast({
        title: 'Success',
        description: 'Account transferred successfully',
      });
      queryClient.invalidateQueries({ queryKey: ['deposit-account', accountId] });
      setTransferData({ new_customer_id: '', reason: '', effective_date: '', notes: '' });
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to transfer account',
        variant: 'destructive',
      });
    },
  });

  // Joint Account Management
  const [jointAccountData, setJointAccountData] = useState({
    customer_id: '',
    relationship: '',
    holding_pattern: 'joint',
    nomination_percentage: '',
  });

  const addJointHolderMutation = useMutation({
    mutationFn: (data: any) => depositService.addJointHolder(accountId, data),
    onSuccess: () => {
      toast({
        title: 'Success',
        description: 'Joint holder added successfully',
      });
      queryClient.invalidateQueries({ queryKey: ['deposit-account', accountId] });
      setJointAccountData({ customer_id: '', relationship: '', holding_pattern: 'joint', nomination_percentage: '' });
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to add joint holder',
        variant: 'destructive',
      });
    },
  });

  const removeJointHolderMutation = useMutation({
    mutationFn: (holderId: number) => depositService.removeJointHolder(accountId, holderId, { removal_reason: 'User requested removal' }),
    onSuccess: () => {
      toast({
        title: 'Success',
        description: 'Joint holder removed successfully',
      });
      queryClient.invalidateQueries({ queryKey: ['deposit-account', accountId] });
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to remove joint holder',
        variant: 'destructive',
      });
    },
  });

  if (accountLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-lg">Loading account details...</div>
        </div>
      </DashboardLayout>
    );
  }

  const handleFreeze = () => {
    if (!freezeData.reason.trim()) {
      toast({
        title: 'Error',
        description: 'Please provide a reason for freezing',
        variant: 'destructive',
      });
      return;
    }
    freezeMutation.mutate({
      freeze_type: 'full',
      reason: freezeData.reason,
      reference_number: freezeData.notes,
    });
  };

  const handleUnfreeze = () => {
    if (window.confirm('Are you sure you want to unfreeze this account?')) {
      unfreezeMutation.mutate({ release_reason: 'Account unfrozen by admin' });
    }
  };

  const handleCreateLien = () => {
    if (!lienData.amount || parseFloat(lienData.amount) <= 0) {
      toast({
        title: 'Error',
        description: 'Please provide a valid lien amount',
        variant: 'destructive',
      });
      return;
    }
    if (!lienData.reason.trim()) {
      toast({
        title: 'Error',
        description: 'Please provide a reason for the lien',
        variant: 'destructive',
      });
      return;
    }
    createLienMutation.mutate({
      lien_amount: parseFloat(lienData.amount),
      lien_reason: lienData.reason,
      reference_type: 'manual',
      reference_number: lienData.reference_number || 'N/A',
    });
  };

  const handleTransfer = () => {
    if (!transferData.new_customer_id.trim()) {
      toast({
        title: 'Error',
        description: 'Please provide the new customer ID',
        variant: 'destructive',
      });
      return;
    }
    if (!transferData.reason.trim()) {
      toast({
        title: 'Error',
        description: 'Please provide a reason for transfer',
        variant: 'destructive',
      });
      return;
    }
    if (window.confirm('Are you sure you want to transfer this account? This action cannot be undone.')) {
      transferMutation.mutate(transferData);
    }
  };

  const handleAddJointHolder = () => {
    if (!jointAccountData.customer_id.trim()) {
      toast({
        title: 'Error',
        description: 'Please provide the customer ID',
        variant: 'destructive',
      });
      return;
    }
    if (!jointAccountData.relationship.trim()) {
      toast({
        title: 'Error',
        description: 'Please provide the relationship',
        variant: 'destructive',
      });
      return;
    }
    addJointHolderMutation.mutate(jointAccountData);
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold">Advanced Operations</h1>
          <p className="text-gray-600 mt-2">
            Account: {account?.data?.account_number} - {account?.data?.customer_name}
          </p>
        </div>

        {/* Account Status Alert */}
        {account?.data?.is_frozen && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
            <AlertTriangleIcon className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-red-900">Account is Frozen</h3>
              <p className="text-red-700 text-sm mt-1">
                This account is currently frozen. No transactions can be performed until unfrozen.
              </p>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('freeze')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'freeze'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <FreezeIcon className="h-5 w-5 inline mr-2" />
              Freeze/Unfreeze
            </button>
            <button
              onClick={() => setActiveTab('lien')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'lien'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <LockIcon className="h-5 w-5 inline mr-2" />
              Lien Management
            </button>
            <button
              onClick={() => setActiveTab('transfer')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'transfer'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <TransferIcon className="h-5 w-5 inline mr-2" />
              Transfer Account
            </button>
            <button
              onClick={() => setActiveTab('joint')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'joint'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <UsersIcon className="h-5 w-5 inline mr-2" />
              Joint Account
            </button>
          </nav>
        </div>

        {/* Freeze/Unfreeze Tab */}
        {activeTab === 'freeze' && (
          <div className="space-y-6">
            <Card>
              <div className="p-6">
                <div className="flex items-start gap-3 mb-6">
                  <InfoIcon className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <h3 className="font-semibold text-gray-900">Account Freeze/Unfreeze</h3>
                    <p className="text-gray-600 text-sm mt-1">
                      Freeze an account to prevent all transactions temporarily. Unfreeze to restore normal operations.
                      Frozen accounts cannot process deposits, withdrawals, or interest postings.
                    </p>
                  </div>
                </div>

                {account?.data?.is_frozen ? (
                  <div className="space-y-4">
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                      <h4 className="font-semibold text-yellow-900">Account is Currently Frozen</h4>
                      <p className="text-yellow-700 text-sm mt-1">
                        Frozen on: {new Date(account.data.frozen_at || '').toLocaleDateString()}
                      </p>
                      <p className="text-yellow-700 text-sm">
                        Reason: {account.data.freeze_reason || 'Not specified'}
                      </p>
                    </div>
                    <Button
                      onClick={handleUnfreeze}
                      disabled={unfreezeMutation.isPending}
                      className="w-full"
                    >
                      <CheckCircleIcon className="h-5 w-5 mr-2" />
                      {unfreezeMutation.isPending ? 'Unfreezing...' : 'Unfreeze Account'}
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Reason for Freezing *
                      </label>
                      <select
                        value={freezeData.reason}
                        onChange={(e) => setFreezeData({ ...freezeData, reason: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="">Select a reason</option>
                        <option value="legal_hold">Legal Hold</option>
                        <option value="suspected_fraud">Suspected Fraud</option>
                        <option value="customer_request">Customer Request</option>
                        <option value="compliance_review">Compliance Review</option>
                        <option value="dispute">Dispute</option>
                        <option value="other">Other</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Additional Notes
                      </label>
                      <textarea
                        value={freezeData.notes}
                        onChange={(e) => setFreezeData({ ...freezeData, notes: e.target.value })}
                        rows={3}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="Provide any additional details..."
                      />
                    </div>

                    <Button
                      onClick={handleFreeze}
                      disabled={freezeMutation.isPending}
                      variant="destructive"
                      className="w-full"
                    >
                      <XCircleIcon className="h-5 w-5 mr-2" />
                      {freezeMutation.isPending ? 'Freezing...' : 'Freeze Account'}
                    </Button>
                  </div>
                )}
              </div>
            </Card>
          </div>
        )}

        {/* Lien Management Tab */}
        {activeTab === 'lien' && (
          <div className="space-y-6">
            <Card>
              <div className="p-6">
                <div className="flex items-start gap-3 mb-6">
                  <InfoIcon className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <h3 className="font-semibold text-gray-900">Lien Management</h3>
                    <p className="text-gray-600 text-sm mt-1">
                      Place a lien to mark a specific amount as unavailable for withdrawal. Commonly used for loan collateral,
                      legal holds, or security deposits. Multiple liens can be active simultaneously.
                    </p>
                  </div>
                </div>

                <h4 className="font-semibold text-gray-900 mb-4">Create New Lien</h4>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Lien Amount *
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        value={lienData.amount}
                        onChange={(e) => setLienData({ ...lienData, amount: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="0.00"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Expiry Date (Optional)
                      </label>
                      <input
                        type="date"
                        value={lienData.expiry_date}
                        onChange={(e) => setLienData({ ...lienData, expiry_date: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Reason *
                    </label>
                    <select
                      value={lienData.reason}
                      onChange={(e) => setLienData({ ...lienData, reason: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="">Select a reason</option>
                      <option value="loan_collateral">Loan Collateral</option>
                      <option value="legal_order">Legal Order</option>
                      <option value="security_deposit">Security Deposit</option>
                      <option value="guarantee">Guarantee</option>
                      <option value="other">Other</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Reference Number
                    </label>
                    <input
                      type="text"
                      value={lienData.reference_number}
                      onChange={(e) => setLienData({ ...lienData, reference_number: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="e.g., Loan ID, Court Order Number"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Additional Notes
                    </label>
                    <textarea
                      value={lienData.notes}
                      onChange={(e) => setLienData({ ...lienData, notes: e.target.value })}
                      rows={2}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Any additional details..."
                    />
                  </div>

                  <Button
                    onClick={handleCreateLien}
                    disabled={createLienMutation.isPending}
                    className="w-full"
                  >
                    <LockIcon className="h-5 w-5 mr-2" />
                    {createLienMutation.isPending ? 'Creating Lien...' : 'Create Lien'}
                  </Button>
                </div>
              </div>
            </Card>

            {/* Active Liens */}
            {account?.data?.liens && account.data.liens.length > 0 && (
              <Card>
                <div className="p-6">
                  <h4 className="font-semibold text-gray-900 mb-4">Active Liens</h4>
                  <div className="space-y-3">
                    {account.data.liens.map((lien: any) => (
                      <div key={lien.id} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <span className="font-semibold text-gray-900">
                                ₹{parseFloat(lien.amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                              </span>
                              <span className="px-2 py-1 bg-orange-100 text-orange-800 text-xs rounded">
                                {lien.reason}
                              </span>
                            </div>
                            <p className="text-sm text-gray-600 mt-1">
                              Created: {new Date(lien.created_at).toLocaleDateString()}
                            </p>
                            {lien.expiry_date && (
                              <p className="text-sm text-gray-600">
                                Expires: {new Date(lien.expiry_date).toLocaleDateString()}
                              </p>
                            )}
                            {lien.reference_number && (
                              <p className="text-sm text-gray-600">
                                Ref: {lien.reference_number}
                              </p>
                            )}
                          </div>
                          <Button
                            onClick={() => releaseLienMutation.mutate(lien.id)}
                            disabled={releaseLienMutation.isPending}
                            variant="secondary"
                            size="sm"
                          >
                            Release
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </Card>
            )}
          </div>
        )}

        {/* Transfer Account Tab */}
        {activeTab === 'transfer' && (
          <div className="space-y-6">
            <Card>
              <div className="p-6">
                <div className="flex items-start gap-3 mb-6">
                  <InfoIcon className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <h3 className="font-semibold text-gray-900">Transfer Account Ownership</h3>
                    <p className="text-gray-600 text-sm mt-1">
                      Transfer account ownership to another customer. This is commonly used for inheritance, gift transfers,
                      or legal ownership changes. The account number remains the same but is linked to a new customer.
                    </p>
                  </div>
                </div>

                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
                  <div className="flex gap-3">
                    <AlertTriangleIcon className="h-5 w-5 text-yellow-600 flex-shrink-0" />
                    <div>
                      <h4 className="font-semibold text-yellow-900">Important Warning</h4>
                      <p className="text-yellow-700 text-sm mt-1">
                        This action cannot be undone. Verify the new customer details carefully before proceeding.
                        All future statements and communications will be sent to the new customer.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      New Customer ID *
                    </label>
                    <input
                      type="text"
                      value={transferData.new_customer_id}
                      onChange={(e) => setTransferData({ ...transferData, new_customer_id: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Enter customer ID"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Reason for Transfer *
                    </label>
                    <select
                      value={transferData.reason}
                      onChange={(e) => setTransferData({ ...transferData, reason: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="">Select a reason</option>
                      <option value="inheritance">Inheritance</option>
                      <option value="gift">Gift</option>
                      <option value="legal_order">Legal Order</option>
                      <option value="nominee_claim">Nominee Claim</option>
                      <option value="sale">Sale/Purchase</option>
                      <option value="other">Other</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Effective Date *
                    </label>
                    <input
                      type="date"
                      value={transferData.effective_date}
                      onChange={(e) => setTransferData({ ...transferData, effective_date: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Supporting Documents & Notes
                    </label>
                    <textarea
                      value={transferData.notes}
                      onChange={(e) => setTransferData({ ...transferData, notes: e.target.value })}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Document references, legal order numbers, etc."
                    />
                  </div>

                  <Button
                    onClick={handleTransfer}
                    disabled={transferMutation.isPending}
                    variant="destructive"
                    className="w-full"
                  >
                    <TransferIcon className="h-5 w-5 mr-2" />
                    {transferMutation.isPending ? 'Transferring...' : 'Transfer Account'}
                  </Button>
                </div>
              </div>
            </Card>
          </div>
        )}

        {/* Joint Account Tab */}
        {activeTab === 'joint' && (
          <div className="space-y-6">
            <Card>
              <div className="p-6">
                <div className="flex items-start gap-3 mb-6">
                  <InfoIcon className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <h3 className="font-semibold text-gray-900">Joint Account Management</h3>
                    <p className="text-gray-600 text-sm mt-1">
                      Add or remove joint holders for this account. Joint holders share ownership and can operate the account
                      based on the holding pattern (Either or Survivor, Jointly, Former or Survivor).
                    </p>
                  </div>
                </div>

                <h4 className="font-semibold text-gray-900 mb-4">Add Joint Holder</h4>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Customer ID *
                    </label>
                    <input
                      type="text"
                      value={jointAccountData.customer_id}
                      onChange={(e) => setJointAccountData({ ...jointAccountData, customer_id: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Enter customer ID to add as joint holder"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Relationship to Primary Holder *
                    </label>
                    <select
                      value={jointAccountData.relationship}
                      onChange={(e) => setJointAccountData({ ...jointAccountData, relationship: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="">Select relationship</option>
                      <option value="spouse">Spouse</option>
                      <option value="parent">Parent</option>
                      <option value="child">Child</option>
                      <option value="sibling">Sibling</option>
                      <option value="business_partner">Business Partner</option>
                      <option value="other">Other</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Holding Pattern *
                    </label>
                    <select
                      value={jointAccountData.holding_pattern}
                      onChange={(e) => setJointAccountData({ ...jointAccountData, holding_pattern: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="joint">Joint - All holders must sign</option>
                      <option value="either">Either or Survivor - Any holder can operate</option>
                      <option value="former">Former or Survivor - Primary holder or survivor</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Nomination Percentage (Optional)
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="100"
                      step="0.01"
                      value={jointAccountData.nomination_percentage}
                      onChange={(e) => setJointAccountData({ ...jointAccountData, nomination_percentage: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="0-100%"
                    />
                    <p className="text-sm text-gray-500 mt-1">
                      Leave blank for equal distribution among all holders
                    </p>
                  </div>

                  <Button
                    onClick={handleAddJointHolder}
                    disabled={addJointHolderMutation.isPending}
                    className="w-full"
                  >
                    <UsersIcon className="h-5 w-5 mr-2" />
                    {addJointHolderMutation.isPending ? 'Adding...' : 'Add Joint Holder'}
                  </Button>
                </div>
              </div>
            </Card>

            {/* Existing Joint Holders */}
            {account?.data?.joint_holders && account.data.joint_holders.length > 0 && (
              <Card>
                <div className="p-6">
                  <h4 className="font-semibold text-gray-900 mb-4">Current Joint Holders</h4>
                  <div className="space-y-3">
                    {account.data.joint_holders.map((holder: any) => (
                      <div key={holder.id} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <span className="font-semibold text-gray-900">{holder.customer_name}</span>
                              {holder.is_primary && (
                                <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                                  Primary
                                </span>
                              )}
                            </div>
                            <p className="text-sm text-gray-600 mt-1">
                              Customer ID: {holder.customer_id}
                            </p>
                            <p className="text-sm text-gray-600">
                              Relationship: {holder.relationship}
                            </p>
                            <p className="text-sm text-gray-600">
                              Holding Pattern: {holder.holding_pattern}
                            </p>
                            {holder.nomination_percentage && (
                              <p className="text-sm text-gray-600">
                                Share: {holder.nomination_percentage}%
                              </p>
                            )}
                          </div>
                          {!holder.is_primary && (
                            <Button
                              onClick={() => removeJointHolderMutation.mutate(holder.id)}
                              disabled={removeJointHolderMutation.isPending}
                              variant="danger"
                              size="sm"
                            >
                              Remove
                            </Button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </Card>
            )}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
