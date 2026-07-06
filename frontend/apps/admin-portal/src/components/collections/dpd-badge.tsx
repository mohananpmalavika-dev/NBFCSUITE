/**
 * DPD Badge Component
 * Visual indicator for Days Past Due
 */

interface DPDBadgeProps {
  dpd: number;
  size?: "sm" | "md" | "lg";
  showLabel?: boolean;
}

export function DPDBadge({ dpd, size = "md", showLabel = true }: DPDBadgeProps) {
  const getColorClass = () => {
    if (dpd === 0) return "bg-green-100 text-green-800";
    if (dpd <= 30) return "bg-yellow-100 text-yellow-800";
    if (dpd <= 60) return "bg-orange-100 text-orange-800";
    if (dpd <= 90) return "bg-red-100 text-red-800";
    return "bg-gray-100 text-gray-800"; // NPA
  };

  const getSizeClass = () => {
    switch (size) {
      case "sm": return "px-2 py-0.5 text-xs";
      case "lg": return "px-4 py-2 text-base";
      default: return "px-2.5 py-1 text-sm";
    }
  };

  const getLabel = () => {
    if (!showLabel) return `${dpd}`;
    if (dpd === 0) return "Current";
    if (dpd >= 90) return `${dpd} DPD (NPA)`;
    return `${dpd} DPD`;
  };

  return (
    <span
      className={`inline-flex items-center font-medium rounded-full ${getColorClass()} ${getSizeClass()}`}
    >
      {getLabel()}
    </span>
  );
}
