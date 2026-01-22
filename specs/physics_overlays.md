# Physics Overlays Specification

> Universe-specific rules that modify ability mechanics based on setting.

## Overview

Physics Overlays allow abilities to behave differently based on the universe's rules. A fireball spell might work normally in a high fantasy world but be impossible in a hard sci-fi setting, while tech abilities might be enhanced in a cyberpunk world.

## Core Concepts

### Source Modifiers

Each overlay can modify ability sources:

| Modifier Type | Effect |
|--------------|--------|
| Enhanced | +1 die to damage/healing, advantage on ability checks |
| Normal | No modification |
| Restricted | -2 to save DCs, disadvantage on ability checks |
| Forbidden | Ability cannot be used at all |

### Global Multipliers

Overlays can also apply global multipliers:

- **Healing Multiplier**: Affects all healing (0.5x to 2x)
- **Stress Multiplier**: Affects stress gain (0.5x to 2x)
- **Condition Duration**: Affects how long conditions last

### Condition Modifiers

Specific conditions can be enhanced or weakened:

- **Duration Modifier**: Multiply duration
- **Save DC Modifier**: Add/subtract from save DCs
- **Effect Intensity**: Modify condition severity

## Pre-built Overlays

### HIGH_FANTASY_OVERLAY
The classic D&D-style world where magic is common.

```python
HIGH_FANTASY_OVERLAY = PhysicsOverlay(
    name="High Fantasy",
    description="A world where magic flows freely",
    source_modifiers={
        AbilitySource.MAGIC: SourceModifier.ENHANCED,
        AbilitySource.TECH: SourceModifier.NORMAL,
        AbilitySource.MARTIAL: SourceModifier.NORMAL,
    },
    healing_multiplier=1.25,
    stress_multiplier=0.75,
    condition_modifiers={
        "frightened": ConditionModifier(duration_multiplier=0.75),
    },
)
```

### LOW_MAGIC_OVERLAY
A gritty world where magic is rare and dangerous.

```python
LOW_MAGIC_OVERLAY = PhysicsOverlay(
    name="Low Magic",
    description="Magic is rare and carries risk",
    source_modifiers={
        AbilitySource.MAGIC: SourceModifier.RESTRICTED,
        AbilitySource.TECH: SourceModifier.NORMAL,
        AbilitySource.MARTIAL: SourceModifier.ENHANCED,
    },
    healing_multiplier=0.75,
    stress_multiplier=1.25,
    magic_side_effects=True,
)
```

### CYBERPUNK_OVERLAY
High-tech dystopia where cyberware reigns.

```python
CYBERPUNK_OVERLAY = PhysicsOverlay(
    name="Cyberpunk",
    description="Chrome and neon, tech is king",
    source_modifiers={
        AbilitySource.MAGIC: SourceModifier.FORBIDDEN,
        AbilitySource.TECH: SourceModifier.ENHANCED,
        AbilitySource.MARTIAL: SourceModifier.NORMAL,
    },
    stress_multiplier=1.0,
    tech_crit_bonus=True,
    condition_modifiers={
        "system_shock": ConditionModifier(duration_multiplier=1.5),
    },
)
```

### HORROR_OVERLAY
Dark and terrifying, fear is amplified.

```python
HORROR_OVERLAY = PhysicsOverlay(
    name="Horror",
    description="Darkness and dread permeate everything",
    source_modifiers={
        AbilitySource.MAGIC: SourceModifier.NORMAL,
        AbilitySource.TECH: SourceModifier.RESTRICTED,
        AbilitySource.MARTIAL: SourceModifier.NORMAL,
    },
    healing_multiplier=0.5,
    stress_multiplier=1.5,
    condition_modifiers={
        "frightened": ConditionModifier(duration_multiplier=2.0, save_dc_modifier=2),
        "charmed": ConditionModifier(duration_multiplier=1.5),
    },
)
```

### MYTHIC_OVERLAY
Legendary heroes with godlike power.

