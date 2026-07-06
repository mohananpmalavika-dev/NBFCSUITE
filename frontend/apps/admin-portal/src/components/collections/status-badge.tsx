/**
 * Status Badge Component
 * Reusable status indicator for various collection entities
 */

interface StatusBadgeProps {
  status: string;
  type?: "promise" | "visit" | "notice" | "case" | "settlement" | "action";
  size?: "sm" | "md" | "lg";
}

export function StatusBadge({ status, type = "action", size = "md" }: StatusBadgeProps) {
  const getColorClass = () => {
    const statusLower = status.toLowerCase();
    
    // Success states
    if (["completed", "kept", "delivered", "approved", "paid", "won"].includes(statusLower)) {
      return "bg-green-100 text-green-800";
    }
    
    // Pending/In Progress states
    if (["pending", "scheduled", "in_progress", "under_review", "filed"].includes(statusLower)) {
      return "bg-blue-100 text-blue-800";
    }
    
    // Warning states
    if (["partially_kept", "dispatched", "hearing"].includes(statusLower)) {
      return "bg-yellow-100 text-yellow-800";
    }
    
    // Error/Failed states
    if (["broken", "failed", "cancelled", "rejected", "breached", "lost", "returned"].includes(statusLower)) {
      return "bg-red-100 text-red-800";
    }
    
    // Neutral states
    return "bg-gray-100 text-gray-800";
  };

  const getSizeClass = () => {
    switch (size) {
      case "sm": return "px-2 py-0.5 text-xs";
      case "lg": return "px-4 py-2 text-base";
      default: return "px-2.5 py-1 text-sm";
    }
  };

  const formatStatus = (status: string) => {
    return status
      .split("_")
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  return (
    <span
      className={`inline-flex items-center font-medium rounded-full ${getColorClass()} ${getSizeClass()}`}
    >
      {formatStatus(status)}
    </span>
  );
}
