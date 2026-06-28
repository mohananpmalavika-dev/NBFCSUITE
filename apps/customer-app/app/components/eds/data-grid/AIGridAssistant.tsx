import { Sparkles } from 'lucide-react';
import { Typography } from '../foundation/Typography';

export interface AIGridAssistantProps {
  selectedCount: number;
  prompts?: string[];
}

export function AIGridAssistant({
  selectedCount,
  prompts = ['Summarize selected records', 'Find abnormal entries', 'Explain overdue items'],
}: AIGridAssistantProps) {
  return (
    <aside className="rounded-xl border border-border-default bg-background-elevated p-4">
      <div className="flex items-center gap-2">
        <Sparkles className="h-4 w-4 text-accent-primary" />
        <Typography as="h3" variant="h3">
          Grid AI Assistant
        </Typography>
      </div>
      <Typography tone="secondary" className="mt-2">
        Scoped to {selectedCount} selected record{selectedCount === 1 ? '' : 's'}.
      </Typography>
      <div className="mt-4 space-y-2">
        {prompts.map((prompt) => (
          <button
            key={prompt}
            type="button"
            className="w-full rounded-lg bg-background-surface px-3 py-2 text-left text-sm font-semibold text-text-secondary"
          >
            {prompt}
          </button>
        ))}
      </div>
    </aside>
  );
}
