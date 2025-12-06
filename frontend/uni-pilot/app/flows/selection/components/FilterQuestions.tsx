/**
 * FilterQuestions - Schrittweise Fragen-Navigation
 * Filtert die sichtbaren Jobs basierend auf Antworten
 */

import React from 'react';
import type { FilterQuestion, FilterOption } from '~/types';
import { Button, Card } from '~/components/ui';

interface FilterQuestionsProps {
  questions: FilterQuestion[];
  currentQuestionIndex: number;
  selectedOptions: Record<string, boolean>;
  onOptionSelect: (questionId: string, optionId: "true" | "false") => void;
  onPrev: () => void;
  onNext: () => void;
  canGoNext: boolean;
  canGoPrev: boolean;
}

export const FilterQuestions: React.FC<FilterQuestionsProps> = ({
  questions,
  currentQuestionIndex,
  selectedOptions,
  onOptionSelect,
  onPrev,
  onNext,
  canGoNext,
  canGoPrev,
}) => {
  const currentQuestion = questions[currentQuestionIndex];

  if (!currentQuestion) {
    return null;
  }

  const selectedOptionId = selectedOptions[currentQuestion.id];

  return (
    <Card variant="glass" className="h-full">
      {/* Progress */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex gap-1.5">
          {questions.map((_, idx) => (
            <div
              key={idx}
              className={`
                w-8 h-1.5 rounded-full transition-all duration-300
                ${idx < currentQuestionIndex
                  ? 'bg-indigo-500'
                  : idx === currentQuestionIndex
                    ? 'bg-indigo-400'
                    : 'bg-gray-200 dark:bg-gray-700'
                }
              `}
            />
          ))}
        </div>
      </div>

      {/* Question */}
      <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">
        {currentQuestion.question_text}
      </h3>

      {/* Options */}
      <div className="space-y-3 mb-8">
        <OptionButton
            option="Zustimmen"
            isSelected={selectedOptionId}
            onSelect={() => onOptionSelect(currentQuestion.id, "true")}
          />
          <OptionButton
            option="Ablehnen"
            isSelected={selectedOptionId === false}
            onSelect={() => onOptionSelect(currentQuestion.id, "false")}
          />
      </div>

      {/* Navigation */}
      <div className="flex items-center justify-between pt-4 border-t border-gray-100 dark:border-gray-700">
        <Button
          variant="ghost"
          onClick={onPrev}
          disabled={!canGoPrev}
          leftIcon={
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          }
        >
          Zurück
        </Button>
        <Button
          onClick={onNext}
          disabled={!canGoNext || selectedOptionId === undefined}
          rightIcon={
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          }
        >
          {currentQuestionIndex === questions.length - 1 ? 'Fertig' : 'Weiter'}
        </Button>
      </div>
    </Card>
  );
};

// Option Button Component
interface OptionButtonProps {
  option: string;
  isSelected: boolean;
  onSelect: () => void;
}

const OptionButton: React.FC<OptionButtonProps> = ({
  option,
  isSelected,
  onSelect,
}) => {
  return (
    <button
      onClick={onSelect}
      className={`
        w-full px-5 py-4 rounded-xl
        flex items-center justify-between
        transition-all duration-200
        text-left
        ${isSelected
          ? 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white shadow-lg shadow-indigo-500/30'
          : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:border-indigo-300 dark:hover:border-indigo-600 text-gray-900 dark:text-white'
        }
      `}
    >
      <span className="font-medium">{option}</span>
      <div
        className={`
          w-5 h-5 rounded-full flex items-center justify-center
          ${isSelected
            ? 'bg-white/20'
            : 'border-2 border-gray-300 dark:border-gray-600'
          }
        `}
      >
        {isSelected && (
          <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
          </svg>
        )}
      </div>
    </button>
  );
};

export default FilterQuestions;
