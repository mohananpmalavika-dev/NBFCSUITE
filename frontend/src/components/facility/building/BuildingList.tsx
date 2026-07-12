"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Plus, Building2, Edit, Trash2, Search, Eye } from "lucide-react";
import { buildingService } from "@/services/facility/buildingService";
import type { Building } from "@/services/facility/types";
import { useToast } from "@/components/ui/use-toast";
import BuildingForm from "./BuildingForm";
import BuildingDetails from "./BuildingDetails";

export default function BuildingList() {
  const [buildings, setBuildings] = useState<Building[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  const [selectedBuilding, setSelectedBuilding] = useState<Building | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterType, setFilterType] = useState<string>("all");
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const { toast } = useToast();

  useEffect(() => {
    loadBuildings();
  }, []);

  const loadBuildings = async () => {
    try {
      setLoading(true);
      const params: any = { limit: 100 };
      if (filterType !== "all") params.building_type = filterType;
      if (filterStatus !== "all") params.status = filterStatus;
      if (searchTerm) params.search = searchTerm;

      const response = await buildingService.getBuildings(params);
      setBuildings(response.items);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load buildings",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      loadBuildings();
    }, 300);
    return () => clearTimeout(timer);
  }, [searchTerm, filterType, filterStatus]);

  const handleEdit = (building: Building) => {
    setSelectedBuilding(building);
    setShowForm(true);
  };

  const handleView = (building: Building) => {
    setSelectedBuilding(building);
    setShowDetails(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this building?")) return;

    try {
      await buildingService.deleteBuilding(id);
      toast({
        title: "Success",
        description: "Building deleted successfully",
      });
      loadBuildings();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.message || "Failed to delete building",
        variant: "destructive",
      });
    }
  };

  const handleFormSuccess = () => {
    setShowForm(false);
    setSelectedBuilding(null);
    loadBuildings();
  };

  const getBuildingTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      office: "Office",
      warehouse: "Warehouse",
      factory: "Factory",
      retail: "Retail",
      residential: "Residential",
      mixed_use: "Mixed Use",
    };
    return labels[type] || type;
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      active: "bg-green-500",
      under_construction: "bg-yellow-500",
      maintenance: "bg-orange-500",
      inactive: "bg-gray-500",
    };
    return colors[status] || "bg-gray-500";
  };

  return (
    <>
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Building2 className="h-5 w-5" />
                Building Management
              </CardTitle>
              <CardDescription>
                Manage buildings, floors, and rooms
              </CardDescription>
            </div>
            <Button onClick={() => setShowForm(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Add Building
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {/* Filters */}
          <div className="flex gap-4 mb-6">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search buildings..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select value={filterType} onValueChange={setFilterType}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Building Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="office">Office</SelectItem>
                <SelectItem value="warehouse">Warehouse</SelectItem>
                <SelectItem value="factory">Factory</SelectItem>
                <SelectItem value="retail">Retail</SelectItem>
                <SelectItem value="residential">Residential</SelectItem>
                <SelectItem value="mixed_use">Mixed Use</SelectItem>
              </SelectContent>
            </Select>
            <Select value={filterStatus} onValueChange={setFilterStatus}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="under_construction">Under Construction</SelectItem>
                <SelectItem value="maintenance">Maintenance</SelectItem>
                <SelectItem value="inactive">Inactive</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Buildings Table */}
          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : buildings.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No buildings found. Add your first building to get started.
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Code</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Location</TableHead>
                  <TableHead>Floors</TableHead>
                  <TableHead>Area (sqft)</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {buildings.map((building) => (
                  <TableRow key={building.id}>
                    <TableCell className="font-medium">
                      {building.building_code}
                    </TableCell>
                    <TableCell>{building.building_name}</TableCell>
                    <TableCell>
                      <Badge variant="outline">
                        {getBuildingTypeLabel(building.building_type)}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {building.city && building.state
                        ? `${building.city}, ${building.state}`
                        : "-"}
                    </TableCell>
                    <TableCell>{building.total_floors}</TableCell>
                    <TableCell>
                      {building.total_area_sqft
                        ? building.total_area_sqft.toLocaleString()
                        : "-"}
                    </TableCell>
                    <TableCell>
                      <Badge
                        className={`${getStatusColor(building.status)} text-white`}
                      >
                        {building.status.replace("_", " ").toUpperCase()}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleView(building)}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleEdit(building)}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(building.id)}
                        >
                          <Trash2 className="h-4 w-4 text-red-500" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Building Form Dialog */}
      {showForm && (
        <BuildingForm
          building={selectedBuilding}
          onClose={() => {
            setShowForm(false);
            setSelectedBuilding(null);
          }}
          onSuccess={handleFormSuccess}
        />
      )}

      {/* Building Details Dialog */}
      {showDetails && selectedBuilding && (
        <BuildingDetails
          building={selectedBuilding}
          onClose={() => {
            setShowDetails(false);
            setSelectedBuilding(null);
          }}
          onEdit={() => {
            setShowDetails(false);
            setShowForm(true);
          }}
        />
      )}
    </>
  );
}
