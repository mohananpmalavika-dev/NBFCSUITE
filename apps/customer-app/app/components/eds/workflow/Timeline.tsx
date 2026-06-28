import { Typography } from '../foundation/Typography';

import type { WorkflowStageStatus } from './types';

export interface TimelineItem {
  title: string;
  description?: string;
  time?: string;
  actor?: string;
  state?: WorkflowStageStatus | 'assigned';
}

export interface TimelineProps {
  items: TimelineItem[];
}

const dotToneMap: Record<WorkflowStageStatus, string> = {
  completed: 'bg-accent-success',
  current: 'bg-accent-primary',
  pending: 'bg-accent-muted',
  rejected: 'bg-accent-danger',
};

export function Timeline({ items }: TimelineProps) {
  return (
    <ol className="space-y-4">
      {items.map((item, index) => (
        <li key={`${item.title}-${index}`} className="flex gap-3">
          <span
            className={
              'mt-1 h-2.5 w-2.5 shrink-0 rounded-full ' +
              (item.state && item.state !== 'assigned' ? dotToneMap[item.state] : 'bg-accent-primary')
            }
          />
          <div>
            <Typography as="h4" variant="body" className="font-semibold">
              {item.title}
            </Typography>
            {item.actor ? (
              <Typography tone="secondary" className="mt-1">
                {item.actor}
              </Typography>
            ) : null}
            {item.description ? (
              <Typography tone="secondary" className="mt-1">
                {item.description}
              </Typography>
            ) : null}
            {item.time ? (
              <Typography variant="caption" tone="muted" className="mt-1">
                {item.time}
              </Typography>
            ) : null}
          </div>
        </li>
      ))}
    </ol>
  );
}
