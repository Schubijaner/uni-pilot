# Frontend - Chat Sessions mit Jobs verknüpfen

## Übersicht

Chat Sessions und Roadmaps für Jobs werden über `topic_field_id` verknüpft. Jeder Job hat eine eindeutige `topic_field_id`, die automatisch verwendet wird.

## Backend Endpoints

### Chat Session für Job erstellen

**Endpoint**: `POST /api/v1/jobs/{job_id}/chat/sessions`

**Response**:
```json
{
  "id": 1,
  "user_id": 1,
  "topic_field_id": 6,          // ← Verbindet Chat mit Roadmap
  "career_tree_node_id": 11,    // ← Job ID
  "job": {
    "id": 11,
    "name": "Research Scientist - Network Flow",
    "topic_field_id": 6
  },
  "message_count": 0
}
```

### Roadmap für Job abrufen

**Endpoint**: `GET /api/v1/jobs/{job_id}/roadmap`

**Response**:
```json
{
  "id": 1,
  "topic_field_id": 6,  // ← Gleiche topic_field_id wie Chat Session
  "name": "Roadmap für Research Scientist - Network Flow",
  ...
}
```

## Frontend Implementation

### Schritt 1: Chat Session für Job erstellen

```typescript
// frontend/app/api/createChatSession.ts

import baseUrl from './baseUrl';

interface ChatSessionResponse {
  id: number;
  user_id: number;
  topic_field_id: number | null;
  career_tree_node_id: number | null;
  job?: {
    id: number;
    name: string;
    topic_field_id: number;
  };
  message_count: number;
}

export async function createChatSessionForJob(
  jobId: number,
  token: string
): Promise<ChatSessionResponse> {
  const response = await fetch(`${baseUrl}/jobs/${jobId}/chat/sessions`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to create chat session: ${response.statusText}`);
  }

  return response.json();
}
```

### Schritt 2: Roadmap für Job abrufen

```typescript
// frontend/app/api/getRoadmapForJob.ts

import baseUrl from './baseUrl';
import type { RoadmapResponse } from './generateRoadmap';

export async function getRoadmapForJob(
  jobId: number,
  token: string
): Promise<RoadmapResponse> {
  const response = await fetch(`${baseUrl}/jobs/${jobId}/roadmap`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to get roadmap: ${response.statusText}`);
  }

  return response.json();
}
```

### Schritt 3: Verknüpfung nutzen

```typescript
// Beispiel: Chat Session und Roadmap für einen Job verknüpfen

async function setupJobChatAndRoadmap(jobId: number, token: string) {
  // 1. Chat Session erstellen (setzt automatisch topic_field_id)
  const chatSession = await createChatSessionForJob(jobId, token);
  
  // 2. Roadmap abrufen (verwendet die gleiche topic_field_id)
  const roadmap = await getRoadmapForJob(jobId, token);
  
  // 3. Verknüpfung prüfen
  if (chatSession.topic_field_id === roadmap.topic_field_id) {
    console.log('✅ Chat Session und Roadmap sind verknüpft!');
    console.log(`   topic_field_id: ${chatSession.topic_field_id}`);
  }
  
  return { chatSession, roadmap };
}
```

## Beispiel: In React Component verwenden

```typescript
import { useState, useEffect } from 'react';
import { createChatSessionForJob } from '~/api/createChatSession';
import { getRoadmapForJob } from '~/api/getRoadmapForJob';

function JobChatView({ jobId }: { jobId: number }) {
  const [chatSession, setChatSession] = useState(null);
  const [roadmap, setRoadmap] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadJobData() {
      const token = localStorage.getItem('auth_token');
      if (!token) return;

      try {
        // Chat Session erstellen/abrufen
        const session = await createChatSessionForJob(jobId, token);
        setChatSession(session);

        // Roadmap abrufen (über topic_field_id verknüpft)
        const jobRoadmap = await getRoadmapForJob(jobId, token);
        setRoadmap(jobRoadmap);

        console.log('Verknüpfung:', {
          chat_topic_field_id: session.topic_field_id,
          roadmap_topic_field_id: jobRoadmap.topic_field_id,
          connected: session.topic_field_id === jobRoadmap.topic_field_id
        });
      } catch (error) {
        console.error('Error loading job data:', error);
      } finally {
        setLoading(false);
      }
    }

    loadJobData();
  }, [jobId]);

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h2>Chat für {chatSession?.job?.name}</h2>
      <p>Topic Field ID: {chatSession?.topic_field_id}</p>
      <p>Roadmap: {roadmap?.name}</p>
      {/* Chat UI hier */}
    </div>
  );
}
```

## Verknüpfung über topic_field_id

**Wichtig**: Chat Session und Roadmap sind über `topic_field_id` verbunden:

1. **Job hat `topic_field_id`**: Jeder Job hat eine eindeutige `topic_field_id`
2. **Chat Session verwendet Job's `topic_field_id`**: Automatisch beim Erstellen
3. **Roadmap verwendet gleiche `topic_field_id`**: Über `job.topic_field_id`

**Workflow**:
```
Job (id: 11, topic_field_id: 6)
  ↓
Chat Session (topic_field_id: 6, career_tree_node_id: 11)
  ↓
Roadmap (topic_field_id: 6)
```

**Beide sind verknüpft über `topic_field_id: 6`!**

