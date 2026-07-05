"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  BookOpen, 
  FileText, 
  List, 
  BarChart3,
  Home
} from "lucide-react";

const accountingNavigation = [
  {
    name: "Dashboard",
    href: "/accounting",
    icon: Home,
  },
  {
    name: "Chart of Accounts",
    href: "/accounting/accounts",
    icon: BookOpen,
  },
  {
    name: "Journal Entries",
    href: "/accounting/journal-entries",
    icon: FileText,
  },
  {
    name: "General Ledger",
    href: "/accounting/general-ledger",
    icon: List,
  },
  {
    name: "Reports",
    href: "/accounting/reports",
    icon: BarChart3,
  },
];

export default function AccountingLayout({
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
              <BookOpen className="h-8 w-8 text-blue-600" />
              <h1 className="ml-3 text-2xl font-bold text-gray-900">
                Accounting & Finance
              </h1>
            </div>
          </div>
        </div>
      </div>

      <div className="flex">
        {/* Sidebar Navigation */}
        <div className="w-64 bg-white border-r border-gray-200 min-h-[calc(100vh-4rem)]">
          <nav className="px-4 py-6 space-y-1">
            {accountingNavigation.map((item) => {
              const isActive = pathname === item.href || 
                (item.href !== "/accounting" && pathname.startsWith(item.href));
              
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`
                    flex items-center px-4 py-3 text-sm font-medium rounded-lg
                    transition-colors duration-150
                    ${
                      isActive
                        ? "bg-blue-50 text-blue-700"
                        : "text-gray-700 hover:bg-gray-50 hover:text-gray-900"
                    }
                  `}
                >
                  <item.icon
                    className={`mr-3 h-5 w-5 ${
                      isActive ? "text-blue-700" : "text-gray-400"
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
