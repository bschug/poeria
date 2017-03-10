import json
import re
from collections import defaultdict, Counter

from constants import itemtype


class Affix(object):
    """
    A set of method generators to parse values from a single property description.
    """
    @staticmethod
    def text(text):
        """
        Return 1 if the text matches exactly, otherwise 0.
        """
        return lambda x: 1 if x == text else 0

    @staticmethod
    def int(expr):
        """
        Returns the value of the first match group of the regex, or 0.
        """
        return lambda x: int(Affix._regex(expr, x, '0'))

    @staticmethod
    def float(expr):
        """
        Returns the value of the first match group of the regex, or 0.
        """
        return lambda x: float(Affix._regex(expr, x, '0'))

    @staticmethod
    def _regex(expr, mod_text, default_value):
        try:
            match = re.match(expr, mod_text)
            return default_value if match is None else match.group(1)
        except:
            print("BAD REGEX:", expr)
            raise

    @staticmethod
    def range(expr):
        """
        For mods that specify a range (e.g. Adds 3-9 Physical Damage to Attacks),
        this returns the sum of the upper and lower bound of the range (i.e. twice
        the average). We don't return the average because we work with integers and
        can't have halves.
        :param expr: regular expression with two match groups
        """
        return lambda x: Affix._range(expr, x)

    @staticmethod
    def _range(expr, mod_text):
        match = re.match(expr, mod_text)
        return 0 if match is None else int(match.group(1)) + int(match.group(2))

    @staticmethod
    def granted_skill_id():
        """Returns skill id (see SKILLS) of granted skill, or 0."""
        return lambda x: Affix._granted_skill(x)[0]

    @staticmethod
    def granted_skill_level():
        """Returns level of granted skill, or 0."""
        return lambda x: Affix._granted_skill(x)[1]

    @staticmethod
    def _granted_skill(mod_text):
        match = re.match("Grants level (\d+) ([a-zA-Z\ \']+) Skill", mod_text)
        if match is None:
            return (0, 0)

        return get_skill_id(match.group(2)), int(match.group(1))


class AffixCombine(object):
    """
    Method generators for combining stats with each other.
    """
    @staticmethod
    def restrict_to_one(affix_id):
        """
        For affixes that can't be combined. Will raise an error if the same appears more
        than once.
        """
        return lambda x, y: AffixCombine._restrict_to_one(x, y, affix_id)

    @staticmethod
    def _restrict_to_one(old, new, affix_id):
        if old is 0:
            return new
        if new is 0:
            return old
        raise Exception('Cannot have more than one {} on the same item'.format(affix_id))

    @staticmethod
    def scale(factor):
        """
        Scales new values by the given factor before adding them to the old one.
        This is useful for non-integer attributes like life leech, to bring them into
        integer range.
        """
        return lambda old, new: old + int(factor * new)

    @staticmethod
    def boolean_or():
        """
        For boolean fields, the parser returns 0 or 1, but the dictionary must store
        true or false. This interprets 0 and 1 as False and True and aggregates with
        a boolean OR operation.
        """
        return lambda old, new: old or (new == 1)


def parse_implicit_mods(item, item_type, stats, parsers, ignored=None, banned=None, aggregators=None):
    if 'implicitMods' not in item:
        return
    parse_mods(item['implicitMods'], item_type, 'implicit', stats, parsers,
               ignored=ignored, banned=banned, aggregators=aggregators)


def parse_explicit_mods(item, item_type, stats, parsers, ignored=None, banned=None, aggregators=None):
    if 'explicitMods' not in item:
        return
    parse_mods(item['explicitMods'], item_type, 'explicit', stats, parsers,
               ignored=ignored, banned=banned, aggregators=aggregators)


def parse_mods(mods, item_type, mod_type, stats, parsers, ignored=None, banned=None, aggregators=None):
    """
    Parses the mods in the list.
    Each mod must be covered either by one of the rules in the parsed list or
    in the ignored list. Otherwise an exception will be thrown.
    If any of the mods matches anything in the banned list, an exception will also be thrown.

    Parser functions always take a mod text as input. They return None if the text doesn't
    match their rules, or a value if they could parse something.

    Multiple parser methods can match the same mod. In that case, all of them will be
    executed and their results added together (unless another aggregation rule is defined).

    Aggregators always take and old value and a new values as input and return an
    aggregation of both. If no special aggregator is defined, the operator + is used
    by default.

    :param item:    Item to be parsed (dict, as parsed from poe api json)
    :param stats:   Stats parsed so far (dict of stat id -> value)
    :param parsed:  List of tuples (stat id, parser function)
    :param ignored: List of regular expressions for mods we consciously ignore (optional)
    :param banned:  List of regular expressions for mods we don't want in the data set.
    :param aggregators: List of aggregator functions
    """
    if banned is not None:
        banned = [re.compile(x) for x in banned]
    if ignored is not None:
        ignored = [re.compile(x) for x in ignored]

    for mod_text in mods:
        # If this mod matches any of the banned rules, throw an exception
        if banned is not None and any(x.match(mod_text) is not None for x in banned):
            raise ItemBannedException(item_type, mod_text)

        # If this mod matches any of the ignore rules, skip it
        if ignored is not None and any(x.match(mod_text) is not None for x in ignored):
            continue

        num_matches = 0

        # Run all parsers
        for stat_id, parser in parsers:
            value = parser(mod_text)

            # If parser returned 0, ignore
            if value == 0:
                continue

            # Count number of matching parsers to see if we recognized this mod
            num_matches += 1

            # Aggregate new value
            old_value = stats.get(stat_id, 0)
            if aggregators is not None and stat_id in aggregators:
                new_value = aggregators[stat_id](old_value, value)
            else:
                new_value = old_value + value

            stats[stat_id] = new_value

        # Raise an exception if we have no idea what this mod is about
        if num_matches == 0:
            raise ItemParserException("Couldn't parse {} {} mod: {}".format(
                mod_type, item_type, mod_text))


