/**
 * SkillsStep - Skills-Eingabe und Verarbeitung im Onboarding
 * Textarea für freie Eingabe, simulierte Verarbeitung, Slider-Feintuning
 */

import React from 'react';
import { getSkillsFromText } from '~/api/getSkillsFromText';
import { Card, CardHeader, CardTitle, CardDescription, Textarea, Button, Slider } from '~/components/ui';
import { useOnboarding } from '~/contexts';

export const SkillsStep: React.FC = () => {
  const {
    state,
    setSkillsText,
    processSkills,
    updateSkillValue,
  } = useOnboarding();

  const { skillsText } = state.userData;
  const { isProcessingSkills, processedSkills } = state;

  const hasProcessedSkills = processedSkills.length > 0;
  
  return (
    <div className="max-w-2xl mx-auto">
      <Card variant="glass">
        <CardHeader>
          <CardTitle>
            <span className="flex items-center gap-3">
              <span className="w-10 h-10 rounded-xl bg-gradient-to-br from-pink-500 to-orange-500 flex items-center justify-center text-white">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </span>
              Deine Skills
            </span>
          </CardTitle>
          <CardDescription>
            Erzähl uns von deinen technischen Fähigkeiten, Projekten und Erfahrungen.
          </CardDescription>
        </CardHeader>

        {/* Text Input - Always visible */}
        <div className="space-y-4">
          <Textarea
            label="Beschreibe deine Erfahrungen"
            placeholder="z.B. Ich habe 2 Jahre Erfahrung mit Python und Machine Learning. In meinem letzten Projekt habe ich eine React-App mit TypeScript entwickelt. Außerdem kenne ich mich mit SQL-Datenbanken aus..."
            value={skillsText}
            onChange={(e) => setSkillsText(e.target.value)}
            className="min-h-[150px]"
            disabled={isProcessingSkills}
          />

          <Button
            onClick={processSkills}
            disabled={skillsText.trim().length < 10 || isProcessingSkills}
            isLoading={isProcessingSkills}
            fullWidth
          >
            {isProcessingSkills ? 'Analysiere Skills...' : hasProcessedSkills ? 'Erneut analysieren' : 'Skills analysieren'}
          </Button>

          {isProcessingSkills && (
            <div className="text-center py-8">
              <div className="inline-flex items-center gap-3 px-6 py-4 rounded-2xl bg-indigo-50 dark:bg-indigo-900/30">
                <div className="relative">
                  <div className="w-10 h-10 rounded-full border-4 border-indigo-200 dark:border-indigo-800" />
                  <div className="absolute top-0 left-0 w-10 h-10 rounded-full border-4 border-transparent border-t-indigo-500 animate-spin" />
                </div>
                <div className="text-left">
                  <p className="font-medium text-indigo-700 dark:text-indigo-300">
                    Verarbeite deine Eingabe...
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Processed Skills Sliders */}
        {hasProcessedSkills && (
          <div className="space-y-6 mt-4">
            <div className="p-4 rounded-xl bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800">
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="font-medium text-green-700 dark:text-green-300">
                  Skills erfolgreich analysiert!
                </span>
              </div>
              <p className="text-sm text-green-600 dark:text-green-400 mt-1">
                Passe die Werte an, um deine tatsächlichen Fähigkeiten besser widerzuspiegeln.
              </p>
            </div>

            <div className="space-y-5">
              {processedSkills.map((skill) => (
                <div key={skill.name} className="p-4 rounded-xl bg-gray-50 dark:bg-gray-800/50">
                  <Slider
                    label={skill.name}
                    value={skill.value}
                    onChange={(value) => updateSkillValue(skill.name, value)}
                    min={0}
                    max={100}
                  />
                  <div className="flex justify-between mt-2 text-xs text-gray-400">
                    <span>Anfänger</span>
                    <span>Fortgeschritten</span>
                    <span>Experte</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </Card>
    </div>
  );
};

export default SkillsStep;
