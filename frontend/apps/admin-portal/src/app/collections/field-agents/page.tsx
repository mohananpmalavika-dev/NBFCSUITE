"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Plus, MapPin, Target, TrendingUp, Phone, Mail } from "lucide-react";
import { fieldAgentApi } from "@/lib/api/collection";
import { FieldAgent } from "@/types/collection";
import { StatusBadge } from "@/components/collections";

export default function FieldAgentsPage() {
  const [agents, setAgents] = useState<FieldAgent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      setLoading(true);
      const response = await fieldAgentApi.listAgents({ limit: 100 });
      setAgents(response.items);
    } catch (error) {
      console.error("Error fetching agents:", error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading field agents...</div>
      </div>
    );
  }

  const activeAgents = agents.filter(a => a.is_active);
  const totalCollectionTarget = activeAgents.reduce((sum, a) => sum + a.monthly_collection_target, 0);
  const totalCollectionAchieved = activeAgents.reduce((sum, a) => sum + a.total_collection_amount, 0);

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold text-gray-900">Field Agents</h2>
            <p className="mt-1 text-sm text-gray-500">
              Manage field collection team and track performance
            </p>
          </div>
          <div className="flex gap-3">
            <Link
              href="/collections/field-agents/territories"
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              <MapPin className="h-4 w-4 mr-2" />
              Territories
            </Link>
            <Link
              href="/collections/field-agents/new"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-orange-600 hover:bg-orange-700"
            >
              <Plus className="h-4 w-4 mr-2" />
              New Agent
            </Link>
          </div>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-2 rounded-full bg-blue-100">
              <Target className="h-5 w-5 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Agents</p>
              <p className="text-2xl font-bold text-gray-900">{activeAgents.length}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-2 rounded-full bg-green-100">
              <TrendingUp className="h-5 w-5 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Collection Target</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(totalCollectionTarget)}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-2 rounded-full bg-orange-100">
              <TrendingUp className="h-5 w-5 text-orange-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Collected</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(totalCollectionAchieved)}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-2 rounded-full bg-purple-100">
              <Target className="h-5 w-5 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Achievement</p>
              <p className="text-2xl font-bold text-gray-900">
                {totalCollectionTarget > 0 
                  ? ((totalCollectionAchieved / totalCollectionTarget) * 100).toFixed(1)
                  : 0}%
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Agents List */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">All Field Agents</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Agent
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Contact
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  Collection Target
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  Collected
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                  Achievement
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                  Visits
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                  Status
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {agents.map((agent) => (
                <tr key={agent.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {agent.full_name}
                      </div>
                      <div className="text-xs text-gray-500">
                        {agent.agent_code}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900 flex items-center">
                      <Phone className="h-3 w-3 mr-1" />
                      {agent.mobile}
                    </div>
                    {agent.email && (
                      <div className="text-xs text-gray-500 flex items-center mt-1">
                        <Mail className="h-3 w-3 mr-1" />
                        {agent.email}
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <div className="text-sm font-medium text-gray-900">
                      {formatCurrency(agent.monthly_collection_target)}
                    </div>
                    <div className="text-xs text-gray-500">
                      {agent.monthly_visit_target} visits
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <div className="text-sm font-semibold text-green-600">
                      {formatCurrency(agent.total_collection_amount)}
                    </div>
                    <div className="text-xs text-gray-500">
                      {agent.total_visits_completed} visits
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-center">
                    <div className="flex flex-col items-center">
                      <span className={`text-sm font-semibold ${
                        agent.success_rate >= 80 ? 'text-green-600' :
                        agent.success_rate >= 60 ? 'text-yellow-600' : 'text-red-600'
                      }`}>
                        {agent.success_rate.toFixed(1)}%
                      </span>
                      <div className="w-16 bg-gray-200 rounded-full h-1.5 mt-1">
                        <div
                          className={`h-1.5 rounded-full ${
                            agent.success_rate >= 80 ? 'bg-green-500' :
                            agent.success_rate >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                          }`}
                          style={{ width: `${agent.success_rate}%` }}
                        />
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-center">
                    <span className="text-sm text-gray-900">
                      {agent.total_visits_completed}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-center">
                    <StatusBadge
                      status={agent.is_active ? "active" : "inactive"}
                      size="sm"
                    />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                    <Link
                      href={`/collections/field-agents/${agent.id}`}
                      className="text-orange-600 hover:text-orange-900 font-medium"
                    >
                      View Details
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
