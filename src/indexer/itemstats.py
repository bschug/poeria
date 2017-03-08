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
        match = re.match(expr, mod_text)
        return default_value if match is None else match.group(1)

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
        match = re.match('Grants level (\d+) ([a-zA-Z]+) Skill', mod_text)
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
    try:
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
                ('ChaosAttackDamage', Affix.range('Adds (\d+) to (\d+) Chaos Damage to Attacks')),
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
                'GrantedSkill': AffixCombine.restrict_to_one('GrantedSkill')
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
                ('LifeLeech', Affix.float('(\d+[\.\d+]*)% of Physical Attack Damage Leeched as Life')),
                ('ManaLeech', Affix.float('(\d+[\.\d+]*)% of Physical Attack Damage Leeched as Mana')),
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
                ('LifeRegen', Affix.float('(\d+[\.\d]*) Life Regenerated per second')),
                ('LightRadius', Affix.int('(\d+)% increased Light Radius')),
                ('IncreasedAccuracy', Affix.int('(\d+)% increased Accuracy Rating')),
                ('ManaGainOnKill', Affix.int('\+(\d+) Mana gained on Kill')),
                ('ManaRegen', Affix.int('(\d+)% increased Mana Regeneration Rate')),
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
                'Minions have (\d+)% increased Movement Speed'
            ],
            aggregators={
                'LifeLeech': AffixCombine.scale(100),
                'ManaLeech': AffixCombine.scale(100),
                'LifeRegen': AffixCombine.scale(10),
            }
        )
        return stats

    # Don't catch exceptions that we raised on purpose
    except ItemParserException:
        raise

    # If anything unintended goes wrong, log the item json for debugging
    except:
        print("Exception while parsing ring item ", json.dumps(item))
        raise

def parse_amulet(item):
    return dict()

def parse_body(item):
    try:
        stats = dict()
        parse_sockets(item, stats)
        parse_corrupted(item, stats)
        parse_defenses(item, stats)
        parse_requirements(item, stats)
        parse_life(item, stats)
        parse_mana(item, stats)
        parse_attribute_bonus(item, stats)
        parse_resists(item, stats)
        parse_life_regen(item, stats)
        parse_stun_and_block_recovery(item, stats)
        parse_phys_reflect(item, stats)
        # Corrupted:
        parse_avoid_elemental_status_effect(item, stats)
        parse_granted_skill(item, stats)
        parse_cannot_be_knocked_back(item, stats)
        parse_socketed_gem_level(item, stats)
        parse_socketed_vaal_gem_level(item, stats)
        parse_max_resists(item, stats)
        parse_mana_multiplier(item, stats)
        return stats
    except Exception as ex:
        print("Exception while parsing body item ", json.dumps(item))
        raise ex

def parse_helmet(item):
    return dict()

def parse_gloves(item):
    return dict()

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


def parse_life(item, stats):
    life = read_mod('\+(\d+) to maximum Life', item)
    strength = read_mod('\+(\d+) to Strength', item)
    stats['Life'] = life + strength / 2


def parse_energy_shield(item, stats):
    stats['EnergyShield'] = read_mod('\+(\d+) to maximum Energy Shield', item)


def parse_mana(item, stats):
    mana = read_mod('\+(\d+) to maximum Mana', item)
    intelligence = read_mod('\+(\d+) to Intelligence', item)
    stats['Mana'] = mana + intelligence / 2


def parse_attribute_bonus(item, stats):
    stats['Strength'] = read_mod('\+(\d+) to Strength', item)
    stats['Dexterity'] = read_mod('\+(\d+) to Dexterity', item)
    stats['Intelligence'] = read_mod('\+(\d+) to Intelligence', item)


def parse_resists(item, stats):
    all_resists = read_mod('\+(\d+)% to all Elemental Resistances', item)
    stats['FireResist'] = read_mod('\+(\d+)% to Fire Resistance', item) + all_resists
    stats['ColdResist'] = read_mod('\+(\d+)% to Cold Resistance', item) + all_resists
    stats['LightningResist'] = read_mod('\+(\d+)% to Lightning Resistance', item) + all_resists
    stats['ChaosResist'] = read_mod('\+(\d+)% to Chaos Resistance', item)


