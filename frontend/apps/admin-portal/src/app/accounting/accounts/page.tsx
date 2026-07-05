"use client";

import { useState, useEffect } from "react";
import { 
  Plus, 
  Search, 
  ChevronRight, 
  ChevronDown,
  Edit,
  Trash2,
  Filter
} from "lucide-react";

interface Account {
  id: number;
  account_code: string;
  account_name: string;
  account_type: string;
  account_sub_type: string;
  current_balance: number;
  is_group: boolean;
  is_active: boolean;
  children?: Account[];
}

const accountTypeColors: Record<string, string> = {
  asset: "bg-blue-100 text-blue-800",
  liability: "bg-red-100 text-red-800",
  equity: "bg-purple-100 text-purple-800",
  income: "bg-green-100 text-green-800",
  expense: "bg-orange-100 text-orange-800",
};

function AccountRow({ account, level = 0 }: { account: Account; level?: number }) {
  const [isExpanded, setIsExpanded] = useState(level === 0);
  const hasChildren = account.children && account.children.length > 0;

  return (
    <>
      <tr className="hover:bg-gray-50 border-b border-gray-200">
        <td className="px-6 py-4 whitespace-nowrap">
          <div className="flex items-center" style={{ paddingLeft: `${level * 2}rem` }}>
            {hasChildren && (
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="mr-2 text-gray-400 hover:text-gray-600"
              >
                {isExpanded ? (
                  <ChevronDown className="h-4 w-4" />
                ) : (
                  <ChevronRight className="h-4 w-4" />
                )}
              </button>
            )}
            <div className="flex items-center">
              <span className="text-sm font-medium text-gray-900">
                {account.account_code}
              </span>
              {account.is_group && (
                <span className="ml-2 px-2 py-0.5 text-xs bg-gray-100 text-gray-700 rounded">
                  Group
                </span>
              )}
            </div>
          </div>
        </td>
        <td className="px-6 py-4">
          <div className="text-sm text-gray-900 font-medium">
            {account.account_name}
          </div>
        </td>
        <td className="px-6 py-4 whitespace-nowrap">
          <span
            className={`px-2 py-1 text-xs font-medium rounded-full ${
              accountTypeColors[account.account_type]
            }`}
          >
            {account.account_type.charAt(0).toUpperCase() + account.account_type.slice(1)}
          </span>
        </td>
        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
          {account.account_sub_type.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
        </td>
        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
          <span className={account.current_balance < 0 ? "text-red-600" : "text-gray-900"}>
            ₹{Math.abs(account.current_balance).toLocaleString("en-IN", {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })}
          </span>
        </td>
        <td className="px-6 py-4 whitespace-nowrap">
          <span
            className={`px-2 py-1 text-xs font-medium rounded-full ${
              account.is_active
                ? "bg-green-100 text-green-800"
                : "bg-gray-100 text-gray-800"
            }`}
          >
            {account.is_active ? "Active" : "Inactive"}
          </span>
        </td>
        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
          <button className="text-blue-600 hover:text-blue-900 mr-3">
            <Edit className="h-4 w-4" />
          </button>
          <button className="text-red-600 hover:text-red-900">
            <Trash2 className="h-4 w-4" />
          </button>
        </td>
      </tr>
      {isExpanded && hasChildren && account.children!.map((child) => (
        <AccountRow key={child.id} account={child} level={level + 1} />
      ))}
    </>
  );
}

export default function ChartOfAccountsPage() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterType, setFilterType] = useState<string>("all");
  const [showAddModal, setShowAddModal] = useState(false);

  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    try {
      setLoading(true);
      // TODO: Replace with actual API call
      const mockData: Account[] = [
        {
          id: 1,
          account_code: "1000",
          account_name: "Assets",
          account_type: "asset",
          account_sub_type: "current_asset",
          current_balance: 5000000.00,
          is_group: true,
          is_active: true,
          children: [
            {
              id: 2,
              account_code: "1001",
              account_name: "Cash and Bank",
              account_type: "asset",
              account_sub_type: "cash_bank",
              current_balance: 1500000.00,
              is_group: false,
              is_active: true,
            },
            {
              id: 3,
              account_code: "1100",
              account_name: "Loan Assets",
              account_type: "asset",
              account_sub_type: "loan_asset",
              current_balance: 3500000.00,
              is_group: false,
              is_active: true,
            },
          ],
        },
        {
          id: 4,
          account_code: "2000",
          account_name: "Liabilities",
          account_type: "liability",
          account_sub_type: "current_liability",
          current_balance: 2000000.00,
          is_group: true,
          is_active: true,
          children: [
            {
              id: 5,
              account_code: "2100",
              account_name: "Customer Deposits",
              account_type: "liability",
              account_sub_type: "deposit",
              current_balance: 2000000.00,
              is_group: false,
              is_active: true,
            },
          ],
        },
        {
          id: 6,
          account_code: "4000",
          account_name: "Income",
          account_type: "income",
          account_sub_type: "interest_income",
          current_balance: 500000.00,
          is_group: true,
          is_active: true,
          children: [
            {
              id: 7,
              account_code: "4001",
              account_name: "Interest Income on Loans",
              account_type: "income",
              account_sub_type: "interest_income",
              current_balance: 400000.00,
              is_group: false,
              is_active: true,
            },
            {
              id: 8,
              account_code: "4010",
              account_name: "Fee and Commission Income",
              account_type: "income",
              account_sub_type: "fee_income",
              current_balance: 100000.00,
              is_group: false,
              is_active: true,
            },
          ],
        },
      ];
      setAccounts(mockData);
    } catch (error) {
      console.error("Error fetching accounts:", error);
    } finally {
      setLoading(false);
    }
  };

  const filteredAccounts = accounts.filter((account) => {
    const matchesSearch = account.account_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      account.account_code.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterType === "all" || account.account_type === filterType;
    return matchesSearch && matchesFilter;
  });

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold text-gray-900">Chart of Accounts</h2>
            <p className="mt-1 text-sm text-gray-500">
              Manage your account hierarchy and balances
            </p>
          </div>
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Plus className="h-5 w-5 mr-2" />
            Add Account
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search accounts..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="pl-10 w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none"
            >
              <option value="all">All Types</option>
              <option value="asset">Assets</option>
              <option value="liability">Liabilities</option>
              <option value="equity">Equity</option>
              <option value="income">Income</option>
              <option value="expense">Expenses</option>
            </select>
          </div>
        </div>
      </div>

      {/* Accounts Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-gray-500">Loading accounts...</div>
          </div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Code
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Account Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Sub Type
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Balance
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white">
              {filteredAccounts.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-gray-500">
                    No accounts found
                  </td>
                </tr>
              ) : (
                filteredAccounts.map((account) => (
                  <AccountRow key={account.id} account={account} />
                ))
              )}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
