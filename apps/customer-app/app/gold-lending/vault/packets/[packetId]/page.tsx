'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/app/components/eds/card';
import { Button } from '@/app/components/eds/button';
import { Badge } from '@/app/components/eds/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/app/components/eds/tabs';
import {
  Package,
  QrCode,
  MapPin,
  Shield,
  Clock,
  AlertCircle,
  CheckCircle,
  XCircle,
  Download,
  Scan,
  Lock,
  Unlock,
  TrendingUp,
  FileText,
  History,
} from 'lucide-react';
import { goldApi } from '../../goldApi';

interface Packet {
  id: string;
  packet_number: string;
  qr_code: string;
  status: string;
  vault_id?: string;
  rack_id?: string;
  locker_id?: string;
  tray_id?: string;
  current_location: string;
  ornament_count: number;
  total_weight: number;
  total_value: number;
  seal_number?: string;
  seal_status?: string;
  sealed_at?: string;
  sealed_by?: string;
  created_at: string;
  created_by: string;
}

interface PacketOrnament {
  id: string;
  ornament_id: string;
  ornament_type: string;
  gross_weight: number;
  net_weight: number;
  purity: number;
  valuation_amount: number;
  added_at: string;
  added_by: string;
}

interface Movement {
  id: string;
  movement_type: string;
  from_location?: string;
  to_location?: string;
  reason: string;
  performed_by: string;
  performed_at: string;
  notes?: string;
}

interface SecuritySeal {
  id: string;
  seal_number: string;
  seal_type: string;
  status: string;
  applied_at: string;
  applied_by: string;
  verified_at?: string;
  verified_by?: string;
  broken_at?: string;
  broken_by?: string;
  break_reason?: string;
}

