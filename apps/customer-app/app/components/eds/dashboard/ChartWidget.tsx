import { Typography } from '../foundation/Typography';
import { WidgetContainer } from './WidgetContainer';

export interface ChartDatum {
  label: string;
  value: number;
}

export interface ChartWidgetProps {
  title: string;
  description?: string;
  data: ChartDatum[];
  drilldownTarget?: string;
}

export function ChartWidget({ title, description, data, drilldownTarget }: ChartWidgetProps) {
  const max = Math.max(...data.map((item) => item.value), 1);

  return (
    <WidgetContainer title={title} description={description} category="chart" refreshPolicy="5m" size="lg">
      <div className="flex h-44 items-end gap-3">
        {data.map((item) => {
          const height = `${Math.max((item.value / max) * 100, 8)}%`;

          return (
            <div key={item.label} className="flex min-w-0 flex-1 flex-col items-center gap-2">
              <div className="flex h-36 w-full items-end rounded-lg bg-background-elevated px-2 py-2">
                <div
                  className="w-full rounded-md bg-accent-primary"
                  style={{ height }}
                  aria-label={`${item.label}: ${item.value}`}
                />
              </div>
              <Typography variant="caption" tone="muted" className="truncate">
                {item.label}
              </Typography>
            </div>
          );
        })}
      </div>
      {drilldownTarget ? (
        <Typography variant="caption" tone="muted" className="mt-3">
          Drill-down: {drilldownTarget}
        </Typography>
      ) : null}
    </WidgetContainer>
  );
}
