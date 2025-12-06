# Uni Pilot - Systemarchitektur

## Überblick

Dieses Dokument beschreibt die Systemarchitektur der Uni Pilot Anwendung - einer Karriereorientierungs-App für Studierende mit AI-gestützter Roadmap-Generierung und Chat-Funktionalität.

**Version:** 1.0.0  
**Stand:** MVP (Minimal Viable Product)  
**LLM Provider:** AWS Bedrock

---

## Architektur-Prinzipien

### Minimalistisch aber vollständig
- Funktionsfähige Implementierung aller Kernfeatures
- Klare Trennung von Verantwortlichkeiten (Separation of Concerns)
- Erweiterbar für zukünftige Features
- Production-ready Basis-Struktur

### Tech-Stack Entscheidungen
- **Backend Framework:** FastAPI (bereits vorhanden)
- **Datenbank:** SQLite (Development) → PostgreSQL (Production)
- **ORM:** SQLAlchemy (bereits vorhanden)
- **LLM:** AWS Bedrock (Claude 3 Haiku/Sonnet)
- **Task Queue:** FastAPI Background Tasks (MVP) → Celery (Production)
- **Caching:** Redis (optional für MVP, empfohlen für Production)

---

## System-Architektur Übersicht

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│                    (Nicht Teil dieser Architektur)           │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ HTTP/REST API
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                    FastAPI Application                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │            API Layer (Routers)                       │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │   │
│  │  │   Auth   │  │ Onboard  │  │  Chat    │          │   │
│  │  │          │  │ Career   │  │ Roadmap  │          │   │
│  │  └──────────┘  └──────────┘  └──────────┘          │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Service Layer (Business Logic)               │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │   │
│  │  │  User    │  │ Career   │  │   LLM    │          │   │
│  │  │ Service  │  │ Service  │  │ Service  │          │   │
│  │  └──────────┘  └──────────┘  └──────────┘          │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │            Data Access Layer                          │   │
│  │              (SQLAlchemy ORM)                         │   │
│  └──────────────────────────────────────────────────────┘   │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼──────┐ ┌─────▼──────┐ ┌──────▼─────────┐
│   SQLite DB  │ │AWS Bedrock │ │  Redis Cache   │
│  (PostgreSQL │ │  (LLM API) │ │  (Optional)    │
│   Prod)      │ └────────────┘ └────────────────┘
└──────────────┘
```

---

## Verzeichnisstruktur

```
uni-pilot/
├── api/                          # FastAPI Application
│   ├── __init__.py
│   ├── dependencies.py           # Shared dependencies (DB, Auth)
│   ├── routers/                  # API Endpoints (REST)
│   │   ├── __init__.py
│   │   ├── auth.py              # Authentication & User Management
│   │   ├── users.py             # User Profile Management
│   │   ├── onboarding.py        # Onboarding & Career Tree
│   │   ├── roadmaps.py          # Roadmap Management
│   │   ├── chat.py              # Chat Endpoints
│   │   ├── modules.py           # Module Management
│   │   ├── universities.py      # University & Study Program CRUD
│   │   ├── health.py            # Health Check (vorhanden)
│   │   └── example.py           # Example (kann entfernt werden)
│   ├── services/                 # Business Logic Layer
│   │   ├── __init__.py
│   │   ├── auth_service.py      # Authentication Logic
│   │   ├── user_service.py      # User & Profile Management
│   │   ├── career_service.py    # Career Tree Logic
│   │   ├── roadmap_service.py   # Roadmap Generation & Management
│   │   ├── chat_service.py      # Chat Logic
│   │   └── llm_service.py       # AWS Bedrock Integration
│   ├── models/                   # Pydantic Schemas (Request/Response)
│   │   ├── __init__.py
│   │   ├── auth.py              # Auth Schemas
│   │   ├── user.py              # User Schemas
│   │   ├── roadmap.py           # Roadmap Schemas
│   │   ├── chat.py              # Chat Schemas
│   │   └── common.py            # Common Schemas (Pagination, etc.)
│   ├── core/                     # Core Configuration
│   │   ├── __init__.py
│   │   ├── config.py            # App Configuration (Settings)
│   │   ├── security.py          # JWT, Password Hashing
│   │   └── exceptions.py        # Custom Exceptions
│   └── prompts/                  # LLM Prompt Templates
│       ├── __init__.py
│       ├── chat_prompts.py      # Chat System Prompts
│       └── roadmap_prompts.py   # Roadmap Generation Prompts
│
├── database/                     # Database Layer (bereits vorhanden)
│   ├── __init__.py
│   ├── base.py                  # DB Engine & Session (vorhanden)
│   └── models.py                # SQLAlchemy Models (vorhanden)
│
├── scripts/                      # Utility Scripts (bereits vorhanden)
│   ├── init_db.py
│   ├── seed_database.py
│   └── view_db.py
│
├── documentation/                # Documentation (bereits vorhanden)
│   ├── architecture.md          # Diese Datei
│   ├── Requierements.md
│   ├── api_endpoints.md
│   └── database_schema.md
│
├── main.py                       # FastAPI App Entry Point (vorhanden)
├── requirements.txt              # Python Dependencies
├── environment.yml               # Conda Environment
└── README.md
```

---

## Komponenten-Details

### 1. API Layer (Routers)

Die Router-Schicht implementiert alle REST-Endpunkte gemäß `api_endpoints.md`.

#### **1.1 Auth Router** (`api/routers/auth.py`)
- `POST /api/v1/auth/register` - User Registrierung
- `POST /api/v1/auth/login` - Login & JWT Token
- `GET /api/v1/auth/me` - Aktueller User

**Abhängigkeiten:**
- `auth_service.py` für Business Logic
- `security.py` für JWT & Password Hashing

#### **1.2 Users Router** (`api/routers/users.py`)
- `GET /api/v1/users/me/profile` - User Profil abrufen
- `PUT /api/v1/users/me/profile` - Profil erstellen/aktualisieren
- `GET /api/v1/users/me/modules` - Abgeschlossene Module
- `PUT /api/v1/users/me/modules/{module_id}/progress` - Modul-Progress
- `GET /api/v1/users/me/roadmap-progress` - Roadmap-Progress
- `PUT /api/v1/users/me/roadmap-items/{item_id}/progress` - Roadmap-Item Progress

#### **1.3 Onboarding Router** (`api/routers/onboarding.py`)
- `GET /api/v1/universities` - Alle Universitäten
- `GET /api/v1/universities/{id}/study-programs` - Studiengänge
- `GET /api/v1/study-programs/{id}/career-tree` - Career Tree
- `GET /api/v1/topic-fields` - Alle Themenfelder
- `GET /api/v1/topic-fields/{id}` - Themenfeld Details
- `PUT /api/v1/users/me/profile/topic-field` - Themenfeld auswählen
- `POST /api/v1/users/me/questions` - User-Fragen (für dynamische Anpassung)

#### **1.4 Roadmaps Router** (`api/routers/roadmaps.py`)
- `GET /api/v1/topic-fields/{id}/roadmap` - Roadmap abrufen
- `POST /api/v1/topic-fields/{id}/roadmap/generate` - Roadmap generieren (LLM)
- `GET /api/v1/users/me/roadmap-items` - Roadmap-Items filtern

#### **1.5 Chat Router** (`api/routers/chat.py`)
- `POST /api/v1/topic-fields/{id}/chat/sessions` - Chat-Session erstellen/abrufen
- `GET /api/v1/chat/sessions/{id}/messages` - Nachrichten abrufen
- `POST /api/v1/chat/sessions/{id}/messages` - Nachricht senden (mit LLM-Response)
- `GET /api/v1/users/me/chat/sessions` - Alle Chat-Sessions des Users

#### **1.6 Modules Router** (`api/routers/modules.py`)
- `GET /api/v1/study-programs/{id}/modules` - Module eines Studiengangs
- `POST /api/v1/admin/modules/import` - Module importieren (Admin)

#### **1.7 Universities Router** (`api/routers/universities.py`)
- Separate Router für University/Study Program CRUD (falls erweitert)

---

### 2. Service Layer

Die Service-Schicht enthält die gesamte Business Logic, getrennt von der API-Schicht.

#### **2.1 Auth Service** (`api/services/auth_service.py`)
```python
class AuthService:
    - register_user(email, password, ...) -> User
    - authenticate_user(email, password) -> JWT Token
    - get_current_user(token) -> User