def parse_ring(item):
    stats = Counter()
    stats['DoubledInBreach'] = False
    parse_corrupted(item, stats)
    parse_sockets(item, stats)
    parse_requirements(item, stats)
    parse_implicit_mods(
        item, 'Ring', stats,
        parsers=[
            ('DoubledInBreach', Affix.text('Properties are doubled while in a Breach')),
            ('Life', Affix.int('\+(\d+) to maximum Life')),
            ('AddedPhysAttackDamage', Affix.range('Adds (\d+) to (\d+) Physical Damage to Attacks')),
            ('Mana', Affix.int('\+(\d+) to maximum Mana')),
            ('FireResist', Affix.int('\+(\d+)% to Fire Resistance')),
            ('ColdResist', Affix.int('\+(\d+)% to Cold Resistance')),
            ('LightningResist', Affix.int('\+(\d+)% to Lightning Resistance')),
            ('FireResist', Affix.int('\+(\d+)% to Fire and Cold Resistances')),
            ('ColdResist', Affix.int('\+(\d+)% to Fire and Cold Resistances')),
            ('FireResist', Affix.int('\+(\d+)% to Fire and Lightning Resistances')),
            ('LightningResist', Affix.int('\+(\d+)% to Fire and Lightning Resistances')),
            ('ColdResist', Affix.int('\+(\d+)% to Cold and Lightning Resistances')),
            ('LightningResist', Affix.int('\+(\d+)% to Cold and Lightning Resistances')),
            ('FireResist', Affix.int('\+(\d+)% to all Elemental Resistances')),
            ('ColdResist', Affix.int('\+(\d+)% to all Elemental Resistances')),
            ('LightningResist', Affix.int('\+(\d+)% to all Elemental Resistances')),
            ('CritChance', Affix.int('(\d+)% increased Global Critical Strike Chance')),
            ('ItemRarity', Affix.int('(\d+)% increased Rarity of Items found')),
            ('EnergyShield', Affix.int('\+(\d+) to maximum Energy Shield')),
            ('ChaosResist', Affix.int('\+(\d+)% to Chaos Resistance')),
            ('IncreasedEleDamage', Affix.int('(\d+)% increased Elemental Damage')),
            # Corrupted Implicits
            ('CastSpeed', Affix.int('(\d+)% increased Cast Speed')),
            ('AddedChaosAttackDamage', Affix.range('Adds (\d+) to (\d+) Chaos Damage to Attacks')),
            ('IncreasedWeaponEleDamage', Affix.int('(\d+)% increased Elemental Damage with Weapons')),
            ('DamageToMana', Affix.int('(\d+)% of Damage taken gained as Mana when Hit')),
            ('AvoidFreeze', Affix.int('(\d+)% chance to Avoid being Frozen')),
            ('GrantedSkillId', Affix.granted_skill_id()),
            ('GrantedSkillLevel', Affix.granted_skill_level()),
            ('ManaGainOnHit', Affix.int('\+(\d+) Mana gained for each Enemy hit by your Attacks'))
        ],
        ignored=[
            'Has 1 Socket'
        ],
        aggregators={
            'DoubledInBreach': AffixCombine.boolean_or(),
            'GrantedSkillId': AffixCombine.restrict_to_one('GrantedSkill'),
            'GrantedSkillLevel': AffixCombine.restrict_to_one('GrantedSkill'),
        }
    )
    parse_explicit_mods(
        item, 'Ring', stats,
        parsers=[
            # Prefix
            ('AddedColdAttackDamage', Affix.range('Adds (\d+) to (\d+) Cold Damage to Attacks')),
            ('AddedFireAttackDamage', Affix.range('Adds (\d+) to (\d+) Fire Damage to Attacks')),
            ('AddedLightningAttackDamage', Affix.range('Adds (\d+) to (\d+) Lightning Damage to Attacks')),
            ('AddedPhysAttackDamage', Affix.range('Adds (\d+) to (\d+) Physical Damage to Attacks')),
            ('EnergyShield', Affix.int('\+(\d+) to maximum Energy Shield')),
            ('Evasion', Affix.int('\+(\d+) to Evasion Rating')),
            ('Life', Affix.int('\+(\d+) to maximum Life')),
            ('Mana', Affix.int('\+(\d+) to maximum Mana')),
            ('IncreasedWeaponEleDamage', Affix.int('(\d+)% increased Elemental Damage with Weapons')),
            ('ItemRarity', Affix.int('(\d+)% increased Rarity of Items found')),
            ('LifeLeech', Affix.float('(\d+(\.\d+)?)% of Physical Attack Damage Leeched as Life')),
            ('ManaLeech', Affix.float('(\d+(\.\d+)?)% of Physical Attack Damage Leeched as Mana')),
            # Suffix
            ('Strength', Affix.int('\+(\d+) to all Attributes')),
            ('Dexterity', Affix.int('\+(\d+) to all Attributes')),
            ('Intelligence', Affix.int('\+(\d+) to all Attributes')),
            ('Strength', Affix.int('\+(\d+) to Strength')),
            ('Dexterity', Affix.int('\+(\d+) to Dexterity')),
            ('Intelligence', Affix.int('\+(\d+) to Intelligence')),
            ('FireResist', Affix.int('\+(\d+)% to Fire Resistance')),
            ('ColdResist', Affix.int('\+(\d+)% to Cold Resistance')),
            ('LightningResist', Affix.int('\+(\d+)% to Lightning Resistance')),
            ('FireResist', Affix.int('\+(\d+)% to all Elemental Resistances')),
            ('ColdResist', Affix.int('\+(\d+)% to all Elemental Resistances')),
            ('LightningResist', Affix.int('\+(\d+)% to all Elemental Resistances')),
            ('ChaosResist', Affix.int('\+(\d+)% to Chaos Resistance')),
            ('IncreasedFireDamage', Affix.int('(\d+)% increased Fire Damage')),
            ('IncreasedColdDamage', Affix.int('(\d+)% increased Cold Damage')),
            ('IncreasedLightningDamage', Affix.int('(\d+)% increased Lightning Damage')),
            ('Accuracy', Affix.int('\+(\d+) to Accuracy Rating')),
            ('AttackSpeed', Affix.int('(\d+)% increased Attack Speed')),
            ('CastSpeed', Affix.int('(\d+)% increased Cast Speed')),
            ('LifeGainOnHit', Affix.int('\+(\d+) Life gained for each Enemy hit by your Attacks')),
            ('LifeGainOnKill', Affix.int('\+(\d+) Life gained on Kill')),
            ('LifeRegen', Affix.float('(\d+(\.\d)?) Life Regenerated per second')),
            ('LightRadius', Affix.int('(\d+)% increased Light Radius')),
            ('IncreasedAccuracy', Affix.int('(\d+)% increased Accuracy Rating')),
            ('ManaGainOnKill', Affix.int('\+(\d+) Mana gained on Kill')),
            ('ManaRegen', Affix.int('(\d+)% increased Mana Regeneration Rate')),
            ('SocketedGemLevel', Affix.int('\+(\d+) to Level of Socketed Gems'))
        ],
        banned=[
            # Master signature mods:
            '\-(\d+) to Mana Cost of Skills',
            '(\d+)% increased Damage',
            # Essence only:
            '(\d+)% increased Chaos Damage',
            '\+(\d+)% to Global Critical Strike Multiplier',
            '(\d+)% increased Global Critical Strike Chance',
            '(\d+)% increased Quantity of Items found',
            'Gain (\d+)% of Physical Damage as Extra Fire Damage',
            'Minions have (\d+)% increased Movement Speed',
            '\+\d+ to Armour',
            '\d+% reduced Reflected Damage taken',
            'Adds \d+ to \d+ Cold Damage per Frenzy Charge',
        ],
        aggregators={
            'LifeLeech': AffixCombine.scale(100),
            'ManaLeech': AffixCombine.scale(100),
            'LifeRegen': AffixCombine.scale(10),
        }
    )
    return stats


