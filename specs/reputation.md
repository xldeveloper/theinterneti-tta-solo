# Spec: Faction Reputation Tracking

## Overview

Track player-faction reputation as a numeric score stored on the character entity.
Reputation changes come from quest rewards and are displayed via `/reputation`.

## Storage

Reputation lives on `EntityStats.faction_reputations: dict[str, int]` (Dolt — it's truth).
Keys are faction entity UUID strings; values are integer scores (default 0, unbounded).

## Tier Labels

| Score Range   | Tier       |
|---------------|------------|
| >= 50         | Honored    |
| >= 20         | Friendly   |
| -19 to 19     | Neutral    |
| -49 to -20    | Unfriendly |
| <= -50        | Hostile    |

## Application

When a quest completes with `QuestReward.reputation_changes`, the `ReputationService`:
1. Loads the character entity
2. Adds each delta to `faction_reputations[faction_uuid_str]`
3. Saves the character entity back to Dolt
4. Returns a list of `ReputationChange` results for display

## Display

- `/reputation` (aliases: `rep`, `factions`) — table of all faction standings
- `/status` — one-line summary if any faction reputations exist
- Quest completion notifications show reputation changes inline

## Inputs

- `character_id: UUID` — the player character
- `universe_id: UUID` — current universe
- `changes: dict[UUID, int]` — faction ID to delta

## Outputs

- `ReputationChange` — faction_id, faction_name, old_score, new_score, delta, tier
- `FactionStanding` — faction_id, faction_name, score, tier