```

#### **2.2 User Service** (`api/services/user_service.py`)
```python
class UserService:
    - get_or_create_profile(user_id, ...) -> UserProfile
    - update_profile(user_id, profile_data) -> UserProfile
    - get_user_modules(user_id) -> List[UserModuleProgress]
    - update_module_progress(user_id, module_id, ...) -> UserModuleProgress
    - get_roadmap_progress(user_id, topic_field_id) -> RoadmapProgress
```

#### **2.3 Career Service** (`api/services/career_service.py`)
```python
class CareerService:
    - get_career_tree(study_program_id, db: Session) -> CareerTreeResponse
        # Lädt alle Nodes + Relationships aus DB
        # Baut hierarchische Graph-Struktur auf
        # Gibt verschachtelte JSON-Struktur zurück
    - get_topic_field(topic_field_id, db: Session) -> TopicField
    - select_topic_field(user_id, topic_field_id, db: Session) -> UserProfile
    - create_user_question(user_id, question, answer, node_id, db: Session) -> UserQuestion
```

**Wichtig:** Der Career Tree wird **NICHT durch LLM generiert**, sondern:
1. **Statisch erstellt** (Seed-Script oder Admin)
2. **Zur Laufzeit aus DB geladen** und als Graph-Struktur aufgebaut
3. **Pro Studiengang** ein eigener Career Tree

#### **2.4 Roadmap Service** (`api/services/roadmap_service.py`)
```python
class RoadmapService:
    - get_roadmap(topic_field_id) -> Roadmap | None
    - generate_roadmap(
        user_profile: UserProfile,
        topic_field: TopicField,
        study_program: StudyProgram
      ) -> Roadmap
    - update_roadmap_progress(user_id, roadmap_item_id, ...) -> UserRoadmapItem
```

**Roadmap-Generierung Flow:**
1. User-Profil, Studiengang, Module, Themenfeld-Daten sammeln
2. Prompt konstruieren (`roadmap_prompts.py`)
3. LLM-Service aufrufen (`llm_service.generate_roadmap()`)
4. LLM-Response parsen & validieren (Pydantic)
5. Roadmap & RoadmapItems in DB speichern
6. Roadmap zurückgeben

#### **2.5 Chat Service** (`api/services/chat_service.py`)
```python
class ChatService:
    - get_or_create_session(user_id, topic_field_id) -> ChatSession
    - get_messages(session_id, limit, offset) -> List[ChatMessage]
    - send_message(
        session_id: int,
        user_message: str,
        topic_field: TopicField
      ) -> ChatMessage (assistant response)
