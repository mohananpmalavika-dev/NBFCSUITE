'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { 
  Calendar, Search, DollarSign, AlertTriangle, 
  CheckCircle, Clock, User, CreditCard, Filter,
  Download, RefreshCw, TrendingUp, XCircle
} from 'lucide-react';

// Types
interface RDInstallment {
  id: string;
  account_id: string;
  account_number: string;
  customer_name?: string;
  cif_number?: string;
  installment_number: number;
  due_date: string;
  installment_amount: number;
  paid_amount: number;
  penalty_amount: number;
  total_due: number;
  status: string;
  payment_date?: string;
  days_overdue: number;
  branch_code?: string;
}

interface CollectionStats {
  total_due_today: number;
  total_overdue: number;
  collection_target: number;
  collected_today: number;
  overdue_count: number;
  collection_rate: number;
}

export default function RDCollectionsPage() {
  const router = useRouter();
  const [installments, setInstallments] = useState<RDInstallment[]>([]);
  const [filteredInstallments, setFilteredInstallments] = useState<RDInstallment[]>([]);
  const [stats, setStats] = useState<CollectionStats>({
    total_due_today: 0,
    total_overdue: 0,
    collection_target: 0,
    collected_today: 0,
    overdue_count: 0,
    collection_rate: 0
  });
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<'ALL' | 'DUE_TODAY' | 'OVERDUE' | 'PAID'>('ALL');
  const [processingId, setProcessingId] = useState<string | null>(null);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [selectedInstallment, setSelectedInstallment] = useState<RDInstallment | null>(null);
  const [paymentAmount, setPaymentAmount] = useState('');
  const [paymentMode, setPaymentMode] = useState('CASH');

  useEffect(() => {
    fetchCollections();
  }, []);

  useEffect(() => {
    filterInstallments();
  }, [installments, searchTerm, filterStatus]);

  const fetchCollections = async () => {
    try {
      setLoading(true);
      
      // Fetch RD installments
      const response = await fetch('http://localhost:8007/api/v1/rd/installments/pending');
      if (response.ok) {
        const data = await response.json();
        setInstallments(data);
        
        // Calculate stats
        const today = new Date().toDateString();
        const dueToday = data.filter((inst: RDInstallment) => 
          new Date(inst.due_date).toDateString() === today && inst.status !== 'PAID'
        );
        const overdue = data.filter((inst: RDInstallment) => inst.status === 'OVERDUE');
        const paidToday = data.filter((inst: RDInstallment) => 
          inst.payment_date && new Date(inst.payment_date).toDateString() === today
        );
        
        const totalDueToday = dueToday.reduce((sum: number, inst: RDInstallment) => sum + inst.total_due, 0);
        const totalOverdue = overdue.reduce((sum: number, inst: RDInstallment) => sum + inst.total_due, 0);
        const collectedToday = paidToday.reduce((sum: number, inst: RDInstallment) => sum + inst.paid_amount, 0);
        const target = totalDueToday + totalOverdue;
        
        setStats({
          total_due_today: totalDueToday,
          total_overdue: totalOverdue,
          collection_target: target,
          collected_today: collectedToday,
          overdue_count: overdue.length,
          collection_rate: target > 0 ? (collectedToday / target) * 100 : 0
        });
      }
    } catch (error) {
      console.error('Error fetching collections:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterInstallments = () => {
    let filtered = installments;

    // Filter by status
    if (filterStatus !== 'ALL') {
      if (filterStatus === 'DUE_TODAY') {
        const today = new Date().toDateString();
        filtered = filtered.filter(inst => 
          new Date(inst.due_date).toDateString() === today && inst.status !== 'PAID'
        );
      } else if (filterStatus === 'OVERDUE') {
        filtered = filtered.filter(inst => inst.status === 'OVERDUE');
      } else if (filterStatus === 'PAID') {
        filtered = filtered.filter(inst => inst.status === 'PAID');
      }
    }

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(inst =>
        inst.account_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        inst.cif_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        inst.customer_name?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    setFilteredInstallments(filtered);
  };

  const handleRecordPayment = (installment: RDInstallment) => {
    setSelectedInstallment(installment);
    setPaymentAmount(installment.total_due.toString());
    setShowPaymentModal(true);
  };

  const submitPayment = async () => {
    if (!selectedInstallment) return;

    try {
      setProcessingId(selectedInstallment.id);
      const response = await fetch(`http://localhost:8007/api/v1/rd/installments/${selectedInstallment.id}/pay`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          amount: parseFloat(paymentAmount),
          payment_mode: paymentMode,
          payment_date: new Date().toISOString(),
          collected_by: 'ADMIN' // Replace with actual user
        })
      });

      if (response.ok) {
        alert('Payment recorded successfully!');
        setShowPaymentModal(false);
        setSelectedInstallment(null);
        fetchCollections(); // Refresh
      } else {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error recording payment:', error);
      alert('Failed to record payment');
    } finally {
      setProcessingId(null);
    }
  };

  const downloadReceipt = async (installmentId: string) => {
    try {
      const response = await fetch(`http://localhost:8007/api/v1/rd/installments/${installmentId}/receipt`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `RD_Receipt_${installmentId}.pdf`;
        a.click();
      }
    } catch (error) {
      console.error('Error downloading receipt:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50/30 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600">Loading collections...</p>
        </div>
      </div>
    );
  }

  const statusColors: Record<string, string> = {
    'PENDING': 'bg-yellow-100 text-yellow-800',
    'PAID': 'bg-green-100 text-green-800',
    'OVERDUE': 'bg-red-100 text-red-800',
    'PARTIAL': 'bg-orange-100 text-orange-800'
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50/30 p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">RD Collections</h1>
            <p className="text-slate-600 mt-1">Manage recurring deposit installments</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={fetchCollections}
              className="px-4 py-2 bg-white border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors flex items-center gap-2"
            >
              <RefreshCw className="h-4 w-4" />
              Refresh
            </button>
            <button
              onClick={() => router.push('/deposits/rd/reports')}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <Download className="h-4 w-4" />
              Export
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-6 text-white shadow-lg">
            <div className="flex items-center gap-3 mb-2">
              <Calendar className="h-6 w-6" />
              <span className="text-sm opacity-90">Due Today</span>
            </div>
            <p className="text-3xl font-bold">₹{(stats.total_due_today / 100000).toFixed(2)}L</p>
            <p className="text-sm opacity-75 mt-1">Today's collection target</p>
          </div>

          <div className="bg-gradient-to-br from-red-500 to-red-600 rounded-xl p-6 text-white shadow-lg">
            <div className="flex items-center gap-3 mb-2">
              <AlertTriangle className="h-6 w-6" />
              <span className="text-sm opacity-90">Overdue</span>
            </div>
            <p className="text-3xl font-bold">₹{(stats.total_overdue / 100000).toFixed(2)}L</p>
            <p className="text-sm opacity-75 mt-1">{stats.overdue_count} overdue installments</p>
          </div>

          <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl p-6 text-white shadow-lg">
            <div className="flex items-center gap-3 mb-2">
              <CheckCircle className="h-6 w-6" />
              <span className="text-sm opacity-90">Collected Today</span>
            </div>
            <p className="text-3xl font-bold">₹{(stats.collected_today / 100000).toFixed(2)}L</p>
            <p className="text-sm opacity-75 mt-1">Today's collections</p>
          </div>

          <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-6 text-white shadow-lg">
            <div className="flex items-center gap-3 mb-2">
              <TrendingUp className="h-6 w-6" />
              <span className="text-sm opacity-90">Collection Rate</span>
            </div>
            <p className="text-3xl font-bold">{stats.collection_rate.toFixed(1)}%</p>
            <p className="text-sm opacity-75 mt-1">Achievement rate</p>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
          <div className="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-slate-400" />
              <input
                type="text"
                placeholder="Search by account, CIF, or customer..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div className="flex gap-2">
              {[
                { id: 'ALL', label: 'All', icon: Filter },
                { id: 'DUE_TODAY', label: 'Due Today', icon: Calendar },
                { id: 'OVERDUE', label: 'Overdue', icon: AlertTriangle },
                { id: 'PAID', label: 'Paid', icon: CheckCircle }
              ].map((filter) => (
                <button
                  key={filter.id}
                  onClick={() => setFilterStatus(filter.id as any)}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 ${
                    filterStatus === filter.id
                      ? 'bg-blue-600 text-white'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  <filter.icon className="h-4 w-4" />
                  {filter.label}
                </button>
              ))}
            </div>
          </div>
        </div>
