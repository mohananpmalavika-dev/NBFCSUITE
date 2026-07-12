"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Plus, Users, Search, LogIn, LogOut } from "lucide-react";
import { visitorService } from "@/services/facility/visitorService";
import type { Visitor } from "@/services/facility/types";
import { useToast } from "@/components/ui/use-toast";
import VisitorForm from "./VisitorForm";

export default function VisitorList() {
  const [visitors, setVisitors] = useState<Visitor[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const { toast } = useToast();

  useEffect(() => {
    loadVisitors();
  }, []);

  const loadVisitors = async () => {
    try {
      setLoading(true);
      const params: any = { limit: 100 };
      if (filterStatus !== "all") params.status = filterStatus;
      if (searchTerm) params.search = searchTerm;

      const response = await visitorService.getVisitors(params);
      setVisitors(response.items);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load visitors",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      loadVisitors();
    }, 300);
    return () => clearTimeout(timer);
  }, [searchTerm, filterStatus]);

  const handleCheckIn = async (id: number) => {
    try {
      await visitorService.checkInVisitor(id);
      toast({
        title: "Success",
        description: "Visitor checked in successfully",
      });
      loadVisitors();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.message || "Failed to check in visitor",
        variant: "destructive",
      });
    }
  };

  const handleCheckOut = async (id: number) => {
    try {
      await visitorService.checkOutVisitor(id);
      toast({
        title: "Success",
        description: "Visitor checked out successfully",
      });
      loadVisitors();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.message || "Failed to check out visitor",
        variant: "destructive",
      });
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      scheduled: "bg-blue-500",
      checked_in: "bg-green-500",
      in_meeting: "bg-purple-500",
      checked_out: "bg-gray-500",
      cancelled: "bg-red-500",
    };
    return colors[status] || "bg-gray-500";
  };

  return (
    <>
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                Visitor Registry
              </CardTitle>
              <CardDescription>Manage visitor registrations and check-ins</CardDescription>
            </div>
            <Button onClick={() => setShowForm(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Register Visitor
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {/* Filters */}
          <div className="flex gap-4 mb-6">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search visitors..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select value={filterStatus} onValueChange={setFilterStatus}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="scheduled">Scheduled</SelectItem>
                <SelectItem value="checked_in">Checked In</SelectItem>
                <SelectItem value="in_meeting">In Meeting</SelectItem>
                <SelectItem value="checked_out">Checked Out</SelectItem>
                <SelectItem value="cancelled">Cancelled</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Visitors Table */}
          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : visitors.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No visitors found.
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Pass Number</TableHead>
                  <TableHead>Visitor Name</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Company</TableHead>
                  <TableHead>Purpose</TableHead>
                  <TableHead>Host</TableHead>
                  <TableHead>Visit Date</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {visitors.map((visitor) => (
                  <TableRow key={visitor.id}>
                    <TableCell className="font-medium">
                      {visitor.visitor_pass_number}
                    </TableCell>
                    <TableCell>{visitor.visitor_name}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{visitor.visitor_type}</Badge>
                    </TableCell>
                    <TableCell>{visitor.company_name || "-"}</TableCell>
                    <TableCell>{visitor.purpose}</TableCell>
                    <TableCell>
                      <div>{visitor.host_employee_name}</div>
                      <div className="text-xs text-gray-500">
                        ID: {visitor.host_employee_id}
                      </div>
                    </TableCell>
                    <TableCell>
                      {new Date(visitor.visit_date).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <Badge
                        className={`${getStatusColor(visitor.status)} text-white`}
                      >
                        {visitor.status.replace("_", " ").toUpperCase()}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        {visitor.status === "scheduled" && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleCheckIn(visitor.id)}
                          >
                            <LogIn className="h-4 w-4 mr-1" />
                            Check In
                          </Button>
                        )}
                        {(visitor.status === "checked_in" ||
                          visitor.status === "in_meeting") && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleCheckOut(visitor.id)}
                          >
                            <LogOut className="h-4 w-4 mr-1" />
                            Check Out
                          </Button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {showForm && (
        <VisitorForm
          onClose={() => setShowForm(false)}
          onSuccess={() => {
            setShowForm(false);
            loadVisitors();
          }}
        />
      )}
    </>
  );
}
