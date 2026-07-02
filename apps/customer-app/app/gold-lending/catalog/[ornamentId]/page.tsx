'use client';

import { useParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import { goldApi } from '../../goldApi';

interface OrnamentProfile {
  ornament: any;
  photos: any[];
  stones: any[];
  status_history: any[];
  movements: any[];
  conditions: any[];
  tags: any[];
  certificates: any[];
  insurance: any;
  groups: any[];
  total_photos: number;
  total_stones: number;
  total_stone_weight: number;
  current_condition: string;
  last_movement: any;
  days_in_vault: number;
}

export default function OrnamentCatalogPage() {
  const params = useParams();
  const ornamentId = params.ornamentId as string;
  
  const [profile, setProfile] = useState<OrnamentProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (ornamentId) {
      loadOrnamentProfile();
    }
  }, [ornamentId]);

  const loadOrnamentProfile = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await goldApi.getOrnamentCompleteProfile(ornamentId);
      setProfile(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load ornament profile');
      console.error('Error loading ornament profile:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading ornament profile...</p>
        </div>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h2 className="text-red-800 font-semibold mb-2">Error Loading Profile</h2>
          <p className="text-red-600">{error || 'Profile not found'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Ornament Profile
              </h1>
              <p className="text-sm text-gray-500 mt-1">
                ID: {ornamentId}
              </p>
            </div>
            <div className="flex items-center gap-4">
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                profile.current_condition === 'excellent' ? 'bg-green-100 text-green-800' :
                profile.current_condition === 'good' ? 'bg-blue-100 text-blue-800' :
                profile.current_condition === 'fair' ? 'bg-yellow-100 text-yellow-800' :
                'bg-red-100 text-red-800'
              }`}>
                {profile.current_condition || 'Not Inspected'}
              </span>
              {profile.days_in_vault !== null && (
                <span className="text-sm text-gray-600">
                  {profile.days_in_vault} days in vault
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600 mb-1">Photos</div>
            <div className="text-2xl font-bold text-gray-900">{profile.total_photos}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600 mb-1">Stones</div>
            <div className="text-2xl font-bold text-gray-900">{profile.total_stones}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600 mb-1">Stone Weight</div>
            <div className="text-2xl font-bold text-gray-900">{profile.total_stone_weight.toFixed(3)}g</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600 mb-1">Movements</div>
            <div className="text-2xl font-bold text-gray-900">{profile.movements.length}</div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow">
          <div className="border-b">
            <nav className="flex -mb-px">
              {[
                { id: 'overview', label: 'Overview' },
                { id: 'photos', label: `Photos (${profile.total_photos})` },
                { id: 'stones', label: `Stones (${profile.total_stones})` },
                { id: 'movements', label: 'Movement History' },
                { id: 'conditions', label: 'Inspections' },
                { id: 'certificates', label: 'Certificates' },
                { id: 'insurance', label: 'Insurance' },
                { id: 'groups', label: 'Groups' },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-6 py-3 text-sm font-medium border-b-2 ${
                    activeTab === tab.id
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          <div className="p-6">
            {activeTab === 'overview' && <OverviewTab profile={profile} />}
            {activeTab === 'photos' && <PhotosTab photos={profile.photos} ornamentId={ornamentId} />}
            {activeTab === 'stones' && <StonesTab stones={profile.stones} ornamentId={ornamentId} />}
            {activeTab === 'movements' && <MovementsTab movements={profile.movements} />}
            {activeTab === 'conditions' && <ConditionsTab conditions={profile.conditions} />}
            {activeTab === 'certificates' && <CertificatesTab certificates={profile.certificates} />}
            {activeTab === 'insurance' && <InsuranceTab insurance={profile.insurance} />}
            {activeTab === 'groups' && <GroupsTab groups={profile.groups} />}
          </div>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// TAB COMPONENTS
// ============================================================================

function OverviewTab({ profile }: { profile: OrnamentProfile }) {
  return (
    <div className="space-y-6">
      {/* Basic Information */}
      <div>
        <h3 className="text-lg font-semibold mb-4">Basic Information</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-sm text-gray-600">Ornament Type</div>
            <div className="font-medium">{profile.ornament.ornament_type || 'N/A'}</div>
          </div>
          <div>
            <div className="text-sm text-gray-600">Current Status</div>
            <div className="font-medium">{profile.ornament.status || 'N/A'}</div>
          </div>
          <div>
            <div className="text-sm text-gray-600">Gross Weight</div>
            <div className="font-medium">{profile.ornament.gross_weight_grams || 0}g</div>
          </div>
          <div>
            <div className="text-sm text-gray-600">Net Weight</div>
            <div className="font-medium">{profile.ornament.net_weight_grams || 0}g</div>
          </div>
          <div>
            <div className="text-sm text-gray-600">Purity</div>
            <div className="font-medium">{profile.ornament.purity_karat || 0}K ({profile.ornament.purity_percent || 0}%)</div>
          </div>
          <div>
            <div className="text-sm text-gray-600">Appraised Value</div>
            <div className="font-medium">₹{profile.ornament.appraised_value?.toLocaleString() || 0}</div>
          </div>
        </div>
      </div>

      {/* Tags */}
      {profile.tags.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold mb-3">Tags</h3>
          <div className="flex flex-wrap gap-2">
            {profile.tags.map((tag: any) => (
              <span key={tag.id} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                {tag.tag_category}: {tag.tag_value}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Last Movement */}
      {profile.last_movement && (
        <div>
          <h3 className="text-lg font-semibold mb-3">Last Movement</h3>
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-sm text-gray-600">Movement Type</div>
                <div className="font-medium">{profile.last_movement.movement_type}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Date</div>
                <div className="font-medium">
                  {new Date(profile.last_movement.movement_timestamp).toLocaleString()}
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-600">From</div>
                <div className="font-medium">{profile.last_movement.from_location || 'N/A'}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">To</div>
                <div className="font-medium">{profile.last_movement.to_location || 'N/A'}</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function PhotosTab({ photos, ornamentId }: { photos: any[]; ornamentId: string }) {
  const primaryPhoto = photos.find(p => p.is_primary);
  const otherPhotos = photos.filter(p => !p.is_primary);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Ornament Photos</h3>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          + Add Photo
        </button>
      </div>

      {photos.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          No photos available. Add photos to create a visual catalog.
        </div>
      ) : (
        <>
          {/* Primary Photo */}
          {primaryPhoto && (
            <div className="mb-6">
              <div className="text-sm font-medium text-gray-700 mb-2">Primary Photo</div>
              <div className="relative aspect-video bg-gray-100 rounded-lg overflow-hidden">
                <img
                  src={primaryPhoto.photo_url}
                  alt="Primary ornament photo"
                  className="w-full h-full object-contain"
                />
                <div className="absolute top-2 left-2 px-2 py-1 bg-blue-600 text-white text-xs rounded">
                  {primaryPhoto.photo_type}
                </div>
              </div>
            </div>
          )}

          {/* Other Photos Grid */}
          {otherPhotos.length > 0 && (
            <div>
              <div className="text-sm font-medium text-gray-700 mb-3">Additional Photos</div>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {otherPhotos.map((photo: any) => (
                  <div key={photo.id} className="relative aspect-square bg-gray-100 rounded-lg overflow-hidden group">
                    <img
                      src={photo.photo_url}
                      alt={`Photo ${photo.photo_type}`}
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-opacity">
                      <div className="absolute top-2 left-2 px-2 py-1 bg-gray-900 bg-opacity-75 text-white text-xs rounded">
                        {photo.photo_type}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function StonesTab({ stones, ornamentId }: { stones: any[]; ornamentId: string }) {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Stone Catalog</h3>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          + Add Stone
        </button>
      </div>

      {stones.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          No stones cataloged. Add stone details for comprehensive tracking.
        </div>
      ) : (
        <div className="space-y-4">
          {stones.map((stone: any) => (
            <div key={stone.id} className="border rounded-lg p-4">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <h4 className="font-semibold text-lg">Stone #{stone.stone_number}</h4>
                  <p className="text-sm text-gray-600">{stone.stone_type}</p>
                </div>
                {stone.is_certified && (
                  <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                    Certified
                  </span>
                )}
              </div>
              
              <div className="grid grid-cols-3 md:grid-cols-5 gap-4">
                {stone.stone_shape && (
                  <div>
                    <div className="text-xs text-gray-600">Shape</div>
                    <div className="text-sm font-medium">{stone.stone_shape}</div>
                  </div>
                )}
                {stone.stone_cut && (
                  <div>
                    <div className="text-xs text-gray-600">Cut</div>
                    <div className="text-sm font-medium">{stone.stone_cut}</div>
                  </div>
                )}
                {stone.carat_weight && (
                  <div>
                    <div className="text-xs text-gray-600">Carat</div>
                    <div className="text-sm font-medium">{stone.carat_weight}</div>
                  </div>
                )}
                {stone.stone_color && (
                  <div>
                    <div className="text-xs text-gray-600">Color</div>
                    <div className="text-sm font-medium">{stone.stone_color}</div>
                  </div>
                )}
                {stone.estimated_value && (
                  <div>
                    <div className="text-xs text-gray-600">Value</div>
                    <div className="text-sm font-medium">₹{stone.estimated_value.toLocaleString()}</div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function MovementsTab({ movements }: { movements: any[] }) {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Movement History</h3>
      
      {movements.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          No movement history recorded.
        </div>
      ) : (
        <div className="space-y-3">
          {movements.map((movement: any) => (
            <div key={movement.id} className="border rounded-lg p-4 bg-white">
              <div className="flex justify-between items-start mb-2">
                <div className="flex items-center gap-2">
                  <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
                    {movement.movement_type}
                  </span>
                  {movement.verified_by_user_id && (
                    <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                      ✓ Verified
                    </span>
                  )}
                  {movement.qr_scanned && (
                    <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded">
                      QR Scanned
                    </span>
                  )}
                </div>
                <div className="text-sm text-gray-600">
                  {new Date(movement.movement_timestamp).toLocaleString()}
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <div className="text-gray-600">From</div>
                  <div className="font-medium">{movement.from_location || 'N/A'}</div>
                </div>
                <div>
                  <div className="text-gray-600">To</div>
                  <div className="font-medium">{movement.to_location || 'N/A'}</div>
                </div>
              </div>

              {(movement.gps_latitude || movement.gps_longitude) && (
                <div className="mt-2 text-sm text-gray-600">
                  GPS: {movement.gps_latitude}, {movement.gps_longitude}
                </div>
              )}

              {movement.movement_notes && (
                <div className="mt-2 text-sm text-gray-700">
                  {movement.movement_notes}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function ConditionsTab({ conditions }: { conditions: any[] }) {
  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Condition Inspections</h3>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          + New Inspection
        </button>
      </div>

      {conditions.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          No inspections recorded. Schedule regular condition checks.
        </div>
      ) : (
        <div className="space-y-4">
          {conditions.map((condition: any) => (
            <div key={condition.id} className="border rounded-lg p-4">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <div className="text-sm text-gray-600">
                    {new Date(condition.inspection_date).toLocaleDateString()}
                  </div>
                  <div className="text-lg font-semibold mt-1">
                    <span className={`px-3 py-1 rounded-full ${
                      condition.overall_condition === 'excellent' ? 'bg-green-100 text-green-800' :
                      condition.overall_condition === 'good' ? 'bg-blue-100 text-blue-800' :
                      condition.overall_condition === 'fair' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {condition.overall_condition}
                    </span>
                  </div>
                </div>
                
                <div className="flex gap-2">
                  {condition.has_damage && (
                    <span className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded">
                      Damage
                    </span>
                  )}
                  {condition.has_repair && (
                    <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded">
                      Repair
                    </span>
                  )}
                  {condition.has_missing_parts && (
                    <span className="px-2 py-1 bg-orange-100 text-orange-800 text-xs rounded">
                      Missing Parts
                    </span>
                  )}
                </div>
              </div>

              {condition.damage_description && (
                <div className="mb-2">
                  <div className="text-sm font-medium text-red-700">Damage:</div>
                  <div className="text-sm text-gray-700">{condition.damage_description}</div>
                </div>
              )}

              <div className="grid grid-cols-3 gap-3 text-sm">
                {condition.stone_condition && (
                  <div>
                    <div className="text-gray-600">Stone Condition</div>
                    <div className="font-medium">{condition.stone_condition}</div>
                  </div>
                )}
                {condition.clasp_condition && (
                  <div>
                    <div className="text-gray-600">Clasp Condition</div>
                    <div className="font-medium">{condition.clasp_condition}</div>
                  </div>
                )}
                {condition.polish_level && (
                  <div>
                    <div className="text-gray-600">Polish Level</div>
                    <div className="font-medium">{condition.polish_level}</div>
                  </div>
                )}
              </div>

              {condition.next_inspection_date && (
                <div className="mt-3 pt-3 border-t text-sm">
                  <span className="text-gray-600">Next Inspection: </span>
                  <span className="font-medium">
                    {new Date(condition.next_inspection_date).toLocaleDateString()}
                  </span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function CertificatesTab({ certificates }: { certificates: any[] }) {
  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Certificates</h3>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          + Add Certificate
        </button>
      </div>

      {certificates.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          No certificates on file. Add hallmark, BIS, or purity certificates.
        </div>
      ) : (
        <div className="grid gap-4">
          {certificates.map((cert: any) => (
            <div key={cert.id} className="border rounded-lg p-4">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <div className="font-semibold text-lg">{cert.certificate_type}</div>
                  <div className="text-sm text-gray-600">#{cert.certificate_number}</div>
                </div>
                {cert.is_verified ? (
                  <span className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full">
                    ✓ Verified
                  </span>
                ) : (
                  <span className="px-3 py-1 bg-yellow-100 text-yellow-800 text-sm rounded-full">
                    Unverified
                  </span>
                )}
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <div className="text-gray-600">Issuing Authority</div>
                  <div className="font-medium">{cert.issuing_authority}</div>
                </div>
                <div>
                  <div className="text-gray-600">Issued Date</div>
                  <div className="font-medium">
                    {new Date(cert.issued_date).toLocaleDateString()}
                  </div>
                </div>
                {cert.expiry_date && (
                  <div>
                    <div className="text-gray-600">Expiry Date</div>
                    <div className="font-medium">
                      {new Date(cert.expiry_date).toLocaleDateString()}
                    </div>
                  </div>
                )}
                {cert.verification_method && (
                  <div>
                    <div className="text-gray-600">Verification Method</div>
                    <div className="font-medium">{cert.verification_method}</div>
                  </div>
                )}
              </div>

              {cert.certificate_url && (
                <div className="mt-3 pt-3 border-t">
                  <a
                    href={cert.certificate_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 text-sm"
                  >
                    View Certificate →
                  </a>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function InsuranceTab({ insurance }: { insurance: any }) {
  if (!insurance) {
    return (
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h3 className="text-lg font-semibold">Insurance</h3>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            + Add Insurance
          </button>
        </div>
        <div className="text-center py-12 text-gray-500">
          No active insurance policy. Add insurance for comprehensive protection.
        </div>
      </div>
    );
  }

  const isExpiringSoon = insurance.policy_end_date && 
    new Date(insurance.policy_end_date) <= new Date(Date.now() + 30 * 24 * 60 * 60 * 1000);

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Insurance Policy</h3>
        {insurance.is_active ? (
          <span className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full">
            Active
          </span>
        ) : (
          <span className="px-3 py-1 bg-red-100 text-red-800 text-sm rounded-full">
            Inactive
          </span>
        )}
      </div>

      {isExpiringSoon && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="font-medium text-yellow-800">
            ⚠️ Policy expiring soon - Renew before {new Date(insurance.policy_end_date).toLocaleDateString()}
          </div>
        </div>
      )}

      <div className="border rounded-lg p-6">
        <div className="grid grid-cols-2 gap-6">
          <div>
            <div className="text-sm text-gray-600">Policy Number</div>
            <div className="font-semibold text-lg">{insurance.policy_number}</div>
          </div>
          <div>
            <div className="text-sm text-gray-600">Provider</div>
            <div className="font-semibold text-lg">{insurance.insurance_provider}</div>
          </div>
          <div>
            <div className="text-sm text-gray-600">Insured Value</div>
            <div className="font-semibold text-lg">₹{insurance.insured_value.toLocaleString()}</div>
          </div>
          {insurance.premium_amount && (
            <div>
              <div className="text-sm text-gray-600">Premium</div>
              <div className="font-semibold text-lg">₹{insurance.premium_amount.toLocaleString()}</div>
            </div>
          )}
          <div>
            <div className="text-sm text-gray-600">Start Date</div>
            <div className="font-medium">{new Date(insurance.policy_start_date).toLocaleDateString()}</div>
          </div>
          <div>
            <div className="text-sm text-gray-600">End Date</div>
            <div className="font-medium">{new Date(insurance.policy_end_date).toLocaleDateString()}</div>
          </div>
          {insurance.coverage_type && (
            <div className="col-span-2">
              <div className="text-sm text-gray-600">Coverage Type</div>
              <div className="font-medium">{insurance.coverage_type}</div>
            </div>
          )}
        </div>

        {insurance.policy_document_url && (
          <div className="mt-4 pt-4 border-t">
            <a
              href={insurance.policy_document_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800"
            >
              View Policy Document →
            </a>
          </div>
        )}

        {insurance.claim_history && insurance.claim_history.length > 0 && (
          <div className="mt-4 pt-4 border-t">
            <div className="text-sm font-medium text-gray-700 mb-2">Claim History</div>
            <div className="space-y-2">
              {insurance.claim_history.map((claim: any, idx: number) => (
                <div key={idx} className="bg-gray-50 rounded p-3 text-sm">
                  <div className="font-medium">{claim.claim_number}</div>
                  <div className="text-gray-600">{claim.status} - ₹{claim.amount?.toLocaleString()}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function GroupsTab({ groups }: { groups: any[] }) {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Ornament Groups</h3>

      {groups.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          Not part of any group. Groups help organize sets and collections.
        </div>
      ) : (
        <div className="space-y-3">
          {groups.map((group: any) => (
            <div key={group.id} className="border rounded-lg p-4">
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h4 className="font-semibold text-lg">{group.group_name}</h4>
                  {group.group_type && (
                    <div className="text-sm text-gray-600 mt-1">{group.group_type}</div>
                  )}
                </div>
                <span className="px-2 py-1 bg-blue-100 text-blue-800 text-sm rounded">
                  {group.total_ornaments} items
                </span>
              </div>
              
              {group.description && (
                <p className="text-sm text-gray-700 mb-3">{group.description}</p>
              )}

              <div className="grid grid-cols-3 gap-4 text-sm">
                {group.total_weight_grams && (
                  <div>
                    <div className="text-gray-600">Total Weight</div>
                    <div className="font-medium">{group.total_weight_grams}g</div>
                  </div>
                )}
                {group.total_value && (
                  <div>
                    <div className="text-gray-600">Total Value</div>
                    <div className="font-medium">₹{group.total_value.toLocaleString()}</div>
                  </div>
                )}
                <div>
                  <div className="text-gray-600">Created</div>
                  <div className="font-medium">
                    {new Date(group.created_at).toLocaleDateString()}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
