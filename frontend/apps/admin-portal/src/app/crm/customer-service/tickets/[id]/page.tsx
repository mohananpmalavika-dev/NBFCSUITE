"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Clock, User, Tag, AlertCircle, MessageSquare, FileText, Activity } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { TicketDetails } from "@/components/crm/customer-service/TicketDetails";
import { TicketComments } from "@/components/crm/customer-service/TicketComments";
import { TicketActivities } from "@/components/crm/customer-service/TicketActivities";
import { TicketActions } from "@/components/crm/customer-service/TicketActions";
import { useToast } from "@/hooks/use-toast";
import { customerServiceApi } from "@/lib/api/customer-service";
import { formatDate } from "@/lib/utils";

export default function TicketDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { toast } = useToast();
  const [ticket, setTicket] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (params.id) {
      fetchTicket();
    }
  }, [params.id]);

  const fetchTicket = async () => {
    try {
      setLoading(true);
      const data = await customerServiceApi.getTicket(params.id as string);
      setTicket(data);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch ticket details",
        variant: "destructive"
      });
      router.push("/crm/customer-service/tickets");
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      new: "bg-blue-100 text-blue-800",
      open: "bg-yellow-100 text-yellow-800",
      in_progress: "bg-orange-100 text-orange-800",
      pending_customer: "bg-purple-100 text-purple-800",
      pending_internal: "bg-indigo-100 text-indigo-800",
      resolved: "bg-green-100 text-green-800",
      closed: "bg-gray-100 text-gray-800",
      reopened: "bg-red-100 text-red-800",
      cancelled: "bg-gray-100 text-gray-800"
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
      critical: "bg-red-600 text-white"
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
      paused: "bg-gray-100 text-gray-800"
    };

    return (
      <Badge className={colors[slaStatus] || "bg-gray-100 text-gray-800"}>
        {slaStatus.replace(/_/g, " ").toUpperCase()}
      </Badge>
    );
  };

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
            <p className="mt-4 text-muted-foreground">Loading ticket...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!ticket) {
    return null;
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => router.back()}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">{ticket.ticket_number}</h1>
            <p className="text-muted-foreground">{ticket.subject}</p>
          </div>
        </div>
        <TicketActions ticket={ticket} onUpdate={fetchTicket} />
      </div>

      {/* Status Row */}
      <div className="flex items-center gap-4 flex-wrap">
        {getStatusBadge(ticket.status)}
        {getPriorityBadge(ticket.priority)}
        {ticket.sla_status && getSLABadge(ticket.sla_status)}
        <Badge variant="outline">
          <Tag className="h-3 w-3 mr-1" />
          {ticket.category}
        </Badge>
        <Badge variant="outline">
          {ticket.channel.replace(/_/g, " ")}
        </Badge>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Ticket Details */}
          <Card>
            <CardHeader>
              <CardTitle>Ticket Details</CardTitle>
            </CardHeader>
            <CardContent>
              <TicketDetails ticket={ticket} />
            </CardContent>
          </Card>

          {/* Tabs */}
          <Tabs defaultValue="comments" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="comments">
                <MessageSquare className="h-4 w-4 mr-2" />
                Comments ({ticket.comments?.length || 0})
              </TabsTrigger>
              <TabsTrigger value="activity">
                <Activity className="h-4 w-4 mr-2" />
                Activity ({ticket.activities?.length || 0})
              </TabsTrigger>
            </TabsList>
            <TabsContent value="comments" className="mt-4">
              <TicketComments
                ticketId={ticket.id}
                comments={ticket.comments || []}
                onCommentAdded={fetchTicket}
              />
            </TabsContent>
            <TabsContent value="activity" className="mt-4">
              <TicketActivities activities={ticket.activities || []} />
            </TabsContent>
          </Tabs>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Customer Info */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Customer Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <p className="text-sm text-muted-foreground">Name</p>
                <p className="font-medium">{ticket.customer_name}</p>
              </div>
              {ticket.customer_email && (
                <div>
                  <p className="text-sm text-muted-foreground">Email</p>
                  <p className="font-medium">{ticket.customer_email}</p>
                </div>
              )}
              {ticket.customer_phone && (
                <div>
                  <p className="text-sm text-muted-foreground">Phone</p>
                  <p className="font-medium">{ticket.customer_phone}</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Assignment */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Assignment</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {ticket.assigned_to_name ? (
                <div>
                  <p className="text-sm text-muted-foreground">Assigned To</p>
                  <div className="flex items-center gap-2 mt-1">
                    <User className="h-4 w-4" />
                    <p className="font-medium">{ticket.assigned_to_name}</p>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">Unassigned</p>
              )}
              {ticket.assigned_to_team && (
                <div>
                  <p className="text-sm text-muted-foreground">Team</p>
                  <p className="font-medium">{ticket.assigned_to_team}</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* SLA Information */}
          {ticket.sla_first_response_due && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">SLA Tracking</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <p className="text-sm text-muted-foreground">First Response Due</p>
                  <div className="flex items-center gap-2 mt-1">
                    <Clock className="h-4 w-4" />
                    <p className="font-medium">
                      {formatDate(ticket.sla_first_response_due)}
                    </p>
                  </div>
                </div>
                {ticket.sla_resolution_due && (
                  <div>
                    <p className="text-sm text-muted-foreground">Resolution Due</p>
                    <div className="flex items-center gap-2 mt-1">
                      <Clock className="h-4 w-4" />
                      <p className="font-medium">
                        {formatDate(ticket.sla_resolution_due)}
                      </p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Timestamps */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Timestamps</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div>
                <p className="text-muted-foreground">Created</p>
                <p>{formatDate(ticket.created_at)}</p>
              </div>
              {ticket.resolved_at && (
                <div>
                  <p className="text-muted-foreground">Resolved</p>
                  <p>{formatDate(ticket.resolved_at)}</p>
                </div>
              )}
              {ticket.closed_at && (
                <div>
                  <p className="text-muted-foreground">Closed</p>
                  <p>{formatDate(ticket.closed_at)}</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
