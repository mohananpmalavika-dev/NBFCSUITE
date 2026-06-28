import { ApprovalCard } from '../workflow/ApprovalCard';
import { WidgetContainer } from './WidgetContainer';

export interface DashboardApproval {
  title: string;
  requester: string;
  amount?: string;
  sla: string;
}

export interface ApprovalWidgetProps {
  approvals: DashboardApproval[];
  onApprove?: () => void;
}

export function ApprovalWidget({ approvals, onApprove }: ApprovalWidgetProps) {
  return (
    <WidgetContainer title="Pending Approvals" category="approval" refreshPolicy="30s" size="lg">
      <div className="grid gap-3 lg:grid-cols-2">
        {approvals.map((approval) => (
          <ApprovalCard
            key={`${approval.title}-${approval.requester}`}
            title={approval.title}
            requester={`${approval.requester} | SLA ${approval.sla}`}
            amount={approval.amount}
            onApprove={onApprove}
          />
        ))}
      </div>
    </WidgetContainer>
  );
}
