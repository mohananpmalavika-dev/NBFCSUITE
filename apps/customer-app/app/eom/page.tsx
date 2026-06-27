'use client';

import { useAuth } from '@/lib/auth-context';
import { apiClient } from '@/lib/api';
import { useCallback, useEffect, useMemo, useState } from 'react';

interface Customer {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  branch_id?: string | null;
}

interface Branch {
  id: string;
  branch_code: string;
  branch_name: string;
  area_id?: string | null;
  region_id?: string | null;
  zone_id?: string | null;
}

interface EomBrand {
  id: string;
  brand_code: string;
  brand_name: string;
}

interface EomLegalEntity {
  id: string;
  brand_id: string;
  entity_code: string;
  entity_name: string;
}

interface EomBusinessUnit {
  id: string;
  legal_entity_id: string;
  business_unit_code: string;
  business_unit_name: string;
}

interface EomZone {
  id: string;
  business_unit_id: string;
  zone_code: string;
  zone_name: string;
}

interface EomRegion {
  id: string;
  zone_id: string;
  region_code: string;
  region_name: string;
}

interface EomArea {
  id: string;
  region_id: string;
  area_code: string;
  area_name: string;
}

interface EomCluster {
  id: string;
  area_id: string;
  cluster_code: string;
  cluster_name: string;
}

interface CustomerBranchMapping {
  id: string;
  customer_id: string;
  branch_id: string;
  status: string;
  effective_from: string;
  effective_to?: string | null;
  transferred_from_branch_id?: string | null;
  transferred_by?: string | null;
}

