'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/app/components/eds/card';
import { Button } from '@/app/components/eds/button';
import { Badge } from '@/app/components/eds/badge';
import {
  Shield,
  Plus,
  Search,
  CheckCircle,
  XCircle,
  AlertCircle,
  Clock,
  Package,
  Lock,
  Unlock,
} from 'lucide-react';
import { goldApi } from '../../goldApi';

interface SecuritySeal {
  id: string;
  seal_number: string;
  seal_type: string;
  status: string;
  packet_id?: string;
  packet_number?: string;
  applied_at?: string;
  applied_by?: string;
  verified_at?: string;
  verified_by?: string;
  broken_at?: string;
  broken_by?: string;
  break_reason?: string;
}

export default function SealsManagementPage() {
  const router = useRouter();
  const [seals, setSeals] = useState<SecuritySeal[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadSeals();
  }, []);

  const loadSeals = async () => {
    try {
      setLoading(true);
      // In real implementation, this would be a dedicated endpoint
      // For now, we'll show a placeholder
      const mockSeals: SecuritySeal[] = [];
      setSeals(mockSeals);
    } catch (error) {
      console.error('Failed to load seals:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSeal = async () => {
    const sealNumber = prompt('Enter seal number:');
    if (!sealNumber) return;

    const sealType = prompt('Enter seal type (tamper_evident/security_tag/hologram/biometric):');
    if (!sealType) return;

    try {
      // Create seal in inventory
      alert('Seal inventory management - full implementation requires additional backend support');
      await loadSeals();
    } catch (error) {
      console.error('Failed to create seal:', error);
      alert('Failed to create seal');
    }
  };

  const handleVerifySeal = async (sealId: string) => {
    try {
      const verificationStatus = prompt('Enter verification status (intact/broken/tampered):');
      if (!verificationStatus) return;

      await goldApi.verifySeal(sealId, {
        verification_status: verificationStatus,
        verified_by: 'current-user-id', // Replace with actual user ID
        notes: verificationStatus === 'intact' ? 'Seal verified and intact' : 'Seal compromised',
      });
      await loadSeals();
      alert('Seal verification recorded');
    } catch (error) {
      console.error('Failed to verify seal:', error);
      alert('Failed to verify seal');
    }
  };

  const getSealStatusIcon = (status: string) => {
    switch (status) {
      case 'intact':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'broken':
        return <XCircle className="h-5 w-5 text-red-600" />;
      case 'tampered':
        return <AlertCircle className="h-5 w-5 text-orange-600" />;
      case 'available':
        return <Shield className="h-5 w-5 text-blue-600" />;
      default:
        return <Shield className="h-5 w-5 text-gray-600" />;
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      intact: 'bg-green-100 text-green-800',
      broken: 'bg-red-100 text-red-800',
      tampered: 'bg-orange-100 text-orange-800',
      available: 'bg-blue-100 text-blue-800',
      in_use: 'bg-yellow-100 text-yellow-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const filteredSeals = seals.filter((seal) => {
    if (filter !== 'all' && seal.status !== filter) return false;
    if (searchTerm && !seal.seal_number.toLowerCase().includes(searchTerm.toLowerCase())) return false;
    return true;
  });

  const stats = {
    total: seals.length,
    available: seals.filter((s) => s.status === 'available').length,
    in_use: seals.filter((s) => s.status === 'in_use' || s.status === 'intact').length,
    broken: seals.filter((s) => s.status === 'broken').length,
    tampered: seals.filter((s) => s.status === 'tampered').length,
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Shield className="h-12 w-12 animate-spin mx-auto text-gray-400" />
          <p className="mt-4 text-gray-600">Loading seals...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Shield className="h-8 w-8" />
            Security Seals Management
          </h1>
          <p className="text-gray-600 mt-1">Manage security seal inventory and lifecycle</p>
        </div>
        <Button onClick={handleCreateSeal}>
          <Plus className="h-4 w-4 mr-2" />
          Add Seal to Inventory
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Total Seals</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Available</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{stats.available}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">In Use</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{stats.in_use}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Broken</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{stats.broken}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Tampered</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">{stats.tampered}</div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-4 items-center">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <input
                type="text"
                placeholder="Search by seal number..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border rounded-lg"
              />
            </div>
            <div className="flex gap-2">
              <Button
                variant={filter === 'all' ? 'default' : 'outline'}
                onClick={() => setFilter('all')}
              >
                All
              </Button>
              <Button
                variant={filter === 'available' ? 'default' : 'outline'}
                onClick={() => setFilter('available')}
              >
                Available
              </Button>
              <Button
                variant={filter === 'in_use' ? 'default' : 'outline'}
                onClick={() => setFilter('in_use')}
              >
                In Use
              </Button>
              <Button
                variant={filter === 'broken' ? 'default' : 'outline'}
                onClick={() => setFilter('broken')}
              >
                Broken
              </Button>
              <Button
                variant={filter === 'tampered' ? 'default' : 'outline'}
                onClick={() => setFilter('tampered')}
              >
                Tampered
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Seals Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredSeals.map((seal) => (
          <Card key={seal.id}>
            <CardContent className="pt-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {getSealStatusIcon(seal.status)}
                    <span className="font-bold text-lg">{seal.seal_number}</span>
                  </div>
                  <Badge className={getStatusColor(seal.status)}>
                    {seal.status.replace('_', ' ').toUpperCase()}
                  </Badge>
                </div>

                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Type:</span>
                    <span className="font-medium">{seal.seal_type.replace('_', ' ')}</span>
                  </div>

                  {seal.packet_number && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Packet:</span>
                      <button
                        onClick={() => router.push(`/gold-lending/vault/packets/${seal.packet_id}`)}
                        className="font-medium text-blue-600 hover:underline flex items-center gap-1"
                      >
                        <Package className="h-3 w-3" />
                        {seal.packet_number}
                      </button>
                    </div>
                  )}

                  {seal.applied_at && (
                    <div>
                      <span className="text-gray-600 block">Applied:</span>
                      <span className="text-xs">
                        {new Date(seal.applied_at).toLocaleString()}
                        <br />
                        By: {seal.applied_by}
                      </span>
                    </div>
                  )}

                  {seal.verified_at && (
                    <div>
                      <span className="text-gray-600 block">Verified:</span>
                      <span className="text-xs text-green-600">
                        {new Date(seal.verified_at).toLocaleString()}
                        <br />
                        By: {seal.verified_by}
                      </span>
                    </div>
                  )}

                  {seal.broken_at && (
                    <div>
                      <span className="text-gray-600 block">Broken:</span>
                      <span className="text-xs text-red-600">
                        {new Date(seal.broken_at).toLocaleString()}
                        <br />
                        By: {seal.broken_by}
                        <br />
                        Reason: {seal.break_reason}
                      </span>
                    </div>
                  )}
                </div>

                {seal.status === 'in_use' || seal.status === 'intact' ? (
                  <Button
                    size="sm"
                    variant="outline"
                    className="w-full"
                    onClick={() => handleVerifySeal(seal.id)}
                  >
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Verify Seal
                  </Button>
                ) : null}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredSeals.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center">
            <Shield className="h-12 w-12 mx-auto text-gray-400 mb-4" />
            <p className="text-gray-600">No seals found</p>
            <p className="text-sm text-gray-500 mt-2">
              {seals.length === 0
                ? 'Add seals to inventory to get started'
                : 'Try adjusting your filters'}
            </p>
            <Button onClick={handleCreateSeal} className="mt-4">
              Add First Seal
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Info Panel */}
      <Card>
        <CardHeader>
          <CardTitle>Security Seal Types</CardTitle>
          <CardDescription>Different types of security seals used in vault operations</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="border-l-4 border-blue-500 pl-4">
              <h4 className="font-semibold flex items-center gap-2">
                <Lock className="h-4 w-4" />
                Tamper Evident
              </h4>
              <p className="text-sm text-gray-600 mt-1">
                Standard seals that show visible signs of tampering. Cannot be resealed once broken.
              </p>
            </div>

            <div className="border-l-4 border-green-500 pl-4">
              <h4 className="font-semibold flex items-center gap-2">
                <Shield className="h-4 w-4" />
                Security Tag
              </h4>
              <p className="text-sm text-gray-600 mt-1">
                RFID-enabled tags for electronic tracking and verification. Requires scanner device.
              </p>
            </div>

            <div className="border-l-4 border-purple-500 pl-4">
              <h4 className="font-semibold flex items-center gap-2">
                <AlertCircle className="h-4 w-4" />
                Hologram
              </h4>
              <p className="text-sm text-gray-600 mt-1">
                High-security holographic seals with unique patterns. Extremely difficult to duplicate.
              </p>
            </div>

            <div className="border-l-4 border-orange-500 pl-4">
              <h4 className="font-semibold flex items-center gap-2">
                <Clock className="h-4 w-4" />
                Biometric
              </h4>
              <p className="text-sm text-gray-600 mt-1">
                Advanced seals with biometric verification. Requires fingerprint or iris scan to open.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Best Practices */}
      <Card>
        <CardHeader>
          <CardTitle>Seal Management Best Practices</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2 text-sm">
            <li className="flex items-start gap-2">
              <CheckCircle className="h-4 w-4 text-green-600 mt-0.5" />
              <span>Always verify seal integrity during packet movements and vault audits</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle className="h-4 w-4 text-green-600 mt-0.5" />
              <span>Document the reason for breaking seals in the system</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle className="h-4 w-4 text-green-600 mt-0.5" />
              <span>Maintain adequate inventory of seals for emergency situations</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle className="h-4 w-4 text-green-600 mt-0.5" />
              <span>Report tampered or broken seals immediately to security team</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle className="h-4 w-4 text-green-600 mt-0.5" />
              <span>Use maker-checker approval for high-value packet seal operations</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle className="h-4 w-4 text-green-600 mt-0.5" />
              <span>Conduct periodic audits of seal inventory and usage patterns</span>
            </li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
