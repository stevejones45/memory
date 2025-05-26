# Data Model Design

## Entity Structure (Enhanced)
```python
@dataclass
class Entity:
    name: str
    entityType: str
    observations: list[str]
    weight: int = 0  # NEW: usage counter for conceptual framework mapping
```

## Relation Structure (Unchanged)
```python
@dataclass
class Relation:
    from_entity: str  # renamed from 'from' (Python keyword)
    to_entity: str    # renamed from 'to' (Python keyword)
    relationType: str
```

## Knowledge Graph Structure
```python
@dataclass
class KnowledgeGraph:
    entities: list[Entity]
    relations: list[Relation]
```

## Storage Format (JSONL)
Each line contains either:
```json
{"type": "entity", "name": "...", "entityType": "...", "observations": [...], "weight": 0}
{"type": "relation", "from_entity": "...", "to_entity": "...", "relationType": "..."}
```

## Weight System Logic
- Weight increments when entity is accessed via search/open operations
- Weight increments when entity is mentioned in conversation review
- Entities with weight below threshold can be pruned
- Weight represents conceptual importance/frequency in user's mental model
