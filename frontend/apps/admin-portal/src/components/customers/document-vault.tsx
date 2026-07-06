'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { 
  FileText, 
  Upload, 
  Eye, 
  CheckCircle, 
  XCircle, 
  Clock,
  AlertTriangle,
  Download,
  Trash2,
  Loader2
} from 'lucide-react'
import { useToast } from '@/components/ui/use-toast'
import { customerService } from '@/services/customer.service'
import type { CustomerDocument, DocumentStatus } from '@/types/customer.types'
import { formatDate } from '@/lib/utils'

interface DocumentVaultProps {
  customerId: string
}

export function DocumentVault({ customerId }: DocumentVaultProps) {
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false)
  const [selectedDocument, setSelectedDocument] = useState<CustomerDocument | null>(null)
  const [viewDialogOpen, setViewDialogOpen] = useState(false)

  // Fetch documents
  const { data: documents, isLoading } = useQuery({
    queryKey: ['customer-documents', customerId],
    queryFn: () => customerService.getDocuments(customerId),
  })

  // Delete document mutation
  const deleteMutation = useMutation({
    mutationFn: (documentId: number) => customerService.deleteDocument(customerId, documentId),
    onSuccess: () => {
      toast({
        title: 'Document Deleted',
        description: 'Document has been removed successfully',
      })
      queryClient.invalidateQueries({ queryKey: ['customer-documents', customerId] })
    },
    onError: (error: any) => {
      toast({
        title: 'Failed to delete',
        description: error.response?.data?.detail || 'An error occurred',
        variant: 'destructive',
      })
    },
  })

  // Verify document mutation
  const verifyMutation = useMutation({
    mutationFn: ({ documentId, status, remarks }: { documentId: number; status: 'verified' | 'rejected'; remarks?: string }) =>
      customerService.verifyDocument(customerId, documentId, status, remarks),
    onSuccess: () => {
      toast({
        title: 'Document Updated',
        description: 'Document verification status updated',
      })
      queryClient.invalidateQueries({ queryKey: ['customer-documents', customerId] })
      setSelectedDocument(null)
    },
    onError: (error: any) => {
      toast({
        title: 'Verification Failed',
        description: error.response?.data?.detail || 'An error occurred',
        variant: 'destructive',
      })
    },
  })

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'verified':
        return <CheckCircle className="h-4 w-4" />
      case 'rejected':
        return <XCircle className="h-4 w-4" />
      case 'expired':
        return <AlertTriangle className="h-4 w-4" />
      default:
        return <Clock className="h-4 w-4" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'verified':
        return 'bg-green-100 text-green-800'
      case 'rejected':
        return 'bg-red-100 text-red-800'
      case 'expired':
        return 'bg-orange-100 text-orange-800'
      default:
        return 'bg-yellow-100 text-yellow-800'
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
      </div>
    )
  }

  const documentList = documents?.data || []

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Document Vault
              </CardTitle>
              <CardDescription>
                Upload and manage customer documents
              </CardDescription>
            </div>
            <Button onClick={() => setUploadDialogOpen(true)}>
              <Upload className="h-4 w-4 mr-2" />
              Upload Document
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {documentList.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="h-12 w-12 mx-auto text-gray-400 mb-4" />
              <p className="text-gray-600 mb-4">No documents uploaded yet</p>
              <Button onClick={() => setUploadDialogOpen(true)}>
                <Upload className="h-4 w-4 mr-2" />
                Upload First Document
              </Button>
            </div>
          ) : (
            <div className="space-y-3">
              {documentList.map((doc) => (
                <div
                  key={doc.id}
                  className="flex items-center gap-4 p-4 border rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="flex-shrink-0">
                    <div className="h-12 w-12 bg-primary/10 rounded-lg flex items-center justify-center">
                      <FileText className="h-6 w-6 text-primary" />
                    </div>
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="font-medium text-gray-900 truncate">
                        {doc.document_name}
                      </h4>
                      <Badge className={`${getStatusColor(doc.status)} gap-1`}>
                        {getStatusIcon(doc.status)}
                        {doc.status}
                      </Badge>
                      {doc.is_expired && (
                        <Badge variant="destructive">Expired</Badge>
                      )}
                    </div>
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      {doc.document_type_name && (
                        <span>{doc.document_type_name}</span>
                      )}
                      {doc.document_number && (
                        <span className="font-mono">{doc.document_number}</span>
                      )}
                      <span>Uploaded {formatDate(doc.uploaded_date)}</span>
                      {doc.expiry_date && (
                        <span>Expires {formatDate(doc.expiry_date)}</span>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => {
                        setSelectedDocument(doc)
                        setViewDialogOpen(true)
                      }}
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                    
                    {doc.status === 'pending' && (
                      <>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => verifyMutation.mutate({ documentId: doc.id, status: 'verified' })}
                          disabled={verifyMutation.isPending}
                        >
                          <CheckCircle className="h-4 w-4 text-green-600" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => verifyMutation.mutate({ documentId: doc.id, status: 'rejected' })}
                          disabled={verifyMutation.isPending}
                        >
                          <XCircle className="h-4 w-4 text-red-600" />
                        </Button>
                      </>
                    )}

                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => {
                        if (confirm('Are you sure you want to delete this document?')) {
                          deleteMutation.mutate(doc.id)
                        }
                      }}
                      disabled={deleteMutation.isPending}
                    >
                      <Trash2 className="h-4 w-4 text-red-600" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Upload Dialog */}
      <UploadDocumentDialog
        open={uploadDialogOpen}
        onOpenChange={setUploadDialogOpen}
        customerId={customerId}
      />

      {/* View Document Dialog */}
      <Dialog open={viewDialogOpen} onOpenChange={setViewDialogOpen}>
        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle>Document Details</DialogTitle>
            <DialogDescription>
              {selectedDocument?.document_name}
            </DialogDescription>
          </DialogHeader>
          {selectedDocument && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Document Type</Label>
                  <p className="text-sm">{selectedDocument.document_type_name || '-'}</p>
                </div>
                <div>
                  <Label>Document Number</Label>
                  <p className="text-sm font-mono">{selectedDocument.document_number || '-'}</p>
                </div>
                <div>
                  <Label>Status</Label>
                  <Badge className={getStatusColor(selectedDocument.status)}>
                    {selectedDocument.status}
                  </Badge>
                </div>
                <div>
                  <Label>Uploaded Date</Label>
                  <p className="text-sm">{formatDate(selectedDocument.uploaded_date)}</p>
                </div>
                {selectedDocument.issue_date && (
                  <div>
                    <Label>Issue Date</Label>
                    <p className="text-sm">{formatDate(selectedDocument.issue_date)}</p>
                  </div>
                )}
                {selectedDocument.expiry_date && (
                  <div>
                    <Label>Expiry Date</Label>
                    <p className="text-sm">{formatDate(selectedDocument.expiry_date)}</p>
                  </div>
                )}
                {selectedDocument.verified_date && (
                  <div>
                    <Label>Verified Date</Label>
                    <p className="text-sm">{formatDate(selectedDocument.verified_date)}</p>
                  </div>
                )}
                {selectedDocument.verification_remarks && (
                  <div className="col-span-2">
                    <Label>Remarks</Label>
                    <p className="text-sm">{selectedDocument.verification_remarks}</p>
                  </div>
                )}
              </div>

              <div className="border rounded-lg p-4 bg-gray-50">
                <p className="text-sm text-gray-600 mb-2">Document Preview</p>
                <div className="bg-white border rounded p-8 text-center">
                  <FileText className="h-16 w-16 mx-auto text-gray-400 mb-2" />
                  <p className="text-sm text-gray-600">Preview not available</p>
                  <Button variant="outline" size="sm" className="mt-4">
                    <Download className="h-4 w-4 mr-2" />
                    Download Document
                  </Button>
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}

function UploadDocumentDialog({
  open,
  onOpenChange,
  customerId,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  customerId: string
}) {
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState({
    document_type_id: '',
    document_name: '',
    document_number: '',
    issue_date: '',
    expiry_date: '',
  })
  const [file, setFile] = useState<File | null>(null)

  const uploadMutation = useMutation({
    mutationFn: async () => {
      if (!file) throw new Error('No file selected')
      
      const data = new FormData()
      data.append('file', file)
      data.append('document_type_id', formData.document_type_id)
      data.append('document_name', formData.document_name)
      if (formData.document_number) data.append('document_number', formData.document_number)
      if (formData.issue_date) data.append('issue_date', formData.issue_date)
      if (formData.expiry_date) data.append('expiry_date', formData.expiry_date)
      
      return customerService.uploadDocument(customerId, data)
    },
    onSuccess: () => {
      toast({
        title: 'Document Uploaded',
        description: 'Document uploaded successfully',
      })
      queryClient.invalidateQueries({ queryKey: ['customer-documents', customerId] })
      onOpenChange(false)
      setFormData({
        document_type_id: '',
        document_name: '',
        document_number: '',
        issue_date: '',
        expiry_date: '',
      })
      setFile(null)
    },
    onError: (error: any) => {
      toast({
        title: 'Upload Failed',
        description: error.response?.data?.detail || 'An error occurred',
        variant: 'destructive',
      })
    },
  })

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Upload Document</DialogTitle>
          <DialogDescription>
            Upload a new document for this customer
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="doc-type">Document Type</Label>
            <Select
              value={formData.document_type_id}
              onValueChange={(value) => setFormData({ ...formData, document_type_id: value })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select document type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="1">Aadhaar Card</SelectItem>
                <SelectItem value="2">PAN Card</SelectItem>
                <SelectItem value="3">Driving License</SelectItem>
                <SelectItem value="4">Passport</SelectItem>
                <SelectItem value="5">Voter ID</SelectItem>
                <SelectItem value="6">Bank Statement</SelectItem>
                <SelectItem value="7">Salary Slip</SelectItem>
                <SelectItem value="8">Utility Bill</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="doc-name">Document Name</Label>
            <Input
              id="doc-name"
              value={formData.document_name}
              onChange={(e) => setFormData({ ...formData, document_name: e.target.value })}
              placeholder="e.g., Aadhaar Card Front"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="doc-number">Document Number (Optional)</Label>
            <Input
              id="doc-number"
              value={formData.document_number}
              onChange={(e) => setFormData({ ...formData, document_number: e.target.value })}
              placeholder="e.g., ABCD1234E"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="issue-date">Issue Date (Optional)</Label>
              <Input
                id="issue-date"
                type="date"
                value={formData.issue_date}
                onChange={(e) => setFormData({ ...formData, issue_date: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="expiry-date">Expiry Date (Optional)</Label>
              <Input
                id="expiry-date"
                type="date"
                value={formData.expiry_date}
                onChange={(e) => setFormData({ ...formData, expiry_date: e.target.value })}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="file">Upload File</Label>
            <Input
              id="file"
              type="file"
              accept=".pdf,.jpg,.jpeg,.png"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
            />
            <p className="text-sm text-gray-600">
              Accepted formats: PDF, JPG, PNG (Max 10MB)
            </p>
          </div>

          <div className="flex gap-2">
            <Button
              onClick={() => uploadMutation.mutate()}
              disabled={!file || !formData.document_name || !formData.document_type_id || uploadMutation.isPending}
              className="flex-1"
            >
              {uploadMutation.isPending && (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              )}
              Upload Document
            </Button>
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
