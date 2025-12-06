/**
 * OnboardingFlow - Hauptkomponente für den Onboarding-Flow
 * Orchestriert alle Steps mit Navigation
 */

import React from 'react';
import { Layout } from '~/components/layout';
import { Button, ProgressSteps } from '~/components/ui';
import { OnboardingProvider, useOnboarding } from '~/contexts';
import {
  WelcomeStep,
  ProfileStep,
  ModulesStep,
  SkillsStep,
  AuthStep,
} from './steps';

// Step Konfiguration
const STEPS = [
  { id: 'welcome', label: 'Start' },
  { id: 'profile', label: 'Profil' },
  { id: 'modules', label: 'Module' },
  { id: 'skills', label: 'Skills' },
  { id: 'auth', label: 'Konto' },
];

// Step Renderer
const StepContent: React.FC = () => {
  const { state } = useOnboarding();

  switch (state.currentStep) {
    case 'welcome':
      return <WelcomeStep />;
    case 'profile':
      return <ProfileStep />;
    case 'modules':
      return <ModulesStep />;
    case 'skills':
      return <SkillsStep />;
    case 'auth':
      return <AuthStep />;
    default:
      return <WelcomeStep />;
  }
};

// Navigation Footer
const NavigationFooter: React.FC = () => {
  const { goToPrev, goToNext, canGoPrev, canGoNext, currentStepIndex, state } = useOnboarding();

  // Don't show navigation on welcome (has its own CTA) and auth (has submit)
  if (state.currentStep === 'welcome' || state.currentStep === 'auth') {
    return null;
  }
  
  const isNextDisabled = state.currentStep === 'modules' ? false : !canGoNext;

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-t border-gray-200 dark:border-gray-800 z-50">
      <div className="container mx-auto max-w-6xl px-4 py-4">
        <div className="flex items-center justify-between">
          <Button
            variant="ghost"
            onClick={goToPrev}
            disabled={!canGoPrev}
            leftIcon={
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            }
          >
            Zurück
          </Button>

          <span className="text-sm text-gray-500 dark:text-gray-400">
            Schritt {currentStepIndex + 1} von {STEPS.length}
          </span>

          <Button
            onClick={goToNext}
            disabled={isNextDisabled}
            rightIcon={
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            }
          >
            Weiter
          </Button>
        </div>
      </div>
    </div>
  );
};

// Back Button for welcome step navigation
const BackFromWelcome: React.FC = () => {
  const { state, canGoPrev, goToPrev } = useOnboarding();

  if (state.currentStep === 'welcome' || !canGoPrev) {
    return null;
  }

  return (
    <button
      onClick={goToPrev}
      className="fixed top-6 left-6 p-2 rounded-xl bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors z-50"
    >
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
      </svg>
    </button>
  );
};

// Inner component that uses the context
const OnboardingContent: React.FC = () => {
  const { currentStepIndex, state } = useOnboarding();

  return (
    <Layout variant="centered" showGradient>
      <div className="w-full max-w-4xl mx-auto">
        {/* Progress Steps (hidden on welcome) */}
        {state.currentStep !== 'welcome' && (
          <div className="mb-8 px-4">
            <ProgressSteps steps={STEPS} currentStep={currentStepIndex} />
          </div>
        )}

        {/* Step Content */}
        <div className={`px-4 ${state.currentStep !== 'auth' && state.currentStep !== 'welcome' ? 'pb-24' : ''}`}>
          <StepContent />
        </div>

        {/* Back Button */}
        <BackFromWelcome />

        {/* Navigation Footer */}
        <NavigationFooter />
      </div>
    </Layout>
  );
};

// Main Export with Provider
export const OnboardingFlow: React.FC = () => {
  return (
    <OnboardingProvider>
      <OnboardingContent />
    </OnboardingProvider>
  );
};

export default OnboardingFlow;
