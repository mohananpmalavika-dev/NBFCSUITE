'use client'

/**
 * XBRL Generation Page
 * Generate and download XBRL documents for RBI submission
 */

import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { FileCode, Download, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import { rbiReturnsService } from '@/services/rbi-returns.service'
import { toast } from '@/components/ui/use-toast'
import type { XBRLGenerateRequest } from '@/types/rbi-returns.types'

export default function XBRLGenerationPage() {
  const [returnType, setReturnType] = useState('nbs_7_monthly')
  const [returnId, setReturnId] = useState('')
  const [taxonomy, setTaxonomy] = useState('rbi_nbfc_2024')
  const [entityId, setEntityId] = useState('')
  const [entityName, setEntityName] = useState('')
  const [generatedDoc, setGeneratedDoc] = useState<any>(null)

  // Fetch NBS-7 returns for selection
  const { data: nbs7Returns } = useQuery({
    queryKey: ['nbs7-returns-for-xbrl'],
    queryFn: () => rbiReturnsService.listNBS7Returns({ status: 'approved', limit: 20 }),
    enabled: returnType.includes('nbs_7'),
  })

  // Fetch statutory returns for selection
  const { data: statutoryReturns } = useQuery({
    queryKey: ['statutory-returns-for-xbrl'],
    queryFn: () => rbiReturnsService.listStatutoryReturns({ status: 'approved', limit: 20 }),
    enabled: !returnType.includes('nbs_7'),
  })

  // Generate XBRL mutation
  const generateMutation = useMutation({
    mutationFn: (request: XBRLGenerateRequest) =>
      rbiReturnsService.generateXBRL(request),
    onSuccess: (data) => {
      toast({
        title: 'XBRL Generated',
        description: `XBRL document ${data.document_number} generated successfully`,
      })
      setGeneratedDoc(data)
    },
    onError: (error: any) => {
      toast({
        title: 'Generation Failed',
        description: error.response?.data?.error?.message || 'Failed to generate XBRL',
        variant: 'destructive',
      })
    },
  })

  const handleGenerate = () => {
    if (!returnId || !entityId || !entityName) {
      toast({
        title: 'Validation Error',
        description: 'Please fill all required fields',
        variant: 'destructive',
      })
      return
    }

    const request: XBRLGenerateRequest = {
      return_type: returnType,
      return_id: returnId,
      taxonomy_version: taxonomy,
      entity_identifier: entityId,
      entity_name: entityName,
      include_validation: true,
    }

    generateMutation.mutate(request)
  }

  const handleDownload = async (docId: string) => {
    try {
      await rbiReturnsService.downloadXBRL(docId)
      toast({
        title: 'Download Started',
        description: 'XBRL XML file is being downloaded',
      })
    } catch (error) {
      toast({
        title: 'Download Failed',
        description: 'Failed to download XBRL file',
        variant: 'destructive',
      })
    }
  }

  const availableReturns = returnType.includes('nbs_7') ? nbs7Returns : statutoryReturns

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">XBRL Generation</h1>
        <p className="text-muted-foreground">
          Generate XBRL documents for RBI electronic submission
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Generation Form */}
        <Card>
          <CardHeader>
            <CardTitle>Generate New XBRL Document</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="return_type">
                Return Type <span className="text-red-500">*</span>
              </Label>
              <Select value={returnType} onValueChange={setReturnType}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="nbs_7_monthly">NBS-7 Monthly</SelectItem>
                  <SelectItem value="nbs_7_quarterly">NBS-7 Quarterly</SelectItem>
                  <SelectItem value="alm_return">ALM Return</SelectItem>
                  <SelectItem value="npa_return">NPA Return</SelectItem>
                  <SelectItem value="exposure_return">Exposure Return</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="return_id">
                Select Return <span className="text-red-500">*</span>
              </Label>
              <Select value={returnId} onValueChange={setReturnId}>
                <SelectTrigger>
                  <SelectValue placeholder="Choose an approved return" />
                </SelectTrigger>
                <SelectContent>
                  {availableReturns?.length === 0 ? (
                    <div className="p-2 text-sm text-muted-foreground">
                      No approved returns available
                    </div>
                  ) : (
                    availableReturns?.map((ret: any) => (
                      <SelectItem key={ret.id} value={ret.id}>
                        {ret.return_number} - {ret.reporting_period}
                      </SelectItem>
                    ))
                  )}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="taxonomy">
                XBRL Taxonomy <span className="text-red-500">*</span>
              </Label>
              <Select value={taxonomy} onValueChange={setTaxonomy}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="rbi_nbfc_2024">RBI NBFC 2024</SelectItem>
                  <SelectItem value="rbi_nbfc_2023">RBI NBFC 2023</SelectItem>
                  <SelectItem value="rbi_nbfc_nd_si">
                    RBI NBFC-ND-SI (Non-Deposit Systemically Important)
                  </SelectItem>
                  <SelectItem value="rbi_nbfc_d">RBI NBFC-D (Deposit Taking)</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-xs text-muted-foreground">
                Select the RBI taxonomy version as per guidelines
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="entity_id">
                Entity Identifier <span className="text-red-500">*</span>
              </Label>
              <Input
                id="entity_id"
                placeholder="e.g., NBFC123456"
                value={entityId}
                onChange={(e) => setEntityId(e.target.value)}
              />
              <p className="text-xs text-muted-foreground">
                RBI registration number or entity ID
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="entity_name">
                Entity Name <span className="text-red-500">*</span>
              </Label>
              <Input
                id="entity_name"
                placeholder="e.g., ABC NBFC Limited"
                value={entityName}
                onChange={(e) => setEntityName(e.target.value)}
              />
            </div>

            <div className="rounded-lg border p-4 bg-blue-50">
              <p className="text-sm text-blue-900 font-medium mb-2">What is XBRL?</p>
              <p className="text-xs text-blue-700">
                eXtensible Business Reporting Language (XBRL) is the standard format for
                electronic regulatory reporting to RBI. The generated XML file can be directly
                uploaded to the RBI COSMOS portal.
              </p>
            </div>

            <Button
              className="w-full"
              onClick={handleGenerate}
              disabled={generateMutation.isPending || !returnId}
            >
              {generateMutation.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <FileCode className="h-4 w-4 mr-2" />
                  Generate XBRL
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Generated Document */}
        <Card>
          <CardHeader>
            <CardTitle>Generated Document</CardTitle>
          </CardHeader>
          <CardContent>
            {!generatedDoc ? (
              <div className="text-center py-12">
                <FileCode className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground">
                  Fill the form and generate XBRL document
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="p-4 rounded-lg border bg-green-50">
                  <div className="flex items-center gap-2 mb-2">
                    {generatedDoc.is_valid ? (
                      <CheckCircle className="h-5 w-5 text-green-600" />
                    ) : (
                      <AlertCircle className="h-5 w-5 text-red-600" />
                    )}
                    <span className="font-medium">
                      {generatedDoc.is_valid ? 'Validation Passed' : 'Validation Failed'}
                    </span>
                  </div>
                  {generatedDoc.is_valid ? (
                    <p className="text-sm text-green-700">
                      XBRL document is valid and ready for submission
                    </p>
                  ) : (
                    <p className="text-sm text-red-700">
                      Please fix validation errors before submitting
                    </p>
                  )}
                </div>

                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Document Number:</span>
                    <span className="font-medium">{generatedDoc.document_number}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Return Type:</span>
                    <Badge>{generatedDoc.return_type}</Badge>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Taxonomy:</span>
                    <span className="font-medium">{generatedDoc.taxonomy_version}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Period:</span>
                    <span className="font-medium">{generatedDoc.reporting_period}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Entity:</span>
                    <span className="font-medium">{generatedDoc.entity_name}</span>
                  </div>
                  {generatedDoc.xbrl_file_size && (
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">File Size:</span>
                      <span className="font-medium">
                        {(generatedDoc.xbrl_file_size / 1024).toFixed(2)} KB
                      </span>
                    </div>
                  )}
                </div>

                {generatedDoc.validation_errors &&
                  generatedDoc.validation_errors.length > 0 && (
                    <div className="space-y-2">
                      <p className="text-sm font-medium text-red-600">Validation Errors:</p>
                      <div className="space-y-1">
                        {generatedDoc.validation_errors.map((error: any, idx: number) => (
                          <p key={idx} className="text-xs text-red-600">
                            • {error.message}
                          </p>
                        ))}
                      </div>
                    </div>
                  )}

                <div className="space-y-2 pt-4">
                  <Button
                    className="w-full"
                    onClick={() => handleDownload(generatedDoc.id)}
                    disabled={!generatedDoc.is_valid}
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Download XBRL XML
                  </Button>

                  <p className="text-xs text-center text-muted-foreground">
                    Upload this file to RBI COSMOS portal
                  </p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Information Section */}
      <Card>
        <CardHeader>
          <CardTitle>XBRL Submission Guidelines</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="p-4 rounded-lg border">
              <h3 className="font-semibold mb-2">Step 1: Generate</h3>
              <p className="text-sm text-muted-foreground">
                Select an approved return, choose taxonomy version, and generate XBRL document
              </p>
            </div>
            <div className="p-4 rounded-lg border">
              <h3 className="font-semibold mb-2">Step 2: Validate</h3>
              <p className="text-sm text-muted-foreground">
                System validates XBRL structure and ensures compliance with RBI taxonomy
              </p>
            </div>
            <div className="p-4 rounded-lg border">
              <h3 className="font-semibold mb-2">Step 3: Submit</h3>
              <p className="text-sm text-muted-foreground">
                Download XML file and upload to RBI COSMOS portal for electronic submission
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
