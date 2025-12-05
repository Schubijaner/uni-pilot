# Datenbankschema – Uni Pilot

## Übersicht

Dieses Dokument beschreibt das vollständige Datenbankschema für die Uni Pilot App, eine Karriereorientierungs-App für Studierende. Das Schema unterstützt:

- **User Management**: Registrierung, Login und Profilverwaltung
- **Onboarding**: Erfassung von Universität, Studiengang, Semester und Modulen
- **Career Tree**: Hierarchische Struktur zur Darstellung von Karrierepfaden und Themenfeldern
- **Roadmaps**: Zeitlich strukturierte Lernpfade mit Semester- und Semesterferien-Planung
- **Chat-Funktionalität**: Pro Themenfeld ein eigener Chat mit System-Prompts
- **Progress Tracking**: Verfolgung des Fortschritts bei Modulen und Roadmap-Items

---

## Entitäten

### 1. User (Nutzer)

Basis-Entität für alle Nutzer der App.

| Attribut | Typ | Beschreibung | Constraints |
|----------|-----|--------------|-------------|
| `id` | Integer | Primärschlüssel | PK, Auto-Increment |
| `email` | String(255) | E-Mail-Adresse | Unique, Not Null, Index |
| `password_hash` | String(255) | Gehashtes Passwort | Not Null |
| `first_name` | String(100) | Vorname | Not Null |
| `last_name` | String(100) | Nachname | Not Null |
| `created_at` | DateTime | Erstellungsdatum | Default: UTC Now |
| `updated_at` | DateTime | Letzte Aktualisierung | Default: UTC Now, On Update |

**Relationen:**
- One-to-One: `UserProfile`
- One-to-Many: `ChatSession`
- One-to-Many: `UserQuestion`
- Many-to-Many: `Module` (via `user_module_progress`)
- Many-to-Many: `RoadmapItem` (via `user_roadmap_items`)

---

### 2. UserProfile (Nutzerprofil)

Erweiterte Profilinformationen eines Nutzers.

| Attribut | Typ | Beschreibung | Constraints |
|----------|-----|--------------|-------------|
| `id` | Integer | Primärschlüssel | PK, Auto-Increment |
| `user_id` | Integer | Referenz zu User | FK, Unique, Not Null |
| `university_id` | Integer | Referenz zu University | FK, Nullable |
| `study_program_id` | Integer | Referenz zu StudyProgram | FK, Nullable |
| `current_semester` | Integer | Aktuelles Semester | Nullable |
| `skills` | Text | Skills (JSON oder komma-separiert) | Nullable |
| `selected_topic_field_id` | Integer | Ausgewähltes Themenfeld | FK, Nullable |
| `created_at` | DateTime | Erstellungsdatum | Default: UTC Now |
| `updated_at` | DateTime | Letzte Aktualisierung | Default: UTC Now, On Update |

**Relationen:**
- Many-to-One: `User` (via `user_id`)
- Many-to-One: `University` (via `university_id`)
- Many-to-One: `StudyProgram` (via `study_program_id`)
- Many-to-One: `TopicField` (via `selected_topic_field_id`)

---

### 3. University (Universität)

Universitäten, die in der App unterstützt werden.

| Attribut | Typ | Beschreibung | Constraints |
|----------|-----|--------------|-------------|
| `id` | Integer | Primärschlüssel | PK, Auto-Increment |
| `name` | String(255) | Name der Universität | Unique, Not Null |
| `abbreviation` | String(50) | Abkürzung (z.B. "TUM") | Nullable |
| `created_at` | DateTime | Erstellungsdatum | Default: UTC Now |

**Relationen:**
- One-to-Many: `UserProfile`
- One-to-Many: `StudyProgram`

---

### 4. StudyProgram (Studiengang)

Studiengänge, die an Universitäten angeboten werden.

| Attribut | Typ | Beschreibung | Constraints |
|----------|-----|--------------|-------------|
| `id` | Integer | Primärschlüssel | PK, Auto-Increment |
| `name` | String(255) | Name des Studiengangs | Not Null |
| `university_id` | Integer | Referenz zu University | FK, Not Null |
| `degree_type` | String(50) | Abschlusstyp (z.B. "Bachelor", "Master") | Nullable |
| `created_at` | DateTime | Erstellungsdatum | Default: UTC Now |

