# Archetypes Specification

> Character archetypes that define combat role, paradigm, and focus.

## Overview

The Archetype system provides a flexible character classification that works across all settings. Instead of traditional classes, characters are built from:

1. **Archetype** - Combat/social role (what you do)
2. **Paradigm** - Power source approach (how you do it)
3. **Focus** - Specialization (what you're best at)

## Archetypes (Combat Roles)

| Archetype | Primary Role | Secondary Role |
|-----------|--------------|----------------|
| Guardian | Protect allies, control space | Absorb damage |
| Striker | Deal high single-target damage | Mobility |
| Controller | Area denial, debuffs | Crowd control |
| Leader | Buff allies, healing | Tactical coordination |
| Specialist | Unique utility, infiltration | Problem-solving |

### Guardian
- Bonus HP and AC
- Abilities to mark/taunt enemies
- Damage reduction features
- Area denial around protected allies

### Striker
- Bonus damage dice
- Extra mobility (movement, teleport)
- Abilities that exploit weak points
- Burst damage options

### Controller
- Area effect bonuses
- Condition duration extensions
- Abilities that restrict enemy movement
- Multiple target options

### Leader
- Healing/temp HP bonuses
- Abilities that grant allies actions
- Aura effects
- Combat advantage distribution

### Specialist
- Skill bonuses
- Utility abilities
- Stealth/infiltration features
- Information gathering

## Paradigms (Power Approaches)

| Paradigm | Source | Typical Mechanism |
|----------|--------|-------------------|
| Arcane Caster | Magic (arcane) | Spell slots |
| Divine Caster | Magic (divine) | Spell slots |
| Primal Caster | Magic (primal) | Spell slots |
| Psion | Magic (psionic) | Stress/Momentum |
| Martial Master | Martial | Stress/Momentum |
| Tech Specialist | Tech | Cooldowns |
| Hybrid | Mixed | Varies |

### Paradigm Bonuses

**Arcane Caster**
- Bonus spell slots
- Metamagic options
- Arcane recovery

**Divine Caster**
- Channel divinity uses
- Bonus to healing
- Divine intervention chance

**Primal Caster**
- Wild shape/beast forms
- Nature-based bonuses
- Terrain attunement

**Psion**
- Psionic focus abilities
- Stress tolerance increase
- Mental defense bonuses

**Martial Master**
- Extra attacks
- Maneuver superiority
- Physical save bonuses

**Tech Specialist**
- Gadget slots
- Overclock abilities
- System bonuses

## Focus (Specialization)

Each Archetype+Paradigm combination can have different focuses:

### Guardian Focuses
- **Bulwark**: Maximum defense, immovable
- **Sentinel**: Reactive, punishes enemy movement
- **Warden**: Area protection, zone control

### Striker Focuses
- **Assassin**: Burst damage from stealth
- **Duelist**: Single combat mastery
- **Skirmisher**: Hit-and-run tactics

### Controller Focuses
- **Enchanter**: Mind effects, charms
- **Evoker**: Damage-dealing AoE
- **Transmuter**: Battlefield manipulation

### Leader Focuses
- **Battle Priest**: Healing and buffs
- **Tactician**: Positioning and coordination
- **Inspiring**: Morale and advantage

### Specialist Focuses
- **Scout**: Reconnaissance, stealth
- **Face**: Social manipulation
- **Artificer**: Item creation, gadgets

## Data Models

### Archetype
```python
class Archetype(str, Enum):
    GUARDIAN = "guardian"
    STRIKER = "striker"
    CONTROLLER = "controller"
    LEADER = "leader"
    SPECIALIST = "specialist"
```

### Paradigm
```python
class Paradigm(str, Enum):
    ARCANE = "arcane"
    DIVINE = "divine"
    PRIMAL = "primal"
    PSIONIC = "psionic"
    MARTIAL = "martial"
    TECH = "tech"
    HYBRID = "hybrid"
```

### Focus
```python
class Focus(BaseModel):
    name: str
    description: str
    archetype: Archetype
    bonuses: list[FocusBonus]
```

### CharacterClass
```python
class CharacterClass(BaseModel):
    archetype: Archetype
    paradigm: Paradigm
    focus: Focus | None
    level: int = 1

    # Derived stats
    hp_bonus: int
    starting_abilities: list[UUID]
```

## Class Generation

Characters can be generated procedurally:

```python
def generate_class(
    archetype: Archetype | None = None,
    paradigm: Paradigm | None = None,
    focus_name: str | None = None,
) -> CharacterClass:
    """
    Generate a character class, optionally with random elements.
    """
```

## Example Builds

### "Battle Mage"
- Archetype: Striker
- Paradigm: Arcane
- Focus: Evoker
- Description: High damage caster focused on elemental destruction

### "Tech Knight"
- Archetype: Guardian
- Paradigm: Tech
- Focus: Sentinel
- Description: Power-armored defender with reactive shields

### "Mind Blade"
- Archetype: Striker
- Paradigm: Psionic
- Focus: Duelist
- Description: Psychic warrior with materialized weapons

### "Combat Medic"
- Archetype: Leader
- Paradigm: Tech
- Focus: Battle Priest (re-flavored)
- Description: Field medic with advanced medical tech
