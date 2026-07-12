/**
 * New RFQ Page
 * Create a new Request for Quotation
 */

'use client';

import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';
import RFQForm from '@/components/procurement/RFQForm';

export default function NewRFQPage() {
  const router = useRouter();

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => router.push('/procurement/rfq')}
        >
          <ArrowLeft className="w-5 h-5" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold">Create Request for Quotation</h1>
          <p className="text-gray-600 mt-1">
            Request quotes from multiple vendors
          </p>
        </div>
      </div>

      <RFQForm />
    </div>
  );
}