```

**Chat Flow:**
1. Chat-Session abrufen oder erstellen
2. Letzte N Messages laden (History)
3. System-Prompt vom TopicField laden
4. LLM-Service aufrufen (`llm_service.chat()`)
5. User-Message & Assistant-Response speichern
6. Assistant-Response zurückgeben

#### **2.6 LLM Service** (`api/services/llm_service.py`)
**AWS Bedrock Integration**

```python
class LLMService:
    - __init__(bedrock_client, model_id="anthropic.claude-3-haiku-20240307-v1:0")
    - chat(
        system_prompt: str,
        messages: List[Dict],
        temperature: float = 0.7
      ) -> str
    - generate_roadmap(
        prompt: str,
        response_schema: Dict
      ) -> Dict  # Structured JSON Response
```

**Implementation Details:**
- Verwendet `boto3` für AWS Bedrock API
- `anthropic.claude-3-haiku-20240307-v1:0` für Chat (schnell, günstig)
- `anthropic.claude-3-sonnet-20240229-v1:0` für Roadmap-Generierung (bessere Qualität)
- Error Handling & Retries
- Token Counting (optional)

---

### 3. Core Configuration

#### **3.1 Config** (`api/core/config.py`)
```python
class Settings:
    # Database
    DATABASE_URL: str
    
    # AWS Bedrock
    AWS_REGION: str = "eu-central-1"
    AWS_ACCESS_KEY_ID: str  # Optional, kann von IAM Role kommen
    AWS_SECRET_ACCESS_KEY: str
    BEDROCK_MODEL_CHAT: str = "anthropic.claude-3-haiku-20240307-v1:0"
    BEDROCK_MODEL_ROADMAP: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 Stunden
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # LLM Settings
    MAX_CHAT_HISTORY_MESSAGES: int = 20
    CHAT_TEMPERATURE: float = 0.7
    ROADMAP_TEMPERATURE: float = 0.3  # Weniger kreativ für strukturierte Daten
```

#### **3.2 Security** (`api/core/security.py`)
```python
def hash_password(password: str) -> str
def verify_password(plain_password: str, hashed_password: str) -> bool
def create_access_token(data: Dict, expires_delta: Optional[timedelta]) -> str
def decode_token(token: str) -> Dict
def get_current_user(token: str, db: Session) -> User
```

---

### 4. Prompt Templates

#### **4.1 Chat Prompts** (`api/prompts/chat_prompts.py`)
```python
def get_chat_system_prompt(topic_field: TopicField) -> str:
    """Generiert System-Prompt für Chat basierend auf Themenfeld."""
    return f"""Du bist ein Experte für {topic_field.name}.

{topic_field.description}

Deine Aufgabe:
- Erkläre das Themenfeld verständlich
- Beantworte Fragen präzise und kurz
- Gib praktische Hinweise zu Skills, Tools und Einstiegsmöglichkeiten
- Sei ermutigend und konstruktiv

Antworte immer auf Deutsch und in maximal 300 Wörtern."""
```

#### **4.2 Roadmap Prompts** (`api/prompts/roadmap_prompts.py`)
```python
def generate_roadmap_prompt(
    study_program: StudyProgram,
    user_profile: UserProfile,
    topic_field: TopicField,
    available_modules: List[Module]
) -> str:
    """Generiert Prompt für Roadmap-Generierung."""
    
    # Module als JSON-String formatieren
    modules_str = json.dumps([
        {
            "id": m.id,
            "name": m.name,
            "description": m.description,
            "type": m.module_type.value,
            "semester": m.semester
        }
        for m in available_modules
    ], indent=2)
    
    return f"""Du bist ein Karriereberater für {study_program.name} Studierende.

Erstelle eine detaillierte Roadmap für das Karriereziel: {topic_field.name}

Kontext:
- Studiengang: {study_program.name}
- Aktuelles Semester: {user_profile.current_semester}
- Bereits vorhandene Skills: {user_profile.skills or "Keine angegeben"}
- Themenfeld: {topic_field.name}

Verfügbare Module:
{modules_str}

Die Roadmap muss folgende Struktur haben:
1. Module aus dem Modulhandbuch empfehlen (IDs aus obiger Liste)
2. Bücher/Ressourcen empfehlen
3. Online-Kurse/Bootcamps empfehlen
4. Praktika/Werkstudentenstellen empfehlen
5. Skills vorschlagen
6. Projektideen vorschlagen

Struktur die Roadmap nach Semestern (bis Semester {user_profile.current_semester + 4}) und Semesterferien.

Gib die Antwort als JSON zurück mit folgendem Schema:
{{
    "name": "Roadmap Name",
    "description": "Kurze Beschreibung",
    "items": [
        {{
            "item_type": "MODULE|BOOK|COURSE|PROJECT|SKILL|CERTIFICATE|INTERNSHIP|BOOTCAMP",
            "title": "Titel",
            "description": "Beschreibung",
            "semester": 3,  # oder null
            "is_semester_break": false,
            "order": 1,
            "module_id": 5,  # nur wenn item_type == "MODULE"
            "is_important": true
        }}
    ]
}}"""
```

---

### 5. Data Models (Pydantic Schemas)

Alle Request/Response-Models als Pydantic-Schemas in `api/models/`.

#### Beispiel: `api/models/auth.py`
```python
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
```

#### Beispiel: `api/models/roadmap.py`
```python
class RoadmapItemCreate(BaseModel):
    item_type: RoadmapItemType
    title: str
    description: str
    semester: Optional[int] = None
    is_semester_break: bool = False
    order: int
    module_id: Optional[int] = None
    is_important: bool = False

