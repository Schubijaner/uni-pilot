# Frontend Chat Integration mit topic_field_id

## Übersicht

Der Chat Bot funktioniert über `topic_field_id`. Diese ID verbindet:
- **Chat Sessions** - Gespräche mit dem Bot
- **Roadmaps** - Lernpfade
- **Jobs** - Karriereziele

## API Endpoints

### 1. Chat Session erstellen/abrufen

```http
POST /api/v1/topic-fields/{topic_field_id}/chat/sessions
Authorization: Bearer {token}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 42,
  "topic_field_id": 6,
  "career_tree_node_id": null,
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z",
  "message_count": 0,
  "topic_field": {
    "id": 6,
    "name": "Full Stack Development",
    "description": "...",
    "system_prompt": "Du bist ein Experte für...",
    "created_at": "2024-01-15T09:00:00Z"
  },
  "job": null
}
```

**Wichtig:**
- Wenn für diesen User + `topic_field_id` bereits eine Session existiert, wird die existierende zurückgegeben
- Andernfalls wird eine neue Session erstellt

### 2. Nachrichten abrufen

```http
GET /api/v1/chat/sessions/{session_id}/messages?limit=100&offset=0
Authorization: Bearer {token}
```

**Response:**
```json
[
  {
    "id": 1,
    "session_id": 1,
    "role": "user",
    "content": "Welche Skills brauche ich?",
    "created_at": "2024-01-15T10:01:00Z"
  },
  {
    "id": 2,
    "session_id": 1,
    "role": "assistant",
    "content": "Für Full Stack Development empfehle ich...",
    "created_at": "2024-01-15T10:01:02Z"
  }
]
```

### 3. Nachricht senden

```http
POST /api/v1/chat/sessions/{session_id}/messages
Authorization: Bearer {token}
Content-Type: application/json

{
  "content": "Welche Module sollte ich belegen?"
}
```

**Response:**
```json
{
  "user_message": {
    "id": 3,
    "session_id": 1,
    "role": "user",
    "content": "Welche Module sollte ich belegen?",
    "created_at": "2024-01-15T10:02:00Z"
  },
  "assistant_message": {
    "id": 4,
    "session_id": 1,
    "role": "assistant",
    "content": "Basierend auf deinem Studienprogramm empfehle ich...",
    "created_at": "2024-01-15T10:02:02Z"
  }
}
```

### 4. Alle Sessions des Users abrufen

```http
GET /api/v1/users/me/chat/sessions?topic_field_id=6&limit=100&offset=0
Authorization: Bearer {token}
```

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 42,
    "topic_field_id": 6,
    "career_tree_node_id": null,
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-01-15T10:02:00Z",
    "message_count": 2,
    "topic_field": {
      "id": 6,
      "name": "Full Stack Development",
      ...
    },
    "job": null
  }
]
```

## Frontend Integration - TypeScript

### TypeScript Interfaces

```typescript
interface ChatSession {
  id: number;
  user_id: number;
  topic_field_id: number | null;
  career_tree_node_id: number | null;
  created_at: string;
  updated_at: string;
  message_count: number;
  topic_field?: {
    id: number;
    name: string;
    description: string;
    system_prompt: string;
    created_at: string;
  };
  job?: CareerTreeNode;
}