def parse_amulet(item):
    stats = Counter()
    parse_corrupted(item, stats)
    parse_requirements(item, stats)
    parse_implicit_mods(
        item, 'Amulet', stats,
        parsers=[
            ('LifeRegen', Affix.float('(\d+(\.\d+)?) Life Regenerated per second')),
            ('ManaRegen', Affix.int('(\d+)% increased Mana Regeneration Rate')),
            ('Strength', Affix.int('\+(\d+) to Strength')),
            ('Dexterity', Affix.int('\+(\d+) to Dexterity')),
            ('Intelligence', Affix.int('\+(\d+) to Intelligence')),
            ('ItemRarity', Affix.int('(\d+)% increased Rarity of Items found')),
            ('Strength', Affix.int('\+(\d+) to Strength and Intelligence')),
            ('Intelligence', Affix.int('\+(\d+) to Strength and Intelligence')),
            ('Strength', Affix.int('\+(\d+) to Strength and Dexterity')),
            ('Dexterity', Affix.int('\+(\d+) to Strength and Dexterity')),
            ('Dexterity', Affix.int('\+(\d+) to Dexterity and Intelligence')),
            ('Intelligence', Affix.int('\+(\d+) to Dexterity and Intelligence')),
            ('Strength', Affix.int('\+(\d+) to all Attributes')),
            ('Dexterity', Affix.int('\+(\d+) to all Attributes')),
            ('Intelligence', Affix.int('\+(\d+) to all Attributes')),
            ('IncreasedLifeRegen', Affix.float('(\d+(\.\d+)?)% of Life Regenerated per second')),
            # Corrupted Implicits
            ('AdditionalCurses', Affix.int('Enemies can have (\d) additional Curse[s]?')),
            ('AvoidIgnite', Affix.int('(\d+)% chance to Avoid being Ignited')),
            ('BlockChance', Affix.int('(\d+)% Chance to Block')),
            ('AvoidFreeze', Affix.int('(\d+)% chance to Avoid being Frozen')),
            ('ChaosResist', Affix.int('\+(\d+)% to Chaos Resistance')),
            ('LifeLeechCold', Affix.float('(\d(\.\d+)?)% of Cold Damage Leeched as Life')),
            ('LifeLeechFire', Affix.float('(\d(\.\d+)?)% of Fire Damage Leeched as Life')),
            ('GrantedSkillId', Affix.granted_skill_id()),
            ('GrantedSkillLevel', Affix.granted_skill_level()),
            ('AttackSpeed', Affix.int('(\d+)% increased Attack Speed')),
            ('IncreasedWeaponEleDamage', Affix.int('(\d+)% increased Elemental Damage with Weapons')),
            ('LifeLeechLightning', Affix.float('(\d(\.\d+)?)% of Lightning Damage Leeched as Life')),
            ('MaxFrenzyCharges', Affix.int('\+(\d+) to Maximum Frenzy Charges')),
            ('MaxResists', Affix.int('\+(\d+)% to all maximum Resistances')),
            ('MinionDamage', Affix.int('Minions deal (\d+)% increased Damage')),
            ('MoveSpeed', Affix.int('(\d+)% increased Movement Speed')),
            ('DamageToMana', Affix.int('(\d+)% of Damage taken gained as Mana when Hit')),
            ('PhysDamageReduction', Affix.int('\-(\d+) Physical Damage taken from Attacks')),
            ('SpellBlock', Affix.int('(\d+)% Chance to Block Spells'))
        ],
        aggregators={
            'LifeRegen': AffixCombine.scale(10),
            'IncreasedLifeRegen': AffixCombine.scale(10),
            'ColdLifeLeech': AffixCombine.scale(100),
            'FireLifeLeech': AffixCombine.scale(100),
            'LightningLifeLeech': AffixCombine.scale(100),
            'GrantedSkillId': AffixCombine.restrict_to_one('GrantedSkill'),
            'GrantedSkillLevel': AffixCombine.restrict_to_one('GrantedSkill'),
        }
    )
    parse_explicit_mods(
        item, 'Amulet', stats,
        parsers=[
            # Prefix
            ('AddedColdAttackDamage', Affix.range('Adds (\d+) to (\d+) Cold Damage to Attacks')),
            ('AddedFireAttackDamage', Affix.range('Adds (\d+) to (\d+) Fire Damage to Attacks')),
            ('AddedLightningAttackDamage', Affix.range('Adds (\d+) to (\d+) Lightning Damage to Attacks')),
            ('AddedPhysAttackDamage', Affix.range('Adds (\d+) to (\d+) Physical Damage to Attacks')),
            ('IncreasedEnergyShield', Affix.int('(\d+)% increased maximum Energy Shield')),
            ('IncreasedEvasion', Affix.int('(\d+)% increased Evasion Rating')),
            ('EnergyShield', Affix.int('\+(\d+) to maximum Energy Shield')),
            ('Life', Affix.int('\+(\d+) to maximum Life')),
            ('Mana', Affix.int('\+(\d+) to maximum Mana')),
            ('IncreasedArmour', Affix.int('(\d+)% increased Armour')),
            ('IncreasedWeaponEleDamage', Affix.int('(\d+)% increased Elemental Damage with Weapons')),
            ('ItemRarity', Affix.int('(\d+)% increased Rarity of Items found')),
            ('LifeLeech', Affix.float('(\d+(\.\d+)?)% of Physical Attack Damage Leeched as Life')),
            ('ManaLeech', Affix.float('(\d+(\.\d+)?)% of Physical Attack Damage Leeched as Mana')),
            ('SpellDamage', Affix.int('(\d+)% increased Spell Damage')),
            # Suffix
            ('Strength', Affix.int('\+(\d+) to all Attributes')),
            ('Dexterity', Affix.int('\+(\d+) to all Attributes')),
            ('Intelligence', Affix.int('\+(\d+) to all Attributes')),
            ('FireResist', Affix.int('\+(\d+)% to all Elemental Resistances')),
            ('ColdResist', Affix.int('\+(\d+)% to all Elemental Resistances')),
            ('LightningResist', Affix.int('\+(\d+)% to all Elemental Resistances')),
            ('FireResist', Affix.int('\+(\d+)% to Fire Resistance')),
            ('ColdResist', Affix.int('\+(\d+)% to Cold Resistance')),
            ('LightningResist', Affix.int('\+(\d+)% to Lightning Resistance')),
            ('ChaosResist', Affix.int('\+(\d+)% to Chaos Resistance')),
            ('CritChance', Affix.int('(\d+)% increased Global Critical Strike Chance')),
            ('CritMulti', Affix.int('\+(\d+)% to Global Critical Strike Multiplier')),
            ('Strength', Affix.int('\+(\d+) to Strength')),
            ('Dexterity', Affix.int('\+(\d+) to Dexterity')),
            ('Intelligence', Affix.int('\+(\d+) to Intelligence')),
            ('IncreasedFireDamage', Affix.int('(\d+)% increased Fire Damage')),
            ('IncreasedColdDamage', Affix.int('(\d+)% increased Cold Damage')),
            ('IncreasedLightningDamage', Affix.int('(\d+)% increased Lightning Damage')),
            ('Accuracy', Affix.int('\+(\d+) to Accuracy Rating')),
            ('CastSpeed', Affix.int('(\d+)% increased Cast Speed')),
            ('LifeGainOnHit', Affix.int('\+(\d+) Life gained for each Enemy hit by your Attacks')),
            ('LifeGainOnKill', Affix.int('\+(\d+) Life gained on Kill')),
            ('LifeRegen', Affix.float('(\d+(\.\d)?) Life Regenerated per second')),
            ('ManaGainOnKill', Affix.int('\+(\d+) Mana gained on Kill')),
            ('ManaRegen', Affix.int('(\d+)% increased Mana Regeneration Rate')),
        ],
        aggregators={
            'LifeLeech': AffixCombine.scale(100),
            'ManaLeech': AffixCombine.scale(100),
            'LifeRegen': AffixCombine.scale(10),
        },
        banned={
            # Master signature mods
            '\-\d+ to Mana Cost of Skills',
            # Essence only
            '(\d+)% increased Chaos Damage',
            '\d+% increased Life Leeched per second',
            'Minions have \d+% increased Movement Speed',
            '\d+% increased effect of Fortify on You',
            '\d+% increased Attack Speed',
            # Deprecated stats
            '\d+% increased Quantity of Items found',
        }
    )
    return stats


