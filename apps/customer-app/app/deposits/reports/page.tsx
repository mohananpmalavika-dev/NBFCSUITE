'use client';

import { useEffect, useState } from 'react';
import { 
  Download, Calendar, TrendingUp, BarChart3, 
  FileText, Filter, RefreshCw, Search, PieChart,
  DollarSign, Users, Clock, ChevronDown, Building
} from 'lucide-react';
import { LineChart, Line, BarChart, Bar, PieChart as RechartsPie, Pie, Cell, 
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// Types
interface ReportFilters {
  report_type: string;
  start_date: string;
  end_date: string;
  branch?: string;
  product_type?: string;
  format: 'PDF' | 'EXCEL' | 'CSV';
}

interface DailyReport {
  date: string;
  openings: number;
  closures: number;
  renewals: number;
  amount_opened: number;
  amount_closed: number;
  net_change: number;
}

interface BranchReport {
  branch_code: string;
  branch_name: string;
  total_accounts: number;
  total_balance: number;
  fd_count: number;
  rd_count: number;
  avg_ticket_size: number;
}

interface ProductReport {
  product_name: string;
  product_type: string;
  account_count: number;
  total_amount: number;
  avg_rate: number;
  market_share: number;
}

interface MaturityReport {
  maturity_month: string;
  maturing_count: number;
  maturing_amount: number;
  renewal_count: number;
  renewal_amount: number;
  payout_amount: number;
}

const REPORT_TYPES = [
  { id: 'daily', name: 'Daily Activity Report', icon: Calendar },
  { id: 'branch', name: 'Branch-wise Summary', icon: Building },
  { id: 'product', name: 'Product Performance', icon: PieChart },
  { id: 'maturity', name: 'Maturity Pipeline', icon: Clock },
  { id: 'customer', name: 'Customer Analysis', icon: Users },
  { id: 'interest', name: 'Interest Liability', icon: DollarSign },
  { id: 'compliance', name: 'Regulatory Compliance', icon: FileText },
  { id: 'trends', name: 'Growth Trends', icon: TrendingUp }
];

export default function ReportsPage() {
  const [filters, setFilters] = useState<ReportFilters>({
    report_type: 'daily',
    start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end_date: new Date().toISOString().split('T')[0],
    format: 'PDF'
  });
  
  const [dailyData, setDailyData] = useState<DailyReport[]>([]);
  const [branchData, setBranchData] = useState<BranchReport[]>([]);
  const [productData, setProductData] = useState<ProductReport[]>([]);
  const [maturityData, setMaturityData] = useState<MaturityReport[]>([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [selectedReport, setSelectedReport] = useState('daily');

  useEffect(() => {
    fetchReportData();
  }, [selectedReport, filters.start_date, filters.end_date]);

  const fetchReportData = async () => {
    try {
      setLoading(true);
      
      // Fetch report data based on selected type
      const response = await fetch(
        `http://localhost:8007/api/v1/reports/${selectedReport}?start_date=${filters.start_date}&end_date=${filters.end_date}`
      );
      
      if (response.ok) {
        const data = await response.json();
        
        switch (selectedReport) {
          case 'daily':
            setDailyData(data);
            break;
          case 'branch':
            setBranchData(data);
            break;
          case 'product':
            setProductData(data);
            break;
          case 'maturity':
            setMaturityData(data);
            break;
        }
      }
    } catch (error) {
      console.error('Error fetching report data:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateReport = async () => {
    try {
      setGenerating(true);
      
      const response = await fetch('http://localhost:8007/api/v1/reports/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          report_type: selectedReport,
          start_date: filters.start_date,
          end_date: filters.end_date,
          branch: filters.branch,
          product_type: filters.product_type,
          format: filters.format
        })
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${selectedReport}_report_${filters.start_date}_${filters.end_date}.${filters.format.toLowerCase()}`;
        a.click();
        alert('Report generated successfully!');
      } else {
        alert('Failed to generate report');
      }
    } catch (error) {
      console.error('Error generating report:', error);
      alert('Error generating report');
    } finally {
      setGenerating(false);
    }
  };

  const COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#ec4899'];

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50/30 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600">Loading report data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50/30 p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">Reports & Analytics</h1>
            <p className="text-slate-600 mt-1">Comprehensive deposit reports and insights</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={fetchReportData}
              className="px-4 py-2 bg-white border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors flex items-center gap-2"
            >
              <RefreshCw className="h-4 w-4" />
              Refresh
            </button>
            <button
              onClick={generateReport}
              disabled={generating}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 disabled:opacity-50"
            >
              {generating ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                  Generating...
                </>
              ) : (
                <>
                  <Download className="h-4 w-4" />
                  Export Report
                </>
              )}
            </button>
          </div>
        </div>

        {/* Report Type Selector */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">Select Report Type</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {REPORT_TYPES.map((report) => (
              <button
                key={report.id}
                onClick={() => setSelectedReport(report.id)}
                className={`p-4 rounded-lg border-2 transition-all ${
                  selectedReport === report.id
                    ? 'border-blue-600 bg-blue-50'
                    : 'border-slate-200 bg-white hover:border-slate-300'
                }`}
              >
                <report.icon className={`h-6 w-6 mb-2 ${
                  selectedReport === report.id ? 'text-blue-600' : 'text-slate-400'
                }`} />
                <p className={`text-sm font-medium ${
                  selectedReport === report.id ? 'text-blue-900' : 'text-slate-700'
                }`}>
                  {report.name}
                </p>
              </button>
            ))}
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
          <div className="flex items-center gap-2 mb-4">
            <Filter className="h-5 w-5 text-slate-600" />
            <h3 className="text-lg font-semibold text-slate-900">Filters</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Start Date</label>
              <input
                type="date"
                value={filters.start_date}
                onChange={(e) => setFilters({ ...filters, start_date: e.target.value })}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">End Date</label>
              <input
                type="date"
                value={filters.end_date}
                onChange={(e) => setFilters({ ...filters, end_date: e.target.value })}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Branch</label>
              <select
                value={filters.branch || ''}
                onChange={(e) => setFilters({ ...filters, branch: e.target.value })}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Branches</option>
                <option value="HO">Head Office</option>
                <option value="BR001">Branch 001</option>
                <option value="BR002">Branch 002</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Export Format</label>
              <select
                value={filters.format}
                onChange={(e) => setFilters({ ...filters, format: e.target.value as any })}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="PDF">PDF</option>
                <option value="EXCEL">Excel</option>
                <option value="CSV">CSV</option>
              </select>
            </div>
          </div>
        </div>

        {/* Daily Report */}
        {selectedReport === 'daily' && (
          <div className="space-y-6">
            <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
              <h3 className="text-lg font-semibold text-slate-900 mb-4">Daily Activity Trend</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={dailyData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="openings" stroke="#10b981" name="Openings" />
                  <Line type="monotone" dataKey="closures" stroke="#ef4444" name="Closures" />
                  <Line type="monotone" dataKey="renewals" stroke="#3b82f6" name="Renewals" />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
              <div className="p-6 border-b border-slate-200">
                <h3 className="text-lg font-semibold text-slate-900">Daily Summary</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-slate-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-slate-600 uppercase">Date</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-slate-600 uppercase">Openings</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-slate-600 uppercase">Amount Opened</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-slate-600 uppercase">Closures</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-slate-600 uppercase">Amount Closed</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-slate-600 uppercase">Net Change</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200">
                    {dailyData.map((day, index) => (
                      <tr key={index} className="hover:bg-slate-50">
                        <td className="px-4 py-3 text-sm text-slate-900">
                          {new Date(day.date).toLocaleDateString('en-IN')}
                        </td>
                        <td className="px-4 py-3 text-sm text-right text-green-600 font-medium">
                          {day.openings}
                        </td>
                        <td className="px-4 py-3 text-sm text-right text-slate-900">
                          ₹{day.amount_opened.toLocaleString('en-IN')}
                        </td>
                        <td className="px-4 py-3 text-sm text-right text-red-600 font-medium">
                          {day.closures}
                        </td>
                        <td className="px-4 py-3 text-sm text-right text-slate-900">
                          ₹{day.amount_closed.toLocaleString('en-IN')}
                        </td>
                        <td className={`px-4 py-3 text-sm text-right font-bold ${
                          day.net_change >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {day.net_change >= 0 ? '+' : ''}₹{day.net_change.toLocaleString('en-IN')}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Branch Report */}
        {selectedReport === 'branch' && (
          <div className="space-y-6">
            <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
              <h3 className="text-lg font-semibold text-slate-900 mb-4">Branch Performance</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={branchData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="branch_code" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="total_balance" fill="#3b82f6" name="Total Balance" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
              <div className="p-6 border-b border-slate-200">
                <h3 className="text-lg font-semibold text-slate-900">Branch-wise Summary</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-slate-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-slate-600 uppercase">Branch</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-slate-600 uppercase">Accounts</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-slate-600 uppercase">FD Count</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-slate-600 uppercase">RD Count</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-slate-600 uppercase">Total Balance</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-slate-600 uppercase">Avg Ticket</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200">
                    {branchData.map((branch, index) => (
                      <tr key={index} className="hover:bg-slate-50">
                        <td className="px-4 py-3">
                          <div>
                            <p className="text-sm font-medium text-slate-900">{branch.branch_code}</p>
                            <p className="text-xs text-slate-500">{branch.branch_name}</p>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-sm text-right text-slate-900 font-medium">
                          {branch.total_accounts}
                        </td>
                        <td className="px-4 py-3 text-sm text-right text-slate-600">
                          {branch.fd_count}
                        </td>
                        <td className="px-4 py-3 text-sm text-right text-slate-600">
                          {branch.rd_count}
                        </td>
                        <td className="px-4 py-3 text-sm text-right text-slate-900 font-medium">
                          ₹{branch.total_balance.toLocaleString('en-IN')}
                        </td>
                        <td className="px-4 py-3 text-sm text-right text-slate-600">
                          ₹{branch.avg_ticket_size.toLocaleString('en-IN')}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Product Report */}
        {selectedReport === 'product' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
                <h3 className="text-lg font-semibold text-slate-900 mb-4">Product Distribution</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <RechartsPie>
                    <Pie
                      data={productData}
                      dataKey="account_count"
                      nameKey="product_name"
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      label
                    >
                      {productData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </RechartsPie>
                </ResponsiveContainer>
              </div>

              <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
                <h3 className="text-lg font-semibold text-slate-900 mb-4">Market Share by Amount</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <RechartsPie>
                    <Pie
                      data={productData}
                      dataKey="total_amount"
                      nameKey="product_name"
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      label
                    >
                      {productData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </RechartsPie>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
              <div className="p-6 border-b border-slate-200">
                <h3 className="text-lg font-semibold text-slate-900">Product Performance</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-slate-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-slate-600 uppercase">Product</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-slate-600 uppercase">Accounts</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-slate-600 uppercase">Total Amount</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-slate-600 uppercase">Avg Rate</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-slate-600 uppercase">Market Share</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200">
                    {productData.map((product, index) => (
                      <tr key={index} className="hover:bg-slate-50">
                        <td className="px-4 py-3">
                          <div>
                            <p className="text-sm font-medium text-slate-900">{product.product_name}</p>
                            <span className="text-xs px-2 py-0.5 bg-blue-100 text-blue-800 rounded-full">
                              {product.product_type}
                            </span>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-sm text-right text-slate-900 font-medium">
                          {product.account_count}
                        </td>
                        <td className="px-4 py-3 text-sm text-right text-slate-900 font-medium">
                          ₹{(product.total_amount / 10000000).toFixed(2)}Cr
                        </td>
                        <td className="px-4 py-3 text-sm text-right text-green-600 font-medium">
                          {product.avg_rate}%
                        </td>
                        <td className="px-4 py-3 text-sm text-right text-slate-900">
                          {product.market_share.toFixed(1)}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Maturity Report */}
        {selectedReport === 'maturity' && (
          <div className="space-y-6">
            <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
              <h3 className="text-lg font-semibold text-slate-900 mb-4">Maturity Pipeline by Month</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={maturityData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="maturity_month" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="maturing_amount" fill="#3b82f6" name="Maturing Amount" />
                  <Bar dataKey="renewal_amount" fill="#10b981" name="Renewal Amount" />
                  <Bar dataKey="payout_amount" fill="#f59e0b" name="Payout Amount" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
              <div className="p-6 border-b border-slate-200">
                <h3 className="text-lg font-semibold text-slate-900">Monthly Maturity Summary</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-slate-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-slate-600 uppercase">Month</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-slate-600 uppercase">Maturing Count</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-slate-600 uppercase">Maturing Amount</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-slate-600 uppercase">Renewal Count</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-slate-600 uppercase">Renewal Amount</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-slate-600 uppercase">Payout Amount</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-slate-600 uppercase">Renewal Rate</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200">
                    {maturityData.map((month, index) => (
                      <tr key={index} className="hover:bg-slate-50">
                        <td className="px-4 py-3 text-sm font-medium text-slate-900">
                          {month.maturity_month}
                        </td>
                        <td className="px-4 py-3 text-sm text-right text-slate-900">
                          {month.maturing_count}
                        </td>
                        <td className="px-4 py-3 text-sm text-right text-slate-900 font-medium">
                          ₹{(month.maturing_amount / 10000000).toFixed(2)}Cr
                        </td>
                        <td className="px-4 py-3 text-sm text-right text-green-600 font-medium">
                          {month.renewal_count}
                        </td>
                        <td className="px-4 py-3 text-sm text-right text-green-600 font-medium">
                          ₹{(month.renewal_amount / 10000000).toFixed(2)}Cr
                        </td>
                        <td className="px-4 py-3 text-sm text-right text-orange-600 font-medium">
                          ₹{(month.payout_amount / 10000000).toFixed(2)}Cr
                        </td>
                        <td className="px-4 py-3 text-sm text-right">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            (month.renewal_count / month.maturing_count * 100) >= 70
                              ? 'bg-green-100 text-green-800'
                              : 'bg-orange-100 text-orange-800'
                          }`}>
                            {((month.renewal_count / month.maturing_count) * 100).toFixed(1)}%
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Placeholder for other reports */}
        {!['daily', 'branch', 'product', 'maturity'].includes(selectedReport) && (
          <div className="bg-white rounded-xl p-12 shadow-sm border border-slate-200 text-center">
            <FileText className="h-16 w-16 text-slate-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-slate-900 mb-2">Report Coming Soon</h3>
            <p className="text-slate-600">
              {REPORT_TYPES.find(r => r.id === selectedReport)?.name} will be available shortly.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
