/**
 * SemesterAccordion - Accordion für Semester-ToDos
 */

import React from 'react';
import type { SemesterPlan } from '~/types';
import { AccordionItem } from '~/components/ui';
import { TodoItem } from './TodoItem';

interface SemesterAccordionProps {
  semesterPlan: SemesterPlan;
  onTodoToggle: (todoId: string) => void;
  defaultOpen?: boolean;
}

export const SemesterAccordion: React.FC<SemesterAccordionProps> = ({
  semesterPlan,
  onTodoToggle,
  defaultOpen = false,
}) => {
  const completedCount = semesterPlan.todos.filter((t) => t.completed).length;
  const totalCount = semesterPlan.todos.length;
  const progressPercent = totalCount > 0 ? (completedCount / totalCount) * 100 : 0;

  return (
    <AccordionItem
      title={semesterPlan.title}
      badge={`${completedCount}/${totalCount}`}
      defaultOpen={defaultOpen}
    >
      {/* Progress Bar */}
      <div className="mb-4">
        <div className="flex items-center justify-between text-sm mb-2">
          <span className="text-gray-500 dark:text-gray-400">Fortschritt</span>
          <span className="font-medium text-gray-700 dark:text-gray-300">
            {Math.round(progressPercent)}%
          </span>
        </div>
        <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full transition-all duration-500"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </div>

      {/* ToDo List */}
      <div className="space-y-2">
        {semesterPlan.todos.map((todo) => (
          <TodoItem
            key={todo.id}
            todo={todo}
            onToggle={() => onTodoToggle(todo.id)}
          />
        ))}
      </div>
    </AccordionItem>
  );
};

export default SemesterAccordion;
