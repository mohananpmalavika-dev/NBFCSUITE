import type { ReactNode } from 'react';
import { Typography } from '../foundation/Typography';

export interface WorkspaceHeaderProps {
  eyebrow?: string;
  title: string;
  description?: string;
  actions?: ReactNode;
}

export function WorkspaceHeader({ eyebrow, title, description, actions }: WorkspaceHeaderProps) {
  return (
    <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
      <div className="max-w-3xl">
        {eyebrow ? (
          <Typography variant="label" tone="muted">
            {eyebrow}
          </Typography>
        ) : null}
        <Typography as="h1" variant="h1" className="mt-3">
          {title}
        </Typography>
        {description ? (
          <Typography tone="secondary" className="mt-3">
            {description}
          </Typography>
        ) : null}
      </div>
      {actions ? <div className="flex flex-wrap gap-3">{actions}</div> : null}
    </div>
  );
}
