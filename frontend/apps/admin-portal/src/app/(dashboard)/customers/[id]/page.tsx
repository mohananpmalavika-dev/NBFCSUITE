"use client";

/**
 * Customer Details / Profile Page
 * Comprehensive customer view with tabs for all related information
 */

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import {
  ArrowLeft,
  Edit,
  Trash2,
  Ban,
  Shield,
  CreditCard,
  FileText,
  Users,
  Landmark,
  Activity,
  RefreshCw,
  MoreVertical,
  User,
  Mail,
  Phone,
  MapPin,
  Calendar,
  Briefcase,
  DollarSign,
} from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useToast } from "@/components/ui/use-toast";
import customerService from "@/services/customer.service";

export default function CustomerDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { toast } = useToast();
  const customerId = parseInt(params.id as string);
  
  const [activeTab, setActiveTab] = useState("overview");

  // Fetch complete customer 360 view
  const {
    data: customer360,
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ["customer-360", customerId],
    queryFn: () => customerService.getCustomer360View(customerId),
    enabled: !!customerId,
  });

  const customer = customer360?.customer;
  const kyc = customer360?.kyc;

  const handleBack = () => {
    router.push("/customers/list");
  };

  const handleEdit = () => {
    router.push(`/customers/${customerId}/edit`);
  };

  const handleDelete = async () => {
    if (!confirm("Are you sure you want to delete this customer?")) return;

    try {
      await customerService.deleteCustomer(customerId);
      toast({
        title: "Customer deleted",
        description: "Customer has been successfully deleted.",
      });
      router.push("/customers/list");
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to delete customer",
        variant: "destructive",
      });
    }
  };

  const handleBlacklist = async () => {
    const reason = prompt("Enter reason for blacklisting:");
    if (!reason) return;

    try {
      await customerService.blacklistCustomer(customerId, reason);
      toast({
        title: "Customer blacklisted",
        description: "Customer has been added to blacklist.",
      });
      refetch();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to blacklist customer",
        variant: "destructive",
      });
    }
  };

  if (isLoading) {
    return (
      <div className="flex flex-col gap-6 p-6">
        <Skeleton className="h-12 w-full" />
        <Skeleton className="h-64 w-full" />
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  if (!customer) {
    return (
      <div className="flex flex-col items-center justify-center h-96">
        <h2 className="text-2xl font-bold mb-2">Customer not found</h2>
        <p className="text-muted-foreground mb-4">The customer you're looking for doesn't exist.</p>
        <Button onClick={handleBack}>Go Back</Button>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={handleBack}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">{customer.full_name}</h1>
            <p className="text-muted-foreground">
              {customer.customer_code} • {customer.mobile}
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => refetch()}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Refresh
          </Button>
          <Button variant="outline" size="sm" onClick={handleEdit}>
            <Edit className="mr-2 h-4 w-4" />
            Edit
          </Button>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm">
                <MoreVertical className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuLabel>Actions</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleBlacklist}>
                <Ban className="mr-2 h-4 w-4" />
                Blacklist Customer
              </DropdownMenuItem>
              <DropdownMenuItem onClick={handleDelete} className="text-red-600">
                <Trash2 className="mr-2 h-4 w-4" />
                Delete Customer
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {/* Status Badges */}
      <div className="flex gap-2">
        <Badge variant={customer.kyc_status === "completed" ? "default" : "secondary"}>
          KYC: {customer.kyc_status.toUpperCase()}
        </Badge>
        <Badge
          variant={
            customer.risk_rating === "low"
              ? "default"
              : customer.risk_rating === "high"
              ? "destructive"
              : "secondary"
          }
        >
          Risk: {customer.risk_rating.toUpperCase()}
        </Badge>
        {customer.cibil_score && (
          <Badge variant="outline">CIBIL: {customer.cibil_score}</Badge>
        )}
        <Badge variant={customer.is_active ? "default" : "secondary"}>
          {customer.is_active ? "Active" : "Inactive"}
        </Badge>
        {customer.is_blacklisted && (
          <Badge variant="destructive">Blacklisted</Badge>
        )}
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">
            <User className="mr-2 h-4 w-4" />
            Overview
          </TabsTrigger>
          <TabsTrigger value="kyc">
            <Shield className="mr-2 h-4 w-4" />
            KYC
          </TabsTrigger>
          <TabsTrigger value="documents">
            <FileText className="mr-2 h-4 w-4" />
            Documents ({customer360?.documents?.length || 0})
          </TabsTrigger>
          <TabsTrigger value="family">
            <Users className="mr-2 h-4 w-4" />
            Family ({customer360?.family?.length || 0})
          </TabsTrigger>
          <TabsTrigger value="bank-accounts">
            <Landmark className="mr-2 h-4 w-4" />
            Bank Accounts ({customer360?.bankAccounts?.length || 0})
          </TabsTrigger>
          <TabsTrigger value="bureau">
            <CreditCard className="mr-2 h-4 w-4" />
            Credit Bureau
          </TabsTrigger>
          <TabsTrigger value="timeline">
            <Activity className="mr-2 h-4 w-4" />
            Timeline
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2">
            {/* Personal Information */}
            <Card>
              <CardHeader>
                <CardTitle>Personal Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-3">
                  <User className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="text-sm text-muted-foreground">Full Name</p>
                    <p className="font-medium">{customer.full_name}</p>
                  </div>
                </div>
                <Separator />
                <div className="flex items-center gap-3">
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="text-sm text-muted-foreground">Date of Birth</p>
                    <p className="font-medium">
                      {customer.date_of_birth
                        ? new Date(customer.date_of_birth).toLocaleDateString()
                        : "—"}
                      {customer.age && ` (${customer.age} years)`}
                    </p>
                  </div>
                </div>
                <Separator />
                <div className="flex items-center gap-3">
                  <User className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="text-sm text-muted-foreground">Gender</p>
                    <p className="font-medium capitalize">{customer.gender || "—"}</p>
                  </div>
                </div>
                <Separator />
                <div className="flex items-center gap-3">
                  <User className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="text-sm text-muted-foreground">Marital Status</p>
                    <p className="font-medium capitalize">{customer.marital_status || "—"}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Contact Information */}
            <Card>
              <CardHeader>
                <CardTitle>Contact Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-3">
                  <Phone className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="text-sm text-muted-foreground">Primary Mobile</p>
                    <p className="font-medium">{customer.mobile}</p>
                  </div>
                </div>
                <Separator />
                <div className="flex items-center gap-3">
                  <Phone className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="text-sm text-muted-foreground">Alternate Mobile</p>
                    <p className="font-medium">{customer.alternate_mobile || "—"}</p>
                  </div>
                </div>
                <Separator />
                <div className="flex items-center gap-3">
                  <Mail className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="text-sm text-muted-foreground">Email</p>
                    <p className="font-medium">{customer.email || "—"}</p>
                  </div>
                </div>
                <Separator />
                <div className="flex items-center gap-3">
                  <MapPin className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="text-sm text-muted-foreground">Location</p>
                    <p className="font-medium">
                      {customer.current_city_name && customer.current_state_name
                        ? `${customer.current_city_name}, ${customer.current_state_name}`
                        : "—"}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Identity Documents */}
            <Card>
              <CardHeader>
                <CardTitle>Identity Documents</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <p className="text-sm text-muted-foreground">PAN Number</p>
                  <div className="flex items-center gap-2">
                    <p className="font-medium font-mono">{customer.pan_number || "—"}</p>
                    {kyc?.pan_verified && (
                      <Badge variant="default" className="text-xs">Verified</Badge>
                    )}
                  </div>
                </div>
                <Separator />
                <div>
                  <p className="text-sm text-muted-foreground">Aadhaar Number</p>
                  <div className="flex items-center gap-2">
                    <p className="font-medium font-mono">
                      {customer.aadhaar_number
                        ? `XXXX-XXXX-${customer.aadhaar_number.slice(-4)}`
                        : "—"}
                    </p>
                    {kyc?.aadhaar_verified && (
                      <Badge variant="default" className="text-xs">Verified</Badge>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Professional Information */}
            <Card>
              <CardHeader>
                <CardTitle>Professional Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-3">
                  <Briefcase className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="text-sm text-muted-foreground">Occupation</p>
                    <p className="font-medium">{customer.occupation_name || "—"}</p>
                  </div>
                </div>
                <Separator />
                <div className="flex items-center gap-3">
                  <Briefcase className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="text-sm text-muted-foreground">Industry</p>
                    <p className="font-medium">{customer.industry_name || "—"}</p>
                  </div>
                </div>
                <Separator />
                <div className="flex items-center gap-3">
                  <DollarSign className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="text-sm text-muted-foreground">Monthly Income</p>
                    <p className="font-medium">
                      {customer.monthly_income
                        ? `₹${customer.monthly_income.toLocaleString()}`
                        : "—"}
                    </p>
                  </div>
                </div>
                <Separator />
                <div className="flex items-center gap-3">
                  <DollarSign className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="text-sm text-muted-foreground">Annual Income</p>
                    <p className="font-medium">
                      {customer.annual_income
                        ? `₹${customer.annual_income.toLocaleString()}`
                        : "—"}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Quick Stats */}
          <div className="grid gap-4 md:grid-cols-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Documents</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">{customer360?.documents?.length || 0}</p>
                <p className="text-xs text-muted-foreground">Uploaded</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Family Members</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">{customer360?.family?.length || 0}</p>
                <p className="text-xs text-muted-foreground">Added</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Bank Accounts</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">{customer360?.bankAccounts?.length || 0}</p>
                <p className="text-xs text-muted-foreground">Linked</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Timeline Events</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">{customer360?.timeline?.total || 0}</p>
                <p className="text-xs text-muted-foreground">Activities</p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* KYC Tab */}
        <TabsContent value="kyc">
          <Card>
            <CardHeader>
              <CardTitle>KYC Status</CardTitle>
              <CardDescription>Know Your Customer verification details</CardDescription>
            </CardHeader>
            <CardContent>
              {customer360?.kyc ? (
                <div className="space-y-4">
                  <div className="grid gap-4 md:grid-cols-2">
                    <div>
                      <p className="text-sm text-muted-foreground">Aadhaar Verification</p>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge variant={customer360.kyc.aadhaar_verified ? "default" : "secondary"}>
                          {customer360.kyc.aadhaar_verified ? "Verified" : "Not Verified"}
                        </Badge>
                        {customer360.kyc.aadhaar_verified_date && (
                          <span className="text-sm text-muted-foreground">
                            on {new Date(customer360.kyc.aadhaar_verified_date).toLocaleDateString()}
                          </span>
                        )}
                      </div>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">PAN Verification</p>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge variant={customer360.kyc.pan_verified ? "default" : "secondary"}>
                          {customer360.kyc.pan_verified ? "Verified" : "Not Verified"}
                        </Badge>
                        {customer360.kyc.pan_verified_date && (
                          <span className="text-sm text-muted-foreground">
                            on {new Date(customer360.kyc.pan_verified_date).toLocaleDateString()}
                          </span>
                        )}
                      </div>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Bank Account Verification</p>
                      <Badge variant={customer360.kyc.bank_account_verified ? "default" : "secondary"}>
                        {customer360.kyc.bank_account_verified ? "Verified" : "Not Verified"}
                      </Badge>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Video KYC</p>
                      <Badge variant={customer360.kyc.video_kyc_done ? "default" : "secondary"}>
                        {customer360.kyc.video_kyc_done ? "Completed" : "Pending"}
                      </Badge>
                    </div>
                  </div>
                  <Separator />
                  <div>
                    <p className="text-sm text-muted-foreground mb-2">Overall KYC Status</p>
                    <div className="flex items-center gap-4">
                      <Badge
                        variant={
                          customer360.kyc.overall_kyc_status === "completed"
                            ? "default"
                            : "secondary"
                        }
                      >
                        {customer360.kyc.overall_kyc_status.toUpperCase()}
                      </Badge>
                      <div className="flex-1">
                        <div className="flex items-center justify-between text-sm mb-1">
                          <span>Completion</span>
                          <span>{customer360.kyc.kyc_completion_percentage}%</span>
                        </div>
                        <div className="h-2 bg-muted rounded-full overflow-hidden">
                          <div
                            className="h-full bg-primary transition-all"
                            style={{ width: `${customer360.kyc.kyc_completion_percentage}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <p className="text-center text-muted-foreground py-8">No KYC data available</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Documents Tab */}
        <TabsContent value="documents">
          <Card>
            <CardHeader>
              <CardTitle>Document Vault</CardTitle>
              <CardDescription>All uploaded customer documents</CardDescription>
            </CardHeader>
            <CardContent>
              {customer360?.documents && customer360.documents.length > 0 ? (
                <div className="space-y-3">
                  {customer360.documents.map((doc) => (
                    <div
                      key={doc.id}
                      className="flex items-center justify-between p-4 border rounded-lg"
                    >
                      <div className="flex items-center gap-3">
                        <FileText className="h-8 w-8 text-muted-foreground" />
                        <div>
                          <p className="font-medium">{doc.document_name}</p>
                          <p className="text-sm text-muted-foreground">
                            {doc.document_type_name} • {doc.document_format.toUpperCase()}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant={doc.status === "verified" ? "default" : "secondary"}>
                          {doc.status}
                        </Badge>
                        <Button variant="outline" size="sm" asChild>
                          <a href={doc.document_url} target="_blank" rel="noopener noreferrer">
                            View
                          </a>
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-muted-foreground py-8">No documents uploaded</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Family Tab */}
        <TabsContent value="family">
          <Card>
            <CardHeader>
              <CardTitle>Family Members</CardTitle>
              <CardDescription>Customer's family and dependents</CardDescription>
            </CardHeader>
            <CardContent>
              {customer360?.family && customer360.family.length > 0 ? (
                <div className="space-y-3">
                  {customer360.family.map((member) => (
                    <div
                      key={member.id}
                      className="flex items-center justify-between p-4 border rounded-lg"
                    >
                      <div className="flex items-center gap-3">
                        <Users className="h-8 w-8 text-muted-foreground" />
                        <div>
                          <p className="font-medium">{member.name}</p>
                          <p className="text-sm text-muted-foreground">
                            {member.relationship_type_name}
                            {member.age && ` • ${member.age} years`}
                            {member.gender && ` • ${member.gender}`}
                          </p>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        {member.is_nominee && <Badge>Nominee</Badge>}
                        {member.is_dependent && <Badge variant="secondary">Dependent</Badge>}
                        {member.is_emergency_contact && (
                          <Badge variant="outline">Emergency Contact</Badge>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-muted-foreground py-8">No family members added</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Bank Accounts Tab */}
        <TabsContent value="bank-accounts">
          <Card>
            <CardHeader>
              <CardTitle>Bank Accounts</CardTitle>
              <CardDescription>Linked bank accounts for transactions</CardDescription>
            </CardHeader>
            <CardContent>
              {customer360?.bankAccounts && customer360.bankAccounts.length > 0 ? (
                <div className="space-y-3">
                  {customer360.bankAccounts.map((account) => (
                    <div
                      key={account.id}
                      className="flex items-center justify-between p-4 border rounded-lg"
                    >
                      <div className="flex items-center gap-3">
                        <Landmark className="h-8 w-8 text-muted-foreground" />
                        <div>
                          <p className="font-medium">{account.bank_name}</p>
                          <p className="text-sm text-muted-foreground">
                            {account.account_number.replace(/\d(?=\d{4})/g, "X")} •{" "}
                            {account.account_type.toUpperCase()}
                          </p>
                          <p className="text-sm text-muted-foreground">{account.ifsc_code}</p>
                        </div>
                      </div>
                      <div className="flex flex-col gap-2 items-end">
                        <div className="flex gap-2">
                          {account.is_primary && <Badge>Primary</Badge>}
                          {account.is_verified && (
                            <Badge variant="default">Verified</Badge>
                          )}
                        </div>
                        <div className="flex gap-2 text-xs text-muted-foreground">
                          {account.use_for_disbursement && <span>Disbursement</span>}
                          {account.use_for_collection && <span>Collection</span>}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-muted-foreground py-8">No bank accounts linked</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Credit Bureau Tab */}
        <TabsContent value="bureau">
          <Card>
            <CardHeader>
              <CardTitle>Credit Bureau Reports</CardTitle>
              <CardDescription>Credit score and bureau pull history</CardDescription>
            </CardHeader>
            <CardContent>
              {customer360?.bureauHistory && customer360.bureauHistory.length > 0 ? (
                <div className="space-y-4">
                  <div className="grid gap-4 md:grid-cols-3">
                    <Card>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm">Latest CIBIL Score</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <p className="text-3xl font-bold">{customer.cibil_score || "—"}</p>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm">Total Pulls</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <p className="text-3xl font-bold">{customer360.bureauHistory.length}</p>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm">Last Pulled</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <p className="text-sm">
                          {customer360.bureauHistory[0]?.request_date
                            ? new Date(customer360.bureauHistory[0].request_date).toLocaleDateString()
                            : "—"}
                        </p>
                      </CardContent>
                    </Card>
                  </div>
                  <Separator />
                  <div className="space-y-2">
                    <h4 className="font-medium">Pull History</h4>
                    {customer360.bureauHistory.map((pull) => (
                      <div key={pull.id} className="flex items-center justify-between p-3 border rounded">
                        <div>
                          <p className="font-medium">{pull.bureau_provider.toUpperCase()}</p>
                          <p className="text-sm text-muted-foreground">
                            {new Date(pull.request_date).toLocaleDateString()}
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          {pull.credit_score && (
                            <span className="font-semibold">{pull.credit_score}</span>
                          )}
                          <Badge variant={pull.status === "success" ? "default" : "destructive"}>
                            {pull.status}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <p className="text-center text-muted-foreground py-8">No bureau reports pulled</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Timeline Tab */}
        <TabsContent value="timeline">
          <Card>
            <CardHeader>
              <CardTitle>Activity Timeline</CardTitle>
              <CardDescription>Customer journey and activity history</CardDescription>
            </CardHeader>
            <CardContent>
              {customer360?.timeline?.items && customer360.timeline.items.length > 0 ? (
                <div className="space-y-4">
                  {customer360.timeline.items.map((activity) => (
                    <div key={activity.id} className="flex gap-4">
                      <div className="flex flex-col items-center">
                        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10">
                          <Activity className="h-4 w-4 text-primary" />
                        </div>
                        <div className="w-px flex-1 bg-border" />
                      </div>
                      <div className="flex-1 pb-8">
                        <div className="flex items-start justify-between">
                          <div>
                            <p className="font-medium">{activity.title}</p>
                            {activity.description && (
                              <p className="text-sm text-muted-foreground mt-1">
                                {activity.description}
                              </p>
                            )}
                          </div>
                          {activity.is_important && (
                            <Badge variant="destructive" className="ml-2">Important</Badge>
                          )}
                        </div>
                        <p className="text-xs text-muted-foreground mt-2">
                          {new Date(activity.event_date).toLocaleString()}
                          {activity.performed_by_name && ` • by ${activity.performed_by_name}`}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-muted-foreground py-8">No activities recorded</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
