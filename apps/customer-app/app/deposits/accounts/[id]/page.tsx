'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { 
  ArrowLeft, Download, Calendar, User, DollarSign, 
  TrendingUp, Clock, CheckCircle, XCircle, AlertCircle,
  FileText, Users, CreditCard, RefreshCw, XOctagon
} from 'lucide-react';

// Types
interface DepositAccount {
  id: string;
  account_number: string;
  customer_id: string;
  customer_name?: string;
  cif_number?: string;
  product_id: string;
  product_name?: string;
  deposit_type: string;
  principal_amount: number;
  interest_rate: number;
  tenure_days: number;
  open_date: string;
  maturity_date: string;
  maturity_amount: number;
  status: string;
  branch_code?: string;
  interest_payout_frequency?: string;
  compounding_frequency?: string;
  is_senior_citizen: boolean;
  auto_renewal: boolean;
  created_at: string;
  updated_at: string;
}

interface Nominee {
  id: string;
  name: string;
  relationship: string;
  date_of_birth: string;
  contact_number?: string;
  allocation_percentage: number;
}

interface Transaction {
  id: string;
  transaction_type: string;
  amount: number;
  transaction_date: string;
  description: string;
  balance: number;
  reference_number?: string;
}

interface InterestPosting {
  id: string;
  posting_date: string;
  interest_amount: number;
  tds_amount: number;
  net_amount: number;
  period_from: string;
  period_to: string;
  status: string;
}

interface Certificate {
  id: string;
  certificate_type: string;
  issue_date: string;
  certificate_number: string;
  status: string;
}