**Relationen:**
- Many-to-One: `University` (via `university_id`)
- One-to-Many: `UserProfile`
- One-to-Many: `Module`
- One-to-Many: `CareerTreeNode`

---

### 5. Module (Modul)

Module aus dem Modulhandbuch (Pflicht- und Wahlmodule).

| Attribut | Typ | Beschreibung | Constraints |
|----------|-----|--------------|-------------|
| `id` | Integer | Primärschlüssel | PK, Auto-Increment |
| `name` | String(255) | Name des Moduls | Not Null |
| `description` | Text | Beschreibung des Moduls | Nullable |
| `module_type` | Enum | Typ: `REQUIRED` oder `ELECTIVE` | Not Null |
| `study_program_id` | Integer | Referenz zu StudyProgram | FK, Not Null |
| `semester` | Integer | Empfohlenes Semester | Nullable |
| `created_at` | DateTime | Erstellungsdatum | Default: UTC Now |

**Enum: ModuleType**
- `REQUIRED`: Pflichtmodul
- `ELECTIVE`: Wahlmodul

**Relationen:**
- Many-to-One: `StudyProgram` (via `study_program_id`)
- Many-to-Many: `User` (via `user_module_progress`)
- One-to-Many: `RoadmapItem` (optional, wenn Modul in Roadmap enthalten)
- One-to-Many: `ModuleImport` (Import-Historie)

---

### 6. TopicField (Themenfeld)

Karriere-Themenfelder (z.B. Full Stack Development, Data Science).

| Attribut | Typ | Beschreibung | Constraints |
|----------|-----|--------------|-------------|
| `id` | Integer | Primärschlüssel | PK, Auto-Increment |
| `name` | String(255) | Name des Themenfelds | Not Null |
| `description` | Text | Beschreibung | Nullable |
| `system_prompt` | Text | System-Prompt für Chat-Funktionalität | Nullable |
| `created_at` | DateTime | Erstellungsdatum | Default: UTC Now |

**Relationen:**
- One-to-Many: `CareerTreeNode` (Endknoten des Career Trees)
- One-to-Many: `Roadmap`
- One-to-Many: `ChatSession`
- One-to-Many: `Recommendation`

---

### 7. CareerTreeNode (Karrierebaum-Knoten)

Knoten im hierarchischen Karrierebaum.

| Attribut | Typ | Beschreibung | Constraints |
|----------|-----|--------------|-------------|
| `id` | Integer | Primärschlüssel | PK, Auto-Increment |
| `name` | String(255) | Name des Knotens | Not Null |
| `description` | Text | Beschreibung | Nullable |
| `study_program_id` | Integer | Referenz zu StudyProgram | FK, Not Null |
| `topic_field_id` | Integer | Referenz zu TopicField (wenn Endknoten) | FK, Nullable |
| `is_leaf` | Boolean | Ist Endknoten (Themenfeld)? | Default: False |
| `level` | Integer | Tiefe im Baum | Default: 0 |
| `created_at` | DateTime | Erstellungsdatum | Default: UTC Now |

**Relationen:**
- Many-to-One: `StudyProgram` (via `study_program_id`)
- Many-to-One: `TopicField` (via `topic_field_id`, wenn `is_leaf = True`)
- Many-to-Many: `CareerTreeNode` (selbstreferenzierend, via `career_tree_relationships`)

**Hinweis:** Der Career Tree ist studiengang-spezifisch. Endknoten (`is_leaf = True`) verweisen auf ein `TopicField`.

---

### 8. Roadmap (Roadmap)

Roadmap für ein spezifisches Themenfeld.

| Attribut | Typ | Beschreibung | Constraints |
|----------|-----|--------------|-------------|
| `id` | Integer | Primärschlüssel | PK, Auto-Increment |
| `topic_field_id` | Integer | Referenz zu TopicField | FK, Not Null |
| `name` | String(255) | Name der Roadmap | Not Null |
| `description` | Text | Beschreibung | Nullable |
| `created_at` | DateTime | Erstellungsdatum | Default: UTC Now |
| `updated_at` | DateTime | Letzte Aktualisierung | Default: UTC Now, On Update |

**Relationen:**
- Many-to-One: `TopicField` (via `topic_field_id`)
- One-to-Many: `RoadmapItem`

---

