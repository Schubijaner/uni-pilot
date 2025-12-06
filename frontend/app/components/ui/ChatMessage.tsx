/**
 * ChatMessage - Individual chat message component
 */

import React from 'react';
import type { ChatMessage as ChatMessageType } from '~/api/chat';

interface ChatMessageProps {
  message: ChatMessageType;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}
    >
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-indigo-600 text-white rounded-br-md'
            : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white rounded-bl-md'
        }`}
      >
        <p className="text-sm whitespace-pre-wrap break-words">{message.content}</p>
        <span
          className={`text-xs mt-1 block ${
            isUser ? 'text-indigo-200' : 'text-gray-500 dark:text-gray-400'
          }`}
        >
          {new Date(message.created_at).toLocaleTimeString('de-DE', {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </span>
      </div>
    </div>
  );
};

export default ChatMessage;