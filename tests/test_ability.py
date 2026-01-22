"""
Tests for the Universal Ability Object (UAO) system.
"""

from __future__ import annotations

import pytest

from src.models.ability import (
    Ability,
    AbilitySource,
    ConditionEffect,
    DamageEffect,
    HealingEffect,
    MagicSubtype,
    MartialSubtype,
    MechanismType,
    StatModifierEffect,
    Targeting,
    TargetingType,
    TechSubtype,
    create_martial_technique,
    create_spell,
    create_tech_ability,
)


class TestDamageEffect:
    """Tests for DamageEffect model."""

    def test_basic_damage(self):
        """Test creating a basic damage effect."""
        damage = DamageEffect(dice="2d6", damage_type="fire")
        assert damage.dice == "2d6"
        assert damage.damage_type == "fire"
        assert damage.save_ability is None
        assert damage.save_for_half is False

    def test_damage_with_save(self):
        """Test damage effect with saving throw."""
        damage = DamageEffect(
            dice="8d6",
            damage_type="fire",
            save_ability="dex",
            save_dc_stat="int",
            save_for_half=True,
        )
        assert damage.save_ability == "dex"
        assert damage.save_dc_stat == "int"
        assert damage.save_for_half is True


class TestHealingEffect:
    """Tests for HealingEffect model."""

    def test_dice_healing(self):
        """Test healing with dice."""
        healing = HealingEffect(dice="2d8+3")
        assert healing.dice == "2d8+3"
        assert healing.flat_amount == 0
        assert healing.temp_hp is False

    def test_flat_healing(self):
        """Test flat amount healing."""
        healing = HealingEffect(flat_amount=10)
        assert healing.dice is None
        assert healing.flat_amount == 10

    def test_temp_hp(self):
        """Test temporary HP healing."""
        healing = HealingEffect(dice="1d10+5", temp_hp=True)
        assert healing.temp_hp is True

    def test_healing_requires_source(self):
        """Test that healing requires either dice or flat_amount."""
        with pytest.raises(ValueError, match="must have either dice or flat_amount"):
            HealingEffect()


class TestConditionEffect:
    """Tests for ConditionEffect model."""

    def test_rounds_duration(self):
        """Test condition with rounds duration."""
        condition = ConditionEffect(
            condition="frightened",
            duration_type="rounds",
            duration_value=3,
        )
        assert condition.condition == "frightened"
        assert condition.duration_type == "rounds"
        assert condition.duration_value == 3

    def test_until_save_duration(self):
        """Test condition that lasts until save."""
        condition = ConditionEffect(
            condition="stunned",
            duration_type="until_save",
            save_ability="con",
            save_dc_stat="wis",
        )
        assert condition.duration_type == "until_save"
        assert condition.save_ability == "con"

    def test_rounds_requires_duration_value(self):
        """Test that rounds duration requires duration_value."""
        with pytest.raises(ValueError, match="duration_value required"):
            ConditionEffect(condition="prone", duration_type="rounds")


class TestStatModifierEffect:
    """Tests for StatModifierEffect model."""

    def test_basic_modifier(self):
        """Test creating a stat modifier."""
        modifier = StatModifierEffect(
            stat="ac",
            modifier=2,
            duration_type="concentration",
        )
        assert modifier.stat == "ac"
        assert modifier.modifier == 2
        assert modifier.duration_type == "concentration"

    def test_negative_modifier(self):
        """Test negative stat modifier."""
        modifier = StatModifierEffect(
            stat="speed",
            modifier=-10,
            duration_type="rounds",
            duration_value=1,
        )
        assert modifier.modifier == -10


