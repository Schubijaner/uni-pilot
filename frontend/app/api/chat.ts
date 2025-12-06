import baseUrl from "./baseUrl";

/**
 * Chat API functions
 */
export interface TopicField {
  id: number;
  name: string;
  description: string;
  system_prompt: string;
  created_at: string;
}

export interface Job {
  id: number;
  name: string;
  description: string;
  is_leaf: boolean;
  level: number;
  topic_field_id: number;
  topic_field: TopicField;
  questions: string[];
  children: Job[];
}

export interface ChatSession {
  id: number;
  user_id: number;
  topic_field_id: number;
  career_tree_node_id: number;
  created_at: string;
  updated_at: string;
  topic_field: TopicField;
  job: Job;
  message_count: number;
}

export interface ChatMessage {
  id: number;
  session_id: number;
  role: string;
  content: string;
  created_at: string;
}

export interface SendMessageResponse {
  user_message: ChatMessage;
  assistant_message: ChatMessage;
}

/**
 * Create or get a chat session for a job
 */
export async function createOrGetJobChatSession(
  jobId: number,
  token: string
): Promise<ChatSession> {
    console.log("createOrGetJobChatSession called with jobId:", jobId);
  const response = await fetch(
    `${baseUrl}/api/v1/jobs/${jobId}/chat/sessions`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to create/get chat session: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get chat messages for a session
 */
export async function getChatMessages(
  sessionId: number,
  token: string,
  limit: number = 100,
  offset: number = 0
): Promise<ChatMessage[]> {
  const params = new URLSearchParams({
    limit: limit.toString(),
    offset: offset.toString(),
  });

  const response = await fetch(
    `${baseUrl}/api/v1/chat/sessions/${sessionId}/messages?${params}`,
    {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to get chat messages: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Send a message in a chat session
 */
export async function sendChatMessage(
  sessionId: number,
  content: string,
  token: string
): Promise<SendMessageResponse> {
  const response = await fetch(
    `${baseUrl}/api/v1/chat/sessions/${sessionId}/messages`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ content }),
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to send message: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get all chat sessions for the current user
 */
export async function getUserChatSessions(
  token: string,
  topicFieldId?: number,
  limit: number = 100,
  offset: number = 0
): Promise<ChatSession[]> {
  const params = new URLSearchParams({
    limit: limit.toString(),
    offset: offset.toString(),
  });

  if (topicFieldId !== undefined) {
    params.append('topic_field_id', topicFieldId.toString());
  }

  const response = await fetch(
    `${baseUrl}/api/v1/users/me/chat/sessions?${params}`,
    {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to get user chat sessions: ${response.statusText}`);
  }

  return response.json();
}