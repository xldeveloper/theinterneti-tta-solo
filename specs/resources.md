# Resource System Specification

> Thermodynamics of ability usage - managing limited resources like spell slots, cooldowns, usage dice, and stress/momentum.

## Overview

The resource system manages the costs and limitations of ability usage. It provides unified interfaces for:

1. **Usage Die** - Degrading dice (d12→d10→...→depleted)
2. **Cooldown Tracking** - Per-encounter abilities with recharge
3. **Stress/Momentum** - Risk/reward accumulation mechanics

## Usage Die

The usage die is a degrading resource inspired by The Black Hack. When you use a resource, you roll the current die. On a low result, the die degrades to the next smaller size.

### Die Chain
```
d12 → d10 → d8 → d6 → d4 → depleted
```

### Mechanics
- **Rolling**: Roll the current die when using the resource
- **Degradation**: On a 1 or 2, the die downgrades
- **Depletion**: When d4 degrades, the resource is depleted
- **Restoration**: Rest or items can upgrade the die

### Data Model
```python
class UsageDie(BaseModel):
    die_chain: list[str] = ["d4", "d6", "d8", "d10", "d12"]
    current_index: int = 4  # Start at d12 (index 4)
    degrade_on: list[int] = [1, 2]  # Degrade on these results
    depleted: bool = False

    def roll_and_check() -> UsageDieResult
    def degrade() -> bool  # Returns True if now depleted
    def restore(steps: int = 1) -> int  # Returns new index
```

### Usage
```python
# Roll the usage die
result = usage_die.roll_and_check()
# result.roll = 3, result.degraded = False, result.new_die = "d12"

# On degradation
result = usage_die.roll_and_check()
# result.roll = 1, result.degraded = True, result.new_die = "d10"
```

## Cooldown Tracking

Cooldowns represent abilities that can be used a limited number of times before needing to recharge.

### Mechanics
- **Uses**: Track current/max uses
- **Recharge on Rest**: Restore all uses on short/long rest
- **Recharge Roll**: Some abilities recharge on specific die results (e.g., 5-6 on d6)

### Data Model
```python
class CooldownTracker(BaseModel):
    max_uses: int
    current_uses: int
    recharge_on: list[int] | None = None  # Die results that restore 1 use
    recharge_die: str = "d6"  # Die to roll for recharge
    recharge_on_rest: str | None = None  # "short" or "long"

    def use() -> bool  # Returns True if use was allowed
    def try_recharge() -> CooldownRechargeResult
    def restore_on_rest(rest_type: str) -> int  # Returns uses restored
```

### Usage
```python
# Use an ability
if tracker.use():
    # Ability used successfully
    pass
else:
    # Out of uses
    pass

# Try to recharge at round start
result = tracker.try_recharge()
# result.recharged = True, result.roll = 5, result.uses_restored = 1
```

## Stress/Momentum

A dual-resource system for martial characters. Stress accumulates from risky actions (bad), while Momentum builds from successes (good).

### Stress
- Builds up from risky techniques, taking damage, failed checks
- At max stress: "Breaking Point" - character is rattled/exhausted
- Reduced by rest, certain abilities, or narrative beats

### Momentum
- Builds from successful attacks, critical hits, defeating enemies
- Spent to power special techniques
- Lost if you take damage or fail dramatically

### Data Model
```python
class StressMomentumPool(BaseModel):
    stress: int = 0
    stress_max: int = 10
    momentum: int = 0
    momentum_max: int = 5

    def add_stress(amount: int) -> StressChangeResult
    def reduce_stress(amount: int) -> int
    def add_momentum(amount: int) -> int  # Returns actual gained
    def spend_momentum(amount: int) -> bool  # Returns if spent
    def take_damage_reset() -> int  # Returns momentum lost
    def is_at_breaking_point() -> bool
```

### Stress Consequences
| Stress Level | Effect |
|--------------|--------|
| 0-3 | Normal |
| 4-6 | Disadvantage on concentration checks |
| 7-9 | -2 to all saves |
| 10+ | Breaking Point - must rest or suffer exhaustion |

## Integration

### Entity Resources
Entities track their resource pools:
```python
class EntityResources(BaseModel):
    usage_dice: dict[str, UsageDie]  # Named usage dice
    cooldowns: dict[str, CooldownTracker]  # Ability cooldowns
    stress_momentum: StressMomentumPool | None
    spell_slots: dict[int, SpellSlotTracker] | None
```

### Ability Resolution
When resolving an ability:
1. Check resource availability
2. Consume resource
3. Execute ability
4. Record resource change event

### Rest Integration
On rest:
- **Short Rest**: Restore cooldowns marked "short", reduce stress by 1d4
- **Long Rest**: Restore all resources, reset stress to 0, upgrade usage dice

## Events

New event types:
- `RESOURCE_USED` - A resource was consumed
- `RESOURCE_DEPLETED` - A resource reached 0
- `RESOURCE_RESTORED` - A resource was restored
- `STRESS_GAINED` - Stress increased
- `MOMENTUM_GAINED` - Momentum increased
- `BREAKING_POINT` - Max stress reached

## Skill Functions

### roll_usage_die(usage_die: UsageDie) -> UsageDieResult
Roll a usage die and check for degradation.

### try_recharge_ability(tracker: CooldownTracker) -> CooldownRechargeResult
Attempt to recharge a cooldown ability.

### process_round_start_recharges(cooldowns: dict[str, CooldownTracker]) -> list[CooldownRechargeResult]
Process all recharge rolls at the start of a round.

### apply_rest_to_resources(resources: EntityResources, rest_type: str) -> RestResourceResult
Apply rest effects to all resource pools.