class RoadmapGenerateRequest(BaseModel):
    topic_field_id: int

class RoadmapResponse(BaseModel):
    id: int
    topic_field_id: int
    name: str
    description: Optional[str]
    items: List[RoadmapItemResponse]
```

---

## Datenfluss-Diagramme

### Roadmap-Generierung Flow

```
User wählt Themenfeld
    │
    ▼
PUT /api/v1/users/me/profile/topic-field
    │
    ▼
[AuthService] Token validieren → User
    │
    ▼
[CareerService] select_topic_field()
    │
    ▼
[CareerService] TopicField auswählen & in UserProfile speichern
    │
    ▼
User muss explizit Roadmap generieren:
    │
    ▼
POST /api/v1/topic-fields/{id}/roadmap/generate
    │
    ▼
[RoadmapService] get_roadmap(topic_field_id)
    → Prüft ob Roadmap bereits existiert
    │
    ├─→ JA: Gibt vorhandene Roadmap zurück (keine neue Generierung)
    │
    └─→ NEIN:
        │
        ▼
[RoadmapService] generate_roadmap()
    │
    ├─→ User-Profile laden
    ├─→ Studiengang & Module laden
    ├─→ Themenfeld-Daten laden
    │
    ▼
[Prompt] generate_roadmap_prompt()
    │
    ▼
[LLMService] generate_roadmap(prompt, schema)
    │
    ├─→ AWS Bedrock API Call (Claude 3 Sonnet)
    │
    ▼
LLM Response (JSON)
    │
    ▼
[Pydantic] Validierung gegen Schema
    │
    ▼
[RoadmapService] DB Transaction:
    ├─→ Roadmap erstellen
    ├─→ RoadmapItems erstellen
    │
    ▼
RoadmapResponse zurückgeben
    │
    ▼
Frontend zeigt Roadmap an
```

### Chat Flow

```
User sendet Nachricht
    │
    ▼
POST /api/v1/chat/sessions/{id}/messages
    │
    ▼
[AuthService] Token validieren → User
    │
    ▼
[ChatService] send_message()
    │
    ├─→ ChatSession laden
    ├─→ Letzte 20 Messages laden (History)
    ├─→ TopicField & System-Prompt laden
    │
    ▼
[ChatService] User-Message in DB speichern
    │
    ▼
[LLMService] chat(system_prompt, messages)
    │
    ├─→ Messages formatieren für Bedrock API
    ├─→ AWS Bedrock API Call (Claude 3 Haiku)
    │
    ▼
LLM Response (Text)
    │
    ▼
[ChatService] Assistant-Message in DB speichern
    │
    ▼
ChatMessageResponse zurückgeben
    │
    ▼
Frontend zeigt Antwort an
```

---

## AWS Bedrock Setup

### 1. AWS Account Setup

1. **AWS Account erstellen/verwenden**
2. **Bedrock Access aktivieren:**
   - AWS Console → Amazon Bedrock
   - "Model access" Tab
   - Folgende Modelle freischalten:
     - Anthropic Claude 3 Haiku
     - Anthropic Claude 3 Sonnet
3. **IAM User/Role erstellen:**
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "bedrock:InvokeModel",
           "bedrock:InvokeModelWithResponseStream"
         ],
         "Resource": [
           "arn:aws:bedrock:eu-central-1::foundation-model/anthropic.claude-3-haiku-*",
           "arn:aws:bedrock:eu-central-1::foundation-model/anthropic.claude-3-sonnet-*"
         ]
       }
     ]
   }
   ```
4. **AWS Credentials konfigurieren:**
   - Option A: Environment Variables (`.env`)
     ```
     AWS_REGION=eu-central-1
     AWS_ACCESS_KEY_ID=...
     AWS_SECRET_ACCESS_KEY=...
     ```
   - Option B: AWS CLI (`aws configure`)
   - Option C: IAM Role (für EC2/ECS Deployment)

### 2. Python Dependencies

```txt
boto3>=1.34.0
langchain-aws>=0.1.0  # Optional, für LangChain Integration
```

---

## Fehlerbehandlung & Validierung

### Exception Hierarchy

```python
# api/core/exceptions.py

class UniPilotException(Exception):
    """Base exception."""

class NotFoundError(UniPilotException):
    """Resource not found."""
    
class ValidationError(UniPilotException):
    """Validation error."""
    
class AuthenticationError(UniPilotException):
    """Authentication failed."""
    
class LLMError(UniPilotException):
    """LLM API error."""
```

### Error Response Format

```json
{
  "detail": "Fehlerbeschreibung",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-15T13:00:00Z"
}
```

---

## Caching-Strategie (Optional für MVP)

### Redis Integration (Phase 2)

**Was cachen:**
- Roadmaps: `roadmap:{topic_field_id}:{user_profile_hash}` → TTL: 24h
- Career Trees: `career_tree:{study_program_id}` → TTL: 1h (selten geändert)
- Chat History: `chat_history:{session_id}` → TTL: 24h

**Für MVP:** Kein Caching nötig, später hinzufügen.

---

## Testing-Strategie

### Unit Tests
- Service Layer: Mock DB & LLM
- Prompt Templates: Assert gegen erwartete Strings

### Integration Tests
- API Endpoints: TestClient von FastAPI
- LLM Service: Mock AWS Bedrock Responses

### Test Structure
```
tests/
├── unit/
│   ├── services/
│   └── prompts/
├── integration/
│   └── api/
└── conftest.py  # Fixtures
```

---

## Deployment-Konfiguration

