/**
 * Edit Vendor Page
 * Edit an existing vendor
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { ArrowLeft, AlertCircle } from 'lucide-react';
import VendorForm from '@/components/procurement/VendorForm';
import { procurementService } from '@/services/procurement.service';
import type { Vendor } from '@/types/procurement';

export default function EditVendorPage() {
  const router = useRouter();
  const params = useParams();
  const vendorId = params?.id as string;

  const [vendor, setVendor] = useState<Vendor | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (vendorId) {
      fetchVendor();
    }
  }, [vendorId]);

  const fetchVendor = async () => {
    try {
      setLoading(true);
      const response = await procurementService.vendor.getById(vendorId);
      if (response.success && response.data) {
        setVendor(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch vendor:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading vendor...</p>
        </div>
      </div>
    );
  }

  if (!vendor) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Vendor Not Found</h2>
          <p className="text-gray-600 mb-4">The requested vendor could not be found.</p>
          <Button onClick={() => router.push('/procurement/vendors')}>
            Back to Vendors
          </Button>
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
          onClick={() => router.push(`/procurement/vendors/${vendorId}`)}
        >
          <ArrowLeft className="w-5 h-5" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold">Edit Vendor</h1>
          <p className="text-gray-600 mt-1">{vendor.vendor_name} ({vendor.vendor_code})</p>
        </div>
      </div>

      <VendorForm vendor={vendor} />
    </div>
  );
}
