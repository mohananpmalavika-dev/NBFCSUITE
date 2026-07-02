"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { goldApi } from "../../goldApi";

interface GoldProduct {
  id: string;
  product_code: string;
  product_name: string;
  product_type: string;
  description?: string;
  is_active: boolean;
  display_order: number;
  created_at: string;
  updated_at: string;
  interest?: any;
  tenure?: any;
  limits?: any;
  charges?: any[];
  documents?: any[];
  eligibility?: any[];
  workflow?: any[];
  channels?: any[];
  taxes?: any[];
}

export default function ProductDetailPage() {
  const params = useParams();
  const productId = params?.id as string;
  const [product, setProduct] = useState<GoldProduct | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState("overview");

  useEffect(() => {
    if (productId) {
      loadProduct();
    }
  }, [productId]);

  const loadProduct = async () => {
    try {
      setLoading(true);
      const data = await goldApi.getProduct(productId);
      setProduct(data);
      setError(null);
    } catch (err) {
      setError("Failed to load product details");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount?: number) => {
    if (!amount) return "N/A";
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-IN", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-lg">
            {error || "Product not found"}
          </div>
        </div>
      </div>
    );
  }

  const tabs = [
    { id: "overview", label: "Overview", icon: "📋" },
    { id: "interest", label: "Interest & Tenure", icon: "💰" },
    { id: "limits", label: "Limits & LTV", icon: "📊" },
    { id: "charges", label: "Charges & Fees", icon: "💳" },
    { id: "documents", label: "Documents", icon: "📄" },
    { id: "eligibility", label: "Eligibility", icon: "✅" },
    { id: "workflow", label: "Workflow", icon: "🔄" },
    { id: "channels", label: "Channels", icon: "🌐" },
  ];

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => (window.location.href = "/gold-lending/products")}
            className="text-blue-600 hover:text-blue-800 mb-4 flex items-center gap-2"
          >
            ← Back to Products
          </button>
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                {product.product_name}
              </h1>
              <p className="text-gray-600">{product.product_code}</p>
            </div>
            <div className="flex items-center gap-3">
              <span
                className={`px-4 py-2 rounded-full text-sm font-medium ${
                  product.is_active
                    ? "bg-green-100 text-green-800"
                    : "bg-gray-100 text-gray-800"
                }`}
              >
                {product.is_active ? "Active" : "Inactive"}
              </span>
              <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                Edit Product
              </button>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-sm mb-6">
          <div className="border-b border-gray-200 overflow-x-auto">
            <nav className="flex gap-2 px-4">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-4 py-3 text-sm font-medium border-b-2 whitespace-nowrap transition-colors ${
                    activeTab === tab.id
                      ? "border-blue-600 text-blue-600"
                      : "border-transparent text-gray-600 hover:text-gray-900"
                  }`}
                >
                  {tab.icon} {tab.label}
                </button>
              ))}
            </nav>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {/* Overview Tab */}
            {activeTab === "overview" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Product Information
                  </h3>
                  <div className="grid grid-cols-2 gap-6">
                    <div>
                      <label className="text-sm text-gray-600">Product Type</label>
                      <p className="text-base font-medium text-gray-900 mt-1">
                        {product.product_type.replace("_", " ").toUpperCase()}
                      </p>
                    </div>
                    <div>
                      <label className="text-sm text-gray-600">Display Order</label>
                      <p className="text-base font-medium text-gray-900 mt-1">
                        {product.display_order}
                      </p>
                    </div>
                    <div className="col-span-2">
                      <label className="text-sm text-gray-600">Description</label>
                      <p className="text-base text-gray-900 mt-1">
                        {product.description || "No description provided"}
                      </p>
                    </div>
                    <div>
                      <label className="text-sm text-gray-600">Created At</label>
                      <p className="text-base text-gray-900 mt-1">
                        {formatDate(product.created_at)}
                      </p>
                    </div>
                    <div>
                      <label className="text-sm text-gray-600">Last Updated</label>
                      <p className="text-base text-gray-900 mt-1">
                        {formatDate(product.updated_at)}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Interest & Tenure Tab */}
            {activeTab === "interest" && (
              <div className="space-y-6">
                {product.interest ? (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                      Interest Configuration
                    </h3>
                    <div className="grid grid-cols-2 gap-6">
                      <div>
                        <label className="text-sm text-gray-600">Base Rate</label>
                        <p className="text-2xl font-bold text-blue-600 mt-1">
                          {product.interest.base_rate}% p.a.
                        </p>
                      </div>
                      <div>
                        <label className="text-sm text-gray-600">Interest Type</label>
                        <p className="text-base font-medium text-gray-900 mt-1">
                          {product.interest.interest_type}
                        </p>
                      </div>
                      <div>
                        <label className="text-sm text-gray-600">Rate Type</label>
                        <p className="text-base font-medium text-gray-900 mt-1">
                          {product.interest.rate_type}
                        </p>
                      </div>
                      <div>
                        <label className="text-sm text-gray-600">Penal Interest</label>
                        <p className="text-base font-medium text-gray-900 mt-1">
                          {product.interest.penal_interest}% p.a.
                        </p>
                      </div>
                      <div>
                        <label className="text-sm text-gray-600">Compounding</label>
                        <p className="text-base font-medium text-gray-900 mt-1">
                          {product.interest.compounding_frequency || "None"}
                        </p>
                      </div>
                    </div>
                  </div>
                ) : (
                  <p className="text-gray-600">No interest configuration set</p>
                )}

                {product.tenure && (
                  <div className="pt-6 border-t">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                      Tenure Configuration
                    </h3>
                    <div className="grid grid-cols-3 gap-6">
                      <div>
                        <label className="text-sm text-gray-600">Min Tenure</label>
                        <p className="text-base font-medium text-gray-900 mt-1">
                          {product.tenure.min_tenure_months} months
                        </p>
                      </div>
                      <div>
                        <label className="text-sm text-gray-600">Max Tenure</label>
                        <p className="text-base font-medium text-gray-900 mt-1">
                          {product.tenure.max_tenure_months} months
                        </p>
                      </div>
                      <div>
                        <label className="text-sm text-gray-600">Default Tenure</label>
                        <p className="text-base font-medium text-gray-900 mt-1">
                          {product.tenure.default_tenure_months} months
                        </p>
                      </div>
                      <div>
                        <label className="text-sm text-gray-600">Renewal Allowed</label>
                        <p className="text-base font-medium text-gray-900 mt-1">
                          {product.tenure.renewal_allowed ? "Yes" : "No"}
                        </p>
                      </div>
                      <div>
                        <label className="text-sm text-gray-600">Max Renewals</label>
                        <p className="text-base font-medium text-gray-900 mt-1">
                          {product.tenure.max_renewals || "Unlimited"}
                        </p>
                      </div>
                      <div>
                        <label className="text-sm text-gray-600">Auto Renewal</label>
                        <p className="text-base font-medium text-gray-900 mt-1">
                          {product.tenure.auto_renewal ? "Yes" : "No"}
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Limits Tab */}
            {activeTab === "limits" && product.limits && (
              <div className="space-y-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Loan Limits & LTV
                </h3>
                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <label className="text-sm text-gray-600">Min Loan Amount</label>
                    <p className="text-xl font-bold text-gray-900 mt-1">
                      {formatCurrency(product.limits.min_loan_amount)}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-600">Max Loan Amount</label>
                    <p className="text-xl font-bold text-gray-900 mt-1">
                      {formatCurrency(product.limits.max_loan_amount)}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-600">LTV Percentage</label>
                    <p className="text-xl font-bold text-blue-600 mt-1">
                      {product.limits.ltv_percent}%
                    </p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-600">Min Gold Weight</label>
                    <p className="text-base font-medium text-gray-900 mt-1">
                      {product.limits.min_gold_weight_grams} grams
                    </p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-600">Max Gold Weight</label>
                    <p className="text-base font-medium text-gray-900 mt-1">
                      {product.limits.max_gold_weight_grams
                        ? `${product.limits.max_gold_weight_grams} grams`
                        : "Unlimited"}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-600">Purity Threshold</label>
                    <p className="text-base font-medium text-gray-900 mt-1">
                      {product.limits.purity_threshold_karat}K
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Charges Tab */}
            {activeTab === "charges" && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Charges & Fees
                </h3>
                {product.charges && product.charges.length > 0 ? (
                  <div className="space-y-3">
                    {product.charges.map((charge: any) => (
                      <div
                        key={charge.id}
                        className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors"
                      >
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <h4 className="font-semibold text-gray-900">{charge.charge_name}</h4>
                            <p className="text-sm text-gray-600 mt-1">{charge.charge_code}</p>
                          </div>
                          <div className="text-right">
                            <p className="text-lg font-bold text-gray-900">
                              {charge.charge_type === "percentage"
                                ? `${charge.charge_percentage}%`
                                : formatCurrency(charge.charge_amount)}
                            </p>
                            <p className="text-xs text-gray-500 mt-1">
                              {charge.charge_frequency}
                            </p>
                          </div>
                        </div>
                        <div className="flex gap-2 mt-3">
                          {charge.is_mandatory && (
                            <span className="px-2 py-1 bg-red-100 text-red-700 text-xs rounded">
                              Mandatory
                            </span>
                          )}
                          {charge.is_refundable && (
                            <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded">
                              Refundable
                            </span>
                          )}
                          {charge.tax_applicable && (
                            <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">
                              Tax Applicable
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-600">No charges configured</p>
                )}
              </div>
            )}

            {/* Documents Tab */}
            {activeTab === "documents" && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Required Documents
                </h3>
                {product.documents && product.documents.length > 0 ? (
                  <div className="grid grid-cols-2 gap-4">
                    {product.documents.map((doc: any) => (
                      <div
                        key={doc.id}
                        className="border border-gray-200 rounded-lg p-4"
                      >
                        <h4 className="font-semibold text-gray-900">{doc.document_name}</h4>
                        <p className="text-sm text-gray-600 mt-1">{doc.document_type}</p>
                        <div className="flex gap-2 mt-3">
                          {doc.is_mandatory && (
                            <span className="px-2 py-1 bg-red-100 text-red-700 text-xs rounded">
                              Mandatory
                            </span>
                          )}
                          {doc.verification_required && (
                            <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">
                              Verification Required
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-600">No documents configured</p>
                )}
              </div>
            )}

            {/* Eligibility Tab */}
            {activeTab === "eligibility" && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Eligibility Rules
                </h3>
                {product.eligibility && product.eligibility.length > 0 ? (
                  <div className="space-y-3">
                    {product.eligibility.map((rule: any) => (
                      <div
                        key={rule.id}
                        className="border border-gray-200 rounded-lg p-4"
                      >
                        <div className="flex justify-between items-start">
                          <div>
                            <h4 className="font-semibold text-gray-900">{rule.rule_name}</h4>
                            <p className="text-sm text-gray-600 mt-1">
                              Type: {rule.rule_type} | Operator: {rule.rule_operator}
                            </p>
                            {rule.error_message && (
                              <p className="text-sm text-red-600 mt-2">{rule.error_message}</p>
                            )}
                          </div>
                          {rule.is_mandatory && (
                            <span className="px-2 py-1 bg-red-100 text-red-700 text-xs rounded">
                              Mandatory
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-600">No eligibility rules configured</p>
                )}
              </div>
            )}

            {/* Workflow Tab */}
            {activeTab === "workflow" && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Approval Workflow
                </h3>
                {product.workflow && product.workflow.length > 0 ? (
                  <div className="space-y-4">
                    {product.workflow.map((stage: any, index: number) => (
                      <div key={stage.id} className="flex items-start gap-4">
                        <div className="flex-shrink-0 w-10 h-10 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                          {stage.stage_order}
                        </div>
                        <div className="flex-1 border border-gray-200 rounded-lg p-4">
                          <h4 className="font-semibold text-gray-900">{stage.stage_name}</h4>
                          <div className="grid grid-cols-2 gap-4 mt-3 text-sm">
                            <div>
                              <span className="text-gray-600">Type:</span>
                              <span className="ml-2 font-medium">{stage.stage_type}</span>
                            </div>
                            {stage.approver_role && (
                              <div>
                                <span className="text-gray-600">Role:</span>
                                <span className="ml-2 font-medium">{stage.approver_role}</span>
                              </div>
                            )}
                            {stage.sla_hours && (
                              <div>
                                <span className="text-gray-600">SLA:</span>
                                <span className="ml-2 font-medium">{stage.sla_hours} hours</span>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-600">No workflow configured</p>
                )}
              </div>
            )}

            {/* Channels Tab */}
            {activeTab === "channels" && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Available Channels
                </h3>
                {product.channels && product.channels.length > 0 ? (
                  <div className="grid grid-cols-2 gap-4">
                    {product.channels.map((channel: any) => (
                      <div
                        key={channel.id}
                        className={`border rounded-lg p-4 ${
                          channel.is_enabled
                            ? "border-green-300 bg-green-50"
                            : "border-gray-200 bg-gray-50"
                        }`}
                      >
                        <div className="flex justify-between items-start">
                          <h4 className="font-semibold text-gray-900">
                            {channel.channel_type.toUpperCase()}
                          </h4>
                          <span
                            className={`px-2 py-1 text-xs rounded ${
                              channel.is_enabled
                                ? "bg-green-100 text-green-700"
                                : "bg-gray-200 text-gray-600"
                            }`}
                          >
                            {channel.is_enabled ? "Enabled" : "Disabled"}
                          </span>
                        </div>
                        {channel.instant_approval_limit && (
                          <p className="text-sm text-gray-600 mt-2">
                            Instant Approval:{" "}
                            {formatCurrency(channel.instant_approval_limit)}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-600">No channels configured</p>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
