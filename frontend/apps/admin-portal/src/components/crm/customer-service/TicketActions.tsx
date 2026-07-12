import { useState } from "react";
import { MoreVertical, UserPlus, CheckCircle, XCircle, RotateCcw, Edit } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { customerServiceApi } from "@/lib/api/customer-service";

interface TicketActionsProps {
  ticket: any;
  onUpdate: () => void;
}

export function TicketActions({ ticket, onUpdate }: TicketActionsProps) {
  const [showResolveDialog, setShowResolveDialog] = useState(false);
  const [showCloseDialog, setShowCloseDialog] = useState(false);
  const [showReopenDialog, setShowReopenDialog] = useState(false);
  const [resolution, setResolution] = useState("");
  const [closingNotes, setClosingNotes] = useState("");
  const [reopenReason, setReopenReason] = useState("");
  const [loading, setLoading] = useState(false);
  
  const { toast } = useToast();

  const canResolve = ["new", "open", "in_progress", "pending_customer", "pending_internal"].includes(
    ticket.status
  );
  const canClose = ticket.status === "resolved";
  const canReopen = ["resolved", "closed"].includes(ticket.status);

  const handleResolve = async () => {
    if (!resolution.trim()) {
      toast({
        title: "Error",
        description: "Please provide a resolution description",
        variant: "destructive",
      });
      return;
    }

    try {
      setLoading(true);
      await customerServiceApi.resolveTicket(ticket.id, {
        resolution,
        send_notification: true,
      });
      
      toast({
        title: "Success",
        description: "Ticket marked as resolved",
      });
      
      setShowResolveDialog(false);
      setResolution("");
      onUpdate();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to resolve ticket",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleClose = async () => {
    try {
      setLoading(true);
      await customerServiceApi.closeTicket(ticket.id, {
        closing_notes: closingNotes,
        send_notification: true,
      });
      
      toast({
        title: "Success",
        description: "Ticket closed successfully",
      });
      
      setShowCloseDialog(false);
      setClosingNotes("");
      onUpdate();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to close ticket",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleReopen = async () => {
    if (!reopenReason.trim()) {
      toast({
        title: "Error",
        description: "Please provide a reason for reopening",
        variant: "destructive",
      });
      return;
    }

    try {
      setLoading(true);
      await customerServiceApi.reopenTicket(ticket.id, {
        reason: reopenReason,
      });
      
      toast({
        title: "Success",
        description: "Ticket reopened",
      });
      
      setShowReopenDialog(false);
      setReopenReason("");
      onUpdate();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to reopen ticket",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline">
            <MoreVertical className="h-4 w-4 mr-2" />
            Actions
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-48">
          <DropdownMenuLabel>Ticket Actions</DropdownMenuLabel>
          <DropdownMenuSeparator />
          
          {canResolve && (
            <DropdownMenuItem onClick={() => setShowResolveDialog(true)}>
              <CheckCircle className="h-4 w-4 mr-2" />
              Resolve Ticket
            </DropdownMenuItem>
          )}
          
          {canClose && (
            <DropdownMenuItem onClick={() => setShowCloseDialog(true)}>
              <XCircle className="h-4 w-4 mr-2" />
              Close Ticket
            </DropdownMenuItem>
          )}
          
          {canReopen && (
            <DropdownMenuItem onClick={() => setShowReopenDialog(true)}>
              <RotateCcw className="h-4 w-4 mr-2" />
              Reopen Ticket
            </DropdownMenuItem>
          )}
          
          <DropdownMenuSeparator />
          
          <DropdownMenuItem>
            <UserPlus className="h-4 w-4 mr-2" />
            Assign Ticket
          </DropdownMenuItem>
          
          <DropdownMenuItem>
            <Edit className="h-4 w-4 mr-2" />
            Edit Details
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Resolve Dialog */}
      <AlertDialog open={showResolveDialog} onOpenChange={setShowResolveDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Resolve Ticket</AlertDialogTitle>
            <AlertDialogDescription>
              Please provide details about how the issue was resolved.
            </AlertDialogDescription>
          </AlertDialogHeader>
          
          <div className="space-y-2">
            <Label htmlFor="resolution">Resolution Details *</Label>
            <Textarea
              id="resolution"
              placeholder="Describe how the issue was resolved..."
              rows={4}
              value={resolution}
              onChange={(e) => setResolution(e.target.value)}
            />
          </div>
          
          <AlertDialogFooter>
            <AlertDialogCancel disabled={loading}>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleResolve} disabled={loading}>
              {loading ? "Resolving..." : "Resolve Ticket"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Close Dialog */}
      <AlertDialog open={showCloseDialog} onOpenChange={setShowCloseDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Close Ticket</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to close this ticket? This action indicates the issue is fully resolved and confirmed by the customer.
            </AlertDialogDescription>
          </AlertDialogHeader>
          
          <div className="space-y-2">
            <Label htmlFor="closingNotes">Closing Notes (Optional)</Label>
            <Textarea
              id="closingNotes"
              placeholder="Any additional notes..."
              rows={3}
              value={closingNotes}
              onChange={(e) => setClosingNotes(e.target.value)}
            />
          </div>
          
          <AlertDialogFooter>
            <AlertDialogCancel disabled={loading}>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleClose} disabled={loading}>
              {loading ? "Closing..." : "Close Ticket"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Reopen Dialog */}
      <AlertDialog open={showReopenDialog} onOpenChange={setShowReopenDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Reopen Ticket</AlertDialogTitle>
            <AlertDialogDescription>
              Please provide a reason for reopening this ticket.
            </AlertDialogDescription>
          </AlertDialogHeader>
          
          <div className="space-y-2">
            <Label htmlFor="reopenReason">Reason for Reopening *</Label>
            <Textarea
              id="reopenReason"
              placeholder="Why is this ticket being reopened?"
              rows={3}
              value={reopenReason}
              onChange={(e) => setReopenReason(e.target.value)}
            />
          </div>
          
          <AlertDialogFooter>
            <AlertDialogCancel disabled={loading}>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleReopen} disabled={loading}>
              {loading ? "Reopening..." : "Reopen Ticket"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
