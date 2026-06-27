// CIF Onboarding State Management
import { create } from 'zustand';

export interface CIFState {
  // Current onboarding step (1-18)
  currentStep: number;
  
  // Customer/Prospect IDs
  prospectId: string | null;
  customerId: string | null;
  cifId: string | null;
  
  // Form data by stage
  searchData: {
    mobileNumber?: string;
    aadharNumber?: string;
    panNumber?: string;
    email?: string;
  };
  
  prospectData: {
    firstName: string;
    lastName: string;
    phone: string;
    email: string;
    source?: string;
  };
  
  basicDetails: {
    dateOfBirth?: string;
    gender?: string;
    occupation?: string;
    maritalStatus?: string;
    education?: string;
    pan?: string;
    aadhar?: string;
  };
  
  identityDocuments: Array<{
    type: string;
    number: string;
    file?: File;
    extractedData?: any;
  }>;
  
  address: {
    type: string;
    street?: string;
    city?: string;
    state?: string;
    postalCode?: string;
    country?: string;
  };
  
  contact: {
    phone?: string;
    email?: string;
    whatsapp?: string;
    preferredLanguage?: string;
  };
  
  employment: {
    type?: string;
    employer?: string;
    designation?: string;
    salary?: number;
  };
  
  financial: {
    monthlyIncome?: number;
    monthlyExpense?: number;
    assets?: number;
    liabilities?: number;
  };
  
  banking: {
    primaryBank?: string;
    accountNumber?: string;
    averageBalance?: number;
  };
  
  compliance: {
    panVerified?: boolean;
    aadharVerified?: boolean;
    amlPassed?: boolean;
    status?: string;
  };
  
  behavior: {
    riskAppetite?: string;
    spendingPattern?: string;
    finDna?: string;
    productAffinity?: Record<string, number>;
  };
  
  familyMembers?: Array<{
    name: string;
    relationship: string;
    dependents: boolean;
  }>;
  
  business?: {
    businessName?: string;
    businessType?: string;
    annualTurnover?: number;
    employees?: number;
    registrationNumber?: string;
  };
  
  documents: Array<{
    type: string;
    title: string;
    file?: File;
  }>;
  
  // Progress tracking
  completedStages: number[];
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setCurrentStep: (step: number) => void;
  setProspectId: (id: string) => void;
  setCustomerId: (id: string) => void;
  setCifId: (id: string) => void;
  updateSearchData: (data: Partial<CIFState['searchData']>) => void;
  updateProspectData: (data: Partial<CIFState['prospectData']>) => void;
  updateBasicDetails: (data: Partial<CIFState['basicDetails']>) => void;
  updateAddress: (data: Partial<CIFState['address']>) => void;
  updateContact: (data: Partial<CIFState['contact']>) => void;
  updateEmployment: (data: Partial<CIFState['employment']>) => void;
  updateFinancial: (data: Partial<CIFState['financial']>) => void;
  updateBanking: (data: Partial<CIFState['banking']>) => void;
  updateCompliance: (data: Partial<CIFState['compliance']>) => void;
  updateBehavior: (data: Partial<CIFState['behavior']>) => void;
  addDocument: (doc: { type: string; title: string; file?: File }) => void;
  removeDocument: (index: number) => void;
  addIdentityDocument: (doc: { type: string; number: string; file?: File; extractedData?: any }) => void;
  removeIdentityDocument: (index: number) => void;
  addFamilyMember: (member: { name: string; relationship: string; dependents: boolean }) => void;
  removeFamilyMember: (index: number) => void;
  updateBusiness: (data: Partial<CIFState['business']>) => void;
  markStageComplete: (stage: number) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

const initialState = {
  currentStep: 1,
  prospectId: null,
  customerId: null,
  cifId: null,
  searchData: {},
  prospectData: { firstName: '', lastName: '', phone: '', email: '' },
  basicDetails: {},
  identityDocuments: [],
  address: { type: 'permanent' },
  contact: {},
  employment: {},
  financial: {},
  banking: {},
  compliance: {},
  behavior: {},
  familyMembers: [],
  business: {},
  documents: [],
  completedStages: [],
  isLoading: false,
  error: null,
};

export const useCIFStore = create<CIFState>((set) => ({
  ...initialState,
  
  setCurrentStep: (step) => set({ currentStep: step }),
  setProspectId: (id) => set({ prospectId: id }),
  setCustomerId: (id) => set({ customerId: id }),
  setCifId: (id) => set({ cifId: id }),
  
  updateSearchData: (data) =>
    set((state) => ({
      searchData: { ...state.searchData, ...data },
    })),
  
  updateProspectData: (data) =>
    set((state) => ({
      prospectData: { ...state.prospectData, ...data },
    })),
  
  updateBasicDetails: (data) =>
    set((state) => ({
      basicDetails: { ...state.basicDetails, ...data },
    })),
  
  updateAddress: (data) =>
    set((state) => ({
      address: { ...state.address, ...data },
    })),
  
  updateContact: (data) =>
    set((state) => ({
      contact: { ...state.contact, ...data },
    })),
  
  updateEmployment: (data) =>
    set((state) => ({
      employment: { ...state.employment, ...data },
    })),
  
  updateFinancial: (data) =>
    set((state) => ({
      financial: { ...state.financial, ...data },
    })),
  
  updateBanking: (data) =>
    set((state) => ({
      banking: { ...state.banking, ...data },
    })),
  
  updateCompliance: (data) =>
    set((state) => ({
      compliance: { ...state.compliance, ...data },
    })),
  
  updateBehavior: (data) =>
    set((state) => ({
      behavior: { ...state.behavior, ...data },
    })),
  
  addDocument: (doc) =>
    set((state) => ({
      documents: [...state.documents, doc],
    })),
  
  removeDocument: (index) =>
    set((state) => ({
      documents: state.documents.filter((_, i) => i !== index),
    })),
  
  addIdentityDocument: (doc) =>
    set((state) => ({
      identityDocuments: [...state.identityDocuments, doc],
    })),

  removeIdentityDocument: (index) =>
    set((state) => ({
      identityDocuments: state.identityDocuments.filter((_, i) => i !== index),
    })),

  addFamilyMember: (member) =>
    set((state) => ({
      familyMembers: [...(state.familyMembers || []), member],
    })),

  removeFamilyMember: (index) =>
    set((state) => ({
      familyMembers: (state.familyMembers || []).filter((_, i) => i !== index),
    })),

  updateBusiness: (data) =>
    set((state) => ({
      business: { ...state.business, ...data },
    })),

  markStageComplete: (stage) =>
    set((state) => ({
      completedStages: [...new Set([...state.completedStages, stage])],
    })),
  
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
  reset: () => set(initialState),
}));
