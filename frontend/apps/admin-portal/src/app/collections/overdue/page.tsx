"use client";

import { useState, useEffect } from "react";
import { 
  Search, 
  Filter,
  Phone,
  Mail,
  AlertTriangle,
  DollarSign,
  Calendar
} from "lucide-react";

interface OverdueAccount {
  id: number;
  account_number: string;
  customer_id: number;
  customer_name: string;
  customer_mobile: string;
  customer_email: string;
  loan_amount: number;
  outstanding_principal: number;
  outstanding_interest: number;
  overdue_amount: number;
  dpd: number;
  dpd_bucket: string;
  last_payment_date: string;
  last_payment_amount: number;
  penal_interest: number;
  total_overdue: number;
}

const dpdBucketColors: Record<string, string> = {
  "bucket_1_30": "bg-yellow-100 text-yellow-800 border-yellow-200",
  "bucket_31_60": "bg-orange-100 text-orange-800 border-orange-200",
  "bucket_61_90": "bg-red-100 text-red-800 border-red-200",
  "bucket_91_180": "bg-purple-100 text-purple-800 border-purple-200",
  "bucket_180_plus": "bg-gray-100 text-gray-800 border-gray-200",
};

const dpdBucketLabels: Record<string, string> = {
  "bucket_1_30": "0-30 Days",
  "bucket_31_60": "31-60 Days",
  "bucket_61_90": "61-90 Days",
  "bucket_91_180": "91-180 Days",
  "bucket_180_plus": "180+ Days (NPA)",
};

