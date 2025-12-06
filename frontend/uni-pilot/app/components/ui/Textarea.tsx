/**
 * Textarea - Wiederverwendbare Textarea-Komponente
 * Unterstützt Labels, Fehleranzeige und automatische Höhenanpassung
 */

import React, { forwardRef } from 'react';

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ label, error, helperText, className = '', id, ...props }, ref) => {
    const textareaId = id || `textarea-${Math.random().toString(36).substr(2, 9)}`;
    const hasError = Boolean(error);

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={textareaId}
            className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
          >
            {label}
          </label>
        )}
        <textarea
          ref={ref}
          id={textareaId}
          className={`
            w-full px-4 py-3 
            bg-white/80 dark:bg-gray-800/80 
            border rounded-xl
            text-gray-900 dark:text-white
            placeholder:text-gray-400 dark:placeholder:text-gray-500
            backdrop-blur-sm
            transition-all duration-200
            focus:outline-none focus:ring-2 focus:ring-offset-2
            dark:focus:ring-offset-gray-900
            resize-none
            min-h-[120px]
            ${hasError
              ? 'border-red-300 dark:border-red-500 focus:ring-red-500/50 focus:border-red-500'
              : 'border-gray-200 dark:border-gray-700 focus:ring-indigo-500/50 focus:border-indigo-500'
            }
            ${className}
          `}
          {...props}
        />
        {(error || helperText) && (
          <p
            className={`mt-2 text-sm ${
              hasError ? 'text-red-500 dark:text-red-400' : 'text-gray-500 dark:text-gray-400'
            }`}
          >
            {error || helperText}
          </p>
        )}
      </div>
    );
  }
);

Textarea.displayName = 'Textarea';

export default Textarea;