### 9. RoadmapItem (Roadmap-Eintrag)

Einzelner Eintrag in einer Roadmap (zeitlich strukturiert).

| Attribut | Typ | Beschreibung | Constraints |
|----------|-----|--------------|-------------|
| `id` | Integer | Primärschlüssel | PK, Auto-Increment |
| `roadmap_id` | Integer | Referenz zu Roadmap | FK, Not Null |
| `item_type` | Enum | Typ des Eintrags | Not Null |
| `title` | String(255) | Titel | Not Null |
| `description` | Text | Beschreibung | Nullable |
| `semester` | Integer | Semester (wenn während Semester) | Nullable |
| `is_semester_break` | Boolean | In Semesterferien? | Default: False |
| `order` | Integer | Reihenfolge in Roadmap | Default: 0 |
| `module_id` | Integer | Referenz zu Module (optional) | FK, Nullable |
| `is_important` | Boolean | Besonders wichtig? | Default: False |
| `created_at` | DateTime | Erstellungsdatum | Default: UTC Now |

**Enum: RoadmapItemType**
- `COURSE`: Kurs
- `MODULE`: Modul
- `PROJECT`: Projekt
- `SKILL`: Skill
- `BOOK`: Buch
- `CERTIFICATE`: Zertifikat
- `INTERNSHIP`: Praktikum
- `BOOTCAMP`: Bootcamp

**Relationen:**
- Many-to-One: `Roadmap` (via `roadmap_id`)
- Many-to-One: `Module` (via `module_id`, optional)
- Many-to-Many: `User` (via `user_roadmap_items`)

**Hinweis:** Zeitliche Strukturierung erfolgt über `semester` (während Semester) und `is_semester_break` (Semesterferien).

---

### 10. Recommendation (Empfehlung)

Empfehlungen für Kurse, Bücher, Projekte, Skills etc.

| Attribut | Typ | Beschreibung | Constraints |
|----------|-----|--------------|-------------|
| `id` | Integer | Primärschlüssel | PK, Auto-Increment |
| `roadmap_item_id` | Integer | Referenz zu RoadmapItem (optional) | FK, Nullable |
| `topic_field_id` | Integer | Referenz zu TopicField (optional) | FK, Nullable |
| `title` | String(255) | Titel | Not Null |
| `description` | Text | Beschreibung | Nullable |
| `recommendation_type` | Enum | Typ (wie RoadmapItemType) | Not Null |
| `url` | String(500) | Link (optional) | Nullable |
| `created_at` | DateTime | Erstellungsdatum | Default: UTC Now |

**Relationen:**
- Many-to-One: `RoadmapItem` (via `roadmap_item_id`, optional)
- Many-to-One: `TopicField` (via `topic_field_id`, optional)

**Hinweis:** Empfehlungen können entweder einem RoadmapItem oder einem TopicField zugeordnet sein.

---

### 11. ChatSession (Chat-Session)

Chat-Session für ein spezifisches Themenfeld.

| Attribut | Typ | Beschreibung | Constraints |
|----------|-----|--------------|-------------|
| `id` | Integer | Primärschlüssel | PK, Auto-Increment |
| `user_id` | Integer | Referenz zu User | FK, Not Null |
| `topic_field_id` | Integer | Referenz zu TopicField | FK, Not Null |
| `created_at` | DateTime | Erstellungsdatum | Default: UTC Now |
| `updated_at` | DateTime | Letzte Aktualisierung | Default: UTC Now, On Update |

**Relationen:**
- Many-to-One: `User` (via `user_id`)
- Many-to-One: `TopicField` (via `topic_field_id`)
- One-to-Many: `ChatMessage`

**Hinweis:** Jedes Themenfeld hat einen eigenen Chat mit einem System-Prompt aus `TopicField.system_prompt`.

---

### 12. ChatMessage (Chat-Nachricht)

Einzelne Nachricht in einer Chat-Session.

| Attribut | Typ | Beschreibung | Constraints |
|----------|-----|--------------|-------------|
| `id` | Integer | Primärschlüssel | PK, Auto-Increment |
| `session_id` | Integer | Referenz zu ChatSession | FK, Not Null |
| `role` | String(20) | Rolle: `user` oder `assistant` | Not Null |
| `content` | Text | Nachrichteninhalt | Not Null |
| `created_at` | DateTime | Erstellungsdatum | Default: UTC Now |

