import { Badge } from '../foundation/Badge';

export interface RoleBadgeProps {
  role: string;
  elevated?: boolean;
}

export function RoleBadge({ role, elevated = false }: RoleBadgeProps) {
  return <Badge tone={elevated ? 'warning' : 'neutral'}>{role}</Badge>;
}
