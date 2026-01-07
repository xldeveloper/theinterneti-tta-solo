# TTA-Solo: Core Ontology & Data Schema

## 1. Design Philosophy: The "Dual-State" Model

Every entity exists in two states simultaneously:

1. **The Fact (Dolt):** Immutable, versioned row. (e.g., "HP: 10/20")
2. **The Context (Neo4j):** Relational, semantic node. (e.g., "FEARS -> Spiders")

---

## 2. Dolt Schema (The "Truth")

These tables store the hard state. "Forking" the world means branching these tables.

### Table: `universes`

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary Key |
| `name` | VARCHAR(255) | "Prime Material", "Dark Sun Fork 2" |
| `parent_universe_id` | UUID | Logic for branching (Git lineage) |
| `created_at` | TIMESTAMP | Creation time |

### Table: `entities`

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary Key |
| `universe_id` | UUID | FK - The entity exists in *this* timeline |
| `type` | ENUM | 'Character', 'Location', 'Item', 'Faction' |
| `name` | VARCHAR(255) | Display name |
| `data_json` | JSON | The SRD stats (see Entity Standard below) |
| `current_location_id` | UUID | Where they are physically |

### Table: `events` (The Event Log)

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary Key |
| `universe_id` | UUID | FK - Which timeline |
| `timestamp` | TIMESTAMP | In-game time |
| `actor_id` | UUID | Who did it |
| `action_type` | VARCHAR(50) | 'COMBAT_ROUND', 'DIALOGUE', 'TRAVEL', 'ITEM_TRANSFER' |
| `payload` | JSON | The delta (see Event Standard below) |

---

## 3. Neo4j Schema (The "Brain")

These nodes allow the AI to search for "vibe" and "connection."

### Labels

- `:Entity` - Base label for everything
- `:Character` - Players, NPCs, Monsters
- `:Location` - Rooms, Cities, Planes
- `:Item` - Weapons, Artifacts, Resources
- `:Concept` - Abstract ideas: "Justice", "Fire Magic"

### Relationships (The "Soft" State)

```cypher
(:Character)-[:KNOWS {trust: 0.5}]->(:Character)
(:Character)-[:LOCATED_IN]->(:Location)
(:Location)-[:HAS_ATMOSPHERE]->(:Concept)
(:Event)-[:CAUSED]->(:Event)
(:Character)-[:FEARS]->(:Concept)
(:Character)-[:DESIRES]->(:Concept)
```

### Vector Properties

Every `:Entity` and `:Concept` node has:
- `embedding`: Vector embedding of its `description` field
- Usage: "Find me a monster that feels like 'Lovecraftian horror'" (Vector Search)

---

## 4. The Entity Standard (JSON)

All game objects must adhere to this structure:

```json
{
  "id": "uuid-v4",
  "name": "String",
  "type": "character | location | item | faction",
  "stats": {
    "srd_block": "Reference to 5e Statblock",
    "hp_current": 15,
    "hp_max": 20,
    "ac": 14,
    "abilities": {
      "str": 16, "dex": 12, "con": 14,
      "int": 10, "wis": 8, "cha": 10
    }
  },
  "tags": ["humanoid", "goblinoid", "hostile"],
  "description": "Natural language description for Vector Embedding."
}
```

---

## 5. The Event Standard (JSON)

History is a list of Events. An Event is the atomic unit of Story.

```json
{
  "event_id": "uuid-v4",
  "action": "ATTACK_MELEE",
  "actor": "character_id",
  "target": "target_id",
  "result": {
    "roll": 18,
    "outcome": "HIT",
    "damage": 6
  },
  "narrative_summary": "The goblin shrieks as the sword connects."
}
```

### Event Types

| Type | Description | Payload Fields |
|------|-------------|----------------|
| `COMBAT_ROUND` | A combat action | actor, target, roll, damage, outcome |
| `DIALOGUE` | Conversation | speaker, listener, text, emotion |
| `TRAVEL` | Movement | actor, from_location, to_location |
| `ITEM_TRANSFER` | Giving/taking | actor, target, item, direction |
| `FORK` | Timeline split | parent_universe, child_universe, reason |

---

## 6. The Bridge: Handling "Forks"

When a user forks a universe:

1. **Dolt:** Creates a new branch `branch_user_B`. (Zero cost)
2. **Neo4j:** We do *not* duplicate the whole graph.
   - Query with parameter `$universe_id`
   - If entity diverges: create new node with `[:VARIANT_OF]` edge

```cypher
// King dies in Branch B but lives in A
(:Entity {id: "King_B"})-[:VARIANT_OF]->(:Entity {id: "King_A"})
```

---

## 7. Pydantic Models (Implementation)

```python
from __future__ import annotations
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Literal

class EntityStats(BaseModel):
    srd_block: str | None = None
    hp_current: int
    hp_max: int
    ac: int = 10
    abilities: dict[str, int] = Field(default_factory=dict)

class Entity(BaseModel):
    id: UUID
    name: str
    type: Literal["character", "location", "item", "faction"]
    stats: EntityStats | None = None
    tags: list[str] = Field(default_factory=list)
    description: str = ""

class EventResult(BaseModel):
    roll: int | None = None
    outcome: str
    damage: int | None = None

class Event(BaseModel):
    event_id: UUID
    action: str
    actor: UUID
    target: UUID | None = None
    result: EventResult
    narrative_summary: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```
