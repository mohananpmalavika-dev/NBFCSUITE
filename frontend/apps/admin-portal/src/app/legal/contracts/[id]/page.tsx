'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import {
  FileText, Edit, Trash2, Download, AlertCircle, Calendar,
  Users, File, History, RefreshCw, CheckCircle, Clock, XCircle
} from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { toast } from 'sonner'
import { contractService } from '@/services/contract.service'

export default function ContractDetailsPage() {
  const params = useParams()
  const router = useRouter()
  const queryClient = useQueryClient()
  const contractId = params.id as string
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)

  const { data: contractData, isLoading } = useQuery({
    queryKey: ['contract', contractId],
    queryFn: () => contractService.getContract(contractId),
    enabled: !!contractId,
  })

  const contract = contractData?.data?.data

  const deleteMutation = useMutation({
    mutationFn: () => contractService.deleteContract(contractId),
    onSuccess: () => {
      toast.success('Contract deleted successfully')
      queryClient.invalidateQueries({ queryKey: ['contracts'] })
      router.push('/legal/contracts')
    },
    onError: () => {
      toast.error('Failed to delete contract')
    },
  })

  const handleDelete = () => {
    deleteMutation.mutate()
    setShowDeleteDialog(false)
  }

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <Clock className="h-12 w-12 text-gray-400 mx-auto mb-4 animate-spin" />
            <p className="text-gray-600">Loading contract details...</p>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  if (!contract) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <XCircle className="h-12 w-12 text-red-400 mx-auto mb-4" />
            <p className="text-gray-600">Contract not found</p>
            <Link href="/legal/contracts">
              <Button className="mt-4">Back to Contracts</Button>
            </Link>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-start">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-3xl font-bold text-gray-900">{contract.title}</h1>
              <StatusBadge status={contract.status} />
              {contract.is_expiring_soon && (
                <Badge variant="outline" className="border-yellow-500 text-yellow-700">
                  <AlertCircle className="h-3 w-3 mr-1" />
                  Expiring Soon
                </Badge>
              )}
              {contract.is_expired && (
                <Badge variant="destructive">
                  <XCircle className="h-3 w-3 mr-1" />
                  Expired
                </Badge>
              )}
            </div>
            <p className="text-gray-600 mt-1">{contract.contract_number}</p>
          </div>
          <div className="flex gap-2">
            <Link href={`/legal/contracts/${contractId}/edit`}>
              <Button variant="outline">
                <Edit className="h-4 w-4 mr-2" />
                Edit
              </Button>
            </Link>
            <Button variant="outline" onClick={() => setShowDeleteDialog(true)}>
              <Trash2 className="h-4 w-4 mr-2" />
              Delete
            </Button>
            {contract.document_url && (
              <Button variant="outline">
                <Download className="h-4 w-4 mr-2" />
                Download
              </Button>
            )}
          </div>
        </div>

        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <InfoCard
            label="Contract Value"
            value={contractService.formatCurrency(contract.contract_value, contract.currency)}
            icon={FileText}
          />
          <InfoCard
            label="Effective Date"
            value={contractService.formatDate(contract.effective_date)}
            icon={Calendar}
          />
          <InfoCard
            label="Expiry Date"
            value={contract.expiry_date ? contractService.formatDate(contract.expiry_date) : 'No Expiry'}
            icon={Calendar}
          />
          <InfoCard
            label="Days Until Expiry"
            value={contract.days_until_expiry !== null ? `${contract.days_until_expiry} days` : 'N/A'}
            icon={Clock}
          />
        </div>

        {/* Tabs */}
        <Tabs defaultValue="details" className="w-full">
          <TabsList>
            <TabsTrigger value="details">Details</TabsTrigger>
            <TabsTrigger value="parties">Parties ({contract.parties?.length || 0})</TabsTrigger>
            <TabsTrigger value="documents">Documents ({contract.documents?.length || 0})</TabsTrigger>
            <TabsTrigger value="versions">Versions ({contract.versions?.length || 0})</TabsTrigger>
            <TabsTrigger value="renewals">Renewals ({contract.renewals?.length || 0})</TabsTrigger>
          </TabsList>

          {/* Details Tab */}
          <TabsContent value="details">
            <Card>
              <CardHeader>
                <CardTitle>Contract Information</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <DetailRow label="Contract Type" value={contractService.getContractTypeLabel(contract.contract_type)} />
                  <DetailRow label="Status" value={contractService.getContractStatusLabel(contract.status)} />
                  <DetailRow label="Contract Value" value={contractService.formatCurrency(contract.contract_value, contract.currency)} />
                  <DetailRow label="Currency" value={contract.currency} />
                  <DetailRow label="Effective Date" value={contractService.formatDate(contract.effective_date)} />
                  <DetailRow label="Expiry Date" value={contractService.formatDate(contract.expiry_date)} />
                  <DetailRow label="Execution Date" value={contractService.formatDate(contract.execution_date)} />
                  <DetailRow label="Termination Date" value={contractService.formatDate(contract.termination_date)} />
                  <DetailRow label="Renewable" value={contract.is_renewable ? 'Yes' : 'No'} />
                  <DetailRow label="Auto Renewal" value={contract.auto_renewal ? 'Yes' : 'No'} />
                  <DetailRow label="Renewal Notice Days" value={contract.renewal_notice_days.toString()} />
                  <DetailRow label="Renewal Status" value={contractService.getRenewalStatusLabel(contract.renewal_status)} />
                  <DetailRow label="Current Version" value={`Version ${contract.current_version}`} />
                  <DetailRow label="Alert Before Expiry" value={`${contract.alert_before_expiry_days} days`} />
                  <DetailRow label="Created At" value={contractService.formatDate(contract.created_at)} />
                  <DetailRow label="Updated At" value={contractService.formatDate(contract.updated_at)} />
                </div>
                {contract.description && (
                  <div className="mt-6">
                    <h3 className="font-semibold text-gray-900 mb-2">Description</h3>
                    <p className="text-gray-700 whitespace-pre-wrap">{contract.description}</p>
                  </div>
                )}
                {contract.notes && (
                  <div className="mt-6">
                    <h3 className="font-semibold text-gray-900 mb-2">Notes</h3>
                    <p className="text-gray-700 whitespace-pre-wrap">{contract.notes}</p>
                  </div>
                )}
                {contract.tags && contract.tags.length > 0 && (
                  <div className="mt-6">
                    <h3 className="font-semibold text-gray-900 mb-2">Tags</h3>
                    <div className="flex gap-2 flex-wrap">
                      {contract.tags.map((tag: string, index: number) => (
                        <Badge key={index} variant="outline">{tag}</Badge>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Parties Tab */}
          <TabsContent value="parties">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <CardTitle>Contract Parties</CardTitle>
                  <Button size="sm">
                    <Users className="h-4 w-4 mr-2" />
                    Add Party
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {contract.parties && contract.parties.length > 0 ? (
                  <div className="space-y-4">
                    {contract.parties.map((party: any) => (
                      <Card key={party.id}>
                        <CardContent className="pt-6">
                          <div className="flex justify-between items-start">
                            <div className="space-y-2">
                              <div className="flex items-center gap-2">
                                <h3 className="font-semibold text-lg">{party.party_name}</h3>
                                <Badge variant="outline">{party.party_type}</Badge>
                                {party.is_signatory && (
                                  <Badge variant="default">Signatory</Badge>
                                )}
                              </div>
                              {party.party_designation && (
                                <p className="text-sm text-gray-600">{party.party_designation}</p>
                              )}
                              {party.organization_name && (
                                <p className="text-sm text-gray-600">{party.organization_name}</p>
                              )}
                              <div className="flex gap-4 text-sm text-gray-600">
                                {party.email && <span>📧 {party.email}</span>}
                                {party.phone && <span>📞 {party.phone}</span>}
                              </div>
                              {party.address && (
                                <p className="text-sm text-gray-600">{party.address}</p>
                              )}
                              {party.signature_date && (
                                <p className="text-sm text-gray-600">
                                  Signed on {contractService.formatDate(party.signature_date)}
                                </p>
                              )}
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <Users className="h-12 w-12 mx-auto mb-2 text-gray-400" />
                    <p>No parties added yet</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Documents Tab */}
          <TabsContent value="documents">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <CardTitle>Contract Documents</CardTitle>
                  <Button size="sm">
                    <File className="h-4 w-4 mr-2" />
                    Upload Document
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {contract.documents && contract.documents.length > 0 ? (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Document Name</TableHead>
                        <TableHead>Type</TableHead>
                        <TableHead>Version</TableHead>
                        <TableHead>Size</TableHead>
                        <TableHead>Uploaded</TableHead>
                        <TableHead>Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {contract.documents.map((doc: any) => (
                        <TableRow key={doc.id}>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              <File className="h-4 w-4 text-gray-400" />
                              {doc.document_name}
                              {doc.is_confidential && (
                                <Badge variant="outline" className="text-xs">Confidential</Badge>
                              )}
                            </div>
                          </TableCell>
                          <TableCell>{doc.document_type || '—'}</TableCell>
                          <TableCell>v{doc.version}</TableCell>
                          <TableCell>{doc.file_size ? `${(doc.file_size / 1024).toFixed(2)} KB` : '—'}</TableCell>
                          <TableCell>{contractService.formatDate(doc.uploaded_at)}</TableCell>
                          <TableCell>
                            <Button variant="ghost" size="sm">
                              <Download className="h-4 w-4" />
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <File className="h-12 w-12 mx-auto mb-2 text-gray-400" />
                    <p>No documents uploaded yet</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Versions Tab */}
          <TabsContent value="versions">
            <Card>
              <CardHeader>
                <CardTitle>Version History</CardTitle>
              </CardHeader>
              <CardContent>
                {contract.versions && contract.versions.length > 0 ? (
                  <div className="space-y-4">
                    {contract.versions.map((version: any, index: number) => (
                      <Card key={version.id}>
                        <CardContent className="pt-6">
                          <div className="flex justify-between items-start">
                            <div className="space-y-2 flex-1">
                              <div className="flex items-center gap-2">
                                <h3 className="font-semibold">Version {version.version_number}</h3>
                                {version.version_name && (
                                  <Badge variant="outline">{version.version_name}</Badge>
                                )}
                                {index === 0 && (
                                  <Badge variant="default">Current</Badge>
                                )}
                              </div>
                              <p className="text-sm text-gray-600">{version.title}</p>
                              {version.changes_summary && (
                                <p className="text-sm text-gray-700">
                                  <strong>Changes:</strong> {version.changes_summary}
                                </p>
                              )}
                              {version.change_reason && (
                                <p className="text-sm text-gray-700">
                                  <strong>Reason:</strong> {version.change_reason}
                                </p>
                              )}
                              <div className="flex gap-4 text-sm text-gray-600">
                                <span>Effective: {contractService.formatDate(version.effective_date)}</span>
                                {version.expiry_date && (
                                  <span>Expires: {contractService.formatDate(version.expiry_date)}</span>
                                )}
                                {version.contract_value && (
                                  <span>Value: {contractService.formatCurrency(version.contract_value)}</span>
                                )}
                              </div>
                              <p className="text-xs text-gray-500">
                                Created {contractService.formatDate(version.created_at)}
                              </p>
                            </div>
                            <Button variant="ghost" size="sm">
                              <Download className="h-4 w-4" />
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <History className="h-12 w-12 mx-auto mb-2 text-gray-400" />
                    <p>No version history available</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Renewals Tab */}
          <TabsContent value="renewals">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <CardTitle>Renewal History</CardTitle>
                  {contract.is_renewable && (
                    <Button size="sm">
                      <RefreshCw className="h-4 w-4 mr-2" />
                      Initiate Renewal
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                {contract.renewals && contract.renewals.length > 0 ? (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Renewal #</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Due Date</TableHead>
                        <TableHead>Completed Date</TableHead>
                        <TableHead>New Expiry</TableHead>
                        <TableHead>New Value</TableHead>
                        <TableHead>Change %</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {contract.renewals.map((renewal: any) => (
                        <TableRow key={renewal.id}>
                          <TableCell>#{renewal.renewal_number}</TableCell>
                          <TableCell>
                            <Badge variant={renewal.renewal_status === 'completed' ? 'default' : 'outline'}>
                              {contractService.getRenewalStatusLabel(renewal.renewal_status)}
                            </Badge>
                          </TableCell>
                          <TableCell>{contractService.formatDate(renewal.renewal_due_date)}</TableCell>
                          <TableCell>{contractService.formatDate(renewal.renewal_completed_date)}</TableCell>
                          <TableCell>{contractService.formatDate(renewal.new_expiry_date)}</TableCell>
                          <TableCell>{contractService.formatCurrency(renewal.new_contract_value)}</TableCell>
                          <TableCell>
                            {renewal.value_change_percentage ? `${renewal.value_change_percentage}%` : '—'}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <RefreshCw className="h-12 w-12 mx-auto mb-2 text-gray-400" />
                    <p>No renewal history</p>
                    {contract.is_renewable && (
                      <Button className="mt-4" size="sm">Initiate First Renewal</Button>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Delete Confirmation Dialog */}
        <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Delete Contract</AlertDialogTitle>
              <AlertDialogDescription>
                Are you sure you want to delete this contract? This action cannot be undone.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
              <AlertDialogAction onClick={handleDelete} className="bg-red-600 hover:bg-red-700">
                Delete
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </DashboardLayout>
  )
}

function InfoCard({ label, value, icon: Icon }: any) {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm text-gray-600">{label}</p>
            <p className="text-xl font-bold text-gray-900 mt-1">{value}</p>
          </div>
          <div className="h-10 w-10 rounded-lg bg-blue-100 text-blue-600 flex items-center justify-center">
            <Icon className="h-5 w-5" />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-sm font-medium text-gray-600">{label}</p>
      <p className="text-base text-gray-900 mt-1">{value}</p>
    </div>
  )
}

function StatusBadge({ status }: any) {
  const color = contractService.getContractStatusColor(status)
  const label = contractService.getContractStatusLabel(status)

  const variants: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
    gray: 'outline',
    blue: 'default',
    yellow: 'outline',
    green: 'default',
    red: 'destructive',
    purple: 'secondary',
  }

  return <Badge variant={variants[color] || 'outline'}>{label}</Badge>
}
