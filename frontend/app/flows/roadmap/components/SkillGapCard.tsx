/**
 * SkillGapCard - Zeigt Skill-Lücken und Empfehlungen
 */

import React from 'react';
import type { Skill } from '~/types';
import { Card, CardHeader, CardTitle } from '~/components/ui';

interface SkillGapCardProps {
  userSkills: Skill[];
  requiredSkills: Skill[];
}

interface SkillGap {
  name: string;
  userValue: number;
  requiredValue: number;
  gap: number;
}

export const SkillGapCard: React.FC<SkillGapCardProps> = ({
  userSkills,
  requiredSkills,
}) => {
  // Calculate skill gaps
  const skillGaps: SkillGap[] = requiredSkills.map((required) => {
    const userSkill = userSkills.find((s) => s.name === required.name);
    const userValue = userSkill?.value || 0;
    return {
      name: required.name,
      userValue,
      requiredValue: required.value,
      gap: Math.max(0, required.value - userValue),
    };
  }).sort((a, b) => b.gap - a.gap);

  const significantGaps = skillGaps.filter((g) => g.gap > 10);

  return (
    <Card variant="glass">
      <CardHeader>
        <CardTitle>
          <span className="flex items-center gap-2">
            <svg className="w-5 h-5 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            Skill-Lücken
          </span>
        </CardTitle>
      </CardHeader>

      {significantGaps.length === 0 ? (
        <div className="text-center py-6">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
            <svg className="w-8 h-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <p className="text-green-600 dark:text-green-400 font-medium">
            Großartig! Keine signifikanten Skill-Lücken.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {significantGaps.map((gap) => (
            <div key={gap.name} className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-medium text-gray-900 dark:text-white">
                  {gap.name}
                </span>
                <span className={`
                  text-sm font-medium
                  ${gap.gap > 30
                    ? 'text-red-500'
                    : gap.gap > 15
                      ? 'text-amber-500'
                      : 'text-yellow-500'
                  }
                `}>
                  -{gap.gap}%
                </span>
              </div>
              <div className="relative h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                {/* User skill (green) */}
                <div
                  className="absolute inset-y-0 left-0 bg-indigo-500 rounded-full"
                  style={{ width: `${gap.userValue}%` }}
                />
                {/* Required skill marker */}
                <div
                  className="absolute inset-y-0 w-1 bg-red-500"
                  style={{ left: `${gap.requiredValue}%` }}
                />
              </div>
              <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400">
                <span>Du: {gap.userValue}%</span>
                <span>Benötigt: {gap.requiredValue}%</span>
              </div>
            </div>
          ))}

          {/* Recommendations */}
          <div className="mt-6 p-4 rounded-xl bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-200 dark:border-indigo-800">
            <h4 className="font-medium text-indigo-700 dark:text-indigo-300 mb-2">
              💡 Empfehlung
            </h4>
            <p className="text-sm text-indigo-600 dark:text-indigo-400">
              Fokussiere dich zuerst auf <strong>{significantGaps[0]?.name}</strong>.
              Mit gezieltem Training kannst du diese Lücke in etwa 2-3 Monaten schließen.
            </p>
          </div>
        </div>
      )}
    </Card>
  );
};

export default SkillGapCard;
