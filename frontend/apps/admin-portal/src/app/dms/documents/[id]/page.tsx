/**
 * Document Detail Page
 * View and manage a specific document
 */

"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { 
  FileText, 
  Download, 
  Share2,
  CheckCircle2,
  Clock,
  User,
  Calendar,
  FileType,
  HardDrive,
  AlertCircle
} from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function DocumentDetailPage() {
  // Mock document data
  const document = {
    id: 1,
    name: "Loan Agreement - LA001",
    type: "loan_agreement",
    status: "approved",
    uploadedBy: "John Doe",
    uploadedAt: "2024-01-15 10:30 AM",
    approvedBy: "Manager Name",
    approvedAt: "2024-01-15 02:45 PM",
    size: "2.5 MB",
    version: "1.0",
    description: "Loan agreement document for customer application LA001",
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "approved":
        return (
          <Badge className="bg-green-100 text-green-800 hover:bg-green-100">
            <CheckCircle2 className="h-4 w-4 mr-1" />
            Approved
          </Badge>
        );
      case "pending_approval":
        return (
          <Badge className="bg-yellow-100 text-yellow-800 hover:bg-yellow-100">
            <Clock className="h-4 w-4 mr-1" />
            Pending
          </Badge>
        );
      default:
        return <Badge>{status}</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold">{document.name}</h1>
          <p className="text-muted-foreground mt-2">
            Document ID: {document.id}
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Share2 className="h-4 w-4 mr-2" />
            Share
          </Button>
          <Button>
            <Download className="h-4 w-4 mr-2" />
            Download
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <div className="flex justify-between items-start">
            <div>
              <CardTitle>Document Information</CardTitle>
              <CardDescription>Basic details and metadata</CardDescription>
            </div>
            {getStatusBadge(document.status)}
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid gap-6 md:grid-cols-2">
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <FileType className="h-5 w-5 text-muted-foreground mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm font-medium">Document Type</p>
                  <p className="text-sm text-muted-foreground">
                    {document.type.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <HardDrive className="h-5 w-5 text-muted-foreground mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm font-medium">File Size</p>
                  <p className="text-sm text-muted-foreground">{document.size}</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <FileText className="h-5 w-5 text-muted-foreground mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm font-medium">Version</p>
                  <p className="text-sm text-muted-foreground">{document.version}</p>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <User className="h-5 w-5 text-muted-foreground mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm font-medium">Uploaded By</p>
                  <p className="text-sm text-muted-foreground">{document.uploadedBy}</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <Calendar className="h-5 w-5 text-muted-foreground mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm font-medium">Upload Date</p>
                  <p className="text-sm text-muted-foreground">{document.uploadedAt}</p>
                </div>
              </div>

              {document.status === "approved" && (
                <>
                  <div className="flex items-start gap-3">
                    <CheckCircle2 className="h-5 w-5 text-green-500 mt-0.5" />
                    <div className="flex-1">
                      <p className="text-sm font-medium">Approved By</p>
                      <p className="text-sm text-muted-foreground">{document.approvedBy}</p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3">
                    <Calendar className="h-5 w-5 text-muted-foreground mt-0.5" />
                    <div className="flex-1">
                      <p className="text-sm font-medium">Approval Date</p>
                      <p className="text-sm text-muted-foreground">{document.approvedAt}</p>
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>

          {document.description && (
            <>
              <Separator className="my-4" />
              <div>
                <p className="text-sm font-medium mb-2">Description</p>
                <p className="text-sm text-muted-foreground">{document.description}</p>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      <Tabs defaultValue="preview" className="w-full">
        <TabsList>
          <TabsTrigger value="preview">Preview</TabsTrigger>
          <TabsTrigger value="history">History</TabsTrigger>
          <TabsTrigger value="permissions">Permissions</TabsTrigger>
        </TabsList>

        <TabsContent value="preview" className="space-y-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-center h-96 border-2 border-dashed rounded-lg">
                <div className="text-center">
                  <FileText className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <p className="text-sm text-muted-foreground">
                    Document preview will be displayed here
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="history" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Version History</CardTitle>
              <CardDescription>Track all changes and updates</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-start gap-3 pb-4 border-b">
                  <CheckCircle2 className="h-5 w-5 text-green-500 mt-0.5" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">Document Approved</p>
                    <p className="text-xs text-muted-foreground">
                      {document.approvedAt} by {document.approvedBy}
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <Clock className="h-5 w-5 text-blue-500 mt-0.5" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">Document Uploaded</p>
                    <p className="text-xs text-muted-foreground">
                      {document.uploadedAt} by {document.uploadedBy}
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="permissions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Access Permissions</CardTitle>
              <CardDescription>Manage who can view or edit this document</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center gap-3">
                    <User className="h-5 w-5 text-muted-foreground" />
                    <div>
                      <p className="text-sm font-medium">Owner</p>
                      <p className="text-xs text-muted-foreground">{document.uploadedBy}</p>
                    </div>
                  </div>
                  <Badge>Full Access</Badge>
                </div>
                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center gap-3">
                    <User className="h-5 w-5 text-muted-foreground" />
                    <div>
                      <p className="text-sm font-medium">Approver</p>
                      <p className="text-xs text-muted-foreground">{document.approvedBy}</p>
                    </div>
                  </div>
                  <Badge variant="outline">View & Approve</Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
