"use client";

import { useState, useEffect } from "react";
import { 
  AlertCircle, 
  Phone,
  MessageSquare,
  CheckCircle,
  Clock
} from "lucide-react";

interface QueueItem {
  id: number;
  account_number: string;
  customer_name: string;
  customer_mobile: string;
  overdue_amount: number;
  dpd: number;
  priority: "high" | "medium" | "low";
  last_contact_date?: string;
  next_follow_up_date?: string;
  notes?: string;
  assigned_to?: string;
}

const priorityConfig = {
  high: {
    label: "High Priority",
    color: "bg-red-100 text-red-800 border-red-300",
    icon: AlertCircle,
    description: "DPD > 60 days",
  },
  medium: {
    label: "Medium Priority",
    color: "bg-orange-100 text-orange-800 border-orange-300",
    icon: Clock,
    description: "DPD 30-60 days",
  },
  low: {
    label: "Low Priority",
    color: "bg-yellow-100 text-yellow-800 border-yellow-300",
    icon: CheckCircle,
    description: "DPD < 30 days",
  },
};

export default function CollectionQueuePage() {
  const [queueItems, setQueueItems] = useState<QueueItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPriority, setSelectedPriority] = useState<"all" | "high" | "medium" | "low">("all");
  const [selectedItem, setSelectedItem] = useState<QueueItem | null>(null);

  useEffect(() => {
    fetchQueue();
  }, []);

  const fetchQueue = async () => {
    try {
      setLoading(true);
      // TODO: Replace with actual API call
      const mockData: QueueItem[] = [
        {
          id: 1,
          account_number: "LA-202512-0045",
          customer_name: "Rajesh Kumar",
          customer_mobile: "+91 98765 43210",
          overdue_amount: 130000,
          dpd: 95,
          priority: "high",
          last_contact_date: "2026-01-03",
          next_follow_up_date: "2026-01-06",
          notes: "Promised payment by 10th Jan",
          assigned_to: "Agent 1",
        },
        {
          id: 2,
          account_number: "LA-202510-0234",
          customer_name: "Amit Patel",
          customer_mobile: "+91 98765 43212",
          overdue_amount: 93700,
          dpd: 112,
          priority: "high",
          last_contact_date: "2026-01-02",
          next_follow_up_date: "2026-01-05",
          notes: "Customer unavailable, try evening",
          assigned_to: "Agent 2",
        },
        {
          id: 3,
          account_number: "LA-202511-0123",
          customer_name: "Priya Sharma",
          customer_mobile: "+91 98765 43211",
          overdue_amount: 101500,
          dpd: 87,
          priority: "high",
          last_contact_date: "2026-01-04",
          next_follow_up_date: "2026-01-07",
          assigned_to: "Agent 1",
        },
        {
          id: 4,
          account_number: "LA-202512-0089",
          customer_name: "Sneha Reddy",
          customer_mobile: "+91 98765 43213",
          overdue_amount: 77800,
          dpd: 68,
          priority: "high",
          last_contact_date: "2026-01-03",
          next_follow_up_date: "2026-01-06",
          assigned_to: "Agent 3",
        },
        {
          id: 5,
          account_number: "LA-202512-0156",
          customer_name: "Karthik Iyer",
          customer_mobile: "+91 98765 43215",
          overdue_amount: 55000,
          dpd: 45,
          priority: "medium",
          last_contact_date: "2026-01-04",
          next_follow_up_date: "2026-01-08",
          assigned_to: "Agent 2",
        },
        {
          id: 6,
          account_number: "LA-202601-0012",
          customer_name: "Vikram Singh",
          customer_mobile: "+91 98765 43214",
          overdue_amount: 25500,
          dpd: 22,
          priority: "low",
          last_contact_date: "2026-01-05",
          next_follow_up_date: "2026-01-10",
          assigned_to: "Agent 3",
        },
      ];
      setQueueItems(mockData);
    } catch (error) {
      console.error("Error fetching collection queue:", error);
    } finally {
      setLoading(false);
    }
  };

  const filteredItems = selectedPriority === "all" 
    ? queueItems 
    : queueItems.filter(item => item.priority === selectedPriority);

  const getItemsByPriority = (priority: "high" | "medium" | "low") => {
    return queueItems.filter(item => item.priority === priority);
  };

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900">Collection Queue</h2>
        <p className="mt-1 text-sm text-gray-500">
          Priority-based follow-up queue for collection activities
        </p>
      </div>

      {/* Priority Tabs */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setSelectedPriority("all")}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                selectedPriority === "all"
                  ? "border-blue-500 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              All ({queueItems.length})
            </button>
            <button
              onClick={() => setSelectedPriority("high")}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                selectedPriority === "high"
                  ? "border-red-500 text-red-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              High Priority ({getItemsByPriority("high").length})
            </button>
            <button
              onClick={() => setSelectedPriority("medium")}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                selectedPriority === "medium"
                  ? "border-orange-500 text-orange-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              Medium Priority ({getItemsByPriority("medium").length})
            </button>
            <button
              onClick={() => setSelectedPriority("low")}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                selectedPriority === "low"
                  ? "border-yellow-500 text-yellow-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              Low Priority ({getItemsByPriority("low").length})
            </button>
          </nav>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        {Object.entries(priorityConfig).map(([key, config]) => {
          const Icon = config.icon;
          const items = getItemsByPriority(key as any);
          const totalAmount = items.reduce((sum, item) => sum + item.overdue_amount, 0);
          
          return (
            <div
              key={key}
              className={`rounded-lg border-2 p-6 ${config.color}`}
            >
              <div className="flex items-center justify-between mb-4">
                <Icon className="h-8 w-8" />
                <span className="text-2xl font-bold">{items.length}</span>
              </div>
              <h3 className="text-lg font-semibold mb-1">{config.label}</h3>
              <p className="text-sm mb-2">{config.description}</p>
              <p className="text-xl font-bold">
                ₹{totalAmount.toLocaleString("en-IN", { maximumFractionDigits: 0 })}
              </p>
            </div>
          );
        })}
      </div>

      {/* Queue Items */}
      <div className="space-y-4">
        {loading ? (
          <div className="flex items-center justify-center h-64 bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500">Loading collection queue...</div>
          </div>
        ) : filteredItems.length === 0 ? (
          <div className="flex items-center justify-center h-64 bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500">No items in queue</div>
          </div>
        ) : (
          filteredItems.map((item) => {
            const config = priorityConfig[item.priority];
            const Icon = config.icon;
            
            return (
              <div
                key={item.id}
                className={`bg-white rounded-lg shadow-sm border-2 ${config.color} p-6`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center mb-2">
                      <Icon className="h-5 w-5 mr-2" />
                      <h3 className="text-lg font-semibold text-gray-900">
                        {item.customer_name}
                      </h3>
                      <span className={`ml-3 px-3 py-1 text-xs font-medium rounded-full ${config.color} border`}>
                        {item.dpd} DPD
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                      <div>
                        <p className="text-sm text-gray-600">Account Number</p>
                        <p className="text-sm font-medium text-blue-600">{item.account_number}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Mobile</p>
                        <p className="text-sm font-medium text-gray-900">{item.customer_mobile}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Overdue Amount</p>
                        <p className="text-sm font-bold text-red-600">
                          ₹{item.overdue_amount.toLocaleString("en-IN")}
                        </p>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                      {item.last_contact_date && (
                        <div>
                          <p className="text-sm text-gray-600">Last Contact</p>
                          <p className="text-sm text-gray-900">
                            {new Date(item.last_contact_date).toLocaleDateString("en-IN", {
                              month: "short",
                              day: "numeric",
                            })}
                          </p>
                        </div>
                      )}
                      {item.next_follow_up_date && (
                        <div>
                          <p className="text-sm text-gray-600">Next Follow-up</p>
                          <p className="text-sm font-medium text-orange-600">
                            {new Date(item.next_follow_up_date).toLocaleDateString("en-IN", {
                              month: "short",
                              day: "numeric",
                            })}
                          </p>
                        </div>
                      )}
                      {item.assigned_to && (
                        <div>
                          <p className="text-sm text-gray-600">Assigned To</p>
                          <p className="text-sm text-gray-900">{item.assigned_to}</p>
                        </div>
                      )}
                    </div>

                    {item.notes && (
                      <div className="bg-gray-50 rounded-lg p-3 mb-4">
                        <p className="text-sm text-gray-600 mb-1">Notes</p>
                        <p className="text-sm text-gray-900">{item.notes}</p>
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex items-center justify-end space-x-3 mt-4 pt-4 border-t border-gray-200">
                  <button className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm">
                    <Phone className="h-4 w-4 mr-2" />
                    Call Customer
                  </button>
                  <button className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm">
                    <MessageSquare className="h-4 w-4 mr-2" />
                    Send SMS
                  </button>
                  <button className="flex items-center px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 text-sm">
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Record Payment
                  </button>
                  <button className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 text-sm">
                    Update Notes
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
