/**
 * Edit Purchase Order Page
 * Wrapper for PO editing form
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import POForm from '@/components/procurement/POForm';
import { procurementService } from '@/services/procurement.service';
import type { PurchaseOrder } from '@/types/procurement';

interface EditPurchaseOrderPageProps {
  params: {
    id: string;
  };
}

export default function EditPurchaseOrderPage({ params }: EditPurchaseOrderPageProps) {
  const router = useRouter();
  const [po, setPo] = useState<PurchaseOrder | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPO();
  }, [params.id]);

  const fetchPO = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await procurementService.purchaseOrder.getById(params.id);
      if (response.success && response.data) {
        setPo(response.data);
      } else {
        setError(response.message || 'Failed to fetch purchase order');
      }
    } catch (err) {
      setError('An error occurred while fetching the purchase order');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading purchase order...</div>
      </div>
    );
  }

  if (error || !po) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error || 'Purchase order not found'}
        </div>
        <Button
          onClick={() => router.push('/procurement/purchase-orders')}
          className="mt-4"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Purchase Orders
        </Button>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push(`/procurement/purchase-orders/${po.id}`)}
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </Button>
        <div>
          <h1 className="text-3xl font-bold">Edit Purchase Order</h1>
          <p className="text-gray-600">{po.po_number}</p>
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
        <a
          href={`/procurement/purchase-orders/${po.id}`}
          className="hover:text-blue-600"
        >
          {po.po_number}
        </a>
        <span className="mx-2">/</span>
        <span className="text-gray-900">Edit</span>
      </nav>

      {/* Form */}
      <POForm
        po={po}
        onSuccess={() => router.push(`/procurement/purchase-orders/${po.id}`)}
        onCancel={() => router.push(`/procurement/purchase-orders/${po.id}`)}
      />
    </div>
  );
}
