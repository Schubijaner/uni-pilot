# API-Endpunkte – Uni Pilot

## Übersicht

Dieses Dokument spezifiziert alle API-Endpunkte für die Uni Pilot App im Sinne einer API-First-Entwicklung. Die API folgt RESTful Prinzipien und verwendet JSON für Request/Response Bodies.

**Base URL:** `/api/v1`

**Authentication:** Bearer Token (JWT) für geschützte Endpunkte

---

## Authentifizierung & User Management

### 1. User Registrierung

**POST** `/auth/register`

Registriert einen neuen User.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123",
  "first_name": "Max",
  "last_name": "Mustermann"
}
```

**Response 201 Created:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "Max",
  "last_name": "Mustermann",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Error Responses:**
- `400 Bad Request`: E-Mail bereits vorhanden oder ungültige Daten
- `422 Unprocessable Entity`: Validierungsfehler

---

### 2. User Login

**POST** `/auth/login`

Authentifiziert einen User und gibt ein JWT Token zurück.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response 200 OK:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "Max",
    "last_name": "Mustermann"
  }
}
```

**Error Responses:**
- `401 Unauthorized`: Falsche Credentials

---

### 3. Get Current User

**GET** `/auth/me`

Gibt Informationen über den aktuell authentifizierten User zurück.

**Headers:**
```
Authorization: Bearer <token>
```