export default function OverdueAccountsPage() {
  const [accounts, setAccounts] = useState<OverdueAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterBucket, setFilterBucket] = useState<string>("all");
  const [selectedAccount, setSelectedAccount] = useState<OverdueAccount | null>(null);
  const [showActionModal, setShowActionModal] = useState(false);

  useEffect(() => {
    fetchOverdueAccounts();
  }, []);

  const fetchOverdueAccounts = async () => {
    try {
      setLoading(true);
      // TODO: Replace with actual API call
      const mockData: OverdueAccount[] = [
        {
          id: 1,
          account_number: "LA-202512-0045",
          customer_id: 101,
          customer_name: "Rajesh Kumar",
          customer_mobile: "+91 98765 43210",
          customer_email: "rajesh.kumar@example.com",
          loan_amount: 500000,
          outstanding_principal: 375000,
          outstanding_interest: 45000,
          overdue_amount: 125000,
          dpd: 95,
          dpd_bucket: "bucket_91_180",
          last_payment_date: "2025-10-02",
          last_payment_amount: 15000,
          penal_interest: 5000,
          total_overdue: 130000,
        },
        {
          id: 2,
          account_number: "LA-202511-0123",
          customer_id: 102,
          customer_name: "Priya Sharma",
          customer_mobile: "+91 98765 43211",
          customer_email: "priya.sharma@example.com",
          loan_amount: 300000,
          outstanding_principal: 245000,
          outstanding_interest: 28000,
          overdue_amount: 98000,
          dpd: 87,
          dpd_bucket: "bucket_61_90",
          last_payment_date: "2025-10-10",
          last_payment_amount: 12000,
          penal_interest: 3500,
          total_overdue: 101500,
        },
        {
          id: 3,
          account_number: "LA-202510-0234",
          customer_id: 103,
          customer_name: "Amit Patel",
          customer_mobile: "+91 98765 43212",
          customer_email: "amit.patel@example.com",
          loan_amount: 750000,
          outstanding_principal: 625000,
          outstanding_interest: 72000,
          overdue_amount: 87500,
          dpd: 112,
          dpd_bucket: "bucket_91_180",
          last_payment_date: "2025-09-15",
          last_payment_amount: 20000,
          penal_interest: 6200,
          total_overdue: 93700,
        },
        {
          id: 4,
          account_number: "LA-202512-0089",
          customer_id: 104,
          customer_name: "Sneha Reddy",
          customer_mobile: "+91 98765 43213",
          customer_email: "sneha.reddy@example.com",
          loan_amount: 400000,
          outstanding_principal: 325000,
          outstanding_interest: 38000,
          overdue_amount: 75000,
          dpd: 68,
          dpd_bucket: "bucket_61_90",
          last_payment_date: "2025-10-29",
          last_payment_amount: 15000,
          penal_interest: 2800,
          total_overdue: 77800,
        },
        {
          id: 5,
          account_number: "LA-202601-0012",
          customer_id: 105,
          customer_name: "Vikram Singh",
          customer_mobile: "+91 98765 43214",
          customer_email: "vikram.singh@example.com",
          loan_amount: 200000,
          outstanding_principal: 150000,
          outstanding_interest: 18000,
          overdue_amount: 25000,
          dpd: 22,
          dpd_bucket: "bucket_1_30",
          last_payment_date: "2025-12-14",
          last_payment_amount: 8000,
          penal_interest: 500,
          total_overdue: 25500,
        },
      ];
      setAccounts(mockData);
    } catch (error) {
      console.error("Error fetching overdue accounts:", error);
    } finally {
      setLoading(false);
    }
  };

  const filteredAccounts = accounts.filter((account) => {
    const matchesSearch = 
      account.account_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      account.customer_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      account.customer_mobile.includes(searchTerm);
    const matchesBucket = filterBucket === "all" || account.dpd_bucket === filterBucket;
    return matchesSearch && matchesBucket;
  });

  const handleRecordPayment = (account: OverdueAccount) => {
    setSelectedAccount(account);
    setShowActionModal(true);
  };

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900">Overdue Accounts</h2>
        <p className="mt-1 text-sm text-gray-500">
          Manage and follow up on overdue loan accounts
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Overdue</p>
              <p className="mt-1 text-2xl font-bold text-gray-900">{accounts.length}</p>
            </div>
            <AlertTriangle className="h-8 w-8 text-orange-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Amount</p>
              <p className="mt-1 text-2xl font-bold text-red-600">
                ₹{accounts.reduce((sum, acc) => sum + acc.total_overdue, 0).toLocaleString("en-IN", {
                  maximumFractionDigits: 0,
                })}
              </p>
            </div>
            <DollarSign className="h-8 w-8 text-red-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Avg DPD</p>
              <p className="mt-1 text-2xl font-bold text-orange-600">
                {Math.round(accounts.reduce((sum, acc) => sum + acc.dpd, 0) / accounts.length)} days
              </p>
            </div>
            <Calendar className="h-8 w-8 text-orange-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">High Priority</p>
              <p className="mt-1 text-2xl font-bold text-purple-600">
                {accounts.filter(a => a.dpd > 60).length}
              </p>
            </div>
            <AlertTriangle className="h-8 w-8 text-purple-500" />
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search by account, customer, mobile..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
            />
          </div>
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <select
              value={filterBucket}
              onChange={(e) => setFilterBucket(e.target.value)}
              className="pl-10 w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent appearance-none"
            >
              <option value="all">All Buckets</option>
              <option value="bucket_1_30">0-30 Days</option>
              <option value="bucket_31_60">31-60 Days</option>
              <option value="bucket_61_90">61-90 Days</option>
              <option value="bucket_91_180">91-180 Days</option>
              <option value="bucket_180_plus">180+ Days (NPA)</option>
            </select>
          </div>
          <div className="flex items-center justify-end">
            <span className="text-sm text-gray-600">
              {filteredAccounts.length} accounts found
            </span>
          </div>
        </div>
      </div>

      {/* Accounts Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-gray-500">Loading overdue accounts...</div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Account / Customer
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Contact
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Outstanding
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Overdue Amount
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    DPD
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Payment
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredAccounts.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-6 py-12 text-center text-gray-500">
                      No overdue accounts found
                    </td>
                  </tr>
                ) : (
                  filteredAccounts.map((account) => (
                    <tr key={account.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div className="text-sm font-medium text-blue-600">
                          {account.account_number}
                        </div>
                        <div className="text-sm text-gray-900">{account.customer_name}</div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center text-sm text-gray-900">
                          <Phone className="h-4 w-4 mr-1 text-gray-400" />
                          {account.customer_mobile}
                        </div>
                        <div className="flex items-center text-xs text-gray-500 mt-1">
                          <Mail className="h-3 w-3 mr-1 text-gray-400" />
                          {account.customer_email}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="text-sm font-semibold text-gray-900">
                          ₹{(account.outstanding_principal + account.outstanding_interest).toLocaleString("en-IN")}
                        </div>
                        <div className="text-xs text-gray-500">
                          P: ₹{account.outstanding_principal.toLocaleString("en-IN", { maximumFractionDigits: 0 })}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="text-sm font-bold text-red-600">
                          ₹{account.total_overdue.toLocaleString("en-IN")}
                        </div>
                        {account.penal_interest > 0 && (
                          <div className="text-xs text-red-500">
                            +₹{account.penal_interest.toLocaleString("en-IN")} penal
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 text-center">
                        <div>
                          <span className={`px-3 py-1 text-xs font-bold rounded-full ${
                            dpdBucketColors[account.dpd_bucket]
                          } border`}>
                            {account.dpd} days
                          </span>
                          <div className="text-xs text-gray-500 mt-1">
                            {dpdBucketLabels[account.dpd_bucket]}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900">
                          {new Date(account.last_payment_date).toLocaleDateString("en-IN", {
                            year: "numeric",
                            month: "short",
                            day: "numeric",
                          })}
                        </div>
                        <div className="text-xs text-gray-500">
                          ₹{account.last_payment_amount.toLocaleString("en-IN")}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex justify-end space-x-2">
                          <button
                            onClick={() => handleRecordPayment(account)}
                            className="text-sm px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700"
                          >
                            Record Payment
                          </button>
                          <button className="text-sm px-3 py-1 bg-orange-600 text-white rounded hover:bg-orange-700">
                            Follow Up
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