**Relationen:**
- Many-to-One: `ChatSession` (via `session_id`)

---

### 13. UserQuestion (User-Fragen)

Fragen, die der User beantwortet hat, um den Career Tree dynamisch anzupassen.

| Attribut | Typ | Beschreibung | Constraints |
|----------|-----|--------------|-------------|
| `id` | Integer | Primärschlüssel | PK, Auto-Increment |
| `user_id` | Integer | Referenz zu User | FK, Not Null |
| `question_text` | Text | Frage-Text | Not Null |
| `answer` | Boolean | Antwort: `True` (Ja) oder `False` (Nein) | Not Null |
| `career_tree_node_id` | Integer | Referenz zu CareerTreeNode (kontextbezogen) | FK, Nullable |
| `created_at` | DateTime | Erstellungsdatum | Default: UTC Now |

**Relationen:**
- Many-to-One: `User` (via `user_id`)
- Many-to-One: `CareerTreeNode` (via `career_tree_node_id`, optional)

**Hinweis:** Speichert Ja/Nein-Fragen, die der User während des Onboardings oder der Career Tree Navigation beantwortet. Die Antworten können verwendet werden, um den Career Tree dynamisch anzupassen und die Roadmap zu aktualisieren.

---

### 14. ModuleImport (Modul-Import)

Historie und Metadaten für den Import von Modulen aus Modulhandbüchern.

| Attribut | Typ | Beschreibung | Constraints |
|----------|-----|--------------|-------------|
| `id` | Integer | Primärschlüssel | PK, Auto-Increment |
| `module_id` | Integer | Referenz zu Module | FK, Not Null |
| `import_source` | String(255) | Quelle (z.B. "Modulhandbuch TUM 2024") | Not Null |
| `import_data` | Text | Rohe Import-Daten (JSON) | Nullable |
| `import_status` | String(50) | Status: `success`, `partial`, `failed` | Not Null |
| `imported_at` | DateTime | Import-Zeitpunkt | Default: UTC Now |
| `imported_by` | String(100) | Wer hat importiert (User oder System) | Nullable |

**Relationen:**
- Many-to-One: `Module` (via `module_id`)

**Hinweis:** Speichert Informationen über den Import von Modulen aus Modulhandbüchern. Ermöglicht Nachverfolgbarkeit und mögliche Re-Import-Funktionalität.

---

## Zwischentabellen (Many-to-Many)

### user_module_progress

Verfolgt den Fortschritt eines Users bei Modulen.

| Attribut | Typ | Beschreibung | Constraints |
|----------|-----|--------------|-------------|
| `user_id` | Integer | Referenz zu User | PK, FK |
| `module_id` | Integer | Referenz zu Module | PK, FK |
| `completed` | Boolean | Abgeschlossen? | Default: False |
| `grade` | String(10) | Note (optional) | Nullable |
| `completed_at` | DateTime | Abschlussdatum | Nullable |

---

### user_roadmap_items

Verfolgt den Fortschritt eines Users bei Roadmap-Items.

| Attribut | Typ | Beschreibung | Constraints |
|----------|-----|--------------|-------------|
| `user_id` | Integer | Referenz zu User | PK, FK |
| `roadmap_item_id` | Integer | Referenz zu RoadmapItem | PK, FK |
| `completed` | Boolean | Abgeschlossen? | Default: False |
| `completed_at` | DateTime | Abschlussdatum | Nullable |
| `notes` | Text | Notizen des Users | Nullable |

---

### career_tree_relationships

Selbstreferenzielle Beziehung für Career Tree Hierarchie.

| Attribut | Typ | Beschreibung | Constraints |
|----------|-----|--------------|-------------|
| `parent_id` | Integer | Referenz zu CareerTreeNode (Parent) | PK, FK |
| `child_id` | Integer | Referenz zu CareerTreeNode (Child) | PK, FK |

**Hinweis:** Ermöglicht hierarchische Struktur des Career Trees.

---

## Relationen-Übersicht

### One-to-One Beziehungen

```
User ──(1:1)── UserProfile
```

### One-to-Many Beziehungen