def parse_life_regen(item, stats):
    stats['LifeRegen'] = int(read_float_mod('(\d+[\.\d]*) Life Regenerated per second', item) * 10)


def parse_mana_regen(item, stats):
    stats['ManaRegen'] = read_mod('(\d+)% increased Mana Regeneration Rate', item)


def parse_stun_and_block_recovery(item, stats):
    stats['StunRecovery'] = read_mod('(\d+)% increased Stun and Block Recovery', item)


def parse_phys_reflect(item, stats):
    stats['PhysReflect'] = read_mod('Reflects (\d+) Physical Damage to Melee Attackers', item)


def parse_avoid_elemental_status_effect(item, stats):
    stats['AvoidIgnite'] = read_mod('(\d+)% chance to Avoid being Ignited', item)
    stats['AvoidChill'] = read_mod('(\d+)% chance to Avoid being Chilled', item)
    stats['AvoidFreeze'] = read_mod('(\d+)% chance to Avoid being Frozen', item)
    stats['AvoidShock'] = read_mod('(\d+)% chance to Avoid being Shocked', item)


def parse_granted_skill(item, stats):
    skills = read_mod2('Grants level (\d+) ([a-zA-Z]+) Skill', item)
    skills = [(level, get_skill_id(name)) for level, name in skills]
    if len(skills) == 0:
        stats['GrantedSkillLevel'] = 0
        stats['GrantedSkillId'] = 0
        return
    stats['GrantedSkillLevel'] = int(skills[0][0])
    stats['GrantedSkillId'] = int(skills[0][1])


def parse_cannot_be_knocked_back(item, stats):
    stats['CannotBeKnockedBack'] = has_mod('Cannot be Knocked Back', item)


def parse_socketed_gem_level(item, stats):
    stats['SocketedGemLevel'] = read_mod('\+(\d+) to Level of Socketed Gems', item)


def parse_socketed_vaal_gem_level(item, stats):
    stats['SocketedVaalGemLevel'] = read_mod('\+(\d+) to Level of Socketed Vaal Gems', item)


def parse_max_resists(item, stats):
    all_resists = read_mod('\+(\d+)% to all maximum Resistances', item)
    stats['MaxFireResist'] = read_mod('\+(\d+)% to maximum Fire Resistance', item) + all_resists
    stats['MaxColdResist'] = read_mod('\+(\d+)% to maximum Cold Resistance', item) + all_resists
    stats['MaxLightningResist'] = read_mod('\+(\d+)% to maximum Lightning Resistance', item) + all_resists
    stats['MaxChaosResist'] = read_mod('\+(\d+)% to maximum Chaos Resistance', item) + all_resists


def parse_mana_multiplier(item, stats):
    stats['ManaMultiplier'] = read_mod('Socketed Skill Gems get a (\d+)% Mana Multiplier', item)


def parse_doubled_in_breach(item, stats):
    stats['DoubledInBreach'] = has_mod('Properties are doubled while in a Breach', item)


def parse_flat_defense_bonus(item, stats):
    stats['Armour'] = read_mod('\+(\d+) to Armour', item)
    stats['Evasion'] = read_mod('\+(\d+) to Evasion Rating', item)
    stats['EnergyShield'] = read_mod('\+(\d+) to Energy Shield', item)


def parse_accuracy(item, stats):
    stats['Accuracy'] = read_mod('\+(\d+) to Accuracy Rating', item)


def parse_added_attack_damage(item, stats):
    stats['AddedPhysAttackDamage'] = read_range_mod('Adds (\d+) to (\d+) Physical Damage to Attacks', item)
    stats['AddedFireAttackDamage'] = read_range_mod('Adds (\d+) to (\d+) Fire Damage to Attacks', item)
    stats['AddedColdAttackDamage'] = read_range_mod('Adds (\d+) to (\d+) Cold Damage to Attacks', item)
    stats['AddedLightningAttackDamage'] = read_range_mod('Adds (\d+) to (\d+) Lightning Damage to Attacks', item)
    stats['AddedChaosAttackDamage'] = read_range_mod('Adds (\d+) to (\d+) Chaos Damage to Attacks', item)