def parse_body(item):
    stats = Counter()
    stats['CannotBeKnockedBack'] = False
    parse_sockets(item, stats)
    parse_corrupted(item, stats)
    parse_defenses(item, stats)
    parse_requirements(item, stats)
    parse_implicit_mods(
        item, 'BodyArmour', stats,
        parsers=[
            ('Mana', Affix.int('\+(\d+) to maximum Mana')),
            ('SpellDamage', Affix.int('(\d+)% increased Spell Damage')),
            ('MoveSpeed', Affix.int('(\d+)% increased Movement Speed')),
            ('FireResist', Affix.int('\+(\d+)% to all Elemental Resistances')),
            ('ColdResist', Affix.int('\+(\d+)% to all Elemental Resistances')),
            ('LightningResist', Affix.int('\+(\d+)% to all Elemental Resistances')),
            # Corrupted
            ('AvoidFreeze', Affix.int('(\d+)% chance to Avoid being Frozen')),
            ('AvoidIgnite', Affix.int('(\d+)% chance to Avoid being Ignited')),
            ('ChaosResist', Affix.int('\+(\d+)% to Chaos Resistance')),
            ('GrantedSkillId', Affix.granted_skill_id()),
            ('GrantedSkillLevel', Affix.granted_skill_level()),
            ('CannotBeKnockedBack', Affix.text('Cannot be Knocked Back')),
            ('SocketedGemLevel', Affix.int('\+(\d+) to Level of Socketed Gems')),
            ('SocketedVaalGemLevel', Affix.int('\+(\d+) to Level of Socketed Vaal Gems')),
            ('MaxResists', Affix.int('\+(\d+)% to all maximum Resistances')),
            ('AvoidShock', Affix.int('(\d+)% chance to Avoid being Shocked')),
            ('ManaMultiplier', Affix.int('Socketed Skill Gems get a (\d+)% Mana Multiplier'))
        ],
        aggregators={
            'CannotBeKnockedBack': AffixCombine.boolean_or(),
            'GrantedSkillId': AffixCombine.restrict_to_one('GrantedSkill'),
            'GrantedSkillLevel': AffixCombine.restrict_to_one('GrantedSkill'),
        },
        ignored={
            '\d% reduced Movement Speed'
        },
    )
    parse_explicit_mods(
        item, 'BodyArmour', stats,
        parsers=[
            # Prefix
            ('PhysReflect', Affix.int('Reflects (\d+) Physical Damage to Melee Attackers')),
            ('StunRecovery', Affix.int('(\d+)% increased Stun and Block Recovery')),
            ('Life', Affix.int('\+(\d+) to maximum Life')),
            ('Mana', Affix.int('\+(\d+) to maximum Mana')),
            # Suffix
            ('ChaosResist', Affix.int('\+(\d+)% to Chaos Resistance')),
            ('FireResist', Affix.int('\+(\d+)% to Fire Resistance')),
            ('ColdResist', Affix.int('\+(\d+)% to Cold Resistance')),
            ('LightningResist', Affix.int('\+(\d+)% to Lightning Resistance')),
            ('LifeRegen', Affix.float('(\d+(\.\d)?) Life Regenerated per second')),
            ('Strength', Affix.int('\+(\d+) to Strength')),
            ('Dexterity', Affix.int('\+(\d+) to Dexterity')),
            ('Intelligence', Affix.int('\+(\d+) to Intelligence')),
        ],
        ignored={
            '\d+% increased Armour',
            '\d+% increased Evasion Rating',
            '\d+% increased Energy Shield',
            '\d+% increased Armour and Evasion',
            '\d+% increased Armour and Energy Shield',
            '\d+% increased Evasion and Energy Shield',
            '\d+% increased Armour, Evasion and Energy Shield',
            '\+\d+ to Armour',
            '\+\d+ to Evasion',
            '\+\d+ to maximum Energy Shield',
            '\d+% reduced Attribute Requirements',
        },
        banned={
            # Essence
            'Gain Onslaught for 3 seconds when Hit',
            'Minions have \d+% increased maximum Life',
            '\d+% increased Area of Effect of Area Skills',
            '\d+% chance to Avoid (Lightning|Cold|Fire) Damage when Hit',
            '\d+% of Physical Damage taken as Cold Damage',
            '\d+% chance to Dodge Attacks',
            '\d+% chance to Dodge Spell Damage',
        }
    )
    return stats


