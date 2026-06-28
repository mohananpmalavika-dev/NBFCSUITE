import { Badge } from '../foundation/Badge';
import { Typography } from '../foundation/Typography';
import { WidgetContainer } from './WidgetContainer';

export interface DashboardTask {
  title: string;
  due: string;
  owner: string;
  priority: 'low' | 'medium' | 'high';
}

export interface TaskWidgetProps {
  tasks: DashboardTask[];
}

const priorityToneMap = {
  low: 'neutral',
  medium: 'warning',
  high: 'danger',
} as const;

export function TaskWidget({ tasks }: TaskWidgetProps) {
  return (
    <WidgetContainer title="Task Center" category="task" refreshPolicy="30s" size="md">
      <div className="space-y-3">
        {tasks.map((task) => (
          <div key={task.title} className="rounded-xl bg-background-elevated p-3">
            <div className="flex items-start justify-between gap-3">
              <Typography as="h4" variant="body" className="font-semibold">
                {task.title}
              </Typography>
              <Badge tone={priorityToneMap[task.priority]}>{task.priority}</Badge>
            </div>
            <Typography variant="caption" tone="muted" className="mt-2">
              {task.owner} | {task.due}
            </Typography>
          </div>
        ))}
      </div>
    </WidgetContainer>
  );
}
