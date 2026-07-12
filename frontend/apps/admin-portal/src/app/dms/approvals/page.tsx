/**
 * Approvals Page
 * Manage document approvals and workflows
 */

"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Clock, 
  CheckCircle2, 
  XCircle,
  FileText,
  Eye,
  ThumbsUp,
  ThumbsDown,
  AlertCircle
} from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

const mockPendingApprovals = [
  {
    id: 1,
    documentName: "KYC Document - KYC123",
    submittedBy: "Jane Smith",
    submittedAt: "2024-01-15 09:15 AM",
    priority: "high",
    type: "kyc_document",
  },
  {
    id: 2,
    documentName: "Loan Application - LA002",
    submittedBy: "Robert Brown",
    submittedAt: "2024-01-15 08:30 AM",
    priority: "medium",
    type: "loan_application",
  },
  {
    id: 3,
    documentName: "Financial Statement - FS456",
    submittedBy: "Emily Davis",
    submittedAt: "2024-01-14 05:20 PM",
    priority: "low",
    type: "financial_statement",
  },
];

const mockApprovedDocuments = [
  {
    id: 4,
    documentName: "Loan Agreement - LA001",
    submittedBy: "John Doe",
    approvedAt: "2024-01-15 02:45 PM",
    approvedBy: "Manager Name",
    type: "loan_agreement",
  },
];

const mockRejectedDocuments = [
  {
    id: 5,
    documentName: "Identity Proof - Customer 456",
    submittedBy: "Sarah Wilson",
    rejectedAt: "2024-01-14 03:10 PM",
    rejectedBy: "Compliance Officer",
    reason: "Document quality insufficient",
    type: "identity_proof",
  },
];

export default function ApprovalsPage() {
  const [activeTab, setActiveTab] = useState("pending");

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case "high":
        return <Badge className="bg-red-100 text-red-800 hover:bg-red-100">High</Badge>;
      case "medium":
        return <Badge className="bg-yellow-100 text-yellow-800 hover:bg-yellow-100">Medium</Badge>;
      case "low":
        return <Badge className="bg-blue-100 text-blue-800 hover:bg-blue-100">Low</Badge>;
      default:
        return <Badge>{priority}</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Document Approvals</h1>
        <p className="text-muted-foreground mt-2">
          Review and manage document approval requests
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Approvals</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockPendingApprovals.length}</div>
            <p className="text-xs text-muted-foreground">
              Awaiting your review
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Approved Today</CardTitle>
            <CheckCircle2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">12</div>
            <p className="text-xs text-muted-foreground">
              +3 from yesterday
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Rejected This Week</CardTitle>
            <XCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">5</div>
            <p className="text-xs text-muted-foreground">
              -2 from last week
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList>
          <TabsTrigger value="pending">
            <Clock className="h-4 w-4 mr-2" />
            Pending ({mockPendingApprovals.length})
          </TabsTrigger>
          <TabsTrigger value="approved">
            <CheckCircle2 className="h-4 w-4 mr-2" />
            Approved
          </TabsTrigger>
          <TabsTrigger value="rejected">
            <XCircle className="h-4 w-4 mr-2" />
            Rejected
          </TabsTrigger>
        </TabsList>

        <TabsContent value="pending" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Pending Approvals</CardTitle>
              <CardDescription>Documents awaiting your review and approval</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Document</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Submitted By</TableHead>
                    <TableHead>Submitted At</TableHead>
                    <TableHead>Priority</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {mockPendingApprovals.map((doc) => (
                    <TableRow key={doc.id}>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <FileText className="h-4 w-4 text-blue-500" />
                          <span className="font-medium">{doc.documentName}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <span className="text-sm text-muted-foreground">
                          {doc.type.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
                        </span>
                      </TableCell>
                      <TableCell>{doc.submittedBy}</TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {doc.submittedAt}
                      </TableCell>
                      <TableCell>{getPriorityBadge(doc.priority)}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button variant="outline" size="sm">
                            <Eye className="h-4 w-4 mr-1" />
                            View
                          </Button>
                          <Button variant="default" size="sm" className="bg-green-600 hover:bg-green-700">
                            <ThumbsUp className="h-4 w-4 mr-1" />
                            Approve
                          </Button>
                          <Button variant="destructive" size="sm">
                            <ThumbsDown className="h-4 w-4 mr-1" />
                            Reject
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="approved" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Approved Documents</CardTitle>
              <CardDescription>Recently approved documents</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Document</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Submitted By</TableHead>
                    <TableHead>Approved By</TableHead>
                    <TableHead>Approved At</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {mockApprovedDocuments.map((doc) => (
                    <TableRow key={doc.id}>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <FileText className="h-4 w-4 text-green-500" />
                          <span className="font-medium">{doc.documentName}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <span className="text-sm text-muted-foreground">
                          {doc.type.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
                        </span>
                      </TableCell>
                      <TableCell>{doc.submittedBy}</TableCell>
                      <TableCell>{doc.approvedBy}</TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {doc.approvedAt}
                      </TableCell>
                      <TableCell className="text-right">
                        <Button variant="outline" size="sm">
                          <Eye className="h-4 w-4 mr-1" />
                          View
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="rejected" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Rejected Documents</CardTitle>
              <CardDescription>Documents that were rejected with reasons</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Document</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Submitted By</TableHead>
                    <TableHead>Rejected By</TableHead>
                    <TableHead>Reason</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {mockRejectedDocuments.map((doc) => (
                    <TableRow key={doc.id}>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <FileText className="h-4 w-4 text-red-500" />
                          <span className="font-medium">{doc.documentName}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <span className="text-sm text-muted-foreground">
                          {doc.type.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
                        </span>
                      </TableCell>
                      <TableCell>{doc.submittedBy}</TableCell>
                      <TableCell>{doc.rejectedBy}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <AlertCircle className="h-4 w-4 text-red-500" />
                          <span className="text-sm text-muted-foreground">{doc.reason}</span>
                        </div>
                      </TableCell>
                      <TableCell className="text-right">
                        <Button variant="outline" size="sm">
                          <Eye className="h-4 w-4 mr-1" />
                          View
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
