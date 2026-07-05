"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { 
  ArrowLeft, 
  Edit, 
  Ban, 
  CheckCircle,
  User,
  Phone,
  Mail,
  MapPin,
  Briefcase,
  FileText,
  Users,
  Building2,
  AlertTriangle,
  TrendingUp
} from "lucide-react";

interface Customer {
  id: number;
  customer_code: string;
  customer_type: string;
  full_name: string;
  first_name?: string;
  middle_name?: string;
  last_name?: string;
  email?: string;
  mobile: string;
  alternate_mobile?: string;
  pan_number?: string;
  aadhaar_number?: string;
  date_of_birth?: string;
  age?: number;
  gender?: string;
  marital_status?: string;
  father_name?: string;
  mother_name?: string;
  occupation_name?: string;
  industry_name?: string;
  monthly_income?: number;
  current_address_line1?: string;
  current_city_name?: string;
  current_state_name?: string;
  current_pincode?: string;
  kyc_status: string;
  risk_rating: string;
  cibil_score?: number;
  is_active: boolean;
  is_blacklisted: boolean;
  blacklist_reason?: string;
  created_at: string;
}

export default function CustomerDetailPage() {
  const router = useRouter();
  const params = useParams();
  const customerId = params?.id as string;
  
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");

  useEffect(() => {
    if (customerId) {
      fetchCustomer();
    }
  }, [customerId]);

  const fetchCustomer = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/v1/customers/${customerId}`, {
        headers: { "Content-Type": "application/json" }
      });

      if (response.ok) {
        const data = await response.json();
        setCustomer(data);
      }
    } catch (error) {
      console.error("Error fetching customer:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleBlacklist = async () => {
    const reason = prompt("Enter reason for blacklisting:");
    if (!reason) return;

    try {
      const response = await fetch(`/api/v1/customers/${customerId}/blacklist?reason=${encodeURIComponent(reason)}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" }
      });

      if (response.ok) {
        alert("Customer blacklisted successfully");
        fetchCustomer();
      }
    } catch (error) {
      console.error("Error blacklisting customer:", error);
      alert("Failed to blacklist customer");
    }
  };

  const handleUnblacklist = async () => {
    if (!confirm("Remove customer from blacklist?")) return;

    try {
      const response = await fetch(`/api/v1/customers/${customerId}/unblacklist`, {
        method: "POST",
        headers: { "Content-Type": "application/json" }
      });

      if (response.ok) {
        alert("Customer removed from blacklist");
        fetchCustomer();
      }
    } catch (error) {
      console.error("Error unblacklisting customer:", error);
      alert("Failed to remove from blacklist");
    }
  };

  const getKYCBadge = (status: string) => {
    const badges = {
      pending: { bg: "bg-yellow-100", text: "text-yellow-800", label: "Pending" },
      in_progress: { bg: "bg-blue-100", text: "text-blue-800", label: "In Progress" },
      completed: { bg: "bg-green-100", text: "text-green-800", label: "Completed" },
      rejected: { bg: "bg-red-100", text: "text-red-800", label: "Rejected" }
    };
    const badge = badges[status as keyof typeof badges] || badges.pending;
    return (
      <span className={`px-3 py-1 text-sm font-medium rounded-full ${badge.bg} ${badge.text}`}>
        {badge.label}
      </span>
    );
  };

  const getRiskBadge = (rating: string) => {
    const badges = {
      low: { bg: "bg-green-100", text: "text-green-800", label: "Low Risk" },
      medium: { bg: "bg-yellow-100", text: "text-yellow-800", label: "Medium Risk" },
      high: { bg: "bg-orange-100", text: "text-orange-800", label: "High Risk" },
      very_high: { bg: "bg-red-100", text: "text-red-800", label: "Very High Risk" }
    };
    const badge = badges[rating as keyof typeof badges] || badges.medium;
    return (
      <span className={`px-3 py-1 text-sm font-medium rounded-full ${badge.bg} ${badge.text}`}>
        {badge.label}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!customer) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Customer Not Found</h2>
          <p className="text-gray-600 mb-4">The customer you're looking for doesn't exist.</p>
          <button
            onClick={() => router.push("/customers")}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Back to Customers
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => router.back()}
                className="w-10 h-10 flex items-center justify-center rounded-lg hover:bg-gray-100"
              >
                <ArrowLeft className="w-5 h-5" />
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{customer.full_name}</h1>
                <p className="text-sm text-gray-600 font-mono">{customer.customer_code}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              {customer.is_blacklisted ? (
                <button
                  onClick={handleUnblacklist}
                  className="flex items-center gap-2 px-4 py-2 border border-green-600 text-green-600 rounded-lg hover:bg-green-50"
                >
                  <CheckCircle className="w-4 h-4" />
                  Remove Blacklist
                </button>
              ) : (
                <button
                  onClick={handleBlacklist}
                  className="flex items-center gap-2 px-4 py-2 border border-red-600 text-red-600 rounded-lg hover:bg-red-50"
                >
                  <Ban className="w-4 h-4" />
                  Blacklist
                </button>
              )}
              <button
                onClick={() => router.push(`/customers/${customerId}/edit`)}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                <Edit className="w-4 h-4" />
                Edit
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Status Bar */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600">KYC Status:</span>
              {getKYCBadge(customer.kyc_status)}
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600">Risk Rating:</span>
              {getRiskBadge(customer.risk_rating)}
            </div>
            {customer.cibil_score && (
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600">CIBIL:</span>
                <span className={`text-lg font-bold ${
                  customer.cibil_score >= 750 ? 'text-green-600' :
                  customer.cibil_score >= 650 ? 'text-yellow-600' :
                  'text-red-600'
                }`}>
                  {customer.cibil_score}
                </span>
              </div>
            )}
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600">Status:</span>
              {customer.is_active ? (
                <span className="flex items-center gap-1 text-sm font-medium text-green-700">
                  <CheckCircle className="w-4 h-4" />
                  Active
                </span>
              ) : (
                <span className="flex items-center gap-1 text-sm font-medium text-red-700">
                  <Ban className="w-4 h-4" />
                  Inactive
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex gap-8">
            {['overview', 'kyc', 'documents', 'family', 'accounts'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Personal Information */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center gap-2 mb-4">
                <User className="w-5 h-5 text-blue-600" />
                <h2 className="text-lg font-semibold text-gray-900">Personal Information</h2>
              </div>
              <dl className="space-y-3">
                <div className="flex justify-between">
                  <dt className="text-sm text-gray-600">Full Name</dt>
                  <dd className="text-sm font-medium text-gray-900">{customer.full_name}</dd>
                </div>
                {customer.date_of_birth && (
                  <div className="flex justify-between">
                    <dt className="text-sm text-gray-600">Date of Birth</dt>
                    <dd className="text-sm font-medium text-gray-900">
                      {new Date(customer.date_of_birth).toLocaleDateString('en-IN')}
                      {customer.age && ` (${customer.age} years)`}
                    </dd>
                  </div>
                )}
                {customer.gender && (
                  <div className="flex justify-between">
                    <dt className="text-sm text-gray-600">Gender</dt>
                    <dd className="text-sm font-medium text-gray-900 capitalize">{customer.gender}</dd>
                  </div>
                )}
                {customer.marital_status && (
                  <div className="flex justify-between">
                    <dt className="text-sm text-gray-600">Marital Status</dt>
                    <dd className="text-sm font-medium text-gray-900 capitalize">{customer.marital_status}</dd>
                  </div>
                )}
                {customer.father_name && (
                  <div className="flex justify-between">
                    <dt className="text-sm text-gray-600">Father's Name</dt>
                    <dd className="text-sm font-medium text-gray-900">{customer.father_name}</dd>
                  </div>
                )}
                {customer.mother_name && (
                  <div className="flex justify-between">
                    <dt className="text-sm text-gray-600">Mother's Name</dt>
                    <dd className="text-sm font-medium text-gray-900">{customer.mother_name}</dd>
                  </div>
                )}
              </dl>
            </div>

            {/* Contact Information */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center gap-2 mb-4">
                <Phone className="w-5 h-5 text-green-600" />
                <h2 className="text-lg font-semibold text-gray-900">Contact Information</h2>
              </div>
              <dl className="space-y-3">
                <div className="flex justify-between">
                  <dt className="text-sm text-gray-600">Mobile</dt>
                  <dd className="text-sm font-medium text-gray-900">{customer.mobile}</dd>
                </div>
                {customer.alternate_mobile && (
                  <div className="flex justify-between">
                    <dt className="text-sm text-gray-600">Alternate Mobile</dt>
                    <dd className="text-sm font-medium text-gray-900">{customer.alternate_mobile}</dd>
                  </div>
                )}
                {customer.email && (
                  <div className="flex justify-between">
                    <dt className="text-sm text-gray-600">Email</dt>
                    <dd className="text-sm font-medium text-gray-900">{customer.email}</dd>
                  </div>
                )}
              </dl>
            </div>

            {/* Identity Information */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center gap-2 mb-4">
                <FileText className="w-5 h-5 text-purple-600" />
                <h2 className="text-lg font-semibold text-gray-900">Identity Information</h2>
              </div>
              <dl className="space-y-3">
                {customer.pan_number && (
                  <div className="flex justify-between">
                    <dt className="text-sm text-gray-600">PAN Number</dt>
                    <dd className="text-sm font-medium text-gray-900 font-mono">{customer.pan_number}</dd>
                  </div>
                )}
                {customer.aadhaar_number && (
                  <div className="flex justify-between">
                    <dt className="text-sm text-gray-600">Aadhaar Number</dt>
                    <dd className="text-sm font-medium text-gray-900 font-mono">
                      {customer.aadhaar_number.replace(/(\d{4})(\d{4})(\d{4})/, '$1-$2-$3')}
                    </dd>
                  </div>
                )}
              </dl>
            </div>

            {/* Occupation & Income */}
            {(customer.occupation_name || customer.monthly_income) && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center gap-2 mb-4">
                  <Briefcase className="w-5 h-5 text-orange-600" />
                  <h2 className="text-lg font-semibold text-gray-900">Occupation & Income</h2>
                </div>
                <dl className="space-y-3">
                  {customer.occupation_name && (
                    <div className="flex justify-between">
                      <dt className="text-sm text-gray-600">Occupation</dt>
                      <dd className="text-sm font-medium text-gray-900">{customer.occupation_name}</dd>
                    </div>
                  )}
                  {customer.industry_name && (
                    <div className="flex justify-between">
                      <dt className="text-sm text-gray-600">Industry</dt>
                      <dd className="text-sm font-medium text-gray-900">{customer.industry_name}</dd>
                    </div>
                  )}
                  {customer.monthly_income && (
                    <div className="flex justify-between">
                      <dt className="text-sm text-gray-600">Monthly Income</dt>
                      <dd className="text-sm font-medium text-gray-900">
                        ₹{customer.monthly_income.toLocaleString('en-IN')}
                      </dd>
                    </div>
                  )}
                </dl>
              </div>
            )}

            {/* Address */}
            {customer.current_address_line1 && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 lg:col-span-2">
                <div className="flex items-center gap-2 mb-4">
                  <MapPin className="w-5 h-5 text-red-600" />
                  <h2 className="text-lg font-semibold text-gray-900">Current Address</h2>
                </div>
                <p className="text-sm text-gray-900">
                  {customer.current_address_line1}
                  {customer.current_city_name && `, ${customer.current_city_name}`}
                  {customer.current_state_name && `, ${customer.current_state_name}`}
                  {customer.current_pincode && ` - ${customer.current_pincode}`}
                </p>
              </div>
            )}

            {/* Blacklist Warning */}
            {customer.is_blacklisted && customer.blacklist_reason && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-6 lg:col-span-2">
                <div className="flex items-start gap-3">
                  <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <h3 className="text-sm font-semibold text-red-900 mb-1">Customer Blacklisted</h3>
                    <p className="text-sm text-red-700">{customer.blacklist_reason}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Other tabs content (placeholder) */}
        {activeTab !== 'overview' && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {activeTab.charAt(0).toUpperCase() + activeTab.slice(1)} Section
            </h3>
            <p className="text-sm text-gray-600">
              This section is under development. Will include {activeTab} management features.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
