"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Plus, Play, Edit, Trash2, Search } from "lucide-react";
import { collectionStrategyApi } from "@/lib/api/collection";
import { CollectionStrategy } from "@/types/collection";
import { StatusBadge } from "@/components/collections";

export default function CollectionStrategiesPage() {
  const [strategies, setStrategies] = useState<CollectionStrategy[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterActive, setFilterActive] = useState<boolean | undefined>(undefined);

  useEffect(() => {
    fetchStrategies();
  }, [filterActive]);

  const fetchStrategies = async () => {
    try {
      setLoading(true);
      const response = await collectionStrategyApi.list({
        is_active: filterActive,
        limit: 100
      });
      setStrategies(response.items);
    } catch (error) {
      console.error("Error fetching strategies:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleExecuteStrategies = async () => {
    if (!confirm("Execute collection strategies for all overdue accounts?")) return;
    
    try {
      await collectionStrategyApi.execute();
      alert("Strategies executed successfully!");
    } catch (error) {
      console.error("Error executing strategies:", error);
      alert("Failed to execute strategies");
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this strategy?")) return;
    
    try {
      await collectionStrategyApi.delete(id);
      fetchStrategies();
    } catch (error) {
      console.error("Error deleting strategy:", error);
      alert("Failed to delete strategy");
    }
  };

  const filteredStrategies = strategies.filter(strategy =>
    strategy.strategy_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    strategy.strategy_code.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading strategies...</div>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold text-gray-900">Collection Strategies</h2>
            <p className="mt-1 text-sm text-gray-500">
              Manage automated collection workflows based on DPD buckets
            </p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={handleExecuteStrategies}
              className="inline-flex items-center px-4 py-2 border border-orange-300 text-sm font-medium rounded-md text-orange-700 bg-white hover:bg-orange-50"
            >
              <Play className="h-4 w-4 mr-2" />
              Execute Now
            </button>
            <Link
              href="/collections/strategies/new"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-orange-600 hover:bg-orange-700"
            >
              <Plus className="h-4 w-4 mr-2" />
              New Strategy
            </Link>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="mb-6 flex items-center gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search strategies..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 w-full rounded-md border-gray-300 shadow-sm focus:border-orange-500 focus:ring-orange-500"
          />
        </div>
        <select
          value={filterActive === undefined ? "" : filterActive ? "active" : "inactive"}
          onChange={(e) => setFilterActive(e.target.value === "" ? undefined : e.target.value === "active")}
          className="rounded-md border-gray-300 shadow-sm focus:border-orange-500 focus:ring-orange-500"
        >
          <option value="">All Status</option>
          <option value="active">Active Only</option>
          <option value="inactive">Inactive Only</option>
        </select>
      </div>

      {/* Strategies Grid */}
      <div className="grid grid-cols-1 gap-6">
        {filteredStrategies.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
            <p className="text-gray-500">No strategies found</p>
            <Link
              href="/collections/strategies/new"
              className="mt-4 inline-flex items-center text-orange-600 hover:text-orange-700"
            >
              <Plus className="h-4 w-4 mr-1" />
              Create your first strategy
            </Link>
          </div>
        ) : (
          filteredStrategies.map((strategy) => (
            <div
              key={strategy.id}
              className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {strategy.strategy_name}
                    </h3>
                    <StatusBadge
                      status={strategy.is_active ? "active" : "inactive"}
                      size="sm"
                    />
                    <span className="px-2 py-0.5 text-xs font-medium rounded bg-blue-100 text-blue-800">
                      Priority {strategy.priority}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-4">
                    {strategy.description || strategy.strategy_code}
                  </p>
                  <div className="grid grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">DPD Range:</span>
                      <p className="font-medium text-gray-900">
                        {strategy.dpd_min} - {strategy.dpd_max} days
                      </p>
                    </div>
                    <div>
                      <span className="text-gray-500">Action Type:</span>
                      <p className="font-medium text-gray-900 capitalize">
                        {strategy.action_type.replace("_", " ")}
                      </p>
                    </div>
                    <div>
                      <span className="text-gray-500">Frequency:</span>
                      <p className="font-medium text-gray-900">
                        Every {strategy.frequency_days} days
                      </p>
                    </div>
                    <div>
                      <span className="text-gray-500">Max Attempts:</span>
                      <p className="font-medium text-gray-900">
                        {strategy.max_attempts}
                      </p>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2 ml-4">
                  <Link
                    href={`/collections/strategies/${strategy.id}/edit`}
                    className="p-2 text-gray-600 hover:text-orange-600 hover:bg-orange-50 rounded"
                  >
                    <Edit className="h-4 w-4" />
                  </Link>
                  <button
                    onClick={() => handleDelete(strategy.id)}
                    className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Quick Actions Info */}
      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="text-sm font-semibold text-blue-900 mb-2">Strategy Execution</h4>
        <p className="text-sm text-blue-700">
          Strategies are automatically executed daily for all overdue accounts. 
          You can also manually trigger execution using the "Execute Now" button.
        </p>
      </div>
    </div>
  );
}
