/**
 * Mock-Daten für die gesamte Anwendung
 */

import type { 
  StudyModule, 
  JobBranch, 
  FilterQuestion, 
  Skill,
  CareerPath,
  SemesterPlan 
} from '~/types';

// ============================================
// Study Modules (für Onboarding Step 3)
// ============================================

export const STUDY_MODULES: StudyModule[] = [
  { id: 'ds', name: 'Data Structures', category: 'Fundamentals', semester: 1 },
  { id: 'algo', name: 'Algorithms', category: 'Fundamentals', semester: 2 },
  { id: 'web1', name: 'Web Development I', category: 'Development', semester: 2 },
  { id: 'web2', name: 'Web Development II', category: 'Development', semester: 3 },
  { id: 'db', name: 'Database Systems', category: 'Data', semester: 3 },
  { id: 'ml', name: 'Machine Learning', category: 'AI/ML', semester: 4 },
  { id: 'sec', name: 'Cybersecurity Basics', category: 'Security', semester: 3 },
  { id: 'cloud', name: 'Cloud Computing', category: 'Infrastructure', semester: 4 },
  { id: 'mobile', name: 'Mobile App Development', category: 'Development', semester: 4 },
  { id: 'devops', name: 'DevOps & CI/CD', category: 'Infrastructure', semester: 5 },
];

// ============================================
// Job Tree (für Selection View)
// ============================================

export const JOB_BRANCHES: JobBranch[] = [
  {
    id: 'software-engineering',
    name: 'Software Engineering',
    description: 'Build and maintain software systems',
    icon: '💻',
    jobs: [
      {
        id: 'fullstack',
        name: 'Full-Stack Developer',
        description: 'End-to-end web application development',
        requiredSkills: [
          { name: 'React', value: 85 },
          { name: 'Node.js', value: 80 },
          { name: 'TypeScript', value: 75 },
          { name: 'SQL', value: 70 },
          { name: 'Git', value: 80 },
        ],
        tags: ['creative', 'technical', 'frontend', 'backend'],
      },
      {
        id: 'backend',
        name: 'Backend Engineer',
        description: 'Server-side logic and database management',
        requiredSkills: [
          { name: 'Python', value: 85 },
          { name: 'SQL', value: 90 },
          { name: 'Docker', value: 75 },
          { name: 'AWS', value: 70 },
          { name: 'Git', value: 80 },
        ],
        tags: ['analytical', 'technical', 'backend', 'systems'],
      },
      {
        id: 'frontend',
        name: 'Frontend Developer',
        description: 'User interface and experience implementation',
        requiredSkills: [
          { name: 'React', value: 90 },
          { name: 'CSS', value: 85 },
          { name: 'TypeScript', value: 80 },
          { name: 'UI/UX', value: 75 },
          { name: 'Git', value: 75 },
        ],
        tags: ['creative', 'visual', 'frontend', 'user-focused'],
      },
    ],
  },
  {
    id: 'data-science',
    name: 'Data Science',
    description: 'Extract insights from data',
    icon: '📊',
    jobs: [
      {
        id: 'ml-engineer',
        name: 'ML Engineer',
        description: 'Design and deploy machine learning models',
        requiredSkills: [
          { name: 'Python', value: 90 },
          { name: 'TensorFlow', value: 80 },
          { name: 'Statistics', value: 85 },
          { name: 'SQL', value: 75 },
          { name: 'Docker', value: 70 },
        ],
        tags: ['analytical', 'research', 'data', 'ai'],
      },
      {
        id: 'data-analyst',
        name: 'Data Analyst',
        description: 'Analyze and visualize data patterns',
        requiredSkills: [
          { name: 'SQL', value: 90 },
          { name: 'Python', value: 75 },
          { name: 'Statistics', value: 80 },
          { name: 'Visualization', value: 85 },
          { name: 'Excel', value: 80 },
        ],
        tags: ['analytical', 'business', 'data', 'reporting'],
      },
    ],
  },
  {
    id: 'cyber-security',
    name: 'Cyber Security',
    description: 'Protect systems and data',
    icon: '🔐',
    jobs: [
      {
        id: 'pentester',
        name: 'Penetration Tester',
        description: 'Identify security vulnerabilities',
        requiredSkills: [
          { name: 'Networking', value: 90 },
          { name: 'Linux', value: 85 },
          { name: 'Python', value: 75 },
          { name: 'Security Tools', value: 90 },
          { name: 'Scripting', value: 80 },
        ],
        tags: ['analytical', 'technical', 'security', 'offensive'],
      },
      {
        id: 'security-analyst',
        name: 'Security Analyst',
        description: 'Monitor and respond to security threats',
        requiredSkills: [
          { name: 'Networking', value: 85 },
          { name: 'SIEM', value: 80 },
          { name: 'Incident Response', value: 85 },
          { name: 'Linux', value: 75 },
          { name: 'Documentation', value: 70 },
        ],
        tags: ['analytical', 'monitoring', 'security', 'defensive'],
      },
    ],
  },
];

