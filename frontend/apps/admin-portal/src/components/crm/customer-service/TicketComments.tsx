import { useState } from "react";
import { Send, MessageSquare, Lock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { useToast } from "@/hooks/use-toast";
import { customerServiceApi } from "@/lib/api/customer-service";
import { formatDate } from "@/lib/utils";

interface TicketCommentsProps {
  ticketId: number;
  comments: any[];
  onCommentAdded: () => void;
}

export function TicketComments({
  ticketId,
  comments,
  onCommentAdded,
}: TicketCommentsProps) {
  const [newComment, setNewComment] = useState("");
  const [isInternal, setIsInternal] = useState(false);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!newComment.trim()) {
      toast({
        title: "Error",
        description: "Please enter a comment",
        variant: "destructive",
      });
      return;
    }

    try {
      setLoading(true);
      await customerServiceApi.addComment(ticketId, {
        comment: newComment,
        is_internal: isInternal,
        is_solution: false,
      });

      setNewComment("");
      setIsInternal(false);
      onCommentAdded();

      toast({
        title: "Success",
        description: "Comment added successfully",
      });
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to add comment",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <div className="space-y-6">
      {/* Comment List */}
      <div className="space-y-4">
        {comments.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <MessageSquare className="h-12 w-12 mx-auto mb-2 opacity-20" />
            <p>No comments yet</p>
            <p className="text-sm">Be the first to add a comment</p>
          </div>
        ) : (
          comments.map((comment) => (
            <div
              key={comment.id}
              className={`flex gap-3 p-4 rounded-lg ${
                comment.is_internal ? "bg-yellow-50 border border-yellow-200" : "bg-muted"
              }`}
            >
              <Avatar className="h-10 w-10">
                <AvatarFallback>
                  {comment.created_by_name
                    ? getInitials(comment.created_by_name)
                    : "U"}
                </AvatarFallback>
              </Avatar>

              <div className="flex-1 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold">
                      {comment.created_by_name || "Unknown User"}
                    </span>
                    {comment.is_internal && (
                      <Badge variant="outline" className="bg-yellow-100 text-yellow-800">
                        <Lock className="h-3 w-3 mr-1" />
                        Internal
                      </Badge>
                    )}
                    {comment.is_solution && (
                      <Badge variant="outline" className="bg-green-100 text-green-800">
                        Solution
                      </Badge>
                    )}
                  </div>
                  <span className="text-sm text-muted-foreground">
                    {formatDate(comment.created_at)}
                  </span>
                </div>

                <p className="text-sm whitespace-pre-wrap">{comment.comment}</p>
              </div>
            </div>
          ))
        )}
      </div>

      <Separator />

      {/* Add Comment Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <Label htmlFor="comment">Add Comment</Label>
          <Textarea
            id="comment"
            placeholder="Type your comment here..."
            rows={4}
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            disabled={loading}
            className="mt-2"
          />
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Checkbox
              id="internal"
              checked={isInternal}
              onCheckedChange={(checked) => setIsInternal(checked as boolean)}
              disabled={loading}
            />
            <Label
              htmlFor="internal"
              className="text-sm font-normal cursor-pointer"
            >
              Internal note (not visible to customer)
            </Label>
          </div>

          <Button type="submit" disabled={loading || !newComment.trim()}>
            <Send className="h-4 w-4 mr-2" />
            {loading ? "Sending..." : "Send Comment"}
          </Button>
        </div>

        {isInternal && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 text-sm">
            <div className="flex items-start gap-2">
              <Lock className="h-4 w-4 text-yellow-600 mt-0.5" />
              <div>
                <p className="font-semibold text-yellow-900">Internal Note</p>
                <p className="text-yellow-700">
                  This comment will only be visible to team members and will not be shown to the customer.
                </p>
              </div>
            </div>
          </div>
        )}
      </form>
    </div>
  );
}
