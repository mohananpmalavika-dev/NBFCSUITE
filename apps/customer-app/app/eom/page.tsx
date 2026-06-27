'use client';

import { apiClient } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import type { ReactNode } from 'react';
import { useCallback, useEffect, useMemo, useState } from 'react';

const tenantId = 'default';

type TabKey = 'foundation' | 'network' | 'people' | 'assets' | 'ownership';

interface Customer {
  id: string;
  first_name: string;
  last_name: string;
  email?: string;
  phone?: string;
  branch_id?: string | null;
}

interface Enterprise {
  id: string;
  enterprise_code: string;
  enterprise_name: string;
  country?: string | null;
  currency?: string | null;
  timezone?: string | null;
  status: string;
}

interface Brand {
  id: string;
  enterprise_id?: string | null;
  brand_code: string;
  brand_name: string;
  theme_color?: string | null;
}

interface LegalEntity {
  id: string;
  brand_id: string;
  entity_code: string;
  entity_name: string;
}

interface BusinessUnit {
  id: string;
  legal_entity_id: string;
  business_unit_code: string;
  business_unit_name: string;
}

interface Division {
  id: string;
  business_unit_id: string;
  division_code: string;
  division_name: string;
}

interface Zone {
  id: string;
  business_unit_id: string;
  division_id?: string | null;
  zone_code: string;
  zone_name: string;
}

interface Region {
  id: string;
  zone_id: string;
  region_code: string;
  region_name: string;
}

interface Area {
  id: string;
  region_id: string;
  area_code: string;
  area_name: string;
}

interface Cluster {
  id: string;
  area_id: string;
  cluster_code: string;
  cluster_name: string;
}

interface Branch {
  id: string;
  branch_code: string;
  branch_name: string;
  area_id?: string | null;
  region_id?: string | null;
  zone_id?: string | null;
  cluster_id?: string | null;
}

interface Department {
  id: string;
  branch_id: string;
  department_code: string;
  department_name: string;
}

interface Team {
  id: string;
  department_id: string;
  team_code: string;
  team_name: string;
}

interface Position {
  id: string;
  department_id?: string | null;
  team_id?: string | null;
  position_code: string;
  position_title: string;
  status: string;
}

interface Vendor {
  id: string;
  vendor_code: string;
  vendor_name: string;
  vendor_type?: string | null;
  status: string;
}

interface Asset {
  id: string;
  asset_code: string;
  asset_name: string;
  asset_type?: string | null;
  branch_id?: string | null;
  vendor_id?: string | null;
  status: string;
}

interface Mapping {
  id: string;
  customer_id: string;
  branch_id: string;
  status: string;
  effective_from: string;
  effective_to?: string | null;
  transferred_by?: string | null;
}

interface Summary {
  enterprises: number;
  brands: number;
  legal_entities: number;
  business_units: number;
  divisions: number;
  zones: number;
  regions: number;
  areas: number;
  clusters: number;
  branches: number;
  departments: number;
  teams: number;
  positions: number;
  employees: number;
  vendors: number;
  assets: number;
  customer_branch_mappings: number;
}

interface TreeNode {
  id: string;
  code: string;
  name: string;
  type: string;
  brands?: TreeNode[];
  legal_entities?: TreeNode[];
  business_units?: TreeNode[];
  divisions?: TreeNode[];
  zones?: TreeNode[];
  regions?: TreeNode[];
  areas?: TreeNode[];
  clusters?: TreeNode[];
  branches?: TreeNode[];
}

const tabs: Array<{ key: TabKey; label: string }> = [
  { key: 'foundation', label: 'Foundation' },
  { key: 'network', label: 'Network' },
  { key: 'people', label: 'People' },
  { key: 'assets', label: 'Vendors & Assets' },
  { key: 'ownership', label: 'Customer Ownership' },
];

const emptySummary: Summary = {
  enterprises: 0,
  brands: 0,
  legal_entities: 0,
  business_units: 0,
  divisions: 0,
  zones: 0,
  regions: 0,
  areas: 0,
  clusters: 0,
  branches: 0,
  departments: 0,
  teams: 0,
  positions: 0,
  employees: 0,
  vendors: 0,
  assets: 0,
  customer_branch_mappings: 0,
};

function textFromError(error: unknown, fallback: string) {
  const maybeError = error as { response?: { data?: { detail?: string } } };
  return maybeError?.response?.data?.detail || fallback;
}

function displayCode(name: string, code?: string | null) {
  return code ? `${name} (${code})` : name;
}

function TextInput({
  label,
  value,
  onChange,
  type = 'text',
  placeholder,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  type?: string;
  placeholder?: string;
}) {
  return (
    <label className="block">
      <span className="mb-1 block text-xs font-semibold uppercase text-slate-500">{label}</span>
      <input
        value={value}
        onChange={(event) => onChange(event.target.value)}
        type={type}
        placeholder={placeholder}
        className="h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-sm text-slate-900 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
      />
    </label>
  );
}

function SelectInput({
  label,
  value,
  onChange,
  children,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  children: ReactNode;
}) {
  return (
    <label className="block">
      <span className="mb-1 block text-xs font-semibold uppercase text-slate-500">{label}</span>
      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-sm text-slate-900 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
      >
        {children}
      </select>
    </label>
  );
}

function TreeRows({ nodes, depth = 0 }: { nodes: TreeNode[]; depth?: number }) {
  return (
    <>
      {nodes.map((node) => {
        const children = [
          ...(node.brands || []),
          ...(node.legal_entities || []),
          ...(node.business_units || []),
          ...(node.divisions || []),
          ...(node.zones || []),
          ...(node.regions || []),
          ...(node.areas || []),
          ...(node.clusters || []),
          ...(node.branches || []),
        ];
        return (
          <div key={`${node.type}-${node.id}`}>
            <div
              className="grid grid-cols-[1fr_auto] border-b border-slate-100 py-2 text-sm"
              style={{ paddingLeft: `${depth * 16}px` }}
            >
              <span className="font-medium text-slate-800">{node.name}</span>
              <span className="text-xs uppercase text-slate-500">{node.type.replace('_', ' ')}</span>
            </div>
            {children.length > 0 && <TreeRows nodes={children} depth={depth + 1} />}
          </div>
        );
      })}
    </>
  );
}