class TestTargeting:
    """Tests for Targeting model."""

    def test_self_targeting(self):
        """Test self-targeting."""
        targeting = Targeting(type=TargetingType.SELF)
        assert targeting.type == TargetingType.SELF
        assert targeting.range_ft == 0

    def test_single_target_with_range(self):
        """Test single target with range."""
        targeting = Targeting(
            type=TargetingType.SINGLE,
            range_ft=120,
        )
        assert targeting.type == TargetingType.SINGLE
        assert targeting.range_ft == 120

    def test_area_sphere(self):
        """Test area sphere targeting."""
        targeting = Targeting(
            type=TargetingType.AREA_SPHERE,
            range_ft=150,
            area_size_ft=20,
        )
        assert targeting.type == TargetingType.AREA_SPHERE
        assert targeting.area_size_ft == 20

    def test_area_requires_size(self):
        """Test that area types require area_size_ft."""
        with pytest.raises(ValueError, match="area_size_ft required"):
            Targeting(type=TargetingType.AREA_CONE, range_ft=60)

    def test_multiple_targets(self):
        """Test multiple targets."""
        targeting = Targeting(
            type=TargetingType.MULTIPLE,
            range_ft=30,
            max_targets=3,
        )
        assert targeting.max_targets == 3


class TestAbility:
    """Tests for the core Ability model."""

    def test_basic_ability(self):
        """Test creating a basic ability."""
        ability = Ability(
            name="Test Ability",
            description="A test ability",
            source=AbilitySource.MAGIC,
            mechanism=MechanismType.FREE,
            damage=DamageEffect(dice="1d8", damage_type="force"),
        )
        assert ability.name == "Test Ability"
        assert ability.source == AbilitySource.MAGIC
        assert ability.mechanism == MechanismType.FREE
        assert ability.has_effects() is True

    def test_spell_with_slots(self):
        """Test a spell using spell slots."""
        ability = Ability(
            name="Fireball",
            source=AbilitySource.MAGIC,
            subtype="arcane",
            mechanism=MechanismType.SLOTS,
            mechanism_details={"level": 3},
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
        assert ability.is_spell() is True
        assert ability.is_cantrip() is False
        assert ability.spell_level() == 3
        assert ability.is_area_effect() is True

    def test_cantrip(self):
        """Test a cantrip (level 0 spell)."""
        ability = Ability(
            name="Fire Bolt",
            source=AbilitySource.MAGIC,
            mechanism=MechanismType.FREE,
            damage=DamageEffect(dice="1d10", damage_type="fire"),
            targeting=Targeting(type=TargetingType.SINGLE, range_ft=120),
        )
        assert ability.is_cantrip() is True
        assert ability.spell_level() == 0

    def test_tech_ability(self):
        """Test a tech ability."""
        ability = Ability(
            name="Plasma Cutter",
            source=AbilitySource.TECH,
            subtype="cybertech",
            mechanism=MechanismType.COOLDOWN,
            mechanism_details={"max_uses": 2, "recharge_on_rest": "short"},
            damage=DamageEffect(dice="3d6", damage_type="fire"),
        )
        assert ability.source == AbilitySource.TECH
        assert ability.is_spell() is False
        assert ability.spell_level() is None

    def test_martial_technique(self):
        """Test a martial technique."""
        ability = Ability(
            name="Stunning Strike",
            source=AbilitySource.MARTIAL,
            subtype="ki",
            mechanism=MechanismType.MOMENTUM,
            mechanism_details={"momentum_cost": 2},
            conditions=[
                ConditionEffect(
                    condition="stunned",
                    duration_type="until_save",
                    save_ability="con",
                )
            ],
        )
        assert ability.source == AbilitySource.MARTIAL
        assert ability.has_effects() is True

    def test_mechanism_validation_slots(self):
        """Test that SLOTS mechanism requires level."""
        with pytest.raises(ValueError, match="must include 'level'"):
            Ability(
                name="Bad Spell",
                source=AbilitySource.MAGIC,
                mechanism=MechanismType.SLOTS,
                mechanism_details={},
            )

    def test_mechanism_validation_cooldown(self):
        """Test that COOLDOWN mechanism requires max_uses."""
        with pytest.raises(ValueError, match="must include 'max_uses'"):
            Ability(
                name="Bad Tech",
                source=AbilitySource.TECH,
                mechanism=MechanismType.COOLDOWN,
                mechanism_details={},
            )

    def test_mechanism_validation_usage_die(self):
        """Test that USAGE_DIE mechanism requires die_type."""
        with pytest.raises(ValueError, match="must include 'die_type'"):
            Ability(
                name="Bad Ability",
                source=AbilitySource.TECH,
                mechanism=MechanismType.USAGE_DIE,
                mechanism_details={},
            )

    def test_mechanism_validation_stress(self):
        """Test that STRESS mechanism requires stress_cost."""
        with pytest.raises(ValueError, match="must include 'stress_cost'"):
            Ability(
                name="Bad Technique",
                source=AbilitySource.MARTIAL,
                mechanism=MechanismType.STRESS,
                mechanism_details={},
            )

    def test_mechanism_validation_momentum(self):
        """Test that MOMENTUM mechanism requires momentum_cost."""
        with pytest.raises(ValueError, match="must include 'momentum_cost'"):
            Ability(
                name="Bad Technique",
                source=AbilitySource.MARTIAL,
                mechanism=MechanismType.MOMENTUM,
                mechanism_details={},
            )

    def test_has_effects_with_conditions(self):
        """Test has_effects with only conditions."""
        ability = Ability(
            name="Sleep",
            source=AbilitySource.MAGIC,
            mechanism=MechanismType.SLOTS,
            mechanism_details={"level": 1},
            conditions=[
                ConditionEffect(condition="unconscious", duration_type="minutes", duration_value=1)
            ],
        )
        assert ability.has_effects() is True

    def test_has_effects_with_stat_modifiers(self):
        """Test has_effects with only stat modifiers."""
        ability = Ability(
            name="Shield",
            source=AbilitySource.MAGIC,
            mechanism=MechanismType.SLOTS,
            mechanism_details={"level": 1},
            stat_modifiers=[
                StatModifierEffect(stat="ac", modifier=5, duration_type="rounds", duration_value=1)
            ],
            action_cost="reaction",
        )
        assert ability.has_effects() is True

    def test_no_effects(self):
        """Test ability with no effects."""
        ability = Ability(
            name="Minor Illusion",
            source=AbilitySource.MAGIC,
            mechanism=MechanismType.FREE,
        )
        assert ability.has_effects() is False


class TestCreateSpell:
    """Tests for create_spell factory function."""

    def test_create_cantrip(self):
        """Test creating a cantrip."""
        spell = create_spell(
            name="Fire Bolt",
            level=0,
            description="Hurl a bolt of fire.",
            damage=DamageEffect(dice="1d10", damage_type="fire"),
            targeting=Targeting(type=TargetingType.SINGLE, range_ft=120),
        )
        assert spell.name == "Fire Bolt"
        assert spell.is_cantrip() is True
        assert spell.mechanism == MechanismType.FREE
        assert "spell" in spell.tags

    def test_create_leveled_spell(self):
        """Test creating a leveled spell."""
        spell = create_spell(
            name="Fireball",
            level=3,
            description="A ball of fire explodes at a point.",
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
        assert spell.spell_level() == 3
        assert spell.mechanism == MechanismType.SLOTS
        assert spell.mechanism_details["level"] == 3
        assert spell.subtype == "arcane"

    def test_create_concentration_spell(self):
        """Test creating a concentration spell."""
        spell = create_spell(
            name="Bless",
            level=1,
            subtype=MagicSubtype.DIVINE,
            stat_modifiers=[
                StatModifierEffect(
                    stat="attack_rolls",
                    modifier=4,  # Represented as +1d4 average
                    duration_type="concentration",
                )
            ],
            targeting=Targeting(type=TargetingType.MULTIPLE, range_ft=30, max_targets=3),
            requires_concentration=True,
        )
        assert spell.requires_concentration is True
        assert spell.subtype == "divine"

    def test_create_healing_spell(self):
        """Test creating a healing spell."""
        spell = create_spell(
            name="Cure Wounds",
            level=1,
            subtype=MagicSubtype.DIVINE,
            healing=HealingEffect(dice="1d8+3"),
            targeting=Targeting(type=TargetingType.SINGLE, range_ft=5),
        )
        assert spell.healing is not None
        assert spell.healing.dice == "1d8+3"


class TestCreateTechAbility:
    """Tests for create_tech_ability factory function."""

    def test_create_basic_tech_ability(self):
        """Test creating a basic tech ability."""
        ability = create_tech_ability(
            name="Plasma Cutter",
            description="Fire a concentrated plasma beam.",
            subtype=TechSubtype.CYBERTECH,
            max_uses=2,
            recharge_on_rest="short",
            damage=DamageEffect(dice="3d6", damage_type="fire"),
            targeting=Targeting(type=TargetingType.SINGLE, range_ft=60),
        )
        assert ability.name == "Plasma Cutter"
        assert ability.source == AbilitySource.TECH
        assert ability.subtype == "cybertech"
        assert ability.mechanism == MechanismType.COOLDOWN
        assert ability.mechanism_details["max_uses"] == 2
        assert ability.mechanism_details["recharge_on_rest"] == "short"
        assert "tech" in ability.tags

    def test_create_nanotech_healing(self):
        """Test creating a nanotech healing ability."""
        ability = create_tech_ability(
            name="Nanite Injection",
            description="Deploy healing nanites.",
            subtype=TechSubtype.NANOTECH,
            max_uses=3,
            healing=HealingEffect(dice="2d8+4"),
            targeting=Targeting(type=TargetingType.SINGLE, range_ft=5),
        )
        assert ability.subtype == "nanotech"
        assert ability.healing is not None

    def test_create_tech_with_recharge_roll(self):
        """Test tech ability with recharge on specific die roll."""
        ability = create_tech_ability(
            name="Overcharge",
            description="Release stored energy.",
            max_uses=1,
            recharge_on_rest=None,
            recharge_on=[5, 6],
            damage=DamageEffect(dice="4d10", damage_type="lightning"),
        )
        assert ability.mechanism_details["recharge_on"] == [5, 6]
        assert "recharge_on_rest" not in ability.mechanism_details


class TestCreateMartialTechnique:
    """Tests for create_martial_technique factory function."""

    def test_create_momentum_technique(self):
        """Test creating a momentum-based technique."""
        technique = create_martial_technique(
            name="Stunning Strike",
            description="Channel ki into your strike.",
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
        assert technique.name == "Stunning Strike"
        assert technique.source == AbilitySource.MARTIAL
        assert technique.subtype == "ki"
        assert technique.mechanism == MechanismType.MOMENTUM
        assert technique.mechanism_details["momentum_cost"] == 2
        assert technique.action_cost == "bonus"
        assert "martial" in technique.tags

    def test_create_stress_technique(self):
        """Test creating a stress-based technique."""
        technique = create_martial_technique(
            name="Desperate Lunge",
            description="A risky all-out attack.",
            subtype=MartialSubtype.MANEUVER,
            stress_cost=3,
            damage=DamageEffect(dice="2d8", damage_type="piercing"),
            stat_modifiers=[
                StatModifierEffect(
                    stat="ac",
                    modifier=-2,
                    duration_type="rounds",
                    duration_value=1,
                )
            ],
        )
        assert technique.mechanism == MechanismType.STRESS
        assert technique.mechanism_details["stress_cost"] == 3

    def test_create_free_technique(self):
        """Test creating a free (no cost) technique."""
        technique = create_martial_technique(
            name="Basic Strike",
            description="A standard attack.",
            subtype=MartialSubtype.MANEUVER,
            damage=DamageEffect(dice="1d8", damage_type="slashing"),
        )
        assert technique.mechanism == MechanismType.FREE

    def test_create_stance(self):
        """Test creating a stance technique."""
        technique = create_martial_technique(
            name="Defensive Stance",
            description="Adopt a defensive posture.",
            subtype=MartialSubtype.STANCE,
            stat_modifiers=[
                StatModifierEffect(
                    stat="ac",
                    modifier=2,
                    duration_type="concentration",
                )
            ],
            action_cost="bonus",
        )
        assert technique.subtype == "stance"

    def test_create_combined_cost_technique(self):
        """Test technique with both momentum and stress costs."""
        technique = create_martial_technique(
            name="Ultimate Strike",
            description="The ultimate technique.",
            momentum_cost=3,
            stress_cost=2,
            damage=DamageEffect(dice="6d10", damage_type="force"),
        )
        # Primary mechanism is momentum, but stress_cost is also included
        assert technique.mechanism == MechanismType.MOMENTUM
        assert technique.mechanism_details["momentum_cost"] == 3
        assert technique.mechanism_details["stress_cost"] == 2
