# TTA-Solo

**AI-Native Infinite Multiverse Engine**

A Neuro-symbolic text adventure where players collaborate with AI to tell stories in a shared, branching multiverse.

## Vision

The ultimate solo "choose your own adventure" D&D experience you can share with friends:
- **Share a character** - Archetype builder across worlds
- **Share an adventure** - Others relive your story's options
- **Share a world** - Create new stories in existing settings
- **Share a world network** - Stories that cross multiple worlds

## Architecture

| Layer | Tech | Purpose |
|-------|------|---------|
| **Truth** | Dolt | Git-like SQL - branching timelines, event sourcing |
| **Brain** | Neo4j | Graph + Vector search - relationships, semantic search |
| **Hands** | Python Skills | Stateless scripts for game mechanics |

### The Neuro-Symbolic Model

- **Neural** (LLM): Narrative, dialogue, improvisation
- **Symbolic** (Python): SRD 5e rules, dice, state validation
- **Bridge** (Skills): Translate intent to mechanics and back

## Quick Start

```bash
# Install dependencies
uv sync --all-extras

# Run tests
uv run pytest -v

# Type check
uv run pyright src/
```

## Project Structure

```
tta-solo/
├── specs/              # Specs MUST exist before code
│   ├── ontology.md     # Entity/Event schemas
│   ├── mechanics.md    # SRD rule implementations
│   └── multiverse.md   # Timeline branching rules
├── src/
│   ├── skills/         # Stateless Python tools
│   └── engine/         # Core game loops
├── tests/              # 100% coverage goal
└── data/               # Local database storage
```

## Development Workflow

1. **Spec Phase**: Write spec in `/specs/` before any code
2. **Skill Phase**: Implement as stateless Python with Pydantic
3. **Test Phase**: TDD - write tests that verify the spec
4. **Execute**: Wire into agent loop

## License

MIT
