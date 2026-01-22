# Universal Ability Object (UAO) System

> The "Singularity Engine" - A unified framework for abilities across magic, tech, and martial sources.

## Overview

The UAO system provides a single data model that can represent any ability in the game, regardless of whether it's a magic spell, a tech gadget, or a martial technique. This allows for:

- Consistent resolution across all ability types
- Physics overlays that modify abilities based on universe rules
- Cross-source hybrid abilities (technomancy, psionic martial arts)
- Solo play balance mechanics

## Core Concepts

### Ability Sources

Every ability has exactly one primary source:

| Source | Description | Resource Typical |
|--------|-------------|-----------------|
| `magic` | Supernatural power from arcane, divine, primal, or psionic sources | Spell slots |
| `tech` | Technological devices, implants, or gadgets | Cooldowns/Energy |
| `martial` | Physical techniques enhanced by training or ki | Stress/Momentum |

### Source Subtypes

Each source has subtypes that may interact differently with physics overlays:

**Magic Subtypes:**
- `arcane` - Learned/studied magic (wizards)
- `divine` - Granted by deities (clerics, paladins)
- `primal` - Nature-based (druids, rangers)
- `psionic` - Mind powers (psychics)

**Tech Subtypes:**
- `biotech` - Organic enhancements
- `cybertech` - Mechanical/electronic implants
- `nanotech` - Nanomachine-based abilities

**Martial Subtypes:**
- `ki` - Internal energy manipulation
- `stance` - Combat positioning/forms
- `maneuver` - Tactical combat techniques

### Resource Mechanisms

Abilities are gated by one of these resource mechanisms:

| Mechanism | Description | Recovery |
|-----------|-------------|----------|
| `slots` | Traditional spell slots (1st-9th level) | Long rest |
| `cooldown` | Per-encounter uses with recharge chance | Short/Long rest |
| `usage_die` | Degrading die (d12→d10→...→depleted) | Varies |
| `stress` | Risk accumulation (high = bad) | Rest/narrative |
| `momentum` | Reward accumulation (high = good) | Spent on use |
| `free` | No cost (cantrips, at-will) | N/A |

## Data Model

### Ability (Core Model)

```python
class Ability(BaseModel):
    id: UUID
    name: str
    description: str

    # Source classification
    source: AbilitySource  # magic, tech, martial
    subtype: str | None    # arcane, cybertech, ki, etc.

    # Resource cost
    mechanism: MechanismType  # slots, cooldown, usage_die, etc.
    mechanism_details: dict[str, Any]  # level, die_type, max_uses, etc.

    # Effects
    damage: DamageEffect | None
    healing: HealingEffect | None
    conditions: list[ConditionEffect]
    stat_modifiers: list[StatModifierEffect]

    # Targeting
    targeting: Targeting

    # Action economy
    action_cost: str  # action, bonus, reaction, free
    requires_concentration: bool

    # Metadata
    tags: list[str]
    prerequisites: list[str]
```

### Effect Components

**DamageEffect:**
```python
class DamageEffect(BaseModel):
    dice: str           # "2d6", "3d8+4"
    damage_type: str    # fire, cold, slashing, etc.
    save_ability: str | None   # dex, con, etc.
    save_dc_stat: str | None   # Ability used for DC calc
    save_for_half: bool = False
```

**HealingEffect:**
```python
class HealingEffect(BaseModel):
    dice: str | None    # "2d8+3"
    flat_amount: int = 0
    temp_hp: bool = False
```

**ConditionEffect:**
```python
class ConditionEffect(BaseModel):
    condition: str          # frightened, prone, stunned
    duration_type: str      # rounds, minutes, until_save
    duration_value: int | None
    save_ability: str | None
    save_dc_stat: str | None
```

**StatModifierEffect:**
```python
class StatModifierEffect(BaseModel):
    stat: str           # ac, speed, str, attack_rolls
    modifier: int       # +2, -4, etc.
    duration_type: str  # rounds, minutes, concentration
    duration_value: int | None
```

### Targeting

```python
class TargetingType(str, Enum):
    SELF = "self"
    SINGLE = "single"
    MULTIPLE = "multiple"
    AREA_SPHERE = "area_sphere"
    AREA_CONE = "area_cone"
    AREA_LINE = "area_line"
    AREA_CUBE = "area_cube"

class Targeting(BaseModel):
    type: TargetingType
    range_ft: int = 0           # 0 = self/touch
    area_size_ft: int | None    # Radius/length depending on type
    max_targets: int | None     # For MULTIPLE type
```