```
University ──(1:N)── StudyProgram
University ──(1:N)── UserProfile

StudyProgram ──(1:N)── UserProfile
StudyProgram ──(1:N)── Module
StudyProgram ──(1:N)── CareerTreeNode

User ──(1:N)── UserProfile
User ──(1:N)── ChatSession
User ──(1:N)── UserQuestion

TopicField ──(1:N)── CareerTreeNode (Endknoten)
TopicField ──(1:N)── Roadmap
TopicField ──(1:N)── ChatSession
TopicField ──(1:N)── Recommendation

Roadmap ──(1:N)── RoadmapItem

ChatSession ──(1:N)── ChatMessage

RoadmapItem ──(1:N)── Recommendation

Module ──(1:N)── RoadmapItem (optional)
Module ──(1:N)── ModuleImport

CareerTreeNode ──(1:N)── UserQuestion (optional)
```

### Many-to-Many Beziehungen

```
User ──(N:M)── Module (via user_module_progress)
User ──(N:M)── RoadmapItem (via user_roadmap_items)
CareerTreeNode ──(N:M)── CareerTreeNode (via career_tree_relationships)
```

---

## Visuelle Darstellung (ER-Diagramm-ähnlich)

```
┌─────────────┐
│    User     │
│─────────────│
│ id (PK)     │
│ email       │◄──┐
│ password    │   │
│ first_name  │   │
│ last_name   │   │
└─────────────┘   │
      │           │
      │ 1:1       │
      ▼           │
┌─────────────┐  │
│UserProfile  │  │
│─────────────│  │
│ id (PK)     │  │
│ user_id (FK)├──┘
│ university  │
│ study_prog  │
│ semester    │
│ skills      │
│ topic_field │
└─────────────┘
      │
      │ N:1
      ▼
┌─────────────┐
│ University  │
│─────────────│
│ id (PK)     │
│ name        │
└─────────────┘
      │
      │ 1:N
      ▼
┌─────────────┐
│StudyProgram │
│─────────────│
│ id (PK)     │
│ university  │
│ name        │
└─────────────┘
      │
      ├──(1:N)──► Module
      │
      └──(1:N)──► CareerTreeNode
                      │
                      │ (hierarchisch)
                      ▼
                  ┌─────────────┐
                  │TopicField   │
                  │─────────────│
                  │ id (PK)     │
                  │ name        │
                  │ system_prompt│
                  └─────────────┘
                      │
                      ├──(1:N)──► Roadmap ──(1:N)──► RoadmapItem
                      │
                      ├──(1:N)──► ChatSession ──(1:N)──► ChatMessage
                      │
                      └──(1:N)──► Recommendation

User ──(1:N)──► UserQuestion ──(N:1, optional)──► CareerTreeNode

Module ──(1:N)──► ModuleImport
```

**Erweiterte Darstellung:**

```
┌─────────────┐
│    User     │
│─────────────│
│ id (PK)     │
└─────────────┘
      │
      ├──(1:N)──► ┌──────────────┐
      │           │UserQuestion  │
      │           │──────────────│
      │           │ id (PK)      │
      │           │ user_id (FK) │
      │           │ question_text│
      │           │ answer (bool)│
      │           │ node_id (FK) │
      │           └──────────────┘
      │                    │
      │                    │ N:1 (optional)
      │                    ▼
      │           ┌──────────────┐
      │           │CareerTreeNode│
      │           └──────────────┘
      │
      └──(1:N)──► ┌──────────────┐
                  │ChatSession   │
                  └──────────────┘

┌─────────────┐
│   Module    │
│─────────────│
│ id (PK)     │
└─────────────┘
      │
      └──(1:N)──► ┌──────────────┐
                  │ModuleImport  │
                  │──────────────│
                  │ id (PK)      │
                  │ module_id(FK)│
                  │ import_source│
                  │ import_status│
                  │ imported_at  │
                  └──────────────┘
```

---

## Design-Entscheidungen

### 1. Trennung von User und UserProfile
- **Grund:** Bessere Trennung von Authentifizierungsdaten (User) und Profildaten (UserProfile)
- **Vorteil:** Flexibilität bei Erweiterungen, klarere Datenstruktur

### 2. Career Tree als selbstreferenzielle Struktur
- **Grund:** Ermöglicht flexible, hierarchische Darstellung von Karrierepfaden
- **Implementierung:** Via `career_tree_relationships` Zwischentabelle
- **Endknoten:** Verweisen auf `TopicField` (`is_leaf = True`)

