/**
 * ModulesStep - Modul-Auswahl im Onboarding
 * Mehrfachauswahl aus einer Liste von Studienmodulen
 */

import React, { useEffect, useState } from 'react';
import { getModulesByStudyProgram } from '~/api/getModulesByStudyProgram';
import { Card, CardHeader, CardTitle, CardDescription, Checkbox } from '~/components/ui';
import { useOnboarding } from '~/contexts';
import { STUDY_MODULES } from '~/data/mockData';
import type { Module } from '~/types';

export const ModulesStep: React.FC = () => {
  const { toggleModule, isModuleSelected, state } = useOnboarding();
  const [filter, setFilter] = useState<string>('all');
  const [modules, setModules] = useState<Module[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const studyProgramId = state.userData.profile.major;

  // Fetch modules based on selected study program
  useEffect(() => {
    const fetchModules = async () => {
      if (!studyProgramId) {
        setModules([]);
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        setError(null);
        const data = await getModulesByStudyProgram(parseInt(studyProgramId, 10));
        setModules(data.items);
      } catch (err) {
        console.error('Failed to fetch modules:', err);
        setError('Module konnten nicht geladen werden');
      } finally {
        setIsLoading(false);
      }
    };

    fetchModules();
  }, [studyProgramId]);

  // Unique module types for filter
  const moduleTypes = ['all', ...new Set(modules.map((m) => m.module_type))];

  // Filtered modules
  const filteredModules = filter === 'all'
    ? modules
    : modules.filter((m) => m.module_type === filter);

  // Group modules by semester
  const modulesBySemester = filteredModules.reduce((acc, module) => {
    const semester = module.semester;
    if (!acc[semester]) {
      acc[semester] = [];
    }
    acc[semester].push(module);
    return acc;
  }, {} as Record<number, Module[]>);

  // Sort semesters
  const sortedSemesters = Object.keys(modulesBySemester)
    .map(Number)
    .sort((a, b) => a - b);

  const selectedCount = state.userData.selectedModules.length;

  const getModuleTypeLabel = (type: string) => {
    switch (type) {
      case 'REQUIRED': return 'Pflicht';
      case 'ELECTIVE': return 'Wahl';
      default: return type;
    }
  };

  if (!studyProgramId) {
    return (
      <div className="max-w-3xl mx-auto">
        <Card variant="glass">
          <CardHeader>
            <CardTitle>Module auswählen</CardTitle>
            <CardDescription>
              Bitte wähle zuerst einen Studiengang im vorherigen Schritt aus.
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto">
      <Card variant="glass">
        <CardHeader>
          <CardTitle>
            <span className="flex items-center gap-3">
              <span className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </span>
              Wähle deine Module
            </span>
          </CardTitle>
          <CardDescription>
            Welche Module hast du bereits belegt?
          </CardDescription>
        </CardHeader>

        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
            <span className="ml-3 text-gray-600 dark:text-gray-400">Lade Module...</span>
          </div>
        ) : error ? (
          <div className="text-red-500 text-center py-8">{error}</div>
        ) : (
          <>
            {/* Modules grouped by Semester */}
            <div className="space-y-6">
              {sortedSemesters.map((semester) => (
                <div key={semester}>
                  <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 mb-3 flex items-center gap-2">
                    <span className="w-6 h-6 rounded-full bg-indigo-100 dark:bg-indigo-900 text-indigo-600 dark:text-indigo-400 flex items-center justify-center text-xs">
                      {semester}
                    </span>
                    Semester {semester}
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {modulesBySemester[semester].map((module) => (
                      <Checkbox
                        key={module.id}
                        label={module.name}
                        description={`${getModuleTypeLabel(module.module_type)}`}
                        checked={isModuleSelected(module.id.toString())}
                        onChange={() => toggleModule(module.id.toString())}
                      />
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </>
        )}

        {/* Selection Count */}
        <div className="mt-6 pt-4 border-t border-gray-100 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm">
              {selectedCount > 0 ? (
                <>
                  <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="text-green-600 dark:text-green-400">
                    {selectedCount} Modul{selectedCount !== 1 ? 'e' : ''} ausgewählt
                  </span>
                </>
              ) : (
                <span className="text-gray-500 dark:text-gray-400">
                  Keine Module ausgewählt (optional)
                </span>
              )}
            </div>

            {selectedCount > 0 && (
              <button
                onClick={() => {
                  state.userData.selectedModules.forEach((id) => toggleModule(id));
                }}
                className="text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
              >
                Auswahl zurücksetzen
              </button>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
};

export default ModulesStep;
