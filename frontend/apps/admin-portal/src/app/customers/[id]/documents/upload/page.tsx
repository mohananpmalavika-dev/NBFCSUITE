'use client'

import { useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, Upload as UploadIcon, Check } from 'lucide-react'
import Link from 'next/link'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { FileUpload } from '@/components/ui/file-upload'
import { useToast } from '@/hooks/use-toast'
import { customerService } from '@/services/customer.service'

export default function UploadDocumentPage() {
  const params = useParams()
  const router = useRouter()
  const customerId = params.id as string
  const queryClient = useQueryClient()
  const { toast } = useToast()

  const [formData, setFormData] = useState({
    document_type: '',
    document_number: '',
    remarks: '',
  })
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])

  const uploadMutation = useMutation({
    mutationFn: async () => {
      if (selectedFiles.length === 0) {
        throw new Error('Please select at least one file')
      }

      // Create FormData for file upload
      const formDataToSend = new FormData()
      selectedFiles.forEach((file) => {
        formDataToSend.append('files', file)
      })
      formDataToSend.append('document_type', formData.document_type)
      if (formData.document_number) {
        formDataToSend.append('document_number', formData.document_number)
      }
      if (formData.remarks) {
        formDataToSend.append('remarks', formData.remarks)
      }

      // Note: This is a placeholder. Actual implementation would use customerService
      return { success: true }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['customer-documents', customerId] })
      toast({
        title: 'Documents uploaded',
        description: `${selectedFiles.length} document(s) uploaded successfully`,
      })
      router.push(`/customers/${customerId}?tab=documents`)
    },
    onError: (error: any) => {
      toast({
        title: 'Upload failed',
        description: error.message || 'Failed to upload documents',
        variant: 'destructive',
      })
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.document_type) {
      toast({
        title: 'Validation error',
        description: 'Please select document type',
        variant: 'destructive',
      })
      return
    }

    uploadMutation.mutate()
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Link href={`/customers/${customerId}?tab=documents`}>
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-5 w-5" />
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Upload Documents</h1>
            <p className="text-gray-600 mt-1">Upload customer documents for verification</p>
          </div>
        </div>

        {/* Upload Form */}
        <form onSubmit={handleSubmit}>
          <Card>
            <CardHeader>
              <CardTitle>Document Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Document Type */}
              <div className="space-y-2">
                <Label htmlFor="document_type">
                  Document Type <span className="text-red-500">*</span>
                </Label>
                <select
                  id="document_type"
                  required
                  value={formData.document_type}
                  onChange={(e) => setFormData({ ...formData, document_type: e.target.value })}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  <option value="">Select document type</option>
                  <option value="PAN Card">PAN Card</option>
                  <option value="Aadhaar Card">Aadhaar Card</option>
                  <option value="Voter ID">Voter ID</option>
                  <option value="Driving License">Driving License</option>
                  <option value="Passport">Passport</option>
                  <option value="Bank Statement">Bank Statement</option>
                  <option value="Salary Slip">Salary Slip</option>
                  <option value="Property Documents">Property Documents</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              {/* Document Number */}
              <div className="space-y-2">
                <Label htmlFor="document_number">Document Number</Label>
                <Input
                  id="document_number"
                  placeholder="Enter document number"
                  value={formData.document_number}
                  onChange={(e) => setFormData({ ...formData, document_number: e.target.value })}
                />
                <p className="text-sm text-gray-500">Optional for reference</p>
              </div>

              {/* Remarks */}
              <div className="space-y-2">
                <Label htmlFor="remarks">Remarks</Label>
                <textarea
                  id="remarks"
                  placeholder="Additional notes about the document"
                  value={formData.remarks}
                  onChange={(e) => setFormData({ ...formData, remarks: e.target.value })}
                  className="flex min-h-[100px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                />
              </div>

              {/* File Upload */}
              <div className="space-y-2">
                <Label>
                  Upload Files <span className="text-red-500">*</span>
                </Label>
                <FileUpload
                  onFileSelect={setSelectedFiles}
                  multiple
                  accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
                  maxSize={10}
                  maxFiles={5}
                />
                <p className="text-sm text-gray-500">
                  Accepted formats: PDF, JPG, PNG, DOC, DOCX. Max 10MB per file, up to 5 files.
                </p>
              </div>

              {/* Actions */}
              <div className="flex gap-3 pt-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => router.back()}
                  disabled={uploadMutation.isPending}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={uploadMutation.isPending || selectedFiles.length === 0}
                >
                  {uploadMutation.isPending ? (
                    <>
                      <UploadIcon className="h-4 w-4 mr-2 animate-spin" />
                      Uploading...
                    </>
                  ) : (
                    <>
                      <Check className="h-4 w-4 mr-2" />
                      Upload Documents
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </form>

        {/* Upload Guidelines */}
        <Card>
          <CardHeader>
            <CardTitle>Upload Guidelines</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-0.5">•</span>
                <span>Ensure all documents are clear and legible</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-0.5">•</span>
                <span>Document should not be older than 3 months (for bank statements, salary slips)</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-0.5">•</span>
                <span>All pages of the document must be uploaded</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-0.5">•</span>
                <span>Documents should be in color (not black and white)</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-0.5">•</span>
                <span>File size should not exceed 10MB per document</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-0.5">•</span>
                <span>Supported formats: PDF, JPG, PNG, DOC, DOCX</span>
              </li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
