/**
 * Utility functions to parse skill data from description fields
 * Backend stores skill_impact and current_skills in description with placeholders
 */

import type { Skill, SkillImpact } from '~/types';

/**
 * Remove placeholder markers and their content from description
 * Returns only the clean description text without the skill data placeholders
 */
export function cleanDescription(description: string | null | undefined): string {
  if (!description) {
    return '';
  }

  let cleaned = description;

  // Remove __SKILL_DATA_START__ ... __SKILL_DATA_END__
  const skillDataStart = '__SKILL_DATA_START__';
  const skillDataEnd = '__SKILL_DATA_END__';
  const skillDataStartIndex = cleaned.indexOf(skillDataStart);
  const skillDataEndIndex = cleaned.indexOf(skillDataEnd);
  
  if (skillDataStartIndex !== -1 && skillDataEndIndex !== -1 && skillDataStartIndex < skillDataEndIndex) {
    cleaned = cleaned.substring(0, skillDataStartIndex) + cleaned.substring(skillDataEndIndex + skillDataEnd.length);
  }

  // Remove __CURRENT_SKILLS_START__ ... __CURRENT_SKILLS_END__
  const currentSkillsStart = '__CURRENT_SKILLS_START__';
  const currentSkillsEnd = '__CURRENT_SKILLS_END__';
  const currentSkillsStartIndex = cleaned.indexOf(currentSkillsStart);
  const currentSkillsEndIndex = cleaned.indexOf(currentSkillsEnd);
  
  if (currentSkillsStartIndex !== -1 && currentSkillsEndIndex !== -1 && currentSkillsStartIndex < currentSkillsEndIndex) {
    cleaned = cleaned.substring(0, currentSkillsStartIndex) + cleaned.substring(currentSkillsEndIndex + currentSkillsEnd.length);
  }

  // Clean up extra whitespace/newlines
  return cleaned.trim();
}

/**
 * Parse skill_impact from description field using placeholders
 * Format: __SKILL_DATA_START__\n{json}\n__SKILL_DATA_END__
 */
export function parseSkillImpactFromDescription(description: string | null | undefined): SkillImpact[] | null {
  if (!description) {
    return null;
  }

  const startMarker = '__SKILL_DATA_START__';
  const endMarker = '__SKILL_DATA_END__';

  const startIndex = description.indexOf(startMarker);
  const endIndex = description.indexOf(endMarker);

  if (startIndex === -1 || endIndex === -1 || startIndex >= endIndex) {
    return null;
  }

  try {
    const jsonString = description.substring(startIndex + startMarker.length, endIndex).trim();
    const data = JSON.parse(jsonString);
    
    if (data.skill_impact && Array.isArray(data.skill_impact)) {
      return data.skill_impact.map((item: any) => ({
        skill: item.skill || '',
        impact: Math.max(0, Math.min(100, item.impact || 0)),
      }));
    }
  } catch (error) {
    console.error('Failed to parse skill_impact from description:', error);
    return null;
  }

  return null;
}

/**
 * Parse current_skills from roadmap description field using placeholders
 * Format: __CURRENT_SKILLS_START__\n{json}\n__CURRENT_SKILLS_END__
 */
export function parseCurrentSkillsFromDescription(description: string | null | undefined): Skill[] | null {
  if (!description) {
    return null;
  }

  const startMarker = '__CURRENT_SKILLS_START__';
  const endMarker = '__CURRENT_SKILLS_END__';

  const startIndex = description.indexOf(startMarker);
  const endIndex = description.indexOf(endMarker);

  if (startIndex === -1 || endIndex === -1 || startIndex >= endIndex) {
    return null;
  }

  try {
    const jsonString = description.substring(startIndex + startMarker.length, endIndex).trim();
    const data = JSON.parse(jsonString);
    
    if (data.current_skills && Array.isArray(data.current_skills)) {
      return data.current_skills.map((item: any) => ({
        name: item.skill || '',
        value: Math.max(0, Math.min(100, item.score || 0)),
      }));
    }
  } catch (error) {
    console.error('Failed to parse current_skills from description:', error);
    return null;
  }

  return null;
}

