import baseUrl from './baseUrl';
import type { CareerPath, Skill } from '~/types';

interface RoadmapItem {
  id: number;
  title: string;
  item_type: string;
  description?: string;
  semester?: number;
  is_semester_break?: boolean;
  is_leaf: boolean;
  is_career_goal: boolean;
  level: number;
  order: number;
  module_id?: number;
  is_important?: boolean;
  children: RoadmapItem[];
}

interface RoadmapResponse {
  id: number;
  topic_field_id: number;
  name: string;
  description: string;
  tree: RoadmapItem;
  career_goals: RoadmapItem[];
}

/**
 * Generate or get roadmap for a topic field
 */
export async function generateRoadmap(
  topicFieldId: number,
  token: string
): Promise<CareerPath> {

  // First try to get existing roadmap
  let response = await fetch(`${baseUrl}/topic-fields/${topicFieldId}/roadmap`, {
    method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
  });

  if (!response.ok) {
    throw new Error(`Failed to get/generate roadmap: ${response.statusText}`);
  }

  const roadmapData: RoadmapResponse = await response.json();

  // Transform the tree structure to CareerPath format
  const transformRoadmapItem = (item: RoadmapItem, semester: number): any => {
    if (item.is_leaf && item.is_career_goal) {
      // This is a career goal - we'll use it for the job info
      return null;
    }

    const todo = {
      id: item.id.toString(),
      title: item.title,
      type: item.item_type.toLowerCase() as 'module' | 'internship' | 'certification' | 'project' | 'skill',
      completed: false,
      description: item.description,
    };

    // Process children recursively
    const children = item.children
      .map(child => transformRoadmapItem(child, item.semester || semester))
      .filter(Boolean);

    return { todo, children, semester: item.semester || semester };
  };

  // Group items by semester
  const semesterPlans: Record<number, any[]> = {};

  const processTree = (item: RoadmapItem, parentSemester?: number) => {
    const semester = item.semester || parentSemester || 1;
    
    if (item.item_type === 'MODULE' || item.item_type === 'SKILL' || item.item_type === 'PROJECT' || item.item_type === 'CERTIFICATION') {
      if (!semesterPlans[semester]) {
        semesterPlans[semester] = [];
      }
      
      semesterPlans[semester].push({
        id: item.id.toString(),
        title: item.title,
        type: item.item_type.toLowerCase() as 'module' | 'internship' | 'certification' | 'project' | 'skill',
        completed: false,
        description: item.description,
      });
    }

    // Process children
    item.children.forEach(child => processTree(child, semester));
  };

  processTree(roadmapData.tree);

  // Convert to SemesterPlan format
  const roadmap = Object.entries(semesterPlans)
    .sort(([a], [b]) => parseInt(a) - parseInt(b))
    .map(([semester, todos]) => ({
      semester: parseInt(semester),
      title: `Semester ${semester}`,
      todos: todos,
    }));

  // Get career goal info
  const careerGoal = roadmapData.career_goals?.[0] || roadmapData.tree;
  const jobName = careerGoal.title || 'Career Goal';
  const jobId = careerGoal.id.toString();

  // Extract required skills from the roadmap (this would ideally come from the API)
  const requiredSkills: Skill[] = [];

  return {
    jobId,
    jobName,
    requiredSkills,
    roadmap,
  };
}