def parse_helmet(item):
    if is_enchanted(item):
        raise ItemBannedException('Item is enchanted', item['enchantMods'][0])

    stats = Counter()
    stats['EnemiesCannotLeech'] = False
    parse_sockets(item, stats)
    parse_corrupted(item, stats)
    parse_defenses(item, stats)
    parse_requirements(item, stats)
    parse_implicit_mods(
        item, 'Helmet', stats,
        parsers=[
            ('MinionDamage', Affix.int('Minions deal (\d+)% increased Damage')),
            # Corrupted:
            ('ChaosResist', Affix.int('\+(\d+)% to Chaos Resistance')),
            ('ManaShield', Affix.int('When Hit, (\d+)% of Damage is taken from Mana before Life')),
            ('EnemiesCannotLeech', Affix.text('Enemies Cannot Leech Life From You')),
            ('GrantedSkillId', Affix.granted_skill_id()),
            ('GrantedSkillLevel', Affix.granted_skill_level()),
            ('SocketedVaalGemLevel', Affix.int('\+(\d+) to Level of Socketed Vaal Gems')),
            ('SupportedByCastOnCrit', Affix.int('Socketed Gems are supported by level (\d+) Cast On Crit')),
            ('SupportedByCastOnStun', Affix.int('Socketed Gems are supported by level (\d+) Cast when Stunned'))
        ],
        aggregators={
            'EnemiesCannotLeech': AffixCombine.boolean_or(),
            'GrantedSkillId': AffixCombine.restrict_to_one('GrantedSkill'),
            'GrantedSkillLevel': AffixCombine.restrict_to_one('GrantedSkill'),
        }
    )
    parse_explicit_mods(
        item, 'Helmet', stats,
        parsers = [
            # Prefix
            ('PhysReflect', Affix.int('Reflects (\d+) Physical Damage to Melee Attackers')),
            ('StunRecovery', Affix.int('(\d+)% increased Stun and Block Recovery')),
            ('SocketedMinionGemLevel', Affix.int('\+(\d+) to Level of Socketed Minion Gems')),
            ('Life', Affix.int('\+(\d+) to maximum Life')),
            ('Mana', Affix.int('\+(\d+) to maximum Mana')),
            ('ItemRarity', Affix.int('(\d+)% increased Rarity of Items found')),
            # Suffix
            ('ChaosResist', Affix.int('\+(\d+)% to Chaos Resistance')),
            ('ColdResist', Affix.int('\+(\d+)% to Cold Resistance')),
            ('Dexterity', Affix.int('\+(\d+) to Dexterity')),
            ('FireResist', Affix.int('\+(\d+)% to Fire Resistance')),
            ('Accuracy', Affix.int('\+(\d+) to Accuracy Rating')),
            ('IncreasedAccuracy', Affix.int('(\d+)% increased Accuracy Rating')),
            ('Intelligence', Affix.int('\+(\d+) to Intelligence')),
            ('LifeRegen', Affix.float('(\d+(\.\d)?) Life Regenerated per second')),
            ('LightRadius', Affix.int('(\d+)% increased Light Radius')),
            ('LightningResist', Affix.int('\+(\d+)% to Lightning Resistance')),
            ('Strength', Affix.int('\+(\d+) to Strength')),
            ('StunRecovery', Affix.int('(\d+)% increased Stun and Block Recovery')),
        ],
        ignored={
            '\d+% increased Armour',
            '\d+% increased Evasion Rating',
            '\d+% increased Energy Shield',
            '\d+% increased Armour and Evasion',
            '\d+% increased Armour and Energy Shield',
            '\d+% increased Evasion and Energy Shield',
            '\d+% increased Armour, Evasion and Energy Shield',
            '\+\d+ to Armour',
            '\+\d+ to Evasion',
            '\+\d+ to maximum Energy Shield',
            '\d+% reduced Attribute Requirements',
        },
        banned={
            # Essences
            'Minions have \d+% increased maximum Life',
            '\d+% reduced Mana Reserved',
            '\d+% chance to Avoid being (Stunned|Shocked|Frozen|Ignited)',
            '\+\d to Level of Socketed Aura Gems',
            'Socketed Gems deal \d+% more Elemental Damage',
            '\d+% of Physical Damage taken as (Fire|Cold|Lightning) Damage',
            # Deprecated
            '\d+% increased Quantity of Items found'
        }
    )
    return stats