interface ChatMessage {
  id: number;
  session_id: number;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

interface SendMessageResponse {
  user_message: ChatMessage;
  assistant_message: ChatMessage;
}
```

### API Funktionen

```typescript
const baseUrl = 'http://localhost:8000/api/v1';

// 1. Chat Session erstellen/abrufen
export async function createChatSession(
  topicFieldId: number,
  token: string
): Promise<ChatSession> {
  const response = await fetch(`${baseUrl}/topic-fields/${topicFieldId}/chat/sessions`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to create chat session: ${response.statusText}`);
  }

  return await response.json();
}

// 2. Nachrichten abrufen
export async function getChatMessages(
  sessionId: number,
  token: string,
  limit: number = 100,
  offset: number = 0
): Promise<ChatMessage[]> {
  const response = await fetch(
    `${baseUrl}/chat/sessions/${sessionId}/messages?limit=${limit}&offset=${offset}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to get messages: ${response.statusText}`);
  }

  return await response.json();
}

// 3. Nachricht senden
export async function sendChatMessage(
  sessionId: number,
  content: string,
  token: string
): Promise<SendMessageResponse> {
  const response = await fetch(`${baseUrl}/chat/sessions/${sessionId}/messages`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ content }),
  });

  if (!response.ok) {
    throw new Error(`Failed to send message: ${response.statusText}`);
  }

  return await response.json();
}

// 4. Alle Sessions abrufen
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
  
  if (topicFieldId) {
    params.append('topic_field_id', topicFieldId.toString());
  }

  const response = await fetch(`${baseUrl}/users/me/chat/sessions?${params}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to get chat sessions: ${response.statusText}`);
  }

  return await response.json();
}
```

## Beispiel-Workflow

### Szenario: User wählt Job und startet Chat

```typescript
// 1. User wählt Job aus Career Tree
const jobId = 11;
const job = await getJobFromTree(jobId);

// 2. Job hat topic_field_id
const topicFieldId = job.topic_field_id; // z.B. 6

// 3. Chat Session erstellen/abrufen
const session = await createChatSession(topicFieldId, token);
console.log(`Chat Session ID: ${session.id}`);

// 4. Vorhandene Nachrichten laden
const existingMessages = await getChatMessages(session.id, token);
console.log(`Vorhandene Nachrichten: ${existingMessages.length}`);

// 5. Neue Nachricht senden
const response = await sendChatMessage(
  session.id,
  "Welche Module sollte ich belegen?",
  token
);

console.log('User:', response.user_message.content);
console.log('Bot:', response.assistant_message.content);

// 6. Alle Nachrichten erneut abrufen (inkl. neue)
const allMessages = await getChatMessages(session.id, token);
```

### Szenario: Chat mit Roadmap verknüpfen

```typescript
// Chat Session und Roadmap verwenden die gleiche topic_field_id!

// 1. Chat Session erstellen
const session = await createChatSession(topicFieldId, token);

// 2. Roadmap abrufen (verwendet gleiche topic_field_id)
const roadmap = await getRoadmap(topicFieldId, token);

// 3. Beide gehören zusammen!
console.log(session.topic_field_id === roadmap.topic_field_id); // true

// 4. User kann im Chat über die Roadmap fragen
await sendChatMessage(
  session.id,
  `Welche Module aus meiner Roadmap sollte ich zuerst belegen?`,
  token
);
```

## React Component Beispiel

```typescript
import { useState, useEffect } from 'react';
import { createChatSession, getChatMessages, sendChatMessage } from '~/api/chat';

interface ChatComponentProps {
  topicFieldId: number;
  token: string;
}

export function ChatComponent({ topicFieldId, token }: ChatComponentProps) {
  const [session, setSession] = useState<ChatSession | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  // Session erstellen beim Mount
  useEffect(() => {
    async function initChat() {
      const newSession = await createChatSession(topicFieldId, token);
      setSession(newSession);
      
      const existingMessages = await getChatMessages(newSession.id, token);
      setMessages(existingMessages);
    }
    
    initChat();
  }, [topicFieldId, token]);

  // Nachricht senden
  async function handleSend() {
    if (!session || !input.trim()) return;

    setLoading(true);
    try {
      const response = await sendChatMessage(session.id, input, token);
      
      // Neue Nachrichten zur Liste hinzufügen
      setMessages(prev => [
        ...prev,
        response.user_message,
        response.assistant_message,
      ]);
      
      setInput('');
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setLoading(false);
    }
  }

  if (!session) {
    return <div>Lade Chat...</div>;
  }

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map(msg => (
          <div key={msg.id} className={`message ${msg.role}`}>
            <div className="role">{msg.role === 'user' ? 'Du' : 'Bot'}</div>
            <div className="content">{msg.content}</div>
            <div className="time">{new Date(msg.created_at).toLocaleTimeString()}</div>
          </div>
        ))}
      </div>
      
      <div className="input-area">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Nachricht eingeben..."
          disabled={loading}
        />
        <button onClick={handleSend} disabled={loading || !input.trim()}>
          {loading ? 'Sende...' : 'Senden'}
        </button>
      </div>
    </div>
  );
}
```

## Wichtige Punkte

1. **topic_field_id ist zentral**: Alle Funktionen basieren auf dieser ID
2. **Sessions werden automatisch wiederverwendet**: Gleiche `topic_field_id` = gleiche Session
3. **Chat-Historie bleibt erhalten**: Alle Nachrichten werden in der Datenbank gespeichert
4. **Verknüpfung mit Roadmap**: Gleiche `topic_field_id` verbindet Chat und Roadmap
5. **System Prompt**: Jedes TopicField hat einen `system_prompt`, der den Bot-Kontext bestimmt

## Unterschied: Job vs. TopicField

### Über Job-ID (Convenience)
```typescript
// POST /api/v1/jobs/{job_id}/chat/sessions
// → Backend holt automatisch job.topic_field_id
// → Erstellt Session mit job.topic_field_id
```

### Über TopicField-ID (Direkt)
```typescript
// POST /api/v1/topic-fields/{topic_field_id}/chat/sessions
// → Direkte Verwendung der topic_field_id
// → Funktioniert auch ohne Job-Kontext
```

**Empfehlung**: Nutze `topic_field_id` direkt, wenn du sie bereits hast (z.B. von einer Roadmap oder einem Job).

