'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { 
  Shield, 
  CheckCircle2, 
  XCircle, 
  Loader2, 
  Fingerprint,
  CreditCard,
  FileText,
  ExternalLink
} from 'lucide-react'
import { useToast } from '@/components/ui/use-toast'
import { customerService } from '@/services/customer.service'
import type { Customer } from '@/types/customer.types'

interface KYCManagementProps {
  customer: Customer
}

export function KYCManagement({ customer }: KYCManagementProps) {
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<'overview' | 'aadhaar' | 'digilocker'>('overview')

  // Aadhaar verification state
  const [aadhaarNumber, setAadhaarNumber] = useState('')
  const [otp, setOtp] = useState('')
  const [requestId, setRequestId] = useState('')
  const [otpSent, setOtpSent] = useState(false)

  // DigiLocker state
  const [digilockerAccessToken, setDigilockerAccessToken] = useState('')

  // Initiate Aadhaar OTP
  const initiateOTPMutation = useMutation({
    mutationFn: () => customerService.initiateAadhaarOTP(customer.id.toString(), aadhaarNumber),
    onSuccess: (response) => {
      setRequestId(response.data.request_id)
      setOtpSent(true)
      toast({
        title: 'OTP Sent',
        description: response.data.message,
      })
    },
    onError: (error: any) => {
      toast({
        title: 'Failed to send OTP',
        description: error.response?.data?.detail || 'An error occurred',
        variant: 'destructive',
      })
    },
  })

  // Verify Aadhaar OTP
  const verifyOTPMutation = useMutation({
    mutationFn: () => customerService.verifyAadhaarOTP(customer.id.toString(), {
      aadhaar_number: aadhaarNumber,
      otp,
      request_id: requestId,
    }),
    onSuccess: (response) => {
      if (response.data.verified) {
        toast({
          title: 'Aadhaar Verified',
          description: 'KYC verification successful',
        })
        queryClient.invalidateQueries({ queryKey: ['customer', customer.id.toString()] })
        setOtpSent(false)
        setOtp('')
        setAadhaarNumber('')
      } else {
        toast({
          title: 'Verification Failed',
          description: response.data.message,
          variant: 'destructive',
        })
      }
    },
    onError: (error: any) => {
      toast({
        title: 'Verification Failed',
        description: error.response?.data?.detail || 'An error occurred',
        variant: 'destructive',
      })
    },
  })

  // Initiate DigiLocker
  const initiateDigiLockerMutation = useMutation({
    mutationFn: () => customerService.initiateDigiLocker(
      customer.id.toString(), 
      `${window.location.origin}/customers/${customer.id}/digilocker-callback`
    ),
    onSuccess: (response) => {
      // Redirect to DigiLocker authorization
      window.open(response.data.authorization_url, '_blank')
      toast({
        title: 'DigiLocker Authorization',
        description: 'Please complete authorization in the new window',
      })
    },
    onError: (error: any) => {
      toast({
        title: 'Failed to initiate DigiLocker',
        description: error.response?.data?.detail || 'An error occurred',
        variant: 'destructive',
      })
    },
  })

  const kycCompletionPercentage = calculateKYCCompletion(customer)

  return (
    <div className="space-y-6">
      {/* KYC Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            KYC Status Overview
          </CardTitle>
          <CardDescription>
            Complete customer verification and KYC process
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Progress */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">KYC Completion</span>
              <span className="text-sm text-gray-600">{kycCompletionPercentage}%</span>
            </div>
            <Progress value={kycCompletionPercentage} className="h-2" />
          </div>

          {/* Verification Checklist */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <VerificationItem
              label="Aadhaar Verified"
              verified={customer.aadhaar_number ? true : false}
              icon={<CreditCard className="h-5 w-5" />}
            />
            <VerificationItem
              label="PAN Verified"
              verified={customer.pan_number ? true : false}
              icon={<CreditCard className="h-5 w-5" />}
            />
            <VerificationItem
              label="Bank Account Verified"
              verified={false}
              icon={<CreditCard className="h-5 w-5" />}
            />
            <VerificationItem
              label="Address Verified"
              verified={customer.current_address_line1 ? true : false}
              icon={<FileText className="h-5 w-5" />}
            />
          </div>
        </CardContent>
      </Card>

      {/* Verification Tabs */}
      <div className="flex gap-2 border-b">
        <button
          onClick={() => setActiveTab('overview')}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'overview'
              ? 'border-primary text-primary'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}
        >
          Overview
        </button>
        <button
          onClick={() => setActiveTab('aadhaar')}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'aadhaar'
              ? 'border-primary text-primary'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}
        >
          Aadhaar eKYC
        </button>
        <button
          onClick={() => setActiveTab('digilocker')}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'digilocker'
              ? 'border-primary text-primary'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}
        >
          DigiLocker
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <Card>
          <CardHeader>
            <CardTitle>Verification Methods</CardTitle>
            <CardDescription>
              Choose a method to verify customer identity
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Button
                variant="outline"
                className="h-auto p-6 flex flex-col items-start gap-2"
                onClick={() => setActiveTab('aadhaar')}
              >
                <Fingerprint className="h-8 w-8 text-primary" />
                <div className="text-left">
                  <p className="font-semibold">Aadhaar eKYC</p>
                  <p className="text-sm text-gray-600">OTP or Biometric verification</p>
                </div>
              </Button>

              <Button
                variant="outline"
                className="h-auto p-6 flex flex-col items-start gap-2"
                onClick={() => setActiveTab('digilocker')}
              >
                <FileText className="h-8 w-8 text-primary" />
                <div className="text-left">
                  <p className="font-semibold">DigiLocker</p>
                  <p className="text-sm text-gray-600">Fetch verified documents</p>
                </div>
              </Button>

              <Button
                variant="outline"
                className="h-auto p-6 flex flex-col items-start gap-2"
                disabled
              >
                <CreditCard className="h-8 w-8 text-gray-400" />
                <div className="text-left">
                  <p className="font-semibold">Video KYC</p>
                  <p className="text-sm text-gray-600">Coming soon</p>
                </div>
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {activeTab === 'aadhaar' && (
        <Card>
          <CardHeader>
            <CardTitle>Aadhaar eKYC Verification</CardTitle>
            <CardDescription>
              Verify customer identity using Aadhaar OTP
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {!otpSent ? (
              <>
                <div className="space-y-2">
                  <Label htmlFor="aadhaar">Aadhaar Number</Label>
                  <Input
                    id="aadhaar"
                    placeholder="Enter 12-digit Aadhaar number"
                    value={aadhaarNumber}
                    onChange={(e) => setAadhaarNumber(e.target.value.replace(/\D/g, '').slice(0, 12))}
                    maxLength={12}
                  />
                  <p className="text-sm text-gray-600">
                    OTP will be sent to Aadhaar-linked mobile number
                  </p>
                </div>

                <Button
                  onClick={() => initiateOTPMutation.mutate()}
                  disabled={aadhaarNumber.length !== 12 || initiateOTPMutation.isPending}
                  className="w-full"
                >
                  {initiateOTPMutation.isPending && (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  )}
                  Send OTP
                </Button>
              </>
            ) : (
              <>
                <div className="space-y-2">
                  <Label htmlFor="otp">Enter OTP</Label>
                  <Input
                    id="otp"
                    placeholder="Enter 6-digit OTP"
                    value={otp}
                    onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                    maxLength={6}
                  />
                  <p className="text-sm text-gray-600">
                    OTP sent to Aadhaar-linked mobile
                  </p>
                </div>

                <div className="flex gap-2">
                  <Button
                    onClick={() => verifyOTPMutation.mutate()}
                    disabled={otp.length !== 6 || verifyOTPMutation.isPending}
                    className="flex-1"
                  >
                    {verifyOTPMutation.isPending && (
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    )}
                    Verify OTP
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => {
                      setOtpSent(false)
                      setOtp('')
                    }}
                  >
                    Cancel
                  </Button>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      )}

      {activeTab === 'digilocker' && (
        <Card>
          <CardHeader>
            <CardTitle>DigiLocker Integration</CardTitle>
            <CardDescription>
              Fetch verified documents from DigiLocker
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-sm text-blue-900">
                DigiLocker is a secure digital locker system by Government of India.
                You can fetch verified documents like Aadhaar, PAN, Driving License, etc.
              </p>
            </div>

            <Button
              onClick={() => initiateDigiLockerMutation.mutate()}
              disabled={initiateDigiLockerMutation.isPending}
              className="w-full"
            >
              {initiateDigiLockerMutation.isPending ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <ExternalLink className="h-4 w-4 mr-2" />
              )}
              Connect to DigiLocker
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

function VerificationItem({ 
  label, 
  verified, 
  icon 
}: { 
  label: string
  verified: boolean
  icon: React.ReactNode 
}) {
  return (
    <div className="flex items-center gap-3 p-3 border rounded-lg">
      <div className="text-gray-600">{icon}</div>
      <div className="flex-1">
        <p className="text-sm font-medium">{label}</p>
      </div>
      {verified ? (
        <CheckCircle2 className="h-5 w-5 text-green-600" />
      ) : (
        <XCircle className="h-5 w-5 text-gray-400" />
      )}
    </div>
  )
}

function calculateKYCCompletion(customer: Customer): number {
  let completed = 0
  let total = 5

  if (customer.aadhaar_number) completed++
  if (customer.pan_number) completed++
  if (customer.current_address_line1) completed++
  if (customer.mobile) completed++
  if (customer.email) completed++

  return Math.round((completed / total) * 100)
}
