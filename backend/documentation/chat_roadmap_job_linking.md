# Chat Sessions and Roadmaps - Job Linking via topic_field_id

## Overview

Chat Sessions und Roadmaps für Jobs sind jetzt über `topic_field_id` verbunden. Jeder Job hat eine eindeutige `topic_field_id`, die sowohl für Chat Sessions als auch für Roadmaps verwendet wird.

## Backend Implementation

### 1. Job → Chat Session Verknüpfung

**Endpoint**: `POST /api/v1/jobs/{job_id}/chat/sessions`

**Funktionsweise**:
- Wenn eine Chat Session für einen Job erstellt wird, verwendet das Backend automatisch die `topic_field_id` des Jobs
- Die Chat Session wird mit beiden Feldern erstellt:
  - `career_tree_node_id` = job_id (für Job-Referenz)
  - `topic_field_id` = job.topic_field_id (für Roadmap-Verknüpfung)

**Code**: `backend/api/services/chat_service.py:get_or_create_job_session()`

```python
# Automatisch setzt topic_field_id vom Job
topic_field_id = job.topic_field_id
ChatService.get_or_create_session(
    user_id=user_id,
    topic_field_id=topic_field_id,  # Verbindet mit Roadmap
    career_tree_node_id=job_id,      # Job-Referenz
    db=db,
)
```

### 2. Job → Roadmap Verknüpfung

**Endpoint**: `GET /api/v1/jobs/{job_id}/roadmap` (neu!)
**Endpoint**: `POST /api/v1/jobs/{job_id}/roadmap/generate`

**Funktionsweise**:
- Roadmap wird über die `topic_field_id` des Jobs abgerufen/generiert
- Jeder Job hat eine eindeutige `topic_field_id`, daher gibt es eine 1:1-Beziehung

## Frontend Integration

### Chat Session für Job erstellen

```typescript
// Option 1: Direkt über Job ID
POST /api/v1/jobs/{job_id}/chat/sessions

// Response enthält:
{
  "id": 1,
  "topic_field_id": 6,        // ← Verbindet Chat mit Roadmap
  "career_tree_node_id": 11,  // ← Job ID
  "job": {
    "id": 11,
    "name": "Research Scientist - Network Flow",
    ...
  }
}
```

### Roadmap für Job abrufen

```typescript
// Option 1: Über Job ID (neu!)
GET /api/v1/jobs/{job_id}/roadmap

// Option 2: Über topic_field_id
GET /api/v1/topic-fields/{topic_field_id}/roadmap

// Beide geben die gleiche Roadmap zurück, wenn job.topic_field_id === topic_field_id
```

### Verknüpfung nutzen

Da Chat Session und Roadmap die gleiche `topic_field_id` haben:

```typescript
// 1. Chat Session für Job erstellen
const chatSession = await createChatSessionForJob(jobId, token);

// 2. Roadmap über topic_field_id abrufen
const roadmap = await getRoadmap(chatSession.topic_field_id, token);

// Oder direkt über Job ID
const roadmap = await getRoadmapForJob(jobId, token);
```

## Beispiel Workflow

1. **User wählt Job aus Career Tree**
   - Job hat `topic_field_id: 6`

2. **Frontend erstellt Chat Session**
   ```
   POST /api/v1/jobs/11/chat/sessions
   → Chat Session mit topic_field_id: 6
   ```

3. **Frontend ruft Roadmap ab**
   ```
   GET /api/v1/jobs/11/roadmap
   → Roadmap mit topic_field_id: 6
   ```

4. **Chat Session und Roadmap sind verbunden**
   - Beide verwenden die gleiche `topic_field_id: 6`
   - Können über `topic_field_id` verknüpft werden

## API Endpoints Zusammenfassung

| Aktion | Endpoint | Verknüpfung |
|--------|----------|-------------|
| Chat Session für Job erstellen | `POST /api/v1/jobs/{job_id}/chat/sessions` | Setzt automatisch `topic_field_id` vom Job |
| Roadmap für Job abrufen | `GET /api/v1/jobs/{job_id}/roadmap` | Verwendet `job.topic_field_id` |
| Roadmap für Job generieren | `POST /api/v1/jobs/{job_id}/roadmap/generate` | Verwendet `job.topic_field_id` |
| Roadmap über topic_field_id | `GET /api/v1/topic-fields/{topic_field_id}/roadmap` | Direkte Verknüpfung |

## Frontend Implementation Guide

### TypeScript Interfaces

```typescript
interface ChatSessionResponse {
  id: number;
  topic_field_id: number | null;      // ← Verbindet mit Roadmap
  career_tree_node_id: number | null; // ← Job ID
  job?: CareerTreeNode;
  message_count: number;
}

interface RoadmapResponse {
  id: number;
  topic_field_id: number;  // ← Verbindet mit Chat Session
  name: string;
  // ...
}
```

### Beispiel: Chat Session erstellen

```typescript
async function createChatSessionForJob(jobId: number, token: string) {
  const response = await fetch(`${baseUrl}/jobs/${jobId}/chat/sessions`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  
  const session: ChatSessionResponse = await response.json();
  return session;
}
```

### Beispiel: Roadmap abrufen

```typescript
async function getRoadmapForJob(jobId: number, token: string) {
  const response = await fetch(`${baseUrl}/jobs/${jobId}/roadmap`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  
  const roadmap: RoadmapResponse = await response.json();
  return roadmap;
}
```

### Beispiel: Verknüpfung nutzen

```typescript
// Chat Session und Roadmap für denselben Job abrufen
const jobId = 11;

// Beide verwenden die gleiche topic_field_id
const chatSession = await createChatSessionForJob(jobId, token);
const roadmap = await getRoadmapForJob(jobId, token);

// Verknüpfung über topic_field_id
console.log(chatSession.topic_field_id === roadmap.topic_field_id); // true
```

