/**
 * ProgressSteps - Komponente zur Anzeige des Onboarding-Fortschritts
 */

import React from 'react';

interface Step {
  id: string;
  label: string;
}

interface ProgressStepsProps {
  steps: Step[];
  currentStep: number;
  className?: string;
}

export const ProgressSteps: React.FC<ProgressStepsProps> = ({
  steps,
  currentStep,
  className = '',
}) => {
  return (
    <div className={`w-full ${className}`}>
      {/* Mobile: Simple dots */}
      <div className="flex justify-center gap-2 md:hidden">
        {steps.map((_, index) => (
          <div
            key={index}
            className={`
              w-2.5 h-2.5 rounded-full transition-all duration-300
              ${index < currentStep
                ? 'bg-indigo-500'
                : index === currentStep
                  ? 'bg-indigo-500 ring-4 ring-indigo-200 dark:ring-indigo-900'
                  : 'bg-gray-300 dark:bg-gray-600'
              }
            `}
          />
        ))}
      </div>

      {/* Desktop: Full progress bar */}
      <div className="hidden md:flex items-start justify-between">
        {steps.map((step, index) => (
          <React.Fragment key={step.id}>
            <div className="flex flex-col items-center gap-2">
              <div
                className={`
                  w-10 h-10 rounded-full
                  flex items-center justify-center
                  font-semibold text-sm
                  transition-all duration-300
                  ${index < currentStep
                    ? 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white'
                    : index === currentStep
                      ? 'bg-white dark:bg-gray-800 border-2 border-indigo-500 text-indigo-600 dark:text-indigo-400'
                      : 'bg-gray-100 dark:bg-gray-800 text-gray-400 dark:text-gray-500'
                  }
                `}
              >
                {index < currentStep ? (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  index + 1
                )}
              </div>
              <span
                className={`
                  text-xs font-medium
                  ${index <= currentStep
                    ? 'text-gray-900 dark:text-white'
                    : 'text-gray-400 dark:text-gray-500'
                  }
                `}
              >
                {step.label}
              </span>
            </div>
            {index < steps.length - 1 && (
              <div
                className={`
                  flex-1 h-0.5 mx-4 mt-5
                  ${index < currentStep
                    ? 'bg-gradient-to-r from-indigo-500 to-purple-500'
                    : 'bg-gray-200 dark:bg-gray-700'
                  }
                `}
              />
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
};

export default ProgressSteps;
