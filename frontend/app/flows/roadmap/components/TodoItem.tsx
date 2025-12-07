/**
 * TodoItem - Einzelnes ToDo-Element für die Roadmap
 */

import React from 'react';
import type { RoadmapTodo, TodoType } from '~/types';
import { cleanDescription } from '~/utils/parseSkillData';

interface TodoItemProps {
  todo: RoadmapTodo;
  onToggle: () => void;
}

// ...existing code...

const typeConfig: Record<TodoType, { icon: string; color: string; bg: string }> = {
  module: {
    icon: '📚',
    color: 'text-blue-600 dark:text-blue-400',
    bg: 'bg-blue-100 dark:bg-blue-900/30',
  },
  course: {
    icon: '🎓',
    color: 'text-cyan-600 dark:text-cyan-400',
    bg: 'bg-cyan-100 dark:bg-cyan-900/30',
  },
  project: {
    icon: '🚀',
    color: 'text-purple-600 dark:text-purple-400',
    bg: 'bg-purple-100 dark:bg-purple-900/30',
  },
  skill: {
    icon: '⚡',
    color: 'text-pink-600 dark:text-pink-400',
    bg: 'bg-pink-100 dark:bg-pink-900/30',
  },
  book: {
    icon: '📖',
    color: 'text-orange-600 dark:text-orange-400',
    bg: 'bg-orange-100 dark:bg-orange-900/30',
  },
  certificate: {
    icon: '🏆',
    color: 'text-amber-600 dark:text-amber-400',
    bg: 'bg-amber-100 dark:bg-amber-900/30',
  },
  internship: {
    icon: '💼',
    color: 'text-green-600 dark:text-green-400',
    bg: 'bg-green-100 dark:bg-green-900/30',
  },
  bootcamp: {
    icon: '🏕️',
    color: 'text-red-600 dark:text-red-400',
    bg: 'bg-red-100 dark:bg-red-900/30',
  },
  career: {
    icon: '🎯',
    color: 'text-indigo-600 dark:text-indigo-400',
    bg: 'bg-indigo-100 dark:bg-indigo-900/30',
  },
};

const typeLabels: Record<TodoType, string> = {
  module: 'Modul',
  course: 'Kurs',
  project: 'Projekt',
  skill: 'Skill',
  book: 'Buch',
  certificate: 'Zertifikat',
  internship: 'Praktikum',
  bootcamp: 'Bootcamp',
  career: 'Karriere',
};

export const TodoItem: React.FC<TodoItemProps> = ({ todo, onToggle }) => {
  const config = typeConfig[todo.type];

  return (
    <div
      className={`
        flex items-start gap-4 p-4 rounded-xl
        transition-all duration-200
        ${todo.completed
          ? 'bg-gray-50 dark:bg-gray-800/30 opacity-60'
          : 'bg-white dark:bg-gray-800/50 hover:bg-gray-50 dark:hover:bg-gray-700/50'
        }
      `}
    >
      {/* Checkbox */}
      <button
        onClick={onToggle}
        className={`
          mt-0.5 w-6 h-6 rounded-lg flex-shrink-0
          flex items-center justify-center
          transition-all duration-200
          ${todo.completed
            ? 'bg-gradient-to-r from-green-500 to-emerald-500'
            : 'border-2 border-gray-300 dark:border-gray-600 hover:border-indigo-400'
          }
        `}
      >
        {todo.completed && (
          <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
          </svg>
        )}
      </button>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${config.bg} ${config.color}`}>
            {config.icon} {typeLabels[todo.type]}
          </span>
        </div>
        <h4
          className={`
            font-medium
            ${todo.completed
              ? 'text-gray-400 dark:text-gray-500 line-through'
              : 'text-gray-900 dark:text-white'
            }
          `}
        >
          {todo.title}
        </h4>
        {todo.description && (
          <p
            className={`
              text-sm mt-1
              ${todo.completed
                ? 'text-gray-400 dark:text-gray-600'
                : 'text-gray-500 dark:text-gray-400'
              }
            `}
          >
            {cleanDescription(todo.description)}
          </p>
        )}
        {todo.skill_impact && todo.skill_impact.length > 0 && (
          <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-1 mb-1">
              <svg className="w-4 h-4 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
              <span className="text-xs font-medium text-indigo-600 dark:text-indigo-400">
                Skill-Impact:
              </span>
            </div>
            <div className="flex flex-wrap gap-2">
              {todo.skill_impact.map((impact, index) => (
                <span
                  key={index}
                  className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-indigo-50 dark:bg-indigo-900/20 text-xs text-indigo-700 dark:text-indigo-300"
                >
                  <span className="font-medium">{impact.skill}</span>
                  <span className="text-indigo-500">+{impact.impact}%</span>
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TodoItem;
