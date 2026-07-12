"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Building2, Calendar, User, Phone } from "lucide-react";
import type { Visitor } from "@/services/facility/types";

interface VisitorBadgeProps {
  visitor: Visitor;
}

export default function VisitorBadge({ visitor }: VisitorBadgeProps) {
  return (
    <Card className="w-96 border-4 border-blue-600">
      <CardContent className="p-6">
        <div className="text-center mb-4">
          <div className="text-xs text-gray-500 uppercase">Visitor Pass</div>
          <div className="text-3xl font-bold text-blue-600">{visitor.visitor_pass_number}</div>
        </div>

        <div className="space-y-3">
          <div>
            <div className="text-xs text-gray-500 uppercase">Visitor Name</div>
            <div className="text-xl font-bold">{visitor.visitor_name}</div>
          </div>

          {visitor.company_name && (
            <div className="flex items-center gap-2">
              <Building2 className="h-4 w-4 text-gray-400" />
              <span className="text-sm">{visitor.company_name}</span>
            </div>
          )}

          <div className="flex items-center gap-2">
            <User className="h-4 w-4 text-gray-400" />
            <span className="text-sm">Host: {visitor.host_employee_name}</span>
          </div>

          <div className="flex items-center gap-2">
            <Calendar className="h-4 w-4 text-gray-400" />
            <span className="text-sm">{new Date(visitor.visit_date).toLocaleDateString()}</span>
          </div>

          <div className="flex items-center gap-2">
            <Phone className="h-4 w-4 text-gray-400" />
            <span className="text-sm">{visitor.mobile_number}</span>
          </div>

          <div className="pt-2 border-t">
            <Badge className="w-full justify-center text-sm py-2">
              {visitor.visitor_type.toUpperCase()}
            </Badge>
          </div>
        </div>

        <div className="mt-4 text-xs text-center text-gray-500">
          Please wear this badge at all times
        </div>
      </CardContent>
    </Card>
  );
}
