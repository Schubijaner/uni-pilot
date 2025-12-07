import React, { useState, useEffect } from 'react';

interface LoadingModalProps {
  isOpen: boolean;
  title?: string;
  messages?: string[];
  tips?: string[];
  estimatedDurationMs?: number;
}

// Default estimated duration in milliseconds (30 seconds)
const DEFAULT_ESTIMATED_DURATION_MS = 45000;

const defaultMessages = [
  'Analysiere deine Interessen...',
  'Erstelle deinen persönlichen Karriereweg...',
  'Optimiere die Lernpfade...',
  'Bereite deine Roadmap vor...',
];

const defaultTips = [
  '💡 Wusstest du? Die meisten erfolgreichen Karrierewechsel dauern 2-5 Jahre.',
  '🎯 Tipp: Kleine, konsistente Schritte führen zum Erfolg.',
  '📚 Fun Fact: Lebenslanges Lernen steigert die Karrierechancen um 30%.',
  '🚀 Motivation: Jede Reise beginnt mit dem ersten Schritt!',
  '⭐ Wusstest du? Mentoren können deine Karriere beschleunigen.',
];

export const LoadingModal: React.FC<LoadingModalProps> = ({
  isOpen,
  title = 'Deine Roadmap wird erstellt',
  messages = defaultMessages,
  tips = defaultTips,
  estimatedDurationMs = DEFAULT_ESTIMATED_DURATION_MS,
}) => {
  const [currentMessageIndex, setCurrentMessageIndex] = useState(0);
  const [currentTip, setCurrentTip] = useState(tips[0]);
  const [progress, setProgress] = useState(0);

  // Calculate intervals based on estimated duration
  const messageInterval = estimatedDurationMs / messages.length;
  const tipInterval = Math.max(estimatedDurationMs / 3, 5000);
  const progressUpdateInterval = estimatedDurationMs / 20;

  useEffect(() => {
    if (!isOpen) {
      setCurrentMessageIndex(0);
      setProgress(0);
      return;
    }

    // Cycle through messages
    const messageTimer = setInterval(() => {
      setCurrentMessageIndex((prev) => (prev + 1) % messages.length);
    }, messageInterval);

    // Rotate tips
    const tipTimer = setInterval(() => {
      setCurrentTip(tips[Math.floor(Math.random() * tips.length)]);
    }, tipInterval);

    // Progress animation - reach ~90% by estimated duration
    const progressTimer = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 90) return prev;
        const increment = 90 / (estimatedDurationMs / progressUpdateInterval);
        return Math.min(prev + increment, 90);
      });
    }, progressUpdateInterval);

    return () => {
      clearInterval(messageTimer);
      clearInterval(tipTimer);
      clearInterval(progressTimer);
    };
  }, [isOpen, messages, tips, messageInterval, tipInterval, progressUpdateInterval, estimatedDurationMs]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" />

      {/* Modal */}
      <div className="relative z-10 w-full max-w-md mx-4">
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden">
          {/* Header with gradient */}
          <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-6 py-4">
            <h2 className="text-xl font-bold text-white text-center">
              {title}
            </h2>
          </div>

          {/* Content */}
          <div className="p-6">
            {/* Animated Icon */}
            <div className="flex justify-center mb-6">
              <div className="relative">
                {/* Outer spinning ring */}
                <div className="w-20 h-20 rounded-full border-4 border-indigo-100 dark:border-indigo-900 animate-pulse" />
                <div className="absolute inset-0 w-20 h-20 rounded-full border-4 border-transparent border-t-indigo-600 animate-spin" />
                
                {/* Center icon */}
                <div className="absolute inset-0 flex items-center justify-center">
                  <svg
                    className="w-8 h-8 text-indigo-600 dark:text-indigo-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"
                    />
                  </svg>
                </div>
              </div>
            </div>

            {/* Progress bar */}
            <div className="mb-4">
              <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-indigo-600 to-purple-600 rounded-full transition-all duration-500 ease-out"
                  style={{ width: `${Math.min(progress, 95)}%` }}
                />
              </div>
            </div>

            {/* Current status message */}
            <p className="text-center text-gray-700 dark:text-gray-300 font-medium mb-6 min-h-[1.5rem] transition-opacity duration-300">
              {messages[currentMessageIndex]}
            </p>

            {/* Divider */}
            <div className="border-t border-gray-200 dark:border-gray-700 my-4" />

            {/* Tip section */}
            <div className="bg-indigo-50 dark:bg-indigo-900/30 rounded-xl p-4">
              <p className="text-sm text-indigo-700 dark:text-indigo-300 text-center transition-opacity duration-500">
                {currentTip}
              </p>
            </div>

            {/* Fun waiting message */}
            <p className="text-center text-xs text-gray-400 dark:text-gray-500 mt-4">
              Gute Dinge brauchen Zeit... ☕
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoadingModal;