"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  LayoutDashboard, 
  AlertCircle, 
  ListChecks,
  TrendingUp
} from "lucide-react";

const collectionsNavigation = [
  {
    name: "Dashboard",
    href: "/collections",
    icon: LayoutDashboard,
  },
  {
    name: "Overdue Accounts",
    href: "/collections/overdue",
    icon: AlertCircle,
  },
  {
    name: "Collection Queue",
    href: "/collections/queue",
    icon: ListChecks,
  },
  {
    name: "Analytics",
    href: "/collections/analytics",
    icon: TrendingUp,
  },
];

export default function CollectionsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <AlertCircle className="h-8 w-8 text-orange-600" />
              <h1 className="ml-3 text-2xl font-bold text-gray-900">
                Collections Management
              </h1>
            </div>
          </div>
        </div>
      </div>

      <div className="flex">
        {/* Sidebar Navigation */}
        <div className="w-64 bg-white border-r border-gray-200 min-h-[calc(100vh-4rem)]">
          <nav className="px-4 py-6 space-y-1">
            {collectionsNavigation.map((item) => {
              const isActive = pathname === item.href || 
                (item.href !== "/collections" && pathname.startsWith(item.href));
              
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`
                    flex items-center px-4 py-3 text-sm font-medium rounded-lg
                    transition-colors duration-150
                    ${
                      isActive
                        ? "bg-orange-50 text-orange-700"
                        : "text-gray-700 hover:bg-gray-50 hover:text-gray-900"
                    }
                  `}
                >
                  <item.icon
                    className={`mr-3 h-5 w-5 ${
                      isActive ? "text-orange-700" : "text-gray-400"
                    }`}
                  />
                  {item.name}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Main Content */}
        <div className="flex-1 p-8">
          {children}
        </div>
      </div>
    </div>
  );
}