def parse_gloves(item):
    stats = Counter()
    parse_sockets(item, stats)
    parse_corrupted(item, stats)
    parse_defenses(item, stats)
    parse_requirements(item, stats)
    parse_implicit_mods(
        item, 'Gloves', stats,
        parsers=[
            ('MeleeDamage', Affix.int('(\d+)% increased Melee Damage')),
            ('ProjectileAttackDamage', Affix.int('(\d+)% increased Projectile Attack Damage')),
            ('SpellDamage', Affix.int('(\d+)% increased Spell Damage')),
            # Corrupted
            ('ChaosResist', Affix.int('\+(\d+)% to Chaos Resistance')),
            ('EleWeaknessOnHit', Affix.int('Curse Enemies with level (\d+) Elemental Weakness on Hit')),
            ('TempChainsOnHit', Affix.int('Curse Enemies with level (\d+) Temporal Chains on Hit')),
            ('VulnerabilityOnHit', Affix.int('Curse Enemies with level (\d+) Vulnerability on Hit')),
            ('GrantedSkillId', Affix.granted_skill_id()),
            ('GrantedSkillLevel', Affix.granted_skill_level()),
            ('SocketedGemLevel', Affix.int('\+(\d+) to Level of Socketed Gems')),
            ('SocketedVaalGemLevel', Affix.int('\+(\d+) to Level of Socketed Vaal Gems')),
            ('CastSpeed', Affix.int('(\d+)% increased Cast Speed')),
            ('SupportedByCastOnCrit', Affix.int('Socketed Gems are supported by level (\d+) Cast On Crit')),
            ('SupportedByCastOnStun', Affix.int('Socketed Gems are supported by level (\d+) Cast when Stunned'))
        ],
        aggregators={
            'GrantedSkillId': AffixCombine.restrict_to_one('GrantedSkill'),
            'GrantedSkillLevel': AffixCombine.restrict_to_one('GrantedSkill'),
        }
    )
    parse_explicit_mods(
        item, 'Gloves', stats,
        parsers=[
            # Prefix
            ('AddedColdAttackDamage', Affix.range('Adds (\d+) to (\d+) Cold Damage to Attacks')),
            ('StunRecovery', Affix.int('(\d+)% increased Stun and Block Recovery')),
            ('AddedFireAttackDamage', Affix.range('Adds (\d+) to (\d+) Fire Damage to Attacks')),
            ('Life', Affix.int('\+(\d+) to maximum Life')),
            ('Mana', Affix.int('\+(\d+) to maximum Mana')),
            ('ItemRarity', Affix.int('(\d+)% increased Rarity of Items found')),
            ('LifeLeech', Affix.float('(\d+(\.\d+)?)% of Physical Attack Damage Leeched as Life')),
            ('AddedLightningAttackDamage', Affix.range('Adds (\d+) to (\d+) Lightning Damage to Attacks')),
            ('ManaLeech', Affix.float('(\d+(\.\d+)?)% of Physical Attack Damage Leeched as Mana')),
            ('AddedPhysAttackDamage', Affix.range('Adds (\d+) to (\d+) Physical Damage to Attacks')),
            # Suffix
            ('ChaosResist', Affix.int('\+(\d+)% to Chaos Resistance')),
            ('ColdResist', Affix.int('\+(\d+)% to Cold Resistance')),
            ('Dexterity', Affix.int('\+(\d+) to Dexterity')),
            ('FireResist', Affix.int('\+(\d+)% to Fire Resistance')),
            ('Accuracy', Affix.int('\+(\d+) to Accuracy Rating')),
            ('AttackSpeed', Affix.int('(\d+)% increased Attack Speed')),
            ('Intelligence', Affix.int('\+(\d+) to Intelligence')),
            ('LifeGainOnHit', Affix.int('\+(\d+) Life gained for each Enemy hit by your Attacks')),
            ('LifeGainOnKill', Affix.int('\+(\d+) Life gained on Kill')),
            ('LifeRegen', Affix.float('(\d+(\.\d)?) Life Regenerated per second')),
            ('LightningResist', Affix.int('\+(\d+)% to Lightning Resistance')),
            ('ManaGainOnKill', Affix.int('\+(\d+) Mana gained on Kill')),
            ('Strength', Affix.int('\+(\d+) to Strength')),
        ],
        aggregators={
            'LifeLeech': AffixCombine.scale(100),
            'ManaLeech': AffixCombine.scale(100),
            'LifeRegen': AffixCombine.scale(10),
        },
        ignored={
            '\d+% increased Armour',
            '\d+% increased Evasion Rating',
            '\d+% increased Energy Shield',
            '\d+% increased Armour and Evasion',
            '\d+% increased Armour and Energy Shield',
            '\d+% increased Evasion and Energy Shield',
            '\d+% increased Armour, Evasion and Energy Shield',
            '\+\d+ to Armour',
            '\+\d+ to Evasion',
            '\+\d+ to maximum Energy Shield',
            '\d+% reduced Attribute Requirements',
        },
        banned={
            # Essence
            'Socketed Gems have \d+% more Attack and Cast Speed',
            'Socketed Gems have \+\d+(\.\d)?% Critical Strike Chance',
            'Socketed Gems deal 175 to 225 additional Fire Damage',
            'Minions have \d+% increased maximum Life',
            '\d+% increased Global Critical Strike Chance',
            '\d+% increased Life Leeched per second',
            'Your Flasks grant \d+% increased Rarity of Items found while using a Flask',
            # Deprecated
            '\d+% increased Quantity of Items found'
        }
    )
    return stats

