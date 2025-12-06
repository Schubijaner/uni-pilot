/**
 * Layout-Komponente - Wiederverwendbares Hauptlayout
 * Unterstützt verschiedene Layout-Varianten und Dark Mode
 */

import React from 'react';

interface LayoutProps {
  children: React.ReactNode;
  variant?: 'default' | 'centered' | 'sidebar';
  className?: string;
  showGradient?: boolean;
}

export const Layout: React.FC<LayoutProps> = ({
  children,
  variant = 'default',
  className = '',
  showGradient = true,
}) => {
  return (
    <div className={`min-h-screen bg-gray-50 dark:bg-gray-950 ${className}`}>
      {/* Gradient Background */}
      {showGradient && (
        <div className="fixed inset-0 -z-10 overflow-hidden">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-300 dark:bg-purple-900/30 rounded-full mix-blend-multiply dark:mix-blend-normal filter blur-3xl opacity-70 animate-blob" />
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-indigo-300 dark:bg-indigo-900/30 rounded-full mix-blend-multiply dark:mix-blend-normal filter blur-3xl opacity-70 animate-blob animation-delay-2000" />
          <div className="absolute top-1/2 left-1/2 w-80 h-80 bg-pink-300 dark:bg-pink-900/30 rounded-full mix-blend-multiply dark:mix-blend-normal filter blur-3xl opacity-70 animate-blob animation-delay-4000" />
        </div>
      )}

      {variant === 'centered' ? (
        <div className="flex items-center justify-center min-h-screen p-4">
          {children}
        </div>
      ) : variant === 'sidebar' ? (
        <div className="flex min-h-screen">
          {children}
        </div>
      ) : (
        <div className="container mx-auto px-4 py-8 max-w-6xl">
          {children}
        </div>
      )}
    </div>
  );
};

export default Layout;
