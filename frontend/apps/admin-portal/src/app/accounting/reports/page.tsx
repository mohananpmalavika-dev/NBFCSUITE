"use client";

import { useState } from "react";
import { 
  BarChart3, 
  TrendingUp,
  PieChart,
  Download,
  Calendar,
  FileText
} from "lucide-react";

type ReportType = "trial-balance" | "profit-loss" | "balance-sheet";

interface ReportCard {
  id: ReportType;
  title: string;
  description: string;
  icon: any;
  color: string;
}

const reports: ReportCard[] = [
  {
    id: "trial-balance",
    title: "Trial Balance",
    description: "Verify that total debits equal total credits across all accounts",
    icon: BarChart3,
    color: "bg-blue-600",
  },
  {
    id: "profit-loss",
    title: "Profit & Loss Statement",
    description: "Income statement showing revenues, expenses, and net profit",
    icon: TrendingUp,
    color: "bg-green-600",
  },
  {
    id: "balance-sheet",
    title: "Balance Sheet",
    description: "Statement of financial position - Assets, Liabilities, and Equity",
    icon: PieChart,
    color: "bg-purple-600",
  },
];

export default function FinancialReportsPage() {
  const [selectedReport, setSelectedReport] = useState<ReportType | null>(null);
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");
  const [asOfDate, setAsOfDate] = useState("");
  const [reportData, setReportData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const generateReport = async () => {
    setLoading(true);
    try {
      // TODO: Replace with actual API calls
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      if (selectedReport === "trial-balance") {
        setReportData({
          balance_date: asOfDate,
          entries: [
            { account_code: "1001", account_name: "Cash and Bank", account_type: "asset", debit_balance: 1500000, credit_balance: 0 },
            { account_code: "1100", account_name: "Loan Assets", account_type: "asset", debit_balance: 3500000, credit_balance: 0 },
            { account_code: "2100", account_name: "Customer Deposits", account_type: "liability", debit_balance: 0, credit_balance: 2000000 },
            { account_code: "4001", account_name: "Interest Income", account_type: "income", debit_balance: 0, credit_balance: 500000 },
            { account_code: "5200", account_name: "Operating Expenses", account_type: "expense", debit_balance: 200000, credit_balance: 0 },
          ],
          summary: {
            total_debit_balance: 5200000,
            total_credit_balance: 2500000,
          },
        });
      } else if (selectedReport === "profit-loss") {
        setReportData({
          from_date: fromDate,
          to_date: toDate,
          income: [
            { account_code: "4001", account_name: "Interest Income on Loans", amount: 400000 },
            { account_code: "4010", account_name: "Fee and Commission Income", amount: 100000 },
          ],
          expenses: [
            { account_code: "5100", account_name: "Interest Expense", amount: 150000 },
            { account_code: "5200", account_name: "Operating Expenses", amount: 200000 },
            { account_code: "5300", account_name: "Administrative Expenses", amount: 100000 },
          ],
          total_income: 500000,
          total_expenses: 450000,
          net_profit: 50000,
          profit_margin: 10,
        });
      } else if (selectedReport === "balance-sheet") {
        setReportData({
          as_of_date: asOfDate,
          assets: [
            { account_code: "1001", account_name: "Cash and Bank", amount: 1500000 },
            { account_code: "1100", account_name: "Loan Assets", amount: 3500000 },
          ],
          liabilities: [
            { account_code: "2100", account_name: "Customer Deposits", amount: 2000000 },
            { account_code: "2200", account_name: "Borrowings", amount: 1000000 },
          ],
          equity: [
            { account_code: "3100", account_name: "Share Capital", amount: 1500000 },
            { account_code: "3200", account_name: "Retained Earnings", amount: 500000 },
          ],
          total_assets: 5000000,
          total_liabilities: 3000000,
          total_equity: 2000000,
          is_balanced: true,
        });
      }
    } catch (error) {
      console.error("Error generating report:", error);
    } finally {
      setLoading(false);
    }
  };

  const exportReport = () => {
    // TODO: Implement export functionality
    alert("Export functionality to be implemented");
  };

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900">Financial Reports</h2>
        <p className="mt-1 text-sm text-gray-500">
          Generate and export financial statements and reports
        </p>
      </div>

      {/* Report Selection */}
      {!selectedReport && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {reports.map((report) => {
            const Icon = report.icon;
            return (
              <button
                key={report.id}
                onClick={() => setSelectedReport(report.id)}
                className="bg-white rounded-lg shadow-sm border-2 border-gray-200 p-6 hover:border-blue-500 hover:shadow-md transition-all text-left"
              >
                <div className={`inline-flex p-3 rounded-lg ${report.color} mb-4`}>
                  <Icon className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {report.title}
                </h3>
                <p className="text-sm text-gray-600">
                  {report.description}
                </p>
              </button>
            );
          })}
        </div>
      )}

      {/* Report Generation Form */}
      {selectedReport && !reportData && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-semibold text-gray-900">
              {reports.find(r => r.id === selectedReport)?.title}
            </h3>
            <button
              onClick={() => setSelectedReport(null)}
              className="text-sm text-gray-600 hover:text-gray-900"
            >
              ← Back to reports
            </button>
          </div>

          <div className="space-y-4">
            {selectedReport === "trial-balance" && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  As of Date
                </label>
                <div className="relative">
                  <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="date"
                    value={asOfDate}
                    onChange={(e) => setAsOfDate(e.target.value)}
                    className="pl-10 w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
            )}

            {selectedReport === "profit-loss" && (
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    From Date
                  </label>
                  <input
                    type="date"
                    value={fromDate}
                    onChange={(e) => setFromDate(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    To Date
                  </label>
                  <input
                    type="date"
                    value={toDate}
                    onChange={(e) => setToDate(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
            )}

            {selectedReport === "balance-sheet" && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  As of Date
                </label>
                <input
                  type="date"
                  value={asOfDate}
                  onChange={(e) => setAsOfDate(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            )}

            <button
              onClick={generateReport}
              disabled={loading || 
                (selectedReport === "profit-loss" && (!fromDate || !toDate)) ||
                ((selectedReport === "trial-balance" || selectedReport === "balance-sheet") && !asOfDate)
              }
              className="w-full flex items-center justify-center px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {loading ? (
                "Generating Report..."
              ) : (
                <>
                  <FileText className="h-5 w-5 mr-2" />
                  Generate Report
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Report Display */}
      {reportData && selectedReport === "trial-balance" && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
            <div>
              <h3 className="text-xl font-semibold text-gray-900">Trial Balance</h3>
              <p className="text-sm text-gray-500">As of {reportData.balance_date}</p>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={exportReport}
                className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                <Download className="h-4 w-4 mr-2" />
                Export
              </button>
              <button
                onClick={() => {
                  setReportData(null);
                  setSelectedReport(null);
                }}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Close
              </button>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Code</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Account Name</th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Type</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Debit</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Credit</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {reportData.entries.map((entry: any, index: number) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {entry.account_code}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {entry.account_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        entry.account_type === 'asset' ? 'bg-blue-100 text-blue-800' :
                        entry.account_type === 'liability' ? 'bg-red-100 text-red-800' :
                        entry.account_type === 'income' ? 'bg-green-100 text-green-800' :
                        'bg-orange-100 text-orange-800'
                      }`}>
                        {entry.account_type}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium text-gray-900">
                      {entry.debit_balance > 0 ? `₹${entry.debit_balance.toLocaleString("en-IN")}` : "-"}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium text-gray-900">
                      {entry.credit_balance > 0 ? `₹${entry.credit_balance.toLocaleString("en-IN")}` : "-"}
                    </td>
                  </tr>
                ))}
                <tr className="bg-gray-100 font-bold">
                  <td colSpan={3} className="px-6 py-4 text-right text-sm text-gray-900">
                    TOTAL
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                    ₹{reportData.summary.total_debit_balance.toLocaleString("en-IN")}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                    ₹{reportData.summary.total_credit_balance.toLocaleString("en-IN")}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Profit & Loss Report Display - Similar structure */}
      {/* Balance Sheet Report Display - Similar structure */}
    </div>
  );
}
