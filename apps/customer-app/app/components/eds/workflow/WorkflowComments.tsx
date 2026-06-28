import { MessageSquarePlus, Paperclip } from 'lucide-react';
import { Button } from '../foundation/Button';
import type { WorkflowComment } from './types';

export interface WorkflowCommentsProps {
  comments: WorkflowComment[];
  onAddComment?: () => void;
}

export function WorkflowComments({ comments, onAddComment }: WorkflowCommentsProps) {
  return (
    <section className="rounded-xl border border-border-default bg-background-elevated p-4">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h3 className="text-sm font-semibold text-text-primary">Comments</h3>
          <p className="mt-1 text-sm text-text-secondary">Mention users, attach files, and keep collaboration in context.</p>
        </div>
        <Button size="sm" variant="secondary" icon={<MessageSquarePlus className="h-4 w-4" />} onClick={onAddComment}>
          Add
        </Button>
      </div>
      <div className="mt-4 space-y-3">
        {comments.map((comment) => (
          <article key={comment.id} className="rounded-xl border border-border-default bg-background-surface p-3">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <p className="text-sm font-semibold text-text-primary">{comment.author}</p>
              <p className="text-xs text-text-muted">{comment.time}</p>
            </div>
            <p className="mt-2 text-sm leading-6 text-text-secondary">{comment.message}</p>
            {comment.attachments?.length ? (
              <div className="mt-2 flex flex-wrap gap-2 text-xs font-semibold text-text-secondary">
                {comment.attachments.map((attachment) => (
                  <span key={attachment} className="inline-flex items-center gap-1 rounded-full bg-background-elevated px-2 py-1">
                    <Paperclip className="h-3 w-3" />
                    {attachment}
                  </span>
                ))}
              </div>
            ) : null}
          </article>
        ))}
      </div>
    </section>
  );
}