### 3. Zeitliche Strukturierung in RoadmapItem
- **Semester:** `semester` Feld für Items während des Semesters
- **Semesterferien:** `is_semester_break` Flag für Items in den Ferien
- **Flexibilität:** Beide Felder können kombiniert werden

### 4. Chat pro Themenfeld
- **Grund:** Jedes Themenfeld hat spezifische System-Prompts
- **Implementierung:** `ChatSession` verknüpft User + TopicField
- **System-Prompt:** Gespeichert in `TopicField.system_prompt`

### 5. Progress Tracking via Zwischentabellen
- **Module Progress:** `user_module_progress` mit Note und Abschlussdatum
- **Roadmap Progress:** `user_roadmap_items` mit Notizen
- **Vorteil:** Zusätzliche Metadaten (Grade, Notes) pro Beziehung

### 6. Empfehlungen flexibel zuordenbar
- **Option 1:** Direkt zu `RoadmapItem` (spezifische Empfehlung)
- **Option 2:** Zu `TopicField` (allgemeine Empfehlung)
- **Beide optional:** Ermöglicht freie Empfehlungen

### 7. Dynamische Career Tree Anpassung via UserQuestion
- **Grund:** User-Antworten auf Ja/Nein-Fragen sollen den Career Tree anpassen
- **Implementierung:** `UserQuestion` speichert Frage, Antwort und optionalen Career Tree Kontext
- **Verwendung:** Antworten können verwendet werden, um Career Tree Navigation zu beeinflussen und Roadmaps anzupassen

### 8. Module-Import Tracking
- **Grund:** Nachverfolgbarkeit von Modul-Imports aus Modulhandbüchern
- **Implementierung:** `ModuleImport` speichert Quelle, Status und Metadaten
- **Vorteil:** Ermöglicht Re-Import, Fehlerbehandlung und Audit-Trail

---

## Index-Strategie

Empfohlene Indizes für Performance:

- `User.email` (Unique Index) - Login-Lookup
- `UserProfile.user_id` (Unique Index) - 1:1 Beziehung
- `Module.study_program_id` (Index) - Filterung nach Studiengang
- `CareerTreeNode.study_program_id` (Index) - Career Tree Lookup
- `RoadmapItem.roadmap_id` (Index) - Roadmap-Items laden
- `RoadmapItem.semester` (Index) - Zeitliche Filterung
- `ChatSession.user_id` + `ChatSession.topic_field_id` (Composite Index) - Chat-Lookup
- `UserQuestion.user_id` (Index) - User-Fragen Lookup
- `UserQuestion.career_tree_node_id` (Index) - Career Tree Kontext
- `ModuleImport.module_id` (Index) - Import-Historie pro Modul

---

## Migration-Hinweise

Bei Implementierung mit SQLAlchemy + Alembic:

1. **Reihenfolge der Tabellen-Erstellung:**
   - Basis-Entitäten: `User`, `University`, `StudyProgram`, `TopicField`
   - Abhängige Entitäten: `UserProfile`, `Module`, `CareerTreeNode`
   - Komplexe Entitäten: `Roadmap`, `RoadmapItem`, `ChatSession`, `UserQuestion`
   - Import/Historie: `ModuleImport`
   - Zwischentabellen: `user_module_progress`, `user_roadmap_items`, `career_tree_relationships`

2. **Foreign Key Constraints:**
   - Alle Foreign Keys sollten `ON DELETE CASCADE` oder `ON DELETE SET NULL` haben (je nach Anforderung)
   - Besonders wichtig bei `User` → `UserProfile` (CASCADE)
   - Bei `RoadmapItem` → `Module` (SET NULL, da optional)

3. **Enum-Typen:**
   - `ModuleType`: `REQUIRED`, `ELECTIVE`
   - `RoadmapItemType`: `COURSE`, `MODULE`, `PROJECT`, `SKILL`, `BOOK`, `CERTIFICATE`, `INTERNSHIP`, `BOOTCAMP`

---

## Offene Fragen / Erweiterungsmöglichkeiten

1. **Social Features:** Aktuell nicht im Schema, aber Platz für zukünftige Erweiterungen (z.B. `User` → `User` Beziehungen)

---

*Dokument erstellt für Review - Stand: 2024*

