import { useState } from "react";
import { useRouter } from "next/navigation";
import { Eye, Clock, User, Tag } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { formatDate, formatDistanceToNow } from "@/lib/utils";

interface TicketListProps {
  tickets: any[];
  loading: boolean;
  pagination: {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
  };
  onPageChange: (page: number) => void;
  onRefresh: () => void;
}

export function TicketList({
  tickets,
  loading,
  pagination,
  onPageChange,
  onRefresh,
}: TicketListProps) {
  const router = useRouter();

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      new: "bg-blue-100 text-blue-800",
      open: "bg-yellow-100 text-yellow-800",
      in_progress: "bg-orange-100 text-orange-800",
      pending_customer: "bg-purple-100 text-purple-800",
      resolved: "bg-green-100 text-green-800",
      closed: "bg-gray-100 text-gray-800",
      reopened: "bg-red-100 text-red-800",
    };

    return (
      <Badge className={colors[status] || "bg-gray-100 text-gray-800"}>
        {status.replace(/_/g, " ").toUpperCase()}
      </Badge>
    );
  };

  const getPriorityBadge = (priority: string) => {
    const colors: Record<string, string> = {
      low: "bg-blue-100 text-blue-800",
      medium: "bg-yellow-100 text-yellow-800",
      high: "bg-orange-100 text-orange-800",
      urgent: "bg-red-100 text-red-800",
      critical: "bg-red-600 text-white",
    };

    return (
      <Badge className={colors[priority] || "bg-gray-100 text-gray-800"}>
        {priority.toUpperCase()}
      </Badge>
    );
  };

  const getSLABadge = (slaStatus: string) => {
    const colors: Record<string, string> = {
      within_sla: "bg-green-100 text-green-800",
      approaching_breach: "bg-yellow-100 text-yellow-800",
      breached: "bg-red-100 text-red-800",
    };

    return (
      <Badge className={colors[slaStatus] || "bg-gray-100 text-gray-800"}>
        {slaStatus === "within_sla" ? "✓" : slaStatus === "approaching_breach" ? "⚠" : "✗"}
      </Badge>
    );
  };

  const handleRowClick = (ticketId: number) => {
    router.push(`/crm/customer-service/tickets/${ticketId}`);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading tickets...</p>
        </div>
      </div>
    );
  }

  if (tickets.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">No tickets found</p>
        <Button variant="outline" onClick={onRefresh} className="mt-4">
          Refresh
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Ticket #</TableHead>
              <TableHead>Subject</TableHead>
              <TableHead>Customer</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Priority</TableHead>
              <TableHead>SLA</TableHead>
              <TableHead>Assigned To</TableHead>
              <TableHead>Created</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {tickets.map((ticket) => (
              <TableRow
                key={ticket.id}
                className="cursor-pointer hover:bg-muted/50"
                onClick={() => handleRowClick(ticket.id)}
              >
                <TableCell className="font-medium">{ticket.ticket_number}</TableCell>
                <TableCell>
                  <div className="max-w-xs truncate">{ticket.subject}</div>
                  <div className="flex items-center gap-1 mt-1">
                    <Tag className="h-3 w-3 text-muted-foreground" />
                    <span className="text-xs text-muted-foreground">{ticket.category}</span>
                  </div>
                </TableCell>
                <TableCell>{ticket.customer_name}</TableCell>
                <TableCell>{getStatusBadge(ticket.status)}</TableCell>
                <TableCell>{getPriorityBadge(ticket.priority)}</TableCell>
                <TableCell>
                  {ticket.sla_status ? getSLABadge(ticket.sla_status) : "-"}
                </TableCell>
                <TableCell>
                  {ticket.assigned_to_name ? (
                    <div className="flex items-center gap-1">
                      <User className="h-3 w-3" />
                      <span className="text-sm">{ticket.assigned_to_name}</span>
                    </div>
                  ) : (
                    <span className="text-muted-foreground text-sm">Unassigned</span>
                  )}
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-1">
                    <Clock className="h-3 w-3 text-muted-foreground" />
                    <span className="text-sm">{formatDistanceToNow(ticket.created_at)}</span>
                  </div>
                </TableCell>
                <TableCell>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleRowClick(ticket.id);
                    }}
                  >
                    <Eye className="h-4 w-4" />
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between">
        <div className="text-sm text-muted-foreground">
          Showing {(pagination.page - 1) * pagination.pageSize + 1} to{" "}
          {Math.min(pagination.page * pagination.pageSize, pagination.total)} of{" "}
          {pagination.total} tickets
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => onPageChange(pagination.page - 1)}
            disabled={pagination.page === 1}
          >
            Previous
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => onPageChange(pagination.page + 1)}
            disabled={pagination.page >= pagination.totalPages}
          >
            Next
          </Button>
        </div>
      </div>
    </div>
  );
}
