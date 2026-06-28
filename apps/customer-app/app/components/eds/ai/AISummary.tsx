import { Sparkles } from 'lucide-react';
import { Typography } from '../foundation/Typography';

export interface AISummaryProps {
  title?: string;
  summary: string;
  suggestions?: string[];
}

export function AISummary({ title = 'AI Summary', summary, suggestions = [] }: AISummaryProps) {
  return (
    <section className="rounded-xl border border-border-default bg-background-elevated p-4">
      <div className="flex items-center gap-2">
        <Sparkles className="h-4 w-4 text-accent-primary" />
        <Typography as="h3" variant="h3">
          {title}
        </Typography>
      </div>
      <Typography tone="secondary" className="mt-3">
        {summary}
      </Typography>
      {suggestions.length > 0 ? (
        <ul className="mt-4 space-y-2 text-sm text-text-secondary">
          {suggestions.map((suggestion) => (
            <li key={suggestion} className="rounded-lg bg-background-surface px-3 py-2">
              {suggestion}
            </li>
          ))}
        </ul>
      ) : null}
    </section>
  );
}
