/**
 * New Invoice Page
 * Wrapper for invoice creation form
 */

'use client';

import { Suspense } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import InvoiceForm from '@/components/procurement/InvoiceForm';

function NewInvoiceContent() {
  const router = useRouter();

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push('/procurement/invoices')}
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </Button>
        <div>
          <h1 className="text-3xl font-bold">Create Vendor Invoice</h1>
          <p className="text-gray-600">
            Record a vendor invoice with 3-way matching
          </p>
        </div>
      </div>

      {/* Breadcrumb */}
      <nav className="flex mb-6 text-sm text-gray-600">
        <a href="/procurement/dashboard" className="hover:text-blue-600">
          Procurement
        </a>
        <span className="mx-2">/</span>
        <a href="/procurement/invoices" className="hover:text-blue-600">
          Invoices
        </a>
        <span className="mx-2">/</span>
        <span className="text-gray-900">New</span>
      </nav>

      {/* Form */}
      <InvoiceForm
        onSuccess={() => router.push('/procurement/invoices')}
        onCancel={() => router.push('/procurement/invoices')}
      />
    </div>
  );
}

export default function NewInvoicePage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <NewInvoiceContent />
    </Suspense>
  );
}
