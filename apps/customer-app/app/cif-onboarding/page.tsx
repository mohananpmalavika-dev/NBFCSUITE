'use client';

import { useState, useEffect } from 'react';
import { useCIFStore } from '@/lib/cif-store';
import StageSearch from './components/stage-search';
import StageProspect from './components/stage-prospect';
import StageBasicDetails from './components/stage-basic-details';
import StageIdentity from './components/stage-identity';
import StageAddress from './components/stage-address';
import StageContact from './components/stage-contact';
import StageFamily from './components/stage-family';
import StageEmployment from './components/stage-employment';
import StageBusiness from './components/stage-business';
import StageFinancial from './components/stage-financial';
import StageBanking from './components/stage-banking';
import StageCompliance from './components/stage-compliance';
import StageBehavior from './components/stage-behavior';
import StageRelationships from './components/stage-relationships';
import StageDocuments from './components/stage-documents';
import StageApproval from './components/stage-approval';
import StageReview from './components/stage-review';
import StageProgress from './components/stage-progress';

const stageLabels = [
  { id: 1, name: 'Search', icon: '🔍' },
  { id: 2, name: 'Prospect', icon: '💼' },
  { id: 3, name: 'Basic Details', icon: '📝' },
  { id: 4, name: 'Identity', icon: '🆔' },
  { id: 5, name: 'Address', icon: '📍' },
  { id: 6, name: 'Contact', icon: '📞' },
  { id: 7, name: 'Family', icon: '👨‍👩‍👧‍👦' },
  { id: 8, name: 'Employment', icon: '💼' },
  { id: 9, name: 'Business', icon: '🏢' },
  { id: 10, name: 'Financial', icon: '💰' },
  { id: 11, name: 'Banking', icon: '🏦' },
  { id: 12, name: 'Compliance', icon: '✅' },
  { id: 13, name: 'Behavior', icon: '🧠' },
  { id: 14, name: 'Relationships', icon: '🔗' },
  { id: 15, name: 'Documents', icon: '📦' },
  { id: 16, name: 'Approval', icon: '⚙️' },
  { id: 17, name: 'CIF Gen', icon: '🆔' },
  { id: 18, name: 'Customer 360', icon: '📊' },
];

export default function CIFOnboarding() {
  const { currentStep, setCurrentStep, isLoading, error, reset } = useCIFStore();
  const [showConfirm, setShowConfirm] = useState(false);

  useEffect(() => {
    // Check if user has unfinished onboarding
    const savedStep = localStorage.getItem('cif_current_step');
    if (savedStep) {
      setCurrentStep(parseInt(savedStep));
    }
  }, [setCurrentStep]);

  useEffect(() => {
    // Save current step to localStorage
    localStorage.setItem('cif_current_step', currentStep.toString());
  }, [currentStep]);

  const handleNext = () => {
    if (currentStep < 18) {
      setCurrentStep(currentStep + 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handlePrev = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handleReset = () => {
    if (confirm('Reset all data? This cannot be undone.')) {
      reset();
      localStorage.removeItem('cif_current_step');
      setCurrentStep(1);
      setShowConfirm(false);
    }
  };

  const renderStage = () => {
    switch (currentStep) {
      case 1:
        return <StageSearch />;
      case 2:
        return <StageProspect onNext={handleNext} />;
      case 3:
        return <StageBasicDetails onNext={handleNext} />;
      case 4:
        return <StageIdentity onNext={handleNext} />;
      case 5:
        return <StageAddress onNext={handleNext} />;
      case 6:
        return <StageContact onNext={handleNext} />;
      case 7:
        return <StageFamily onNext={handleNext} />;
      case 8:
        return <StageEmployment onNext={handleNext} />;
      case 9:
        return <StageBusiness onNext={handleNext} />;
      case 10:
        return <StageFinancial onNext={handleNext} />;
      case 11:
        return <StageBanking onNext={handleNext} />;
      case 12:
        return <StageCompliance onNext={handleNext} />;
      case 13:
        return <StageBehavior onNext={handleNext} />;
      case 14:
        return <StageRelationships onNext={handleNext} />;
      case 15:
        return <StageDocuments onNext={handleNext} />;
      case 16:
        return <StageApproval onNext={handleNext} />;
      case 17:
        return <StageReview onNext={handleNext} />;
      case 18:
        return <StageProgress />;
      default:
        return <div className="p-6 text-center text-slate-500">Stage {currentStep} - Coming Soon</div>;
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-blue-50 to-slate-50">
      {/* Header */}
      <div className="bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-slate-900">Customer Onboarding</h1>
              <p className="text-sm text-slate-600 mt-1">18-Stage CIF Creation Process</p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => setShowConfirm(true)}
                className="px-4 py-2 bg-red-50 text-red-700 rounded-lg hover:bg-red-100 transition-colors text-sm font-medium"
              >
                Reset
              </button>
              <button
                onClick={() => (window.location.href = '/customer-360')}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
              >
                Dashboard
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Progress Indicator */}
      <div className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            {stageLabels.map((stage, index) => (
              <div key={stage.id} className="flex items-center">
                <button
                  onClick={() => setCurrentStep(stage.id)}
                  className={`flex flex-col items-center gap-1 px-2 py-2 rounded-lg transition-all ${
                    currentStep === stage.id
                      ? 'bg-blue-100 text-blue-700'
                      : currentStep > stage.id
                      ? 'bg-green-100 text-green-700'
                      : 'bg-slate-100 text-slate-600'
                  }`}
                  title={stage.name}
                >
                  <span className="text-xl">{stage.icon}</span>
                  <span className="text-xs font-semibold hidden lg:inline">{stage.name}</span>
                </button>
                {index < stageLabels.length - 1 && (
                  <div
                    className={`h-1 w-2 mx-1 ${
                      currentStep > stage.id ? 'bg-green-500' : 'bg-slate-300'
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
          <div className="mt-4 text-sm text-slate-600">
            Stage {currentStep} of 18: {stageLabels[currentStep - 1].name}
          </div>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 m-4">
          <p className="text-red-700 font-semibold">Error</p>
          <p className="text-red-600 text-sm">{error}</p>
        </div>
      )}

      {/* Stage Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6 mb-6">
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <div className="inline-block animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full mb-4"></div>
                <p className="text-slate-600">Processing...</p>
              </div>
            </div>
          ) : (
            renderStage()
          )}
        </div>

        {/* Navigation Buttons */}
        <div className="flex justify-between gap-4">
          <button
            onClick={handlePrev}
            disabled={currentStep === 1 || isLoading}
            className="px-6 py-2 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
          >
            ← Previous
          </button>
          <button
            onClick={handleNext}
            disabled={currentStep === 18 || isLoading}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
          >
            Next →
          </button>
        </div>
      </div>

      {/* Reset Confirmation Modal */}
      {showConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 shadow-lg max-w-md">
            <h3 className="text-lg font-bold text-slate-900 mb-2">Reset Data?</h3>
            <p className="text-slate-600 mb-6">
              This will clear all entered information. This action cannot be undone.
            </p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowConfirm(false)}
                className="px-4 py-2 bg-slate-200 text-slate-700 rounded-lg hover:bg-slate-300"
              >
                Cancel
              </button>
              <button
                onClick={handleReset}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
              >
                Reset All
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
