import { AISummary } from '../ai/AISummary';
import { WidgetContainer } from './WidgetContainer';

export interface AISummaryWidgetProps {
  summary: string;
  suggestions?: string[];
}

export function AISummaryWidget({ summary, suggestions }: AISummaryWidgetProps) {
  return (
    <WidgetContainer title="AI Insights" category="ai" refreshPolicy="on demand" size="lg">
      <AISummary summary={summary} suggestions={suggestions} />
    </WidgetContainer>
  );
}
