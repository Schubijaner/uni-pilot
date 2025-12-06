/**
 * Card - Wiederverwendbare Card-Komponente
 * Glassmorphism-Stil mit verschiedenen Varianten
 */

import React from 'react';

type CardVariant = 'default' | 'elevated' | 'glass' | 'bordered';

interface CardProps {
  children: React.ReactNode;
  variant?: CardVariant;
  className?: string;
  padding?: 'none' | 'sm' | 'md' | 'lg';
  onClick?: () => void;
  hoverable?: boolean;
}

const variantStyles: Record<CardVariant, string> = {
  default: `
    bg-white dark:bg-gray-800 
    border border-gray-100 dark:border-gray-700
  `,
  elevated: `
    bg-white dark:bg-gray-800 
    shadow-xl shadow-gray-200/50 dark:shadow-gray-900/50
  `,
  glass: `
    bg-white/60 dark:bg-gray-800/60 
    backdrop-blur-xl 
    border border-white/20 dark:border-gray-700/50
    shadow-xl shadow-gray-200/30 dark:shadow-gray-900/30
  `,
  bordered: `
    bg-transparent
    border-2 border-dashed border-gray-200 dark:border-gray-700
  `,
};

const paddingStyles: Record<string, string> = {
  none: '',
  sm: 'p-3',
  md: 'p-5',
  lg: 'p-8',
};

export const Card: React.FC<CardProps> = ({
  children,
  variant = 'default',
  className = '',
  padding = 'md',
  onClick,
  hoverable = false,
}) => {
  const isClickable = Boolean(onClick);

  return (
    <div
      className={`
        rounded-2xl
        transition-all duration-300
        ${variantStyles[variant]}
        ${paddingStyles[padding]}
        ${hoverable || isClickable ? 'hover:scale-[1.02] hover:shadow-2xl cursor-pointer' : ''}
        ${className}
      `}
      onClick={onClick}
      role={isClickable ? 'button' : undefined}
      tabIndex={isClickable ? 0 : undefined}
    >
      {children}
    </div>
  );
};

// Card Header Sub-Component
interface CardHeaderProps {
  children: React.ReactNode;
  className?: string;
}

export const CardHeader: React.FC<CardHeaderProps> = ({ children, className = '' }) => (
  <div className={`mb-4 ${className}`}>{children}</div>
);

// Card Title Sub-Component
interface CardTitleProps {
  children: React.ReactNode;
  className?: string;
}

export const CardTitle: React.FC<CardTitleProps> = ({ children, className = '' }) => (
  <h3 className={`text-xl font-semibold text-gray-900 dark:text-white ${className}`}>
    {children}
  </h3>
);

// Card Description Sub-Component
interface CardDescriptionProps {
  children: React.ReactNode;
  className?: string;
}

export const CardDescription: React.FC<CardDescriptionProps> = ({ children, className = '' }) => (
  <p className={`text-gray-500 dark:text-gray-400 mt-1 ${className}`}>{children}</p>
);

// Card Content Sub-Component
interface CardContentProps {
  children: React.ReactNode;
  className?: string;
}

export const CardContent: React.FC<CardContentProps> = ({ children, className = '' }) => (
  <div className={className}>{children}</div>
);

// Card Footer Sub-Component
interface CardFooterProps {
  children: React.ReactNode;
  className?: string;
}

export const CardFooter: React.FC<CardFooterProps> = ({ children, className = '' }) => (
  <div className={`mt-4 pt-4 border-t border-gray-100 dark:border-gray-700 ${className}`}>
    {children}
  </div>
);

export default Card;
