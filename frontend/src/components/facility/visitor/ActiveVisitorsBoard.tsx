"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Users, UserCheck } from "lucide-react";
import { visitorService } from "@/services/facility/visitorService";
import type { Visitor } from "@/services/facility/types";
import { useToast } from "@/components/ui/use-toast";

export default function ActiveVisitorsBoard() {
  const [activeVisitors, setActiveVisitors] = useState<Visitor[]>([]);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    loadActiveVisitors();
    const interval = setInterval(loadActiveVisitors, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadActiveVisitors = async () => {
    try {
      const visitors = await visitorService.getActiveVisitors();
      setActiveVisitors(visitors);
      setLoading(false);
    } catch (error) {
      if (!loading) {
        toast({
          title: "Error",
          description: "Failed to load active visitors",
          variant: "destructive",
        });
      }
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <UserCheck className="h-5 w-5" />
          Active Visitors
        </CardTitle>
        <CardDescription>Visitors currently on premises</CardDescription>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="text-center py-8">Loading...</div>
        ) : activeVisitors.length === 0 ? (
          <div className="text-center py-12">
            <Users className="h-12 w-12 mx-auto text-gray-400 mb-3" />
            <div className="text-lg font-semibold text-gray-600 mb-1">
              No Active Visitors
            </div>
            <div className="text-sm text-gray-500">
              No visitors are currently on premises
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            {activeVisitors.map((visitor) => (
              <Card key={visitor.id} className="bg-green-50">
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <div className="font-bold text-lg">{visitor.visitor_name}</div>
                        <Badge className="bg-green-500 text-white">ACTIVE</Badge>
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div>
                          <span className="text-gray-500">Company:</span>{" "}
                          {visitor.company_name || "N/A"}
                        </div>
                        <div>
                          <span className="text-gray-500">Type:</span>{" "}
                          {visitor.visitor_type}
                        </div>
                        <div>
                          <span className="text-gray-500">Host:</span>{" "}
                          {visitor.host_employee_name}
                        </div>
                        <div>
                          <span className="text-gray-500">Check-in:</span>{" "}
                          {visitor.check_in_time}
                        </div>
                      </div>
                      {visitor.badge_number && (
                        <div className="mt-2 text-xs text-gray-600">
                          Badge: {visitor.badge_number}
                        </div>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
        <div className="mt-4 text-center text-sm text-gray-500">
          Total Active: {activeVisitors.length}
        </div>
      </CardContent>
    </Card>
  );
}
