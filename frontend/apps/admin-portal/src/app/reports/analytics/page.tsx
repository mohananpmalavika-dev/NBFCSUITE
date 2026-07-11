"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  Brain, TrendingUp, AlertTriangle, Target, Activity,
  Users, DollarSign, Zap, Play, Eye, Settings, CheckCircle
} from "lucide-react";

interface PredictiveModel {
  id: number;
  model_name: string;
  model_description: string;
  model_type: string;
  use_case: string;
  algorithm: string;
  accuracy: number;
  is_deployed: boolean;
  prediction_count: number;
  created_at: string;
}

export default function PredictiveAnalyticsPage() {
  const [models, setModels] = useState<PredictiveModel[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedUseCase, setSelectedUseCase] = useState<string>("");
  const [predictionInput, setPredictionInput] = useState<any>({});
  const [predictionResult, setPredictionResult] = useState<any>(null);

  useEffect(() => {
    fetchModels();
  }, []);

  const fetchModels = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/analytics/models?page=1&page_size=20`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const result = await response.json();
        setModels(result.data.items || []);
      }
    } catch (error) {
      console.error("Error fetching models:", error);
    } finally {
      setLoading(false);
    }
  };

  const makePrediction = async (modelId: number) => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/analytics/predict`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            model_id: modelId,
            entity_type: "customer",
            entity_id: "CUST001",
            input_features: {
              credit_score: 750,
              income: 50000,
              existing_loans: 2,
              payment_history: "good"
            }
          }),
        }
      );

      if (response.ok) {
        const result = await response.json();
        setPredictionResult(result.data);
      }
    } catch (error) {
      console.error("Error making prediction:", error);
    }
  };

  const useCases = [
    {
      value: "credit_risk",
      label: "Credit Risk Scoring",
      description: "Predict credit risk for loan applications",
      icon: Target,
      color: "blue",
      accuracy: 87.5
    },
    {
      value: "churn",
      label: "Customer Churn",
      description: "Predict customer churn probability",
      icon: Users,
      color: "purple",
      accuracy: 92.3
    },
    {
      value: "default",
      label: "Default Prediction",
      description: "Predict loan default probability",
      icon: AlertTriangle,
      color: "red",
      accuracy: 85.8
    },
    {
      value: "fraud",
      label: "Fraud Detection",
      description: "Detect fraudulent transactions",
      icon: Activity,
      color: "orange",
      accuracy: 94.1
    },
    {
      value: "ltv",
      label: "Customer Lifetime Value",
      description: "Predict customer lifetime value",
      icon: DollarSign,
      color: "green",
      accuracy: 89.2
    }
  ];

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <Link href="/reports" className="text-blue-600 hover:text-blue-700 text-sm mb-2 inline-block">
          ← Back to Reports
        </Link>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Predictive Analytics
        </h1>
        <p className="text-gray-600">
          AI-powered predictions for credit risk, churn, fraud, and more using machine learning models
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Models</p>
              <p className="text-2xl font-bold text-gray-900">8</p>
            </div>
            <Brain className="h-10 w-10 text-blue-500" />
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Predictions Made</p>
              <p className="text-2xl font-bold text-gray-900">12,847</p>
            </div>
            <Activity className="h-10 w-10 text-green-500" />
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg Accuracy</p>
              <p className="text-2xl font-bold text-gray-900">89.8%</p>
            </div>
            <Target className="h-10 w-10 text-purple-500" />
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Models Training</p>
              <p className="text-2xl font-bold text-gray-900">2</p>
            </div>
            <Zap className="h-10 w-10 text-orange-500" />
          </div>
        </div>
      </div>

      {/* Use Cases */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Analytics Use Cases</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {useCases.map((useCase) => {
            const Icon = useCase.icon;
            return (
              <div
                key={useCase.value}
                className="bg-white rounded-lg shadow border border-gray-200 hover:shadow-lg transition-shadow p-6"
              >
                <div className={`w-12 h-12 rounded-lg bg-${useCase.color}-100 flex items-center justify-center mb-4`}>
                  <Icon className={`h-6 w-6 text-${useCase.color}-600`} />
                </div>
                
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {useCase.label}
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  {useCase.description}
                </p>
                
                <div className="flex items-center justify-between mb-4">
                  <span className="text-sm text-gray-600">Accuracy</span>
                  <span className="text-sm font-semibold text-gray-900">{useCase.accuracy}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
                  <div
                    className={`bg-${useCase.color}-500 h-2 rounded-full`}
                    style={{ width: `${useCase.accuracy}%` }}
                  />
                </div>

                <button
                  onClick={() => setSelectedUseCase(useCase.value)}
                  className={`w-full flex items-center justify-center gap-2 px-4 py-2 bg-${useCase.color}-600 text-white rounded-lg hover:bg-${useCase.color}-700 transition-colors`}
                >
                  <Play className="h-4 w-4" />
                  <span className="text-sm font-medium">Try Model</span>
                </button>
              </div>
            );
          })}
        </div>
      </div>

      {/* Deployed Models */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Deployed Models</h2>
        
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading models...</p>
          </div>
        ) : models.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <Brain className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No models deployed</h3>
            <p className="text-gray-600">Train and deploy your first ML model to start making predictions</p>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow border border-gray-200 overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Model</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Use Case</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Algorithm</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Accuracy</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Predictions</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {models.map((model) => (
                  <tr key={model.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <Brain className="h-5 w-5 text-blue-500 mr-2" />
                        <div>
                          <div className="text-sm font-medium text-gray-900">{model.model_name}</div>
                          <div className="text-xs text-gray-500">{model.algorithm}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-gray-900">{model.use_case}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-gray-900">{model.model_type}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm font-semibold text-gray-900">
                        {model.accuracy ? `${(model.accuracy * 100).toFixed(1)}%` : "N/A"}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-gray-900">{model.prediction_count.toLocaleString()}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {model.is_deployed ? (
                        <span className="flex items-center gap-1 text-xs font-medium px-2 py-1 rounded-full bg-green-100 text-green-700">
                          <CheckCircle className="h-3 w-3" />
                          Deployed
                        </span>
                      ) : (
                        <span className="text-xs font-medium px-2 py-1 rounded-full bg-gray-100 text-gray-700">
                          Training
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex gap-2">
                        <button
                          onClick={() => makePrediction(model.id)}
                          className="text-blue-600 hover:text-blue-700"
                          title="Make Prediction"
                        >
                          <Play className="h-4 w-4" />
                        </button>
                        <button className="text-gray-600 hover:text-gray-700" title="View Details">
                          <Eye className="h-4 w-4" />
                        </button>
                        <button className="text-gray-600 hover:text-gray-700" title="Configure">
                          <Settings className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Recent Predictions */}
      {predictionResult && (
        <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Latest Prediction Result</h3>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-sm text-gray-600">Predicted Class</p>
                <p className="text-lg font-semibold text-gray-900">{predictionResult.predicted_class}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Confidence</p>
                <p className="text-lg font-semibold text-gray-900">
                  {(predictionResult.probability * 100).toFixed(1)}%
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Prediction Time</p>
                <p className="text-lg font-semibold text-gray-900">{predictionResult.prediction_time_ms}ms</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Entity</p>
                <p className="text-lg font-semibold text-gray-900">{predictionResult.entity_id}</p>
              </div>
            </div>
            {predictionResult.explanation && (
              <div className="mt-4">
                <p className="text-sm text-gray-600 mb-1">Explanation</p>
                <p className="text-sm text-gray-900">{predictionResult.explanation}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
