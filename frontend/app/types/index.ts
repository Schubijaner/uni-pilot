/**
 * Zentrale Type-Definitionen für die gesamte Anwendung
 */

// ============================================
// User & Profile Types
// ============================================

export interface UserProfile {
  firstName: string;
  lastName: string;
  university: string;
  major: string;
}

export interface University {
  id: number;
  name: string;
  abbreviation: string;
}

export interface StudyProgram {
  id: number;
  name: string;
  university_id: number;
  degree_type: string;
  created_at: string;
}

export interface Module {
    id: number;
    name: string;
    description: string;
    module_type: 'REQUIRED' | 'ELECTIVE';
    study_program_id: number;
    semester: number;
    created_at: string;
}

export interface Skill {
  name: string;
  value: number; // 0-100
}

export interface UserQuestion {
    id: number;
    question_text: string;
    answer: boolean;
    career_tree_node_id: number;
    created_at: string;
}

export interface UserData {
  profile: UserProfile;
  selectedModules: string[];
  skills: Skill[];
  skillsText: string;
}

// ============================================
// Module Types
// ============================================

export interface StudyModule {
  id: string;
  name: string;
  category: string;
  semester?: number;
}

// ============================================
// Job Tree Types
// ============================================

export interface JobLeaf {
  id: string;
  name: string;
  description: string;
  requiredSkills: Skill[];
  tags: string[];
}

export interface JobBranch {
  id: string;
  name: string;
  description: string;
  icon: string;
  jobs: JobLeaf[];
}

export interface FilterQuestion {
  id: string;
  question: string;
  options: FilterOption[];
}

export interface FilterOption {
  id: string;
  label: string;
  filterTags: string[]; // Tags die bei Auswahl angezeigt werden
}

// ============================================
// Roadmap Types
// ============================================

export type TodoType = 'module' | 'course' | 'project' | 'skill' | 'book' | 'certificate' | 'internship' | 'bootcamp' | 'career';

export interface RoadmapTodo {
  id: string;
  title: string;
  type: TodoType;
  completed: boolean;
  description?: string;
}

export interface SemesterPlan {
  semester: number;
  title: string;
  todos: RoadmapTodo[];
}

export interface CareerPath {
  jobId: string;
  jobName: string;
  requiredSkills: Skill[];
  roadmap: SemesterPlan[];
}

// ============================================
// Auth Types
// ============================================

export interface AuthCredentials {
  email: string;
  password: string;
}

export interface AuthUser {
  id: string;
  email: string;
  profile?: UserProfile;
}

// ============================================
// Onboarding Types
// ============================================

export type OnboardingStep = 
  | 'welcome'
  | 'profile'
  | 'modules'
  | 'skills'
  | 'auth';

export interface OnboardingState {
  currentStep: OnboardingStep;
  userData: UserData;
  isProcessingSkills: boolean;
  processedSkills: Skill[];
}