def parse_boots(item):
    return dict()

def parse_belt(item):
    return dict()

def parse_shield(item):
    return dict()

def parse_wand(item):
    return dict()

def parse_staff(item):
    return dict()

def parse_dagger(item):
    return dict()

def parse_one_hand_sword(item):
    return dict()

def parse_two_hand_sword(item):
    return dict()

def parse_one_hand_axe(item):
    return dict()

def parse_two_hand_axe(item):
    return dict()

def parse_one_hand_mace(item):
    return dict()

def parse_two_hand_mace(item):
    return dict()

def parse_bow(item):
    return dict()

def parse_quiver(item):
    return dict()

def parse_claw(item):
    return dict()

def parse_sceptre(item):
    return dict()


def is_enchanted(item):
    return 'enchantMods' in item and len(item['enchantMods']) > 0


def parse_sockets(item, stats):
    """
    Converts socket JSON into string, e.g. "SDD D I" for a 5-socket 3-link
    """
    groups = defaultdict(lambda: [])
    for socket_info in item['sockets']:
        groups[socket_info['group']].append(socket_info['attr'])
    stats['Sockets'] = ' '.join([''.join(x) for x in groups.values()])


def parse_corrupted(item, stats):
    stats['Corrupted'] = item['corrupted']


def parse_defenses(item, stats):
    quality = read_quality_multiplier(item)
    armour = read_int_property('Armour', item)
    evasion = read_int_property('Evasion Rating', item)
    energy_shield = read_int_property('Energy Shield', item)
    stats['Armour'] = int(armour / quality * 1.20)
    stats['Evasion'] = int(evasion / quality * 1.20)
    stats['EnergyShield'] = int(energy_shield / quality * 1.20)


