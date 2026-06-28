import type { ReactNode } from 'react';
import { Badge } from '../foundation/Badge';
import { Typography } from '../foundation/Typography';

export interface AlertProps {
  title: string;
  children?: ReactNode;
  tone?: 'info' | 'success' | 'warning' | 'danger';
}

const toneMap = {
  info: 'accent',
  success: 'success',
  warning: 'warning',
  danger: 'danger',
} as const;

export function Alert({ title, children, tone = 'info' }: AlertProps) {
  return (
    <div className="rounded-xl border border-border-default bg-background-surface p-4">
      <div className="flex flex-wrap items-center gap-3">
        <Badge tone={toneMap[tone]}>{tone}</Badge>
        <Typography as="h3" variant="h3">
          {title}
        </Typography>
      </div>
      {children ? (
        <Typography tone="secondary" className="mt-3">
          {children}
        </Typography>
      ) : null}
    </div>
  );
}
