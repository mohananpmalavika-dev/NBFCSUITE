/**
 * New Vendor Page
 * Create a new vendor
 */

'use client';

import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';
import VendorForm from '@/components/procurement/VendorForm';

export default function NewVendorPage() {
  const router = useRouter();

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => router.push('/procurement/vendors')}
        >
          <ArrowLeft className="w-5 h-5" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold">Create New Vendor</h1>
          <p className="text-gray-600 mt-1">Add a new vendor to the system</p>
        </div>
      </div>

      <VendorForm />
    </div>
  );
}
