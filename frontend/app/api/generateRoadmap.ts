import baseUrl from './baseUrl';
import type { CareerPath, Skill } from '~/types';

interface RoadmapItem {
  item_type: 'MODULE' | 'COURSE' | 'PROJECT' | 'SKILL' | 'BOOK' | 'CERTIFICATE' | 'INTERNSHIP' | 'BOOTCAMP' | 'CAREER';
  title: string;
  description: string;
  semester?: number;
  is_semester_break: boolean;
  order: number;
  level: number;
  is_leaf: boolean;
  is_career_goal: boolean;
  module_id: number | null;
  is_important: boolean;
  top_skills: any | null;
  id: number;
  roadmap_id: number;
  parent_id: number | null;
  created_at: string;
  children: RoadmapItem[];
}

interface RoadmapResponse {
  id: number;
  topic_field_id: number;
  name: string;
  description: string;
  tree: RoadmapItem;
  items: RoadmapItem[];
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

  // Group items by semester and is_semester_break
  const semesterPlans: Record<number, { regular: any[]; semesterBreak: any[] }> = {};

  // Process flat items array instead of tree
  roadmapData.items.forEach(item => {
    const semester = item.semester || 1;
    
    if (!semesterPlans[semester]) {
      semesterPlans[semester] = { regular: [], semesterBreak: [] };
    }
    
    const itemData = {
      id: item.id.toString(),
      title: item.title,
      type: item.item_type.toLowerCase(),
      completed: false,
      description: item.description,
      is_semester_break: item.is_semester_break,
    };

    if (item.is_semester_break) {
      semesterPlans[semester].semesterBreak.push(itemData);
    } else {
      semesterPlans[semester].regular.push(itemData);
    }
  });

  // Convert to SemesterPlan format - separate regular and semester break
  const roadmap: { semester: number; title: string; todos: any[] }[] = [];
  
  Object.entries(semesterPlans)
    .sort(([a], [b]) => parseInt(a) - parseInt(b))
    .forEach(([semester, todos]) => {
      // Add regular semester items
      if (todos.regular.length > 0) {
        roadmap.push({
          semester: parseInt(semester),
          title: `Semester ${semester}`,
          todos: todos.regular,
        });
      }
      
      // Add semester break items as separate entry
      if (todos.semesterBreak.length > 0) {
        roadmap.push({
          semester: parseInt(semester),
          title: `Semesterferien ${semester}`,
          todos: todos.semesterBreak,
        });
      }
    });

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