def parse_increased_ele_damage(item, stats):
    stats['IncreasedEleDamage'] = read_mod('(\d+)% increased Elemental Damage', item)
    stats['IncreasedFireDamage'] = read_mod('(\d+)% increased Fire Damage', item)
    stats['IncreasedColdDamage'] = read_mod('(\d+)% increased Cold Damage', item)
    stats['IncreasedLightningDamage'] = read_mod('(\d+)% increased Lightning Damage', item)


def parse_increased_weapon_ele_damage(item, stats):
    stats['IncreasedWeaponEleDamage'] = read_mod('(\d+)% increased Elemental Damage with Weapons', item)


def parse_increased_global_crit_chance(item, stats):
    stats['CritChance'] = read_mod('(\d+)% increased Global Critical Strike Chance', item)


def parse_item_rarity(item, stats):
    stats['ItemRarity'] = read_mod('(\d+)% increased Rarity of Items found', item)


def parse_leech(item, stats):
    stats['LifeLeech'] = int(read_float_mod('(\d+[\.\d]*)% of Physical Attack Damage Leeched as Life', item) * 100)
    stats['ManaLeech'] = int(read_float_mod('(\d+[\.\d]*)% of Physical Attack Damage Leeched as Mana', item) * 100)


def parse_attack_speed(item, stats):
    stats['AttackSpeed'] = read_mod('(\d+)% increased Attack Speed', item)


def parse_cast_speed(item, stats):
    stats['CastSpeed'] = read_mod('(\d+)% increased Cast Speed', item)


def parse_gain_on_hit_kill(item, stats):
    stats['LifeGainOnHit'] = read_mod('\+(\d+) Life gained for each Enemy hit by your Attacks', item)
    stats['LifeGainOnKill'] = read_mod('\+(\d+) Life gained on Kill', item)
    stats['ManaGainOnHit'] = read_mod('\+(\d+) Mana gained for each Enemy hit by your Attacks', item)
    stats['ManaGainOnKill'] = read_mod('\+(\d+) Mana gained on Kill', item)


def parse_light_radius(item, stats):
    stats['LightRadius'] = read_mod('(\d+)% increased Light Radius', item)


def parse_damage_to_mana(item, stats):
    stats['DamageToMana'] = read_mod('(\d+)% of Damage taken gained as Mana when Hit', item)


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


def has_mod(regex, item):
    """
    Checks if the item has an implicit or explicit mod that matches the pattern.
    """
    for mod in item.get('implicitMods', []) + item.get('explicitMods', []):
        match = re.match(regex, mod)
        if match is not None:
            return True
    return False


def read_mod(regex, item):
    """
    Reads a numeric mod from an item.
    Implicit and explicit mods will be added.
    :param regex: Regular expression with one matching group for the resulting number
    :param item:
    """
    mods = item.get('implicitMods', []) + item.get('explicitMods', [])
    return sum([read_mod_from_text(regex, x) for x in mods])


def read_mod_from_text(regex, text):
    match = re.match(regex, text)
    return 0 if match is None else int(match.group(1))


def read_float_mod(regex, item):
    mods = item.get('implicitMods', []) + item.get('explicitMods', [])
    return sum([read_float_mod_from_text(regex, x) for x in mods])


def read_float_mod_from_text(regex, text):
    match = re.match(regex, text)
    return 0 if match is None else float(match.group(1))


def read_mod2(regex, item):
    """
    Reads a two-value mod from an item.
    Returns a list of tuples.
    :param regex: Regular expression with two matching groups.
    :param item:
    """
    mods = item.get('implicitMods', []) + item.get('explicitMods', [])
    skills = [read_mod_from_text2(regex, x) for x in mods]
    return [x for x in skills if x is not None]


def read_mod_from_text2(regex, text):
    match = re.match(regex, text)
    return None if match is None else (match.group(1), match.group(2))


def read_range_mod(regex, item):
    """
    Reads a mod with two values (from - to) and returns their sum.
    (we don't return the average because everything is integer here and we can't have halves)
    """
    return sum([int(x) + int(y) for x, y in read_mod2(regex, item)])



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
