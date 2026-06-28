import { Timeline, type TimelineItem } from '../workflow/Timeline';
import { WidgetContainer } from './WidgetContainer';

export interface ActivityWidgetProps {
  activities: TimelineItem[];
}

export function ActivityWidget({ activities }: ActivityWidgetProps) {
  return (
    <WidgetContainer title="Recent Activity" category="activity" refreshPolicy="1m" size="md">
      <Timeline items={activities} />
    </WidgetContainer>
  );
}