export default function PacketDetailPage() {
  const params = useParams();
  const router = useRouter();
  const packetId = params.packetId as string;

  const [packet, setPacket] = useState<Packet | null>(null);
  const [ornaments, setOrnaments] = useState<PacketOrnament[]>([]);
  const [movements, setMovements] = useState<Movement[]>([]);
  const [seals, setSeals] = useState<SecuritySeal[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadPacketData();
  }, [packetId]);

  const loadPacketData = async () => {
    try {
      setLoading(true);
      const [packetData, ornamentsData, movementsData, sealsData] = await Promise.all([
        goldApi.getPacket(packetId),
        goldApi.getPacketOrnaments(packetId),
        goldApi.getPacketMovements(packetId),
        goldApi.getPacketSeals(packetId),
      ]);

      setPacket(packetData);
      setOrnaments(ornamentsData);
      setMovements(movementsData);
      setSeals(sealsData);
    } catch (error) {
      console.error('Failed to load packet data:', error);
    } finally {
      setLoading(false);
    }
  };

  const downloadQRCode = () => {
    if (!packet) return;

    const link = document.createElement('a');
    link.href = packet.qr_code;
    link.download = `packet-${packet.packet_number}-qr.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleSealPacket = async () => {
    if (!packet) return;

    const sealNumber = prompt('Enter seal number:');
    if (!sealNumber) return;

    try {
      await goldApi.sealPacket(packetId, {
        seal_number: sealNumber,
        seal_type: 'tamper_evident',
        sealed_by: 'current-user-id', // Replace with actual user ID
      });
      await loadPacketData();
      alert('Packet sealed successfully');
    } catch (error) {
      console.error('Failed to seal packet:', error);
      alert('Failed to seal packet');
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
      await loadPacketData();
      alert('Seal verification recorded');
    } catch (error) {
      console.error('Failed to verify seal:', error);
      alert('Failed to verify seal');
    }
  };

  const handleBreakSeal = async (sealId: string) => {
    if (!confirm('Are you sure you want to break this seal?')) return;

    const reason = prompt('Enter reason for breaking seal:');
    if (!reason) return;

    try {
      await goldApi.breakSeal(sealId, {
        broken_by: 'current-user-id', // Replace with actual user ID
        break_reason: reason,
      });
      await loadPacketData();
      alert('Seal broken successfully');
    } catch (error) {
      console.error('Failed to break seal:', error);
      alert('Failed to break seal');
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      active: 'bg-green-100 text-green-800',
      sealed: 'bg-blue-100 text-blue-800',
      in_transit: 'bg-yellow-100 text-yellow-800',
      archived: 'bg-gray-100 text-gray-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getSealStatusIcon = (status: string) => {
    switch (status) {
      case 'intact':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'broken':
        return <XCircle className="h-5 w-5 text-red-600" />;
      case 'tampered':
        return <AlertCircle className="h-5 w-5 text-orange-600" />;
      default:
        return <Shield className="h-5 w-5 text-gray-600" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Package className="h-12 w-12 animate-spin mx-auto text-gray-400" />
          <p className="mt-4 text-gray-600">Loading packet details...</p>
        </div>
      </div>
    );
  }

  if (!packet) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 mx-auto text-red-400" />
          <p className="mt-4 text-gray-600">Packet not found</p>
          <Button onClick={() => router.back()} className="mt-4">
            Go Back
          </Button>
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
            <Package className="h-8 w-8" />
            Packet {packet.packet_number}
          </h1>
          <p className="text-gray-600 mt-1">
            {packet.ornament_count} ornaments • {packet.total_weight.toFixed(2)}g • ₹{packet.total_value.toLocaleString()}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge className={getStatusColor(packet.status)}>
            {packet.status.replace('_', ' ').toUpperCase()}
          </Badge>
          {packet.seal_status && (
            <Badge className="flex items-center gap-1">
              {getSealStatusIcon(packet.seal_status)}
              {packet.seal_status.toUpperCase()}
            </Badge>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="flex gap-2">
        <Button onClick={downloadQRCode} variant="outline">
          <Download className="h-4 w-4 mr-2" />
          Download QR
        </Button>
        {packet.status !== 'sealed' && (
          <Button onClick={handleSealPacket} variant="outline">
            <Lock className="h-4 w-4 mr-2" />
            Seal Packet
          </Button>
        )}
        <Button variant="outline">
          <Scan className="h-4 w-4 mr-2" />
          Scan QR
        </Button>
      </div>

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="ornaments">Ornaments ({ornaments.length})</TabsTrigger>
          <TabsTrigger value="movements">Movement History ({movements.length})</TabsTrigger>
          <TabsTrigger value="seals">Security Seals ({seals.length})</TabsTrigger>
          <TabsTrigger value="qr">QR Code</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium">Current Location</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2">
                  <MapPin className="h-5 w-5 text-gray-400" />
                  <span className="font-semibold">{packet.current_location}</span>
                </div>
                <div className="mt-2 text-xs text-gray-600">
                  {packet.vault_id && <div>Vault: {packet.vault_id}</div>}
                  {packet.rack_id && <div>Rack: {packet.rack_id}</div>}
                  {packet.locker_id && <div>Locker: {packet.locker_id}</div>}
                  {packet.tray_id && <div>Tray: {packet.tray_id}</div>}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium">Contents Summary</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Ornaments:</span>
                    <span className="font-semibold">{packet.ornament_count}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Total Weight:</span>
                    <span className="font-semibold">{packet.total_weight.toFixed(2)}g</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Total Value:</span>
                    <span className="font-semibold">₹{packet.total_value.toLocaleString()}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium">Security Status</CardTitle>
              </CardHeader>
              <CardContent>
                {packet.seal_number ? (
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      {getSealStatusIcon(packet.seal_status || 'unknown')}
                      <span className="font-semibold">{packet.seal_status?.toUpperCase()}</span>
                    </div>
                    <div className="text-xs text-gray-600">
                      <div>Seal: {packet.seal_number}</div>
                      <div>Sealed: {new Date(packet.sealed_at || '').toLocaleString()}</div>
                      <div>By: {packet.sealed_by}</div>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-center gap-2 text-gray-500">
                    <Unlock className="h-5 w-5" />
                    <span>Not sealed</span>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Packet Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="text-sm text-gray-600">Packet ID:</span>
                  <p className="font-mono text-sm">{packet.id}</p>
                </div>
                <div>
                  <span className="text-sm text-gray-600">Packet Number:</span>
                  <p className="font-semibold">{packet.packet_number}</p>
                </div>
                <div>
                  <span className="text-sm text-gray-600">Created At:</span>
                  <p className="text-sm">{new Date(packet.created_at).toLocaleString()}</p>
                </div>
                <div>
                  <span className="text-sm text-gray-600">Created By:</span>
                  <p className="text-sm">{packet.created_by}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Ornaments Tab */}
        <TabsContent value="ornaments" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Ornaments in Packet ({ornaments.length})</CardTitle>
              <CardDescription>All ornaments stored in this packet</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-2">Ornament ID</th>
                      <th className="text-left p-2">Type</th>
                      <th className="text-right p-2">Gross Weight</th>
                      <th className="text-right p-2">Net Weight</th>
                      <th className="text-right p-2">Purity</th>
                      <th className="text-right p-2">Value</th>
                      <th className="text-left p-2">Added</th>
                    </tr>
                  </thead>
                  <tbody>
                    {ornaments.map((ornament) => (
                      <tr key={ornament.id} className="border-b hover:bg-gray-50">
                        <td className="p-2">
                          <button
                            onClick={() => router.push(`/gold-lending/catalog/${ornament.ornament_id}`)}
                            className="text-blue-600 hover:underline font-mono text-sm"
                          >
                            {ornament.ornament_id.substring(0, 8)}...
                          </button>
                        </td>
                        <td className="p-2">{ornament.ornament_type}</td>
                        <td className="p-2 text-right">{ornament.gross_weight.toFixed(2)}g</td>
                        <td className="p-2 text-right">{ornament.net_weight.toFixed(2)}g</td>
                        <td className="p-2 text-right">{ornament.purity}K</td>
                        <td className="p-2 text-right">₹{ornament.valuation_amount.toLocaleString()}</td>
                        <td className="p-2 text-xs text-gray-600">
                          {new Date(ornament.added_at).toLocaleDateString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Movement History Tab */}
        <TabsContent value="movements" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Movement History ({movements.length})</CardTitle>
              <CardDescription>Complete audit trail of packet movements</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {movements.map((movement) => (
                  <div key={movement.id} className="border-l-4 border-blue-500 pl-4 py-2">
                    <div className="flex items-center gap-2 mb-1">
                      <History className="h-4 w-4 text-gray-400" />
                      <span className="font-semibold">{movement.movement_type.replace('_', ' ').toUpperCase()}</span>
                      <span className="text-xs text-gray-500">
                        {new Date(movement.performed_at).toLocaleString()}
                      </span>
                    </div>
                    <div className="text-sm text-gray-600">
                      {movement.from_location && (
                        <div>From: <span className="font-medium">{movement.from_location}</span></div>
                      )}
                      {movement.to_location && (
                        <div>To: <span className="font-medium">{movement.to_location}</span></div>
                      )}
                      <div>Reason: {movement.reason}</div>
                      <div>By: {movement.performed_by}</div>
                      {movement.notes && <div className="mt-1 italic">{movement.notes}</div>}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Security Seals Tab */}
        <TabsContent value="seals" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Security Seals ({seals.length})</CardTitle>
              <CardDescription>All seals applied to this packet</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {seals.map((seal) => (
                  <Card key={seal.id}>
                    <CardContent className="pt-6">
                      <div className="flex items-start justify-between">
                        <div className="space-y-2">
                          <div className="flex items-center gap-2">
                            {getSealStatusIcon(seal.status)}
                            <span className="font-bold text-lg">{seal.seal_number}</span>
                            <Badge>{seal.seal_type.replace('_', ' ')}</Badge>
                          </div>
                          <div className="text-sm space-y-1">
                            <div className="text-gray-600">
                              Applied: {new Date(seal.applied_at).toLocaleString()} by {seal.applied_by}
                            </div>
                            {seal.verified_at && (
                              <div className="text-green-600">
                                Verified: {new Date(seal.verified_at).toLocaleString()} by {seal.verified_by}
                              </div>
                            )}
                            {seal.broken_at && (
                              <div className="text-red-600">
                                Broken: {new Date(seal.broken_at).toLocaleString()} by {seal.broken_by}
                                <br />
                                Reason: {seal.break_reason}
                              </div>
                            )}
                          </div>
                        </div>
                        <div className="flex gap-2">
                          {seal.status === 'intact' && (
                            <>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleVerifySeal(seal.id)}
                              >
                                Verify
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleBreakSeal(seal.id)}
                              >
                                Break Seal
                              </Button>
                            </>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* QR Code Tab */}
        <TabsContent value="qr" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Packet QR Code</CardTitle>
              <CardDescription>Scan this code to quickly access packet details</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col items-center justify-center py-8">
              <div className="border-4 border-gray-200 rounded-lg p-4 bg-white">
                <img
                  src={packet.qr_code}
                  alt={`QR Code for ${packet.packet_number}`}
                  className="w-64 h-64"
                />
              </div>
              <div className="mt-4 text-center">
                <p className="font-mono text-lg font-bold">{packet.packet_number}</p>
                <p className="text-sm text-gray-600 mt-1">Packet ID: {packet.id}</p>
              </div>
              <Button onClick={downloadQRCode} className="mt-6">
                <Download className="h-4 w-4 mr-2" />
                Download QR Code
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