**Response 200 OK:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "Max",
  "last_name": "Mustermann",
  "created_at": "2024-01-15T10:30:00Z",
  "profile": {
    "id": 1,
    "university_id": 1,
    "study_program_id": 1,
    "current_semester": 3,
    "skills": "Python, JavaScript, SQL",
    "selected_topic_field_id": 5
  }
}
```

**Error Responses:**
- `401 Unauthorized`: Token ungültig oder abgelaufen

---

## Onboarding & Profil

### 4. Get All Universities

**GET** `/universities`

Gibt eine Liste aller verfügbaren Universitäten zurück.

**Query Parameters:**
- `search` (optional): Suchbegriff für Name oder Abkürzung
- `limit` (optional, default: 100): Maximale Anzahl Ergebnisse
- `offset` (optional, default: 0): Pagination Offset

**Response 200 OK:**
```json
{
  "items": [
    {
      "id": 1,
      "name": "Technische Universität München",
      "abbreviation": "TUM",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "limit": 100,
  "offset": 0
}
```

---

### 5. Get Study Programs by University

**GET** `/universities/{university_id}/study-programs`

Gibt alle Studiengänge einer Universität zurück.

**Path Parameters:**
- `university_id` (integer): ID der Universität

**Query Parameters:**
- `degree_type` (optional): Filter nach Abschlusstyp (z.B. "Bachelor", "Master")

**Response 200 OK:**
```json
{
  "items": [
    {
      "id": 1,
      "name": "Informatik",
      "university_id": 1,
      "degree_type": "Bachelor",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1
}
```

---

### 6. Get User Profile

**GET** `/users/me/profile`

Gibt das Profil des aktuellen Users zurück.

**Headers:**
```
Authorization: Bearer <token>
```

**Response 200 OK:**
```json
{
  "id": 1,
  "user_id": 1,
  "university_id": 1,
  "study_program_id": 1,
  "current_semester": 3,
  "skills": "Python, JavaScript, SQL",
  "selected_topic_field_id": 5,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "university": {
    "id": 1,
    "name": "Technische Universität München",
    "abbreviation": "TUM"
  },
  "study_program": {
    "id": 1,
    "name": "Informatik",
    "degree_type": "Bachelor"
  }
}
```

**Error Responses:**
- `404 Not Found`: Profil existiert noch nicht

---

### 7. Create or Update User Profile

**PUT** `/users/me/profile`

Erstellt oder aktualisiert das Profil des aktuellen Users (Onboarding).

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "university_id": 1,
  "study_program_id": 1,
  "current_semester": 3,
  "skills": "Python, JavaScript, SQL"
}
```

**Response 200 OK:**
```json
{
  "id": 1,
  "user_id": 1,
  "university_id": 1,
  "study_program_id": 1,
  "current_semester": 3,
  "skills": "Python, JavaScript, SQL",
  "selected_topic_field_id": null,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

## Module Management

### 8. Get Modules by Study Program

**GET** `/study-programs/{study_program_id}/modules`

Gibt alle Module eines Studiengangs zurück.

**Path Parameters:**
- `study_program_id` (integer): ID des Studiengangs

**Query Parameters:**
- `module_type` (optional): Filter nach Typ (`REQUIRED` oder `ELECTIVE`)
- `semester` (optional): Filter nach empfohlenem Semester
- `limit` (optional, default: 100)
- `offset` (optional, default: 0)

**Response 200 OK:**
```json
{
  "items": [
    {
      "id": 1,
      "name": "Datenbanken",
      "description": "Grundlagen relationaler Datenbanken",
      "module_type": "REQUIRED",
      "study_program_id": 1,
      "semester": 3,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "limit": 100,
  "offset": 0
}
```

---

### 9. Get User's Completed Modules

**GET** `/users/me/modules`

Gibt alle Module zurück, die der User abgeschlossen hat (mit Progress-Daten).

**Headers:**
```
Authorization: Bearer <token>
```

**Response 200 OK:**
```json
{
  "items": [
    {
      "module": {
        "id": 1,
        "name": "Datenbanken",
        "module_type": "REQUIRED",
        "semester": 3
      },
      "completed": true,
      "grade": "1.7",
      "completed_at": "2024-01-10T00:00:00Z"
    }
  ],
  "total": 1
}
```

---

### 10. Update Module Progress

**PUT** `/users/me/modules/{module_id}/progress`

Aktualisiert den Fortschritt eines Users bei einem Modul.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `module_id` (integer): ID des Moduls

**Request Body:**
```json
{
  "completed": true,
  "grade": "1.7",
  "completed_at": "2024-01-10T00:00:00Z"
}
```

**Response 200 OK:**
```json
{
  "user_id": 1,
  "module_id": 1,
  "completed": true,
  "grade": "1.7",
  "completed_at": "2024-01-10T00:00:00Z"
}
```

---

## Career Tree & Topic Fields

### 11. Get Career Tree for Study Program

**GET** `/study-programs/{study_program_id}/career-tree`

Gibt den Career Tree für einen Studiengang zurück (hierarchische Struktur).

**Path Parameters:**
- `study_program_id` (integer): ID des Studiengangs

**Response 200 OK:**
```json
{
  "study_program_id": 1,
  "nodes": [
    {
      "id": 1,
      "name": "Software Development",
      "description": "Entwicklung von Software-Anwendungen",
      "is_leaf": false,
      "level": 1,
      "children": [
        {
          "id": 2,
          "name": "Full Stack Development",
          "description": "Frontend und Backend Entwicklung",
          "is_leaf": true,
          "level": 2,
          "topic_field": {
            "id": 1,
            "name": "Full Stack Development",
            "description": "Komplette Web-Entwicklung"
          },
          "children": []
        }
      ]
    }
  ]
}
```

---

### 12. Get All Topic Fields

**GET** `/topic-fields`

Gibt alle verfügbaren Themenfelder zurück.

**Query Parameters:**
- `search` (optional): Suchbegriff
- `limit` (optional, default: 100)
- `offset` (optional, default: 0)

**Response 200 OK:**
```json
{
  "items": [
    {
      "id": 1,
      "name": "Full Stack Development",
      "description": "Komplette Web-Entwicklung von Frontend bis Backend",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "limit": 100,
  "offset": 0
}
```

---

### 13. Get Topic Field by ID

**GET** `/topic-fields/{topic_field_id}`

Gibt Details zu einem spezifischen Themenfeld zurück.

**Path Parameters:**
- `topic_field_id` (integer): ID des Themenfelds

**Response 200 OK:**
```json
{
  "id": 1,
  "name": "Full Stack Development",
  "description": "Komplette Web-Entwicklung von Frontend bis Backend",
  "system_prompt": "Du bist ein Experte für Full Stack Development...",
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

### 14. Select Topic Field

**PUT** `/users/me/profile/topic-field`

Wählt ein Themenfeld für den User aus (nach Career Tree Navigation).

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "topic_field_id": 1
}
```

**Response 200 OK:**
```json
{
  "id": 1,
  "user_id": 1,
  "selected_topic_field_id": 1,
  "updated_at": "2024-01-15T11:00:00Z"
}
```

---

## User Questions (Dynamische Career Tree Anpassung)

### 15. Create User Question

**POST** `/users/me/questions`

Speichert eine beantwortete Frage des Users (für dynamische Career Tree Anpassung).

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "question_text": "Interessierst du dich für Frontend-Entwicklung?",
  "answer": true,
  "career_tree_node_id": 2
}
```

**Response 201 Created:**
```json
{
  "id": 1,
  "user_id": 1,
  "question_text": "Interessierst du dich für Frontend-Entwicklung?",
  "answer": true,
  "career_tree_node_id": 2,
  "created_at": "2024-01-15T11:30:00Z"
}
```

---

### 16. Get User Questions

**GET** `/users/me/questions`

Gibt alle beantworteten Fragen des Users zurück.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `career_tree_node_id` (optional): Filter nach Career Tree Node
- `limit` (optional, default: 100)
- `offset` (optional, default: 0)

**Response 200 OK:**
```json
{
  "items": [
    {
      "id": 1,
      "question_text": "Interessierst du dich für Frontend-Entwicklung?",
      "answer": true,
      "career_tree_node_id": 2,
      "created_at": "2024-01-15T11:30:00Z"
    }
  ],
  "total": 1,
  "limit": 100,
  "offset": 0
}
```

---

## Roadmaps

### 17. Get Roadmap for Topic Field

**GET** `/topic-fields/{topic_field_id}/roadmap`

Gibt die Roadmap für ein Themenfeld zurück.

**Path Parameters:**
- `topic_field_id` (integer): ID des Themenfelds

**Query Parameters:**
- `include_items` (optional, default: true): Ob Roadmap-Items eingeschlossen werden sollen

**Response 200 OK:**
```json
{
  "id": 1,
  "topic_field_id": 1,
  "name": "Full Stack Development Roadmap",
  "description": "Schritt-für-Schritt Anleitung zum Full Stack Developer",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T00:00:00Z",
  "items": [
    {
      "id": 1,
      "roadmap_id": 1,
      "item_type": "MODULE",
      "title": "Web Development Grundlagen",
      "description": "Lerne HTML, CSS und JavaScript",
      "semester": 3,
      "is_semester_break": false,
      "order": 1,
      "module_id": 5,
      "is_important": true,
      "created_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": 2,
      "roadmap_id": 1,
      "item_type": "PROJECT",
      "title": "Eigene Web-App erstellen",
      "description": "Baue eine vollständige Web-Anwendung",
      "semester": null,
      "is_semester_break": true,
      "order": 2,
      "module_id": null,
      "is_important": false,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

### 18. Get User's Roadmap Progress

**GET** `/users/me/roadmap-progress`

Gibt den Fortschritt des Users bei seiner ausgewählten Roadmap zurück.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `topic_field_id` (optional): Filter nach Themenfeld (falls mehrere Roadmaps)

**Response 200 OK:**
```json
{
  "roadmap": {
    "id": 1,
    "topic_field_id": 1,
    "name": "Full Stack Development Roadmap"
  },
  "items": [
    {
      "roadmap_item": {
        "id": 1,
        "title": "Web Development Grundlagen",
        "item_type": "MODULE",
        "semester": 3,
        "is_semester_break": false,
        "order": 1
      },
      "completed": true,
      "completed_at": "2024-01-12T00:00:00Z",
      "notes": "Sehr hilfreich für das Verständnis"
    },
    {
      "roadmap_item": {
        "id": 2,
        "title": "Eigene Web-App erstellen",
        "item_type": "PROJECT",
        "is_semester_break": true,
        "order": 2
      },
      "completed": false,
      "completed_at": null,
      "notes": null
    }
  ],
  "progress_percentage": 50.0
}
```

---

### 19. Update Roadmap Item Progress

**PUT** `/users/me/roadmap-items/{roadmap_item_id}/progress`

Aktualisiert den Fortschritt eines Users bei einem Roadmap-Item.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `roadmap_item_id` (integer): ID des Roadmap-Items

**Request Body:**
```json
{
  "completed": true,
  "completed_at": "2024-01-12T00:00:00Z",
  "notes": "Sehr hilfreich für das Verständnis"
}
```

**Response 200 OK:**
```json
{
  "user_id": 1,
  "roadmap_item_id": 1,
  "completed": true,
  "completed_at": "2024-01-12T00:00:00Z",
  "notes": "Sehr hilfreich für das Verständnis"
}
```

---

### 20. Get Roadmap Items by Semester

**GET** `/users/me/roadmap-items`

Gibt Roadmap-Items des Users gefiltert nach Semester oder Semesterferien zurück.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `semester` (optional): Filter nach Semester
- `is_semester_break` (optional, boolean): Filter nach Semesterferien
- `completed` (optional, boolean): Filter nach abgeschlossenen Items
- `limit` (optional, default: 100)
- `offset` (optional, default: 0)

**Response 200 OK:**
```json
{
  "items": [
    {
      "roadmap_item": {
        "id": 1,
        "title": "Web Development Grundlagen",
        "item_type": "MODULE",
        "semester": 3,
        "is_semester_break": false
      },
      "completed": true,
      "completed_at": "2024-01-12T00:00:00Z"
    }
  ],
  "total": 1,
  "limit": 100,
  "offset": 0
}
```

---

## Chat

### 21. Create or Get Chat Session

**POST** `/topic-fields/{topic_field_id}/chat/sessions`

Erstellt eine neue Chat-Session für ein Themenfeld oder gibt die bestehende zurück.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `topic_field_id` (integer): ID des Themenfelds

**Response 200 OK (bestehende Session) / 201 Created (neue Session):**
```json
{
  "id": 1,
  "user_id": 1,
  "topic_field_id": 1,
  "created_at": "2024-01-15T12:00:00Z",
  "updated_at": "2024-01-15T12:00:00Z"
}
```

---

### 22. Get Chat Messages

**GET** `/chat/sessions/{session_id}/messages`

Gibt alle Nachrichten einer Chat-Session zurück.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `session_id` (integer): ID der Chat-Session

**Query Parameters:**
- `limit` (optional, default: 100)
- `offset` (optional, default: 0)

**Response 200 OK:**
```json
{
  "items": [
    {
      "id": 1,
      "session_id": 1,
      "role": "user",
      "content": "Welche Skills brauche ich für Full Stack Development?",
      "created_at": "2024-01-15T12:05:00Z"
    },
    {
      "id": 2,
      "session_id": 1,
      "role": "assistant",
      "content": "Für Full Stack Development solltest du folgende Skills beherrschen...",
      "created_at": "2024-01-15T12:05:05Z"
    }
  ],
  "total": 2,
  "limit": 100,
  "offset": 0
}
```

---

### 23. Send Chat Message

**POST** `/chat/sessions/{session_id}/messages`

Sendet eine Nachricht in einer Chat-Session und erhält eine Antwort.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `session_id` (integer): ID der Chat-Session

**Request Body:**
```json
{
  "content": "Welche Tools empfehlst du für Backend-Entwicklung?"
}
```

**Response 200 OK:**
```json
{
  "user_message": {
    "id": 3,
    "session_id": 1,
    "role": "user",
    "content": "Welche Tools empfehlst du für Backend-Entwicklung?",
    "created_at": "2024-01-15T12:10:00Z"
  },
  "assistant_message": {
    "id": 4,
    "session_id": 1,
    "role": "assistant",
    "content": "Für Backend-Entwicklung empfehle ich folgende Tools...",
    "created_at": "2024-01-15T12:10:02Z"
  }
}
```

---

### 24. Get User's Chat Sessions

**GET** `/users/me/chat/sessions`

Gibt alle Chat-Sessions des Users zurück.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `topic_field_id` (optional): Filter nach Themenfeld
- `limit` (optional, default: 100)
- `offset` (optional, default: 0)

**Response 200 OK:**
```json
{
  "items": [
    {
      "id": 1,
      "topic_field_id": 1,
      "topic_field": {
        "id": 1,
        "name": "Full Stack Development"
      },
      "created_at": "2024-01-15T12:00:00Z",
      "updated_at": "2024-01-15T12:10:00Z",
      "message_count": 4
    }
  ],
  "total": 1,
  "limit": 100,
  "offset": 0
}
```

---

## Recommendations

### 25. Get Recommendations for Topic Field

**GET** `/topic-fields/{topic_field_id}/recommendations`

Gibt Empfehlungen für ein Themenfeld zurück.

**Path Parameters:**
- `topic_field_id` (integer): ID des Themenfelds

**Query Parameters:**
- `recommendation_type` (optional): Filter nach Typ (z.B. `BOOK`, `COURSE`, `PROJECT`)
- `limit` (optional, default: 100)
- `offset` (optional, default: 0)

**Response 200 OK:**
```json
{
  "items": [
    {
      "id": 1,
      "topic_field_id": 1,
      "title": "Eloquent JavaScript",
      "description": "Buch über JavaScript Grundlagen",
      "recommendation_type": "BOOK",
      "url": "https://eloquentjavascript.net",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "limit": 100,
  "offset": 0
}
```

---

### 26. Get Recommendations for Roadmap Item

**GET** `/roadmap-items/{roadmap_item_id}/recommendations`

Gibt spezifische Empfehlungen für ein Roadmap-Item zurück.

**Path Parameters:**
- `roadmap_item_id` (integer): ID des Roadmap-Items

**Response 200 OK:**
```json
{
  "items": [
    {
      "id": 2,
      "roadmap_item_id": 1,
      "title": "MDN Web Docs",
      "description": "Umfassende Dokumentation für Web-Entwicklung",
      "recommendation_type": "COURSE",
      "url": "https://developer.mozilla.org",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1
}
```

---

## Module Import (Admin)

### 27. Import Modules

**POST** `/admin/modules/import`

Importiert Module aus einem Modulhandbuch (Admin-Endpunkt).

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Request Body:**
```json
{
  "study_program_id": 1,
  "import_source": "Modulhandbuch TUM Informatik 2024",
  "modules": [
    {
      "name": "Datenbanken",
      "description": "Grundlagen relationaler Datenbanken",
      "module_type": "REQUIRED",
      "semester": 3
    }
  ]
}
```

**Response 201 Created:**
```json
{
  "imported_count": 1,
  "failed_count": 0,
  "imports": [
    {
      "id": 1,
      "module_id": 10,
      "import_source": "Modulhandbuch TUM Informatik 2024",
      "import_status": "success",
      "imported_at": "2024-01-15T13:00:00Z"
    }
  ]
}
```

---

### 28. Get Module Import History

**GET** `/admin/modules/imports`

Gibt die Import-Historie zurück (Admin-Endpunkt).

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Query Parameters:**
- `study_program_id` (optional): Filter nach Studiengang
- `import_status` (optional): Filter nach Status (`success`, `partial`, `failed`)
- `limit` (optional, default: 100)
- `offset` (optional, default: 0)

**Response 200 OK:**
```json
{
  "items": [
    {
      "id": 1,
      "module_id": 10,
      "module": {
        "id": 10,
        "name": "Datenbanken"
      },
      "import_source": "Modulhandbuch TUM Informatik 2024",
      "import_status": "success",
      "imported_at": "2024-01-15T13:00:00Z",
      "imported_by": "admin@example.com"
    }
  ],
  "total": 1,
  "limit": 100,
  "offset": 0
}
```

---

## Utility Endpoints

### 29. Health Check

**GET** `/health`

Prüft den Status der API.

**Response 200 OK:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T13:00:00Z",
  "version": "1.0.0"
}
```

---

### 30. Get API Version

**GET** `/version`

Gibt die API-Version zurück.

**Response 200 OK:**
```json
{
  "version": "1.0.0",
  "api_name": "Uni Pilot API"
}
```

---

## Fehlerbehandlung

### Standard Error Response Format

Alle Fehlerantworten folgen diesem Format:

```json
{
  "detail": "Fehlerbeschreibung",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-15T13:00:00Z"
}
```

### HTTP Status Codes

- `200 OK`: Erfolgreiche Anfrage
- `201 Created`: Ressource erfolgreich erstellt
- `400 Bad Request`: Ungültige Anfrage
- `401 Unauthorized`: Authentifizierung fehlgeschlagen
- `403 Forbidden`: Keine Berechtigung
- `404 Not Found`: Ressource nicht gefunden
- `422 Unprocessable Entity`: Validierungsfehler
- `500 Internal Server Error`: Server-Fehler

---

## Pagination

Endpunkte, die Listen zurückgeben, unterstützen Pagination über Query-Parameter:

- `limit`: Anzahl der Ergebnisse pro Seite (default: 100, max: 1000)
- `offset`: Anzahl der zu überspringenden Ergebnisse (default: 0)

**Response Format:**
```json
{
  "items": [...],
  "total": 150,
  "limit": 100,
  "offset": 0,
  "has_more": true
}
```

---

## Filtering & Sorting

Viele Endpunkte unterstützen Filterung und Sortierung:

**Query Parameters:**
- `search`: Volltext-Suche (wenn unterstützt)
- `sort`: Sortierfeld (z.B. `created_at`, `name`)
- `order`: Sortierrichtung (`asc` oder `desc`, default: `asc`)

**Beispiel:**
```
GET /api/v1/modules?search=datenbank&sort=name&order=asc&limit=20
```

---

## Authentication Flow

1. User registriert sich via `POST /auth/register`
2. User loggt sich ein via `POST /auth/login` und erhält JWT Token
3. Token wird in Header gesetzt: `Authorization: Bearer <token>`
4. Token ist für geschützte Endpunkte erforderlich
5. Token hat Ablaufzeit (z.B. 24 Stunden)

---

## Rate Limiting

Die API implementiert Rate Limiting:

- **Public Endpoints:** 100 Requests pro Minute
- **Authenticated Endpoints:** 1000 Requests pro Minute
- **Admin Endpoints:** 5000 Requests pro Minute

Bei Überschreitung: `429 Too Many Requests`

---

*API-Spezifikation erstellt für Review - Stand: 2024*