### Development
- SQLite Database (bereits vorhanden)
- Local FastAPI Server (Uvicorn)
- AWS Bedrock API (remote)

### Production (Phase 2)
- PostgreSQL Database
- Gunicorn + Uvicorn Workers
- Redis für Caching
- Celery für Background Jobs
- AWS Bedrock API (remote)
- Environment Variables für Secrets

---

## Implementierungs-Prioritäten

### Phase 1: MVP Core Features
1. ✅ Database Models (bereits vorhanden)
2. ✅ FastAPI App Setup (bereits vorhanden)
3. **Auth Service & Router** (JWT, Register, Login)
4. **User Service & Router** (Profile Management)
5. **Onboarding Router** (Universities, Study Programs, Career Tree)
6. **LLM Service** (AWS Bedrock Integration)
7. **Roadmap Service & Router** (Roadmap-Generierung)
8. **Chat Service & Router** (Chat-Funktionalität)

### Phase 2: Production-Ready
1. Error Handling & Validation
2. Rate Limiting
3. Caching (Redis)
4. Background Jobs (Celery)
5. Monitoring & Logging
6. Comprehensive Testing

### Phase 3: Advanced Features
1. Dynamic Career Tree Anpassung (User Questions)
2. Roadmap Regenerierung
3. Vector DB für RAG (optional)
4. A/B Testing für Prompts

---

## Career Tree & Roadmap-Erstellung

### Überblick: Zwei hierarchische Trees in der App

Die App hat **zwei hierarchische Strukturen (Trees)**:

1. **Themenfelder-Tree**: Hierarchischer Graph zur Navigation zu Themenfeldern (TopicFields) - **hierarchisch strukturiert**
2. **Roadmap Tree**: Hierarchischer Graph der Karrierewege - **dynamisch anpassbar, Leaf Nodes = Berufe**

### Was wird wo erstellt?

| Komponente | Typ | Wo wird es erstellt? | Wann? | Struktur |
|------------|-----|---------------------|-------|----------|
| **TopicFields** | Statisch | Seed-Script / Admin | Initial Setup | Flach (Liste) |
| **Themenfelder-Tree** | Statisch | Seed-Script / Admin | Pro Studiengang | **Hierarchisch (Graph)** ✅ |
| **Roadmaps** | Dynamisch | LLM-Service | Bei User-Auswahl | Container |
| **Roadmap Tree** | Dynamisch | LLM-Service | Bei Roadmap-Generierung | **Hierarchisch (Graph)** ⚠️ **FEHLT AKTUELL** |
| **Roadmap Items** | Dynamisch | LLM-Service | Bei Roadmap-Generierung | **Hierarchisch (Parent-Child)** ⚠️ **FEHLT AKTUELL** |

### Wichtige Klarstellung:

- **Themenfelder-Tree**: **Muss hierarchisch sein** - Navigationsbaum zu Themenfeldern (z.B. "Software Development" → "Full Stack Development" → TopicField). Leaf Nodes sind **TopicFields**
- **Roadmap Tree**: **Muss hierarchisch sein** - Leaf Nodes sind **Berufe** (Ziel), dazwischen Skills, Module, Kurse, etc. - **dynamisch anpassbar** basierend auf User-Fragen

---

### 1. TopicFields (Themenfelder)

**Was:** Karriere-Themenfelder wie "Full Stack Development", "Data Science", etc.

**Wo erstellt:**
- **MVP:** Statisch im Seed-Script (`scripts/seed_database.py`)
- **Production:** Admin-Interface oder Seed-Script

**Wie erstellt:**
```python
# scripts/seed_database.py
topic_fullstack = TopicField(
    name="Full Stack Development",
    description="Frontend und Backend Entwicklung",
    system_prompt="Du bist ein Experte für Full Stack Development...",
)
db.add(topic_fullstack)
```

**Wann aktualisiert:**
- Initial Setup (Database Seeding)
- Manuell durch Admin (später über Admin-Interface)
- Nicht automatisch durch LLM

**Beziehungen:**
- Ein TopicField kann mehreren CareerTreeNodes zugeordnet sein (unterschiedliche Studiengänge)
- Ein TopicField hat einen System-Prompt für den Chat

---

### 2. Themenfelder-Tree (Hierarchische Navigation)

**Was:** Hierarchischer Graph/Navigationsbaum zu Themenfeldern für einen Studiengang.

**WICHTIG:** **Muss hierarchisch strukturiert sein** - Leaf Nodes sind **TopicFields**.

**Struktur:**
```
Root (Level 0)
  ├── Software Development (Level 1)
  │   ├── Full Stack Development (Level 2, Leaf) → TopicField
  │   ├── Backend Development (Level 2, Leaf) → TopicField
  │   └── Frontend Development (Level 2, Leaf) → TopicField
  └── Data & Analytics (Level 1)
      ├── Data Science (Level 2, Leaf) → TopicField
      └── Machine Learning (Level 2, Leaf) → TopicField
```

**Anforderungen:**
1. **Hierarchische Struktur**: CareerTreeNodes mit Parent-Child Beziehungen
2. **Leaf Nodes = TopicFields**: Die Endknoten (Leaf Nodes) sind **TopicFields**
3. **Pro Studiengang**: Jeder Studiengang hat seinen eigenen Themenfelder-Tree

**Aktuelle Implementierung:**
- ✅ Bereits als hierarchischer Career Tree implementiert (CareerTreeNode mit CareerTreeRelationship)
- Leaf Nodes sind mit TopicFields verknüpft (`topic_field_id`)

