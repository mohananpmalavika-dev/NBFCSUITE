import { CheckCircle2, Circle, CircleAlert, XCircle } from 'lucide-react';
import type { WorkflowTimelineItem } from './types';

export interface WorkflowTimelineProps {
  items: WorkflowTimelineItem[];
}

function getIcon(state: WorkflowTimelineItem['state']) {
  if (state === 'completed') {
    return CheckCircle2;
  }

  if (state === 'rejected') {
    return XCircle;
  }

  if (state === 'current') {
    return CircleAlert;
  }

  return Circle;
}

function getToneClass(state: WorkflowTimelineItem['state']) {
  if (state === 'completed') {
    return 'text-accent-success';
  }

  if (state === 'rejected') {
    return 'text-accent-danger';
  }

  if (state === 'current') {
    return 'text-accent-primary';
  }

  return 'text-text-muted';
}

export function WorkflowTimeline({ items }: WorkflowTimelineProps) {
  return (
    <ol className="relative space-y-4">
      {items.map((item, index) => {
        const Icon = getIcon(item.state);

        return (
          <li key={`${item.title}-${index}`} className="grid grid-cols-[32px_minmax(0,1fr)] gap-3">
            <div className="relative flex justify-center">
              {index < items.length - 1 ? <span className="absolute bottom-0 top-8 w-px bg-border-default" /> : null}
              <span className={`relative z-10 flex h-8 w-8 items-center justify-center rounded-full border border-border-default bg-background-surface ${getToneClass(item.state)}`}>
                <Icon className="h-4 w-4" />
              </span>
            </div>
            <div className="rounded-xl border border-border-default bg-background-surface p-3">
              <div className="flex flex-wrap items-start justify-between gap-2">
                <div>
                  <p className="text-sm font-semibold text-text-primary">{item.title}</p>
                  {item.actor ? <p className="mt-1 text-xs text-text-muted">{item.actor}</p> : null}
                </div>
                {item.time ? <p className="text-xs font-semibold text-text-muted">{item.time}</p> : null}
              </div>
              {item.description ? <p className="mt-2 text-sm leading-6 text-text-secondary">{item.description}</p> : null}
            </div>
          </li>
        );
      })}
    </ol>
  );
}
