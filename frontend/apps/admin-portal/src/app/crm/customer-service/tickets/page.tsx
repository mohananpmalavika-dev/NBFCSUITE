"use client";

import { useState, useEffect } from "react";
import { Plus, Search, Filter, Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TicketList } from "@/components/crm/customer-service/TicketList";
import { CreateTicketDialog } from "@/components/crm/customer-service/CreateTicketDialog";
import { TicketFilters } from "@/components/crm/customer-service/TicketFilters";
import { useToast } from "@/hooks/use-toast";
import { customerServiceApi } from "@/lib/api/customer-service";

export default function TicketsPage() {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    status: [],
    priority: [],
    category: [],
    channel: [],
    sla_status: []
  });
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 20,
    total: 0,
    totalPages: 0
  });
  const [statistics, setStatistics] = useState({
    total_tickets: 0,
    new_tickets: 0,
    open_tickets: 0,
    in_progress_tickets: 0,
    resolved_tickets: 0,
    closed_tickets: 0
  });

  const { toast } = useToast();

  useEffect(() => {
    fetchTickets();
    fetchStatistics();
  }, [pagination.page, filters, searchQuery]);

  const fetchTickets = async () => {
    try {
      setLoading(true);
      const response = await customerServiceApi.listTickets({
        ...filters,
        search_query: searchQuery,
        page: pagination.page,
        page_size: pagination.pageSize
      });

      setTickets(response.tickets);
      setPagination({
        ...pagination,
        total: response.total,
        totalPages: response.total_pages
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch tickets",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchStatistics = async () => {
    try {
      const stats = await customerServiceApi.getStatistics();
      setStatistics(stats);
    } catch (error) {
      console.error("Failed to fetch statistics", error);
    }
  };

  const handleCreateTicket = () => {
    setShowCreateDialog(true);
  };

  const handleTicketCreated = () => {
    setShowCreateDialog(false);
    fetchTickets();
    fetchStatistics();
    toast({
      title: "Success",
      description: "Ticket created successfully"
    });
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPagination({ ...pagination, page: 1 });
  };

  const handleFilterChange = (newFilters: any) => {
    setFilters(newFilters);
    setPagination({ ...pagination, page: 1 });
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Support Tickets</h1>
          <p className="text-muted-foreground">
            Manage customer support tickets and inquiries
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setShowFilters(!showFilters)}>
            <Filter className="h-4 w-4 mr-2" />
            Filters
          </Button>
          <Button onClick={handleCreateTicket}>
            <Plus className="h-4 w-4 mr-2" />
            Create Ticket
          </Button>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{statistics.total_tickets}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">New</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">
              {statistics.new_tickets}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Open</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">
              {statistics.open_tickets}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">In Progress</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              {statistics.in_progress_tickets}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Resolved</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {statistics.resolved_tickets}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Closed</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-600">
              {statistics.closed_tickets}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Search Bar */}
      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search tickets by number, subject, or customer..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
        <Button type="submit">Search</Button>
      </form>

      {/* Filters Panel */}
      {showFilters && (
        <TicketFilters
          filters={filters}
          onFilterChange={handleFilterChange}
          onClose={() => setShowFilters(false)}
        />
      )}

      {/* Tickets List */}
      <Card>
        <CardHeader>
          <CardTitle>All Tickets</CardTitle>
          <CardDescription>
            {pagination.total} ticket{pagination.total !== 1 ? "s" : ""} found
          </CardDescription>
        </CardHeader>
        <CardContent>
          <TicketList
            tickets={tickets}
            loading={loading}
            pagination={pagination}
            onPageChange={(page) => setPagination({ ...pagination, page })}
            onRefresh={fetchTickets}
          />
        </CardContent>
      </Card>

      {/* Create Ticket Dialog */}
      {showCreateDialog && (
        <CreateTicketDialog
          open={showCreateDialog}
          onClose={() => setShowCreateDialog(false)}
          onSuccess={handleTicketCreated}
        />
      )}
    </div>
  );
}
