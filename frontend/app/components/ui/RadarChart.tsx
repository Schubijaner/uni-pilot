/**
 * RadarChart - SVG-basierte Radar-Chart Komponente
 * Für Skill-Vergleich in der Roadmap View
 */

import React from 'react';
import type { Skill } from '~/types';

interface RadarChartProps {
  userSkills: Skill[];
  requiredSkills: Skill[];
  size?: number;
  className?: string;
}

export const RadarChart: React.FC<RadarChartProps> = ({
  userSkills,
  requiredSkills,
  size = 300,
  className = '',
}) => {
  // Alle einzigartigen Skills kombinieren
  const allSkillNames = Array.from(
    new Set([...userSkills.map(s => s.name), ...requiredSkills.map(s => s.name)])
  );

  const numPoints = allSkillNames.length;
  const centerX = size / 2;
  const centerY = size / 2;
  const radius = (size / 2) * 0.75;

  // Berechne Punktkoordinaten für einen Wert (0-100)
  const getPoint = (index: number, value: number): { x: number; y: number } => {
    const angle = (Math.PI * 2 * index) / numPoints - Math.PI / 2;
    const r = (value / 100) * radius;
    return {
      x: centerX + r * Math.cos(angle),
      y: centerY + r * Math.sin(angle),
    };
  };

  // Erzeuge Polygon-Pfad
  const getPath = (skills: Skill[]): string => {
    const points = allSkillNames.map((name, i) => {
      const skill = skills.find(s => s.name === name);
      const value = skill?.value || 0;
      const point = getPoint(i, value);
      return `${point.x},${point.y}`;
    });
    return `M ${points.join(' L ')} Z`;
  };

  // Erzeuge Gitterlinien
  const gridLevels = [20, 40, 60, 80, 100];

  return (
    <div className={`relative ${className}`}>
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        className="mx-auto"
      >
        {/* Grid circles */}
        {gridLevels.map((level) => (
          <polygon
            key={level}
            points={allSkillNames
              .map((_, i) => {
                const point = getPoint(i, level);
                return `${point.x},${point.y}`;
              })
              .join(' ')}
            fill="none"
            stroke="currentColor"
            strokeWidth="1"
            className="text-gray-200 dark:text-gray-700"
          />
        ))}

        {/* Axis lines */}
        {allSkillNames.map((_, i) => {
          const point = getPoint(i, 100);
          return (
            <line
              key={i}
              x1={centerX}
              y1={centerY}
              x2={point.x}
              y2={point.y}
              stroke="currentColor"
              strokeWidth="1"
              className="text-gray-200 dark:text-gray-700"
            />
          );
        })}

        {/* Required Skills Polygon (Background) */}
        <path
          d={getPath(requiredSkills)}
          fill="rgba(239, 68, 68, 0.2)"
          stroke="rgb(239, 68, 68)"
          strokeWidth="2"
          className="drop-shadow-lg"
        />

        {/* User Skills Polygon (Foreground) */}
        <path
          d={getPath(userSkills)}
          fill="rgba(99, 102, 241, 0.3)"
          stroke="rgb(99, 102, 241)"
          strokeWidth="2.5"
          className="drop-shadow-lg"
        />

        {/* Skill Labels */}
        {allSkillNames.map((name, i) => {
          const point = getPoint(i, 115);
          return (
            <text
              key={name}
              x={point.x}
              y={point.y}
              textAnchor="middle"
              dominantBaseline="middle"
              className="text-xs font-medium fill-gray-600 dark:fill-gray-400"
            >
              {name}
            </text>
          );
        })}
      </svg>

      {/* Legend */}
      <div className="flex justify-center gap-6 mt-4">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-indigo-500/50 border-2 border-indigo-500" />
          <span className="text-sm text-gray-600 dark:text-gray-400">Deine Skills</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-red-500/30 border-2 border-red-500" />
          <span className="text-sm text-gray-600 dark:text-gray-400">Benötigte Skills</span>
        </div>
      </div>
    </div>
  );
};

export default RadarChart;