// ============================================
// Filter Questions (für Selection View)
// ============================================

export const FILTER_QUESTIONS: FilterQuestion[] = [
  {
    id: 'q1',
    question: 'Bevorzugen Sie kreative oder analytische Arbeit?',
    options: [
      { id: 'creative', label: 'Kreativ', filterTags: ['creative', 'visual', 'user-focused'] },
      { id: 'analytical', label: 'Analytisch', filterTags: ['analytical', 'data', 'systems'] },
      { id: 'both', label: 'Beides', filterTags: ['creative', 'analytical', 'visual', 'data'] },
    ],
  },
  {
    id: 'q2',
    question: 'Möchten Sie eher mit Nutzern oder mit Systemen arbeiten?',
    options: [
      { id: 'users', label: 'Mit Nutzern', filterTags: ['frontend', 'user-focused', 'business'] },
      { id: 'systems', label: 'Mit Systemen', filterTags: ['backend', 'systems', 'security'] },
      { id: 'both', label: 'Beides', filterTags: ['frontend', 'backend', 'user-focused', 'systems'] },
    ],
  },
  {
    id: 'q3',
    question: 'Welcher Bereich interessiert Sie am meisten?',
    options: [
      { id: 'web', label: 'Web & Apps', filterTags: ['frontend', 'backend', 'creative'] },
      { id: 'data', label: 'Daten & AI', filterTags: ['data', 'ai', 'research'] },
      { id: 'security', label: 'Sicherheit', filterTags: ['security', 'offensive', 'defensive'] },
    ],
  },
];

// ============================================
// Default Skills (für Skills Processing Simulation)
// ============================================

export const DEFAULT_PROCESSED_SKILLS: Skill[] = [
  { name: 'React', value: 75 },
  { name: 'Python', value: 90 },
  { name: 'TypeScript', value: 65 },
  { name: 'SQL', value: 70 },
  { name: 'Git', value: 80 },
  { name: 'Docker', value: 45 },
];

// ============================================
// Career Path Roadmaps (für Roadmap View)
// ============================================

export const generateRoadmap = (jobId: string, userSkills: Skill[]): CareerPath => {
  const allJobs = JOB_BRANCHES.flatMap(branch => branch.jobs);
  const job = allJobs.find(j => j.id === jobId) || allJobs[0];
  
  const roadmap: SemesterPlan[] = [
    {
      semester: 1,
      title: 'Semester 1 - Grundlagen',
      todos: [
        { id: '1-1', title: 'Data Structures', type: 'module', completed: false },
        { id: '1-2', title: 'Introduction to Programming', type: 'module', completed: false },
        { id: '1-3', title: 'GitHub Fundamentals', type: 'skill', completed: false, description: 'Complete GitHub Learning Path' },
      ],
    },
    {
      semester: 2,
      title: 'Semester 2 - Vertiefung',
      todos: [
        { id: '2-1', title: 'Algorithms', type: 'module', completed: false },
        { id: '2-2', title: 'Web Development I', type: 'module', completed: false },
        { id: '2-3', title: 'Build Portfolio Website', type: 'project', completed: false, description: 'Create personal portfolio' },
      ],
    },
    {
      semester: 3,
      title: 'Semester 3 - Spezialisierung',
      todos: [
        { id: '3-1', title: 'Database Systems', type: 'module', completed: false },
        { id: '3-2', title: 'Web Development II', type: 'module', completed: false },
        { id: '3-3', title: 'Summer Internship 2026', type: 'internship', completed: false, description: 'Apply for internship positions' },
      ],
    },
    {
      semester: 4,
      title: 'Semester 4 - Praxis',
      todos: [
        { id: '4-1', title: 'Cloud Computing', type: 'module', completed: false },
        { id: '4-2', title: 'AWS Certified Developer', type: 'certification', completed: false, description: 'Prepare for AWS certification' },
        { id: '4-3', title: 'Open Source Contribution', type: 'project', completed: false, description: 'Contribute to 2+ open source projects' },
      ],
    },
    {
      semester: 5,
      title: 'Semester 5 - Abschluss',
      todos: [
        { id: '5-1', title: 'DevOps & CI/CD', type: 'module', completed: false },
        { id: '5-2', title: 'Thesis Project', type: 'project', completed: false, description: 'Complete bachelor thesis' },
        { id: '5-3', title: 'Job Applications', type: 'skill', completed: false, description: 'Apply for full-time positions' },
      ],
    },
  ];

  return {
    jobId: job.id,
    jobName: job.name,
    requiredSkills: job.requiredSkills,
    roadmap,
  };
};
