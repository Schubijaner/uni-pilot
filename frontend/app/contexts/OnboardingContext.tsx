/**
 * OnboardingContext - Zentraler State-Management für den Onboarding-Flow
 * Verwaltet alle Schritte, Navigation und Nutzerdaten
 */

import React, { createContext, useContext, useReducer, useCallback, type ReactNode } from 'react';
import type { OnboardingState, OnboardingStep, UserProfile, Skill } from '~/types';
import { getSkillsFromText } from '~/api/getSkillsFromText';

// ============================================
// Initial State
// ============================================

const initialUserData = {
  profile: {
    firstName: '',
    lastName: '',
    university: '',
    major: '',
  },
  selectedModules: [] as string[],
  skills: [] as Skill[],
  skillsText: '',
};

const initialState: OnboardingState = {
  currentStep: 'welcome',
  userData: initialUserData,
  isProcessingSkills: false,
  processedSkills: [],
};

// ============================================
// Step Order
// ============================================

const STEP_ORDER: OnboardingStep[] = ['welcome', 'profile', 'modules', 'skills', 'auth'];

// ============================================
// Action Types
// ============================================

type OnboardingAction =
  | { type: 'NEXT_STEP' }
  | { type: 'PREV_STEP' }
  | { type: 'GO_TO_STEP'; payload: OnboardingStep }
  | { type: 'UPDATE_PROFILE'; payload: Partial<UserProfile> }
  | { type: 'TOGGLE_MODULE'; payload: string }
  | { type: 'SET_SKILLS_TEXT'; payload: string }
  | { type: 'SET_PROCESSING_SKILLS'; payload: boolean }
  | { type: 'SET_PROCESSED_SKILLS'; payload: Skill[] }
  | { type: 'UPDATE_SKILL_VALUE'; payload: { name: string; value: number } }
  | { type: 'COMPLETE_ONBOARDING' };

// ============================================
// Reducer
// ============================================

function onboardingReducer(state: OnboardingState, action: OnboardingAction): OnboardingState {
  switch (action.type) {
    case 'NEXT_STEP': {
      const currentIndex = STEP_ORDER.indexOf(state.currentStep);
      if (currentIndex < STEP_ORDER.length - 1) {
        return { ...state, currentStep: STEP_ORDER[currentIndex + 1] };
      }
      return state;
    }
    case 'PREV_STEP': {
      const currentIndex = STEP_ORDER.indexOf(state.currentStep);
      if (currentIndex > 0) {
        return { ...state, currentStep: STEP_ORDER[currentIndex - 1] };
      }
      return state;
    }
    case 'GO_TO_STEP':
      return { ...state, currentStep: action.payload };
    case 'UPDATE_PROFILE':
      return {
        ...state,
        userData: {
          ...state.userData,
          profile: { ...state.userData.profile, ...action.payload },
        },
      };
    case 'TOGGLE_MODULE': {
      const modules = state.userData.selectedModules.includes(action.payload)
        ? state.userData.selectedModules.filter((m) => m !== action.payload)
        : [...state.userData.selectedModules, action.payload];
      return {
        ...state,
        userData: { ...state.userData, selectedModules: modules },
      };
    }
    case 'SET_SKILLS_TEXT':
      return {
        ...state,
        userData: { ...state.userData, skillsText: action.payload },
      };
    case 'SET_PROCESSING_SKILLS':
      return { ...state, isProcessingSkills: action.payload };
    case 'SET_PROCESSED_SKILLS':
      return { 
        ...state, 
        processedSkills: action.payload,
        userData: { ...state.userData, skills: action.payload },
      };
    case 'UPDATE_SKILL_VALUE': {
      const updatedSkills = state.processedSkills.map((skill) =>
        skill.name === action.payload.name
          ? { ...skill, value: action.payload.value }
          : skill
      );
      return { 
        ...state, 
        processedSkills: updatedSkills,
        userData: { ...state.userData, skills: updatedSkills },
      };
    }
    case 'COMPLETE_ONBOARDING':
      return state;
    default:
      return state;
  }
}

// ============================================
// Context Definition
// ============================================

