"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Calendar, Plus, MapPin, User, Car } from "lucide-react";
import { transportService } from "@/services/facility/transportService";
import type { Trip } from "@/services/facility/types";
import { useToast } from "@/components/ui/use-toast";
import TripForm from "./TripForm";

export default function TripScheduler() {
  const [trips, setTrips] = useState<Trip[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [selectedTrip, setSelectedTrip] = useState<Trip | null>(null);
  const [selectedDate, setSelectedDate] = useState<string>(
    new Date().toISOString().split("T")[0]
  );
  const { toast } = useToast();

  useEffect(() => {
    loadTrips();
  }, [selectedDate]);

  const loadTrips = async () => {
    try {
      setLoading(true);
      const response = await transportService.getTrips({
        from_date: selectedDate,
        to_date: selectedDate,
        limit: 100,
      });
      setTrips(response.items);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load trips",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      scheduled: "bg-blue-500",
      in_progress: "bg-green-500",
      completed: "bg-gray-500",
      cancelled: "bg-red-500",
    };
    return colors[status] || "bg-gray-500";
  };

  const handleDateChange = (days: number) => {
    const date = new Date(selectedDate);
    date.setDate(date.getDate() + days);
    setSelectedDate(date.toISOString().split("T")[0]);
  };

  const groupedTrips = trips.reduce((acc, trip) => {
    const status = trip.status;
    if (!acc[status]) acc[status] = [];
    acc[status].push(trip);
    return acc;
  }, {} as Record<string, Trip[]>);

  return (
    <>
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5" />
                Trip Scheduler
              </CardTitle>
              <CardDescription>View and manage scheduled trips</CardDescription>
            </div>
            <Button onClick={() => setShowForm(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Schedule Trip
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {/* Date Selector */}
          <div className="flex items-center justify-between mb-6 p-4 bg-gray-50 rounded-lg">
            <Button variant="outline" onClick={() => handleDateChange(-1)}>
              ← Previous Day
            </Button>
            <div className="text-center">
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="text-lg font-semibold border rounded px-3 py-1"
              />
              <div className="text-sm text-gray-500 mt-1">
                {new Date(selectedDate).toLocaleDateString("en-US", {
                  weekday: "long",
                  year: "numeric",
                  month: "long",
                  day: "numeric",
                })}
              </div>
            </div>
            <Button variant="outline" onClick={() => handleDateChange(1)}>
              Next Day →
            </Button>
          </div>

          {/* Trip Statistics */}
          <div className="grid grid-cols-4 gap-4 mb-6">
            <Card>
              <CardContent className="pt-6">
                <div className="text-2xl font-bold">{trips.length}</div>
                <div className="text-sm text-gray-500">Total Trips</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="text-2xl font-bold text-blue-600">
                  {groupedTrips.scheduled?.length || 0}
                </div>
                <div className="text-sm text-gray-500">Scheduled</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="text-2xl font-bold text-green-600">
                  {groupedTrips.in_progress?.length || 0}
                </div>
                <div className="text-sm text-gray-500">In Progress</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="text-2xl font-bold text-gray-600">
                  {groupedTrips.completed?.length || 0}
                </div>
                <div className="text-sm text-gray-500">Completed</div>
              </CardContent>
            </Card>
          </div>

          {/* Trips Timeline */}
          {loading ? (
            <div className="text-center py-8">Loading trips...</div>
          ) : trips.length === 0 ? (
            <div className="text-center py-12">
              <Calendar className="h-12 w-12 mx-auto text-gray-400 mb-3" />
              <div className="text-lg font-semibold text-gray-600 mb-1">
                No Trips Scheduled
              </div>
              <div className="text-sm text-gray-500">
                No trips scheduled for this date
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              {trips.map((trip) => (
                <Card
                  key={trip.id}
                  className="hover:shadow-md transition-shadow cursor-pointer"
                  onClick={() => {
                    setSelectedTrip(trip);
                    setShowForm(true);
                  }}
                >
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <Badge
                            className={`${getStatusColor(trip.status)} text-white`}
                          >
                            {trip.status.replace("_", " ").toUpperCase()}
                          </Badge>
                          <span className="font-bold text-lg">
                            {trip.trip_number}
                          </span>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <div className="flex items-center gap-2 text-sm">
                              <MapPin className="h-4 w-4 text-gray-400" />
                              <div>
                                <div className="text-xs text-gray-500">From</div>
                                <div className="font-medium">
                                  {trip.start_location}
                                </div>
                              </div>
                            </div>
                            <div className="flex items-center gap-2 text-sm">
                              <MapPin className="h-4 w-4 text-gray-400" />
                              <div>
                                <div className="text-xs text-gray-500">To</div>
                                <div className="font-medium">
                                  {trip.end_location}
                                </div>
                              </div>
                            </div>
                          </div>

                          <div className="space-y-2">
                            <div className="flex items-center gap-2 text-sm">
                              <Car className="h-4 w-4 text-gray-400" />
                              <div>
                                <div className="text-xs text-gray-500">Vehicle ID</div>
                                <div className="font-medium">{trip.vehicle_id}</div>
                              </div>
                            </div>
                            <div className="flex items-center gap-2 text-sm">
                              <User className="h-4 w-4 text-gray-400" />
                              <div>
                                <div className="text-xs text-gray-500">Driver ID</div>
                                <div className="font-medium">{trip.driver_id}</div>
                              </div>
                            </div>
                          </div>
                        </div>

                        {trip.purpose && (
                          <div className="mt-3 text-sm text-gray-600">
                            <span className="font-medium">Purpose:</span> {trip.purpose}
                          </div>
                        )}

                        <div className="mt-2 flex items-center gap-4 text-xs text-gray-500">
                          <span>Passengers: {trip.passenger_count}</span>
                          {trip.distance_km && (
                            <span>Distance: {trip.distance_km} km</span>
                          )}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Trip Form Dialog */}
      {showForm && (
        <TripForm
          trip={selectedTrip}
          onClose={() => {
            setShowForm(false);
            setSelectedTrip(null);
          }}
          onSuccess={() => {
            setShowForm(false);
            setSelectedTrip(null);
            loadTrips();
          }}
        />
      )}
    </>
  );
}
