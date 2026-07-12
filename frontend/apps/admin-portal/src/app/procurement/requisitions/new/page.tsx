/**
 * New Purchase Requisition Page
 * Create a new purchase requisition
 */

'use client';

import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';
import RequisitionForm from '@/components/procurement/RequisitionForm';

export default function NewRequisitionPage() {
  const router = useRouter();

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => router.push('/procurement/requisitions')}
        >
          <ArrowLeft className="w-5 h-5" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold">Create Purchase Requisition</h1>
          <p className="text-gray-600 mt-1">
            Request for purchase of goods or services
          </p>
        </div>
      </div>

      <RequisitionForm />
    </div>
  );
}
