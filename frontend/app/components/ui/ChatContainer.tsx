/**
 * ChatContainer - Main chat container component
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import {
  createOrGetJobChatSession,
  getChatMessages,
  sendChatMessage,
  type ChatMessage as ChatMessageType,
  type ChatSession,
} from '~/api/chat';

interface ChatContainerProps {
  topicFieldId: number;
  topicFieldName: string;
  topicFieldDescription: string;
  token: string;
  onClose?: () => void;
}

export const ChatContainer: React.FC<ChatContainerProps> = ({
  topicFieldId,
  topicFieldName,
  topicFieldDescription,
  token,
  onClose,
}) => {
  const [session, setSession] = useState<ChatSession | null>(null);
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom when messages change
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Initialize chat session
  useEffect(() => {
    const initSession = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const chatSession = await createOrGetJobChatSession(topicFieldId, token);
        setSession(chatSession);

        // Load existing messages
        const existingMessages = await getChatMessages(chatSession.id, token);
        setMessages(existingMessages);
      } catch (err) {
        console.error('Failed to initialize chat session:', err);
        setError('Chat konnte nicht geladen werden');
      } finally {
        setIsLoading(false);
      }
    };

    initSession();
  }, [topicFieldId, token]);

  // Handle sending message
  const handleSendMessage = useCallback(
    async (content: string) => {
      if (!session || isSending) return;

      setIsSending(true);
      setError(null);

      // Optimistically add user message
      const tempUserMessage: ChatMessageType = {
        id: Date.now(),
        session_id: session.id,
        role: 'user',
        content,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, tempUserMessage]);

      try {
        const response = await sendChatMessage(session.id, content, token);
        
        // Replace temp message with real one and add assistant response
        setMessages((prev) => [
          ...prev.filter((m) => m.id !== tempUserMessage.id),
          response.user_message,
          response.assistant_message,
        ]);
      } catch (err) {
        console.error('Failed to send message:', err);
        setError('Nachricht konnte nicht gesendet werden');
        // Remove optimistic message on error
        setMessages((prev) => prev.filter((m) => m.id !== tempUserMessage.id));
      } finally {
        setIsSending(false);
      }
    },
    [session, token, isSending]
  );

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex justify-between items-start gap-4 pb-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex-1 min-w-0">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white truncate">
            {topicFieldName}
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">
            {topicFieldDescription}
          </p>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 
                       flex-shrink-0 p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700
                       transition-colors duration-200"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        )}
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto py-4 min-h-0">
        {isLoading ? (
          <div className="flex items-center justify-center h-full">
            <div className="flex flex-col items-center gap-3">
              <div className="animate-spin rounded-full h-8 w-8 border-2 border-indigo-600 border-t-transparent" />
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Chat wird geladen...
              </p>
            </div>
          </div>
        ) : error && messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="text-red-500 mb-2">
                <svg
                  className="w-12 h-12 mx-auto"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
              </div>
              <p className="text-gray-600 dark:text-gray-400">{error}</p>
            </div>
          </div>
        ) : messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center max-w-sm">
              <div className="text-indigo-500 mb-4">
                <svg
                  className="w-16 h-16 mx-auto"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                  />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                Starte eine Konversation
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Stelle Fragen zu "{topicFieldName}" und erhalte hilfreiche Antworten.
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-1">
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            {isSending && (
              <div className="flex justify-start mb-4">
                <div className="bg-gray-100 dark:bg-gray-700 rounded-2xl rounded-bl-md px-4 py-3">
                  <div className="flex items-center gap-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Error Toast */}
      {error && messages.length > 0 && (
        <div className="py-2">
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 
                          rounded-lg px-3 py-2 text-sm text-red-600 dark:text-red-400">
            {error}
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
        <ChatInput
          onSend={handleSendMessage}
          disabled={isLoading || isSending || !session}
          placeholder={`Frage zu "${topicFieldName}" stellen...`}
        />
      </div>
    </div>
  );
};

export default ChatContainer;