**Wo erstellt:**
- **MVP:** Statisch im Seed-Script (`scripts/seed_database.py`)
- **Production:** Admin-Interface oder Seed-Script

**Wie erstellt:**

#### Schritt 1: Career Tree Nodes erstellen
```python
# scripts/seed_database.py

# Root Node
root_node = CareerTreeNode(
    name="Karrierewege",
    description="Alle verfügbaren Karrierewege",
    study_program_id=study_program.id,
    is_leaf=False,
    level=0,
)

# Level 1: Hauptkategorien
node_software = CareerTreeNode(
    name="Software Development",
    description="Entwicklung von Software-Anwendungen",
    study_program_id=study_program.id,
    is_leaf=False,
    level=1,
)

# Level 2: Leaf Nodes (Endknoten mit TopicField)
node_fullstack = CareerTreeNode(
    name="Full Stack Development",
    description="Frontend und Backend Entwicklung",
    study_program_id=study_program.id,
    topic_field_id=topic_fullstack.id,  # Verknüpfung zum TopicField
    is_leaf=True,
    level=2,
)
```

#### Schritt 2: Graph-Beziehungen erstellen
```python
# Career Tree Relationships (Graph-Edge)
relationships = [
    CareerTreeRelationship(parent_id=root_node.id, child_id=node_software.id),
    CareerTreeRelationship(parent_id=node_software.id, child_id=node_fullstack.id),
]
db.add_all(relationships)
```

**Wann aktualisiert:**
- Initial Setup pro Studiengang
- Manuell durch Admin (später)
- Optional: Dynamisch basierend auf User Questions (Phase 3)

**Admin-Endpunkte (Phase 2):**
```python
# api/routers/admin.py (optional für Production)

POST /api/v1/admin/study-programs/{id}/career-tree/nodes
PUT /api/v1/admin/career-tree/nodes/{id}
DELETE /api/v1/admin/career-tree/nodes/{id}
POST /api/v1/admin/career-tree/relationships
```

**Datenstruktur:**
- `CareerTreeNode`: Knoten im Graph
- `CareerTreeRelationship`: Edge zwischen Parent und Child
- Jeder Studiengang hat seinen eigenen Career Tree
- Leaf Nodes (Endknoten) sind mit TopicFields verknüpft

**Wie wird der Graph zur Laufzeit aufgebaut?**

Der Career Tree wird **zur Laufzeit aus der Datenbank geladen** und als hierarchische Struktur aufgebaut:

```python
# api/services/career_service.py

class CareerService:
    def get_career_tree(self, study_program_id: int, db: Session) -> CareerTreeResponse:
        """
        Lädt Career Tree für Studiengang aus DB und baut hierarchische Struktur auf.
        """
        # 1. Alle Nodes für diesen Studiengang laden
        nodes = db.query(CareerTreeNode).filter(
            CareerTreeNode.study_program_id == study_program_id
        ).all()
        
        # 2. Alle Relationships laden
        node_ids = [n.id for n in nodes]
        relationships = db.query(CareerTreeRelationship).filter(
            CareerTreeRelationship.parent_id.in_(node_ids)
        ).all()
        
        # 3. Graph-Struktur aufbauen (Nodes nach Parent-Child organisieren)
        node_map = {node.id: node for node in nodes}
        children_map = {}  # parent_id -> [child_nodes]
        
        for rel in relationships:
            if rel.parent_id not in children_map:
                children_map[rel.parent_id] = []
            children_map[rel.parent_id].append(node_map[rel.child_id])
        
        # 4. Root Node finden (Level 0, keine Parent-Relationship)
        root_nodes = [n for n in nodes if n.level == 0]
        root = root_nodes[0] if root_nodes else None
        
        # 5. Rekursiv hierarchische Struktur aufbauen
        def build_tree(node: CareerTreeNode) -> Dict:
            children = children_map.get(node.id, [])
            return {
                "id": node.id,
                "name": node.name,
                "description": node.description,
                "is_leaf": node.is_leaf,
                "level": node.level,
                "topic_field": {
                    "id": node.topic_field.id,
                    "name": node.topic_field.name,
                    "description": node.topic_field.description
                } if node.topic_field else None,
                "children": [build_tree(child) for child in children]
            }
        
        # 6. Von Root aus rekursiv aufbauen
        if root:
            tree_structure = build_tree(root)
        else:
            tree_structure = None
        
        return CareerTreeResponse(
            study_program_id=study_program_id,
            nodes=tree_structure
        )
```

**API-Endpoint:**
```
GET /api/v1/study-programs/{study_program_id}/career-tree
```

**Response-Format:**
```json
{
  "study_program_id": 1,
  "nodes": {
    "id": 1,
    "name": "Karrierewege",
    "level": 0,
    "is_leaf": false,
    "children": [
      {
        "id": 2,
        "name": "Software Development",
        "level": 1,
        "is_leaf": false,
        "children": [
          {
            "id": 3,
            "name": "Full Stack Development",
            "level": 2,
            "is_leaf": true,
            "topic_field": {
              "id": 1,
              "name": "Full Stack Development",
              "description": "..."
            },
            "children": []
          }
        ]
      }
    ]
  }
}
```

**Wann wird der Career Tree geladen?**
- Beim Onboarding: User wählt Studiengang → Frontend lädt Career Tree
- Bei Profile-View: Zeigt aktuellen Career Tree basierend auf User's Studiengang

---

### 3. Roadmap Tree (Hierarchische Karrierewege)

**Was:** Hierarchischer Graph/Tree, der den Karriereweg zum Zielberuf zeigt. **Leaf Nodes = Berufe (Ziel)**.