export default function EomPage() {
  const { user, token, isLoading } = useAuth();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [brands, setBrands] = useState<EomBrand[]>([]);
  const [legalEntities, setLegalEntities] = useState<EomLegalEntity[]>([]);
  const [businessUnits, setBusinessUnits] = useState<EomBusinessUnit[]>([]);
  const [zones, setZones] = useState<EomZone[]>([]);
  const [regions, setRegions] = useState<EomRegion[]>([]);
  const [areas, setAreas] = useState<EomArea[]>([]);
  const [clusters, setClusters] = useState<EomCluster[]>([]);
  const [selectedCustomerId, setSelectedCustomerId] = useState('');
  const [selectedBranchId, setSelectedBranchId] = useState('');
  const [mappingHistory, setMappingHistory] = useState<CustomerBranchMapping[]>([]);
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);

  const [newBrand, setNewBrand] = useState({
    brand_code: '',
    brand_name: '',
    legal_name: '',
    short_name: '',
    email: '',
    phone: '',
  });
  const [newLegalEntity, setNewLegalEntity] = useState({
    brand_id: '',
    entity_code: '',
    entity_name: '',
    entity_type: 'company',
    registered_address: '',
    state: '',
    country: '',
  });
  const [newBusinessUnit, setNewBusinessUnit] = useState({
    legal_entity_id: '',
    business_unit_code: '',
    business_unit_name: '',
    head: '',
  });
  const [newZone, setNewZone] = useState({
    business_unit_id: '',
    zone_code: '',
    zone_name: '',
    zone_head: '',
  });
  const [newRegion, setNewRegion] = useState({
    zone_id: '',
    region_code: '',
    region_name: '',
    regional_manager: '',
    office_address: '',
  });
  const [newArea, setNewArea] = useState({
    region_id: '',
    area_code: '',
    area_name: '',
    area_manager: '',
    office_address: '',
  });
  const [newCluster, setNewCluster] = useState({
    area_id: '',
    cluster_code: '',
    cluster_name: '',
    cluster_manager: '',
  });
  const [newBranch, setNewBranch] = useState({
    area_id: '',
    branch_code: '',
    branch_name: '',
    short_name: '',
    zone_id: '',
    region_id: '',
    cluster_id: '',
  });

  const selectedCustomer = useMemo(
    () => customers.find((customer) => customer.id === selectedCustomerId),
    [customers, selectedCustomerId],
  );
  const branchMap = useMemo(
    () => new Map(branches.map((branch) => [branch.id, branch.branch_name])),
    [branches],
  );

  const loadEomData = useCallback(async () => {
    if (!token) return;
    setMessage('');
    try {
      const [
        customersRes,
        brandsRes,
        legalEntitiesRes,
        businessUnitsRes,
        zonesRes,
        regionsRes,
        areasRes,
        clustersRes,
        branchesRes,
      ] = await Promise.all([
        apiClient.getCustomers(),
        apiClient.getEomBrands(),
        apiClient.getEomLegalEntities(),
        apiClient.getEomBusinessUnits(),
        apiClient.getEomZones(),
        apiClient.getEomRegions(),
        apiClient.getEomAreas(),
        apiClient.getEomClusters(),
        apiClient.getEomBranches(),
      ]);

      const loadedCustomers = Array.isArray(customersRes.data.items)
        ? customersRes.data.items
        : customersRes.data || [];

      setCustomers(loadedCustomers);
      setBrands(brandsRes.data || []);
      setLegalEntities(legalEntitiesRes.data || []);
      setBusinessUnits(businessUnitsRes.data || []);
      setZones(zonesRes.data || []);
      setRegions(regionsRes.data || []);
      setAreas(areasRes.data || []);
      setClusters(clustersRes.data || []);
      setBranches(branchesRes.data || []);

      if (!selectedCustomerId && loadedCustomers.length > 0) {
        setSelectedCustomerId(loadedCustomers[0].id);
      }

      if (!selectedBranchId && Array.isArray(branchesRes.data) && branchesRes.data.length > 0) {
        setSelectedBranchId(branchesRes.data[0].id);
      }

      if (Array.isArray(businessUnitsRes.data) && businessUnitsRes.data.length > 0) {
        setNewZone((current) => ({ ...current, business_unit_id: current.business_unit_id || businessUnitsRes.data[0].id }));
      }
      if (Array.isArray(zonesRes.data) && zonesRes.data.length > 0) {
        setNewRegion((current) => ({ ...current, zone_id: current.zone_id || zonesRes.data[0].id }));
      }
      if (Array.isArray(regionsRes.data) && regionsRes.data.length > 0) {
        setNewArea((current) => ({ ...current, region_id: current.region_id || regionsRes.data[0].id }));
      }
      if (Array.isArray(areasRes.data) && areasRes.data.length > 0) {
        setNewCluster((current) => ({ ...current, area_id: current.area_id || areasRes.data[0].id }));
        setNewBranch((current) => ({ ...current, area_id: current.area_id || areasRes.data[0].id }));
      }
    } catch (error) {
      setMessage('Unable to load EOM data.');
    }
  }, [selectedBranchId, selectedCustomerId, token]);

  const loadMappingHistory = useCallback(async () => {
    if (!token || !selectedCustomerId) {
      setMappingHistory([]);
      return;
    }
    try {
      const mappingRes = await apiClient.getCustomerBranchMapping(selectedCustomerId);
      setMappingHistory(mappingRes.data || []);
    } catch (error) {
      setMappingHistory([]);
    }
  }, [selectedCustomerId, token]);

  useEffect(() => {
    loadEomData();
  }, [loadEomData]);

  useEffect(() => {
    loadMappingHistory();
  }, [loadMappingHistory]);

  const createBrand = async () => {
    setBusy(true);
    setMessage('');
    try {
      await apiClient.createEomBrand({
        tenant_id: 'default',
        ...newBrand,
      });
      setMessage('Brand created successfully.');
      setNewBrand({ brand_code: '', brand_name: '', legal_name: '', short_name: '', email: '', phone: '' });
      await loadEomData();
    } catch (error: any) {
      setMessage(error?.response?.data?.detail ?? 'Brand creation failed.');
    } finally {
      setBusy(false);
    }
  };

  const createLegalEntity = async () => {
    setBusy(true);
    setMessage('');
    try {
      await apiClient.createEomLegalEntity({
        tenant_id: 'default',
        ...newLegalEntity,
      });
      setMessage('Legal entity created successfully.');
      setNewLegalEntity({
        brand_id: newLegalEntity.brand_id,
        entity_code: '',
        entity_name: '',
        entity_type: 'company',
        registered_address: '',
        state: '',
        country: '',
      });
      await loadEomData();
    } catch (error: any) {
      setMessage(error?.response?.data?.detail ?? 'Legal entity creation failed.');
    } finally {
      setBusy(false);
    }
  };

  const createBusinessUnit = async () => {
    setBusy(true);
    setMessage('');
    try {
      await apiClient.createEomBusinessUnit({
        tenant_id: 'default',
        ...newBusinessUnit,
      });
      setMessage('Business unit created successfully.');
      setNewBusinessUnit({ legal_entity_id: newBusinessUnit.legal_entity_id, business_unit_code: '', business_unit_name: '', head: '' });
      await loadEomData();
    } catch (error: any) {
      setMessage(error?.response?.data?.detail ?? 'Business unit creation failed.');
    } finally {
      setBusy(false);
    }
  };

  const createZone = async () => {
    setBusy(true);
    setMessage('');
    try {
      await apiClient.createEomZone({
        tenant_id: 'default',
        ...newZone,
      });
      setMessage('Zone created successfully.');
      setNewZone({ business_unit_id: newZone.business_unit_id, zone_code: '', zone_name: '', zone_head: '' });
      await loadEomData();
    } catch (error: any) {
      setMessage(error?.response?.data?.detail ?? 'Zone creation failed.');
    } finally {
      setBusy(false);
    }
  };

  const createRegion = async () => {
    setBusy(true);
    setMessage('');
    try {
      await apiClient.createEomRegion({
        tenant_id: 'default',
        ...newRegion,
      });
      setMessage('Region created successfully.');
      setNewRegion({ zone_id: newRegion.zone_id, region_code: '', region_name: '', regional_manager: '', office_address: '' });
      await loadEomData();
    } catch (error: any) {
      setMessage(error?.response?.data?.detail ?? 'Region creation failed.');
    } finally {
      setBusy(false);
    }
  };

  const createArea = async () => {
    setBusy(true);
    setMessage('');
    try {
      await apiClient.createEomArea({
        tenant_id: 'default',
        ...newArea,
      });
      setMessage('Area created successfully.');
      setNewArea({ region_id: newArea.region_id, area_code: '', area_name: '', area_manager: '', office_address: '' });
      await loadEomData();
    } catch (error: any) {
      setMessage(error?.response?.data?.detail ?? 'Area creation failed.');
    } finally {
      setBusy(false);
    }
  };

  const createCluster = async () => {
    setBusy(true);
    setMessage('');
    try {
      await apiClient.createEomCluster({
        tenant_id: 'default',
        ...newCluster,
      });
      setMessage('Cluster created successfully.');
      setNewCluster({ area_id: newCluster.area_id, cluster_code: '', cluster_name: '', cluster_manager: '' });
      await loadEomData();
    } catch (error: any) {
      setMessage(error?.response?.data?.detail ?? 'Cluster creation failed.');
    } finally {
      setBusy(false);
    }
  };

  const createBranch = async () => {
    setBusy(true);
    setMessage('');
    try {
      await apiClient.createEomBranch({
        tenant_id: 'default',
        ...newBranch,
      });
      setMessage('Branch created successfully.');
      setNewBranch({ area_id: newBranch.area_id, branch_code: '', branch_name: '', short_name: '', zone_id: newBranch.zone_id, region_id: newBranch.region_id, cluster_id: newBranch.cluster_id });
      await loadEomData();
    } catch (error: any) {
      setMessage(error?.response?.data?.detail ?? 'Branch creation failed.');
    } finally {
      setBusy(false);
    }
  };

  const assignBranch = async () => {
    if (!selectedCustomerId || !selectedBranchId || !user) {
      return;
    }
    setBusy(true);
    setMessage('');
    try {
      await apiClient.assignCustomerBranch(
        selectedCustomerId,
        selectedBranchId,
        user.username || 'system',
        'default',
      );
      setMessage('Customer branch assignment saved.');
      await loadMappingHistory();
    } catch (error: any) {
      setMessage(error?.response?.data?.detail ?? 'Assignment failed.');
    } finally {
      setBusy(false);
    }
  };

  if (isLoading || !token) {
    return <div className="p-8 text-center">Loading...</div>;
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-8">
      <div className="mx-auto max-w-7xl space-y-6">
        <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <h1 className="text-3xl font-bold text-slate-950">EOM Master Data</h1>
          <p className="mt-2 text-sm text-slate-600">
            Manage enterprise organisation branches and assign customers to EOM branches.
          </p>
        </section>

        {message && (
          <div className="rounded-md border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-900">
            {message}
          </div>
        )}

        <section className="grid gap-6 xl:grid-cols-[1.4fr_1fr]">
          <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-xl font-semibold text-slate-950">Branch Assignment</h2>

            <label className="mb-4 block">
              <span className="mb-1 block text-sm font-medium text-slate-700">Customer</span>
              <select
                value={selectedCustomerId}
                onChange={(event) => setSelectedCustomerId(event.target.value)}
                className="w-full rounded-md border border-slate-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
              >
                <option value="">Select customer</option>
                {customers.map((customer) => (
                  <option key={customer.id} value={customer.id}>
                    {customer.first_name} {customer.last_name} ({customer.email || customer.phone})
                  </option>
                ))}
              </select>
            </label>

            <label className="mb-4 block">
              <span className="mb-1 block text-sm font-medium text-slate-700">EOM Branch</span>
              <select
                value={selectedBranchId}
                onChange={(event) => setSelectedBranchId(event.target.value)}
                className="w-full rounded-md border border-slate-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
              >
                <option value="">Select branch</option>
                {branches.map((branch) => (
                  <option key={branch.id} value={branch.id}>
                    {branch.branch_name} {branch.branch_code ? `(${branch.branch_code})` : ''}
                  </option>
                ))}
              </select>
            </label>

            <button
              type="button"
              disabled={busy || !selectedCustomerId || !selectedBranchId}
              onClick={assignBranch}
              className="inline-flex items-center justify-center rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {busy ? 'Assigning…' : 'Assign Branch'}
            </button>

            <div className="mt-8">
              <h3 className="mb-3 text-lg font-semibold text-slate-950">Selected Customer Details</h3>
              <dl className="grid gap-3 sm:grid-cols-2">
                <div>
                  <dt className="text-xs font-semibold uppercase tracking-wide text-slate-500">Name</dt>
                  <dd className="mt-1 text-sm text-slate-700">
                    {selectedCustomer ? `${selectedCustomer.first_name} ${selectedCustomer.last_name}` : '-'}
                  </dd>
                </div>
                <div>
                  <dt className="text-xs font-semibold uppercase tracking-wide text-slate-500">Email / Phone</dt>
                  <dd className="mt-1 text-sm text-slate-700">
                    {selectedCustomer ? selectedCustomer.email || selectedCustomer.phone : '-'}
                  </dd>
                </div>
                <div>
                  <dt className="text-xs font-semibold uppercase tracking-wide text-slate-500">Legacy branch</dt>
                  <dd className="mt-1 text-sm text-slate-700">{selectedCustomer?.branch_id || 'None'}</dd>
                </div>
              </dl>
            </div>
          </div>

          <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-xl font-semibold text-slate-950">Customer Branch Mapping</h2>
            {selectedCustomerId ? (
              <div className="space-y-3">
                {mappingHistory.length === 0 ? (
                  <p className="rounded-md bg-slate-50 p-4 text-sm text-slate-600">No mapping history found for this customer.</p>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full min-w-[520px] text-sm">
                      <thead>
                        <tr className="border-b border-slate-200 text-left text-slate-500">
                          <th className="px-3 py-3">Branch</th>
                          <th className="px-3 py-3">Status</th>
                          <th className="px-3 py-3">From</th>
                          <th className="px-3 py-3">To</th>
                          <th className="px-3 py-3">Transferred By</th>
                        </tr>
                      </thead>
                      <tbody>
                        {mappingHistory.map((item) => (
                          <tr key={item.id} className="border-b border-slate-100">
                            <td className="px-3 py-3 text-slate-700">
                              {branchMap.get(item.branch_id) || item.branch_id}
                            </td>
                            <td className="px-3 py-3 capitalize text-slate-700">{item.status}</td>
                            <td className="px-3 py-3 text-slate-700">{new Date(item.effective_from).toLocaleString()}</td>
                            <td className="px-3 py-3 text-slate-700">
                              {item.effective_to ? new Date(item.effective_to).toLocaleString() : '-'}
                            </td>
                            <td className="px-3 py-3 text-slate-700">{item.transferred_by || '-'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            ) : (
              <p className="rounded-md bg-slate-50 p-4 text-sm text-slate-600">Select a customer to view mapping history.</p>
            )}
          </div>
        </section>

        <section className="grid gap-6 xl:grid-cols-[1fr_1fr]">
          <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-xl font-semibold text-slate-950">Create EOM Master Data</h2>

            <div className="space-y-6">
              <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                <h3 className="mb-3 text-lg font-semibold text-slate-950">Brand</h3>
                <div className="grid gap-3 sm:grid-cols-2">
                  <label className="block">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Brand Code</span>
                    <input
                      value={newBrand.brand_code}
                      onChange={(event) => setNewBrand({ ...newBrand, brand_code: event.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                    />
                  </label>
                  <label className="block">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Brand Name</span>
                    <input
                      value={newBrand.brand_name}
                      onChange={(event) => setNewBrand({ ...newBrand, brand_name: event.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                    />
                  </label>
                  <label className="block">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Legal Name</span>
                    <input
                      value={newBrand.legal_name}
                      onChange={(event) => setNewBrand({ ...newBrand, legal_name: event.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                    />
                  </label>
                  <label className="block">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Short Name</span>
                    <input
                      value={newBrand.short_name}
                      onChange={(event) => setNewBrand({ ...newBrand, short_name: event.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                    />
                  </label>
                  <label className="block">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Email</span>
                    <input
                      value={newBrand.email}
                      onChange={(event) => setNewBrand({ ...newBrand, email: event.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                      type="email"
                    />
                  </label>
                  <label className="block">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Phone</span>
                    <input
                      value={newBrand.phone}
                      onChange={(event) => setNewBrand({ ...newBrand, phone: event.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                    />
                  </label>
                </div>
                <button
                  type="button"
                  disabled={busy || !newBrand.brand_code || !newBrand.brand_name}
                  onClick={createBrand}
                  className="mt-4 inline-flex items-center justify-center rounded-md bg-green-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {busy ? 'Saving…' : 'Create Brand'}
                </button>
              </div>

              <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                <h3 className="mb-3 text-lg font-semibold text-slate-950">Legal Entity</h3>
                <div className="grid gap-3 sm:grid-cols-2">
                  <label className="block">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Brand</span>
                    <select
                      value={newLegalEntity.brand_id}
                      onChange={(event) => setNewLegalEntity({ ...newLegalEntity, brand_id: event.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                    >
                      <option value="">Select brand</option>
                      {brands.map((brand) => (
                        <option key={brand.id} value={brand.id}>
                          {brand.brand_name} ({brand.brand_code})
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="block">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Entity Code</span>
                    <input
                      value={newLegalEntity.entity_code}
                      onChange={(event) => setNewLegalEntity({ ...newLegalEntity, entity_code: event.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                    />
                  </label>
                  <label className="block sm:col-span-2">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Entity Name</span>
                    <input
                      value={newLegalEntity.entity_name}
                      onChange={(event) => setNewLegalEntity({ ...newLegalEntity, entity_name: event.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                    />
                  </label>
                  <label className="block">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Type</span>
                    <input
                      value={newLegalEntity.entity_type}
                      onChange={(event) => setNewLegalEntity({ ...newLegalEntity, entity_type: event.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                    />
                  </label>
                  <label className="block">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Country</span>
                    <input
                      value={newLegalEntity.country}
                      onChange={(event) => setNewLegalEntity({ ...newLegalEntity, country: event.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                    />
                  </label>
                  <label className="block sm:col-span-2">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Registered Address</span>
                    <input
                      value={newLegalEntity.registered_address}
                      onChange={(event) => setNewLegalEntity({ ...newLegalEntity, registered_address: event.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                    />
                  </label>
                </div>
                <button
                  type="button"
                  disabled={busy || !newLegalEntity.brand_id || !newLegalEntity.entity_code || !newLegalEntity.entity_name}
                  onClick={createLegalEntity}
                  className="mt-4 inline-flex items-center justify-center rounded-md bg-green-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {busy ? 'Saving…' : 'Create Legal Entity'}
                </button>
              </div>

              <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                <h3 className="mb-3 text-lg font-semibold text-slate-950">Business Unit</h3>
                <div className="grid gap-3 sm:grid-cols-2">
                  <label className="block">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Legal Entity</span>
                    <select
                      value={newBusinessUnit.legal_entity_id}
                      onChange={(event) => setNewBusinessUnit({ ...newBusinessUnit, legal_entity_id: event.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                    >
                      <option value="">Select legal entity</option>
                      {legalEntities.map((entity) => (
                        <option key={entity.id} value={entity.id}>
                          {entity.entity_name} ({entity.entity_code})
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="block">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Unit Code</span>
                    <input
                      value={newBusinessUnit.business_unit_code}
                      onChange={(event) => setNewBusinessUnit({ ...newBusinessUnit, business_unit_code: event.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                    />
                  </label>
                  <label className="block sm:col-span-2">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Unit Name</span>
                    <input
                      value={newBusinessUnit.business_unit_name}
                      onChange={(event) => setNewBusinessUnit({ ...newBusinessUnit, business_unit_name: event.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                    />
                  </label>
                  <label className="block sm:col-span-2">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Head</span>
                    <input
                      value={newBusinessUnit.head}
                      onChange={(event) => setNewBusinessUnit({ ...newBusinessUnit, head: event.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                    />
                  </label>
                </div>
                <button
                  type="button"
                  disabled={busy || !newBusinessUnit.legal_entity_id || !newBusinessUnit.business_unit_code || !newBusinessUnit.business_unit_name}
                  onClick={createBusinessUnit}
                  className="mt-4 inline-flex items-center justify-center rounded-md bg-green-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {busy ? 'Saving…' : 'Create Business Unit'}
                </button>
              </div>
            </div>
          </div>

          <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-xl font-semibold text-slate-950">EOM Hierarchy</h2>

            <div className="space-y-6">
              <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                <h3 className="mb-3 text-lg font-semibold text-slate-950">Zone</h3>
                <div className="grid gap-3 sm:grid-cols-2">
                  <label className="block">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Business Unit</span>
                    <select
                      value={newZone.business_unit_id}
                      onChange={(event) => setNewZone({ ...newZone, business_unit_id: event.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                    >
                      <option value="">Select business unit</option>
                      {businessUnits.map((unit) => (
                        <option key={unit.id} value={unit.id}>
                          {unit.business_unit_name} ({unit.business_unit_code})
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="block">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Zone Code</span>
                    <input
                      value={newZone.zone_code}
                      onChange={(event) => setNewZone({ ...newZone, zone_code: event.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                    />
                  </label>
                  <label className="block sm:col-span-2">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Zone Name</span>
                    <input
                      value={newZone.zone_name}
                      onChange={(event) => setNewZone({ ...newZone, zone_name: event.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                    />
                  </label>
                  <label className="block sm:col-span-2">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Zone Head</span>
                    <input
                      value={newZone.zone_head}
                      onChange={(event) => setNewZone({ ...newZone, zone_head: event.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                    />
                  </label>
                </div>
                <button
                  type="button"
                  disabled={busy || !newZone.business_unit_id || !newZone.zone_code || !newZone.zone_name}
                  onClick={createZone}
                  className="mt-4 inline-flex items-center justify-center rounded-md bg-green-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {busy ? 'Saving…' : 'Create Zone'}
                </button>
              </div>

              <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                <h3 className="mb-3 text-lg font-semibold text-slate-950">Region</h3>
                <div className="grid gap-3 sm:grid-cols-2">
                  <label className="block">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Zone</span>
                    <select
                      value={newRegion.zone_id}
                      onChange={(event) => setNewRegion({ ...newRegion, zone_id: event.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                    >
                      <option value="">Select zone</option>
                      {zones.map((zone) => (
                        <option key={zone.id} value={zone.id}>
                          {zone.zone_name} ({zone.zone_code})
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="block">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Region Code</span>
                    <input
                      value={newRegion.region_code}
                      onChange={(event) => setNewRegion({ ...newRegion, region_code: event.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                    />
                  </label>
                  <label className="block sm:col-span-2">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Region Name</span>
                    <input
                      value={newRegion.region_name}
                      onChange={(event) => setNewRegion({ ...newRegion, region_name: event.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                    />
                  </label>
                  <label className="block">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Regional Manager</span>
                    <input
                      value={newRegion.regional_manager}
                      onChange={(event) => setNewRegion({ ...newRegion, regional_manager: event.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                    />
                  </label>
                  <label className="block sm:col-span-2">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Office Address</span>
                    <input
                      value={newRegion.office_address}
                      onChange={(event) => setNewRegion({ ...newRegion, office_address: event.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                    />
                  </label>
                </div>
                <button
                  type="button"
                  disabled={busy || !newRegion.zone_id || !newRegion.region_code || !newRegion.region_name}
                  onClick={createRegion}
                  className="mt-4 inline-flex items-center justify-center rounded-md bg-green-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {busy ? 'Saving…' : 'Create Region'}
                </button>
              </div>

              <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                <h3 className="mb-3 text-lg font-semibold text-slate-950">Area</h3>
                <div className="grid gap-3 sm:grid-cols-2">
                  <label className="block">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Region</span>
                    <select
                      value={newArea.region_id}
                      onChange={(event) => setNewArea({ ...newArea, region_id: event.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                    >
                      <option value="">Select region</option>
                      {regions.map((region) => (
                        <option key={region.id} value={region.id}>
                          {region.region_name} ({region.region_code})
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="block">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Area Code</span>
                    <input
                      value={newArea.area_code}
                      onChange={(event) => setNewArea({ ...newArea, area_code: event.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                    />
                  </label>
                  <label className="block sm:col-span-2">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Area Name</span>
                    <input
                      value={newArea.area_name}
                      onChange={(event) => setNewArea({ ...newArea, area_name: event.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                    />
                  </label>
                  <label className="block">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Area Manager</span>
                    <input
                      value={newArea.area_manager}
                      onChange={(event) => setNewArea({ ...newArea, area_manager: event.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                    />
                  </label>
                  <label className="block sm:col-span-2">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Office Address</span>
                    <input
                      value={newArea.office_address}
                      onChange={(event) => setNewArea({ ...newArea, office_address: event.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                    />
                  </label>
                </div>
                <button
                  type="button"
                  disabled={busy || !newArea.region_id || !newArea.area_code || !newArea.area_name}
                  onClick={createArea}
                  className="mt-4 inline-flex items-center justify-center rounded-md bg-green-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {busy ? 'Saving…' : 'Create Area'}
                </button>
              </div>

              <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                <h3 className="mb-3 text-lg font-semibold text-slate-950">Cluster</h3>
                <div className="grid gap-3 sm:grid-cols-2">
                  <label className="block">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Area</span>
                    <select
                      value={newCluster.area_id}
                      onChange={(event) => setNewCluster({ ...newCluster, area_id: event.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                    >
                      <option value="">Select area</option>
                      {areas.map((area) => (
                        <option key={area.id} value={area.id}>
                          {area.area_name} ({area.area_code})
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="block">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Cluster Code</span>
                    <input
                      value={newCluster.cluster_code}
                      onChange={(event) => setNewCluster({ ...newCluster, cluster_code: event.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                    />
                  </label>
                  <label className="block sm:col-span-2">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Cluster Name</span>
                    <input
                      value={newCluster.cluster_name}
                      onChange={(event) => setNewCluster({ ...newCluster, cluster_name: event.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                    />
                  </label>
                  <label className="block sm:col-span-2">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Cluster Manager</span>
                    <input
                      value={newCluster.cluster_manager}
                      onChange={(event) => setNewCluster({ ...newCluster, cluster_manager: event.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                    />
                  </label>
                </div>
                <button
                  type="button"
                  disabled={busy || !newCluster.area_id || !newCluster.cluster_code || !newCluster.cluster_name}
                  onClick={createCluster}
                  className="mt-4 inline-flex items-center justify-center rounded-md bg-green-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {busy ? 'Saving…' : 'Create Cluster'}
                </button>
              </div>

              <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                <h3 className="mb-3 text-lg font-semibold text-slate-950">Branch</h3>
                <div className="grid gap-3 sm:grid-cols-2">
                  <label className="block">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Area</span>
                    <select
                      value={newBranch.area_id}
                      onChange={(event) => setNewBranch({ ...newBranch, area_id: event.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                    >
                      <option value="">Select area</option>
                      {areas.map((area) => (
                        <option key={area.id} value={area.id}>
                          {area.area_name} ({area.area_code})
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="block">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Branch Code</span>
                    <input
                      value={newBranch.branch_code}
                      onChange={(event) => setNewBranch({ ...newBranch, branch_code: event.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                    />
                  </label>
                  <label className="block sm:col-span-2">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Branch Name</span>
                    <input
                      value={newBranch.branch_name}
                      onChange={(event) => setNewBranch({ ...newBranch, branch_name: event.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                    />
                  </label>
                  <label className="block">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Short Name</span>
                    <input
                      value={newBranch.short_name}
                      onChange={(event) => setNewBranch({ ...newBranch, short_name: event.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                    />
                  </label>
                  <label className="block">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Zone</span>
                    <select
                      value={newBranch.zone_id}
                      onChange={(event) => setNewBranch({ ...newBranch, zone_id: event.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                    >
                      <option value="">Optional zone</option>
                      {zones.map((zone) => (
                        <option key={zone.id} value={zone.id}>
                          {zone.zone_name} ({zone.zone_code})
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="block">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Region</span>
                    <select
                      value={newBranch.region_id}
                      onChange={(event) => setNewBranch({ ...newBranch, region_id: event.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                    >
                      <option value="">Optional region</option>
                      {regions.map((region) => (
                        <option key={region.id} value={region.id}>
                          {region.region_name} ({region.region_code})
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="block sm:col-span-2">
                    <span className="mb-1 block text-sm font-medium text-slate-700">Cluster</span>
                    <select
                      value={newBranch.cluster_id}
                      onChange={(event) => setNewBranch({ ...newBranch, cluster_id: event.target.value })}
                      className="w-full rounded-md border border-slate-300 px-3 py-2"
                    >
                      <option value="">Optional cluster</option>
                      {clusters.map((cluster) => (
                        <option key={cluster.id} value={cluster.id}>
                          {cluster.cluster_name} ({cluster.cluster_code})
                        </option>
                      ))}
                    </select>
                  </label>
                </div>
                <button
                  type="button"
                  disabled={busy || !newBranch.area_id || !newBranch.branch_name}
                  onClick={createBranch}
                  className="mt-4 inline-flex items-center justify-center rounded-md bg-green-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {busy ? 'Saving…' : 'Create Branch'}
                </button>
              </div>
            </div>
          </div>
        </section>

        <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-xl font-semibold text-slate-950">EOM Hierarchy Summary</h2>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
              <dt className="text-xs font-semibold uppercase tracking-wide text-slate-500">Brands</dt>
              <dd className="mt-2 text-3xl font-semibold text-slate-950">{brands.length}</dd>
            </div>
            <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
              <dt className="text-xs font-semibold uppercase tracking-wide text-slate-500">Legal Entities</dt>
              <dd className="mt-2 text-3xl font-semibold text-slate-950">{legalEntities.length}</dd>
            </div>
            <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
              <dt className="text-xs font-semibold uppercase tracking-wide text-slate-500">Business Units</dt>
              <dd className="mt-2 text-3xl font-semibold text-slate-950">{businessUnits.length}</dd>
            </div>
            <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
              <dt className="text-xs font-semibold uppercase tracking-wide text-slate-500">Zones</dt>
              <dd className="mt-2 text-3xl font-semibold text-slate-950">{zones.length}</dd>
            </div>
            <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
              <dt className="text-xs font-semibold uppercase tracking-wide text-slate-500">Regions</dt>
              <dd className="mt-2 text-3xl font-semibold text-slate-950">{regions.length}</dd>
            </div>
            <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
              <dt className="text-xs font-semibold uppercase tracking-wide text-slate-500">Areas</dt>
              <dd className="mt-2 text-3xl font-semibold text-slate-950">{areas.length}</dd>
            </div>
            <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
              <dt className="text-xs font-semibold uppercase tracking-wide text-slate-500">Clusters</dt>
              <dd className="mt-2 text-3xl font-semibold text-slate-950">{clusters.length}</dd>
            </div>
            <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
              <dt className="text-xs font-semibold uppercase tracking-wide text-slate-500">Branches</dt>
              <dd className="mt-2 text-3xl font-semibold text-slate-950">{branches.length}</dd>
            </div>
          </div>
        </section>

        <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-xl font-semibold text-slate-950">EOM Branches</h2>
          {branches.length === 0 ? (
            <p className="rounded-md bg-slate-50 p-4 text-sm text-slate-600">No branches are available.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[700px] text-sm">
                <thead>
                  <tr className="border-b border-slate-200 text-left text-slate-500">
                    <th className="px-3 py-3">Name</th>
                    <th className="px-3 py-3">Code</th>
                    <th className="px-3 py-3">Zone</th>
                    <th className="px-3 py-3">Region</th>
                    <th className="px-3 py-3">Area</th>
                  </tr>
                </thead>
                <tbody>
                  {branches.map((branch) => (
                    <tr key={branch.id} className="border-b border-slate-100">
                      <td className="px-3 py-3 text-slate-700">{branch.branch_name}</td>
                      <td className="px-3 py-3 text-slate-700">{branch.branch_code}</td>
                      <td className="px-3 py-3 text-slate-700">{branch.zone_id || '-'}</td>
                      <td className="px-3 py-3 text-slate-700">{branch.region_id || '-'}</td>
                      <td className="px-3 py-3 text-slate-700">{branch.area_id || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
