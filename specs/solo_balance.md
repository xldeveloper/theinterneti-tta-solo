# Solo Balance Stack Specification

> Mechanics for solo play balance, inspired by WWN/Godbound and other OSR systems.

## Overview

Solo play requires different balance mechanics than party-based play. The solo balance stack provides:

1. **Fray Die** - Automatic damage to weaker enemies
2. **Damage Thresholds** - Simplified damage tracking
3. **Defy Death** - Death-defying saves
4. **Action Economy Boost** - Multiple actions per round

## Fray Die

The Fray Die represents a hero's ambient lethality - their ability to damage lesser foes just by being in combat with them.

### Mechanics
- Roll once per round at start of turn
- Damage applies to one enemy with HD <= your level
- No attack roll needed
- Cannot target enemies above your level
- Can split damage among multiple mooks

### Configuration
```python
class FrayDie(BaseModel):
    die: str = "d6"  # Base die
    affects_mooks_only: bool = True  # Only targets HD <= level
    level_scaling: bool = True  # Die increases at higher levels
    can_split: bool = True  # Split damage among multiple targets
```

### Level Scaling
| Level | Fray Die |
|-------|----------|
| 1-4   | 1d6      |
| 5-8   | 1d8      |
| 9-12  | 1d10     |
| 13+   | 1d12     |

## Damage Thresholds

Instead of tracking exact HP damage, use simplified damage thresholds for faster play.

### Threshold Levels
| Threshold | Description | Effect on Mook | Effect on Elite |
|-----------|-------------|----------------|-----------------|
| 0 | Miss | No effect | No effect |
| 1 | Light Hit | 1 HP damage | Minor wound |
| 2 | Solid Hit | Kill (1-2 HD) | Wound |
| 4 | Heavy Hit | Kill (any mook) | Serious wound |
| 6+ | Devastating | Kill + overflow | Critical wound |

### Calculation
```python
def calculate_threshold_damage(
    attack_roll: int,
    target_ac: int,
    is_critical: bool,
    weapon_weight: str,  # "light", "medium", "heavy"
) -> int:
    """
    Convert attack success into threshold damage.

    - Beat AC by 0-4: Light hit (1)
    - Beat AC by 5-9: Solid hit (2)
    - Beat AC by 10+: Heavy hit (4)
    - Critical: +2 threshold levels
    - Heavy weapon: +1 threshold level
    """
```

## Defy Death

When a solo character would die or be knocked unconscious, they can attempt to defy death.

### Mechanics
1. When reduced to 0 HP, make a CON save
2. DC = 10 + total damage this round
3. On success: Stay at 1 HP, gain exhaustion
4. On failure: Fall unconscious normally
5. Each use increases DC by 5 until long rest

### Configuration
```python
class DefyDeathConfig(BaseModel):
    base_dc: int = 10
    dc_increase_per_use: int = 5
    grants_exhaustion: bool = True
    max_uses_per_day: int = 3
```

### Result
```python
class DefyDeathResult(BaseModel):
    survived: bool
    roll: int
    dc: int
    total: int
    exhaustion_gained: int
    uses_remaining: int
```

## Action Economy Boost

Solo characters can take multiple actions to compensate for lack of party members.

### Heroic Action
Once per round, a solo character can take a Heroic Action:
- An additional action (attack, cast spell, etc.)
- OR movement equal to their speed
- Costs 1 Momentum (if using stress/momentum)
- Alternately: Costs 1d4 Stress

### Reaction Boost
- Solo characters can take 2 reactions per round instead of 1
- Second reaction costs 1 Momentum

## Round Start Resolution

At the start of each combat round for a solo character:

```python
class SoloRoundStartResult(BaseModel):
    fray_damage: int
    fray_targets: list[UUID]
    recharge_results: list[CooldownRechargeResult]
    momentum_gained: int  # +1 if round started in combat
```

### Sequence
1. Gain 1 Momentum (combat flow)
2. Roll Fray Die, apply to valid targets
3. Process ability recharges
4. Reset action economy

## Configuration Model

```python
class SoloCombatConfig(BaseModel):
    """Configuration for solo combat mechanics."""

    # Fray Die
    use_fray_die: bool = True
    fray_die_base: str = "d6"
    fray_affects_mooks_only: bool = True

    # Damage Thresholds
    use_damage_thresholds: bool = False  # Optional simplification

    # Defy Death
    use_defy_death: bool = True
    defy_death_max_uses: int = 3

    # Action Economy
    heroic_action_enabled: bool = True
    heroic_action_cost: str = "momentum"  # "momentum", "stress", or "free"
    extra_reactions: int = 1

    # Momentum
    combat_momentum_gain: int = 1  # Per round
```

## Integration

### Router Integration
The SkillRouter should optionally apply solo mechanics:

```python
def resolve(self, intent, context, extra):
    # ... normal resolution ...

    if self.solo_config and self.solo_config.use_fray_die:
        fray_result = resolve_fray_die(actor, enemies)
        result.fray_damage = fray_result
```

### Combat Flow
1. **Initiative**: Roll normally
2. **Round Start**: Apply solo round start
3. **Turn**: Normal + optional Heroic Action
4. **Reactions**: Up to 2 reactions
5. **Round End**: Tick effects, check morale

## Example Combat

```
Round 1 Start:
- Solo warrior (Level 5) vs 3 goblins (1 HD) + 1 hobgoblin chief (4 HD)
- Gain 1 Momentum (now at 1)
- Roll Fray Die: d8 = 6 damage
- Apply to goblin: goblin dies (HD 1, threshold exceeded)

Warrior's Turn:
- Attack hobgoblin chief: Hit for solid damage (threshold 2)
- Heroic Action (spend 1 Momentum): Attack again, light hit (threshold 1)

Goblin's Turn:
- Two goblins attack, one hits for 4 damage
- Warrior uses reaction to Parry, reducing to 2 damage

Round 2 Start:
- Gain 1 Momentum (now at 1)
- Fray Die: d8 = 3 damage, kills another goblin

... and so on
```