**WICHTIG:** Muss hierarchisch strukturiert sein und dynamisch anpassbar!

**Struktur (Beispiel):**
```
Roadmap für "Full Stack Development"
│
├── Semester 3 (Parent Node)
│   ├── Modul: Web Development (Child)
│   ├── Modul: Datenbanken (Child)
│   └── Skill: HTML/CSS/JS (Child)
│
├── Semester 4 (Parent Node)
│   ├── Kurs: React Fundamentals (Child)
│   ├── Projekt: Portfolio Website (Child)
│   └── Skill: Frontend Frameworks (Child)
│
├── Semesterferien (Parent Node)
│   ├── Praktikum: Frontend Developer (Child)
│   └── Bootcamp: Full Stack (Child)
│
└── Ziel: Full Stack Developer ⭐ (Leaf Node = Beruf)
    ├── Voraussetzungen:
    │   ├── Frontend Skills (Child)
    │   ├── Backend Skills (Child)
    │   └── DevOps Basics (Child)
    └── Empfehlungen:
        ├── Portfolio mit 3+ Projekten
        └── Zertifikate
```

**Anforderungen:**
1. **Hierarchische Struktur**: RoadmapItems müssen Parent-Child Beziehungen haben
2. **Leaf Nodes = Berufe**: Die Endknoten (Leaf Nodes) sind **Berufe** (z.B. "Full Stack Developer", "Data Scientist")
3. **Dynamische Anpassung**: Der Tree kann basierend auf User-Fragen angepasst werden
   - User beantwortet Fragen → Tree wird neu strukturiert
   - Neue Pfade können hinzugefügt/entfernt werden
   - Leaf Nodes (Berufe) können sich ändern

**Aktuelle Datenstruktur:** ⚠️ **FEHLT - RoadmapItems sind aktuell als flache Liste strukturiert!**

**Erforderliche Änderungen:**
1. `RoadmapItem` Model erweitern:
   - `parent_id`: Optional ForeignKey zu `RoadmapItem` (für Parent-Child Beziehungen)
   - `is_leaf`: Boolean (ist Endknoten = Beruf?)
   - `is_career_goal`: Boolean (ist dieser Item ein Beruf?)
   - `level`: Integer (Tiefe im Tree)

2. `RoadmapItemRelationship` Tabelle (optional, ähnlich wie CareerTreeRelationship):
   - Für komplexere Graph-Strukturen (wenn ein Item mehrere Parents haben kann)

3. Service-Logik erweitern:
   - Tree-Aufbau aus Parent-Child Beziehungen
   - Dynamische Anpassung basierend auf User Questions

**Wie erstellt - Flow:**

```
1. User wählt TopicField im Career Tree
   │
   ▼
2. PUT /api/v1/users/me/profile/topic-field
   │
   ▼
3. RoadmapService.get_roadmap(topic_field_id)
   → Prüft ob Roadmap bereits existiert
   │
   ├─→ JA: Gibt vorhandene Roadmap zurück
   │
   └─→ NEIN:
       │
       ▼
4. POST /api/v1/topic-fields/{id}/roadmap/generate
   │
   ▼
5. RoadmapService.generate_roadmap()
   │
   ├─→ User-Profile laden (Semester, Skills)
   ├─→ Studiengang & Module laden
   ├─→ TopicField-Daten laden
   │
   ▼
6. Prompt konstruieren (roadmap_prompts.py)
   - User-Kontext (Semester, Skills)
   - Verfügbare Module
   - Themenfeld-Informationen
   │
   ▼
7. LLMService.generate_roadmap(prompt, schema)
   - AWS Bedrock API Call (Claude 3 Sonnet)
   - Strukturierte JSON-Response
   │
   ▼
8. Response validieren & parsen (Pydantic)
   │
   ▼
9. Roadmap & RoadmapItems in DB speichern
   - Roadmap (1 Eintrag)
   - RoadmapItems (N Einträge)
   │
   ▼
10. Roadmap zurückgeben
```

**Code-Beispiel:**

```python
# api/services/roadmap_service.py

class RoadmapService:
    def generate_roadmap(
        self,
        user_profile: UserProfile,
        topic_field: TopicField,
        study_program: StudyProgram,
        db: Session
    ) -> Roadmap:
        # 1. Daten sammeln
        modules = db.query(Module).filter(
            Module.study_program_id == study_program.id
        ).all()
        
        # 2. Prompt konstruieren
        prompt = generate_roadmap_prompt(
            study_program=study_program,
            user_profile=user_profile,
            topic_field=topic_field,
            available_modules=modules
        )
        
        # 3. LLM aufrufen
        llm_response = self.llm_service.generate_roadmap(
            prompt=prompt,
            response_schema=ROADMAP_JSON_SCHEMA
        )
        
        # 4. Validieren
        roadmap_data = RoadmapCreateResponse(**llm_response)
        
        # 5. In DB speichern
        roadmap = Roadmap(
            topic_field_id=topic_field.id,
            name=roadmap_data.name,
            description=roadmap_data.description
        )
        db.add(roadmap)
        db.flush()
        
        for item_data in roadmap_data.items:
            roadmap_item = RoadmapItem(
                roadmap_id=roadmap.id,
                item_type=item_data.item_type,
                title=item_data.title,
                description=item_data.description,
                semester=item_data.semester,
                is_semester_break=item_data.is_semester_break,
                order=item_data.order,
                module_id=item_data.module_id,
                is_important=item_data.is_important
            )
            db.add(roadmap_item)
        
        db.commit()
        return roadmap
```

