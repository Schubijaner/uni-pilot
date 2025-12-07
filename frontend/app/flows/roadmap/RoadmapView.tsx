/**
 * RoadmapView - Hauptansicht für die Karriere-Roadmap
 * Kombiniert Radar Chart und Semester-ToDos
 */

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router';
import { Layout } from '~/components/layout';
import { Card, CardHeader, CardTitle, CardDescription, Button, RadarChart, Accordion } from '~/components/ui';
import { useApp } from '~/contexts';
import { SemesterAccordion } from './components/SemesterAccordion';
import { SkillGapCard } from './components/SkillGapCard';

export const RoadmapView: React.FC = () => {
  const navigate = useNavigate();
  const { state, toggleTodo, generateRoadmap, token } = useApp();
  const { currentCareerPath, currentTopicFieldId, userSkills } = state;
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch roadmap if we have a topic field ID but no roadmap data
  useEffect(() => {
    const fetchRoadmap = async () => {
      if (!currentCareerPath && currentTopicFieldId && token) {
        setIsLoading(true);
        setError(null);
        try {
          await generateRoadmap(currentTopicFieldId, token);
        } catch (err) {
          console.error('Failed to fetch roadmap:', err);
          setError('Fehler beim Laden der Roadmap');
        } finally {
          setIsLoading(false);
        }
      }
    };

    fetchRoadmap();
  }, [currentCareerPath, currentTopicFieldId, token, generateRoadmap]);

  // Loading state
  if (isLoading) {
    return (
      <Layout variant="centered">
        <Card variant="glass" className="text-center max-w-md">
          <div className="py-8">
            <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center">
              <svg className="w-10 h-10 text-indigo-500 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
            </div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              Roadmap wird geladen...
            </h2>
            <p className="text-gray-500 dark:text-gray-400">
              Bitte warte einen Moment.
            </p>
          </div>
        </Card>
      </Layout>
    );
  }

  // Error state
  if (error) {
    return (
      <Layout variant="centered">
        <Card variant="glass" className="text-center max-w-md">
          <div className="py-8">
            <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
              <svg className="w-10 h-10 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              Fehler beim Laden
            </h2>
            <p className="text-gray-500 dark:text-gray-400 mb-6">
              {error}
            </p>
            <Button onClick={() => navigate('/selection')}>
              Zur Auswahl
            </Button>
          </div>
        </Card>
      </Layout>
    );
  }

  // Redirect if no career path and no topic field ID
  if (!currentCareerPath && !currentTopicFieldId) {
    return (
      <Layout variant="centered">
        <Card variant="glass" className="text-center max-w-md">
          <div className="py-8">
            <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
              <svg className="w-10 h-10 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              Keine Roadmap gefunden
            </h2>
            <p className="text-gray-500 dark:text-gray-400 mb-6">
              Bitte wähle zuerst einen Karrierepfad aus.
            </p>
            <Button onClick={() => navigate('/selection')}>
              Zur Auswahl
            </Button>
          </div>
        </Card>
      </Layout>
    );
  }

  // Still loading (waiting for roadmap to be fetched)
  if (!currentCareerPath) {
    return (
      <Layout variant="centered">
        <Card variant="glass" className="text-center max-w-md">
          <div className="py-8">
            <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center">
              <svg className="w-10 h-10 text-indigo-500 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
            </div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              Roadmap wird geladen...
            </h2>
          </div>
        </Card>
      </Layout>
    );
  }

  // Calculate overall progress
  const allTodos = currentCareerPath.roadmap.flatMap((s) => s.todos);
  const completedTodos = allTodos.filter((t) => t.completed);
  const overallProgress = (completedTodos.length / allTodos.length) * 100;

  return (
    <Layout>
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400 mb-2">
          <button
            onClick={() => navigate('/selection')}
            className="hover:text-indigo-500 transition-colors"
          >
            Auswahl
          </button>
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
          <span className="text-gray-900 dark:text-white font-medium">Roadmap</span>
        </div>
        <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-2">
          Dein Weg zum{' '}
          <span className="bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
            {currentCareerPath.jobName}
          </span>
        </h1>
        <p className="text-gray-600 dark:text-gray-400 text-lg">
          Personalisierte Roadmap basierend auf deinen Skills und Zielen.
        </p>
      </div>

      {/* Overall Progress */}
      <Card variant="glass" className="mb-8">
        <div className="flex flex-col md:flex-row md:items-center gap-6">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              Gesamtfortschritt
            </h3>
            <div className="flex items-center gap-4">
              <div className="flex-1 h-4 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-full transition-all duration-500"
                  style={{ width: `${overallProgress}%` }}
                />
              </div>
              <span className="text-2xl font-bold text-gray-900 dark:text-white">
                {Math.round(overallProgress)}%
              </span>
            </div>
          </div>
          <div className="flex gap-4 text-center">
            <div className="px-4">
              <p className="text-3xl font-bold text-indigo-600 dark:text-indigo-400">
                {completedTodos.length}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">Erledigt</p>
            </div>
            <div className="px-4 border-l border-gray-200 dark:border-gray-700">
              <p className="text-3xl font-bold text-gray-400">
                {allTodos.length - completedTodos.length}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">Offen</p>
            </div>
          </div>
        </div>
      </Card>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Column - Skill Visualization */}
        <div className="space-y-6">
          {/* Radar Chart */}
          <Card variant="glass">
            <CardHeader>
              <CardTitle>Skill-Vergleich</CardTitle>
              <CardDescription>
                Deine aktuellen Skills vs. Anforderungen für {currentCareerPath.jobName}
              </CardDescription>
            </CardHeader>
            <div className="flex justify-center py-4">
              <RadarChart
                userSkills={userSkills}
                requiredSkills={currentCareerPath.requiredSkills}
                size={320}
              />
            </div>
          </Card>

          {/* Skill Gap Card */}
          <SkillGapCard
            userSkills={userSkills}
            requiredSkills={currentCareerPath.requiredSkills}
          />
        </div>

        {/* Right Column - Semester ToDos */}
        <div>
          <Card variant="glass">
            <CardHeader>
              <CardTitle>
                <span className="flex items-center gap-2">
                  <svg className="w-5 h-5 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                  </svg>
                  Semester-Aufgaben
                </span>
              </CardTitle>
              <CardDescription>
                Dein Schritt-für-Schritt Plan zum Karriereziel
              </CardDescription>
            </CardHeader>

            <Accordion className="mt-4">
              {currentCareerPath.roadmap.map((semesterPlan, index) => (
                <SemesterAccordion
                  key={semesterPlan.semester}
                  semesterPlan={semesterPlan}
                  onTodoToggle={(todoId) => toggleTodo(semesterPlan.semester, todoId)}
                  defaultOpen={index === 0}
                />
              ))}
            </Accordion>
          </Card>
        </div>
      </div>

      {/* Action Bar */}
      <div className="fixed bottom-0 left-0 right-0 bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-t border-gray-200 dark:border-gray-800 z-50">
        <div className="container mx-auto max-w-6xl px-4 py-4">
          <div className="flex items-center justify-between">
            <Button variant="ghost" onClick={() => navigate('/selection')}>
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Andere Karriere wählen
            </Button>
            <div className="flex gap-3">
              <Button variant="secondary" disabled>
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                </svg>
                Teilen
              </Button>
              <Button disabled>
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                PDF Export
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Spacer for fixed bottom bar */}
      <div className="h-24" />
    </Layout>
  );
};

export default RoadmapView;
