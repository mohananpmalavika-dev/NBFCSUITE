/**
 * Vendor Detail Page
 * Displays complete vendor information with ratings, orders, and performance metrics
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  ArrowLeft,
  Edit,
  Phone,
  Mail,
  MapPin,
  Building,
  CreditCard,
  Star,
  TrendingUp,
  Package,
  Clock,
  AlertCircle,
} from 'lucide-react';
import { procurementService } from '@/services/procurement.service';
import type { Vendor, VendorRating, VendorStatus } from '@/types/procurement';

export default function VendorDetailPage() {
  const router = useRouter();
  const params = useParams();
  const vendorId = params?.id as string;

  const [vendor, setVendor] = useState<Vendor | null>(null);
  const [ratings, setRatings] = useState<VendorRating[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (vendorId) {
      fetchVendorDetails();
    }
  }, [vendorId]);

  const fetchVendorDetails = async () => {
    try {
      setLoading(true);
      const response = await procurementService.vendor.getById(vendorId);
      if (response.success && response.data) {
        setVendor(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch vendor details:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: VendorStatus) => {
    const colors = {
      active: 'bg-green-100 text-green-800',
      inactive: 'bg-gray-100 text-gray-800',
      blacklisted: 'bg-red-100 text-red-800',
      suspended: 'bg-yellow-100 text-yellow-800',
      under_review: 'bg-blue-100 text-blue-800',
    };
    return (
      <Badge className={colors[status]}>
        {status.replace('_', ' ').toUpperCase()}
      </Badge>
    );
  };

  const formatRating = (rating: number) => {
    return (
      <div className="flex items-center gap-1">
        <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
        <span className="font-semibold text-lg">{rating.toFixed(1)}</span>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading vendor details...</p>
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
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => router.push('/procurement/vendors')}
          >
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">{vendor.vendor_name}</h1>
            <div className="flex items-center gap-3 mt-2">
              <span className="text-gray-600">{vendor.vendor_code}</span>
              {getStatusBadge(vendor.status)}
              <Badge variant="outline">
                {vendor.vendor_type.replace('_', ' ')}
              </Badge>
            </div>
          </div>
        </div>
        <Button
          onClick={() => router.push(`/procurement/vendors/${vendorId}/edit`)}
          className="flex items-center gap-2"
        >
          <Edit className="w-4 h-4" />
          Edit Vendor
        </Button>
      </div>

      {/* Performance Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              Overall Rating
            </CardTitle>
          </CardHeader>
          <CardContent>{formatRating(vendor.overall_rating)}</CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              Total Orders
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Package className="w-5 h-5 text-blue-500" />
              <span className="text-2xl font-bold">{vendor.total_orders}</span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              On-Time Delivery
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Clock className="w-5 h-5 text-green-500" />
              <span className="text-2xl font-bold">
                {vendor.total_orders > 0
                  ? Math.round((vendor.on_time_deliveries / vendor.total_orders) * 100)
                  : 0}
                %
              </span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              Credit Limit
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <CreditCard className="w-5 h-5 text-purple-500" />
              <span className="text-2xl font-bold">
                ₹{vendor.credit_limit.toLocaleString()}
              </span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              Credit Period
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {vendor.credit_period_days} days
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="details" className="space-y-4">
        <TabsList>
          <TabsTrigger value="details">Details</TabsTrigger>
          <TabsTrigger value="ratings">Ratings</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="orders">Orders</TabsTrigger>
        </TabsList>

        {/* Details Tab */}
        <TabsContent value="details" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Contact Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Phone className="w-5 h-5" />
                  Contact Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {vendor.contact_person && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">
                      Contact Person
                    </label>
                    <p className="text-base">{vendor.contact_person}</p>
                  </div>
                )}
                {vendor.email && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">Email</label>
                    <p className="text-base flex items-center gap-2">
                      <Mail className="w-4 h-4 text-gray-400" />
                      {vendor.email}
                    </p>
                  </div>
                )}
                {vendor.phone && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">Phone</label>
                    <p className="text-base flex items-center gap-2">
                      <Phone className="w-4 h-4 text-gray-400" />
                      {vendor.phone}
                    </p>
                  </div>
                )}
                {vendor.mobile && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">Mobile</label>
                    <p className="text-base">{vendor.mobile}</p>
                  </div>
                )}
                {vendor.website && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">Website</label>
                    <p className="text-base">
                      <a
                        href={vendor.website}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline"
                      >
                        {vendor.website}
                      </a>
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Address */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MapPin className="w-5 h-5" />
                  Address
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {vendor.address_line1 && <p>{vendor.address_line1}</p>}
                {vendor.address_line2 && <p>{vendor.address_line2}</p>}
                <p>
                  {[vendor.city, vendor.state, vendor.pincode]
                    .filter(Boolean)
                    .join(', ')}
                </p>
                <p className="font-medium">{vendor.country}</p>
              </CardContent>
            </Card>

            {/* Tax & Compliance */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Building className="w-5 h-5" />
                  Tax & Compliance
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {vendor.gst_number && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">GST Number</label>
                    <p className="text-base font-mono">{vendor.gst_number}</p>
                  </div>
                )}
                {vendor.pan_number && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">PAN Number</label>
                    <p className="text-base font-mono">{vendor.pan_number}</p>
                  </div>
                )}
                {vendor.tan_number && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">TAN Number</label>
                    <p className="text-base font-mono">{vendor.tan_number}</p>
                  </div>
                )}
                {vendor.msme_registration && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">
                      MSME Registration
                    </label>
                    <p className="text-base font-mono">{vendor.msme_registration}</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Banking Details */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CreditCard className="w-5 h-5" />
                  Banking Details
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {vendor.bank_name && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">Bank Name</label>
                    <p className="text-base">{vendor.bank_name}</p>
                  </div>
                )}
                {vendor.bank_branch && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">Branch</label>
                    <p className="text-base">{vendor.bank_branch}</p>
                  </div>
                )}
                {vendor.account_number && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">
                      Account Number
                    </label>
                    <p className="text-base font-mono">{vendor.account_number}</p>
                  </div>
                )}
                {vendor.ifsc_code && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">IFSC Code</label>
                    <p className="text-base font-mono">{vendor.ifsc_code}</p>
                  </div>
                )}
                {vendor.account_holder_name && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">
                      Account Holder Name
                    </label>
                    <p className="text-base">{vendor.account_holder_name}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Additional Info */}
          <Card>
            <CardHeader>
              <CardTitle>Additional Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <label className="text-sm font-medium text-gray-500">
                  Payment Terms
                </label>
                <p className="text-base">
                  {vendor.payment_terms.replace('_', ' ').toUpperCase()}
                </p>
              </div>
              {vendor.products_services && (
                <div>
                  <label className="text-sm font-medium text-gray-500">
                    Products/Services
                  </label>
                  <p className="text-base">{vendor.products_services}</p>
                </div>
              )}
              {vendor.notes && (
                <div>
                  <label className="text-sm font-medium text-gray-500">Notes</label>
                  <p className="text-base whitespace-pre-wrap">{vendor.notes}</p>
                </div>
              )}
              {vendor.blacklist_reason && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <label className="text-sm font-medium text-red-700">
                    Blacklist Reason
                  </label>
                  <p className="text-base text-red-900">{vendor.blacklist_reason}</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Ratings Tab */}
        <TabsContent value="ratings">
          <Card>
            <CardHeader>
              <CardTitle>Vendor Ratings</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <div className="text-sm text-gray-600">Quality</div>
                  <div className="text-2xl font-bold text-blue-600">
                    {vendor.quality_rating.toFixed(1)}
                  </div>
                  <div className="flex justify-center mt-1">
                    {[...Array(5)].map((_, i) => (
                      <Star
                        key={i}
                        className={`w-4 h-4 ${
                          i < Math.round(vendor.quality_rating)
                            ? 'fill-blue-400 text-blue-400'
                            : 'text-gray-300'
                        }`}
                      />
                    ))}
                  </div>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <div className="text-sm text-gray-600">Delivery</div>
                  <div className="text-2xl font-bold text-green-600">
                    {vendor.delivery_rating.toFixed(1)}
                  </div>
                  <div className="flex justify-center mt-1">
                    {[...Array(5)].map((_, i) => (
                      <Star
                        key={i}
                        className={`w-4 h-4 ${
                          i < Math.round(vendor.delivery_rating)
                            ? 'fill-green-400 text-green-400'
                            : 'text-gray-300'
                        }`}
                      />
                    ))}
                  </div>
                </div>
                <div className="text-center p-4 bg-purple-50 rounded-lg">
                  <div className="text-sm text-gray-600">Price</div>
                  <div className="text-2xl font-bold text-purple-600">
                    {vendor.price_rating.toFixed(1)}
                  </div>
                  <div className="flex justify-center mt-1">
                    {[...Array(5)].map((_, i) => (
                      <Star
                        key={i}
                        className={`w-4 h-4 ${
                          i < Math.round(vendor.price_rating)
                            ? 'fill-purple-400 text-purple-400'
                            : 'text-gray-300'
                        }`}
                      />
                    ))}
                  </div>
                </div>
                <div className="text-center p-4 bg-orange-50 rounded-lg">
                  <div className="text-sm text-gray-600">Service</div>
                  <div className="text-2xl font-bold text-orange-600">
                    {vendor.service_rating.toFixed(1)}
                  </div>
                  <div className="flex justify-center mt-1">
                    {[...Array(5)].map((_, i) => (
                      <Star
                        key={i}
                        className={`w-4 h-4 ${
                          i < Math.round(vendor.service_rating)
                            ? 'fill-orange-400 text-orange-400'
                            : 'text-gray-300'
                        }`}
                      />
                    ))}
                  </div>
                </div>
                <div className="text-center p-4 bg-yellow-50 rounded-lg">
                  <div className="text-sm text-gray-600">Overall</div>
                  <div className="text-2xl font-bold text-yellow-600">
                    {vendor.overall_rating.toFixed(1)}
                  </div>
                  <div className="flex justify-center mt-1">
                    {[...Array(5)].map((_, i) => (
                      <Star
                        key={i}
                        className={`w-4 h-4 ${
                          i < Math.round(vendor.overall_rating)
                            ? 'fill-yellow-400 text-yellow-400'
                            : 'text-gray-300'
                        }`}
                      />
                    ))}
                  </div>
                </div>
              </div>
              <div className="text-center py-8 text-gray-500">
                Rating history will be displayed here
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Performance Tab */}
        <TabsContent value="performance">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                Performance Metrics
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-gray-500">
                Performance analytics and charts will be displayed here
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Orders Tab */}
        <TabsContent value="orders">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Package className="w-5 h-5" />
                Purchase Orders
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-gray-500">
                Purchase order history will be displayed here
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