export default function AccountDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const accountId = params.id as string;

  const [account, setAccount] = useState<DepositAccount | null>(null);
  const [nominees, setNominees] = useState<Nominee[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [interestPostings, setInterestPostings] = useState<InterestPosting[]>([]);
  const [certificates, setCertificates] = useState<Certificate[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'transactions' | 'interest' | 'nominees' | 'certificates'>('overview');

  useEffect(() => {
    fetchAccountDetails();
  }, [accountId]);

  const fetchAccountDetails = async () => {
    try {
      setLoading(true);
      
      // Fetch account details
      const accountResponse = await fetch(`http://localhost:8007/api/v1/accounts/${accountId}`);
      if (accountResponse.ok) {
        const accountData = await accountResponse.json();
        setAccount(accountData);
      }

      // Fetch nominees
      const nomineesResponse = await fetch(`http://localhost:8007/api/v1/accounts/${accountId}/nominees`);
      if (nomineesResponse.ok) {
        const nomineesData = await nomineesResponse.json();
        setNominees(nomineesData);
      }

      // Fetch transactions
      const transactionsResponse = await fetch(`http://localhost:8007/api/v1/accounts/${accountId}/transactions`);
      if (transactionsResponse.ok) {
        const transactionsData = await transactionsResponse.json();
        setTransactions(transactionsData);
      }

      // Fetch interest postings
      const interestResponse = await fetch(`http://localhost:8007/api/v1/accounts/${accountId}/interest-postings`);
      if (interestResponse.ok) {
        const interestData = await interestResponse.json();
        setInterestPostings(interestData);
      }

      // Fetch certificates
      const certificatesResponse = await fetch(`http://localhost:8007/api/v1/accounts/${accountId}/certificates`);
      if (certificatesResponse.ok) {
        const certificatesData = await certificatesResponse.json();
        setCertificates(certificatesData);
      }

    } catch (error) {
      console.error('Error fetching account details:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePrematureClosure = () => {
    router.push(`/deposits/accounts/${accountId}/premature-closure`);
  };

  const handleRenewal = () => {
    router.push(`/deposits/accounts/${accountId}/renewal`);
  };

  const handleDownloadCertificate = async () => {
    try {
      const response = await fetch(`http://localhost:8007/api/v1/accounts/${accountId}/certificate`, {
        method: 'POST'
      });
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `FD_Certificate_${account?.account_number}.pdf`;
        a.click();
      }
    } catch (error) {
      console.error('Error downloading certificate:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50/30 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600">Loading account details...</p>
        </div>
      </div>
    );
  }

  if (!account) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50/30 flex items-center justify-center">
        <div className="text-center">
          <XCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-slate-900 mb-2">Account Not Found</h2>
          <p className="text-slate-600 mb-4">The account you're looking for doesn't exist.</p>
          <Link href="/deposits/accounts" className="text-blue-600 hover:text-blue-700">
            Back to Accounts
          </Link>
        </div>
      </div>
    );
  }

  const statusColors: Record<string, string> = {
    'ACTIVE': 'bg-green-100 text-green-800',
    'PENDING_APPROVAL': 'bg-yellow-100 text-yellow-800',
    'MATURED': 'bg-blue-100 text-blue-800',
    'CLOSED': 'bg-gray-100 text-gray-800',
    'PREMATURE_CLOSED': 'bg-red-100 text-red-800'
  };

  const daysToMaturity = Math.ceil((new Date(account.maturity_date).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24));

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50/30 p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link 
              href="/deposits/accounts"
              className="p-2 hover:bg-white rounded-lg transition-colors"
            >
              <ArrowLeft className="h-5 w-5 text-slate-600" />
            </Link>
            <div>
              <h1 className="text-3xl font-bold text-slate-900">
                Account #{account.account_number}
              </h1>
              <p className="text-slate-600">
                {account.product_name} • {account.deposit_type}
              </p>
            </div>
          </div>
          <div className="flex gap-3">
            <button
              onClick={handleDownloadCertificate}
              className="px-4 py-2 bg-white border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors flex items-center gap-2"
            >
              <Download className="h-4 w-4" />
              Certificate
            </button>
            {account.status === 'ACTIVE' && (
              <>
                <button
                  onClick={handleRenewal}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
                >
                  <RefreshCw className="h-4 w-4" />
                  Renew
                </button>
                <button
                  onClick={handlePrematureClosure}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center gap-2"
                >
                  <XOctagon className="h-4 w-4" />
                  Close Early
                </button>
              </>
            )}
          </div>
        </div>

        {/* Status Badge */}
        <div className="flex items-center gap-4">
          <span className={`px-4 py-2 rounded-full text-sm font-medium ${statusColors[account.status] || 'bg-gray-100 text-gray-800'}`}>
            {account.status.replace('_', ' ')}
          </span>
          {daysToMaturity > 0 && daysToMaturity <= 30 && (
            <div className="flex items-center gap-2 text-orange-600">
              <AlertCircle className="h-5 w-5" />
              <span className="text-sm font-medium">Matures in {daysToMaturity} days</span>
            </div>
          )}
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
            <div className="flex items-center gap-3 mb-2">
              <DollarSign className="h-5 w-5 text-blue-600" />
              <span className="text-sm text-slate-600">Principal Amount</span>
            </div>
            <p className="text-2xl font-bold text-slate-900">
              ₹{account.principal_amount.toLocaleString('en-IN')}
            </p>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
            <div className="flex items-center gap-3 mb-2">
              <TrendingUp className="h-5 w-5 text-green-600" />
              <span className="text-sm text-slate-600">Interest Rate</span>
            </div>
            <p className="text-2xl font-bold text-slate-900">
              {account.interest_rate}% p.a.
            </p>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
            <div className="flex items-center gap-3 mb-2">
              <Calendar className="h-5 w-5 text-purple-600" />
              <span className="text-sm text-slate-600">Tenure</span>
            </div>
            <p className="text-2xl font-bold text-slate-900">
              {Math.floor(account.tenure_days / 365)} years {account.tenure_days % 365} days
            </p>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
            <div className="flex items-center gap-3 mb-2">
              <CreditCard className="h-5 w-5 text-orange-600" />
              <span className="text-sm text-slate-600">Maturity Amount</span>
            </div>
            <p className="text-2xl font-bold text-slate-900">
              ₹{account.maturity_amount.toLocaleString('en-IN')}
            </p>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200">
          <div className="border-b border-slate-200">
            <div className="flex gap-1 p-2">
              {[
                { id: 'overview', label: 'Overview', icon: FileText },
                { id: 'transactions', label: 'Transactions', icon: CreditCard },
                { id: 'interest', label: 'Interest', icon: TrendingUp },
                { id: 'nominees', label: 'Nominees', icon: Users },
                { id: 'certificates', label: 'Certificates', icon: Download }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                    activeTab === tab.id
                      ? 'bg-blue-50 text-blue-600'
                      : 'text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  <tab.icon className="h-4 w-4" />
                  {tab.label}
                </button>
              ))}
            </div>
          </div>

          <div className="p-6">
            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Account Details */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-slate-900">Account Details</h3>
                    <div className="space-y-3">
                      <InfoRow label="Account Number" value={account.account_number} />
                      <InfoRow label="CIF Number" value={account.cif_number || 'N/A'} />
                      <InfoRow label="Customer Name" value={account.customer_name || 'N/A'} />
                      <InfoRow label="Branch Code" value={account.branch_code || 'N/A'} />
                      <InfoRow label="Open Date" value={new Date(account.open_date).toLocaleDateString('en-IN')} />
                      <InfoRow label="Maturity Date" value={new Date(account.maturity_date).toLocaleDateString('en-IN')} />
                    </div>
                  </div>

                  {/* Product Details */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-slate-900">Product Details</h3>
                    <div className="space-y-3">
                      <InfoRow label="Product Name" value={account.product_name || 'N/A'} />
                      <InfoRow label="Deposit Type" value={account.deposit_type} />
                      <InfoRow label="Interest Payout" value={account.interest_payout_frequency || 'Cumulative'} />
                      <InfoRow label="Compounding" value={account.compounding_frequency || 'Quarterly'} />
                      <InfoRow label="Senior Citizen" value={account.is_senior_citizen ? 'Yes' : 'No'} />
                      <InfoRow label="Auto Renewal" value={account.auto_renewal ? 'Yes' : 'No'} />
                    </div>
                  </div>
                </div>

                {/* Interest Calculation Summary */}
                <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-200">
                  <h3 className="text-lg font-semibold text-slate-900 mb-4">Interest Summary</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <p className="text-sm text-slate-600 mb-1">Total Interest</p>
                      <p className="text-xl font-bold text-slate-900">
                        ₹{(account.maturity_amount - account.principal_amount).toLocaleString('en-IN')}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-slate-600 mb-1">Effective Rate</p>
                      <p className="text-xl font-bold text-slate-900">
                        {account.interest_rate}% p.a.
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-slate-600 mb-1">Return on Investment</p>
                      <p className="text-xl font-bold text-green-600">
                        {(((account.maturity_amount - account.principal_amount) / account.principal_amount) * 100).toFixed(2)}%
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Transactions Tab */}
            {activeTab === 'transactions' && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-slate-900">Transaction History</h3>
                {transactions.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-slate-50">
                        <tr>
                          <th className="px-4 py-3 text-left text-xs font-medium text-slate-600 uppercase">Date</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-slate-600 uppercase">Type</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-slate-600 uppercase">Description</th>
                          <th className="px-4 py-3 text-right text-xs font-medium text-slate-600 uppercase">Amount</th>
                          <th className="px-4 py-3 text-right text-xs font-medium text-slate-600 uppercase">Balance</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-slate-600 uppercase">Reference</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-200">
                        {transactions.map((txn) => (
                          <tr key={txn.id} className="hover:bg-slate-50">
                            <td className="px-4 py-3 text-sm text-slate-900">
                              {new Date(txn.transaction_date).toLocaleDateString('en-IN')}
                            </td>
                            <td className="px-4 py-3">
                              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                txn.transaction_type === 'CREDIT' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                              }`}>
                                {txn.transaction_type}
                              </span>
                            </td>
                            <td className="px-4 py-3 text-sm text-slate-600">{txn.description}</td>
                            <td className="px-4 py-3 text-sm font-medium text-right">
                              ₹{txn.amount.toLocaleString('en-IN')}
                            </td>
                            <td className="px-4 py-3 text-sm text-right text-slate-900">
                              ₹{txn.balance.toLocaleString('en-IN')}
                            </td>
                            <td className="px-4 py-3 text-sm text-slate-500">{txn.reference_number || '-'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="text-center py-12 text-slate-500">
                    <CreditCard className="h-12 w-12 mx-auto mb-3 opacity-50" />
                    <p>No transactions yet</p>
                  </div>
                )}
              </div>
            )}

            {/* Interest Tab */}
            {activeTab === 'interest' && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-slate-900">Interest Postings</h3>
                {interestPostings.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-slate-50">
                        <tr>
                          <th className="px-4 py-3 text-left text-xs font-medium text-slate-600 uppercase">Posting Date</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-slate-600 uppercase">Period</th>
                          <th className="px-4 py-3 text-right text-xs font-medium text-slate-600 uppercase">Interest</th>
                          <th className="px-4 py-3 text-right text-xs font-medium text-slate-600 uppercase">TDS</th>
                          <th className="px-4 py-3 text-right text-xs font-medium text-slate-600 uppercase">Net Amount</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-slate-600 uppercase">Status</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-200">
                        {interestPostings.map((posting) => (
                          <tr key={posting.id} className="hover:bg-slate-50">
                            <td className="px-4 py-3 text-sm text-slate-900">
                              {new Date(posting.posting_date).toLocaleDateString('en-IN')}
                            </td>
                            <td className="px-4 py-3 text-sm text-slate-600">
                              {new Date(posting.period_from).toLocaleDateString('en-IN')} - {new Date(posting.period_to).toLocaleDateString('en-IN')}
                            </td>
                            <td className="px-4 py-3 text-sm font-medium text-right text-green-600">
                              ₹{posting.interest_amount.toLocaleString('en-IN')}
                            </td>
                            <td className="px-4 py-3 text-sm text-right text-red-600">
                              ₹{posting.tds_amount.toLocaleString('en-IN')}
                            </td>
                            <td className="px-4 py-3 text-sm font-medium text-right">
                              ₹{posting.net_amount.toLocaleString('en-IN')}
                            </td>
                            <td className="px-4 py-3">
                              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                posting.status === 'POSTED' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                              }`}>
                                {posting.status}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="text-center py-12 text-slate-500">
                    <TrendingUp className="h-12 w-12 mx-auto mb-3 opacity-50" />
                    <p>No interest postings yet</p>
                  </div>
                )}
              </div>
            )}

            {/* Nominees Tab */}
            {activeTab === 'nominees' && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-slate-900">Nominee Details</h3>
                {nominees.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {nominees.map((nominee) => (
                      <div key={nominee.id} className="bg-slate-50 rounded-lg p-4 border border-slate-200">
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex items-center gap-3">
                            <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                              <User className="h-5 w-5 text-blue-600" />
                            </div>
                            <div>
                              <p className="font-semibold text-slate-900">{nominee.name}</p>
                              <p className="text-sm text-slate-600">{nominee.relationship}</p>
                            </div>
                          </div>
                          <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                            {nominee.allocation_percentage}%
                          </span>
                        </div>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-slate-600">Date of Birth:</span>
                            <span className="text-slate-900">{new Date(nominee.date_of_birth).toLocaleDateString('en-IN')}</span>
                          </div>
                          {nominee.contact_number && (
                            <div className="flex justify-between">
                              <span className="text-slate-600">Contact:</span>
                              <span className="text-slate-900">{nominee.contact_number}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12 text-slate-500">
                    <Users className="h-12 w-12 mx-auto mb-3 opacity-50" />
                    <p>No nominees added</p>
                  </div>
                )}
              </div>
            )}

            {/* Certificates Tab */}
            {activeTab === 'certificates' && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-slate-900">Certificates & Documents</h3>
                  <button
                    onClick={handleDownloadCertificate}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
                  >
                    <Download className="h-4 w-4" />
                    Generate Certificate
                  </button>
                </div>
                {certificates.length > 0 ? (
                  <div className="grid grid-cols-1 gap-3">
                    {certificates.map((cert) => (
                      <div key={cert.id} className="flex items-center justify-between p-4 bg-slate-50 rounded-lg border border-slate-200 hover:bg-slate-100 transition-colors">
                        <div className="flex items-center gap-3">
                          <FileText className="h-5 w-5 text-blue-600" />
                          <div>
                            <p className="font-medium text-slate-900">{cert.certificate_type}</p>
                            <p className="text-sm text-slate-600">
                              Certificate #{cert.certificate_number} • {new Date(cert.issue_date).toLocaleDateString('en-IN')}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                            cert.status === 'ACTIVE' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                          }`}>
                            {cert.status}
                          </span>
                          <button className="p-2 hover:bg-white rounded-lg transition-colors">
                            <Download className="h-4 w-4 text-slate-600" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12 text-slate-500">
                    <FileText className="h-12 w-12 mx-auto mb-3 opacity-50" />
                    <p>No certificates generated yet</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// Helper Component
function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between py-2 border-b border-slate-100">
      <span className="text-sm text-slate-600">{label}</span>
      <span className="text-sm font-medium text-slate-900">{value}</span>
    </div>
  );
}
