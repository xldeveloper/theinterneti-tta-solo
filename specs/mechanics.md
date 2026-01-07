# TTA-Solo: Game Mechanics Spec

## 1. Philosophy: Neuro-Symbolic Resolution

The game uses a **hybrid** approach:
- **Symbolic Layer**: Python enforces SRD 5e rules strictly
- **Neural Layer**: LLM wraps results in narrative

The Symbolic layer NEVER hallucinates. Dice use RNG, not LLM prediction.

---

## 2. The Resolution Loop

```
Player Input ("I attack the goblin")
    ↓
Neural: Parse Intent → AttackAction(target="Goblin", weapon="Longsword")
    ↓
Symbolic: Execute Rules
    - Roll d20 + modifiers
    - Compare to AC
    - Calculate damage
    ↓
Return: {success: true, damage: 8, target_hp: 4}
    ↓
Neural: Narrate → "Your blade catches the goblin's shoulder..."
```

---

## 3. Dice Rolling

### Spec: `roll_dice(notation: str) -> DiceResult`

**Input**: Standard dice notation (e.g., "2d6+3", "1d20", "4d6kh3")

**Output**:
```python
class DiceResult(BaseModel):
    notation: str           # Original notation
    rolls: list[int]        # Individual die results
    modifier: int           # Any +/- modifier
    total: int              # Final result
    kept: list[int] | None  # For "keep highest/lowest"
```

**Rules**:
- Use `secrets.randbelow()` for cryptographic randomness
- Support: `NdX`, `NdX+M`, `NdXkhN` (keep highest), `NdXklN` (keep lowest)

---

## 4. Attack Resolution

### Spec: `resolve_attack(attacker: Entity, target: Entity, weapon: Weapon) -> AttackResult`

**Input**:
- `attacker`: Entity with stats
- `target`: Entity with AC
- `weapon`: Weapon with damage dice

**Process**:
1. Roll d20
2. Add ability modifier (STR for melee, DEX for ranged/finesse)
3. Add proficiency bonus if proficient
4. Compare to target AC

**Output**:
```python
class AttackResult(BaseModel):
    hit: bool
    critical: bool          # Natural 20
    fumble: bool            # Natural 1
    attack_roll: int        # The d20 result
    total_attack: int       # With modifiers
    damage: int | None      # Only if hit
    damage_type: str | None # "slashing", "fire", etc.
```

**SRD Rules Enforced**:
- Natural 20 always hits, double damage dice
- Natural 1 always misses
- Cover bonuses to AC (+2 half, +5 three-quarters)

---

## 5. Saving Throws

### Spec: `make_saving_throw(entity: Entity, ability: str, dc: int) -> SaveResult`

**Input**:
- `entity`: The one making the save
- `ability`: "str", "dex", "con", "int", "wis", "cha"
- `dc`: Difficulty Class to beat

**Output**:
```python
class SaveResult(BaseModel):
    success: bool
    roll: int               # The d20
    total: int              # With modifier
    dc: int
    margin: int             # How much over/under
```

---

## 6. Skill Checks

### Spec: `skill_check(entity: Entity, skill: str, dc: int) -> CheckResult`

**Skills mapped to abilities** (SRD):
```python
SKILL_ABILITIES = {
    "athletics": "str",
    "acrobatics": "dex",
    "stealth": "dex",
    "arcana": "int",
    "history": "int",
    "investigation": "int",
    "nature": "int",
    "religion": "int",
    "animal_handling": "wis",
    "insight": "wis",
    "medicine": "wis",
    "perception": "wis",
    "survival": "wis",
    "deception": "cha",
    "intimidation": "cha",
    "performance": "cha",
    "persuasion": "cha",
}
```

**Output**: Same as SaveResult

---

## 7. PbtA-Style Narrative Moves

When the Symbolic layer returns a result, the Neural layer uses **Moves** to pace the narrative:

### On Success (roll >= DC)
- Story progresses positively
- Player achieves their goal
- May reveal new information or opportunities

### On Partial Success (roll within 5 of DC but fails)
- "Success with a cost"
- Goal achieved but complication introduced
- OR offered a hard choice

### On Failure (roll < DC - 5)
- "Fail forward" - never "nothing happens"
- Complication introduced
- Enemy acts, situation worsens
- New information revealed (often bad)

---

## 8. Economy Rules

### Currency
- 1 PP (platinum) = 10 GP
- 1 GP (gold) = 10 SP
- 1 SP (silver) = 10 CP

### Transaction Events
```python
class TransactionEvent(BaseModel):
    event_type: Literal["BUY", "SELL", "LOOT", "TRADE"]
    actor: UUID
    counterparty: UUID | None  # None for loot
    items: list[ItemTransfer]
    currency_delta: int        # In copper pieces
```

---

## 9. Rest Mechanics

### Short Rest (1 hour)
- Spend Hit Dice to heal
- Some abilities recharge

### Long Rest (8 hours)
- Regain all HP
- Regain half max Hit Dice (minimum 1)
- Spell slots reset

---

## 10. Implementation Priority

1. **Phase 1**: Dice rolling (`roll_dice`)
2. **Phase 2**: Attack resolution (`resolve_attack`)
3. **Phase 3**: Saving throws and skill checks
4. **Phase 4**: Economy and inventory
5. **Phase 5**: Rest and resource management
