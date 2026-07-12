/**
 * New GRN Page
 * Wrapper for GRN creation form
 */

'use client';

import { Suspense } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import GRNForm from '@/components/procurement/GRNForm';

function NewGRNContent() {
  const router = useRouter();

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push('/procurement/grn')}
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </Button>
        <div>
          <h1 className="text-3xl font-bold">Create Goods Receipt Note</h1>
          <p className="text-gray-600">
            Record goods received against a purchase order
          </p>
        </div>
      </div>

      {/* Breadcrumb */}
      <nav className="flex mb-6 text-sm text-gray-600">
        <a href="/procurement/dashboard" className="hover:text-blue-600">
          Procurement
        </a>
        <span className="mx-2">/</span>
        <a href="/procurement/grn" className="hover:text-blue-600">
          GRNs
        </a>
        <span className="mx-2">/</span>
        <span className="text-gray-900">New</span>
      </nav>

      {/* Form */}
      <GRNForm
        onSuccess={() => router.push('/procurement/grn')}
        onCancel={() => router.push('/procurement/grn')}
      />
    </div>
  );
}

export default function NewGRNPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <NewGRNContent />
    </Suspense>
  );
}
