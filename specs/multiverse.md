# TTA-Solo: Multiverse & Timeline Spec

## 1. Core Concept: Git for Fiction

The multiverse is implemented as a **version-controlled database**. Each "parallel world" is a branch. Player choices can fork reality.

---

## 2. Universe Structure

### The Prime Material
- The "main" branch - canonical world state
- Maintained by the system, not individual players
- High-quality player content can be merged back

### Player Branches
- Format: `user/{username}/{campaign_id}`
- Full copy of world state at fork point
- Zero cost to create (Dolt branch is O(1))

### Shared Adventures
- A "template" branch that multiple players can fork
- Example: "The Mines of Phandelver" adventure
- Player A and B both fork from the same starting point
- Their stories diverge independently

---

## 3. Fork Events

### When to Fork
A fork occurs when:
1. Player makes a **significant divergent choice**
2. Player explicitly requests to "explore what if"
3. Player dies and wants to continue from a checkpoint

### Fork Event Schema
```json
{
  "event_type": "FORK",
  "parent_universe_id": "uuid-parent",
  "child_universe_id": "uuid-child",
  "fork_point": "timestamp or event_id",
  "reason": "Player chose to spare the villain",
  "player_id": "uuid-player"
}
```

---

## 4. Dolt Operations

### Creating a Fork
```bash
# From the parent branch
dolt checkout main
dolt branch user/player1/campaign_goblin_king

# Player works on their branch
dolt checkout user/player1/campaign_goblin_king
# ... events are written here ...
```

### Python Skill: `fork_universe`
```python
def fork_universe(
    parent_universe_id: UUID,
    new_universe_name: str,
    fork_reason: str,
    player_id: UUID,
) -> Universe:
    """
    Create a new timeline branch.
    
    1. Create Dolt branch
    2. Insert new row in `universes` table
    3. Record FORK event
    4. Return new Universe object
    """
```

---

## 5. Neo4j Handling

### The Challenge
We don't want to duplicate the entire graph for every fork.

### The Solution: Lazy Divergence

1. **Shared nodes**: Most entities remain shared across timelines
2. **Query with universe_id**: Always filter by current timeline
3. **On divergence**: Create variant node with `[:VARIANT_OF]` relationship

```cypher
// Query: Get the King in this universe
MATCH (k:Character {name: "King Alaric"})
WHERE k.universe_id = $current_universe 
   OR (k.universe_id = "prime" AND NOT EXISTS {
       MATCH (variant:Character)-[:VARIANT_OF]->(k)
       WHERE variant.universe_id = $current_universe
   })
RETURN k
```

### Creating a Variant
```cypher
// King dies in Branch B
CREATE (k_b:Character {
  id: randomUUID(),
  name: "King Alaric",
  universe_id: "branch_b",
  is_dead: true
})
MATCH (k_a:Character {name: "King Alaric", universe_id: "prime"})
CREATE (k_b)-[:VARIANT_OF]->(k_a)
```

---

## 6. Time Travel Rules

### Visiting the Past
- Player can "view" past events (read-only)
- Cannot change events that already happened
- Can fork from any past point to explore "what if"

### Paradox Prevention
- No true time travel within a timeline
- "Going back" always creates a fork
- Original timeline continues unaffected

---

## 7. Cross-World Travel

### World Networks
Some worlds are connected, allowing characters to travel between them.

### Travel Event Schema
```json
{
  "event_type": "WORLD_TRAVEL",
  "actor_id": "uuid-character",
  "from_universe": "uuid-source",
  "to_universe": "uuid-destination",
  "method": "portal | spell | artifact",
  "timestamp": "in-game time"
}
```

### Rules
1. Character state is **copied** to destination world
2. Original remains in source (can be "dormant")
3. Inventory travels with character
4. Relationships do NOT transfer (must build new ones)

---

## 8. Merging Content Back

### The "Pull Request" for Fiction

High-quality player-created content can be proposed for the Prime Material:
- New locations
- Well-developed NPCs
- Interesting lore

### Merge Criteria
1. Does not contradict existing canon
2. Adds value to the shared world
3. Quality threshold met (AI + human review)

### Merge Process
```bash
# Propose merge
dolt checkout main
dolt merge user/player1/campaign_goblin_king --squash

# Review changes
dolt diff HEAD~1

# If approved, push
dolt push origin main
```

---

## 9. Implementation Priority

1. **Phase 1**: Basic fork/branch creation
2. **Phase 2**: Event recording with universe_id
3. **Phase 3**: Neo4j variant node logic
4. **Phase 4**: Cross-world travel
5. **Phase 5**: Merge/PR system for canon