interface OnboardingContextType {
  state: OnboardingState;
  currentStepIndex: number;
  totalSteps: number;
  // Navigation
  goToNext: () => void;
  goToPrev: () => void;
  goToStep: (step: OnboardingStep) => void;
  canGoNext: boolean;
  canGoPrev: boolean;
  // Profile
  updateProfile: (profile: Partial<UserProfile>) => void;
  isProfileValid: boolean;
  // Modules
  toggleModule: (moduleId: string) => void;
  isModuleSelected: (moduleId: string) => boolean;
  // Skills
  setSkillsText: (text: string) => void;
  processSkills: () => void;
  updateSkillValue: (name: string, value: number) => void;
}

const OnboardingContext = createContext<OnboardingContextType | null>(null);

// ============================================
// Provider Component
// ============================================

interface OnboardingProviderProps {
  children: ReactNode;
}

export const OnboardingProvider: React.FC<OnboardingProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(onboardingReducer, initialState);

  const currentStepIndex = STEP_ORDER.indexOf(state.currentStep);
  const totalSteps = STEP_ORDER.length;

  // Validation
  const isProfileValid = Boolean(
    state.userData.profile.firstName.trim() &&
    state.userData.profile.lastName.trim() &&
    state.userData.profile.university.trim() &&
    state.userData.profile.major.trim()
  );

  const canGoNext = 
    (state.currentStep === 'welcome') ||
    (state.currentStep === 'profile' && isProfileValid) ||
    (state.currentStep === 'modules') ||
    (state.currentStep === 'skills' && state.processedSkills.length > 0) ||
    (state.currentStep === 'auth');

  const canGoPrev = currentStepIndex > 0;

  // Navigation
  const goToNext = useCallback(() => {
    if (canGoNext) {
      dispatch({ type: 'NEXT_STEP' });
    }
  }, [canGoNext]);

  const goToPrev = useCallback(() => {
    dispatch({ type: 'PREV_STEP' });
  }, []);

  const goToStep = useCallback((step: OnboardingStep) => {
    dispatch({ type: 'GO_TO_STEP', payload: step });
  }, []);

  // Profile
  const updateProfile = useCallback((profile: Partial<UserProfile>) => {
    dispatch({ type: 'UPDATE_PROFILE', payload: profile });
  }, []);

  // Modules
  const toggleModule = useCallback((moduleId: string) => {
    dispatch({ type: 'TOGGLE_MODULE', payload: moduleId });
  }, []);

  const isModuleSelected = useCallback(
    (moduleId: string) => state.userData.selectedModules.includes(moduleId),
    [state.userData.selectedModules]
  );

  // Skills
  const setSkillsText = useCallback((text: string) => {
    dispatch({ type: 'SET_SKILLS_TEXT', payload: text });
  }, []);

  const processSkills = useCallback(async () => {
    dispatch({ type: 'SET_PROCESSING_SKILLS', payload: true });
    try {
      const response = await getSkillsFromText(state.userData.skillsText);
      dispatch({ type: 'SET_PROCESSED_SKILLS', payload: response.skills });
    } catch (error) {
      console.error('Failed to process skills:', error);
    } finally {
      dispatch({ type: 'SET_PROCESSING_SKILLS', payload: false });
    }
  }, [state.userData.skillsText]);

  const updateSkillValue = useCallback((name: string, value: number) => {
    dispatch({ type: 'UPDATE_SKILL_VALUE', payload: { name, value } });
  }, []);

  const value: OnboardingContextType = {
    state,
    currentStepIndex,
    totalSteps,
    goToNext,
    goToPrev,
    goToStep,
    canGoNext,
    canGoPrev,
    updateProfile,
    isProfileValid,
    toggleModule,
    isModuleSelected,
    setSkillsText,
    processSkills,
    updateSkillValue,
  };

  return (
    <OnboardingContext.Provider value={value}>
      {children}
    </OnboardingContext.Provider>
  );
};

// ============================================
// Custom Hook
// ============================================

export const useOnboarding = (): OnboardingContextType => {
  const context = useContext(OnboardingContext);
  if (!context) {
    throw new Error('useOnboarding must be used within an OnboardingProvider');
  }
  return context;
};

export default OnboardingContext;
