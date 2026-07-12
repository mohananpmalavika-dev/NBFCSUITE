"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { LogIn, LogOut, Search } from "lucide-react";
import { visitorService } from "@/services/facility/visitorService";
import { useToast } from "@/components/ui/use-toast";

export default function CheckInOutWidget() {
  const [passNumber, setPassNumber] = useState("");
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const handleCheckIn = async () => {
    if (!passNumber) {
      toast({
        title: "Error",
        description: "Please enter pass number",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    try {
      // Search visitor by pass number
      const response = await visitorService.getVisitors({ search: passNumber, limit: 1 });
      if (response.items.length === 0) {
        throw new Error("Visitor not found");
      }
      
      await visitorService.checkInVisitor(response.items[0].id);
      toast({
        title: "Success",
        description: `Visitor ${response.items[0].visitor_name} checked in successfully`,
      });
      setPassNumber("");
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to check in",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCheckOut = async () => {
    if (!passNumber) {
      toast({
        title: "Error",
        description: "Please enter pass number",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    try {
      const response = await visitorService.getVisitors({ search: passNumber, limit: 1 });
      if (response.items.length === 0) {
        throw new Error("Visitor not found");
      }
      
      await visitorService.checkOutVisitor(response.items[0].id);
      toast({
        title: "Success",
        description: `Visitor ${response.items[0].visitor_name} checked out successfully`,
      });
      setPassNumber("");
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to check out",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="max-w-md mx-auto">
      <CardHeader>
        <CardTitle className="text-center">Quick Check-In/Out</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="passNumber">Visitor Pass Number</Label>
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <Input
                id="passNumber"
                value={passNumber}
                onChange={(e) => setPassNumber(e.target.value)}
                placeholder="Enter pass number"
                className="pl-10"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <Button
              onClick={handleCheckIn}
              disabled={loading || !passNumber}
              className="w-full"
            >
              <LogIn className="h-4 w-4 mr-2" />
              Check In
            </Button>
            <Button
              onClick={handleCheckOut}
              disabled={loading || !passNumber}
              variant="outline"
              className="w-full"
            >
              <LogOut className="h-4 w-4 mr-2" />
              Check Out
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
