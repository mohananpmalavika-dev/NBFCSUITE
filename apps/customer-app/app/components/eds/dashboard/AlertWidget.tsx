import { Badge } from '../foundation/Badge';
import { Typography } from '../foundation/Typography';
import { WidgetContainer } from './WidgetContainer';

export interface DashboardAlert {
  title: string;
  severity: 'warning' | 'danger' | 'success';
  owner?: string;
}

export interface AlertWidgetProps {
  alerts: DashboardAlert[];
}

export function AlertWidget({ alerts }: AlertWidgetProps) {
  return (
    <WidgetContainer title="Attention Required" category="alert" refreshPolicy="30s" size="lg">
      <div className="space-y-3">
        {alerts.map((alert) => (
          <div key={alert.title} className="rounded-xl border border-border-default bg-background-elevated p-3">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <Typography as="h4" variant="body" className="font-semibold">
                {alert.title}
              </Typography>
              <Badge tone={alert.severity}>{alert.severity}</Badge>
            </div>
            {alert.owner ? (
              <Typography variant="caption" tone="muted" className="mt-2">
                Owner: {alert.owner}
              </Typography>
            ) : null}
          </div>
        ))}
      </div>
    </WidgetContainer>
  );
}
