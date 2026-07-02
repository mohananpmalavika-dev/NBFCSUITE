"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { goldApi } from "../../goldApi";

interface AppraisalSession {
  id: string;
  session_number: string;
  customer_id: string;
  session_status: string;
  total_ornaments: number;
  total_gross_weight: number;
  total_net_weight: number;
  total_appraised_value: number;
  average_purity_karat: number;
  ltv_percent: number;
  eligible_loan_amount: number;
}

interface Ornament {
  id: string;
  ornament_type: string;
  barcode?: string;
  gross_weight_grams: number;
  stone_weight_grams: number;
  net_weight_grams: number;
  purity_karat: number;
  purity_percent: number;
  appraised_value: number;
  is_hallmarked: boolean;
  status: string;
  photo_urls?: string[];
}

interface OrnamentType {
  id: string;
  type_code: string;
  type_name: string;
  category: string;
  typical_stone_percentage: number;
}

interface MarketRate {
  id: string;
  purity_karat: number;
  rate_per_gram: number;
  rate_date: string;
}

export default function AppraisalPage() {
  const params = useParams();
  const sessionId = params?.sessionId as string;
  
  const [session, setSession] = useState<AppraisalSession | null>(null);
  const [ornaments, setOrnaments] = useState<Ornament[]>([]);
  const [ornamentTypes, setOrnamentTypes] = useState<OrnamentType[]>([]);
  const [marketRates, setMarketRates] = useState<MarketRate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // New ornament form
  const [showAddOrnament, setShowAddOrnament] = useState(false);
  const [newOrnament, setNewOrnament] = useState({
    ornament_type_id: "",
    gross_weight_grams: "",
    stone_weight_grams: "",
    purity_karat: "22",
    is_hallmarked: false,
    hallmark_id: "",
  });

  useEffect(() => {
    if (sessionId) {
      loadAppraisalData();
    }
  }, [sessionId]);

  const loadAppraisalData = async () => {
    try {
      setLoading(true);
      const [sessionData, types, rates] = await Promise.all([
        goldApi.getAppraisalSession(sessionId),
        goldApi.listOrnamentTypes(),
        goldApi.getCurrentMarketRates(),
      ]);
      
      setSession(sessionData.session);
      setOrnaments(sessionData.ornaments || []);
      setOrnamentTypes(types);
      setMarketRates(rates);
      setError(null);
    } catch (err) {
      setError("Failed to load appraisal data");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddOrnament = async () => {
    if (!newOrnament.ornament_type_id || !newOrnament.gross_weight_grams) {
      setError("Please fill in required fields");
      return;
    }

    try {
      setLoading(true);
      
      // Calculate net weight
      const grossWeight = parseFloat(newOrnament.gross_weight_grams);
      const stoneWeight = parseFloat(newOrnament.stone_weight_grams || "0");
      const netWeight = grossWeight - stoneWeight;
      
      // Get current gold rate for selected purity
      const purity = parseFloat(newOrnament.purity_karat);
      const rate = marketRates.find(r => r.purity_karat === purity);
      
      if (!rate) {
        setError(`No market rate found for ${purity}K gold`);
        return;
      }
      
      // Calculate value
      const purityPercent = (purity / 24) * 100;
      const appraisedValue = netWeight * rate.rate_per_gram * purityPercent / 100;
      
      const ornamentData = {
        ornament_type_id: newOrnament.ornament_type_id,
        ornament_type: ornamentTypes.find(t => t.id === newOrnament.ornament_type_id)?.type_name || "",
        gross_weight_grams: grossWeight,
        stone_weight_grams: stoneWeight,
        purity_karat: purity,
        is_hallmarked: newOrnament.is_hallmarked,
        hallmark_id: newOrnament.hallmark_id,
      };
      
      // In production: await goldApi.catalogOrnament(sessionId, ornamentData);
      
      // Reload data
      await loadAppraisalData();
      
      // Reset form
      setNewOrnament({
        ornament_type_id: "",
        gross_weight_grams: "",
        stone_weight_grams: "",
        purity_karat: "22",
        is_hallmarked: false,
        hallmark_id: "",
      });
      setShowAddOrnament(false);
      setError(null);
    } catch (err) {
      setError("Failed to add ornament");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCompleteAppraisal = async () => {
    if (!session) return;
    
    if (ornaments.length === 0) {
      setError("Please add at least one ornament before completing");
      return;
    }

    try {
      setLoading(true);
      await goldApi.completeAppraisalSession(sessionId);
      await loadAppraisalData();
      setError(null);
    } catch (err) {
      setError("Failed to complete appraisal");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getPurityBadgeColor = (karat: number) => {
    if (karat >= 22) return "bg-yellow-100 text-yellow-800";
    if (karat >= 20) return "bg-orange-100 text-orange-800";
    return "bg-gray-100 text-gray-800";
  };

  if (loading && !session) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => window.history.back()}
            className="text-blue-600 hover:text-blue-800 mb-4 flex items-center gap-2"
          >
            ← Back
          </button>
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Gold Appraisal
              </h1>
              <p className="text-gray-600">
                Session: {session?.session_number}
              </p>
            </div>
            <span
              className={`px-4 py-2 rounded-full text-sm font-medium ${
                session?.session_status === "completed"
                  ? "bg-green-100 text-green-800"
                  : "bg-blue-100 text-blue-800"
              }`}
            >
              {session?.session_status}
            </span>
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Summary Cards */}
        {session && (
          <div className="grid grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-lg shadow-sm p-4">
              <div className="text-sm text-gray-600 mb-1">Total Ornaments</div>
              <div className="text-2xl font-bold text-gray-900">
                {session.total_ornaments}
              </div>
            </div>
            <div className="bg-white rounded-lg shadow-sm p-4">
              <div className="text-sm text-gray-600 mb-1">Net Weight</div>
              <div className="text-2xl font-bold text-gray-900">
                {session.total_net_weight.toFixed(3)}g
              </div>
            </div>
            <div className="bg-white rounded-lg shadow-sm p-4">
              <div className="text-sm text-gray-600 mb-1">Total Value</div>
              <div className="text-2xl font-bold text-blue-600">
                {formatCurrency(session.total_appraised_value)}
              </div>
            </div>
            <div className="bg-white rounded-lg shadow-sm p-4">
              <div className="text-sm text-gray-600 mb-1">Eligible Loan</div>
              <div className="text-2xl font-bold text-green-600">
                {formatCurrency(session.eligible_loan_amount)}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {session.ltv_percent}% LTV
              </div>
            </div>
          </div>
        )}

        {/* Market Rates */}
        {marketRates.length > 0 && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <div className="flex items-center justify-between">
              <div className="text-sm font-medium text-blue-900">
                Current Gold Rates
              </div>
              <div className="flex gap-4">
                {marketRates.map((rate) => (
                  <div key={rate.id} className="text-sm">
                    <span className="font-semibold text-blue-900">
                      {rate.purity_karat}K:
                    </span>
                    <span className="ml-2 text-blue-700">
                      ₹{rate.rate_per_gram.toLocaleString()}/g
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Ornaments List */}
        <div className="bg-white rounded-lg shadow-sm mb-6">
          <div className="p-4 border-b border-gray-200 flex justify-between items-center">
            <h2 className="text-lg font-semibold text-gray-900">
              Ornaments ({ornaments.length})
            </h2>
            {session?.session_status !== "completed" && (
              <button
                onClick={() => setShowAddOrnament(true)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                + Add Ornament
              </button>
            )}
          </div>

          {ornaments.length === 0 ? (
            <div className="p-12 text-center text-gray-500">
              <div className="text-6xl mb-4">💍</div>
              <p className="text-lg font-medium mb-2">No ornaments added yet</p>
              <p className="text-sm">Start by adding ornaments for appraisal</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {ornaments.map((ornament, index) => (
                <div key={ornament.id} className="p-4 hover:bg-gray-50">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-lg font-semibold text-gray-900">
                          #{index + 1}
                        </span>
                        <h3 className="text-lg font-semibold text-gray-900">
                          {ornament.ornament_type}
                        </h3>
                        {ornament.is_hallmarked && (
                          <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full">
                            ✓ Hallmarked
                          </span>
                        )}
                        <span
                          className={`px-2 py-1 text-xs rounded-full ${getPurityBadgeColor(
                            ornament.purity_karat
                          )}`}
                        >
                          {ornament.purity_karat}K
                        </span>
                      </div>
                      {ornament.barcode && (
                        <p className="text-sm text-gray-600 mb-3">
                          Barcode: {ornament.barcode}
                        </p>
                      )}
                      <div className="grid grid-cols-4 gap-4 text-sm">
                        <div>
                          <span className="text-gray-600">Gross Weight:</span>
                          <span className="ml-2 font-medium text-gray-900">
                            {ornament.gross_weight_grams.toFixed(3)}g
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-600">Stone Weight:</span>
                          <span className="ml-2 font-medium text-gray-900">
                            {ornament.stone_weight_grams.toFixed(3)}g
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-600">Net Weight:</span>
                          <span className="ml-2 font-medium text-gray-900">
                            {ornament.net_weight_grams.toFixed(3)}g
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-600">Purity:</span>
                          <span className="ml-2 font-medium text-gray-900">
                            {ornament.purity_percent.toFixed(2)}%
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-xl font-bold text-blue-600 mb-1">
                        {formatCurrency(ornament.appraised_value)}
                      </div>
                      <div className="text-sm text-gray-500">Appraised Value</div>
                    </div>
                  </div>
                  {ornament.photo_urls && ornament.photo_urls.length > 0 && (
                    <div className="mt-3 flex gap-2">
                      {ornament.photo_urls.map((url, idx) => (
                        <img
                          key={idx}
                          src={url}
                          alt={`Ornament ${index + 1} photo ${idx + 1}`}
                          className="w-20 h-20 object-cover rounded border border-gray-200"
                        />
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Add Ornament Modal */}
        {showAddOrnament && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4">
              <div className="p-6 border-b border-gray-200">
                <h3 className="text-xl font-semibold text-gray-900">
                  Add Ornament
                </h3>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Ornament Type *
                    </label>
                    <select
                      value={newOrnament.ornament_type_id}
                      onChange={(e) =>
                        setNewOrnament({
                          ...newOrnament,
                          ornament_type_id: e.target.value,
                        })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Select type</option>
                      {ornamentTypes.map((type) => (
                        <option key={type.id} value={type.id}>
                          {type.type_name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Purity (Karat) *
                    </label>
                    <select
                      value={newOrnament.purity_karat}
                      onChange={(e) =>
                        setNewOrnament({
                          ...newOrnament,
                          purity_karat: e.target.value,
                        })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="24">24K (99.9%)</option>
                      <option value="22">22K (91.6%)</option>
                      <option value="20">20K (83.3%)</option>
                      <option value="18">18K (75.0%)</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Gross Weight (grams) *
                    </label>
                    <input
                      type="number"
                      step="0.001"
                      value={newOrnament.gross_weight_grams}
                      onChange={(e) =>
                        setNewOrnament({
                          ...newOrnament,
                          gross_weight_grams: e.target.value,
                        })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      placeholder="0.000"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Stone Weight (grams)
                    </label>
                    <input
                      type="number"
                      step="0.001"
                      value={newOrnament.stone_weight_grams}
                      onChange={(e) =>
                        setNewOrnament({
                          ...newOrnament,
                          stone_weight_grams: e.target.value,
                        })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      placeholder="0.000"
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={newOrnament.is_hallmarked}
                        onChange={(e) =>
                          setNewOrnament({
                            ...newOrnament,
                            is_hallmarked: e.target.checked,
                          })
                        }
                        className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                      />
                      <span className="text-sm font-medium text-gray-700">
                        Is Hallmarked
                      </span>
                    </label>
                  </div>
                  {newOrnament.is_hallmarked && (
                    <div className="col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Hallmark ID
                      </label>
                      <input
                        type="text"
                        value={newOrnament.hallmark_id}
                        onChange={(e) =>
                          setNewOrnament({
                            ...newOrnament,
                            hallmark_id: e.target.value,
                          })
                        }
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        placeholder="Enter hallmark ID"
                      />
                    </div>
                  )}
                </div>
              </div>
              <div className="p-6 border-t border-gray-200 flex justify-end gap-3">
                <button
                  onClick={() => setShowAddOrnament(false)}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleAddOrnament}
                  disabled={loading}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
                >
                  {loading ? "Adding..." : "Add Ornament"}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        {session?.session_status === "in_progress" && (
          <div className="flex justify-end gap-3">
            <button
              onClick={handleCompleteAppraisal}
              disabled={loading || ornaments.length === 0}
              className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium disabled:bg-gray-400"
            >
              Complete Appraisal
            </button>
          </div>
        )}

        {session?.session_status === "completed" && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
            <div className="text-4xl mb-3">✅</div>
            <h3 className="text-xl font-semibold text-green-900 mb-2">
              Appraisal Completed
            </h3>
            <p className="text-green-700 mb-4">
              Eligible Loan Amount: {formatCurrency(session.eligible_loan_amount)}
            </p>
            <button
              onClick={() =>
                (window.location.href = `/gold-lending/applications/${session.id}/vault`)
              }
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Proceed to Vault Storage →
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
