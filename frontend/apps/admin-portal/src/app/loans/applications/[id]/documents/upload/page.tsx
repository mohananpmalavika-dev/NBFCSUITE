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

export default function UploadLoanDocumentPage() {
  const params = useParams()
  const router = useRouter()
  const applicationId = params.id as string
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

      return { success: true }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['loan-documents', applicationId] })
      toast({
        title: 'Documents uploaded',
        description: `${selectedFiles.length} document(s) uploaded successfully`,
      })
      router.push(`/loans/applications/${applicationId}?tab=documents`)
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
          <Link href={`/loans/applications/${applicationId}?tab=documents`}>
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-5 w-5" />
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Upload Loan Documents</h1>
            <p className="text-gray-600 mt-1">Upload required documents for loan application</p>
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
                  <optgroup label="Identity Documents">
                    <option value="PAN Card">PAN Card</option>
                    <option value="Aadhaar Card">Aadhaar Card</option>
                    <option value="Passport">Passport</option>
                    <option value="Driving License">Driving License</option>
                    <option value="Voter ID">Voter ID</option>
                  </optgroup>
                  <optgroup label="Income Documents">
                    <option value="Salary Slip">Salary Slip (Last 3 months)</option>
                    <option value="Form 16">Form 16</option>
                    <option value="ITR">Income Tax Returns</option>
                    <option value="Bank Statement">Bank Statement (Last 6 months)</option>
                  </optgroup>
                  <optgroup label="Address Proof">
                    <option value="Utility Bill">Utility Bill</option>
                    <option value="Rent Agreement">Rent Agreement</option>
                    <option value="Property Documents">Property Documents</option>
                  </optgroup>
                  <optgroup label="Business Documents">
                    <option value="Business Registration">Business Registration</option>
                    <option value="GST Certificate">GST Certificate</option>
                    <option value="Financial Statements">Financial Statements</option>
                    <option value="Balance Sheet">Balance Sheet</option>
                  </optgroup>
                  <optgroup label="Collateral Documents">
                    <option value="Property Papers">Property Papers</option>
                    <option value="Vehicle RC">Vehicle RC</option>
                    <option value="Valuation Report">Valuation Report</option>
                  </optgroup>
                  <optgroup label="Other">
                    <option value="Application Form">Application Form</option>
                    <option value="Photograph">Photograph</option>
                    <option value="Other">Other</option>
                  </optgroup>
                </select>
              </div>

              {/* Document Number */}
              <div className="space-y-2">
                <Label htmlFor="document_number">Document Number</Label>
                <Input
                  id="document_number"
                  placeholder="Enter document number or reference"
                  value={formData.document_number}
                  onChange={(e) => setFormData({ ...formData, document_number: e.target.value })}
                />
                <p className="text-sm text-gray-500">Optional for tracking</p>
              </div>

              {/* Remarks */}
              <div className="space-y-2">
                <Label htmlFor="remarks">Remarks</Label>
                <textarea
                  id="remarks"
                  placeholder="Additional notes or comments"
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
                  maxFiles={10}
                />
                <p className="text-sm text-gray-500">
                  Accepted formats: PDF, JPG, PNG, DOC, DOCX. Max 10MB per file, up to 10 files.
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

        {/* Document Checklist */}
        <Card>
          <CardHeader>
            <CardTitle>Required Documents Checklist</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h4 className="font-semibold text-sm mb-2">Mandatory Documents:</h4>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li className="flex items-start gap-2">
                    <span className="text-red-600 mt-0.5">•</span>
                    <span>PAN Card (for all applicants and co-applicants)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-red-600 mt-0.5">•</span>
                    <span>Aadhaar Card (both sides)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-red-600 mt-0.5">•</span>
                    <span>Bank Statement (Last 6 months)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-red-600 mt-0.5">•</span>
                    <span>Salary Slips (Last 3 months) OR ITR (Last 2 years)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-red-600 mt-0.5">•</span>
                    <span>Passport size photographs</span>
                  </li>
                </ul>
              </div>

              <div>
                <h4 className="font-semibold text-sm mb-2">Additional Documents (if applicable):</h4>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li className="flex items-start gap-2">
                    <span className="text-blue-600 mt-0.5">•</span>
                    <span>Property documents (for secured loans)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-blue-600 mt-0.5">•</span>
                    <span>Business registration documents (for self-employed)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-blue-600 mt-0.5">•</span>
                    <span>GST returns (for business loans)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-blue-600 mt-0.5">•</span>
                    <span>Valuation report (for property/gold loans)</span>
                  </li>
                </ul>
              </div>

              <div className="pt-4 border-t">
                <h4 className="font-semibold text-sm mb-2">Document Guidelines:</h4>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li className="flex items-start gap-2">
                    <span className="text-green-600 mt-0.5">✓</span>
                    <span>All documents must be clear and legible</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-600 mt-0.5">✓</span>
                    <span>Documents should be recent (not older than stated period)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-600 mt-0.5">✓</span>
                    <span>Upload all pages of multi-page documents</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-600 mt-0.5">✓</span>
                    <span>Ensure no information is cut off or obscured</span>
                  </li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
