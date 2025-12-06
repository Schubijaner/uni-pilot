/**
 * AppContext - Globaler Anwendungs-State
 * Verwaltet ausgewählte Jobs und Roadmap-Daten
 */

import React, { createContext, useContext, useReducer, useCallback, type ReactNode } from 'react';
import type { Skill, CareerPath } from '~/types';
import { generateRoadmap as generateRoadmapAPI } from '~/api/generateRoadmap';

// ============================================
// State Definition
// ============================================

interface AppState {
  selectedJobs: string[];
  userSkills: Skill[];
  currentCareerPath: CareerPath | null;
  isAuthenticated: boolean;
}

const initialState: AppState = {
  selectedJobs: [],
  userSkills: [],
  currentCareerPath: null,
  isAuthenticated: false,
};

// ============================================
// Action Types
// ============================================

type AppAction =
  | { type: 'SELECT_JOB'; payload: string }
  | { type: 'DESELECT_JOB'; payload: string }
  | { type: 'SET_SELECTED_JOBS'; payload: string[] }
  | { type: 'SET_USER_SKILLS'; payload: Skill[] }
  | { type: 'GENERATE_ROADMAP'; payload: CareerPath }
  | { type: 'SET_AUTHENTICATED'; payload: boolean }
  | { type: 'TOGGLE_TODO'; payload: { semester: number; todoId: string } };

// ============================================
// Reducer
// ============================================

function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'SELECT_JOB':
      if (state.selectedJobs.includes(action.payload)) {
        return state;
      }
      return { ...state, selectedJobs: [...state.selectedJobs, action.payload] };
    case 'DESELECT_JOB':
      return {
        ...state,
        selectedJobs: state.selectedJobs.filter((id) => id !== action.payload),
      };
    case 'SET_SELECTED_JOBS':
      return { ...state, selectedJobs: action.payload };
    case 'SET_USER_SKILLS':
      return { ...state, userSkills: action.payload };
    case 'GENERATE_ROADMAP': {
      return { ...state, currentCareerPath: action.payload };
    }
    case 'SET_AUTHENTICATED':
      return { ...state, isAuthenticated: action.payload };
    case 'TOGGLE_TODO': {
      if (!state.currentCareerPath) return state;
      const updatedRoadmap = state.currentCareerPath.roadmap.map((semesterPlan) => {
        if (semesterPlan.semester !== action.payload.semester) return semesterPlan;
        return {
          ...semesterPlan,
          todos: semesterPlan.todos.map((todo) =>
            todo.id === action.payload.todoId
              ? { ...todo, completed: !todo.completed }
              : todo
          ),
        };
      });
      return {
        ...state,
        currentCareerPath: { ...state.currentCareerPath, roadmap: updatedRoadmap },
      };
    }
    default:
      return state;
  }
}

// ============================================
// Context Definition
// ============================================

interface AppContextType {
  state: AppState;
  selectJob: (jobId: string) => void;
  deselectJob: (jobId: string) => void;
  toggleJob: (jobId: string) => void;
  isJobSelected: (jobId: string) => boolean;
  setUserSkills: (skills: Skill[]) => void;
  generateRoadmap: (topicFieldIds: number[], token: string) => Promise<void>;
  toggleTodo: (semester: number, todoId: string) => void;
  setAuthenticated: (value: boolean) => void;
}

const AppContext = createContext<AppContextType | null>(null);

// ============================================
// Provider Component
// ============================================

interface AppProviderProps {
  children: ReactNode;
}

export const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState);

  const selectJob = useCallback((jobId: string) => {
    dispatch({ type: 'SELECT_JOB', payload: jobId });
  }, []);

  const deselectJob = useCallback((jobId: string) => {
    dispatch({ type: 'DESELECT_JOB', payload: jobId });
  }, []);

  const toggleJob = useCallback((jobId: string) => {
    if (state.selectedJobs.includes(jobId)) {
      dispatch({ type: 'DESELECT_JOB', payload: jobId });
    } else {
      dispatch({ type: 'SELECT_JOB', payload: jobId });
    }
  }, [state.selectedJobs]);

  const isJobSelected = useCallback(
    (jobId: string) => state.selectedJobs.includes(jobId),
    [state.selectedJobs]
  );

  const setUserSkills = useCallback((skills: Skill[]) => {
    dispatch({ type: 'SET_USER_SKILLS', payload: skills });
  }, []);

  const generateRoadmapAction = useCallback(async (topicFieldIds: number[], token: string) => {
    // For now, use the first topic field ID
    // In the future, we might want to handle multiple topic fields
    if (topicFieldIds.length === 0) {
      console.error('No topic field IDs provided');
      return;
    }
    
    try {
      const roadmap = await generateRoadmapAPI(topicFieldIds[0], token);
      dispatch({ type: 'GENERATE_ROADMAP', payload: roadmap });
    } catch (error) {
      console.error('Failed to generate roadmap:', error);
      throw error;
    }
  }, []);

  const toggleTodo = useCallback((semester: number, todoId: string) => {
    dispatch({ type: 'TOGGLE_TODO', payload: { semester, todoId } });
  }, []);

  const setAuthenticated = useCallback((value: boolean) => {
    dispatch({ type: 'SET_AUTHENTICATED', payload: value });
  }, []);

  const value: AppContextType = {
    state,
    selectJob,
    deselectJob,
    toggleJob,
    isJobSelected,
    setUserSkills,
    generateRoadmap: generateRoadmapAction,
    toggleTodo,
    setAuthenticated,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};

// ============================================
// Custom Hook
// ============================================

export const useApp = (): AppContextType => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};

export default AppContext;