def parse_requirements(item, stats):
    stats['ReqLevel'] = 0
    stats['ReqStr'] = 0
    stats['ReqDex'] = 0
    stats['ReqInt'] = 0

    if 'requirements' not in item:
        return

    for requirement in item['requirements']:
        if requirement['name'][:3] not in {'Lev', 'Str', 'Dex', 'Int'}:
            print("WARNING: Unknown requirement: ", requirement['name'])
            continue
        # Yes this really happens, sometimes they write the full name...
        if requirement['name'] != 'Level':
            requirement['name'] = requirement['name'][:3]
        stats['Req' + requirement['name']] = int(requirement['values'][0][0])


def read_property(property_name, item, default_value=None):
    for property in item['properties']:
        if property['name'] == property_name:
            return property['values']
    return default_value


def read_int_property(property_name, item, default_value=0):
    values = read_property(property_name, item)
    if values is None or len(values) == 0:
        return default_value
    return int(values[0][0])


def read_quality_multiplier(item):
    """
    Returns quality multiplier of an item, or 1.0 if item has no quality.
    """
    for property in item['properties']:
        if property['name'] == 'Quality':
            return 1.0 + float(property['values'][0][0][1:-1])
    return 1.0


PARSERS = {
    itemtype.RING: parse_ring,
    itemtype.AMULET: parse_amulet,
    itemtype.BODY: parse_body,
    itemtype.HELMET: parse_helmet,
    itemtype.GLOVES: parse_gloves,
    itemtype.BOOTS: parse_boots,
    itemtype.BELT: parse_belt,
    itemtype.SHIELD: parse_shield,
    itemtype.WAND: parse_wand,
    itemtype.STAFF: parse_staff,
    itemtype.DAGGER: parse_dagger,
    itemtype.ONE_HAND_SWORD: parse_one_hand_sword,
    itemtype.TWO_HAND_SWORD: parse_two_hand_sword,
    itemtype.ONE_HAND_AXE: parse_one_hand_axe,
    itemtype.TWO_HAND_AXE: parse_two_hand_axe,
    itemtype.ONE_HAND_MACE: parse_one_hand_mace,
    itemtype.TWO_HAND_MACE: parse_two_hand_mace,
    itemtype.BOW: parse_bow,
    itemtype.QUIVER: parse_quiver,
    itemtype.CLAW: parse_claw,
    itemtype.SCEPTRE: parse_sceptre,
}


def parse_stats(item, item_type):
    return PARSERS[item_type](item)


SKILLS = {
    'None': 0,
    'Purity of Fire': 1,
    'Purity of Ice': 2,
    'Purity of Lightning': 3,
    'Conductivity': 4,
    'Flammability': 5,
    'Frostbite': 6,
    'Purity of Elements': 7,
    'Clarity': 8,
    'Wrath': 9,
    'Assassin\'s Mark': 10
}


def get_skill_id(name):
    return SKILLS[name]


class ItemParserException(Exception):
    def __init__(self, msg):
        self.msg = msg
        Exception.__init__(self, msg)


class ItemBannedException(ItemParserException):
    def __init__(self, item_type, mod_text):
        self.item_type = item_type
        self.mod_text = mod_text
        ItemParserException.__init__(self, mod_text)
