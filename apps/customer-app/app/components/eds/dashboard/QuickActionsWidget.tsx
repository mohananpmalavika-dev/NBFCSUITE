import { Button } from '../foundation/Button';
import type { DashboardAction } from './types';
import { WidgetContainer } from './WidgetContainer';

export interface QuickActionsWidgetProps {
  actions: DashboardAction[];
}

export function QuickActionsWidget({ actions }: QuickActionsWidgetProps) {
  return (
    <WidgetContainer title="Quick Actions" category="quick-action" refreshPolicy="role based" size="md">
      <div className="flex flex-wrap gap-3">
        {actions.map((action, index) => (
          <Button
            key={action.label}
            size="sm"
            variant={index === 0 ? 'primary' : 'secondary'}
            icon={action.icon}
            onClick={action.onClick}
          >
            {action.label}
          </Button>
        ))}
      </div>
    </WidgetContainer>
  );
}