**Wann erstellt:**
- Bei erster User-Auswahl eines TopicFields
- Optional: Regenerierung auf User-Anfrage

**Caching:**
- Roadmaps werden in DB gespeichert (persistent)
- Optional: Redis-Cache für schnelleren Zugriff
- Gleiche User-Inputs könnten gleiche Roadmaps generieren

**Personalisierung:**
- Roadmap ist abhängig von:
  - Aktuellem Semester
  - Bereits vorhandenen Skills
  - Verfügbaren Modulen des Studiengangs
  - Gewähltem TopicField

---

### 4. Service-Integration

**Career Service** (`api/services/career_service.py`):
```python
class CareerService:
    def get_career_tree(self, study_program_id: int, db: Session) -> CareerTreeResponse:
        """
        Gibt Themenfelder-Tree für Studiengang zurück (hierarchische Struktur).
        Leaf Nodes = TopicFields
        """
        # Lädt CareerTreeNodes + Relationships aus DB
        # Baut hierarchische Struktur auf
        # Leaf Nodes enthalten TopicField-Informationen
        pass
    
    def get_topic_fields(self, study_program_id: int, db: Session) -> List[TopicField]:
        """
        Hilfsmethode: Gibt alle TopicFields für Studiengang zurück (aus Career Tree Leaf Nodes).
        """
        # Lädt alle Leaf Nodes des Career Trees
        # Extrahiert TopicFields
        pass
```

**Roadmap Service** (`api/services/roadmap_service.py`):
```python
class RoadmapService:
    def get_roadmap(self, topic_field_id: int, db: Session) -> Optional[Roadmap]:
        """Prüft ob Roadmap existiert."""
        return db.query(Roadmap).filter(
            Roadmap.topic_field_id == topic_field_id
        ).first()
    
    def get_roadmap_tree(self, roadmap_id: int, db: Session) -> RoadmapTreeResponse:
        """
        Baut hierarchischen Roadmap Tree auf.
        Leaf Nodes = Berufe (is_career_goal = True)
        """
        # 1. Alle RoadmapItems für Roadmap laden
        items = db.query(RoadmapItem).filter(
            RoadmapItem.roadmap_id == roadmap_id
        ).all()
        
        # 2. Tree-Struktur aufbauen (Parent-Child)
        root_items = [item for item in items if item.parent_id is None]
        # Rekursiv Tree aufbauen...
        
        return RoadmapTreeResponse(
            roadmap_id=roadmap_id,
            tree=tree_structure,
            career_goals=[item for item in items if item.is_career_goal]
        )
    
    def generate_roadmap(...) -> Roadmap:
        """
        Generiert neue Roadmap durch LLM.
        LLM muss hierarchische Struktur generieren mit Leaf Nodes = Berufe.
        """
        # LLM Prompt muss explizit anweisen:
        # - Hierarchische Struktur zu generieren
        # - Leaf Nodes als Berufe zu definieren
        # - Parent-Child Beziehungen zu erstellen
        pass
    
    def adapt_roadmap_tree(
        self,
        roadmap_id: int,
        user_questions: List[UserQuestion],
        db: Session
    ) -> Roadmap:
        """
        Passt Roadmap Tree dynamisch an basierend auf User-Fragen.
        - Analysiert User-Antworten
        - Strukturiert Tree neu
        - Aktualisiert Leaf Nodes (Berufe)
        """
        # 1. User Questions analysieren
        # 2. Aktuelle Roadmap laden
        # 3. LLM aufrufen mit: Roadmap + User Questions → Neue Struktur
        # 4. Tree anpassen (Items löschen/hinzufügen/neu strukturieren)
        # 5. Speichern
        pass
```

---

### 5. Admin-Management (Optional für Production)

Für Production könnte ein Admin-Interface nötig sein:

**Career Tree Management:**
- UI zum Erstellen/Bearbeiten von Career Trees
- Visual Editor für Graph-Struktur
- Drag & Drop für Node-Positionen

**TopicField Management:**
- CRUD für TopicFields
- System-Prompt Editor

**Roadmap Template Management:**
- Vordefinierte Roadmap-Templates (optional)
- Fallback-Roadmaps (falls LLM fehlschlägt)

---

## Offene Entscheidungen

1. **AWS Region:** `eu-central-1` (Deutschland) empfohlen
2. **Chat Streaming:** Soll Chat-Response gestreamt werden? (WebSocket nötig)
3. **Roadmap Caching:** Wie lange cachen? (24h empfohlen)
4. **Background Jobs:** Für MVP synchron, später async?
5. **Rate Limiting:** Wie viele Requests pro User/Minute?
6. **Career Tree Regenerierung:** Sollen Career Trees durch LLM generiert werden? (Aktuell: Statisch)
7. **Roadmap Sharing:** Können User ihre Roadmaps teilen/vergleichen?

---

## Nächste Schritte

1. Requirements.txt erweitern (boto3, pydantic, python-jose, passlib, etc.)
2. Core Configuration erstellen (`api/core/config.py`)
3. Security Module implementieren (`api/core/security.py`)
4. LLM Service implementieren (`api/services/llm_service.py`)
5. Prompt Templates erstellen (`api/prompts/`)
6. Services implementieren (Auth, User, Career, Roadmap, Chat)
7. Router implementieren (alle Endpoints)
8. Pydantic Schemas erstellen (`api/models/`)
9. Error Handling & Middleware
10. Testing Setup

---

**Dokument erstellt:** 2025  
**Nächste Review:** Nach MVP Implementation

