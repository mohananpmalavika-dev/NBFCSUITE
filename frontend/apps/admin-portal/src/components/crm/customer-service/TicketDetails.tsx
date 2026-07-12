import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";

interface TicketDetailsProps {
  ticket: any;
}

export function TicketDetails({ ticket }: TicketDetailsProps) {
  return (
    <div className="space-y-6">
      {/* Description */}
      <div>
        <h3 className="font-semibold mb-2">Description</h3>
        <p className="text-sm text-muted-foreground whitespace-pre-wrap">
          {ticket.description}
        </p>
      </div>

      <Separator />

      {/* Details Grid */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <p className="text-sm text-muted-foreground mb-1">Ticket Number</p>
          <p className="font-medium">{ticket.ticket_number}</p>
        </div>

        <div>
          <p className="text-sm text-muted-foreground mb-1">Category</p>
          <Badge variant="outline">{ticket.category}</Badge>
        </div>

        <div>
          <p className="text-sm text-muted-foreground mb-1">Priority</p>
          <Badge variant="outline">{ticket.priority}</Badge>
        </div>

        <div>
          <p className="text-sm text-muted-foreground mb-1">Channel</p>
          <Badge variant="outline">{ticket.channel.replace(/_/g, " ")}</Badge>
        </div>

        {ticket.tags && ticket.tags.length > 0 && (
          <div className="col-span-2">
            <p className="text-sm text-muted-foreground mb-2">Tags</p>
            <div className="flex gap-2 flex-wrap">
              {ticket.tags.map((tag: string, index: number) => (
                <Badge key={index} variant="secondary">
                  {tag}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Resolution (if resolved) */}
      {ticket.resolution && (
        <>
          <Separator />
          <div>
            <h3 className="font-semibold mb-2 text-green-700">Resolution</h3>
            <p className="text-sm text-muted-foreground whitespace-pre-wrap">
              {ticket.resolution}
            </p>
          </div>
        </>
      )}

      {/* Customer Feedback (if provided) */}
      {ticket.customer_satisfaction_rating && (
        <>
          <Separator />
          <div>
            <h3 className="font-semibold mb-2">Customer Feedback</h3>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-sm text-muted-foreground">Rating:</span>
              <div className="flex">
                {[1, 2, 3, 4, 5].map((star) => (
                  <span
                    key={star}
                    className={
                      star <= ticket.customer_satisfaction_rating
                        ? "text-yellow-400"
                        : "text-gray-300"
                    }
                  >
                    ★
                  </span>
                ))}
              </div>
              <span className="text-sm font-medium">
                {ticket.customer_satisfaction_rating}/5
              </span>
            </div>
            {ticket.customer_feedback && (
              <p className="text-sm text-muted-foreground">
                {ticket.customer_feedback}
              </p>
            )}
          </div>
        </>
      )}
    </div>
  );
}
