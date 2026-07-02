"use client";

import { useState, useEffect } from "react";
import { goldApi } from "../../goldApi";

type JourneyStep = "session" | "search" | "customer" | "product" | "eligibility" | "application";

interface Session {
  id: string;
  session_number: string;
  status: string;
  customer_id?: string;
}

interface Customer {
  customer_id: string;
  name: string;
  phone?: string;
  email?: string;
  pan?: string;
  customer_segment?: string;
  existing_gold_loans: number;
  total_outstanding: number;
}

interface ProductRecommendation {
  product_id: string;
  product_code: string;
  product_name: string;
  recommendation_score: number;
  recommendation_reason: string;
  is_eligible: boolean;
}

export default function NewGoldJourneyPage() {
  const [currentStep, setCurrentStep] = useState<JourneyStep>("session");
  const [session, setSession] = useState<Session | null>(null);
  const [searchCriteria, setSearchCriteria] = useState({
    phone: "",
    pan: "",
    aadhar: "",
    name: "",
  });
  const [searchResults, setSearchResults] = useState<Customer[]>([]);
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [recommendations, setRecommendations] = useState<ProductRecommendation[]>([]);
  const [selectedProduct, setSelectedProduct] = useState<ProductRecommendation | null>(null);
  const [requestedAmount, setRequestedAmount] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Step 1: Create Session
  const handleCreateSession = async (channel: string) => {
    try {
      setLoading(true);
      setError(null);
      const sessionData = await goldApi.createJourneySession({
        channel,
        session_type: "new_loan",
        branch_id: "BRANCH-001", // From user context
        initiated_by_user_id: "USER-001", // From auth
      });
      setSession(sessionData);
      setCurrentStep("search");
    } catch (err) {
      setError("Failed to create session");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Step 2: Search Customer
  const handleSearchCustomer = async () => {
    if (!session) return;
    
    try {
      setLoading(true);
      setError(null);
      const results = await goldApi.searchCustomer({
        session_id: session.id,
        ...searchCriteria,
      });
      setSearchResults(results);
      
      if (results.length === 0) {
        setError("No customers found. You can create a new CIF.");
      }
    } catch (err) {
      setError("Search failed");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Step 3: Select Customer
  const handleSelectCustomer = async (customer: Customer) => {
    if (!session) return;
    
    try {
      setLoading(true);
      setError(null);
      await goldApi.selectCustomer(session.id, customer.customer_id);
      setSelectedCustomer(customer);
      setCurrentStep("product");
      
      // Fetch product recommendations
      await fetchRecommendations(customer.customer_id);
    } catch (err) {
      setError("Failed to select customer");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Step 4: Get Product Recommendations
  const fetchRecommendations = async (customerId: string) => {
    if (!session) return;
    
    try {
      const amount = parseFloat(requestedAmount) || undefined;
      const recs = await goldApi.getProductRecommendations(session.id, amount);
      setRecommendations(recs);
    } catch (err) {
      console.error("Failed to fetch recommendations:", err);
    }
  };

  // Step 5: Select Product
  const handleSelectProduct = async (product: ProductRecommendation) => {
    if (!session) return;
    
    try {
      setLoading(true);
      setError(null);
      await goldApi.selectProduct({
        session_id: session.id,
        product_id: product.product_id,
        requested_amount: parseFloat(requestedAmount) || null,
        selection_source: "customer_choice",
      });
      setSelectedProduct(product);
      setCurrentStep("eligibility");
      
      // Check eligibility
      await checkEligibility(product.product_id);
    } catch (err) {
      setError("Failed to select product");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Step 6: Check Eligibility
  const checkEligibility = async (productId: string) => {
    if (!session) return;
    
    try {
      const result = await goldApi.checkEligibility(session.id, productId);
      
      if (result.is_eligible) {
        setCurrentStep("application");
      } else {
        setError(
          `Eligibility check failed. ${result.failed_checks.length} requirements not met.`
        );
      }
    } catch (err) {
      setError("Eligibility check failed");
      console.error(err);
    }
  };

  const steps = [
    { id: "session", label: "Start", icon: "🚀" },
    { id: "search", label: "Customer", icon: "👤" },
    { id: "product", label: "Product", icon: "💰" },
    { id: "eligibility", label: "Eligibility", icon: "✅" },
    { id: "application", label: "Application", icon: "📋" },
  ];

  const getStepIndex = (step: JourneyStep) => {
    const map: Record<JourneyStep, number> = {
      session: 0,
      search: 1,
      customer: 1,
      product: 2,
      eligibility: 3,
      application: 4,
    };
    return map[step];
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">New Gold Loan Journey</h1>
          <p className="text-gray-600">Guide customer through gold loan application</p>
        </div>

        {/* Progress Steps */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between">
            {steps.map((step, index) => (
              <div key={step.id} className="flex items-center flex-1">
                <div className="flex flex-col items-center flex-1">
                  <div
                    className={`w-12 h-12 rounded-full flex items-center justify-center text-xl transition-colors ${
                      getStepIndex(currentStep) >= index
                        ? "bg-blue-600 text-white"
                        : "bg-gray-200 text-gray-500"
                    }`}
                  >
                    {step.icon}
                  </div>
                  <span
                    className={`text-sm mt-2 font-medium ${
                      getStepIndex(currentStep) >= index
                        ? "text-blue-600"
                        : "text-gray-500"
                    }`}
                  >
                    {step.label}
                  </span>
                </div>
                {index < steps.length - 1 && (
                  <div
                    className={`h-1 flex-1 mx-2 rounded transition-colors ${
                      getStepIndex(currentStep) > index ? "bg-blue-600" : "bg-gray-200"
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Session Info */}
        {session && (
          <div className="bg-blue-50 border border-blue-200 px-4 py-3 rounded-lg mb-6">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-sm text-blue-700 font-medium">
                  Session: {session.session_number}
                </span>
                <span className="ml-4 text-sm text-blue-600">Status: {session.status}</span>
              </div>
              {selectedCustomer && (
                <span className="text-sm text-blue-700">
                  Customer: {selectedCustomer.name}
                </span>
              )}
            </div>
          </div>
        )}

        {/* Step Content */}
        <div className="bg-white rounded-lg shadow-sm p-8">
          {/* Step 1: Create Session */}
          {currentStep === "session" && (
            <div className="text-center max-w-md mx-auto">
              <div className="text-6xl mb-6">🏦</div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Start Gold Loan Journey
              </h2>
              <p className="text-gray-600 mb-8">
                Select how the customer is approaching you
              </p>
              <div className="space-y-4">
                <button
                  onClick={() => handleCreateSession("branch")}
                  disabled={loading}
                  className="w-full px-6 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium text-lg disabled:bg-gray-400"
                >
                  🏢 Walk-in at Branch
                </button>
                <button
                  onClick={() => handleCreateSession("mobile")}
                  disabled={loading}
                  className="w-full px-6 py-4 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium text-lg disabled:bg-gray-400"
                >
                  📱 Mobile Application
                </button>
                <button
                  onClick={() => handleCreateSession("web")}
                  disabled={loading}
                  className="w-full px-6 py-4 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-medium text-lg disabled:bg-gray-400"
                >
                  🌐 Web Portal
                </button>
              </div>
            </div>
          )}

          {/* Step 2: Search Customer */}
          {currentStep === "search" && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Search Customer</h2>
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Mobile Number
                  </label>
                  <input
                    type="tel"
                    value={searchCriteria.phone}
                    onChange={(e) =>
                      setSearchCriteria({ ...searchCriteria, phone: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="10-digit mobile"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    PAN Number
                  </label>
                  <input
                    type="text"
                    value={searchCriteria.pan}
                    onChange={(e) =>
                      setSearchCriteria({ ...searchCriteria, pan: e.target.value.toUpperCase() })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="AAAAA1234A"
                    maxLength={10}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Aadhar Number
                  </label>
                  <input
                    type="text"
                    value={searchCriteria.aadhar}
                    onChange={(e) =>
                      setSearchCriteria({ ...searchCriteria, aadhar: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="12-digit Aadhar"
                    maxLength={12}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Customer Name
                  </label>
                  <input
                    type="text"
                    value={searchCriteria.name}
                    onChange={(e) =>
                      setSearchCriteria({ ...searchCriteria, name: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="Full name"
                  />
                </div>
              </div>

              <div className="flex gap-4">
                <button
                  onClick={handleSearchCustomer}
                  disabled={loading}
                  className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:bg-gray-400"
                >
                  {loading ? "Searching..." : "Search Customer"}
                </button>
                <button
                  onClick={() => setCurrentStep("customer")}
                  className="px-6 py-3 border border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 transition-colors font-medium"
                >
                  Create New CIF
                </button>
              </div>

              {/* Search Results */}
              {searchResults.length > 0 && (
                <div className="mt-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Found {searchResults.length} customer(s)
                  </h3>
                  <div className="space-y-3">
                    {searchResults.map((customer) => (
                      <div
                        key={customer.customer_id}
                        className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 cursor-pointer transition-colors"
                        onClick={() => handleSelectCustomer(customer)}
                      >
                        <div className="flex justify-between items-start">
                          <div>
                            <h4 className="font-semibold text-gray-900">{customer.name}</h4>
                            <p className="text-sm text-gray-600 mt-1">
                              {customer.phone} • {customer.pan}
                            </p>
                            {customer.customer_segment && (
                              <span className="inline-block mt-2 px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">
                                {customer.customer_segment}
                              </span>
                            )}
                          </div>
                          <div className="text-right">
                            <p className="text-sm text-gray-600">
                              Existing Gold Loans: {customer.existing_gold_loans}
                            </p>
                            {customer.total_outstanding > 0 && (
                              <p className="text-sm font-medium text-orange-600 mt-1">
                                Outstanding: ₹{customer.total_outstanding.toLocaleString()}
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Step 3: Product Selection */}
          {currentStep === "product" && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Select Gold Loan Product</h2>
              <p className="text-gray-600 mb-6">
                Choose the most suitable product for {selectedCustomer?.name}
              </p>

              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Requested Loan Amount (Optional)
                </label>
                <input
                  type="number"
                  value={requestedAmount}
                  onChange={(e) => {
                    setRequestedAmount(e.target.value);
                    if (session) {
                      fetchRecommendations(session.customer_id!);
                    }
                  }}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter amount"
                />
              </div>

              {recommendations.length > 0 ? (
                <div className="space-y-4">
                  {recommendations.map((rec) => (
                    <div
                      key={rec.product_id}
                      className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                        rec.is_eligible
                          ? "border-green-300 bg-green-50 hover:border-green-400"
                          : "border-gray-200 bg-gray-50 hover:border-gray-300"
                      }`}
                      onClick={() => rec.is_eligible && handleSelectProduct(rec)}
                    >
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900">
                            {rec.product_name}
                          </h3>
                          <p className="text-sm text-gray-600">{rec.product_code}</p>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className="text-sm font-medium text-gray-700">
                            Score: {(rec.recommendation_score * 100).toFixed(0)}%
                          </span>
                          {rec.is_eligible ? (
                            <span className="px-3 py-1 bg-green-100 text-green-700 text-sm rounded-full">
                              Eligible
                            </span>
                          ) : (
                            <span className="px-3 py-1 bg-gray-200 text-gray-600 text-sm rounded-full">
                              Not Eligible
                            </span>
                          )}
                        </div>
                      </div>
                      <p className="text-sm text-gray-700">{rec.recommendation_reason}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <p>Loading product recommendations...</p>
                </div>
              )}
            </div>
          )}

          {/* Step 4: Eligibility Check */}
          {currentStep === "eligibility" && (
            <div className="text-center">
              <div className="text-6xl mb-6">⏳</div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Checking Eligibility...
              </h2>
              <p className="text-gray-600">
                Validating customer against product requirements
              </p>
            </div>
          )}

          {/* Step 5: Create Application */}
          {currentStep === "application" && (
            <div className="text-center">
              <div className="text-6xl mb-6">✅</div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Eligibility Passed!</h2>
              <p className="text-gray-600 mb-8">
                Customer is eligible for {selectedProduct?.product_name}
              </p>
              <button
                onClick={() =>
                  (window.location.href = `/gold-lending/applications/new?session_id=${session?.id}`)
                }
                className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium text-lg"
              >
                Proceed to Gold Appraisal →
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
