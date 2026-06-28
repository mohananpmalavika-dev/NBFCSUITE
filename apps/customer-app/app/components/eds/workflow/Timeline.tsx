import { Typography } from '../foundation/Typography';

export interface TimelineItem {
  title: string;
  description?: string;
  time?: string;
}

export interface TimelineProps {
  items: TimelineItem[];
}

export function Timeline({ items }: TimelineProps) {
  return (
    <ol className="space-y-4">
      {items.map((item, index) => (
        <li key={`${item.title}-${index}`} className="flex gap-3">
          <span className="mt-1 h-2.5 w-2.5 shrink-0 rounded-full bg-accent-primary" />
          <div>
            <Typography as="h4" variant="body" className="font-semibold">
              {item.title}
            </Typography>
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
