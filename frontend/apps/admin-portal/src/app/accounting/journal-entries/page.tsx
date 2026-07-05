"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { 
  Plus, 
  Search, 
  Filter,
  CheckCircle,
  XCircle,
  Clock,
  FileText,
  Eye
} from "lucide-react";

interface JournalEntry {
  id: number;
  entry_number: string;
  entry_date: string;
  posting_date?: string;
  entry_type: string;
  status: string;
  narration: string;
  total_debit: number;
  total_credit: number;
  created_at: string;
}

const statusColors: Record<string, string> = {
  draft: "bg-yellow-100 text-yellow-800",
  posted: "bg-green-100 text-green-800",
  reversed: "bg-gray-100 text-gray-800",
  void: "bg-red-100 text-red-800",
};

const statusIcons: Record<string, any> = {
  draft: Clock,
  posted: CheckCircle,
  reversed: XCircle,
  void: XCircle,
};

const entryTypeLabels: Record<string, string> = {
  manual: "Manual",
  system: "System",
  loan_disbursement: "Loan Disbursement",
  loan_repayment: "Loan Repayment",
  interest_accrual: "Interest Accrual",
  adjustment: "Adjustment",
  reversal: "Reversal",
};

export default function JournalEntriesPage() {
  const [entries, setEntries] = useState<JournalEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [filterType, setFilterType] = useState<string>("all");

  useEffect(() => {
    fetchJournalEntries();
  }, []);

  const fetchJournalEntries = async () => {
    try {
      setLoading(true);
      // TODO: Replace with actual API call
      const mockData: JournalEntry[] = [
        {
          id: 1,
          entry_number: "JE-202601-0125",
          entry_date: "2026-01-05",
          posting_date: "2026-01-05",
          entry_type: "loan_disbursement",
          status: "posted",
          narration: "Loan disbursement - Account #LA-202601-0023",
          total_debit: 100000.00,
          total_credit: 100000.00,
          created_at: "2026-01-05T10:30:00Z",
        },
        {
          id: 2,
          entry_number: "JE-202601-0124",
          entry_date: "2026-01-05",
          posting_date: "2026-01-05",
          entry_type: "loan_repayment",
          status: "posted",
          narration: "Loan repayment received - EMI payment",
          total_debit: 15000.00,
          total_credit: 15000.00,
          created_at: "2026-01-05T09:15:00Z",
        },
        {
          id: 3,
          entry_number: "JE-202601-0123",
          entry_date: "2026-01-04",
          entry_type: "manual",
          status: "draft",
          narration: "Office rent payment for January 2026",
          total_debit: 50000.00,
          total_credit: 50000.00,
          created_at: "2026-01-04T16:45:00Z",
        },
        {
          id: 4,
          entry_number: "JE-202601-0122",
          entry_date: "2026-01-04",
          posting_date: "2026-01-04",
          entry_type: "interest_accrual",
          status: "posted",
          narration: "Monthly interest accrual on active loans",
          total_debit: 250000.00,
          total_credit: 250000.00,
          created_at: "2026-01-04T18:00:00Z",
        },
        {
          id: 5,
          entry_number: "JE-202601-0121",
          entry_date: "2026-01-03",
          posting_date: "2026-01-03",
          entry_type: "manual",
          status: "posted",
          narration: "Utility bills payment",
          total_debit: 25000.00,
          total_credit: 25000.00,
          created_at: "2026-01-03T14:20:00Z",
        },
      ];
      setEntries(mockData);
    } catch (error) {
      console.error("Error fetching journal entries:", error);
    } finally {
      setLoading(false);
    }
  };

  const filteredEntries = entries.filter((entry) => {
    const matchesSearch = 
      entry.entry_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      entry.narration.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === "all" || entry.status === filterStatus;
    const matchesType = filterType === "all" || entry.entry_type === filterType;
    return matchesSearch && matchesStatus && matchesType;
  });

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold text-gray-900">Journal Entries</h2>
            <p className="mt-1 text-sm text-gray-500">
              Create and manage journal entries for all transactions
            </p>
          </div>
          <Link
            href="/accounting/journal-entries/new"
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Plus className="h-5 w-5 mr-2" />
            New Entry
          </Link>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search entries..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="pl-10 w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none"
            >
              <option value="all">All Status</option>
              <option value="draft">Draft</option>
              <option value="posted">Posted</option>
              <option value="reversed">Reversed</option>
              <option value="void">Void</option>
            </select>
          </div>
          <div className="relative">
            <FileText className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="pl-10 w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none"
            >
              <option value="all">All Types</option>
              <option value="manual">Manual</option>
              <option value="system">System</option>
              <option value="loan_disbursement">Loan Disbursement</option>
              <option value="loan_repayment">Loan Repayment</option>
              <option value="interest_accrual">Interest Accrual</option>
            </select>
          </div>
          <div className="flex items-center justify-end">
            <span className="text-sm text-gray-600">
              {filteredEntries.length} entries found
            </span>
          </div>
        </div>
      </div>

      {/* Entries Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-gray-500">Loading journal entries...</div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Entry Number
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Narration
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Amount
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredEntries.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-6 py-12 text-center text-gray-500">
                      No journal entries found
                    </td>
                  </tr>
                ) : (
                  filteredEntries.map((entry) => {
                    const StatusIcon = statusIcons[entry.status];
                    return (
                      <tr key={entry.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-blue-600">
                            {entry.entry_number}
                          </div>
                          <div className="text-xs text-gray-500">
                            Created: {new Date(entry.created_at).toLocaleString("en-IN", {
                              month: "short",
                              day: "numeric",
                              hour: "2-digit",
                              minute: "2-digit",
                            })}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">
                            {new Date(entry.entry_date).toLocaleDateString("en-IN", {
                              year: "numeric",
                              month: "short",
                              day: "numeric",
                            })}
                          </div>
                          {entry.posting_date && (
                            <div className="text-xs text-gray-500">
                              Posted: {new Date(entry.posting_date).toLocaleDateString("en-IN", {
                                month: "short",
                                day: "numeric",
                              })}
                            </div>
                          )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="text-sm text-gray-900">
                            {entryTypeLabels[entry.entry_type] || entry.entry_type}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm text-gray-900 max-w-md truncate">
                            {entry.narration}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right">
                          <div className="text-sm font-semibold text-gray-900">
                            ₹{entry.total_debit.toLocaleString("en-IN")}
                          </div>
                          <div className="text-xs text-gray-500">
                            Dr = Cr
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-center">
                          <span
                            className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                              statusColors[entry.status]
                            }`}
                          >
                            <StatusIcon className="h-3 w-3 mr-1" />
                            {entry.status.charAt(0).toUpperCase() + entry.status.slice(1)}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                          <Link
                            href={`/accounting/journal-entries/${entry.id}`}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            <Eye className="h-4 w-4 inline" />
                          </Link>
                          {entry.status === "draft" && (
                            <button className="text-green-600 hover:text-green-900">
                              Post
                            </button>
                          )}
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Summary Stats */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Entries</p>
              <p className="mt-1 text-2xl font-bold text-gray-900">{entries.length}</p>
            </div>
            <FileText className="h-8 w-8 text-gray-400" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Posted</p>
              <p className="mt-1 text-2xl font-bold text-green-600">
                {entries.filter(e => e.status === "posted").length}
              </p>
            </div>
            <CheckCircle className="h-8 w-8 text-green-400" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Draft</p>
              <p className="mt-1 text-2xl font-bold text-yellow-600">
                {entries.filter(e => e.status === "draft").length}
              </p>
            </div>
            <Clock className="h-8 w-8 text-yellow-400" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">This Month</p>
              <p className="mt-1 text-2xl font-bold text-blue-600">
                ₹{entries
                  .filter(e => e.status === "posted")
                  .reduce((sum, e) => sum + e.total_debit, 0)
                  .toLocaleString("en-IN", { maximumFractionDigits: 0 })}
              </p>
            </div>
            <DollarSign className="h-8 w-8 text-blue-400" />
          </div>
        </div>
      </div>
    </div>
  );
}
