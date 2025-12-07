# Frontend API - Topic Field Format

## Übersicht

Das Frontend erhält `topic_field` in unterschiedlichen Formaten, abhängig vom Endpoint:

## 1. Roadmap Responses

**Endpoint**: `/api/v1/topic-fields/{topic_field_id}/roadmap`

**Format**: `topic_field_id` (nur die ID als Zahl)

```typescript
interface RoadmapResponse {
  id: number;
  topic_field_id: number;  // ← Nur die ID
  name: string;
  description: string;
  // ...
}
```

**Backend Model**: `RoadmapResponse` in `backend/api/models/roadmap.py`
- Feld: `topic_field_id: int` (Zeile 75)
- Das Frontend erhält nur die ID, nicht das vollständige TopicField-Objekt

## 2. Career Tree Node Responses

**Endpoint**: `/api/v1/study-programs/{study_program_id}/career-tree`

**Format**: `topic_field` (vollständiges Objekt mit id, name, description)

```typescript
interface CareerTreeNode {
  id: number;
  name: string;
  topic_field?: TopicField;  // ← Vollständiges Objekt
  // ...
}

interface TopicField {
  id: number;
  name: string;
  description: string;
}
```

**Backend Model**: `CareerTreeNodeResponse` in `backend/api/models/career.py`
- Feld: `topic_field: Optional[TopicFieldResponse] = None` (Zeile 30)
- Das Frontend erhält das vollständige TopicField-Objekt mit allen Eigenschaften

## Zusammenfassung

| Endpoint | Format | Typ |
|----------|--------|-----|
| Roadmap | `topic_field_id` | `number` |
| Career Tree Node | `topic_field` | `TopicField` (Objekt) |

## Frontend Implementation

- **Roadmaps**: `frontend/app/api/generateRoadmap.ts` - erwartet `topic_field_id: number`
- **Career Tree**: `frontend/app/api/getTree.ts` - erwartet `topic_field?: TopicField`

## Career Tree Nodes - topic_field_id Verteilung

**WICHTIG:** Nur Leaf-Nodes (Jobs) können eine `topic_field_id` haben!

- ✅ **Leaf-Nodes (is_leaf=True)**: Können eine `topic_field_id` haben (optional)
- ❌ **Non-Leaf-Nodes (is_leaf=False)**: Haben **KEINE** `topic_field_id` (immer NULL)

### Struktur im Career Tree

```
📁 Research / Development (Level 0) - topic_field_id = NULL
  📁 Research (Level 1) - topic_field_id = NULL
    📁 Theoretical Research (Level 2) - topic_field_id = NULL
      📁 Algorithm Theory (Level 3) - topic_field_id = NULL
        🌿 Research Scientist - Network Flow (Level 10) - topic_field_id = 6 ✅
        🌿 Algorithm Researcher (Level 10) - topic_field_id = 7 ✅
```

**Aktuelle Statistik:**
- Gesamt: 146 Nodes
- Leaf-Nodes: 55 (können topic_field_id haben)
- Non-Leaf-Nodes: 91 (haben immer topic_field_id = NULL)

## Hinweis

Wenn das Frontend für Roadmaps auch das vollständige TopicField-Objekt benötigt, müsste:
1. `RoadmapResponse` erweitert werden um ein `topic_field: Optional[TopicFieldResponse]` Feld
2. Die Route müsste das TopicField-Objekt aus der Datenbank laden und zurückgeben

