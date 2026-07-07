'use client'

/**
 * Treasury Main Page
 * Entry point for treasury operations - redirects to dashboard
 */

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function TreasuryPage() {
  const router = useRouter()

  useEffect(() => {
    // Redirect to treasury dashboard
    router.push('/treasury/dashboard')
  }, [router])

  return (
    <div className="container mx-auto p-6">
      <div className="flex justify-center items-center h-64">
        <div className="text-center">
          <div className="inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
          <p className="mt-4 text-gray-600">Loading Treasury...</p>
        </div>
      </div>
    </div>
  )
}
