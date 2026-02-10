"""Tests for faction reputation tracking."""

from __future__ import annotations

from uuid import uuid4

from src.db.memory import InMemoryDoltRepository
from src.models.entity import Entity, EntityStats, create_character, create_faction
from src.services.reputation import (
    ReputationService,
    get_reputation_tier,
)

# --- Tier tests ---


def test_tier_hostile():
    assert get_reputation_tier(-50) == "Hostile"
    assert get_reputation_tier(-100) == "Hostile"


def test_tier_unfriendly():
    assert get_reputation_tier(-49) == "Unfriendly"
    assert get_reputation_tier(-20) == "Unfriendly"


def test_tier_neutral():
    assert get_reputation_tier(-19) == "Neutral"
    assert get_reputation_tier(0) == "Neutral"
    assert get_reputation_tier(19) == "Neutral"


def test_tier_friendly():
    assert get_reputation_tier(20) == "Friendly"
    assert get_reputation_tier(49) == "Friendly"


def test_tier_honored():
    assert get_reputation_tier(50) == "Honored"
    assert get_reputation_tier(100) == "Honored"


# --- Service tests ---


def _setup() -> tuple[InMemoryDoltRepository, Entity, Entity, Entity]:
    """Create a dolt repo with a character and two factions."""
    dolt = InMemoryDoltRepository()
    universe_id = uuid4()

    character = create_character(universe_id=universe_id, name="Hero", hp_max=20)
    faction_a = create_faction(universe_id=universe_id, name="Iron Guild")
    faction_b = create_faction(universe_id=universe_id, name="Shadow Court")

    dolt.save_entity(character)
    dolt.save_entity(faction_a)
    dolt.save_entity(faction_b)

    return dolt, character, faction_a, faction_b


def test_apply_positive_reputation():
    dolt, char, faction_a, _ = _setup()
    service = ReputationService(dolt)

    changes = service.apply_reputation_changes(char.id, char.universe_id, {faction_a.id: 10})

    assert len(changes) == 1
    assert changes[0].delta == 10
    assert changes[0].old_score == 0
    assert changes[0].new_score == 10
    assert changes[0].faction_name == "Iron Guild"
    assert changes[0].tier == "Neutral"

    # Verify persisted
    updated = dolt.get_entity(char.id, char.universe_id)
    assert updated.stats.faction_reputations[str(faction_a.id)] == 10


def test_apply_negative_reputation():
    dolt, char, faction_a, _ = _setup()
    service = ReputationService(dolt)

    changes = service.apply_reputation_changes(char.id, char.universe_id, {faction_a.id: -25})

    assert changes[0].new_score == -25
    assert changes[0].tier == "Unfriendly"


def test_apply_multiple_factions():
    dolt, char, faction_a, faction_b = _setup()
    service = ReputationService(dolt)

    changes = service.apply_reputation_changes(
        char.id, char.universe_id, {faction_a.id: 20, faction_b.id: -5}
    )

    assert len(changes) == 2
    names = {c.faction_name for c in changes}
    assert names == {"Iron Guild", "Shadow Court"}

    updated = dolt.get_entity(char.id, char.universe_id)
    assert updated.stats.faction_reputations[str(faction_a.id)] == 20
    assert updated.stats.faction_reputations[str(faction_b.id)] == -5


def test_apply_stacks_with_existing():
    dolt, char, faction_a, _ = _setup()
    service = ReputationService(dolt)

    service.apply_reputation_changes(char.id, char.universe_id, {faction_a.id: 10})
    changes = service.apply_reputation_changes(char.id, char.universe_id, {faction_a.id: 15})

    assert changes[0].old_score == 10
    assert changes[0].new_score == 25
    assert changes[0].tier == "Friendly"


def test_get_standings():
    dolt, char, faction_a, faction_b = _setup()
    service = ReputationService(dolt)

    service.apply_reputation_changes(
        char.id, char.universe_id, {faction_a.id: 50, faction_b.id: -10}
    )

    standings = service.get_standings(char.id, char.universe_id)
    assert len(standings) == 2

    by_name = {s.faction_name: s for s in standings}
    assert by_name["Iron Guild"].score == 50
    assert by_name["Iron Guild"].tier == "Honored"
    assert by_name["Shadow Court"].score == -10
    assert by_name["Shadow Court"].tier == "Neutral"


def test_get_standings_empty():
    dolt, char, _, _ = _setup()
    service = ReputationService(dolt)

    standings = service.get_standings(char.id, char.universe_id)
    assert standings == []


def test_apply_to_missing_character():
    dolt = InMemoryDoltRepository()
    service = ReputationService(dolt)

    changes = service.apply_reputation_changes(uuid4(), uuid4(), {uuid4(): 10})
    assert changes == []


def test_entity_stats_default_faction_reputations():
    """Backwards compat: EntityStats without faction_reputations still works."""
    stats = EntityStats(hp_current=10, hp_max=10)
    assert stats.faction_reputations == {}


def test_entity_stats_with_faction_reputations():
    fid = str(uuid4())
    stats = EntityStats(hp_current=10, hp_max=10, faction_reputations={fid: 25})
    assert stats.faction_reputations[fid] == 25


def test_entity_stats_serialization_roundtrip():
    """faction_reputations survives JSON round-trip."""
    fid = str(uuid4())
    stats = EntityStats(hp_current=10, hp_max=10, faction_reputations={fid: -30})
    data = stats.model_dump()
    restored = EntityStats(**data)
    assert restored.faction_reputations[fid] == -30
