# Effect Pipeline Specification

> Managing conditions, temporary effects, and combat state for entities.

## Overview

The Effect Pipeline handles the application and tracking of:

1. **Conditions** - Status effects like frightened, prone, stunned
2. **Active Effects** - Temporary stat modifiers from abilities
3. **Concentration** - Tracking and breaking concentration
4. **Combat State** - Per-entity combat tracking

## Core Concepts

### Conditions

Conditions are status effects that change how an entity behaves or what it can do. They come from the SRD 5e condition list plus custom conditions.

**Standard Conditions:**
- Blinded, Charmed, Deafened, Exhaustion, Frightened
- Grappled, Incapacitated, Invisible, Paralyzed
- Petrified, Poisoned, Prone, Restrained, Stunned, Unconscious

**Duration Types:**
- `rounds` - Expires after N rounds
- `minutes` - Expires after N minutes
- `until_save` - Can save to end at end of turn
- `until_rest` - Removed on short/long rest
- `permanent` - Requires removal ability

### Active Effects

Temporary stat modifications that last for a duration:
- AC bonuses/penalties
- Speed modifications
- Ability score changes
- Attack/damage modifiers
- Saving throw modifiers

### Concentration

Some abilities require concentration:
- Only one concentration effect at a time
- Broken by taking damage (CON save DC 10 or half damage)
- Broken by incapacitation
- Ends if you cast another concentration spell

## Data Models

### ConditionInstance

```python
class ConditionInstance(BaseModel):
    id: UUID
    entity_id: UUID
    universe_id: UUID
    condition_type: str        # "frightened", "prone", etc.
    source_ability_id: UUID | None
    source_entity_id: UUID | None

    # Duration
    duration_type: str         # "rounds", "minutes", "until_save", etc.
    duration_remaining: int | None
    applied_at_round: int | None

    # Save to end
    save_ability: str | None   # "con", "wis", etc.
    save_dc: int | None

    def tick() -> bool          # Returns True if expired
    def attempt_save(roll, modifier) -> bool  # Returns True if saved
```

### ActiveEffect

```python
class ActiveEffect(BaseModel):
    id: UUID
    entity_id: UUID
    universe_id: UUID
    source_ability_id: UUID | None
    source_entity_id: UUID | None

    # Effect
    stat: str                  # "ac", "speed", "str", etc.
    modifier: int
    modifier_type: str         # "bonus", "penalty", "set"

    # Duration
    duration_type: str
    duration_remaining: int | None
    requires_concentration: bool = False
```

### EntityCombatState

```python
class EntityCombatState(BaseModel):
    entity_id: UUID
    universe_id: UUID

    # Conditions and effects
    conditions: list[ConditionInstance]
    active_effects: list[ActiveEffect]

    # Concentration
    concentrating_on: UUID | None  # Ability ID
    concentration_source: UUID | None  # Who cast it

    # Combat tracking
    current_round: int = 0
    has_reaction: bool = True
    has_action: bool = True
    has_bonus_action: bool = True
    death_saves_success: int = 0
    death_saves_failure: int = 0
```

## Effect Pipeline

The EffectPipeline service handles effect application and management.

### apply_ability_effects()

Main entry point for applying an ability's effects to targets.

```python
async def apply_ability_effects(
    ability: Ability,
    caster_id: UUID,
    target_ids: list[UUID],
    universe_id: UUID,
    attack_roll: int | None = None,
    save_roll: int | None = None,
) -> EffectApplicationResult:
    """
    Apply all effects from an ability to targets.

    1. Resolve damage (if any)
    2. Apply conditions (if any)
    3. Apply stat modifiers (if any)
    4. Track concentration (if required)
    """
```

### tick_combat_round()

Called at the start of each entity's turn.

```python
async def tick_combat_round(
    entity_id: UUID,
    universe_id: UUID,
) -> RoundTickResult:
    """
    Process start-of-turn effects:
    1. Decrement duration counters
    2. Remove expired effects
    3. Allow saves against ongoing conditions
    4. Process damage-over-time effects
    """
```

### apply_condition()

Apply a single condition to an entity.

```python
async def apply_condition(
    entity_id: UUID,
    universe_id: UUID,
    condition: ConditionEffect,
    source_ability_id: UUID | None = None,
    source_entity_id: UUID | None = None,
    save_dc: int | None = None,
) -> ConditionApplicationResult:
```

### check_concentration()

Check if concentration is maintained after taking damage.

```python
async def check_concentration(
    entity_id: UUID,
    universe_id: UUID,
    damage_taken: int,
) -> ConcentrationCheckResult:
    """
    DC = max(10, damage / 2)
    Roll CON save
    If failed, concentration is broken
    """
```

### remove_condition()

Remove a condition from an entity.

```python
async def remove_condition(
    entity_id: UUID,
    universe_id: UUID,
    condition_id: UUID,
) -> bool:
```

## Result Models

### EffectApplicationResult

```python
class EffectApplicationResult(BaseModel):
    success: bool
    targets_affected: list[UUID]
    damage_dealt: dict[UUID, int]
    healing_done: dict[UUID, int]
    conditions_applied: list[ConditionInstance]
    effects_applied: list[ActiveEffect]
    saves_made: dict[UUID, bool]
    concentration_started: bool = False
```

### RoundTickResult

```python
class RoundTickResult(BaseModel):
    entity_id: UUID
    conditions_expired: list[str]
    effects_expired: list[str]
    saves_attempted: list[SaveAttemptResult]
    dot_damage: int = 0  # Damage over time
```

### ConcentrationCheckResult

```python
class ConcentrationCheckResult(BaseModel):
    maintained: bool
    roll: int
    dc: int
    total: int
    ability_lost: UUID | None
```

## Event Integration

New event types to add to EventType enum:
- `CONDITION_APPLIED` - A condition was applied
- `CONDITION_REMOVED` - A condition ended
- `EFFECT_APPLIED` - A stat modifier was applied
- `EFFECT_EXPIRED` - A stat modifier expired
- `CONCENTRATION_CHECK` - Concentration was tested
- `CONCENTRATION_BROKEN` - Concentration was lost

## Combat State Integration

Combat state should be:
- Created when entity enters combat
- Updated each round
- Cleared when combat ends
- Persisted to database for session continuity

## Condition Mechanics Reference

| Condition | Primary Effect |
|-----------|----------------|
| Blinded | Can't see, auto-fail sight checks, disadvantage on attacks |
| Charmed | Can't attack charmer, charmer has advantage on social |
| Frightened | Disadvantage on checks/attacks while source visible |
| Grappled | Speed 0 |
| Incapacitated | Can't take actions or reactions |
| Paralyzed | Incapacitated + auto-fail STR/DEX saves + attacks are crits |
| Prone | Disadvantage on attacks, melee attacks have advantage |
| Restrained | Speed 0, disadvantage on attacks/DEX saves |
| Stunned | Incapacitated + auto-fail STR/DEX saves |
| Unconscious | Incapacitated + prone + unaware |
