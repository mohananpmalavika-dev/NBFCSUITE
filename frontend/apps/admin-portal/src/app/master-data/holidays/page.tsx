"use client";

import { useState, useEffect } from "react";
import { Calendar, Building2 } from "lucide-react";

interface Holiday {
  id: number;
  name: string;
  date: string;
  type: string;
  state_name?: string;
  is_national: boolean;
  is_active: boolean;
}

interface FinancialYear {
  id: number;
  name: string;
  start_date: string;
  end_date: string;
  is_current: boolean;
  is_active: boolean;
}

export default function HolidaysPage() {
  const [activeTab, setActiveTab] = useState<'holidays' | 'financial-years'>('holidays');
  const [holidays, setHolidays] = useState<Holiday[]>([]);
  const [financialYears, setFinancialYears] = useState<FinancialYear[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      // Fetch holidays (would need endpoint)
      // const holidaysRes = await fetch('/api/v1/masterdata/holidays');
      // const holidaysData = await holidaysRes.json();
      // setHolidays(holidaysData.items || []);

      // Fetch financial years (would need endpoint)
      // const fyRes = await fetch('/api/v1/masterdata/financial-years');
      // const fyData = await fyRes.json();
      // setFinancialYears(fyData.items || []);

      // Mock data for now
      setHolidays([
        { id: 1, name: "Republic Day", date: "2026-01-26", type: "National", is_national: true, is_active: true },
        { id: 2, name: "Holi", date: "2026-03-14", type: "National", is_national: true, is_active: true },
        { id: 3, name: "Good Friday", date: "2026-04-03", type: "National", is_national: true, is_active: true },
      ]);

      setFinancialYears([
        { id: 1, name: "FY 2023-24", start_date: "2023-04-01", end_date: "2024-03-31", is_current: false, is_active: true },
        { id: 2, name: "FY 2024-25", start_date: "2024-04-01", end_date: "2025-03-31", is_current: false, is_active: true },
        { id: 3, name: "FY 2025-26", start_date: "2025-04-01", end_date: "2026-03-31", is_current: true, is_active: true },
        { id: 4, name: "FY 2026-27", start_date: "2026-04-01", end_date: "2027-03-31", is_current: false, is_active: true },
      ]);
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-violet-600 to-violet-700 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
              <Calendar className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">Holidays & Financial Years</h1>
              <p className="text-sm text-violet-100">
                Manage business calendar and financial year configuration
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex gap-8">
            <button
              onClick={() => setActiveTab('holidays')}
              className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'holidays'
                  ? 'border-violet-600 text-violet-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Holidays (2026)
            </button>
            <button
              onClick={() => setActiveTab('financial-years')}
              className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'financial-years'
                  ? 'border-violet-600 text-violet-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Financial Years
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'holidays' ? (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            {/* Holidays Header */}
            <div className="px-6 py-4 border-b flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">Bank Holidays 2026</h2>
                <p className="text-sm text-gray-600 mt-1">National and state-specific holidays</p>
              </div>
              <button className="px-4 py-2 bg-violet-600 text-white rounded-lg hover:bg-violet-700 text-sm font-medium">
                Add Holiday
              </button>
            </div>

            {/* Holidays List */}
            <div className="divide-y">
              {loading ? (
                <div className="flex items-center justify-center py-12">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-violet-600"></div>
                </div>
              ) : holidays.length === 0 ? (
                <div className="text-center py-12">
                  <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">No holidays configured</p>
                </div>
              ) : (
                holidays.map((holiday) => (
                  <div key={holiday.id} className="px-6 py-4 hover:bg-gray-50 transition-colors">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className="w-16 text-center">
                          <div className="text-2xl font-bold text-violet-600">
                            {new Date(holiday.date).getDate()}
                          </div>
                          <div className="text-xs text-gray-500 uppercase">
                            {new Date(holiday.date).toLocaleDateString('en-IN', { month: 'short' })}
                          </div>
                        </div>
                        <div>
                          <h3 className="font-medium text-gray-900">{holiday.name}</h3>
                          <div className="flex items-center gap-2 mt-1">
                            <span className="text-sm text-gray-600">{formatDate(holiday.date)}</span>
                            <span className="text-gray-300">•</span>
                            <span className={`text-xs px-2 py-0.5 rounded ${
                              holiday.is_national 
                                ? 'bg-red-100 text-red-700' 
                                : 'bg-blue-100 text-blue-700'
                            }`}>
                              {holiday.is_national ? 'National' : holiday.state_name || 'State'}
                            </span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <button className="text-blue-600 hover:text-blue-800 text-sm">Edit</button>
                        <button className="text-red-600 hover:text-red-800 text-sm">Delete</button>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            {/* Financial Years Header */}
            <div className="px-6 py-4 border-b flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">Financial Years</h2>
                <p className="text-sm text-gray-600 mt-1">Configure accounting periods</p>
              </div>
              <button className="px-4 py-2 bg-violet-600 text-white rounded-lg hover:bg-violet-700 text-sm font-medium">
                Add Financial Year
              </button>
            </div>

            {/* Financial Years Grid */}
            <div className="p-6">
              {loading ? (
                <div className="flex items-center justify-center py-12">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-violet-600"></div>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {financialYears.map((fy) => (
                    <div
                      key={fy.id}
                      className={`p-6 rounded-lg border-2 transition-all ${
                        fy.is_current
                          ? 'border-violet-500 bg-violet-50'
                          : 'border-gray-200 bg-white hover:border-gray-300'
                      }`}
                    >
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                            {fy.name}
                            {fy.is_current && (
                              <span className="text-xs bg-violet-600 text-white px-2 py-0.5 rounded">
                                Current
                              </span>
                            )}
                          </h3>
                        </div>
                        <Building2 className={`w-5 h-5 ${fy.is_current ? 'text-violet-600' : 'text-gray-400'}`} />
                      </div>

                      <div className="space-y-3">
                        <div>
                          <p className="text-xs text-gray-500 uppercase tracking-wide">Start Date</p>
                          <p className="text-sm font-medium text-gray-900 mt-1">{formatDate(fy.start_date)}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500 uppercase tracking-wide">End Date</p>
                          <p className="text-sm font-medium text-gray-900 mt-1">{formatDate(fy.end_date)}</p>
                        </div>
                        <div className="pt-3 border-t flex gap-2">
                          <button className="flex-1 px-3 py-1.5 text-sm text-blue-600 border border-blue-600 rounded hover:bg-blue-50">
                            Edit
                          </button>
                          <button className="flex-1 px-3 py-1.5 text-sm text-red-600 border border-red-600 rounded hover:bg-red-50">
                            Delete
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