export default function EomPage() {
  const { user, token, isLoading } = useAuth();
  const [activeTab, setActiveTab] = useState<TabKey>('foundation');
  const [message, setMessage] = useState('');
  const [busyAction, setBusyAction] = useState('');

  const [customers, setCustomers] = useState<Customer[]>([]);
  const [enterprises, setEnterprises] = useState<Enterprise[]>([]);
  const [brands, setBrands] = useState<Brand[]>([]);
  const [legalEntities, setLegalEntities] = useState<LegalEntity[]>([]);
  const [businessUnits, setBusinessUnits] = useState<BusinessUnit[]>([]);
  const [divisions, setDivisions] = useState<Division[]>([]);
  const [zones, setZones] = useState<Zone[]>([]);
  const [regions, setRegions] = useState<Region[]>([]);
  const [areas, setAreas] = useState<Area[]>([]);
  const [clusters, setClusters] = useState<Cluster[]>([]);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [teams, setTeams] = useState<Team[]>([]);
  const [positions, setPositions] = useState<Position[]>([]);
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [summary, setSummary] = useState<Summary>(emptySummary);
  const [tree, setTree] = useState<TreeNode[]>([]);
  const [selectedCustomerId, setSelectedCustomerId] = useState('');
  const [selectedBranchId, setSelectedBranchId] = useState('');
  const [mappingHistory, setMappingHistory] = useState<Mapping[]>([]);

  const [enterpriseForm, setEnterpriseForm] = useState({
    enterprise_code: '',
    enterprise_name: '',
    corporate_address: '',
    corporate_office: '',
    country: 'India',
    currency: 'INR',
    timezone: 'Asia/Kolkata',
    financial_year_start: '04-01',
    financial_year_end: '03-31',
  });
  const [brandForm, setBrandForm] = useState({
    enterprise_id: '',
    brand_code: '',
    brand_name: '',
    theme_color: '',
    website: '',
    email: '',
    phone: '',
  });
  const [entityForm, setEntityForm] = useState({
    brand_id: '',
    entity_code: '',
    entity_name: '',
    entity_type: 'company',
    country: 'India',
  });
  const [unitForm, setUnitForm] = useState({
    legal_entity_id: '',
    business_unit_code: '',
    business_unit_name: '',
    head: '',
  });
  const [divisionForm, setDivisionForm] = useState({
    business_unit_id: '',
    division_code: '',
    division_name: '',
    division_head: '',
  });
  const [zoneForm, setZoneForm] = useState({
    business_unit_id: '',
    division_id: '',
    zone_code: '',
    zone_name: '',
    zone_head: '',
  });
  const [regionForm, setRegionForm] = useState({
    zone_id: '',
    region_code: '',
    region_name: '',
    regional_manager: '',
  });
  const [areaForm, setAreaForm] = useState({
    region_id: '',
    area_code: '',
    area_name: '',
    area_manager: '',
  });
  const [clusterForm, setClusterForm] = useState({
    area_id: '',
    cluster_code: '',
    cluster_name: '',
    cluster_manager: '',
  });
  const [branchForm, setBranchForm] = useState({
    area_id: '',
    zone_id: '',
    region_id: '',
    cluster_id: '',
    branch_code: '',
    branch_name: '',
    short_name: '',
  });
  const [departmentForm, setDepartmentForm] = useState({
    branch_id: '',
    department_code: '',
    department_name: '',
  });
  const [teamForm, setTeamForm] = useState({
    department_id: '',
    team_code: '',
    team_name: '',
  });
  const [positionForm, setPositionForm] = useState({
    department_id: '',
    team_id: '',
    position_code: '',
    position_title: '',
    grade: '',
    employment_type: 'full_time',
  });
  const [vendorForm, setVendorForm] = useState({
    vendor_code: '',
    vendor_name: '',
    vendor_type: '',
    contact_person: '',
    email: '',
    phone: '',
  });
  const [assetForm, setAssetForm] = useState({
    vendor_id: '',
    branch_id: '',
    department_id: '',
    asset_code: '',
    asset_name: '',
    asset_type: '',
    purchase_value: '0',
  });

  const selectedCustomer = useMemo(
    () => customers.find((customer) => customer.id === selectedCustomerId),
    [customers, selectedCustomerId],
  );
  const branchNames = useMemo(
    () => new Map(branches.map((branch) => [branch.id, displayCode(branch.branch_name, branch.branch_code)])),
    [branches],
  );

  const refresh = useCallback(async () => {
    if (!token) return;
    try {
      const [
        customersRes,
        summaryRes,
        treeRes,
        enterprisesRes,
        brandsRes,
        entitiesRes,
        unitsRes,
        divisionsRes,
        zonesRes,
        regionsRes,
        areasRes,
        clustersRes,
        branchesRes,
        departmentsRes,
        teamsRes,
        positionsRes,
        vendorsRes,
        assetsRes,
      ] = await Promise.all([
        apiClient.getCustomers(),
        apiClient.getEomSummary(),
        apiClient.getEomHierarchyTree(),
        apiClient.getEomEnterprises(),
        apiClient.getEomBrands(),
        apiClient.getEomLegalEntities(),
        apiClient.getEomBusinessUnits(),
        apiClient.getEomDivisions(),
        apiClient.getEomZones(),
        apiClient.getEomRegions(),
        apiClient.getEomAreas(),
        apiClient.getEomClusters(),
        apiClient.getEomBranches(),
        apiClient.getEomDepartments(),
        apiClient.getEomTeams(),
        apiClient.getEomPositions(),
        apiClient.getEomVendors(),
        apiClient.getEomAssets(),
      ]);

      const loadedCustomers = Array.isArray(customersRes.data.items) ? customersRes.data.items : customersRes.data || [];
      const loadedBranches = branchesRes.data || [];
      setCustomers(loadedCustomers);
      setSummary(summaryRes.data || emptySummary);
      setTree(treeRes.data?.items || []);
      setEnterprises(enterprisesRes.data || []);
      setBrands(brandsRes.data || []);
      setLegalEntities(entitiesRes.data || []);
      setBusinessUnits(unitsRes.data || []);
      setDivisions(divisionsRes.data || []);
      setZones(zonesRes.data || []);
      setRegions(regionsRes.data || []);
      setAreas(areasRes.data || []);
      setClusters(clustersRes.data || []);
      setBranches(loadedBranches);
      setDepartments(departmentsRes.data || []);
      setTeams(teamsRes.data || []);
      setPositions(positionsRes.data || []);
      setVendors(vendorsRes.data || []);
      setAssets(assetsRes.data || []);

      if (!selectedCustomerId && loadedCustomers.length > 0) setSelectedCustomerId(loadedCustomers[0].id);
      if (!selectedBranchId && loadedBranches.length > 0) setSelectedBranchId(loadedBranches[0].id);
    } catch (error) {
      setMessage(textFromError(error, 'Unable to load EOM workspace.'));
    }
  }, [selectedBranchId, selectedCustomerId, token]);

  const refreshMapping = useCallback(async () => {
    if (!token || !selectedCustomerId) {
      setMappingHistory([]);
      return;
    }
    try {
      const response = await apiClient.getCustomerBranchMapping(selectedCustomerId);
      setMappingHistory(response.data || []);
    } catch {
      setMappingHistory([]);
    }
  }, [selectedCustomerId, token]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  useEffect(() => {
    refreshMapping();
  }, [refreshMapping]);

  async function runAction(name: string, action: () => Promise<void>, success: string) {
    setBusyAction(name);
    setMessage('');
    try {
      await action();
      setMessage(success);
      await refresh();
    } catch (error) {
      setMessage(textFromError(error, `${success.replace('created', 'creation')} failed.`));
    } finally {
      setBusyAction('');
    }
  }

  const metricTiles = [
    ['Enterprises', summary.enterprises],
    ['Brands', summary.brands],
    ['Entities', summary.legal_entities],
    ['Units', summary.business_units],
    ['Divisions', summary.divisions],
    ['Branches', summary.branches],
    ['Teams', summary.teams],
    ['Positions', summary.positions],
    ['Vendors', summary.vendors],
    ['Assets', summary.assets],
    ['Ownerships', summary.customer_branch_mappings],
  ];

  if (isLoading || !token) {
    return <div className="p-8 text-center">Loading...</div>;
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-6">
      <div className="mx-auto max-w-7xl space-y-6">
        <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
            <div>
              <p className="text-xs font-semibold uppercase text-blue-700">Enterprise Organization Management</p>
              <h1 className="mt-1 text-3xl font-bold text-slate-950">EOM Command Center</h1>
              <p className="mt-2 max-w-3xl text-sm text-slate-600">
                Foundation masters for enterprise, brand, legal entity, operating hierarchy, employee structure,
                vendors, assets, and customer ownership.
              </p>
            </div>
            <button
              type="button"
              onClick={refresh}
              className="h-10 rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-800 hover:border-blue-400"
            >
              Refresh
            </button>
          </div>
        </section>

        {message && (
          <div className="rounded-md border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-900">
            {message}
          </div>
        )}

        <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6">
          {metricTiles.map(([label, value]) => (
            <div key={String(label)} className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
              <dt className="text-xs font-semibold uppercase text-slate-500">{label}</dt>
              <dd className="mt-2 text-2xl font-bold text-slate-950">{value}</dd>
            </div>
          ))}
        </section>

        <section className="grid gap-6 xl:grid-cols-[0.9fr_1.5fr]">
          <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <h2 className="text-lg font-semibold text-slate-950">Hierarchy Tree</h2>
            <div className="mt-4 max-h-[560px] overflow-auto">
              {tree.length === 0 ? (
                <p className="rounded-md bg-slate-50 p-4 text-sm text-slate-600">No hierarchy data yet.</p>
              ) : (
                <TreeRows nodes={tree} />
              )}
            </div>
          </div>

          <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex flex-wrap gap-2 border-b border-slate-200 pb-3">
              {tabs.map((tab) => (
                <button
                  key={tab.key}
                  type="button"
                  onClick={() => setActiveTab(tab.key)}
                  className={`h-9 rounded-md px-3 text-sm font-semibold ${
                    activeTab === tab.key ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {activeTab === 'foundation' && (
              <div className="mt-5 grid gap-6 lg:grid-cols-2">
                <div className="space-y-3">
                  <h3 className="text-base font-semibold text-slate-950">Enterprise</h3>
                  <TextInput label="Code" value={enterpriseForm.enterprise_code} onChange={(value) => setEnterpriseForm({ ...enterpriseForm, enterprise_code: value })} />
                  <TextInput label="Name" value={enterpriseForm.enterprise_name} onChange={(value) => setEnterpriseForm({ ...enterpriseForm, enterprise_name: value })} />
                  <TextInput label="Corporate Office" value={enterpriseForm.corporate_office} onChange={(value) => setEnterpriseForm({ ...enterpriseForm, corporate_office: value })} />
                  <div className="grid gap-3 sm:grid-cols-3">
                    <TextInput label="Country" value={enterpriseForm.country} onChange={(value) => setEnterpriseForm({ ...enterpriseForm, country: value })} />
                    <TextInput label="Currency" value={enterpriseForm.currency} onChange={(value) => setEnterpriseForm({ ...enterpriseForm, currency: value })} />
                    <TextInput label="Timezone" value={enterpriseForm.timezone} onChange={(value) => setEnterpriseForm({ ...enterpriseForm, timezone: value })} />
                  </div>
                  <button
                    type="button"
                    disabled={!!busyAction || !enterpriseForm.enterprise_code || !enterpriseForm.enterprise_name}
                    onClick={() =>
                      runAction(
                        'enterprise',
                        async () => {
                          await apiClient.createEomEnterprise({ tenant_id: tenantId, ...enterpriseForm });
                          setEnterpriseForm({ ...enterpriseForm, enterprise_code: '', enterprise_name: '', corporate_address: '', corporate_office: '' });
                        },
                        'Enterprise created.',
                      )
                    }
                    className="h-10 rounded-md bg-blue-600 px-4 text-sm font-semibold text-white disabled:opacity-50"
                  >
                    {busyAction === 'enterprise' ? 'Saving...' : 'Create Enterprise'}
                  </button>
                </div>

                <div className="space-y-3">
                  <h3 className="text-base font-semibold text-slate-950">Brand, Legal Entity, Unit</h3>
                  <SelectInput label="Enterprise" value={brandForm.enterprise_id} onChange={(value) => setBrandForm({ ...brandForm, enterprise_id: value })}>
                    <option value="">Optional enterprise</option>
                    {enterprises.map((enterprise) => (
                      <option key={enterprise.id} value={enterprise.id}>{displayCode(enterprise.enterprise_name, enterprise.enterprise_code)}</option>
                    ))}
                  </SelectInput>
                  <div className="grid gap-3 sm:grid-cols-2">
                    <TextInput label="Brand Code" value={brandForm.brand_code} onChange={(value) => setBrandForm({ ...brandForm, brand_code: value })} />
                    <TextInput label="Brand Name" value={brandForm.brand_name} onChange={(value) => setBrandForm({ ...brandForm, brand_name: value })} />
                  </div>
                  <button
                    type="button"
                    disabled={!!busyAction || !brandForm.brand_code || !brandForm.brand_name}
                    onClick={() =>
                      runAction(
                        'brand',
                        async () => {
                          await apiClient.createEomBrand({ tenant_id: tenantId, ...brandForm, enterprise_id: brandForm.enterprise_id || undefined });
                          setBrandForm({ ...brandForm, brand_code: '', brand_name: '', theme_color: '', website: '', email: '', phone: '' });
                        },
                        'Brand created.',
                      )
                    }
                    className="h-10 rounded-md bg-blue-600 px-4 text-sm font-semibold text-white disabled:opacity-50"
                  >
                    {busyAction === 'brand' ? 'Saving...' : 'Create Brand'}
                  </button>

                  <SelectInput label="Brand" value={entityForm.brand_id} onChange={(value) => setEntityForm({ ...entityForm, brand_id: value })}>
                    <option value="">Select brand</option>
                    {brands.map((brand) => (
                      <option key={brand.id} value={brand.id}>{displayCode(brand.brand_name, brand.brand_code)}</option>
                    ))}
                  </SelectInput>
                  <div className="grid gap-3 sm:grid-cols-2">
                    <TextInput label="Entity Code" value={entityForm.entity_code} onChange={(value) => setEntityForm({ ...entityForm, entity_code: value })} />
                    <TextInput label="Entity Name" value={entityForm.entity_name} onChange={(value) => setEntityForm({ ...entityForm, entity_name: value })} />
                  </div>
                  <button
                    type="button"
                    disabled={!!busyAction || !entityForm.brand_id || !entityForm.entity_code || !entityForm.entity_name}
                    onClick={() =>
                      runAction(
                        'entity',
                        async () => {
                          await apiClient.createEomLegalEntity({ tenant_id: tenantId, ...entityForm });
                          setEntityForm({ ...entityForm, entity_code: '', entity_name: '' });
                        },
                        'Legal entity created.',
                      )
                    }
                    className="h-10 rounded-md bg-blue-600 px-4 text-sm font-semibold text-white disabled:opacity-50"
                  >
                    {busyAction === 'entity' ? 'Saving...' : 'Create Legal Entity'}
                  </button>

                  <SelectInput label="Legal Entity" value={unitForm.legal_entity_id} onChange={(value) => setUnitForm({ ...unitForm, legal_entity_id: value })}>
                    <option value="">Select legal entity</option>
                    {legalEntities.map((entity) => (
                      <option key={entity.id} value={entity.id}>{displayCode(entity.entity_name, entity.entity_code)}</option>
                    ))}
                  </SelectInput>
                  <div className="grid gap-3 sm:grid-cols-2">
                    <TextInput label="Unit Code" value={unitForm.business_unit_code} onChange={(value) => setUnitForm({ ...unitForm, business_unit_code: value })} />
                    <TextInput label="Unit Name" value={unitForm.business_unit_name} onChange={(value) => setUnitForm({ ...unitForm, business_unit_name: value })} />
                  </div>
                  <button
                    type="button"
                    disabled={!!busyAction || !unitForm.legal_entity_id || !unitForm.business_unit_code || !unitForm.business_unit_name}
                    onClick={() =>
                      runAction(
                        'unit',
                        async () => {
                          await apiClient.createEomBusinessUnit({ tenant_id: tenantId, ...unitForm });
                          setUnitForm({ ...unitForm, business_unit_code: '', business_unit_name: '', head: '' });
                        },
                        'Business unit created.',
                      )
                    }
                    className="h-10 rounded-md bg-blue-600 px-4 text-sm font-semibold text-white disabled:opacity-50"
                  >
                    {busyAction === 'unit' ? 'Saving...' : 'Create Business Unit'}
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'network' && (
              <div className="mt-5 grid gap-6 lg:grid-cols-2">
                <div className="space-y-3">
                  <h3 className="text-base font-semibold text-slate-950">Division, Zone, Region</h3>
                  <SelectInput label="Business Unit" value={divisionForm.business_unit_id} onChange={(value) => setDivisionForm({ ...divisionForm, business_unit_id: value })}>
                    <option value="">Select unit</option>
                    {businessUnits.map((unit) => (
                      <option key={unit.id} value={unit.id}>{displayCode(unit.business_unit_name, unit.business_unit_code)}</option>
                    ))}
                  </SelectInput>
                  <div className="grid gap-3 sm:grid-cols-2">
                    <TextInput label="Division Code" value={divisionForm.division_code} onChange={(value) => setDivisionForm({ ...divisionForm, division_code: value })} />
                    <TextInput label="Division Name" value={divisionForm.division_name} onChange={(value) => setDivisionForm({ ...divisionForm, division_name: value })} />
                  </div>
                  <button
                    type="button"
                    disabled={!!busyAction || !divisionForm.business_unit_id || !divisionForm.division_code || !divisionForm.division_name}
                    onClick={() =>
                      runAction(
                        'division',
                        async () => {
                          await apiClient.createEomDivision({ tenant_id: tenantId, ...divisionForm });
                          setDivisionForm({ ...divisionForm, division_code: '', division_name: '', division_head: '' });
                        },
                        'Division created.',
                      )
                    }
                    className="h-10 rounded-md bg-blue-600 px-4 text-sm font-semibold text-white disabled:opacity-50"
                  >
                    {busyAction === 'division' ? 'Saving...' : 'Create Division'}
                  </button>

                  <SelectInput label="Business Unit" value={zoneForm.business_unit_id} onChange={(value) => setZoneForm({ ...zoneForm, business_unit_id: value })}>
                    <option value="">Select unit</option>
                    {businessUnits.map((unit) => (
                      <option key={unit.id} value={unit.id}>{displayCode(unit.business_unit_name, unit.business_unit_code)}</option>
                    ))}
                  </SelectInput>
                  <SelectInput label="Division" value={zoneForm.division_id} onChange={(value) => setZoneForm({ ...zoneForm, division_id: value })}>
                    <option value="">Optional division</option>
                    {divisions.map((division) => (
                      <option key={division.id} value={division.id}>{displayCode(division.division_name, division.division_code)}</option>
                    ))}
                  </SelectInput>
                  <div className="grid gap-3 sm:grid-cols-2">
                    <TextInput label="Zone Code" value={zoneForm.zone_code} onChange={(value) => setZoneForm({ ...zoneForm, zone_code: value })} />
                    <TextInput label="Zone Name" value={zoneForm.zone_name} onChange={(value) => setZoneForm({ ...zoneForm, zone_name: value })} />
                  </div>
                  <button
                    type="button"
                    disabled={!!busyAction || !zoneForm.business_unit_id || !zoneForm.zone_code || !zoneForm.zone_name}
                    onClick={() =>
                      runAction(
                        'zone',
                        async () => {
                          await apiClient.createEomZone({ tenant_id: tenantId, ...zoneForm, division_id: zoneForm.division_id || undefined });
                          setZoneForm({ ...zoneForm, zone_code: '', zone_name: '', zone_head: '' });
                        },
                        'Zone created.',
                      )
                    }
                    className="h-10 rounded-md bg-blue-600 px-4 text-sm font-semibold text-white disabled:opacity-50"
                  >
                    {busyAction === 'zone' ? 'Saving...' : 'Create Zone'}
                  </button>
                </div>

                <div className="space-y-3">
                  <h3 className="text-base font-semibold text-slate-950">Region, Area, Cluster, Branch</h3>
                  <SelectInput label="Zone" value={regionForm.zone_id} onChange={(value) => setRegionForm({ ...regionForm, zone_id: value })}>
                    <option value="">Select zone</option>
                    {zones.map((zone) => (
                      <option key={zone.id} value={zone.id}>{displayCode(zone.zone_name, zone.zone_code)}</option>
                    ))}
                  </SelectInput>
                  <div className="grid gap-3 sm:grid-cols-2">
                    <TextInput label="Region Code" value={regionForm.region_code} onChange={(value) => setRegionForm({ ...regionForm, region_code: value })} />
                    <TextInput label="Region Name" value={regionForm.region_name} onChange={(value) => setRegionForm({ ...regionForm, region_name: value })} />
                  </div>
                  <button
                    type="button"
                    disabled={!!busyAction || !regionForm.zone_id || !regionForm.region_code || !regionForm.region_name}
                    onClick={() =>
                      runAction(
                        'region',
                        async () => {
                          await apiClient.createEomRegion({ tenant_id: tenantId, ...regionForm });
                          setRegionForm({ ...regionForm, region_code: '', region_name: '', regional_manager: '' });
                        },
                        'Region created.',
                      )
                    }
                    className="h-10 rounded-md bg-blue-600 px-4 text-sm font-semibold text-white disabled:opacity-50"
                  >
                    {busyAction === 'region' ? 'Saving...' : 'Create Region'}
                  </button>

                  <SelectInput label="Region" value={areaForm.region_id} onChange={(value) => setAreaForm({ ...areaForm, region_id: value })}>
                    <option value="">Select region</option>
                    {regions.map((region) => (
                      <option key={region.id} value={region.id}>{displayCode(region.region_name, region.region_code)}</option>
                    ))}
                  </SelectInput>
                  <div className="grid gap-3 sm:grid-cols-2">
                    <TextInput label="Area Code" value={areaForm.area_code} onChange={(value) => setAreaForm({ ...areaForm, area_code: value })} />
                    <TextInput label="Area Name" value={areaForm.area_name} onChange={(value) => setAreaForm({ ...areaForm, area_name: value })} />
                  </div>
                  <button
                    type="button"
                    disabled={!!busyAction || !areaForm.region_id || !areaForm.area_code || !areaForm.area_name}
                    onClick={() =>
                      runAction(
                        'area',
                        async () => {
                          await apiClient.createEomArea({ tenant_id: tenantId, ...areaForm });
                          setAreaForm({ ...areaForm, area_code: '', area_name: '', area_manager: '' });
                        },
                        'Area created.',
                      )
                    }
                    className="h-10 rounded-md bg-blue-600 px-4 text-sm font-semibold text-white disabled:opacity-50"
                  >
                    {busyAction === 'area' ? 'Saving...' : 'Create Area'}
                  </button>

                  <SelectInput label="Area" value={clusterForm.area_id} onChange={(value) => setClusterForm({ ...clusterForm, area_id: value })}>
                    <option value="">Select area</option>
                    {areas.map((area) => (
                      <option key={area.id} value={area.id}>{displayCode(area.area_name, area.area_code)}</option>
                    ))}
                  </SelectInput>
                  <div className="grid gap-3 sm:grid-cols-2">
                    <TextInput label="Cluster Code" value={clusterForm.cluster_code} onChange={(value) => setClusterForm({ ...clusterForm, cluster_code: value })} />
                    <TextInput label="Cluster Name" value={clusterForm.cluster_name} onChange={(value) => setClusterForm({ ...clusterForm, cluster_name: value })} />
                  </div>
                  <button
                    type="button"
                    disabled={!!busyAction || !clusterForm.area_id || !clusterForm.cluster_code || !clusterForm.cluster_name}
                    onClick={() =>
                      runAction(
                        'cluster',
                        async () => {
                          await apiClient.createEomCluster({ tenant_id: tenantId, ...clusterForm });
                          setClusterForm({ ...clusterForm, cluster_code: '', cluster_name: '', cluster_manager: '' });
                        },
                        'Cluster created.',
                      )
                    }
                    className="h-10 rounded-md bg-blue-600 px-4 text-sm font-semibold text-white disabled:opacity-50"
                  >
                    {busyAction === 'cluster' ? 'Saving...' : 'Create Cluster'}
                  </button>

                  <SelectInput label="Area" value={branchForm.area_id} onChange={(value) => setBranchForm({ ...branchForm, area_id: value })}>
                    <option value="">Select area</option>
                    {areas.map((area) => (
                      <option key={area.id} value={area.id}>{displayCode(area.area_name, area.area_code)}</option>
                    ))}
                  </SelectInput>
                  <div className="grid gap-3 sm:grid-cols-3">
                    <SelectInput label="Zone" value={branchForm.zone_id} onChange={(value) => setBranchForm({ ...branchForm, zone_id: value })}>
                      <option value="">Optional zone</option>
                      {zones.map((zone) => (
                        <option key={zone.id} value={zone.id}>{displayCode(zone.zone_name, zone.zone_code)}</option>
                      ))}
                    </SelectInput>
                    <SelectInput label="Region" value={branchForm.region_id} onChange={(value) => setBranchForm({ ...branchForm, region_id: value })}>
                      <option value="">Optional region</option>
                      {regions.map((region) => (
                        <option key={region.id} value={region.id}>{displayCode(region.region_name, region.region_code)}</option>
                      ))}
                    </SelectInput>
                    <SelectInput label="Cluster" value={branchForm.cluster_id} onChange={(value) => setBranchForm({ ...branchForm, cluster_id: value })}>
                      <option value="">Optional cluster</option>
                      {clusters.map((cluster) => (
                        <option key={cluster.id} value={cluster.id}>{displayCode(cluster.cluster_name, cluster.cluster_code)}</option>
                      ))}
                    </SelectInput>
                  </div>
                  <div className="grid gap-3 sm:grid-cols-2">
                    <TextInput label="Branch Code" value={branchForm.branch_code} onChange={(value) => setBranchForm({ ...branchForm, branch_code: value })} />
                    <TextInput label="Branch Name" value={branchForm.branch_name} onChange={(value) => setBranchForm({ ...branchForm, branch_name: value })} />
                  </div>
                  <button
                    type="button"
                    disabled={!!busyAction || !branchForm.area_id || !branchForm.branch_name}
                    onClick={() =>
                      runAction(
                        'branch',
                        async () => {
                          await apiClient.createEomBranch({
                            tenant_id: tenantId,
                            ...branchForm,
                            branch_code: branchForm.branch_code || undefined,
                            zone_id: branchForm.zone_id || undefined,
                            region_id: branchForm.region_id || undefined,
                            cluster_id: branchForm.cluster_id || undefined,
                          });
                          setBranchForm({ ...branchForm, branch_code: '', branch_name: '', short_name: '' });
                        },
                        'Branch created.',
                      )
                    }
                    className="h-10 rounded-md bg-blue-600 px-4 text-sm font-semibold text-white disabled:opacity-50"
                  >
                    {busyAction === 'branch' ? 'Saving...' : 'Create Branch'}
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'people' && (
              <div className="mt-5 grid gap-6 lg:grid-cols-3">
                <div className="space-y-3">
                  <h3 className="text-base font-semibold text-slate-950">Department</h3>
                  <SelectInput label="Branch" value={departmentForm.branch_id} onChange={(value) => setDepartmentForm({ ...departmentForm, branch_id: value })}>
                    <option value="">Select branch</option>
                    {branches.map((branch) => (
                      <option key={branch.id} value={branch.id}>{displayCode(branch.branch_name, branch.branch_code)}</option>
                    ))}
                  </SelectInput>
                  <TextInput label="Code" value={departmentForm.department_code} onChange={(value) => setDepartmentForm({ ...departmentForm, department_code: value })} />
                  <TextInput label="Name" value={departmentForm.department_name} onChange={(value) => setDepartmentForm({ ...departmentForm, department_name: value })} />
                  <button
                    type="button"
                    disabled={!!busyAction || !departmentForm.branch_id || !departmentForm.department_code || !departmentForm.department_name}
                    onClick={() =>
                      runAction(
                        'department',
                        async () => {
                          await apiClient.createEomDepartment({ tenant_id: tenantId, ...departmentForm });
                          setDepartmentForm({ ...departmentForm, department_code: '', department_name: '' });
                        },
                        'Department created.',
                      )
                    }
                    className="h-10 rounded-md bg-blue-600 px-4 text-sm font-semibold text-white disabled:opacity-50"
                  >
                    {busyAction === 'department' ? 'Saving...' : 'Create Department'}
                  </button>
                </div>

                <div className="space-y-3">
                  <h3 className="text-base font-semibold text-slate-950">Team</h3>
                  <SelectInput label="Department" value={teamForm.department_id} onChange={(value) => setTeamForm({ ...teamForm, department_id: value })}>
                    <option value="">Select department</option>
                    {departments.map((department) => (
                      <option key={department.id} value={department.id}>{displayCode(department.department_name, department.department_code)}</option>
                    ))}
                  </SelectInput>
                  <TextInput label="Code" value={teamForm.team_code} onChange={(value) => setTeamForm({ ...teamForm, team_code: value })} />
                  <TextInput label="Name" value={teamForm.team_name} onChange={(value) => setTeamForm({ ...teamForm, team_name: value })} />
                  <button
                    type="button"
                    disabled={!!busyAction || !teamForm.department_id || !teamForm.team_code || !teamForm.team_name}
                    onClick={() =>
                      runAction(
                        'team',
                        async () => {
                          await apiClient.createEomTeam({ tenant_id: tenantId, ...teamForm });
                          setTeamForm({ ...teamForm, team_code: '', team_name: '' });
                        },
                        'Team created.',
                      )
                    }
                    className="h-10 rounded-md bg-blue-600 px-4 text-sm font-semibold text-white disabled:opacity-50"
                  >
                    {busyAction === 'team' ? 'Saving...' : 'Create Team'}
                  </button>
                </div>

                <div className="space-y-3">
                  <h3 className="text-base font-semibold text-slate-950">Position</h3>
                  <SelectInput label="Department" value={positionForm.department_id} onChange={(value) => setPositionForm({ ...positionForm, department_id: value })}>
                    <option value="">Optional department</option>
                    {departments.map((department) => (
                      <option key={department.id} value={department.id}>{displayCode(department.department_name, department.department_code)}</option>
                    ))}
                  </SelectInput>
                  <SelectInput label="Team" value={positionForm.team_id} onChange={(value) => setPositionForm({ ...positionForm, team_id: value })}>
                    <option value="">Optional team</option>
                    {teams.map((team) => (
                      <option key={team.id} value={team.id}>{displayCode(team.team_name, team.team_code)}</option>
                    ))}
                  </SelectInput>
                  <TextInput label="Code" value={positionForm.position_code} onChange={(value) => setPositionForm({ ...positionForm, position_code: value })} />
                  <TextInput label="Title" value={positionForm.position_title} onChange={(value) => setPositionForm({ ...positionForm, position_title: value })} />
                  <button
                    type="button"
                    disabled={!!busyAction || !positionForm.position_code || !positionForm.position_title}
                    onClick={() =>
                      runAction(
                        'position',
                        async () => {
                          await apiClient.createEomPosition({
                            tenant_id: tenantId,
                            ...positionForm,
                            department_id: positionForm.department_id || undefined,
                            team_id: positionForm.team_id || undefined,
                          });
                          setPositionForm({ ...positionForm, position_code: '', position_title: '', grade: '' });
                        },
                        'Position created.',
                      )
                    }
                    className="h-10 rounded-md bg-blue-600 px-4 text-sm font-semibold text-white disabled:opacity-50"
                  >
                    {busyAction === 'position' ? 'Saving...' : 'Create Position'}
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'assets' && (
              <div className="mt-5 grid gap-6 lg:grid-cols-2">
                <div className="space-y-3">
                  <h3 className="text-base font-semibold text-slate-950">Vendor</h3>
                  <div className="grid gap-3 sm:grid-cols-2">
                    <TextInput label="Vendor Code" value={vendorForm.vendor_code} onChange={(value) => setVendorForm({ ...vendorForm, vendor_code: value })} />
                    <TextInput label="Vendor Name" value={vendorForm.vendor_name} onChange={(value) => setVendorForm({ ...vendorForm, vendor_name: value })} />
                  </div>
                  <TextInput label="Type" value={vendorForm.vendor_type} onChange={(value) => setVendorForm({ ...vendorForm, vendor_type: value })} />
                  <TextInput label="Contact Person" value={vendorForm.contact_person} onChange={(value) => setVendorForm({ ...vendorForm, contact_person: value })} />
                  <button
                    type="button"
                    disabled={!!busyAction || !vendorForm.vendor_code || !vendorForm.vendor_name}
                    onClick={() =>
                      runAction(
                        'vendor',
                        async () => {
                          await apiClient.createEomVendor({ tenant_id: tenantId, ...vendorForm });
                          setVendorForm({ vendor_code: '', vendor_name: '', vendor_type: '', contact_person: '', email: '', phone: '' });
                        },
                        'Vendor created.',
                      )
                    }
                    className="h-10 rounded-md bg-blue-600 px-4 text-sm font-semibold text-white disabled:opacity-50"
                  >
                    {busyAction === 'vendor' ? 'Saving...' : 'Create Vendor'}
                  </button>
                </div>

                <div className="space-y-3">
                  <h3 className="text-base font-semibold text-slate-950">Asset</h3>
                  <SelectInput label="Vendor" value={assetForm.vendor_id} onChange={(value) => setAssetForm({ ...assetForm, vendor_id: value })}>
                    <option value="">Optional vendor</option>
                    {vendors.map((vendor) => (
                      <option key={vendor.id} value={vendor.id}>{displayCode(vendor.vendor_name, vendor.vendor_code)}</option>
                    ))}
                  </SelectInput>
                  <SelectInput label="Branch" value={assetForm.branch_id} onChange={(value) => setAssetForm({ ...assetForm, branch_id: value })}>
                    <option value="">Optional branch</option>
                    {branches.map((branch) => (
                      <option key={branch.id} value={branch.id}>{displayCode(branch.branch_name, branch.branch_code)}</option>
                    ))}
                  </SelectInput>
                  <div className="grid gap-3 sm:grid-cols-2">
                    <TextInput label="Asset Code" value={assetForm.asset_code} onChange={(value) => setAssetForm({ ...assetForm, asset_code: value })} />
                    <TextInput label="Asset Name" value={assetForm.asset_name} onChange={(value) => setAssetForm({ ...assetForm, asset_name: value })} />
                  </div>
                  <button
                    type="button"
                    disabled={!!busyAction || !assetForm.asset_code || !assetForm.asset_name}
                    onClick={() =>
                      runAction(
                        'asset',
                        async () => {
                          await apiClient.createEomAsset({
                            tenant_id: tenantId,
                            ...assetForm,
                            vendor_id: assetForm.vendor_id || undefined,
                            branch_id: assetForm.branch_id || undefined,
                            department_id: assetForm.department_id || undefined,
                            purchase_value: Number(assetForm.purchase_value || 0),
                          });
                          setAssetForm({ ...assetForm, asset_code: '', asset_name: '', asset_type: '', purchase_value: '0' });
                        },
                        'Asset created.',
                      )
                    }
                    className="h-10 rounded-md bg-blue-600 px-4 text-sm font-semibold text-white disabled:opacity-50"
                  >
                    {busyAction === 'asset' ? 'Saving...' : 'Create Asset'}
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'ownership' && (
              <div className="mt-5 grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
                <div className="space-y-3">
                  <h3 className="text-base font-semibold text-slate-950">Customer Branch Ownership</h3>
                  <SelectInput label="Customer" value={selectedCustomerId} onChange={setSelectedCustomerId}>
                    <option value="">Select customer</option>
                    {customers.map((customer) => (
                      <option key={customer.id} value={customer.id}>
                        {customer.first_name} {customer.last_name} ({customer.email || customer.phone || customer.id})
                      </option>
                    ))}
                  </SelectInput>
                  <SelectInput label="Branch" value={selectedBranchId} onChange={setSelectedBranchId}>
                    <option value="">Select branch</option>
                    {branches.map((branch) => (
                      <option key={branch.id} value={branch.id}>{displayCode(branch.branch_name, branch.branch_code)}</option>
                    ))}
                  </SelectInput>
                  <button
                    type="button"
                    disabled={!!busyAction || !selectedCustomerId || !selectedBranchId}
                    onClick={() =>
                      runAction(
                        'ownership',
                        async () => {
                          await apiClient.assignCustomerBranch(selectedCustomerId, selectedBranchId, user?.username || 'system', tenantId);
                          await refreshMapping();
                        },
                        'Customer ownership assigned.',
                      )
                    }
                    className="h-10 rounded-md bg-blue-600 px-4 text-sm font-semibold text-white disabled:opacity-50"
                  >
                    {busyAction === 'ownership' ? 'Saving...' : 'Assign Ownership'}
                  </button>
                  <dl className="grid gap-3 rounded-md bg-slate-50 p-4 text-sm">
                    <div>
                      <dt className="font-semibold text-slate-500">Selected customer</dt>
                      <dd className="text-slate-900">
                        {selectedCustomer ? `${selectedCustomer.first_name} ${selectedCustomer.last_name}` : '-'}
                      </dd>
                    </div>
                    <div>
                      <dt className="font-semibold text-slate-500">Legacy branch</dt>
                      <dd className="text-slate-900">{selectedCustomer?.branch_id || '-'}</dd>
                    </div>
                  </dl>
                </div>

                <div>
                  <h3 className="text-base font-semibold text-slate-950">Ownership History</h3>
                  <div className="mt-3 overflow-x-auto">
                    <table className="w-full min-w-[560px] text-sm">
                      <thead>
                        <tr className="border-b border-slate-200 text-left text-slate-500">
                          <th className="px-3 py-2">Branch</th>
                          <th className="px-3 py-2">Status</th>
                          <th className="px-3 py-2">From</th>
                          <th className="px-3 py-2">To</th>
                          <th className="px-3 py-2">By</th>
                        </tr>
                      </thead>
                      <tbody>
                        {mappingHistory.map((item) => (
                          <tr key={item.id} className="border-b border-slate-100">
                            <td className="px-3 py-2 text-slate-800">{branchNames.get(item.branch_id) || item.branch_id}</td>
                            <td className="px-3 py-2 capitalize text-slate-700">{item.status}</td>
                            <td className="px-3 py-2 text-slate-700">{new Date(item.effective_from).toLocaleString()}</td>
                            <td className="px-3 py-2 text-slate-700">{item.effective_to ? new Date(item.effective_to).toLocaleString() : '-'}</td>
                            <td className="px-3 py-2 text-slate-700">{item.transferred_by || '-'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    {mappingHistory.length === 0 && (
                      <p className="rounded-md bg-slate-50 p-4 text-sm text-slate-600">No ownership history for this customer.</p>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </section>

        <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-950">Operating Master Lists</h2>
          <div className="mt-4 grid gap-6 lg:grid-cols-3">
            <div>
              <h3 className="text-sm font-semibold uppercase text-slate-500">Branches</h3>
              <div className="mt-2 max-h-72 overflow-auto">
                {branches.map((branch) => (
                  <div key={branch.id} className="border-b border-slate-100 py-2 text-sm">
                    <p className="font-medium text-slate-900">{branch.branch_name}</p>
                    <p className="text-slate-500">{branch.branch_code || branch.id}</p>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <h3 className="text-sm font-semibold uppercase text-slate-500">Positions</h3>
              <div className="mt-2 max-h-72 overflow-auto">
                {positions.map((position) => (
                  <div key={position.id} className="border-b border-slate-100 py-2 text-sm">
                    <p className="font-medium text-slate-900">{position.position_title}</p>
                    <p className="text-slate-500">{position.position_code} - {position.status}</p>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <h3 className="text-sm font-semibold uppercase text-slate-500">Vendors and Assets</h3>
              <div className="mt-2 max-h-72 overflow-auto">
                {[...vendors.map((vendor) => ({ id: `v-${vendor.id}`, name: vendor.vendor_name, meta: vendor.vendor_code })), ...assets.map((asset) => ({ id: `a-${asset.id}`, name: asset.asset_name, meta: asset.asset_code }))].map((item) => (
                  <div key={item.id} className="border-b border-slate-100 py-2 text-sm">
                    <p className="font-medium text-slate-900">{item.name}</p>
                    <p className="text-slate-500">{item.meta}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
