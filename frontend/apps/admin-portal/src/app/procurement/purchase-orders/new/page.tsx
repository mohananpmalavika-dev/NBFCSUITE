/**
 * New Purchase Order Page
 * Wrapper for PO creation form
 */

'use client';

import { useRouter } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import POForm from '@/components/procurement/POForm';

export default function NewPurchaseOrderPage() {
  const router = useRouter();

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push('/procurement/purchase-orders')}
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </Button>
        <div>
          <h1 className="text-3xl font-bold">Create Purchase Order</h1>
          <p className="text-gray-600">
            Create a new purchase order for vendor procurement
          </p>
        </div>
      </div>

      {/* Breadcrumb */}
      <nav className="flex mb-6 text-sm text-gray-600">
        <a href="/procurement/dashboard" className="hover:text-blue-600">
          Procurement
        </a>
        <span className="mx-2">/</span>
        <a href="/procurement/purchase-orders" className="hover:text-blue-600">
          Purchase Orders
        </a>
        <span className="mx-2">/</span>
        <span className="text-gray-900">New</span>
      </nav>

      {/* Form */}
      <POForm
        onSuccess={() => router.push('/procurement/purchase-orders')}
        onCancel={() => router.push('/procurement/purchase-orders')}
      />
    </div>
  );
}
