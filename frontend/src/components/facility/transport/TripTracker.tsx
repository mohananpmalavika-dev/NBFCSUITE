"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { MapPin, Play, CheckCircle, Clock, Navigation } from "lucide-react";
import { transportService } from "@/services/facility/transportService";
import type { Trip } from "@/services/facility/types";
import { useToast } from "@/components/ui/use-toast";

export default function TripTracker() {
  const [activeTrips, setActiveTrips] = useState<Trip[]>([]);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    loadActiveTrips();
    const interval = setInterval(loadActiveTrips, 10000);
    return () => clearInterval(interval);
  }, []);

  const loadActiveTrips = async () => {
    try {
      const response = await transportService.getTrips({
        status: "in_progress",
        limit: 50,
      });
      setActiveTrips(response.items);
      setLoading(false);
    } catch (error) {
      if (!loading) {
        toast({
          title: "Error",
          description: "Failed to load active trips",
          variant: "destructive",
        });
      }
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Navigation className="h-5 w-5" />
          Live Trip Tracker
        </CardTitle>
        <CardDescription>Track vehicles currently on trips</CardDescription>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="text-center py-8">Loading...</div>
        ) : activeTrips.length === 0 ? (
          <div className="text-center py-12">
            <Navigation className="h-12 w-12 mx-auto text-gray-400 mb-3" />
            <div className="text-lg font-semibold text-gray-600 mb-1">
              No Active Trips
            </div>
            <div className="text-sm text-gray-500">
              All vehicles are currently idle
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {activeTrips.map((trip) => (
              <Card key={trip.id} className="bg-gradient-to-r from-blue-50 to-green-50">
                <CardContent className="p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <div className="font-bold text-lg">{trip.trip_number}</div>
                      <Badge className="bg-green-500 text-white mt-1">
                        <Navigation className="h-3 w-3 mr-1 animate-pulse" />
                        IN PROGRESS
                      </Badge>
                    </div>
                    <div className="text-right text-sm text-gray-600">
                      <div>Vehicle ID: {trip.vehicle_id}</div>
                      <div>Driver ID: {trip.driver_id}</div>
                    </div>
                  </div>

                  <div className="flex items-center gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <MapPin className="h-4 w-4 text-blue-500" />
                        <div className="text-sm">
                          <div className="text-xs text-gray-500">From</div>
                          <div className="font-medium">{trip.start_location}</div>
                        </div>
                      </div>
                      <div className="border-l-2 border-dashed border-gray-300 ml-2 h-4"></div>
                      <div className="flex items-center gap-2">
                        <MapPin className="h-4 w-4 text-green-500" />
                        <div className="text-sm">
                          <div className="text-xs text-gray-500">To</div>
                          <div className="font-medium">{trip.end_location}</div>
                        </div>
                      </div>
                    </div>

                    <div className="text-sm text-gray-600">
                      <div>Passengers: {trip.passenger_count}</div>
                      {trip.distance_km && <div>Distance: {trip.distance_km} km</div>}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
