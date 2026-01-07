# TTA-Solo: AI-Native Infinite Multiverse Engine

> A Neuro-symbolic text adventure where players collaborate with AI to tell stories in a shared, branching multiverse.

## Quick Facts

- **Stack**: Python 3.11+, Dolt (versioned SQL), Neo4j (graph + vector)
- **Package Manager**: `uv` (NEVER pip/poetry)
- **Test Command**: `uv run pytest -v`
- **Lint Command**: `uv run ruff check . --fix`
- **Type Check**: `uv run pyright src/`
- **Format**: `uv run ruff format .`

## Architecture: The "Lite" Stack

| Layer | Tech | Purpose |
|-------|------|---------|
| **Truth** | Dolt | Git-like SQL - branching timelines, event sourcing |
| **Brain** | Neo4j | Graph + native Vector search - relationships, semantic search |
| **Hands** | Python Skills | Stateless scripts in `src/skills/` |

## Key Directories

- `specs/` - The "Constitution" - specs MUST exist before code
- `src/skills/` - Stateless Python tools (dice, lore, world_db)
- `src/engine/` - Core game loops and orchestration
- `data/` - Local database storage
- `tests/` - Test files (100% coverage goal)

## Development Workflow: Spec-Driven

**CRITICAL: We do NOT write code until we have a Spec.**

1. **Spec Phase**: Draft markdown in `/specs/` defining inputs, logic, outputs
2. **Skill Phase**: Implement as stateless Python tool with Pydantic validation
3. **Test Phase**: Write tests that verify the spec
4. **Execution Phase**: Wire into the agent loop

## Code Style

- Python 3.11+ with `from __future__ import annotations`
- Type hints: Use `str | None` (NOT `Optional[str]`)
- Dicts: Use `dict[str, Any]` (NOT `Dict[str, Any]`)
- Pydantic for all data validation
- Google-style docstrings
- 100 char line length (Ruff)

## The Neuro-Symbolic Model

### Neural Layer (LLM)
- Handles narrative, dialogue, improvisation
- Uses PbtA-style "Moves" for pacing (fail forward, no dead ends)
- Never hallucinates rules - defers to Symbolic layer

### Symbolic Layer (Python)
- Enforces SRD 5e mechanics strictly
- Dice rolls use RNG, not LLM prediction
- Validates all game state changes

### The Bridge
- Skills translate player intent ("I stab him") into function calls (`attack_roll()`)
- Results flow back through LLM for narrative wrapping

## Core Axioms

1. **Dolt is for Truth, Neo4j is for Search**
   - Kill a goblin → Event in Dolt (can rollback/fork)
   - Goblin's brother hates you → Relationship in Neo4j (for retrieval)

2. **Stateless Simplicity**
   - Skills fail cleanly, database holds state
   - No Python memory between calls

3. **Fail Forward**
   - If Symbolic fails, Neural takes over to keep story moving
   - Log the edge case for later

## Data Schema (Dual-State)

### Dolt Tables (The Facts)
- `universes` - Timeline branches
- `entities` - Characters, items, locations with JSON stats
- `events` - Immutable event log (the history)

### Neo4j Nodes (The Context)
- `:Entity`, `:Character`, `:Location`, `:Concept`
- Relationships: `KNOWS`, `LOCATED_IN`, `CAUSED`, `FEARS`
- Vector embeddings on description fields

## Git Conventions

- **Branch naming**: `{initials}/{description}` (e.g., `ti/add-combat-skill`)
- **Commit format**: Conventional Commits (`feat:`, `fix:`, `docs:`, `spec:`)
- **PR titles**: Same as commit format

## Critical Rules

### Before Writing Code
- Spec MUST exist in `/specs/`
- Schema MUST be defined for any new data structures
- Tests MUST be written (TDD preferred)

### Skills (src/skills/)
- MUST be stateless - no global variables
- MUST use Pydantic for input/output validation
- MUST handle errors gracefully and return structured results
- MUST NOT call LLMs directly - that's the engine's job

### Database Access
- Use direct drivers (mysql-connector for Dolt, neo4j driver)
- No ORMs - keep it simple
- All writes go through event sourcing pattern

## Common Commands

```bash
# Setup
uv sync                     # Install dependencies

# Development
uv run pytest -v            # Run tests
uv run ruff format .        # Format code
uv run ruff check . --fix   # Lint
uv run pyright src/         # Type check

# Database (when set up)
dolt sql                    # Interactive Dolt shell
dolt branch                 # List branches
dolt checkout -b <name>     # Create timeline fork
```

## Skill Activation

Before implementing ANY task, check if relevant skills/specs apply:

- Creating game mechanics → Check `specs/mechanics.md`
- Working with entities → Check `specs/ontology.md`
- Timeline/branching logic → Check `specs/multiverse.md`
- Writing skills → Follow stateless pattern in existing skills
