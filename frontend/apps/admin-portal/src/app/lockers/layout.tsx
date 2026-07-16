"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Lock,
  Users,
  Wallet,
  Settings,
} from "lucide-react";

const navigation = [
  {
    name: "Dashboard",
    href: "/lockers/dashboard",
    icon: LayoutDashboard,
  },
  {
    name: "Locker Master",
    href: "/lockers/master",
    icon: Lock,
  },
  {
    name: "Allocations",
    href: "/lockers/allocations",
    icon: Users,
  },
  {
    name: "Payments",
    href: "/lockers/payments",
    icon: Wallet,
  },
];

export default function LockersLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 border-r bg-gray-50/50">
        <div className="flex h-full flex-col">
          {/* Header */}
          <div className="flex h-16 items-center border-b px-6">
            <Lock className="mr-2 h-5 w-5 text-primary" />
            <h2 className="text-lg font-semibold">Locker Management</h2>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-1 p-4">
            {navigation.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                  )}
                >
                  <item.icon className="h-4 w-4" />
                  {item.name}
                </Link>
              );
            })}
          </nav>

          {/* Footer Info */}
          <div className="border-t p-4">
            <div className="text-xs text-muted-foreground">
              <p className="font-medium">Locker Management System</p>
              <p className="mt-1">Manage locker inventory, allocations, and payments</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        {children}
      </main>
    </div>
  );
}
