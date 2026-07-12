"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { History, Calendar } from "lucide-react";
import { visitorService } from "@/services/facility/visitorService";
import type { Visitor } from "@/services/facility/types";
import { useToast } from "@/components/ui/use-toast";

export default function VisitorHistory() {
  const [visitors, setVisitors] = useState<Visitor[]>([]);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState({
    from: "",
    to: "",
  });
  const { toast } = useToast();

  useEffect(() => {
    loadVisitorHistory();
  }, [dateRange]);

  const loadVisitorHistory = async () => {
    try {
      setLoading(true);
      const params: any = { limit: 100, status: "checked_out" };
      if (dateRange.from) params.from_date = dateRange.from;
      if (dateRange.to) params.to_date = dateRange.to;

      const response = await visitorService.getVisitors(params);
      setVisitors(response.items);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load visitor history",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <History className="h-5 w-5" />
          Visitor History
        </CardTitle>
        <CardDescription>Past visitor records</CardDescription>
      </CardHeader>
      <CardContent>
        {/* Date Range Filter */}
        <div className="flex gap-2 items-center mb-6">
          <Calendar className="h-4 w-4 text-gray-400" />
          <Input
            type="date"
            value={dateRange.from}
            onChange={(e) =>
              setDateRange({ ...dateRange, from: e.target.value })
            }
            className="w-40"
            placeholder="From"
          />
          <span className="text-gray-400">to</span>
          <Input
            type="date"
            value={dateRange.to}
            onChange={(e) =>
              setDateRange({ ...dateRange, to: e.target.value })
            }
            className="w-40"
            placeholder="To"
          />
        </div>

        {/* History Table */}
        {loading ? (
          <div className="text-center py-8">Loading...</div>
        ) : visitors.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No visitor records found for the selected date range.
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Pass Number</TableHead>
                <TableHead>Visitor Name</TableHead>
                <TableHead>Company</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Visit Date</TableHead>
                <TableHead>Check In</TableHead>
                <TableHead>Check Out</TableHead>
                <TableHead>Duration</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {visitors.map((visitor) => {
                const duration =
                  visitor.check_in_time && visitor.check_out_time
                    ? calculateDuration(visitor.check_in_time, visitor.check_out_time)
                    : "-";

                return (
                  <TableRow key={visitor.id}>
                    <TableCell className="font-medium">
                      {visitor.visitor_pass_number}
                    </TableCell>
                    <TableCell>{visitor.visitor_name}</TableCell>
                    <TableCell>{visitor.company_name || "-"}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{visitor.visitor_type}</Badge>
                    </TableCell>
                    <TableCell>
                      {new Date(visitor.visit_date).toLocaleDateString()}
                    </TableCell>
                    <TableCell>{visitor.check_in_time || "-"}</TableCell>
                    <TableCell>{visitor.check_out_time || "-"}</TableCell>
                    <TableCell>{duration}</TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}

function calculateDuration(checkIn: string, checkOut: string): string {
  const inTime = new Date(`1970-01-01T${checkIn}`);
  const outTime = new Date(`1970-01-01T${checkOut}`);
  const diffMs = outTime.getTime() - inTime.getTime();
  const hours = Math.floor(diffMs / 3600000);
  const minutes = Math.floor((diffMs % 3600000) / 60000);
  return `${hours}h ${minutes}m`;
}
