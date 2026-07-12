import { Activity, User, CheckCircle, XCircle, Edit, UserPlus, RotateCcw } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/lib/utils";

interface TicketActivitiesProps {
  activities: any[];
}

export function TicketActivities({ activities }: TicketActivitiesProps) {
  const getActivityIcon = (type: string) => {
    const iconMap: Record<string, any> = {
      created: Activity,
      assigned: UserPlus,
      status_changed: Edit,
      priority_changed: Edit,
      resolved: CheckCircle,
      closed: XCircle,
      reopened: RotateCcw,
      commented: Activity,
      default: Activity,
    };

    const Icon = iconMap[type] || iconMap.default;
    return <Icon className="h-4 w-4" />;
  };

  const getActivityColor = (type: string) => {
    const colorMap: Record<string, string> = {
      created: "bg-blue-100 text-blue-600",
      assigned: "bg-purple-100 text-purple-600",
      status_changed: "bg-orange-100 text-orange-600",
      resolved: "bg-green-100 text-green-600",
      closed: "bg-gray-100 text-gray-600",
      reopened: "bg-red-100 text-red-600",
      default: "bg-gray-100 text-gray-600",
    };

    return colorMap[type] || colorMap.default;
  };

  if (activities.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        <Activity className="h-12 w-12 mx-auto mb-2 opacity-20" />
        <p>No activity recorded</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="relative">
        {/* Timeline line */}
        <div className="absolute left-4 top-0 bottom-0 w-px bg-border" />

        {/* Activity items */}
        <div className="space-y-4">
          {activities.map((activity, index) => (
            <div key={activity.id} className="relative flex gap-4 pl-0">
              {/* Icon */}
              <div
                className={`relative z-10 flex h-8 w-8 items-center justify-center rounded-full ${getActivityColor(
                  activity.activity_type
                )}`}
              >
                {getActivityIcon(activity.activity_type)}
              </div>

              {/* Content */}
              <div className="flex-1 pb-4">
                <div className="flex items-center justify-between mb-1">
                  <p className="font-medium text-sm">{activity.description}</p>
                  <span className="text-xs text-muted-foreground">
                    {formatDate(activity.created_at)}
                  </span>
                </div>

                {activity.created_by_name && (
                  <p className="text-sm text-muted-foreground">
                    by {activity.created_by_name}
                  </p>
                )}

                {/* Show old and new values if available */}
                {(activity.old_value || activity.new_value) && (
                  <div className="mt-2 flex gap-4 text-xs">
                    {activity.old_value && (
                      <div>
                        <span className="text-muted-foreground">From: </span>
                        <Badge variant="outline" className="text-xs">
                          {activity.old_value}
                        </Badge>
                      </div>
                    )}
                    {activity.new_value && (
                      <div>
                        <span className="text-muted-foreground">To: </span>
                        <Badge variant="outline" className="text-xs">
                          {activity.new_value}
                        </Badge>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