```python
MYTHIC_OVERLAY = PhysicsOverlay(
    name="Mythic",
    description="Where legends walk and gods intervene",
    source_modifiers={
        AbilitySource.MAGIC: SourceModifier.ENHANCED,
        AbilitySource.TECH: SourceModifier.RESTRICTED,
        AbilitySource.MARTIAL: SourceModifier.ENHANCED,
    },
    healing_multiplier=1.5,
    stress_multiplier=0.5,
    allow_legendary_actions=True,
)
```

### POST_APOCALYPTIC_OVERLAY
Survival in a ruined world.

```python
POST_APOCALYPTIC_OVERLAY = PhysicsOverlay(
    name="Post-Apocalyptic",
    description="Survival in the wasteland",
    source_modifiers={
        AbilitySource.MAGIC: SourceModifier.RESTRICTED,
        AbilitySource.TECH: SourceModifier.RESTRICTED,
        AbilitySource.MARTIAL: SourceModifier.ENHANCED,
    },
    healing_multiplier=0.75,
    stress_multiplier=1.25,
    resource_scarcity=True,
)
```

## Data Models

### SourceModifier
```python
class SourceModifier(str, Enum):
    ENHANCED = "enhanced"
    NORMAL = "normal"
    RESTRICTED = "restricted"
    FORBIDDEN = "forbidden"
```

### ConditionModifier
```python
class ConditionModifier(BaseModel):
    duration_multiplier: float = 1.0
    save_dc_modifier: int = 0
    effect_intensity: float = 1.0
```

### PhysicsOverlay
```python
class PhysicsOverlay(BaseModel):
    name: str
    description: str
    source_modifiers: dict[AbilitySource, SourceModifier]
    healing_multiplier: float = 1.0
    stress_multiplier: float = 1.0
    condition_modifiers: dict[str, ConditionModifier] = {}

    # Special flags
    magic_side_effects: bool = False
    tech_crit_bonus: bool = False
    resource_scarcity: bool = False
    allow_legendary_actions: bool = False
```

## Integration

### Universe Association
Each Universe can have an optional physics overlay:

```python
class Universe(BaseModel):
    # ... existing fields ...
    physics_overlay: PhysicsOverlay | None = None
```

### Ability Resolution
When resolving abilities, check overlay:

```python
def apply_overlay(ability, overlay):
    source_mod = overlay.source_modifiers.get(ability.source)

    if source_mod == SourceModifier.FORBIDDEN:
        return AbilityResult(success=False, reason="Ability forbidden in this universe")

    if source_mod == SourceModifier.ENHANCED:
        # Add bonus die, advantage, etc.
        pass

    if source_mod == SourceModifier.RESTRICTED:
        # Reduce DC, disadvantage, etc.
        pass
```

### Healing Application
```python
def apply_healing(amount, overlay):
    return int(amount * overlay.healing_multiplier)
```

### Stress Application
```python
def apply_stress(amount, overlay):
    return int(amount * overlay.stress_multiplier)
```

### Condition Duration
```python
def apply_condition_duration(condition_type, base_duration, overlay):
    mod = overlay.condition_modifiers.get(condition_type)
    if mod:
        return int(base_duration * mod.duration_multiplier)
    return base_duration
```

## Examples

### Casting Fireball in Different Settings

**High Fantasy**
- Source: Enhanced (+1 damage die)
- Result: 9d6 fire damage

**Low Magic**
- Source: Restricted (-2 to save DC)
- Result: 8d6 fire, DC reduced by 2
- Side effect chance

**Cyberpunk**
- Source: Forbidden
- Result: Cannot cast, ability fails

### Fear Effect in Horror Setting

**Normal Setting**
- Duration: 1 minute
- Save DC: 14

**Horror Overlay**
- Duration: 2 minutes (2x multiplier)
- Save DC: 16 (+2 modifier)
- Player stress: +2 (1.5x multiplier)
