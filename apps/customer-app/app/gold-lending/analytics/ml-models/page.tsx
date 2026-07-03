'use client';

import React, { useState, useEffect } from 'react';
import { analyticsAPI, MLModel, Prediction } from '../../phase14_analytics_api';

export default function MLModelsPage() {
  const [models, setModels] = useState<MLModel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterType, setFilterType] = useState<string>('');
  const [filterDeployment, setFilterDeployment] = useState<string>('');
  const [selectedModel, setSelectedModel] = useState<MLModel | null>(null);
  const [predictions, setPredictions] = useState<Prediction[]>([]);

  useEffect(() => {
    loadModels();
  }, [filterType, filterDeployment]);

  const loadModels = async () => {
    try {
      setLoading(true);
      const data = await analyticsAPI.listMLModels({
        model_type: filterType || undefined,
        deployment_status: filterDeployment || undefined,
      });
      setModels(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load ML models');
    } finally {
      setLoading(false);
    }
  };

  const handleDeploy = async (id: string) => {
    try {
      await analyticsAPI.deployMLModel(id);
      await loadModels();
      alert('Model deployed successfully!');
    } catch (err) {
      alert('Failed to deploy model: ' + (err instanceof Error ? err.message : 'Unknown error'));
    }
  };

  const loadModelPredictions = async (modelId: string) => {
    try {
      const data = await analyticsAPI.listModelPredictions(modelId, { limit: 10 });
      setPredictions(data);
    } catch (err) {
      console.error('Failed to load predictions:', err);
    }
  };

  const handleViewModel = async (model: MLModel) => {
    setSelectedModel(model);
    await loadModelPredictions(model.id);
  };

  const getDeploymentStatusColor = (status: string) => {
    switch (status) {
      case 'DEPLOYED': return 'text-green-600 bg-green-100';
      case 'TRAINED': return 'text-blue-600 bg-blue-100';
      case 'TRAINING': return 'text-yellow-600 bg-yellow-100';
      case 'ARCHIVED': return 'text-gray-600 bg-gray-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ACTIVE': return 'text-green-600 bg-green-100';
      case 'INACTIVE': return 'text-gray-600 bg-gray-100';
      case 'ERROR': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  if (loading && models.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading ML models...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">ML Models</h1>
          <p className="text-gray-600 mt-1">Machine learning model registry and deployment</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Register Model
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Model Type</label>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Types</option>
              <option value="REGRESSION">Regression</option>
              <option value="CLASSIFICATION">Classification</option>
              <option value="CLUSTERING">Clustering</option>
              <option value="FORECASTING">Forecasting</option>
              <option value="NLP">NLP</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Deployment Status</label>
            <select
              value={filterDeployment}
              onChange={(e) => setFilterDeployment(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Status</option>
              <option value="DEPLOYED">Deployed</option>
              <option value="TRAINED">Trained</option>
              <option value="TRAINING">Training</option>
              <option value="ARCHIVED">Archived</option>
            </select>
          </div>

          <div className="flex items-end">
            <button
              onClick={loadModels}
              className="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
            >
              Apply Filters
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-600">{error}</p>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
          <p className="text-sm text-gray-600">Total Models</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{models.length}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
          <p className="text-sm text-gray-600">Deployed</p>
          <p className="text-2xl font-bold text-green-600 mt-1">
            {models.filter(m => m.deployment_status === 'DEPLOYED').length}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
          <p className="text-sm text-gray-600">Total Predictions</p>
          <p className="text-2xl font-bold text-blue-600 mt-1">
            {models.reduce((sum, m) => sum + m.prediction_count, 0).toLocaleString()}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
          <p className="text-sm text-gray-600">Avg Accuracy</p>
          <p className="text-2xl font-bold text-purple-600 mt-1">
            {models.length > 0
              ? (models.reduce((sum, m) => sum + (m.accuracy_score || 0), 0) / models.filter(m => m.accuracy_score).length * 100).toFixed(1)
              : 0}%
          </p>
        </div>
      </div>

      {/* Models Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {models.length === 0 ? (
          <div className="col-span-full bg-white rounded-lg shadow border border-gray-200 p-12">
            <div className="flex flex-col items-center text-center">
              <svg className="w-16 h-16 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              <h3 className="text-lg font-medium text-gray-900">No ML models found</h3>
              <p className="text-sm text-gray-500 mt-2">Register your first ML model to get started</p>
            </div>
          </div>
        ) : (
          models.map((model) => (
            <div key={model.id} className="bg-white rounded-lg shadow border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow">
              <div className="h-32 bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
                <svg className="w-16 h-16 text-white opacity-80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              
              <div className="p-6">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">{model.model_name}</h3>
                    <p className="text-sm text-gray-500">{model.model_code}</p>
                  </div>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getDeploymentStatusColor(model.deployment_status)}`}>
                    {model.deployment_status}
                  </span>
                </div>

                <div className="space-y-2 mb-4">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Type:</span>
                    <span className="font-medium text-gray-900">{model.model_type}</span>
                  </div>
                  {model.algorithm && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Algorithm:</span>
                      <span className="font-medium text-gray-900 text-right text-xs">{model.algorithm}</span>
                    </div>
                  )}
                  {model.framework && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Framework:</span>
                      <span className="font-medium text-gray-900">{model.framework}</span>
                    </div>
                  )}
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Version:</span>
                    <span className="font-medium text-gray-900">{model.version}</span>
                  </div>
                </div>

                {/* Performance Metrics */}
                {model.accuracy_score && (
                  <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-3 mb-4">
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div>
                        <p className="text-gray-600">Accuracy</p>
                        <p className="font-bold text-green-700">{(model.accuracy_score * 100).toFixed(1)}%</p>
                      </div>
                      {model.f1_score && (
                        <div>
                          <p className="text-gray-600">F1 Score</p>
                          <p className="font-bold text-blue-700">{(model.f1_score * 100).toFixed(1)}%</p>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Predictions Count */}
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-2 mb-4">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-purple-800 font-medium">Predictions</span>
                    <span className="text-sm font-bold text-purple-900">{model.prediction_count.toLocaleString()}</span>
                  </div>
                </div>

                <div className="flex gap-2">
                  {model.deployment_status === 'TRAINED' && (
                    <button
                      onClick={() => handleDeploy(model.id)}
                      className="flex-1 px-3 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 flex items-center justify-center gap-2"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                      </svg>
                      Deploy
                    </button>
                  )}
                  <button
                    onClick={() => handleViewModel(model)}
                    className="flex-1 px-3 py-2 bg-gray-100 text-gray-700 text-sm rounded-lg hover:bg-gray-200"
                  >
                    Details
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Model Details Modal */}
      {selectedModel && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200 flex justify-between items-center">
              <div>
                <h2 className="text-xl font-bold text-gray-900">{selectedModel.model_name}</h2>
                <p className="text-sm text-gray-500 mt-1">{selectedModel.model_code}</p>
              </div>
              <button
                onClick={() => setSelectedModel(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Model Info */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Model Information</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-700">Type</label>
                    <p className="text-sm text-gray-900 mt-1">{selectedModel.model_type}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Algorithm</label>
                    <p className="text-sm text-gray-900 mt-1">{selectedModel.algorithm || 'N/A'}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Framework</label>
                    <p className="text-sm text-gray-900 mt-1">{selectedModel.framework || 'N/A'}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Version</label>
                    <p className="text-sm text-gray-900 mt-1">{selectedModel.version}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Deployment Status</label>
                    <p className="text-sm text-gray-900 mt-1">{selectedModel.deployment_status}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Status</label>
                    <p className="text-sm text-gray-900 mt-1">{selectedModel.status}</p>
                  </div>
                </div>
              </div>

              {/* Performance Metrics */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Performance Metrics</h3>
                <div className="grid grid-cols-4 gap-4">
                  {selectedModel.accuracy_score && (
                    <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                      <p className="text-xs text-gray-600 mb-1">Accuracy</p>
                      <p className="text-lg font-bold text-green-700">{(selectedModel.accuracy_score * 100).toFixed(2)}%</p>
                    </div>
                  )}
                  {selectedModel.precision_score && (
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                      <p className="text-xs text-gray-600 mb-1">Precision</p>
                      <p className="text-lg font-bold text-blue-700">{(selectedModel.precision_score * 100).toFixed(2)}%</p>
                    </div>
                  )}
                  {selectedModel.recall_score && (
                    <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
                      <p className="text-xs text-gray-600 mb-1">Recall</p>
                      <p className="text-lg font-bold text-purple-700">{(selectedModel.recall_score * 100).toFixed(2)}%</p>
                    </div>
                  )}
                  {selectedModel.f1_score && (
                    <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-3">
                      <p className="text-xs text-gray-600 mb-1">F1 Score</p>
                      <p className="text-lg font-bold text-indigo-700">{(selectedModel.f1_score * 100).toFixed(2)}%</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Training Info */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Training Information</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  {selectedModel.training_dataset_size && (
                    <div>
                      <span className="text-gray-600">Dataset Size:</span>
                      <span className="ml-2 font-medium text-gray-900">{selectedModel.training_dataset_size.toLocaleString()}</span>
                    </div>
                  )}
                  {selectedModel.training_duration_minutes && (
                    <div>
                      <span className="text-gray-600">Training Duration:</span>
                      <span className="ml-2 font-medium text-gray-900">{selectedModel.training_duration_minutes} min</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Usage Statistics */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Usage Statistics</h3>
                <div className="grid grid-cols-3 gap-4">
                  <div className="bg-gray-50 rounded-lg p-3">
                    <p className="text-xs text-gray-600 mb-1">Total Predictions</p>
                    <p className="text-lg font-bold text-gray-900">{selectedModel.prediction_count.toLocaleString()}</p>
                  </div>
                  {selectedModel.avg_prediction_time_ms && (
                    <div className="bg-gray-50 rounded-lg p-3">
                      <p className="text-xs text-gray-600 mb-1">Avg Prediction Time</p>
                      <p className="text-lg font-bold text-gray-900">{selectedModel.avg_prediction_time_ms}ms</p>
                    </div>
                  )}
                  {selectedModel.last_prediction_at && (
                    <div className="bg-gray-50 rounded-lg p-3">
                      <p className="text-xs text-gray-600 mb-1">Last Prediction</p>
                      <p className="text-xs font-medium text-gray-900">{new Date(selectedModel.last_prediction_at).toLocaleString()}</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Recent Predictions */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Recent Predictions ({predictions.length})</h3>
                {predictions.length === 0 ? (
                  <p className="text-sm text-gray-500">No predictions recorded yet</p>
                ) : (
                  <div className="space-y-2 max-h-60 overflow-y-auto">
                    {predictions.map((pred) => (
                      <div key={pred.id} className="border border-gray-200 rounded-lg p-3 text-sm">
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-medium text-gray-900">{pred.prediction_code}</span>
                          {pred.confidence_score && (
                            <span className="text-xs text-gray-600">
                              Confidence: {(pred.confidence_score * 100).toFixed(1)}%
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-gray-500">{new Date(pred.created_at).toLocaleString()}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
