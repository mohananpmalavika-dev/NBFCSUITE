/**
 * Edit Purchase Requisition Page
 * Edit an existing purchase requisition (only in draft status)
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { ArrowLeft, AlertCircle } from 'lucide-react';
import RequisitionForm from '@/components/procurement/RequisitionForm';
import { procurementService } from '@/services/procurement.service';
import type { PurchaseRequisition } from '@/types/procurement';

export default function EditRequisitionPage() {
  const router = useRouter();
  const params = useParams();
  const requisitionId = params?.id as string;

  const [requisition, setRequisition] = useState<PurchaseRequisition | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (requisitionId) {
      fetchRequisition();
    }
  }, [requisitionId]);

  const fetchRequisition = async () => {
    try {
      setLoading(true);
      const response = await procurementService.requisition.getById(requisitionId);
      if (response.success && response.data) {
        // Check if requisition can be edited
        if (response.data.status !== 'draft') {
          setError('Only draft requisitions can be edited');
        } else {
          setRequisition(response.data);
        }
      } else {
        setError('Requisition not found');
      }
    } catch (error) {
      console.error('Failed to fetch requisition:', error);
      setError('Failed to load requisition');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading requisition...</p>
        </div>
      </div>
    );
  }

  if (error || !requisition) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            {error || 'Requisition Not Found'}
          </h2>
          <p className="text-gray-600 mb-4">
            {error === 'Only draft requisitions can be edited'
              ? 'This requisition has been submitted and cannot be edited.'
              : 'The requested requisition could not be found.'}
          </p>
          <div className="flex gap-2 justify-center">
            <Button
              variant="outline"
              onClick={() => router.push('/procurement/requisitions')}
            >
              Back to Requisitions
            </Button>
            {requisitionId && (
              <Button
                onClick={() =>
                  router.push(`/procurement/requisitions/${requisitionId}`)
                }
              >
                View Requisition
              </Button>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={() =>
            router.push(`/procurement/requisitions/${requisitionId}`)
          }
        >
          <ArrowLeft className="w-5 h-5" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold">Edit Purchase Requisition</h1>
          <p className="text-gray-600 mt-1">
            {requisition.requisition_number} - {requisition.title}
          </p>
        </div>
      </div>

      <RequisitionForm requisition={requisition} />
    </div>
  );
}
