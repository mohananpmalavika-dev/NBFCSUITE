/**
 * Deposit Products - Catalog & Comparison
 * Browse all deposit products with AI recommendations
 */

'use client';

import { useState, useEffect } from 'react';
import { 
  PiggyBank, 
  Clock, 
  TrendingUp, 
  Calendar,
  Users,
  CheckCircle,
  XCircle,
  ArrowRight,
  Filter,
  Search,
  Sparkles
} from 'lucide-react';
import Link from 'next/link';

interface DepositProduct {
  id: string;
  code: string;
  name: string;
  deposit_type: string;
  min_amount: number;
  max_amount: number | null;
  min_tenure_days: number;
  max_tenure_days: number;
  default_interest_rate: number;
  interest_method: string;
  payout_frequency: string;
  premature_allowed: boolean;
  auto_renewal_allowed: boolean;
  status: string;
}

export default function DepositProductsPage() {
  const [products, setProducts] = useState<DepositProduct[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('ALL');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await fetch('http://localhost:8007/api/v1/products');
      const data = await response.json();
      setProducts(data);
    } catch (error) {
      console.error('Error fetching products:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredProducts = products.filter(product => {
    const matchesFilter = filter === 'ALL' || product.deposit_type === filter;
    const matchesSearch = product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         product.code.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  if (loading) {
    return <LoadingState />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50/30 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-4xl font-bold text-slate-900">Deposit Products</h1>
            <p className="text-slate-600 mt-2">
              Choose from our range of competitive deposit products
            </p>
          </div>
          
          <Link href="/deposits/calculator">
            <button className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors shadow-lg shadow-blue-200">
              Calculate Returns
            </button>
          </Link>
        </div>

        {/* Filters & Search */}
        <div className="bg-white rounded-xl shadow-lg border border-slate-200 p-6">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search products..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Filter Buttons */}
            <div className="flex gap-2">
              <FilterButton
                label="All"
                active={filter === 'ALL'}
                onClick={() => setFilter('ALL')}
              />
              <FilterButton
                label="Fixed Deposit"
                active={filter === 'FIXED_DEPOSIT'}
                onClick={() => setFilter('FIXED_DEPOSIT')}
                icon={<PiggyBank className="w-4 h-4" />}
              />
              <FilterButton
                label="Recurring Deposit"
                active={filter === 'RECURRING_DEPOSIT'}
                onClick={() => setFilter('RECURRING_DEPOSIT')}
                icon={<Clock className="w-4 h-4" />}
              />
            </div>
          </div>
        </div>

        {/* AI Recommendation Banner */}
        <div className="bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-white/20 rounded-xl">
              <Sparkles className="w-8 h-8" />
            </div>
            <div className="flex-1">
              <h3 className="text-xl font-bold mb-1">Get AI-Powered Recommendations</h3>
              <p className="text-white/90">
                Answer a few questions and let our AI suggest the perfect deposit plan for you
              </p>
            </div>
            <Link href="/deposits/ai/recommend">
              <button className="px-6 py-3 bg-white text-purple-600 rounded-lg font-medium hover:bg-purple-50 transition-colors">
                Get Recommendation
              </button>
            </Link>
          </div>
        </div>

        {/* Products Grid */}
        {filteredProducts.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-slate-600">No products found matching your criteria</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {filteredProducts.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        )}

        {/* Rate Comparison Tool */}
        <div className="bg-white rounded-xl shadow-lg border border-slate-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-slate-900">Compare Rates</h2>
              <p className="text-slate-600 mt-1">
                See how rates vary by amount and tenure
              </p>
            </div>
            <Link href="/deposits/compare">
              <button className="px-6 py-3 bg-slate-900 text-white rounded-lg font-medium hover:bg-slate-800 transition-colors">
                Detailed Comparison
              </button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

function ProductCard({ product }: { product: DepositProduct }) {
  const isRD = product.deposit_type === 'RECURRING_DEPOSIT';
  
  return (
    <div className="group bg-white rounded-xl shadow-lg border border-slate-200 hover:shadow-xl transition-all overflow-hidden">
      {/* Header */}
      <div className={`p-6 ${isRD ? 'bg-gradient-to-r from-orange-500 to-red-500' : 'bg-gradient-to-r from-blue-500 to-purple-500'}`}>
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-white/20 rounded-xl">
              {isRD ? (
                <Clock className="w-6 h-6 text-white" />
              ) : (
                <PiggyBank className="w-6 h-6 text-white" />
              )}
            </div>
            <div>
              <h3 className="text-xl font-bold text-white">{product.name}</h3>
              <p className="text-white/80 text-sm">{product.code}</p>
            </div>
          </div>
        </div>
        
        {/* Interest Rate Badge */}
        <div className="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-white/20 backdrop-blur-sm rounded-lg">
          <TrendingUp className="w-5 h-5 text-white" />
          <span className="text-2xl font-bold text-white">
            {product.default_interest_rate}%
          </span>
          <span className="text-white/80 text-sm">p.a.</span>
        </div>
      </div>

      {/* Details */}
      <div className="p-6 space-y-4">
        {/* Key Info */}
        <div className="grid grid-cols-2 gap-4">
          <InfoItem
            icon={<TrendingUp className="w-4 h-4 text-blue-600" />}
            label="Min Amount"
            value={`₹${product.min_amount.toLocaleString('en-IN')}`}
          />
          <InfoItem
            icon={<Calendar className="w-4 h-4 text-purple-600" />}
            label="Min Tenure"
            value={`${product.min_tenure_days} days`}
          />
          <InfoItem
            icon={<TrendingUp className="w-4 h-4 text-green-600" />}
            label="Max Amount"
            value={product.max_amount ? `₹${product.max_amount.toLocaleString('en-IN')}` : 'No Limit'}
          />
          <InfoItem
            icon={<Calendar className="w-4 h-4 text-orange-600" />}
            label="Max Tenure"
            value={`${product.max_tenure_days} days`}
          />
        </div>

        {/* Features */}
        <div className="space-y-2 pt-4 border-t border-slate-200">
          <FeatureItem
            icon={product.premature_allowed ? <CheckCircle className="w-4 h-4 text-green-600" /> : <XCircle className="w-4 h-4 text-slate-400" />}
            label="Premature Withdrawal"
            available={product.premature_allowed}
          />
          <FeatureItem
            icon={product.auto_renewal_allowed ? <CheckCircle className="w-4 h-4 text-green-600" /> : <XCircle className="w-4 h-4 text-slate-400" />}
            label="Auto Renewal"
            available={product.auto_renewal_allowed}
          />
          <FeatureItem
            icon={<CheckCircle className="w-4 h-4 text-green-600" />}
            label={product.payout_frequency.replace(/_/g, ' ')}
            available={true}
          />
        </div>

        {/* Actions */}
        <div className="flex gap-3 pt-4">
          <Link href={`/deposits/${isRD ? 'rd' : 'fd'}/new?product=${product.id}`} className="flex-1">
            <button className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center justify-center gap-2">
              Open Account
              <ArrowRight className="w-4 h-4" />
            </button>
          </Link>
          <Link href={`/deposits/products/${product.id}`}>
            <button className="px-6 py-3 border border-slate-300 rounded-lg font-medium hover:bg-slate-50 transition-colors">
              Details
            </button>
          </Link>
        </div>
      </div>
    </div>
  );
}

function FilterButton({ 
  label, 
  active, 
  onClick, 
  icon 
}: { 
  label: string; 
  active: boolean; 
  onClick: () => void;
  icon?: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 ${
        active
          ? 'bg-blue-600 text-white'
          : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
      }`}
    >
      {icon}
      {label}
    </button>
  );
}

function InfoItem({ 
  icon, 
  label, 
  value 
}: { 
  icon: React.ReactNode; 
  label: string; 
  value: string;
}) {
  return (
    <div className="flex items-start gap-2">
      <div className="mt-1">{icon}</div>
      <div>
        <p className="text-xs text-slate-600">{label}</p>
        <p className="font-semibold text-slate-900">{value}</p>
      </div>
    </div>
  );
}

function FeatureItem({ 
  icon, 
  label, 
  available 
}: { 
  icon: React.ReactNode; 
  label: string;
  available: boolean;
}) {
  return (
    <div className="flex items-center gap-2">
      {icon}
      <span className={`text-sm ${available ? 'text-slate-700' : 'text-slate-400'}`}>
        {label}
      </span>
    </div>
  );
}

function LoadingState() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50/30 p-8 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-slate-600">Loading products...</p>
      </div>
    </div>
  );
}
