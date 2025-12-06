/**
 * JobTree - Interaktive Baum-Komponente für die Job-Auswahl
 * Zeigt Branches (Hauptbereiche) und Leafs (konkrete Jobs)
 */

import React, { useState } from 'react';
import type { JobBranch, JobLeaf } from '~/types';
import { Card } from '~/components/ui';

interface JobTreeProps {
  branches: JobBranch[];
  visibleJobs: string[];
  selectedJobs: string[];
  onJobToggle: (jobId: string) => void;
}

export const JobTree: React.FC<JobTreeProps> = ({
  branches,
  visibleJobs,
  selectedJobs,
  onJobToggle,
}) => {
  const [expandedBranches, setExpandedBranches] = useState<string[]>(
    branches.map((b) => b.id) // All expanded by default
  );

  const toggleBranch = (branchId: string) => {
    setExpandedBranches((prev) =>
      prev.includes(branchId)
        ? prev.filter((id) => id !== branchId)
        : [...prev, branchId]
    );
  };

  const isJobVisible = (jobId: string) => visibleJobs.includes(jobId);
  const isJobSelected = (jobId: string) => selectedJobs.includes(jobId);

  // Count visible jobs per branch
  const getVisibleJobCount = (branch: JobBranch) => {
    return branch.jobs.filter((job) => isJobVisible(job.id)).length;
  };

  return (
    <div className="space-y-4">
      {branches.map((branch) => {
        const visibleCount = getVisibleJobCount(branch);
        const isExpanded = expandedBranches.includes(branch.id);
        const hasVisibleJobs = visibleCount > 0;

        return (
          <div
            key={branch.id}
            className={`
              rounded-2xl overflow-hidden transition-all duration-300
              ${hasVisibleJobs ? 'opacity-100' : 'opacity-40'}
            `}
          >
            {/* Branch Header */}
            <button
              onClick={() => toggleBranch(branch.id)}
              disabled={!hasVisibleJobs}
              className={`
                w-full px-5 py-4 flex items-center justify-between
                bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm
                border border-gray-200 dark:border-gray-700
                ${isExpanded ? 'rounded-t-2xl' : 'rounded-2xl'}
                transition-all duration-200
                hover:bg-gray-50 dark:hover:bg-gray-700/80
                disabled:cursor-not-allowed
              `}
            >
              <div className="flex items-center gap-3">
                <span className="text-2xl">{branch.icon}</span>
                <div className="text-left">
                  <h3 className="font-semibold text-gray-900 dark:text-white">
                    {branch.name}
                  </h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {branch.description}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="px-2.5 py-0.5 text-xs font-medium rounded-full bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300">
                  {visibleCount} / {branch.jobs.length}
                </span>
                <svg
                  className={`w-5 h-5 text-gray-400 transition-transform duration-300 ${
                    isExpanded ? 'rotate-180' : ''
                  }`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </div>
            </button>

            {/* Jobs (Leafs) */}
            <div
              className={`
                overflow-hidden transition-all duration-300
                ${isExpanded && hasVisibleJobs ? 'max-h-[500px] opacity-100' : 'max-h-0 opacity-0'}
              `}
            >
              <div className="bg-gray-50/80 dark:bg-gray-900/80 border-x border-b border-gray-200 dark:border-gray-700 rounded-b-2xl p-3 space-y-2">
                {branch.jobs.map((job) => (
                  <JobLeafCard
                    key={job.id}
                    job={job}
                    isVisible={isJobVisible(job.id)}
                    isSelected={isJobSelected(job.id)}
                    onToggle={() => onJobToggle(job.id)}
                  />
                ))}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

// Job Leaf Card Component
interface JobLeafCardProps {
  job: JobLeaf;
  isVisible: boolean;
  isSelected: boolean;
  onToggle: () => void;
}

const JobLeafCard: React.FC<JobLeafCardProps> = ({
  job,
  isVisible,
  isSelected,
  onToggle,
}) => {
  if (!isVisible) {
    return null;
  }

  return (
    <Card
      variant={isSelected ? 'glass' : 'default'}
      padding="sm"
      hoverable
      onClick={onToggle}
      className={`
        transition-all duration-200 cursor-pointer
        ${isSelected
          ? 'ring-2 ring-indigo-500 bg-indigo-50/80 dark:bg-indigo-950/50'
          : 'hover:bg-white dark:hover:bg-gray-800'
        }
      `}
    >
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <h4 className="font-medium text-gray-900 dark:text-white">
            {job.name}
          </h4>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {job.description}
          </p>
          {/* Skill Tags */}
          <div className="flex flex-wrap gap-1.5 mt-2">
            {job.requiredSkills.slice(0, 3).map((skill) => (
              <span
                key={skill.name}
                className="px-2 py-0.5 text-xs rounded-full bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300"
              >
                {skill.name}
              </span>
            ))}
            {job.requiredSkills.length > 3 && (
              <span className="px-2 py-0.5 text-xs rounded-full bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300">
                +{job.requiredSkills.length - 3}
              </span>
            )}
          </div>
        </div>

        {/* Selection Indicator */}
        <div
          className={`
            w-6 h-6 rounded-full flex items-center justify-center
            transition-all duration-200
            ${isSelected
              ? 'bg-gradient-to-r from-indigo-500 to-purple-500'
              : 'border-2 border-gray-300 dark:border-gray-600'
            }
          `}
        >
          {isSelected && (
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
            </svg>
          )}
        </div>
      </div>
    </Card>
  );
};

export default JobTree;
