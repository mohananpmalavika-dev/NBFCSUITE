import type { ReactNode } from 'react';
import { Typography } from '../foundation/Typography';

export interface EmptyStateProps {
  title: string;
  description?: string;
  action?: ReactNode;
}

export function EmptyState({ title, description, action }: EmptyStateProps) {
  return (
    <div className="rounded-xl border border-dashed border-border-default bg-background-surface px-6 py-10 text-center">
      <Typography as="h3" variant="h3">
        {title}
      </Typography>
      {description ? (
        <Typography tone="secondary" className="mx-auto mt-2 max-w-md">
          {description}
        </Typography>
      ) : null}
      {action ? <div className="mt-5 flex justify-center">{action}</div> : null}
    </div>
  );
}
