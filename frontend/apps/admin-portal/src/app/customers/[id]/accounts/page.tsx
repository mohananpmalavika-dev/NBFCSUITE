"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { 
  Building2, 
  Plus, 
  Edit2, 
  Trash2, 
  CheckCircle, 
  XCircle, 
  Star,
  CreditCard,
  TrendingUp,
  TrendingDown,
  AlertCircle
} from "lucide-react";
import CustomerBankAccountModal from "@/components/CustomerBankAccountModal";

interface BankAccount {
  id: number;
  customer_id: number;
  bank_id: number;
  bank_name?: string;
  branch_name?: string;
  account_number: string;
  account_holder_name: string;
  account_type: string;
  ifsc_code: string;
  is_primary: boolean;
  is_verified: boolean;
  verification_method?: string;
  verification_date?: string;
  penny_drop_status?: string;
  use_for_disbursement: boolean;
  use_for_collection: boolean;
  is_active: boolean;
  created_at: string;
}

interface Bank {
  id: number;
  name: string;
  code: string;
}

export default function CustomerAccountsPage() {
  const params = useParams();
  const customerId = params?.id as string;

  const [accounts, setAccounts] = useState<BankAccount[]>([]);
  const [banks, setBanks] = useState<Bank[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingAccount, setEditingAccount] = useState<BankAccount | undefined>();

  useEffect(() => {
    if (customerId) {
      fetchAccounts();
      fetchBanks();
    }
  }, [customerId]);

  const fetchAccounts = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/v1/customers/${customerId}/accounts`, {
        headers: { "Content-Type": "application/json" }
      });

      if (response.ok) {
        const data = await response.json();
        setAccounts(data);
      }
    } catch (error) {
      console.error("Error fetching accounts:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchBanks = async () => {
    try {
      const response = await fetch("/api/v1/masterdata/banks", {
        headers: { "Content-Type": "application/json" }
      });

      if (response.ok) {
        const data = await response.json();
        setBanks(data.items || data);
      }
    } catch (error) {
      console.error("Error fetching banks:", error);
    }
  };

  const handleSave = async (data: any) => {
    try {
      const url = editingAccount
        ? `/api/v1/customers/${customerId}/accounts/${editingAccount.id}`
        : `/api/v1/customers/${customerId}/accounts`;

      const method = editingAccount ? "PUT" : "POST";

      const response = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to save");
      }

      await fetchAccounts();
      setIsModalOpen(false);
      setEditingAccount(undefined);
    } catch (error) {
      throw error;
    }
  };

  const handleEdit = (account: BankAccount) => {
    setEditingAccount(account);
    setIsModalOpen(true);
  };

  const handleDelete = async (accountId: number) => {
    if (!confirm("Are you sure you want to delete this bank account?")) return;

    try {
      const response = await fetch(`/api/v1/customers/${customerId}/accounts/${accountId}`, {
        method: "DELETE",
        headers: { "Content-Type": "application/json" }
      });

      if (response.ok) {
        await fetchAccounts();
      } else {
        const error = await response.json();
        alert(error.detail || "Failed to delete account");
      }
    } catch (error) {
      console.error("Error deleting account:", error);
      alert("Failed to delete account");
    }
  };

  const handleSetPrimary = async (accountId: number) => {
    try {
      const response = await fetch(
        `/api/v1/customers/${customerId}/accounts/${accountId}/set-primary`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" }
        }
      );

      if (response.ok) {
        await fetchAccounts();
        alert("Primary account updated successfully");
      } else {
        alert("Failed to update primary account");
      }
    } catch (error) {
      console.error("Error setting primary:", error);
      alert("Failed to update primary account");
    }
  };

  const handleVerify = async (accountId: number) => {
    if (!confirm("Mark this account as verified?")) return;

    try {
      const response = await fetch(
        `/api/v1/customers/${customerId}/accounts/${accountId}/verify`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            verification_method: "manual",
            verified: true
          })
        }
      );

      if (response.ok) {
        await fetchAccounts();
        alert("Account verified successfully");
      } else {
        alert("Failed to verify account");
      }
    } catch (error) {
      console.error("Error verifying account:", error);
      alert("Failed to verify account");
    }
  };

  const handlePennyDrop = async (accountId: number) => {
    const amount = prompt("Enter penny drop amount (e.g., 1.00):");
    if (!amount) return;

    const referenceId = `PD${Date.now()}`;

    try {
      const response = await fetch(
        `/api/v1/customers/${customerId}/accounts/${accountId}/penny-drop`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            amount: parseFloat(amount),
            reference_id: referenceId,
            status: "success"
          })
        }
      );

      if (response.ok) {
        await fetchAccounts();
        alert("Penny drop verification initiated");
      } else {
        alert("Failed to initiate penny drop");
      }
    } catch (error) {
      console.error("Error with penny drop:", error);
      alert("Failed to initiate penny drop");
    }
  };

  const handleAddNew = () => {
    setEditingAccount(undefined);
    setIsModalOpen(true);
  };

  const getAccountTypeBadge = (type: string) => {
    const types: Record<string, { bg: string; text: string; label: string }> = {
      savings: { bg: "bg-blue-100", text: "text-blue-800", label: "Savings" },
      current: { bg: "bg-purple-100", text: "text-purple-800", label: "Current" },
      overdraft: { bg: "bg-orange-100", text: "text-orange-800", label: "Overdraft" },
      cash_credit: { bg: "bg-green-100", text: "text-green-800", label: "Cash Credit" }
    };
    
    const badge = types[type] || types.savings;
    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${badge.bg} ${badge.text}`}>
        {badge.label}
      </span>
    );
  };

  const primaryAccount = accounts.find(a => a.is_primary);
  const verifiedAccounts = accounts.filter(a => a.is_verified);
  const activeAccounts = accounts.filter(a => a.is_active);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Bank Accounts</h2>
          <p className="text-sm text-gray-600 mt-1">
            Manage customer bank accounts for disbursement and collection
          </p>
        </div>
        <button
          onClick={handleAddNew}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Plus className="w-4 h-4" />
          Add Account
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Accounts</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{accounts.length}</p>
            </div>
            <CreditCard className="w-8 h-8 text-blue-600 opacity-20" />
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Verified</p>
              <p className="text-2xl font-bold text-green-600 mt-1">{verifiedAccounts.length}</p>
            </div>
            <CheckCircle className="w-8 h-8 text-green-600 opacity-20" />
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Active</p>
              <p className="text-2xl font-bold text-blue-600 mt-1">{activeAccounts.length}</p>
            </div>
            <Building2 className="w-8 h-8 text-blue-600 opacity-20" />
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Primary Account</p>
              <p className="text-sm font-medium text-gray-900 mt-1">
                {primaryAccount ? '✓ Set' : 'Not Set'}
              </p>
            </div>
            <Star className="w-8 h-8 text-yellow-600 opacity-20" />
          </div>
        </div>
      </div>

      {/* Warning if no primary account */}
      {accounts.length > 0 && !primaryAccount && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="text-sm font-semibold text-yellow-900">No Primary Account Set</h4>
              <p className="text-sm text-yellow-700 mt-1">
                Please designate one account as primary for default transactions.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Accounts List */}
      {accounts.length === 0 ? (
        <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
          <Building2 className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-sm text-gray-600 mb-4">No bank accounts added yet</p>
          <button
            onClick={handleAddNew}
            className="text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            Add your first bank account
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {accounts.map((account) => (
            <div
              key={account.id}
              className={`bg-white rounded-lg border-2 p-6 hover:shadow-md transition-shadow ${
                account.is_primary ? 'border-yellow-400' : 'border-gray-200'
              }`}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Building2 className="w-6 h-6 text-blue-600" />
                  </div>
                  
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {account.bank_name}
                      </h3>
                      {account.is_primary && (
                        <span className="flex items-center gap-1 px-2 py-1 bg-yellow-100 text-yellow-800 text-xs font-medium rounded-full">
                          <Star className="w-3 h-3 fill-yellow-600" />
                          Primary
                        </span>
                      )}
                      {account.is_verified && (
                        <span className="flex items-center gap-1 px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
                          <CheckCircle className="w-3 h-3" />
                          Verified
                        </span>
                      )}
                      {!account.is_active && (
                        <span className="flex items-center gap-1 px-2 py-1 bg-gray-100 text-gray-800 text-xs font-medium rounded-full">
                          <XCircle className="w-3 h-3" />
                          Inactive
                        </span>
                      )}
                    </div>
                    
                    <p className="text-sm text-gray-600">{account.account_holder_name}</p>
                    <p className="text-sm font-mono text-gray-900 mt-1">
                      {account.account_number}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleEdit(account)}
                    className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
                    title="Edit"
                  >
                    <Edit2 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(account.id)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
                    title="Delete"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Account Details Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div>
                  <p className="text-xs text-gray-600">Account Type</p>
                  <div className="mt-1">{getAccountTypeBadge(account.account_type)}</div>
                </div>
                
                <div>
                  <p className="text-xs text-gray-600">IFSC Code</p>
                  <p className="text-sm font-mono font-medium text-gray-900 mt-1">
                    {account.ifsc_code}
                  </p>
                </div>

                {account.branch_name && (
                  <div>
                    <p className="text-xs text-gray-600">Branch</p>
                    <p className="text-sm font-medium text-gray-900 mt-1">
                      {account.branch_name}
                    </p>
                  </div>
                )}

                {account.verification_method && (
                  <div>
                    <p className="text-xs text-gray-600">Verification Method</p>
                    <p className="text-sm font-medium text-gray-900 mt-1 capitalize">
                      {account.verification_method.replace('_', ' ')}
                    </p>
                  </div>
                )}
              </div>

              {/* Usage Flags */}
              <div className="flex items-center gap-4 mb-4">
                {account.use_for_disbursement && (
                  <div className="flex items-center gap-1.5 px-3 py-1.5 bg-green-50 text-green-700 text-xs font-medium rounded-lg">
                    <TrendingDown className="w-3.5 h-3.5" />
                    Disbursement
                  </div>
                )}
                {account.use_for_collection && (
                  <div className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-50 text-blue-700 text-xs font-medium rounded-lg">
                    <TrendingUp className="w-3.5 h-3.5" />
                    Collection
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-2 pt-4 border-t">
                {!account.is_primary && (
                  <button
                    onClick={() => handleSetPrimary(account.id)}
                    className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-yellow-700 bg-yellow-50 rounded-lg hover:bg-yellow-100"
                  >
                    <Star className="w-4 h-4" />
                    Set as Primary
                  </button>
                )}
                
                {!account.is_verified && (
                  <>
                    <button
                      onClick={() => handleVerify(account.id)}
                      className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-green-700 bg-green-50 rounded-lg hover:bg-green-100"
                    >
                      <CheckCircle className="w-4 h-4" />
                      Verify Account
                    </button>
                    
                    <button
                      onClick={() => handlePennyDrop(account.id)}
                      className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-blue-700 bg-blue-50 rounded-lg hover:bg-blue-100"
                    >
                      Penny Drop Test
                    </button>
                  </>
                )}

                {account.verification_date && (
                  <p className="text-xs text-gray-500 ml-auto">
                    Verified on {new Date(account.verification_date).toLocaleDateString('en-IN')}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      <CustomerBankAccountModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setEditingAccount(undefined);
        }}
        onSave={handleSave}
        account={editingAccount}
        banks={banks}
      />
    </div>
  );
}
