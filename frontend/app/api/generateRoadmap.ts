import baseUrl from './baseUrl';
import type { CareerPath, Skill, SkillImpact } from '~/types';
import { parseSkillImpactFromDescription, parseCurrentSkillsFromDescription } from '~/utils/parseSkillData';

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
  top_skills: Array<{ skill: string; score: number }> | null;
  skill_impact: Array<{ skill: string; impact: number }> | null;
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
  career_goals?: RoadmapItem[];
  target_skills: Array<{ skill: string; score: number }> | null;
  current_skills: Array<{ skill: string; score: number }> | null;
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

  // Parse current_skills from roadmap description (fallback to API field if available)
  let currentSkills: Skill[] = [];
  if (roadmapData.current_skills && Array.isArray(roadmapData.current_skills)) {
    currentSkills = roadmapData.current_skills.map(s => ({
      name: s.skill,
      value: Math.max(0, Math.min(100, s.score || 0)),
    }));
  } else {
    // Try parsing from description as fallback
    const parsed = parseCurrentSkillsFromDescription(roadmapData.description);
    if (parsed) {
      currentSkills = parsed;
    }
  }

  // Parse target_skills from leaf nodes (top_skills)
  let targetSkills: Skill[] = [];
  if (roadmapData.target_skills && Array.isArray(roadmapData.target_skills)) {
    targetSkills = roadmapData.target_skills.map(s => ({
      name: s.skill,
      value: Math.max(0, Math.min(100, s.score || 0)),
    }));
  } else {
    // Fallback: find leaf node with top_skills
    const leafNode = roadmapData.items.find(item => item.is_career_goal && item.is_leaf && item.top_skills);
    if (leafNode && leafNode.top_skills) {
      targetSkills = leafNode.top_skills.map(s => ({
        name: s.skill,
        value: Math.max(0, Math.min(100, s.score || 0)),
      }));
    }
  }

  // Group items by semester and is_semester_break
  const semesterPlans: Record<number, { regular: any[]; semesterBreak: any[] }> = {};

  // Process flat items array instead of tree
  roadmapData.items.forEach(item => {
    const semester = item.semester || 1;
    
    if (!semesterPlans[semester]) {
      semesterPlans[semester] = { regular: [], semesterBreak: [] };
    }
    
    // Parse skill_impact from description
    let skillImpact: SkillImpact[] | null = null;
    if (item.skill_impact && Array.isArray(item.skill_impact)) {
      skillImpact = item.skill_impact.map(s => ({
        skill: s.skill,
        impact: Math.max(0, Math.min(100, s.impact || 0)),
      }));
    } else {
      // Try parsing from description as fallback
      skillImpact = parseSkillImpactFromDescription(item.description);
    }
    
    const itemData = {
      id: item.id.toString(),
      title: item.title,
      type: item.item_type.toLowerCase(),
      completed: false,
      description: item.description,
      is_semester_break: item.is_semester_break,
      skill_impact: skillImpact || undefined,
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

  // Get career goal info - find the leaf node with is_career_goal=true
  let careerGoal: RoadmapItem | null = null;
  
  // First try career_goals array if available
  if (roadmapData.career_goals && roadmapData.career_goals.length > 0) {
    careerGoal = roadmapData.career_goals[0];
  } else {
    // Fallback: find leaf node with is_career_goal=true from items
    careerGoal = roadmapData.items.find(item => item.is_career_goal && item.is_leaf) || null;
  }
  
  // If still no career goal found, use roadmap name as fallback
  const jobName = careerGoal?.title || roadmapData.name || 'Karriereziel';
  const jobId = careerGoal?.id?.toString() || roadmapData.id.toString();

  return {
    jobId,
    jobName,
    requiredSkills: targetSkills, // Soll-Skills (target_skills)
    currentSkills: currentSkills, // Ist-Skills (current_skills)
    roadmap,
  };
}

