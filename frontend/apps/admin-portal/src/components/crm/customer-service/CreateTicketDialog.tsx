import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { customerServiceApi } from "@/lib/api/customer-service";

const ticketSchema = z.object({
  customer_id: z.number().min(1, "Customer is required"),
  subject: z.string().min(5, "Subject must be at least 5 characters"),
  description: z.string().min(10, "Description must be at least 10 characters"),
  category: z.enum([
    "account", "loan", "deposit", "payment", "technical",
    "complaint", "inquiry", "request", "feedback", "other"
  ]),
  priority: z.enum(["low", "medium", "high", "urgent", "critical"]),
  channel: z.enum([
    "phone", "email", "web_portal", "mobile_app", "chat",
    "social_media", "walk_in", "whatsapp"
  ]),
  assigned_to_user_id: z.number().optional(),
  tags: z.string().optional(),
});

type TicketFormData = z.infer<typeof ticketSchema>;

interface CreateTicketDialogProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function CreateTicketDialog({
  open,
  onClose,
  onSuccess,
}: CreateTicketDialogProps) {
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const form = useForm<TicketFormData>({
    resolver: zodResolver(ticketSchema),
    defaultValues: {
      priority: "medium",
      channel: "web_portal",
    },
  });

  const onSubmit = async (data: TicketFormData) => {
    try {
      setLoading(true);
      
      // Convert tags string to array
      const tags = data.tags
        ? data.tags.split(",").map((tag) => tag.trim()).filter(Boolean)
        : [];

      const payload = {
        ...data,
        tags,
      };

      await customerServiceApi.createTicket(payload);
      
      toast({
        title: "Success",
        description: "Ticket created successfully",
      });
      
      form.reset();
      onSuccess();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to create ticket",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Create New Ticket</DialogTitle>
          <DialogDescription>
            Create a support ticket for a customer inquiry or issue
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="customer_id"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Customer ID *</FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      placeholder="Enter customer ID"
                      {...field}
                      onChange={(e) => field.onChange(parseInt(e.target.value) || 0)}
                    />
                  </FormControl>
                  <FormDescription>
                    The ID of the customer reporting the issue
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="subject"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Subject *</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="Brief description of the issue"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Description *</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Detailed description of the issue"
                      rows={4}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="category"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Category *</FormLabel>
                    <Select
                      onValueChange={field.onChange}
                      defaultValue={field.value}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select category" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="account">Account</SelectItem>
                        <SelectItem value="loan">Loan</SelectItem>
                        <SelectItem value="deposit">Deposit</SelectItem>
                        <SelectItem value="payment">Payment</SelectItem>
                        <SelectItem value="technical">Technical</SelectItem>
                        <SelectItem value="complaint">Complaint</SelectItem>
                        <SelectItem value="inquiry">Inquiry</SelectItem>
                        <SelectItem value="request">Request</SelectItem>
                        <SelectItem value="feedback">Feedback</SelectItem>
                        <SelectItem value="other">Other</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="priority"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Priority *</FormLabel>
                    <Select
                      onValueChange={field.onChange}
                      defaultValue={field.value}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select priority" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="low">Low</SelectItem>
                        <SelectItem value="medium">Medium</SelectItem>
                        <SelectItem value="high">High</SelectItem>
                        <SelectItem value="urgent">Urgent</SelectItem>
                        <SelectItem value="critical">Critical</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <FormField
              control={form.control}
              name="channel"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Channel *</FormLabel>
                  <Select
                    onValueChange={field.onChange}
                    defaultValue={field.value}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select channel" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="phone">Phone</SelectItem>
                      <SelectItem value="email">Email</SelectItem>
                      <SelectItem value="web_portal">Web Portal</SelectItem>
                      <SelectItem value="mobile_app">Mobile App</SelectItem>
                      <SelectItem value="chat">Chat</SelectItem>
                      <SelectItem value="social_media">Social Media</SelectItem>
                      <SelectItem value="walk_in">Walk-in</SelectItem>
                      <SelectItem value="whatsapp">WhatsApp</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormDescription>
                    How the customer contacted support
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="tags"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Tags</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="e.g., login, urgent, technical"
                      {...field}
                    />
                  </FormControl>
                  <FormDescription>
                    Comma-separated tags for categorization
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={onClose}
                disabled={loading}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={loading}>
                {loading ? "Creating..." : "Create Ticket"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
