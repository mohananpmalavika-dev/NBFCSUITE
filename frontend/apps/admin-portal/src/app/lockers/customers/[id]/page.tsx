"use client";

import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "@/components/ui/use-toast";
import { Checkbox } from "@/components/ui/checkbox";
import {
  ArrowLeft,
  Edit,
  FileText,
  Upload,
  Download,
  Eye,
  CheckCircle,
  XCircle,
  User,
  Phone,
  Mail,
  MapPin,
  Briefcase,
  CreditCard,
  Shield,
  Users,
  UserCheck,
} from "lucide-react";
import {
  lockerCustomerService,
  CustomerCategory,
  VerificationStatus,
  KYCDocumentType,
  KYCDocumentCategory,
  type LockerCustomer,
  type LockerKYC,
} from "@/services/locker.service";
import { format } from "date-fns";

export default function CustomerProfilePage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const customerId = params.id as string;

  const [showKYCUpload, setShowKYCUpload] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [kycForm, setKycForm] = useState({
    document_type: KYCDocumentType.PAN_CARD,
    document_category: KYCDocumentCategory.IDENTITY_PROOF,
    document_number: "",
    document_file_path: "",
    issuing_authority: "",
    issue_date: "",
    expiry_date: "",
  });

  // Fetch complete customer profile
  const { data: profileData, isLoading } = useQuery({
    queryKey: ["locker-customer-profile", customerId],
    queryFn: () => lockerCustomerService.getCustomerCompleteProfile(customerId),
  });

  // Fetch KYC compliance
  const { data: kycCompliance } = useQuery({
    queryKey: ["locker-customer-kyc-compliance", customerId],
    queryFn: () => lockerCustomerService.checkKYCCompliance(customerId),
    enabled: !!customerId,
  });

  // Upload KYC mutation
  const uploadKYC = useMutation({
    mutationFn: (data: typeof kycForm) =>
      lockerCustomerService.uploadKYC({
        locker_customer_id: customerId,
        ...data,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["locker-customer-profile"] });
      queryClient.invalidateQueries({
        queryKey: ["locker-customer-kyc-compliance"],
      });
      toast({
        title: "KYC Document Uploaded",
        description: "Document uploaded successfully and pending verification.",
      });
      setShowKYCUpload(false);
      setKycForm({
        document_type: KYCDocumentType.PAN_CARD,
        document_category: KYCDocumentCategory.IDENTITY_PROOF,
        document_number: "",
        document_file_path: "",
        issuing_authority: "",
        issue_date: "",
        expiry_date: "",
      });
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to upload document",
        variant: "destructive",
      });
    },
  });

  // Verify KYC mutation
  const verifyKYC = useMutation({
    mutationFn: (data: {
      kycId: string;
      status: VerificationStatus;
      remarks?: string;
    }) =>
      lockerCustomerService.verifyKYCDocument(
        data.kycId,
        data.status,
        data.remarks
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["locker-customer-profile"] });
      queryClient.invalidateQueries({
        queryKey: ["locker-customer-kyc-compliance"],
      });
      toast({
        title: "KYC Verified",
        description: "Document verification status updated.",
      });
    },
  });

  const handleKYCUpload = (e: React.FormEvent) => {
    e.preventDefault();
    uploadKYC.mutate(kycForm);
  };

  if (isLoading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center h-64">
          <p>Loading customer profile...</p>
        </div>
      </div>
    );
  }

  const customer = profileData?.data?.customer as LockerCustomer;
  const kycDocuments = profileData?.data?.kyc_documents || [];
  const nominees = profileData?.data?.nominees || [];
  const jointHolders = profileData?.data?.joint_holders || [];
  const authorizations = profileData?.data?.authorizations || [];
  const compliance = kycCompliance?.data || {};

  if (!customer) {
    return (
      <div className="container mx-auto p-6">
        <div className="text-center">
          <p>Customer not found</p>
          <Button onClick={() => router.back()} className="mt-4">
            Go Back
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">{customer.full_name}</h1>
            <p className="text-muted-foreground">{customer.locker_customer_id}</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setShowEditDialog(true)}>
            <Edit className="mr-2 h-4 w-4" />
            Edit Profile
          </Button>
        </div>
      </div>

      {/* Status Overview */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Category</CardTitle>
          </CardHeader>
          <CardContent>
            <Badge className="text-sm">
              {customer.customer_category.replace("_", " ")}
            </Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Verification</CardTitle>
          </CardHeader>
          <CardContent>
            <Badge
              variant={
                customer.verification_status === "verified"
                  ? "default"
                  : "secondary"
              }
            >
              {customer.verification_status}
            </Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">KYC Compliance</CardTitle>
          </CardHeader>
          <CardContent>
            <Badge
              variant={compliance.is_compliant ? "default" : "destructive"}
            >
              {compliance.is_compliant ? "Compliant" : "Incomplete"}
            </Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Status</CardTitle>
          </CardHeader>
          <CardContent>
            <Badge variant={customer.status === "active" ? "default" : "secondary"}>
              {customer.status}
            </Badge>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="profile" className="space-y-4">
        <TabsList>
          <TabsTrigger value="profile">Profile</TabsTrigger>
          <TabsTrigger value="kyc">
            KYC Documents ({kycDocuments.length})
          </TabsTrigger>
          <TabsTrigger value="nominees">Nominees ({nominees.length})</TabsTrigger>
          <TabsTrigger value="joint-holders">
            Joint Holders ({jointHolders.length})
          </TabsTrigger>
          <TabsTrigger value="authorizations">
            Authorizations ({authorizations.length})
          </TabsTrigger>
        </TabsList>

        {/* Profile Tab */}
        <TabsContent value="profile" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            {/* Personal Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="h-5 w-5" />
                  Personal Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <Label className="text-muted-foreground">Full Name</Label>
                  <p className="font-medium">{customer.full_name}</p>
                </div>
                {customer.date_of_birth && (
                  <div>
                    <Label className="text-muted-foreground">Date of Birth</Label>
                    <p className="font-medium">
                      {format(new Date(customer.date_of_birth), "dd MMM yyyy")} (Age:{" "}
                      {customer.age})
                    </p>
                  </div>
                )}
                {customer.gender && (
                  <div>
                    <Label className="text-muted-foreground">Gender</Label>
                    <p className="font-medium">{customer.gender}</p>
                  </div>
                )}
                {customer.is_senior_citizen && (
                  <Badge variant="outline">Senior Citizen</Badge>
                )}
              </CardContent>
            </Card>

            {/* Contact Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Phone className="h-5 w-5" />
                  Contact Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <Label className="text-muted-foreground">Mobile Number</Label>
                  <p className="font-medium">{customer.mobile_number}</p>
                </div>
                {customer.alternate_mobile && (
                  <div>
                    <Label className="text-muted-foreground">Alternate Mobile</Label>
                    <p className="font-medium">{customer.alternate_mobile}</p>
                  </div>
                )}
                {customer.email && (
                  <div>
                    <Label className="text-muted-foreground">Email</Label>
                    <p className="font-medium">{customer.email}</p>
                  </div>
                )}
                <div className="flex gap-2">
                  {customer.sms_alerts && <Badge variant="outline">SMS</Badge>}
                  {customer.email_alerts && <Badge variant="outline">Email</Badge>}
                  {customer.whatsapp_alerts && <Badge variant="outline">WhatsApp</Badge>}
                </div>
              </CardContent>
            </Card>

            {/* Current Address */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MapPin className="h-5 w-5" />
                  Current Address
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm">
                  {customer.current_address_line1}
                  {customer.current_address_line2 && `, ${customer.current_address_line2}`}
                  <br />
                  {customer.current_city}, {customer.current_state}{" "}
                  {customer.current_pincode}
                  <br />
                  {customer.current_country}
                </p>
              </CardContent>
            </Card>

            {/* Employment Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Briefcase className="h-5 w-5" />
                  Employment Details
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {customer.occupation && (
                  <div>
                    <Label className="text-muted-foreground">Occupation</Label>
                    <p className="font-medium">{customer.occupation}</p>
                  </div>
                )}
                {customer.employer_name && (
                  <div>
                    <Label className="text-muted-foreground">Employer</Label>
                    <p className="font-medium">{customer.employer_name}</p>
                  </div>
                )}
                {customer.annual_income && (
                  <div>
                    <Label className="text-muted-foreground">Annual Income</Label>
                    <p className="font-medium">
                      ₹{customer.annual_income.toLocaleString()}
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Banking Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CreditCard className="h-5 w-5" />
                  Banking Details
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {customer.bank_account_number && (
                  <div>
                    <Label className="text-muted-foreground">Account Number</Label>
                    <p className="font-medium">{customer.bank_account_number}</p>
                  </div>
                )}
                {customer.bank_name && (
                  <div>
                    <Label className="text-muted-foreground">Bank Name</Label>
                    <p className="font-medium">{customer.bank_name}</p>
                  </div>
                )}
                {customer.bank_ifsc && (
                  <div>
                    <Label className="text-muted-foreground">IFSC Code</Label>
                    <p className="font-medium">{customer.bank_ifsc}</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Identification */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5" />
                  Identification
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {customer.pan_number && (
                  <div>
                    <Label className="text-muted-foreground">PAN</Label>
                    <p className="font-medium">{customer.pan_number}</p>
                  </div>
                )}
                {customer.aadhar_number && (
                  <div>
                    <Label className="text-muted-foreground">Aadhar</Label>
                    <p className="font-medium">{customer.aadhar_number}</p>
                  </div>
                )}
                {customer.passport_number && (
                  <div>
                    <Label className="text-muted-foreground">Passport</Label>
                    <p className="font-medium">{customer.passport_number}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* KYC Documents Tab */}
        <TabsContent value="kyc" className="space-y-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>KYC Documents</CardTitle>
                <CardDescription>
                  Compliance: {compliance.verified_documents || 0} of{" "}
                  {compliance.total_documents || 0} documents verified
                </CardDescription>
              </div>
              <Button onClick={() => setShowKYCUpload(true)}>
                <Upload className="mr-2 h-4 w-4" />
                Upload Document
              </Button>
            </CardHeader>
            <CardContent>
              {/* Compliance Status */}
              {compliance.missing_documents?.length > 0 && (
                <div className="mb-4 p-4 border border-orange-500 rounded-lg bg-orange-50">
                  <h4 className="font-semibold text-orange-800 mb-2">
                    Missing Documents:
                  </h4>
                  <ul className="list-disc list-inside text-sm text-orange-700">
                    {compliance.missing_documents.map((doc: string) => (
                      <li key={doc}>{doc.replace("_", " ")}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Documents Table */}
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Document Type</TableHead>
                    <TableHead>Number</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Expiry</TableHead>
                    <TableHead>Uploaded</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {kycDocuments.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} className="text-center">
                        No KYC documents uploaded
                      </TableCell>
                    </TableRow>
                  ) : (
                    kycDocuments.map((doc: LockerKYC) => (
                      <TableRow key={doc.id}>
                        <TableCell className="font-medium">
                          {doc.document_type.replace("_", " ")}
                        </TableCell>
                        <TableCell>{doc.document_number || "-"}</TableCell>
                        <TableCell>
                          <Badge variant="outline">
                            {doc.document_category.replace("_", " ")}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge
                            variant={
                              doc.verification_status === "verified"
                                ? "default"
                                : "secondary"
                            }
                          >
                            {doc.verification_status}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          {doc.expiry_date
                            ? format(new Date(doc.expiry_date), "dd MMM yyyy")
                            : "-"}
                        </TableCell>
                        <TableCell>
                          {format(new Date(doc.upload_date), "dd MMM yyyy")}
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-2">
                            <Button variant="ghost" size="sm">
                              <Eye className="h-4 w-4" />
                            </Button>
                            {doc.verification_status === "pending" && (
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() =>
                                  verifyKYC.mutate({
                                    kycId: doc.id,
                                    status: VerificationStatus.VERIFIED,
                                  })
                                }
                              >
                                <CheckCircle className="h-4 w-4" />
                              </Button>
                            )}
                          </div>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Other tabs content would go here */}
        <TabsContent value="nominees">
          <Card>
            <CardHeader>
              <CardTitle>Nominees</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                {nominees.length} nominee(s) registered
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="joint-holders">
          <Card>
            <CardHeader>
              <CardTitle>Joint Holders</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                {jointHolders.length} joint holder(s)
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="authorizations">
          <Card>
            <CardHeader>
              <CardTitle>Authorizations</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                {authorizations.length} authorization(s)
              </p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* KYC Upload Dialog */}
      <Dialog open={showKYCUpload} onOpenChange={setShowKYCUpload}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Upload KYC Document</DialogTitle>
            <DialogDescription>
              Upload and submit KYC document for verification
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handleKYCUpload} className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label>Document Type *</Label>
                <Select
                  value={kycForm.document_type}
                  onValueChange={(value) =>
                    setKycForm({ ...kycForm, document_type: value as KYCDocumentType })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value={KYCDocumentType.PAN_CARD}>PAN Card</SelectItem>
                    <SelectItem value={KYCDocumentType.AADHAR_CARD}>
                      Aadhar Card
                    </SelectItem>
                    <SelectItem value={KYCDocumentType.PASSPORT}>Passport</SelectItem>
                    <SelectItem value={KYCDocumentType.VOTER_ID}>Voter ID</SelectItem>
                    <SelectItem value={KYCDocumentType.DRIVING_LICENSE}>
                      Driving License
                    </SelectItem>
                    <SelectItem value={KYCDocumentType.PHOTO}>Photo</SelectItem>
                    <SelectItem value={KYCDocumentType.SIGNATURE}>
                      Signature
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Document Category *</Label>
                <Select
                  value={kycForm.document_category}
                  onValueChange={(value) =>
                    setKycForm({
                      ...kycForm,
                      document_category: value as KYCDocumentCategory,
                    })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value={KYCDocumentCategory.IDENTITY_PROOF}>
                      Identity Proof
                    </SelectItem>
                    <SelectItem value={KYCDocumentCategory.ADDRESS_PROOF}>
                      Address Proof
                    </SelectItem>
                    <SelectItem value={KYCDocumentCategory.PHOTO}>Photo</SelectItem>
                    <SelectItem value={KYCDocumentCategory.SIGNATURE}>
                      Signature
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Document Number</Label>
                <Input
                  placeholder="Enter document number"
                  value={kycForm.document_number}
                  onChange={(e) =>
                    setKycForm({ ...kycForm, document_number: e.target.value })
                  }
                />
              </div>

              <div className="space-y-2">
                <Label>Issuing Authority</Label>
                <Input
                  placeholder="Enter issuing authority"
                  value={kycForm.issuing_authority}
                  onChange={(e) =>
                    setKycForm({ ...kycForm, issuing_authority: e.target.value })
                  }
                />
              </div>

              <div className="space-y-2">
                <Label>Issue Date</Label>
                <Input
                  type="date"
                  value={kycForm.issue_date}
                  onChange={(e) =>
                    setKycForm({ ...kycForm, issue_date: e.target.value })
                  }
                />
              </div>

              <div className="space-y-2">
                <Label>Expiry Date</Label>
                <Input
                  type="date"
                  value={kycForm.expiry_date}
                  onChange={(e) =>
                    setKycForm({ ...kycForm, expiry_date: e.target.value })
                  }
                />
              </div>

              <div className="space-y-2 md:col-span-2">
                <Label>Upload File *</Label>
                <Input
                  type="file"
                  onChange={(e) => {
                    // Handle file upload
                    const file = e.target.files?.[0];
                    if (file) {
                      // In real implementation, upload file and get path
                      setKycForm({
                        ...kycForm,
                        document_file_path: `/uploads/${file.name}`,
                      });
                    }
                  }}
                />
              </div>
            </div>

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => setShowKYCUpload(false)}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={uploadKYC.isPending}>
                {uploadKYC.isPending ? "Uploading..." : "Upload Document"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
