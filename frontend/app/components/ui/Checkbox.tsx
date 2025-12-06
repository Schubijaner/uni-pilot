/**
 * Checkbox - Wiederverwendbare Checkbox-Komponente
 * Für Modul-Auswahl und andere Multi-Select Szenarien
 */

import React from 'react';

interface CheckboxProps {
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  description?: string;
  disabled?: boolean;
  className?: string;
}

export const Checkbox: React.FC<CheckboxProps> = ({
  label,
  checked,
  onChange,
  description,
  disabled = false,
  className = '',
}) => {
  return (
    <label
      className={`
        flex items-start gap-3 p-4
        rounded-xl cursor-pointer
        transition-all duration-200
        ${checked 
          ? 'bg-indigo-50 dark:bg-indigo-950/50 border-indigo-200 dark:border-indigo-800' 
          : 'bg-white/50 dark:bg-gray-800/50 border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50'
        }
        border
        ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
        ${className}
      `}
    >
      <div className="relative flex items-center justify-center mt-0.5">
        <input
          type="checkbox"
          checked={checked}
          onChange={(e) => !disabled && onChange(e.target.checked)}
          disabled={disabled}
          className="sr-only"
        />
        <div
          className={`
            w-5 h-5 rounded-md
            flex items-center justify-center
            transition-all duration-200
            ${checked
              ? 'bg-gradient-to-r from-indigo-500 to-purple-500'
              : 'bg-white dark:bg-gray-700 border-2 border-gray-300 dark:border-gray-600'
            }
          `}
        >
          {checked && (
            <svg
              className="w-3 h-3 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={3}
                d="M5 13l4 4L19 7"
              />
            </svg>
          )}
        </div>
      </div>
      <div className="flex-1">
        <span className="block text-sm font-medium text-gray-900 dark:text-white">
          {label}
        </span>
        {description && (
          <span className="block text-sm text-gray-500 dark:text-gray-400 mt-0.5">
            {description}
          </span>
        )}
      </div>
    </label>
  );
};

export default Checkbox;
