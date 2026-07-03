'use client';

import { useEffect, useState } from 'react';
import { goldApi } from '../../goldApi';

export default function MarketRiskPage() {
  const [exposures, setExposures] = useState<any[]>([]);
  const [statistics, setStatistics] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [exposureData, stats] = await Promise.all([
        goldApi.listMarketRiskExposures({ limit: 50 }),
        goldApi.getMarketRiskStatistics()
      ]);
      setExposures(exposureData);
      setStatistics(stats);
    } catch (err) {
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Market Risk Exposures</h1>
          <p className="text-gray-600 mt-1">Monitor gold price volatility and market exposures</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          Record Exposure
        </button>
      </div>

      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600">Total Exposures</div>
            <div className="text-2xl font-bold text-gray-900 mt-2">{statistics.total_exposures}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600">Total Exposure Amount</div>
            <div className="text-2xl font-bold text-gray-900 mt-2">${(statistics.total_exposure_amount || 0).toLocaleString()}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600">Total VaR</div>
            <div className="text-2xl font-bold text-gray-900 mt-2">${(statistics.total_var_amount || 0).toLocaleString()}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600">VaR %</div>
            <div className="text-2xl font-bold text-gray-900 mt-2">
              {statistics.total_exposure_amount ? ((statistics.total_var_amount / statistics.total_exposure_amount) * 100).toFixed(2) : '0'}%
            </div>
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg shadow overflow-hidden">
        {loading ? (
          <div className="p-8 text-center"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div></div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Gold Rate</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Weight (kg)</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total Value</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">VaR Amount</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Volatility</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {exposures.map((exposure) => (
                <tr key={exposure.exposure_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm">{new Date(exposure.exposure_date).toLocaleDateString()}</td>
                  <td className="px-6 py-4 text-sm font-medium">${exposure.gold_rate_per_gram?.toFixed(2)}</td>
                  <td className="px-6 py-4 text-sm">{exposure.total_gold_weight_kg?.toFixed(2)}</td>
                  <td className="px-6 py-4 text-sm font-semibold">${(exposure.total_gold_value || 0).toLocaleString()}</td>
                  <td className="px-6 py-4 text-sm text-red-600">${(exposure.var_amount || 0).toLocaleString()}</td>
                  <td className="px-6 py-4 text-sm">{(exposure.volatility_percent || 0).toFixed(2)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