## Factory Functions

### create_spell()

Creates a magic ability with spell slots as the default mechanism.

```python
def create_spell(
    name: str,
    level: int,  # 0 = cantrip
    description: str,
    subtype: MagicSubtype = MagicSubtype.ARCANE,
    damage: DamageEffect | None = None,
    healing: HealingEffect | None = None,
    conditions: list[ConditionEffect] | None = None,
    targeting: Targeting | None = None,
    action_cost: str = "action",
    requires_concentration: bool = False,
) -> Ability:
```

### create_tech_ability()

Creates a tech ability with cooldown as the default mechanism.

```python
def create_tech_ability(
    name: str,
    description: str,
    subtype: TechSubtype = TechSubtype.CYBERTECH,
    max_uses: int = 1,
    recharge_on_rest: str = "short",
    damage: DamageEffect | None = None,
    conditions: list[ConditionEffect] | None = None,
    targeting: Targeting | None = None,
    action_cost: str = "action",
) -> Ability:
```

### create_martial_technique()

Creates a martial ability with stress/momentum mechanics.

```python
def create_martial_technique(
    name: str,
    description: str,
    subtype: MartialSubtype = MartialSubtype.MANEUVER,
    stress_cost: int = 0,
    momentum_cost: int = 0,
    damage: DamageEffect | None = None,
    conditions: list[ConditionEffect] | None = None,
    targeting: Targeting | None = None,
    action_cost: str = "action",
) -> Ability:
```

## Example Abilities

### Fireball (Magic - Arcane)
```python
fireball = create_spell(
    name="Fireball",
    level=3,
    description="A ball of fire explodes at a point you can see.",
    subtype=MagicSubtype.ARCANE,
    damage=DamageEffect(
        dice="8d6",
        damage_type="fire",
        save_ability="dex",
        save_for_half=True,
    ),
    targeting=Targeting(
        type=TargetingType.AREA_SPHERE,
        range_ft=150,
        area_size_ft=20,
    ),
)
```

### Nanite Injection (Tech - Nanotech)
```python
nanite_heal = create_tech_ability(
    name="Nanite Injection",
    description="Deploy healing nanites to repair tissue.",
    subtype=TechSubtype.NANOTECH,
    max_uses=2,
    recharge_on_rest="short",
    healing=HealingEffect(dice="2d8+4"),
    targeting=Targeting(
        type=TargetingType.SINGLE,
        range_ft=5,
    ),
)
```

### Stunning Strike (Martial - Ki)
```python
stunning_strike = create_martial_technique(
    name="Stunning Strike",
    description="Channel ki into your strike to stun the target.",
    subtype=MartialSubtype.KI,
    momentum_cost=2,
    conditions=[
        ConditionEffect(
            condition="stunned",
            duration_type="until_save",
            save_ability="con",
        )
    ],
    targeting=Targeting(type=TargetingType.SINGLE, range_ft=5),
    action_cost="bonus",
)
```

## Integration Points

### Event System

New event types for ability use:
- `ABILITY_USED` - An ability was activated
- `ABILITY_FAILED` - An ability failed (out of resources, etc.)
- `CONCENTRATION_BROKEN` - Concentration was lost

### Router Integration

The SkillRouter will handle `IntentType.USE_ABILITY`:
1. Look up ability by name/id
2. Check resource availability
3. Resolve targeting
4. Apply effects via EffectPipeline
5. Apply PbtA overlay
6. Return result

### Physics Overlays

Abilities can be modified by universe physics overlays:
- `CYBERPUNK_OVERLAY`: Tech enhanced (+1 die), Magic restricted (-2 DC)
- `HIGH_FANTASY_OVERLAY`: Magic enhanced (+1 die), Healing x1.25
- `HORROR_OVERLAY`: Stress x1.5, Fear effects extended

## Validation Rules

1. `mechanism_details` must match `mechanism` type
   - `slots`: requires `level: int`
   - `cooldown`: requires `max_uses: int`, optional `recharge_on: list[int]`
   - `usage_die`: requires `die_type: str`
   - `stress`: requires `stress_cost: int`
   - `momentum`: requires `momentum_cost: int`

2. Cantrips (level 0) use mechanism `free`

3. `targeting.area_size_ft` required for area types

4. At least one effect must be specified (damage, healing, conditions, or stat_modifiers)
