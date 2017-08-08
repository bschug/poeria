import json
import re
from collections import defaultdict

from constants import itemtype
from util.collections import CaseInsensitiveCounter


class AffixParse(object):
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
        try:
            regex = re.compile(expr)
            return lambda x: int(AffixParse._regex(regex, x, '0'))
        except:
            print("BAD REGEX:", expr)
            raise

    @staticmethod
    def float(scale, expr):
        """
        Returns the value of the first match group of the regex, or 0.
        """
        try:
            regex = re.compile(expr)
            return lambda x: int(scale * float(AffixParse._regex(regex, x, '0')))
        except:
            print("BAD REGEX:", expr)
            raise

    @staticmethod
    def _regex(regex, mod_text, default_value):
        """
        :param regex:           Compiled regular expression
        :param mod_text:        Text to match
        :param default_value:   Value to return if it doesn't match
        """
        match = regex.fullmatch(mod_text)
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
        try:
            regex = re.compile(expr)
            return lambda x: AffixParse._range(regex, x)
        except:
            print("BAD REGEX:", expr)
            raise

    @staticmethod
    def _range(regex, mod_text):
        match = regex.fullmatch(mod_text)
        return 0 if match is None else int(match.group(1)) + int(match.group(2))

    @staticmethod
    def granted_skill_id():
        """Returns skill id (see SKILLS) of granted skill, or 0."""
        return lambda x: AffixParse._granted_skill(x)[0]

    @staticmethod
    def granted_skill_level():
        """Returns level of granted skill, or 0."""
        return lambda x: AffixParse._granted_skill(x)[1]

    @staticmethod
    def _granted_skill(mod_text):
        match = re.fullmatch("Grants level (\d+) ([a-zA-Z \']+) Skill", mod_text)
        if match is None:
            return 0, 0

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
    def boolean_or():
        """
        For boolean fields, the parser returns 0 or 1, but the dictionary must store
        true or false. This interprets 0 and 1 as False and True and aggregates with
        a boolean OR operation.
        """
        return lambda old, new: bool(old) or (new == 1)


class AffixParser(object):
    def __init__(self, stat_ids, parse, aggregate=None):
        """
        Base class for affix parsers. An affix parser consist of a parser function,
        a list of stat ids and an aggregator. The parser function receives a mod
        description as input and returns 0 if it doesn't match, or the value if it does.

        Items can have more than one mod affecting the same stat (e.g. implicit and
        explicit), so multiple sources must be combined. By default, they are simply
        summed up. If that doesn't work, an aggregator can define specific rules.

        :param stat_ids:    Single stat id string or iterable of multiple stat ids
        :param parse:       Parser function: mod text -> value | 0
        :param aggregate:   Aggregator function: old, new -> combined
        """
        # Allow single stat id passed directly, convert to tuple internally
        self.stat_ids = (stat_ids,) if isinstance(stat_ids, str) else stat_ids
        self.parse = parse
        self.aggregator = aggregate

    def aggregate(self, old_value, new_value):
        if self.aggregator is None:
            return old_value + new_value
        else:
            return self.aggregator(old_value, new_value)



class IntAffix(AffixParser):
    def __init__(self, stat_ids, regex):
        super().__init__(stat_ids, AffixParse.int(regex), None)


class FloatAffix(AffixParser):
    def __init__(self, stat_ids, regex, scale):
        super().__init__(stat_ids, AffixParse.float(scale, regex), None)


class BoolAffix(AffixParser):
    def __init__(self, stat_ids, regex):
        super().__init__(stat_ids, AffixParse.text(regex), AffixCombine.boolean_or())


class RangeAffix(AffixParser):
    def __init__(self, stat_ids, regex):
        super().__init__(stat_ids, AffixParse.range(regex), None)


class Affix(object):
    Accuracy = IntAffix('Accuracy', '\+(\d+) to Accuracy Rating')
    AddedArmour = IntAffix('AddedArmour', '\+(\d+) to Armour')
    AddedArmourAndEvasion = IntAffix(('AddedArmour','AddedEvasion'), '\+(\d+) to Armour and Evasion Rating')
    AddedArrow = BoolAffix('AddedArrow', 'Adds an additional Arrow')
    AddedChaosAttackDamage = RangeAffix('AddedChaosAttackDamage', 'Adds (\d+) to (\d+) Chaos Damage to Attacks')
    AddedColdAttackDamage = RangeAffix('AddedColdAttackDamage', 'Adds (\d+) to (\d+) Cold Damage to Attacks')
    AddedEnergyShield = IntAffix('AddedEnergyShield', '\+(\d+) to maximum Energy Shield')
    AddedEvasion = IntAffix('AddedEvasion', '\+(\d+) to Evasion Rating')
    AddedFireAttackDamage = RangeAffix('AddedFireAttackDamage', 'Adds (\d+) to (\d+) Fire Damage to Attacks')
    AddedFireBowDamage = RangeAffix('AddedFireBowDamage', 'Adds (\d+) to (\d+) Fire Damage to Attacks with Bows')
    AddedLightningAttackDamage = RangeAffix('AddedLightningAttackDamage', 'Adds (\d+) to (\d+) Lightning Damage to Attacks')
    AddedPhysAttackDamage = RangeAffix('AddedPhysAttackDamage', 'Adds (\d+) to (\d+) Physical Damage to Attacks')
    AddedPhysBowDamage = RangeAffix('AddedPhysBowDamage', 'Adds (\d+) to (\d+) Physical Damage to Attacks with Bows')
    AddedPhysDamageLocal = RangeAffix('AddedPhysDamageLocal', 'Adds (\d+) to (\d+) Physical Damage$')
    AddedSpellColdDamage = RangeAffix('AddedSpellColdDamage', 'Adds (\d+) to (\d+) Cold Damage to Spells')
    AddedSpellFireDamage = RangeAffix('AddedSpellFireDamage', 'Adds (\d+) to (\d+) Fire Damage to Spells')
    AddedSpellLightningDamage = RangeAffix('AddedSpellLightningDamage', 'Adds (\d+) to (\d+) Lightning Damage to Spells')
    AdditionalCurses = IntAffix('AdditionalCurses', 'Enemies can have (\d) additional Curse[s]?')
    AdditionalTraps = IntAffix('AdditionalTraps', 'Can have up to (\d+) additional Trap(s)? placed at a time')
    AllAttributes = IntAffix(('Strength','Dexterity','Intelligence'), '\+(\d+) to all Attributes')
    AllElementalResists = IntAffix(('FireResist', 'ColdResist', 'LightningResist'), '\+(\d+)% to all Elemental Resistances')
    AttackSpeed = IntAffix('AttackSpeed', '(\d+)% increased Attack Speed')
    AvoidIgnite = IntAffix('AvoidIgnite', '(\d+)% chance to Avoid being Ignited')
    AvoidFreeze = IntAffix('AvoidFreeze', '(\d+)% chance to Avoid being Frozen')
    AvoidShock = IntAffix('AvoidShock', '(\d+)% chance to Avoid being Shocked')
    Bleed = IntAffix('Bleed', '(\d+)% chance to cause Bleeding on Hit')
    BlockChance = IntAffix('BlockChance', '(\d+)% Chance to Block')
    BlockChanceWhileDualWielding = IntAffix('BlockChanceWhileDualWielding', '(\d+)% additional Block Chance while Dual Wielding')
    BlockRecovery = IntAffix('BlockRecovery', '(\d+)% increased Block Recovery')
    CannotBeKnockedBack = BoolAffix('CannotBeKnockedBack', 'Cannot be Knocked Back')
    ChanceToFlee = IntAffix('ChanceToFlee', '(\d+)% chance to Cause Monsters to Flee')
    ChaosResist = IntAffix('ChaosResist', '\+(\d+)% to Chaos Resistance')
    CastSpeed = IntAffix('CastSpeed', '(\d+)% increased Cast Speed')
    ColdAndLightningResist = IntAffix(('ColdResist','LightningResist'), '\+(\d+)% to Cold and Lightning Resistances')
    ColdResist = IntAffix('ColdResist', '\+(\d+)% to Cold Resistance')
    CullingStrike = BoolAffix('CullingStrike', 'Culling Strike')
    DamageToMana = IntAffix('DamageToMana', '(\d+)% of Damage taken gained as Mana when Hit')
    Dexterity = IntAffix('Dexterity', '\+(\d+) to Dexterity')
    DexterityAndIntelligence = IntAffix(('Dexterity','Intelligence'), '\+(\d+) to Dexterity and Intelligence')
    DodgeAttacks = IntAffix('DodgeAttacks', '(\d+)% chance to Dodge Attacks')
    DoubledInBreach = BoolAffix('DoubledInBreach', 'Properties are doubled while in a Breach')
    EleWeaknessOnHit = IntAffix('EleWeaknessOnHit', 'Curse Enemies with level (\d+) Elemental Weakness on Hit')
    EnemiesCannotLeech = BoolAffix('EnemiesCannotLeech', 'Enemies Cannot Leech Life From You')
    FireAndColdResist = IntAffix(('FireResist', 'ColdResist'), '\+(\d+)% to Fire and Cold Resistances')
    FireAndLightningResist = IntAffix(('FireResist', 'LightningResist'), '\+(\d+)% to Fire and Lightning Resistances')
    FireResist = IntAffix('FireResist', '\+(\d+)% to Fire Resistance')
    FlaskChargeGain = IntAffix('FlaskChargeGain', '(\d+)% increased Flask Charges gained')
    FlaskChargeUse = IntAffix('FlaskChargeUse', '(\d+)% reduced Flask Charges used')
    FlaskDuration = IntAffix('FlaskDuration', '(\d+)% increased Flask effect duration')
    FlaskLife = IntAffix('FlaskLife', '(\d+)% increased Flask Life Recovery rate')
    FlaskMana = IntAffix('FlaskMana', '(\d+)% increased Flask Mana Recovery rate')
    GlobalCritChance = IntAffix('GlobalCritChance', '(\d+)% increased Global Critical Strike Chance')
    GlobalCritMulti = IntAffix('GlobalCritMulti', '\+(\d+)% to Global Critical Strike Multiplier')
    GrantedSkillId = AffixParser(('GrantedSkillId',), AffixParse.granted_skill_id(), AffixCombine.restrict_to_one('GrantedSkill'))
    GrantedSkillLevel = AffixParser(('GrantedSkillLevel',), AffixParse.granted_skill_level(), AffixCombine.restrict_to_one('GrantedSkill'))
    IncreasedAccuracy = IntAffix('IncreasedAccuracy', '(\d+)% increased Accuracy Rating')
    IncreasedAoE = IntAffix('IncreasedAoE', '(\d+)% increased Area of Effect of Area Skills')
    IncreasedArmour = IntAffix('IncreasedArmour', '(\d+)% increased Armour')
    IncreasedArmourAndEnergyShield = IntAffix(('IncreasedArmour','IncreasedEnergyShield'), '(\d+)% increased Armour and Energy Shield')
    IncreasedArmourAndEvasion = IntAffix(('IncreasedArmour', 'IncreasedEvasion'), '(\d+)% increased Armour and Evasion')
    IncreasedArmourEvasionAndEnergyShield = IntAffix(('IncreasedArmour', 'IncreasedEvasion', 'IncreasedEnergyShield'), '(\d+)% increased Armour, Evasion and Energy Shield')
    IncreasedEleDamage = IntAffix('IncreasedEleDamage', '(\d+)% increased Elemental Damage')
    IncreasedEnergyShield = IntAffix('IncreasedEnergyShield', '(\d+)% increased( maximum)? Energy Shield')
    IncreasedEvasion = IntAffix('IncreasedEvasion', '(\d+)% increased Evasion Rating')
    IncreasedEvasionAndEnergyShield = IntAffix(('IncreasedEvasion','IncreasedEnergyShield'), '(\d+)% increased Evasion and Energy Shield')
    IncreasedFireDamage = IntAffix('IncreasedFireDamage', '(\d+)% increased Fire Damage')
    IncreasedColdDamage = IntAffix('IncreasedColdDamage', '(\d+)% increased Cold Damage')
    IncreasedLifeRegen = FloatAffix('IncreasedLifeRegen', '(\d+(\.\d+)?)% of Life Regenerated per second', 10)
    IncreasedLightningDamage = IntAffix('IncreasedLightningDamage', '(\d+)% increased Lightning Damage')
    IncreasedPhysDamage = IntAffix('IncreasedPhysDamage', '(\d+)% increased Physical Damage')
    IncreasedWeaponEleDamage = IntAffix('IncreasedWeaponEleDamage', '(\d+)% increased Elemental Damage with Attack Skills')
    Intelligence = IntAffix('Intelligence', '\+(\d+) to Intelligence')
    ItemRarity = IntAffix('ItemRarity', '(\d+)% increased Rarity of Items found')
    Life = IntAffix('Life', '\+(\d+) to maximum Life')
    LifeAndManaGainOnHit = IntAffix(('LifeGainOnHit', 'ManaGainOnHit'), '\+(\d+) Life and Mana gained for each Enemy hit')
    LifeLeech = FloatAffix('LifeLeech', '(\d+(\.\d+)?)% of Physical Attack Damage Leeched as Life', 100)
    LifeLeechCold = FloatAffix('LifeLeechCold', '(\d(\.\d+)?)% of Cold Damage Leeched as Life', 100)
    LifeLeechLightning = FloatAffix('LifeLeechLightning', '(\d(\.\d+)?)% of Lightning Damage Leeched as Life', 100)
    LifeLeechFire = FloatAffix('LifeLeechFire', '(\d(\.\d+)?)% of Fire Damage Leeched as Life', 100)
    LifeGainOnHit = IntAffix('LifeGainOnHit', '\+(\d+) Life gained for each Enemy hit by( your)? Attacks')
    LifeGainOnKill = IntAffix('LifeGainOnKill', '\+(\d+) Life gained on Kill')
    LifeRegen = FloatAffix('LifeRegen', '(\d+(\.\d)?) Life Regenerated per second', 10)
    LightningResist = IntAffix('LightningResist', '\+(\d+)% to Lightning Resistance')
    LightRadius = IntAffix('LightRadius', '(\d+)% increased Light Radius')
    Mana = IntAffix('Mana', '\+(\d+) to maximum Mana')
    ManaGainOnHit = IntAffix('ManaGainOnHit', '\+(\d+) Mana gained for each Enemy hit by (your )?Attacks')
    ManaGainOnKill = IntAffix('ManaGainOnKill', '\+(\d+) Mana gained on Kill')
    ManaLeech = FloatAffix('ManaLeech', '(\d+(\.\d+)?)% of Physical Attack Damage Leeched as Mana', 100)
    ManaMultiplier = IntAffix('ManaMultiplier', 'Socketed Skill Gems get a (\d+)% Mana Multiplier')
    ManaRegen = IntAffix('ManaRegen', '(\d+)% increased Mana Regeneration Rate')
    ManaShield = IntAffix('ManaShield', 'When Hit, (\d+)% of Damage is taken from Mana before Life')
    MaxEnduranceCharges = IntAffix('MaxEnduranceCharges', '\+(\d+) to Maximum Endurance Charges')
    MaxFrenzyCharges = IntAffix('MaxFrenzyCharges', '\+(\d+) to Maximum Frenzy Charges')
    MaxPowerCharges = IntAffix('MaxPowerCharges', '\+(\d+) to Maximum Power Charges')
    MaxResists = IntAffix('MaxResists', '\+(\d+)% to all maximum Resistances')
    MeleeDamage = IntAffix('MeleeDamage', '(\d+)% increased Melee Damage')
    MinionDamage = IntAffix('MinionDamage', 'Minions deal (\d+)% increased Damage')
    MoveSpeed = IntAffix('MoveSpeed', '(\d+)% increased Movement Speed')
    PenetrateEleResist = IntAffix('PenetrateEleResist', 'Damage Penetrates (\d+)% Elemental Resistances')
    PhysDamageReduction = IntAffix('PhysDamageReduction', '\-(\d+) Physical Damage taken from Attacks')
    PhysReflect = IntAffix('PhysReflect', 'Reflects (\d+) Physical Damage to Melee Attackers')
    PhysToCold = IntAffix('PhysToCold', '(\d+)% of Physical Damage Converted to Cold Damage')
    PhysToFire = IntAffix('PhysToFire', '(\d+)% of Physical Damage Converted to Fire Damage')
    PhysToLightning = IntAffix('PhysToFire', '(\d+)% of Physical Damage Converted to Lightning Damage')
    Pierce = IntAffix('Pierce', '(\d+)% chance of (Projectiles|Arrows) Piercing')
    ProjectileAttackDamage = IntAffix('ProjectileAttackDamage', '(\d+)% increased Projectile Attack Damage')
    ProjectileSpeed = IntAffix('ProjectileSpeed', '(\d+)% increased Projectile Speed')
    SkillDuration = IntAffix('SkillDuration', '(\d+)% increased Skill Effect Duration')
    SocketedBowGemLevel = IntAffix('SocketedBowGemLevel', '\+(\d+) to Level of Socketed Bow Gems')
    SocketedChaosGemLevel = IntAffix('SocketedChaosGemLevel', '\+(\d+) to Level of Socketed Chaos Gems')
    SocketedColdGemLevel = IntAffix('SocketedColdGemLevel', '\+(\d+) to Level of Socketed Cold Gems')
    SocketedFireGemLevel = IntAffix('SocketedFireGemLevel', '\+(\d+) to Level of Socketed Fire Gems')
    SocketedGemLevel = IntAffix('SocketedGemLevel', '\+(\d+) to Level of Socketed Gems')
    SocketedLightningGemLevel = IntAffix('SocketedLightningGemLevel', '\+(\d+) to Level of Socketed Lightning Gems')
    SocketedMeleeGemLevel = IntAffix('SocketedMeleeGemLevel', '\+(\d+) to Level of Socketed Melee Gems')
    SocketedMinionGemLevel = IntAffix('SocketedMinionGemLevel', '\+(\d+) to Level of Socketed Minion Gems')
    SocketedVaalGemLevel = IntAffix('SocketedVaalGemLevel', '\+(\d+) to Level of Socketed Vaal Gems')
    SpellBlock = IntAffix('SpellBlock', '(\d+)% Chance to Block Spells')
    SpellCrit = IntAffix('SpellCrit', '(\d+)% increased Critical Strike Chance for Spells')
    SpellDamage = IntAffix('SpellDamage', '(\d+)% increased Spell Damage')
    Strength = IntAffix('Strength', '\+(\d+) to Strength')
    StrengthAndDexterity = IntAffix(('Strength','Dexterity'), '\+(\d+) to Strength and Dexterity')
    StrengthAndIntelligence = IntAffix(('Strength','Intelligence'), '\+(\d+) to Strength and Intelligence')
    StunDuration = IntAffix('StunDuration', '(\d+)% increased Stun Duration on Enemies')
    StunRecovery = IntAffix('StunRecovery', '(\d+)% increased Stun and Block Recovery')
    StunThreshold = IntAffix('StunThreshold', '(\d+)% reduced Enemy Stun Threshold')
    SupportedByAddedFireDamage = IntAffix('SupportedByAddedFireDamage', 'Socketed Gems are Supported by level (\d+) Added Fire Damage')
    SupportedByAdditionalAccuracy = IntAffix('SupportedByAdditionalAccuracy', 'Socketed Gems are supported by level (\d+) Additional Accuracy')
    SupportedByCastOnCrit = IntAffix('SupportedByCastOnCrit', 'Socketed Gems are supported by level (\d+) Cast On Crit')
    SupportedByCastOnStun = IntAffix('SupportedByCastOnStun', 'Socketed Gems are supported by level (\d+) Cast when Stunned')
    SupportedByEleProlif = IntAffix('SupportedByEleProlif', 'Socketed Gems are Supported by level (\d+) Elemental Proliferation')
    SupportedByFasterCasting = IntAffix('SupportedByFasterCasting', 'Socketed Gems are Supported by Level (\d+) Faster Casting')
    SupportedByFork = IntAffix('SupportedByFork', 'Socketed Gems are supported by level (\d+) Fork')
    SupportedByIncreasedAoE = IntAffix('SupportedByIncreasedAoE', 'Socketed Gems are Supported by level (\d+) Increased Area of Effect')
    SupportedByIncreasedCritDamage = IntAffix('SupportedByIncreasedCritDamage', 'Socketed Gems are supported by level (\d+) Increased Critical Damage')
    SupportedByLifeLeech = IntAffix('SupportedByLifeLeech', 'Socketed Gems are supported by level (\d+) Life Leech')
    SupportedByMeleeSplash = IntAffix('SupportedByMeleeSplash', 'Socketed Gems are supported by level (\d+) Melee Splash')
    SupportedByMultistrike = IntAffix('SupportedByMultistrike', 'Socketed Gems are supported by level (\d+) Multistrike')
    SupportedByStun = IntAffix('SupportedByStun', 'Socketed Gems are supported by level (\d+) Stun')
    SupportedByWED = IntAffix('SupportedByWED', 'Socketed Gems are supported by level (\d+) Weapon Elemental Damage')
    TempChainsOnHit = IntAffix('TempChainsOnHit', 'Curse Enemies with level (\d+) Temporal Chains on Hit')
    VulnerabilityOnHit = IntAffix('VulnerabilityOnHit', 'Curse Enemies with level (\d+) Vulnerability on Hit')
    WeaponRange = IntAffix('WeaponRange', '\+(\d+) to Weapon range')



def parse_implicit_mods(item, item_type, stats, parsers, ignored=None, banned=None):
    if 'implicitMods' not in item:
        return
    parse_mods(item['implicitMods'], item_type, 'implicit', stats, parsers,
               ignored=ignored, banned=banned)


def parse_explicit_mods(item, item_type, stats, parsers, ignored=None, banned=None):
    if 'explicitMods' not in item:
        return
    parse_mods(item['explicitMods'], item_type, 'explicit', stats, parsers,
               ignored=ignored, banned=banned)


def parse_mods(mods, item_type, mod_type, stats, affix_parsers, ignored=None, banned=None):
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
        for affix in affix_parsers:
            value = affix.parse(mod_text)

            # If parser returned 0, ignore
            if value == 0:
                continue

            # Count number of matching parsers to see if we recognized this mod
            num_matches += 1

            for stat_id in affix.stat_ids:
                old_value = stats.get(stat_id, 0)
                stats[stat_id] = affix.aggregate(old_value, value)

        # Raise an exception if we have no idea what this mod is about
        if num_matches == 0:
            raise ItemParserException("Couldn't parse {} {} mod: {}".format(
                mod_type, item_type, mod_text))


def parse_ring(item):
    stats = CaseInsensitiveCounter()
    stats['DoubledInBreach'] = False
    parse_corrupted(item, stats)
    parse_sockets(item, stats)
    parse_requirements(item, stats, level_only=True, ignore_others=True)
    parse_implicit_mods(
        item, 'Ring', stats,
        parsers=[
            Affix.DoubledInBreach,
            Affix.Life,
            Affix.AddedPhysAttackDamage,
            Affix.Mana,
            Affix.FireResist,
            Affix.ColdResist,
            Affix.LightningResist,
            Affix.FireAndColdResist,
            Affix.FireAndLightningResist,
            Affix.ColdAndLightningResist,
            Affix.AllElementalResists,
            Affix.GlobalCritChance,
            Affix.ItemRarity,
            Affix.AddedEnergyShield,
            Affix.ChaosResist,
            Affix.IncreasedEleDamage,
            # Corrupted Implicits
            Affix.CastSpeed,
            Affix.AddedChaosAttackDamage,
            Affix.IncreasedWeaponEleDamage,
            Affix.DamageToMana,
            Affix.AvoidFreeze,
            Affix.GrantedSkillId,
            Affix.GrantedSkillLevel,
            Affix.ManaGainOnHit
        ],
        ignored=[
            'Has 1 Socket'
        ]
    )
    parse_explicit_mods(
        item, 'Ring', stats,
        parsers=[
            # Prefix
            Affix.AddedColdAttackDamage,
            Affix.AddedFireAttackDamage,
            Affix.AddedLightningAttackDamage,
            Affix.AddedPhysAttackDamage,
            Affix.AddedEnergyShield,
            Affix.AddedEvasion,
            Affix.Life,
            Affix.Mana,
            Affix.IncreasedWeaponEleDamage,
            Affix.ItemRarity,
            Affix.LifeLeech,
            Affix.ManaLeech,
            # Suffix
            Affix.AllAttributes,
            Affix.Strength,
            Affix.Dexterity,
            Affix.Intelligence,
            Affix.FireResist,
            Affix.ColdResist,
            Affix.LightningResist,
            Affix.AllElementalResists,
            Affix.ChaosResist,
            Affix.IncreasedFireDamage,
            Affix.IncreasedColdDamage,
            Affix.IncreasedLightningDamage,
            Affix.Accuracy,
            Affix.AttackSpeed,
            Affix.CastSpeed,
            Affix.LifeGainOnHit,
            Affix.LifeGainOnKill,
            Affix.LifeRegen,
            Affix.LightRadius,
            Affix.IncreasedAccuracy,
            Affix.ManaGainOnKill,
            Affix.ManaRegen,
            Affix.SocketedGemLevel
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
        ]
    )
    return stats


def parse_amulet(item):
    stats = CaseInsensitiveCounter()
    parse_corrupted(item, stats)
    parse_requirements(item, stats, level_only=True)
    parse_implicit_mods(
        item, 'Amulet', stats,
        parsers=[
            Affix.LifeRegen,
            Affix.ManaRegen,
            Affix.Strength,
            Affix.Dexterity,
            Affix.Intelligence,
            Affix.ItemRarity,
            Affix.DexterityAndIntelligence,
            Affix.StrengthAndDexterity,
            Affix.StrengthAndIntelligence,
            Affix.AllAttributes,
            Affix.IncreasedLifeRegen,
            # Corrupted
            Affix.AdditionalCurses,
            Affix.AvoidIgnite,
            Affix.BlockChance,
            Affix.AvoidFreeze,
            Affix.ChaosResist,
            Affix.LifeLeechCold,
            Affix.LifeLeechFire,
            Affix.GrantedSkillId,
            Affix.GrantedSkillLevel,
            Affix.AttackSpeed,
            Affix.IncreasedWeaponEleDamage,
            Affix.LifeLeechLightning,
            Affix.MaxFrenzyCharges,
            Affix.MaxResists,
            Affix.MinionDamage,
            Affix.MoveSpeed,
            Affix.DamageToMana,
            Affix.PhysDamageReduction,
            Affix.SpellBlock
        ]
    )
    parse_explicit_mods(
        item, 'Amulet', stats,
        parsers=[
            # Prefix
            Affix.AddedColdAttackDamage,
            Affix.AddedFireAttackDamage,
            Affix.AddedLightningAttackDamage,
            Affix.AddedPhysAttackDamage,
            Affix.IncreasedEnergyShield,
            Affix.IncreasedEvasion,
            Affix.AddedEnergyShield,
            Affix.Life,
            Affix.Mana,
            Affix.IncreasedArmour,
            Affix.IncreasedWeaponEleDamage,
            Affix.ItemRarity,
            Affix.LifeLeech,
            Affix.ManaLeech,
            Affix.SpellDamage,
            # Suffix
            Affix.AllAttributes,
            Affix.AllElementalResists,
            Affix.FireResist,
            Affix.ColdResist,
            Affix.LightningResist,
            Affix.ChaosResist,
            Affix.GlobalCritChance,
            Affix.GlobalCritMulti,
            Affix.Strength,
            Affix.Dexterity,
            Affix.Intelligence,
            Affix.IncreasedFireDamage,
            Affix.IncreasedColdDamage,
            Affix.IncreasedLightningDamage,
            Affix.Accuracy,
            Affix.CastSpeed,
            Affix.LifeGainOnHit,
            Affix.LifeGainOnKill,
            Affix.LifeRegen,
            Affix.ManaGainOnKill,
            Affix.ManaRegen
        ],
        banned={
            # Master signature mods
            '\-\d+ to Mana Cost of Skills',
            # Essence only
            '(\d+)% increased Chaos Damage',
            '\d+% increased Life Leeched per second',
            'Minions have \d+% increased Movement Speed',
            '\d+% increased effect of Fortify on You',
            '\d+% increased Attack Speed',
            '\d+(\.\d+)?% of Chaos Damage Leeched as Life',
            '10% chance to Recover 10% of Maximum Mana when you use a Skill',
            # Deprecated stats
            '\d+% increased Quantity of Items found',
        }
    )
    return stats


def parse_body(item):
    stats = CaseInsensitiveCounter()
    stats['CannotBeKnockedBack'] = False
    parse_sockets(item, stats)
    parse_corrupted(item, stats)
    parse_armour_properties(item, stats)
    parse_requirements(item, stats)
    parse_implicit_mods(
        item, 'BodyArmour', stats,
        parsers=[
            Affix.Mana,
            Affix.SpellDamage,
            Affix.MoveSpeed,
            Affix.AllElementalResists,
            # Corrupted
            Affix.AvoidFreeze,
            Affix.AvoidIgnite,
            Affix.ChaosResist,
            Affix.GrantedSkillId,
            Affix.GrantedSkillLevel,
            Affix.CannotBeKnockedBack,
            Affix.SocketedGemLevel,
            Affix.SocketedVaalGemLevel,
            Affix.MaxResists,
            Affix.AvoidShock,
            Affix.ManaMultiplier,
        ],
        ignored={
            '\d% reduced Movement Speed'
        },
    )
    parse_explicit_mods(
        item, 'BodyArmour', stats,
        parsers=[
            # Prefix
            Affix.PhysReflect,
            Affix.AddedArmour,
            Affix.AddedEvasion,
            Affix.AddedEnergyShield,
            Affix.IncreasedArmour,
            Affix.IncreasedEvasion,
            Affix.IncreasedEnergyShield,
            Affix.IncreasedArmourAndEvasion,
            Affix.IncreasedArmourAndEnergyShield,
            Affix.IncreasedEvasionAndEnergyShield,
            Affix.IncreasedArmourEvasionAndEnergyShield,
            Affix.Life,
            Affix.Mana,
            # Suffix
            Affix.ChaosResist,
            Affix.FireResist,
            Affix.ColdResist,
            Affix.LightningResist,
            Affix.LifeRegen,
            Affix.Strength,
            Affix.Dexterity,
            Affix.Intelligence,
            Affix.StunRecovery,
        ],
        ignored={
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

    stats = CaseInsensitiveCounter()
    stats['EnemiesCannotLeech'] = False
    parse_sockets(item, stats)
    parse_corrupted(item, stats)
    parse_armour_properties(item, stats)
    parse_requirements(item, stats)
    parse_implicit_mods(
        item, 'Helmet', stats,
        parsers=[
            Affix.MinionDamage,
            # Corrupted
            Affix.ChaosResist,
            Affix.ManaShield,
            Affix.EnemiesCannotLeech,
            Affix.GrantedSkillId,
            Affix.GrantedSkillLevel,
            Affix.SocketedVaalGemLevel,
            Affix.SupportedByCastOnCrit,
            Affix.SupportedByCastOnStun
        ]
    )
    parse_explicit_mods(
        item, 'Helmet', stats,
        parsers = [
            Affix.PhysReflect,
            Affix.AddedArmour,
            Affix.AddedEvasion,
            Affix.AddedEnergyShield,
            Affix.IncreasedArmour,
            Affix.IncreasedEvasion,
            Affix.IncreasedEnergyShield,
            Affix.IncreasedArmourAndEvasion,
            Affix.IncreasedArmourAndEnergyShield,
            Affix.IncreasedEvasionAndEnergyShield,
            Affix.SocketedMinionGemLevel,
            Affix.Life,
            Affix.Mana,
            Affix.ItemRarity,
            # Suffix
            Affix.ChaosResist,
            Affix.ColdResist,
            Affix.Dexterity,
            Affix.FireResist,
            Affix.Accuracy,
            Affix.IncreasedAccuracy,
            Affix.Intelligence,
            Affix.LifeRegen,
            Affix.LightRadius,
            Affix.LightningResist,
            Affix.Strength,
            Affix.StunRecovery
        ],
        ignored={
            '\d+% reduced Attribute Requirements',
        },
        banned={
            # Signature Mod
            '\+\d to Level of Socketed Support Gems',
            # Essences
            'Minions have \d+% increased maximum Life',
            '\d+% reduced Mana Reserved',
            '\d+% chance to Avoid being (Stunned|Shocked|Frozen|Ignited)',
            '\+\d to Level of Socketed Aura Gems',
            'Socketed Gems deal \d+% more Elemental Damage',
            '\d+% of Physical Damage taken as (Fire|Cold|Lightning) Damage',
            'Socketed Gems have \d+% chance to Ignite',
            'Socketed Gems gain \d+% of Physical Damage as extra Lightning Damage',
            # Deprecated
            '\d+% increased Quantity of Items found'
        }
    )
    return stats

def parse_gloves(item):
    if is_enchanted(item):
        raise ItemBannedException('Item is enchanted', item['enchantMods'][0])

    stats = CaseInsensitiveCounter()
    parse_sockets(item, stats)
    parse_corrupted(item, stats)
    parse_armour_properties(item, stats)
    parse_requirements(item, stats)
    parse_implicit_mods(
        item, 'Gloves', stats,
        parsers=[
            Affix.MeleeDamage,
            Affix.ProjectileAttackDamage,
            Affix.SpellDamage,
            # Corrupted
            Affix.ChaosResist,
            Affix.EleWeaknessOnHit,
            Affix.TempChainsOnHit,
            Affix.VulnerabilityOnHit,
            Affix.GrantedSkillId,
            Affix.GrantedSkillLevel,
            Affix.SocketedGemLevel,
            Affix.SocketedVaalGemLevel,
            Affix.CastSpeed,
            Affix.SupportedByCastOnCrit,
            Affix.SupportedByCastOnStun
        ],
    )
    parse_explicit_mods(
        item, 'Gloves', stats,
        parsers=[
            # Prefix
            Affix.AddedColdAttackDamage,
            Affix.AddedArmour,
            Affix.AddedEvasion,
            Affix.AddedEnergyShield,
            Affix.IncreasedArmour,
            Affix.IncreasedEvasion,
            Affix.IncreasedEnergyShield,
            Affix.IncreasedArmourAndEvasion,
            Affix.IncreasedArmourAndEnergyShield,
            Affix.IncreasedEvasionAndEnergyShield,
            Affix.AddedFireAttackDamage,
            Affix.Life,
            Affix.Mana,
            Affix.ItemRarity,
            Affix.LifeLeech,
            Affix.AddedLightningAttackDamage,
            Affix.ManaLeech,
            Affix.AddedPhysAttackDamage,
            # Suffix
            Affix.ChaosResist,
            Affix.ColdResist,
            Affix.Dexterity,
            Affix.FireResist,
            Affix.Accuracy,
            Affix.AttackSpeed,
            Affix.Intelligence,
            Affix.LifeGainOnHit,
            Affix.LifeGainOnKill,
            Affix.LifeRegen,
            Affix.LightningResist,
            Affix.ManaGainOnKill,
            Affix.Strength,
            Affix.StunRecovery,
        ],
        ignored={
            '\d+% reduced Attribute Requirements',
        },
        banned={
            # Essence
            'Socketed Gems have \d+% more Attack and Cast Speed',
            'Socketed Gems have \+\d+(\.\d)?% Critical Strike Chance',
            'Socketed Gems deal 175 to 225 additional Fire Damage',
            'Socketed Gems deal \d+% more Damage over Time',
            'Minions have \d+% increased maximum Life',
            '\d+% increased Global Critical Strike Chance',
            '\d+% increased Life Leeched per second',
            'Your Flasks grant \d+% increased Rarity of Items found while using a Flask',
            '\d+% chance to Avoid being Stunned',
            # Deprecated
            '\d+% increased Quantity of Items found'
        }
    )
    return stats

def parse_boots(item):
    if is_enchanted(item):
        raise ItemBannedException('Item is enchanted', item['enchantMods'][0])

    stats = CaseInsensitiveCounter()
    stats['CannotBeKnockedBack'] = False
    parse_sockets(item, stats)
    parse_corrupted(item, stats)
    parse_armour_properties(item, stats)
    parse_requirements(item, stats)
    parse_implicit_mods(
        item, 'Boots', stats,
        parsers=[
            Affix.FireAndColdResist,
            Affix.FireAndLightningResist,
            Affix.ColdAndLightningResist,
            # Corrupted
            Affix.DodgeAttacks,
            Affix.ChaosResist,
            Affix.GrantedSkillId,
            Affix.GrantedSkillLevel,
            Affix.CannotBeKnockedBack,
            Affix.SocketedGemLevel,
            Affix.SocketedVaalGemLevel,
            Affix.MaxFrenzyCharges,
            Affix.MoveSpeed
        ],
    )
    parse_explicit_mods(
        item, 'Boots', stats,
        parsers=[
            # Prefix
            Affix.AddedArmour,
            Affix.AddedEvasion,
            Affix.AddedEnergyShield,
            Affix.IncreasedArmour,
            Affix.IncreasedEvasion,
            Affix.IncreasedEnergyShield,
            Affix.IncreasedArmourAndEvasion,
            Affix.IncreasedArmourAndEnergyShield,
            Affix.IncreasedEvasionAndEnergyShield,
            Affix.Life,
            Affix.Mana,
            Affix.ItemRarity,
            Affix.MoveSpeed,
            # Suffix
            Affix.ChaosResist,
            Affix.ColdResist,
            Affix.Dexterity,
            Affix.FireResist,
            Affix.Intelligence,
            Affix.LifeRegen,
            Affix.LightningResist,
            Affix.Strength,
            Affix.StunRecovery
        ],
        ignored={
            '\d+% reduced Attribute Requirements',
        },
        banned={
            # Essence
            'Minions have \d+% increased maximum Life',
            '\d+% chance to Avoid being (Stunned|Shocked|Frozen|Ignited)',
            'Reflects \d+ Physical Damage to Melee Attackers',
            '\d+% chance to Dodge Attacks',
            'Cannot be Frozen',
            'Drops Burning Ground while moving, dealing 2500 Fire Damage per second',
            '\d+% chance to Dodge Spell Damage',
            # Deprecated
            '\d+% increased Quantity of Items found'
        }
    )
    return stats


def parse_belt(item):
    stats = CaseInsensitiveCounter()
    parse_corrupted(item, stats)
    parse_requirements(item, stats, level_only=True)
    parse_implicit_mods(
        item, 'Belt', stats,
        parsers=[
            Affix.AddedEnergyShield,
            Affix.IncreasedPhysDamage,
            Affix.Strength,
            Affix.Life,
            Affix.StunRecovery,
            Affix.StunDuration,
            Affix.AddedArmourAndEvasion,
            # Corrupted
            Affix.IncreasedAoE,
            Affix.ChaosResist,
            Affix.GrantedSkillId,
            Affix.GrantedSkillLevel,
            Affix.MaxEnduranceCharges,
            Affix.AvoidShock,
            Affix.SkillDuration,
            Affix.AdditionalTraps
        ],
    )
    parse_explicit_mods(
        item, 'Belt', stats,
        parsers=[
            # Prefix
            Affix.PhysReflect,
            Affix.FlaskLife,
            Affix.FlaskMana,
            Affix.AddedEnergyShield,
            Affix.AddedArmour,
            Affix.Life,
            Affix.IncreasedWeaponEleDamage,
            # Suffix
            Affix.FlaskChargeGain,
            Affix.FlaskChargeUse,
            Affix.FlaskDuration,
            Affix.ChaosResist,
            Affix.ColdResist,
            Affix.FireResist,
            Affix.LifeRegen,
            Affix.LightningResist,
            Affix.Strength,
            Affix.StunDuration,
            Affix.StunRecovery,
            Affix.StunThreshold,
        ],
        banned={
            # Essence
            '^\d+% increased Damage',
            '\d+% chance to Avoid being (Ignited|Frozen|Shocked|Stunned)',
            '\+\d+ to (Dexterity|Intelligence)',
            '\+\d+ to Evasion Rating',
            'Minions have \d+% increased maximum Life',
            '\d+% increased Movement Speed while using a Flask',
            'Damage Penetrates \d+% Elemental Resistances while using a Flask',
        }
    )
    return stats


def parse_quiver(item):
    stats = CaseInsensitiveCounter()
    stats['AddedArrow'] = False
    parse_corrupted(item, stats)
    parse_requirements(item, stats, level_only=True)
    parse_implicit_mods(
        item, 'Quiver', stats,
        parsers=[
            Affix.IncreasedAccuracy,
            Affix.AddedPhysBowDamage,
            Affix.LifeGainOnHit,
            Affix.StunDuration,
            Affix.AddedFireBowDamage,
            Affix.Pierce,
            Affix.GlobalCritChance,
            # Corrupted
            Affix.AddedArrow,
            Affix.ChaosResist,
            Affix.LifeLeechCold,
            Affix.PhysToCold,
            Affix.PhysToFire,
            Affix.LifeLeechFire,
            Affix.GrantedSkillId,
            Affix.GrantedSkillLevel,
            Affix.PhysToLightning,
            Affix.LifeLeechLightning
        ]
    )
    parse_explicit_mods(
        item, 'Quiver', stats,
        parsers=[
            # Prefix
            Affix.AddedColdAttackDamage,
            Affix.AddedFireAttackDamage,
            Affix.Life,
            Affix.IncreasedWeaponEleDamage,
            Affix.LifeLeech,
            Affix.AddedLightningAttackDamage,
            Affix.ManaLeech,
            Affix.AddedPhysAttackDamage,
            # Suffix
            Affix.ChaosResist,
            Affix.ColdResist,
            Affix.GlobalCritChance,
            Affix.GlobalCritMulti,
            Affix.Dexterity,
            Affix.FireResist,
            Affix.Accuracy,
            Affix.AttackSpeed,
            Affix.LifeGainOnKill,
            Affix.LightningResist,
            Affix.ManaGainOnKill,
            Affix.ProjectileSpeed,
            Affix.StunDuration
        ],
        banned=[
            # Essence
            'Adds \d+ to \d+ Cold Damage per Frenzy Charge',
            '\d+% increased Damage with Poison',
            'Minions have \d+% increased Movement Speed',
        ]
    )
    return stats


def parse_shield(item):
    stats = CaseInsensitiveCounter()
    parse_sockets(item, stats)
    parse_corrupted(item, stats)
    parse_shield_properties(item, stats)
    parse_requirements(item, stats)
    parse_implicit_mods(
        item, 'Shield', stats,
        parsers=[
            Affix.SpellDamage,
            Affix.BlockRecovery,
            Affix.AllElementalResists,
            Affix.PhysReflect,
            # Corrupted
            Affix.AvoidIgnite,
            Affix.ChaosResist,
            Affix.GrantedSkillId,
            Affix.GrantedSkillLevel,
            Affix.SocketedGemLevel,
            Affix.SocketedVaalGemLevel,
            Affix.CastSpeed,
            Affix.DamageToMana,
            Affix.PhysDamageReduction,
            Affix.SpellBlock
        ]
    )
    parse_explicit_mods(
        item, 'Shield', stats,
        parsers=[
            # Prefix
            Affix.PhysReflect,
            Affix.AddedArmour,
            Affix.AddedEvasion,
            Affix.AddedEnergyShield,
            Affix.IncreasedArmour,
            Affix.IncreasedEvasion,
            Affix.IncreasedEnergyShield,
            Affix.IncreasedArmourAndEvasion,
            Affix.IncreasedArmourAndEnergyShield,
            Affix.IncreasedEvasionAndEnergyShield,
            Affix.SocketedMeleeGemLevel,
            Affix.SocketedChaosGemLevel,
            Affix.SocketedColdGemLevel,
            Affix.SocketedFireGemLevel,
            Affix.SocketedLightningGemLevel,
            Affix.Life,
            Affix.Mana,
            Affix.SpellDamage,
            # Suffix
            Affix.AllElementalResists,
            Affix.ChaosResist,
            Affix.ColdResist,
            Affix.Dexterity,
            Affix.FireResist,
            Affix.Intelligence,
            Affix.LifeRegen,
            Affix.LightningResist,
            Affix.ManaRegen,
            Affix.SpellCrit,
            Affix.Strength,
            Affix.StunRecovery
        ],
        ignored=[
            '\+\d+% Chance to Block',
            '\d+% reduced Attribute Requirements',
        ],
        banned=[
            # Signature Mod
            '\+\d+ to Level of Socketed Support Gems',
            # Essence
            '\d+% chance to Avoid (Fire|Cold|Lightning) Damage when Hit',
            'Minions have \d+% increased maximum Life'
        ]
    )
    return stats

def parse_wand(item):
    stats = CaseInsensitiveCounter()
    stats['CullingStrike'] = False
    parse_sockets(item, stats)
    parse_corrupted(item, stats)
    parse_weapon_properties(item, stats)
    parse_requirements(item, stats)
    parse_implicit_mods(
        item, 'Wand', stats,
        parsers=[
            Affix.SpellDamage,
            Affix.CastSpeed,
            # Corrupted
            Affix.LifeLeechCold,
            Affix.CullingStrike,
            Affix.SupportedByEleProlif,
            Affix.LifeLeechFire,
            Affix.GrantedSkillId,
            Affix.GrantedSkillLevel,
            Affix.ChanceToFlee,
            Affix.LifeLeechLightning,
            Affix.Pierce
        ],
        ignored=[
            'Adds \d+ to \d+ Chaos Damage'
        ]
    )
    parse_explicit_mods(
        item, 'Wand', stats,
        parsers=[
            Affix.SocketedGemLevel,
            Affix.SocketedChaosGemLevel,
            Affix.SocketedColdGemLevel,
            Affix.SocketedFireGemLevel,
            Affix.SocketedLightningGemLevel,
            Affix.Mana,
            Affix.IncreasedWeaponEleDamage,
            Affix.LifeLeech,
            Affix.IncreasedPhysDamage,
            Affix.ManaLeech,
            Affix.AddedPhysDamageLocal,
            Affix.AddedSpellColdDamage,
            Affix.AddedSpellFireDamage,
            Affix.AddedSpellLightningDamage,
            Affix.SpellDamage,
            # Suffix
            Affix.ChaosResist,
            Affix.IncreasedColdDamage,
            Affix.ColdResist,
            Affix.GlobalCritMulti,
            Affix.IncreasedFireDamage,
            Affix.FireResist,
            Affix.Accuracy,
            Affix.CastSpeed,
            Affix.Intelligence,
            Affix.LifeGainOnHit,
            Affix.LifeGainOnKill,
            Affix.LightRadius,
            Affix.IncreasedAccuracy,
            Affix.IncreasedLightningDamage,
            Affix.LightningResist,
            Affix.ManaGainOnKill,
            Affix.ManaRegen,
            Affix.ProjectileSpeed,
            Affix.SpellCrit,
            Affix.StunDuration
        ],
        ignored={
            '\d+% increased Critical Strike Chance',
            '\d+% increased Attack Speed',
            '\d+% reduced Attribute Requirements',
            'Adds \d+ to \d+ (Cold|Fire|Lightning|Chaos) Damage',
        },
        banned={
            'Your Hits inflict Decay, dealing 750 Chaos Damage per second for 10 seconds',
            'Minions deal \d+% increased Damage',
            '\d+% chance to gain a Power, Frenzy or Endurance Charge on Kill',
            'Casts level 20 Spectral Spirits when equipped',
            # Signature Mod
            '\+\d+% to Quality of Socketed Support Gems',
        }
    )
    return stats


def parse_staff(item):
    stats = CaseInsensitiveCounter()
    parse_sockets(item, stats)
    parse_corrupted(item, stats)
    parse_weapon_properties(item, stats)
    parse_requirements(item, stats)
    parse_implicit_mods(
        item, 'Staff', stats,
        parsers=[
            Affix.BlockChance,
            Affix.GlobalCritChance,
            # Corrupted
            Affix.LifeLeechCold,
            Affix.SupportedByIncreasedAoE,
            Affix.LifeLeechFire,
            Affix.ChanceToFlee,
            Affix.MaxPowerCharges,
            Affix.LifeLeechLightning,
            Affix.WeaponRange,
            Affix.SpellBlock,
        ],
        ignored=[
            'Adds \d+ to \d+ Chaos Damage'
        ]
    )
    parse_explicit_mods(
        item, 'Staff', stats,
        parsers=[
            # Prefix
            Affix.SocketedGemLevel,
            Affix.SocketedChaosGemLevel,
            Affix.SocketedColdGemLevel,
            Affix.SocketedFireGemLevel,
            Affix.SocketedLightningGemLevel,
            Affix.SocketedMeleeGemLevel,
            Affix.Mana,
            Affix.IncreasedWeaponEleDamage,
            Affix.LifeLeech,
            Affix.IncreasedPhysDamage,
            Affix.ManaLeech,
            Affix.AddedPhysDamageLocal,
            Affix.AddedSpellColdDamage,
            Affix.AddedSpellFireDamage,
            Affix.AddedSpellLightningDamage,
            Affix.SpellDamage,
            # Suffix
            Affix.ChaosResist,
            Affix.IncreasedColdDamage,
            Affix.ColdResist,
            Affix.GlobalCritMulti,
            Affix.IncreasedFireDamage,
            Affix.FireResist,
            Affix.Accuracy,
            Affix.AttackSpeed,
            Affix.CastSpeed,
            Affix.Intelligence,
            Affix.LifeGainOnHit,
            Affix.LifeGainOnKill,
            Affix.LightRadius,
            Affix.IncreasedAccuracy,
            Affix.IncreasedLightningDamage,
            Affix.LightningResist,
            Affix.ManaGainOnKill,
            Affix.ManaRegen,
            Affix.SpellCrit,
            Affix.Strength,
            Affix.StunDuration,
            Affix.StunThreshold
        ],
        ignored=[
            '\d+% increased Critical Strike Chance',
            '\d+% reduced Attribute Requirements',
            'Adds \d+ to \d+ (Cold|Fire|Lightning|Chaos) Damage'
        ],
        banned=[
            # Master-crafting / Signature Mods
            'Hits can\'t be Evaded',
            # Essence
            'Your Hits inflict Decay, dealing 750 Chaos Damage per second for 10 seconds',
            'Minions deal \d+% increased Damage',
            '10% chance to Cast Level 20 Fire Burst on Hit',
        ]
    )
    return stats


def parse_dagger(item):
    stats = CaseInsensitiveCounter()
    stats['CullingStrike'] = False
    parse_sockets(item, stats)
    parse_corrupted(item, stats)
    parse_weapon_properties(item, stats)
    parse_requirements(item, stats)
    parse_implicit_mods(
        item, 'Dagger', stats,
        parsers=[
            Affix.GlobalCritChance,
            Affix.BlockChance,
            # Corrupted
            Affix.BlockChanceWhileDualWielding,
            Affix.LifeLeechCold,
            Affix.CullingStrike,
            Affix.LifeLeechFire,
            Affix.ChanceToFlee,
            Affix.LifeLeechLightning,
            Affix.WeaponRange,
            Affix.SupportedByIncreasedCritDamage,
            Affix.SupportedByMeleeSplash
        ],
        ignored=[
            # Part of Weapon Stats
            'Adds \d+ to \d+ Chaos Damage'
        ]
    )
    parse_explicit_mods(
        item, 'Dagger', stats,
        parsers=[
            # Prefix
            Affix.SocketedGemLevel,
            Affix.SocketedChaosGemLevel,
            Affix.SocketedColdGemLevel,
            Affix.SocketedFireGemLevel,
            Affix.SocketedLightningGemLevel,
            Affix.SocketedMeleeGemLevel,
            Affix.Mana,
            Affix.IncreasedWeaponEleDamage,
            Affix.LifeLeech,
            Affix.IncreasedPhysDamage,
            Affix.ManaLeech,
            Affix.AddedPhysDamageLocal,
            Affix.AddedSpellColdDamage,
            Affix.AddedSpellFireDamage,
            Affix.AddedSpellLightningDamage,
            Affix.SpellDamage,
            # Suffix
            Affix.ChaosResist,
            Affix.ColdResist,
            Affix.GlobalCritMulti,
            Affix.Dexterity,
            Affix.FireResist,
            Affix.Accuracy,
            Affix.IncreasedAccuracy,
            Affix.Intelligence,
            Affix.LifeGainOnHit,
            Affix.LifeGainOnKill,
            Affix.LightRadius,
            Affix.LightningResist,
            Affix.ManaGainOnKill,
            Affix.ManaRegen,
            Affix.SpellCrit,
            Affix.StunDuration
        ],
        ignored={
            # part of base stats
            '\d+% increased Attack Speed',
            '\d+% increased Critical Strike Chance',
            '\d+% reduced Attribute Requirements',
            'Adds \d+ to \d+ (Cold|Fire|Lightning|Chaos) Damage'
        },
        banned={
            # Master
            'Hits can\'t be Evaded',
            '\+\d+ to Level of Socketed Support Gems',
            # Essence
            'Minions deal \d+% increased Damage',
            'Your Hits inflict Decay, dealing 750 Chaos Damage per second for 10 seconds',
            '\d+% increased Cast Speed',
            'Damage Penetrates \d+% Fire Resistance',
        }
    )
    return stats


def parse_one_hand_sword(item):
    stats = CaseInsensitiveCounter()
    stats['CullingStrike'] = False
    parse_sockets(item, stats)
    parse_corrupted(item, stats)
    parse_weapon_properties(item, stats)
    parse_requirements(item, stats)
    parse_implicit_mods(
        item, 'One Hand Sword', stats,
        parsers=[
            Affix.IncreasedAccuracy,
            Affix.Accuracy,
            Affix.DodgeAttacks,
            Affix.GlobalCritMulti,
            Affix.Bleed,
            # Corrupted
            Affix.BlockChanceWhileDualWielding,
            Affix.LifeLeechCold,
            Affix.CullingStrike,
            Affix.LifeLeechFire,
            Affix.ChanceToFlee,
            Affix.LifeLeechLightning,
            Affix.WeaponRange,
            Affix.SupportedByMeleeSplash,
            Affix.SupportedByMultistrike
        ],
        ignored=[
            'Adds \d+ to \d+ Chaos Damage'
        ]
    )
    parse_explicit_mods(
        item, 'One Hand Sword', stats,
        parsers=[
            # Prefix
            Affix.SocketedGemLevel,
            Affix.SocketedMeleeGemLevel,
            Affix.IncreasedWeaponEleDamage,
            Affix.LifeLeech,
            Affix.IncreasedPhysDamage,
            Affix.ManaLeech,
            Affix.AddedPhysDamageLocal,
            # Suffix
            Affix.ChaosResist,
            Affix.ColdResist,
            Affix.GlobalCritMulti,
            Affix.Dexterity,
            Affix.FireResist,
            Affix.Accuracy,
            Affix.LifeGainOnHit,
            Affix.LifeGainOnKill,
            Affix.LightRadius,
            Affix.IncreasedAccuracy,
            Affix.LightningResist,
            Affix.ManaGainOnKill,
            Affix.Strength,
            Affix.StunDuration,
            Affix.StunThreshold
        ],
        ignored=[
            # part of base stats
            '\d+% increased Attack Speed',
            '\d+% increased Critical Strike Chance',
            '\d+% reduced Attribute Requirements',
            'Adds \d+ to \d+ (Cold|Fire|Lightning|Chaos) Damage',
        ],
        banned=[
            # Master-crafting / Signature Mods
            'Hits can\'t be Evaded',
            '\+\d+% to Quality of Socketed Support Gems',
            # Essence
            '\d+% increased Spell Damage',
            'Casts level 20 Spectral Spirits when equipped',
            'Your Hits inflict Decay, dealing 750 Chaos Damage per second for 10 seconds',
            '\d+% increased Spell Damage',
            'Minions deal \d+% increased Damage',
            '\d+% increased Cast Speed',
        ]
    )
    return stats


def parse_two_hand_sword(item):
    stats = CaseInsensitiveCounter()
    stats['CullingStrike'] = False
    parse_sockets(item, stats)
    parse_corrupted(item, stats)
    parse_weapon_properties(item, stats)
    parse_requirements(item, stats)
    parse_implicit_mods(
        item, 'Two Hand Sword', stats,
        parsers=[
            Affix.IncreasedAccuracy,
            Affix.Accuracy,
            Affix.GlobalCritMulti,
            # Corrupted
            Affix.LifeLeechCold,
            Affix.CullingStrike,
            Affix.LifeLeechFire,
            Affix.ChanceToFlee,
            Affix.MaxPowerCharges,
            Affix.LifeLeechLightning,
            Affix.WeaponRange,
            Affix.SupportedByAdditionalAccuracy
        ],
        ignored=[
            'Adds \d+ to \d+ Chaos Damage'
        ]
    )
    parse_explicit_mods(
        item, 'Two Hand Sword', stats,
        parsers=[
            # Prefix
            Affix.SocketedGemLevel,
            Affix.SocketedMeleeGemLevel,
            Affix.IncreasedWeaponEleDamage,
            Affix.LifeLeech,
            Affix.IncreasedPhysDamage,
            Affix.ManaLeech,
            Affix.AddedPhysDamageLocal,
            # Suffix
            Affix.ChaosResist,
            Affix.ColdResist,
            Affix.GlobalCritMulti,
            Affix.Dexterity,
            Affix.FireResist,
            Affix.Accuracy,
            Affix.LifeGainOnHit,
            Affix.LifeGainOnKill,
            Affix.LightRadius,
            Affix.IncreasedAccuracy,
            Affix.LightningResist,
            Affix.ManaGainOnKill,
            Affix.Strength,
            Affix.StunDuration,
            Affix.StunThreshold
        ],
        ignored=[
            # part of base stats
            '\d+% increased Attack Speed',
            '\d+% increased Critical Strike Chance',
            '\d+% reduced Attribute Requirements',
            'Adds \d+ to \d+ (Cold|Fire|Lightning|Chaos) Damage'
        ],
        banned=[
            # Signature Mod
            'Hits can\'t be Evaded',
            # Essence
            '\+\d+ to Level of Socketed (Cold|Fire|Lightning) Gems',
            '\d+% increased Spell Damage',
            'Minions deal \d+% increased Damage',
        ]
    )
    return stats


def parse_one_hand_axe(item):
    stats = CaseInsensitiveCounter()
    stats['CullingStrike'] = False
    parse_sockets(item, stats)
    parse_corrupted(item, stats)
    parse_weapon_properties(item, stats)
    parse_requirements(item, stats)
    parse_implicit_mods(
        item, 'One Hand Axe', stats,
        parsers=[
            Affix.IncreasedPhysDamage,
            # Corrupted
            Affix.LifeLeechCold,
            Affix.CullingStrike,
            Affix.LifeLeechFire,
            Affix.GrantedSkillId,
            Affix.GrantedSkillLevel,
            Affix.ChanceToFlee,
            Affix.LifeLeechLightning,
            Affix.WeaponRange,
            Affix.SupportedByMeleeSplash
        ],
        ignored=[
            'Adds \d+ to \d+ Chaos Damage'
        ]
    )
    parse_explicit_mods(
        item, 'One Hand Axe', stats,
        parsers=[
            # Prefix
            Affix.SocketedGemLevel,
            Affix.SocketedMeleeGemLevel,
            Affix.IncreasedWeaponEleDamage,
            Affix.LifeLeech,
            Affix.IncreasedPhysDamage,
            Affix.ManaLeech,
            Affix.AddedPhysDamageLocal,
            # Suffix
            Affix.ChaosResist,
            Affix.ColdResist,
            Affix.GlobalCritMulti,
            Affix.Dexterity,
            Affix.FireResist,
            Affix.Accuracy,
            Affix.LifeGainOnHit,
            Affix.LifeGainOnKill,
            Affix.LightRadius,
            Affix.IncreasedAccuracy,
            Affix.LightningResist,
            Affix.ManaGainOnKill,
            Affix.Strength,
            Affix.StunDuration,
            Affix.StunThreshold
        ],
        ignored=[
            # part of base stats
            '\d+% increased Attack Speed',
            '\d+% increased Critical Strike Chance',
            '\d+% reduced Attribute Requirements',
            'Adds \d+ to \d+ (Cold|Fire|Lightning|Chaos) Damage'
        ],
        banned=[
            # Signature mods
            'Hits can\'t be Evaded',
        ]
    )
    return stats


def parse_two_hand_axe(item):
    stats = CaseInsensitiveCounter()
    stats['CullingStrike'] = False
    parse_sockets(item, stats)
    parse_corrupted(item, stats)
    parse_weapon_properties(item, stats)
    parse_requirements(item, stats)
    parse_implicit_mods(
        item, 'Two Hand Axe', stats,
        parsers=[
            # Corrupted
            Affix.LifeLeechCold,
            Affix.CullingStrike,
            Affix.LifeLeechFire,
            Affix.GrantedSkillLevel,
            Affix.GrantedSkillId,
            Affix.ChanceToFlee,
            Affix.MaxPowerCharges,
            Affix.LifeLeechLightning,
            Affix.WeaponRange
        ],
        ignored=[
            '\d+% increased Critical Strike Chance',
            'Adds \d+ to \d+ Chaos Damage'
        ]
    )
    parse_explicit_mods(
        item, "Two Hand Axe", stats,
        parsers=[
            # Prefix
            Affix.SocketedGemLevel,
            Affix.SocketedMeleeGemLevel,
            Affix.IncreasedWeaponEleDamage,
            Affix.LifeLeech,
            Affix.IncreasedPhysDamage,
            Affix.ManaLeech,
            Affix.AddedPhysDamageLocal,
            # Suffix
            Affix.ChaosResist,
            Affix.ColdResist,
            Affix.GlobalCritMulti,
            Affix.Dexterity,
            Affix.FireResist,
            Affix.Accuracy,
            Affix.LifeGainOnHit,
            Affix.LifeGainOnKill,
            Affix.LightRadius,
            Affix.IncreasedAccuracy,
            Affix.LightningResist,
            Affix.ManaGainOnKill,
            Affix.Strength,
            Affix.StunDuration,
            Affix.StunThreshold
        ],
        ignored=[
            # part of base stats
            '\d+% increased Attack Speed',
            '\d+% increased Critical Strike Chance',
            '\d+% reduced Attribute Requirements',
            'Adds \d+ to \d+ (Cold|Fire|Lightning|Chaos) Damage',
        ],
        banned=[
            # Essence
            '\+\d to Weapon range',
            '\+\d to Level of Socketed (Cold|Fire|Lightning) Gems',
            '\d+% increased Spell Damage',
        ]
    )
    return stats


def parse_one_hand_mace(item):
    stats = CaseInsensitiveCounter()
    parse_sockets(item, stats)
    parse_corrupted(item, stats)
    parse_weapon_properties(item, stats)
    parse_requirements(item, stats)
    parse_implicit_mods(
        item, 'One Hand Mace', stats,
        parsers=[
            Affix.StunThreshold,
            # Corrupted
            Affix.LifeLeechCold,
            Affix.SupportedByAddedFireDamage,
            Affix.LifeLeechFire,
            Affix.ChanceToFlee,
            Affix.LifeLeechLightning,
            Affix.WeaponRange,
            Affix.SupportedByMeleeSplash,
            Affix.SupportedByStun,
        ],
        ignored=[
            'Adds \d+ to \d+ Chaos Damage',
            '\d+% increased Attack Speed',
        ],
        banned=[
            # Legacy
            '\d+% increased Stun Duration on Enemies'
        ]
    )
    parse_explicit_mods(
        item, 'One Hand Mace', stats,
        parsers=[
            # Prefix
            Affix.SocketedGemLevel,
            Affix.SocketedMeleeGemLevel,
            Affix.IncreasedWeaponEleDamage,
            Affix.LifeLeech,
            Affix.IncreasedPhysDamage,
            Affix.ManaLeech,
            Affix.AddedPhysDamageLocal,
            # Suffix
            Affix.ChaosResist,
            Affix.ColdResist,
            Affix.GlobalCritMulti,
            Affix.FireResist,
            Affix.Accuracy,
            Affix.LifeGainOnHit,
            Affix.LifeGainOnKill,
            Affix.LightRadius,
            Affix.IncreasedAccuracy,
            Affix.LightningResist,
            Affix.ManaGainOnKill,
            Affix.Strength,
            Affix.StunDuration,
            Affix.StunThreshold,
        ],
        ignored=[
            # part of base stats
            '\d+% increased Attack Speed',
            '\d+% increased Critical Strike Chance',
            '\d+% reduced Attribute Requirements',
            'Adds \d+ to \d+ (Cold|Fire|Lightning|Chaos) Damage'
        ]
    )
    return stats


def parse_two_hand_mace(item):
    stats = CaseInsensitiveCounter()
    parse_sockets(item, stats)
    parse_corrupted(item, stats)
    parse_weapon_properties(item, stats)
    parse_requirements(item, stats)
    parse_implicit_mods(
        item, 'Two Hand Mace', stats,
        parsers=[
            Affix.StunDuration,
            Affix.IncreasedAoE,
            # Corrupted
            Affix.LifeLeechCold,
            Affix.LifeLeechFire,
            Affix.ChanceToFlee,
            Affix.MaxPowerCharges,
            Affix.LifeLeechLightning,
            Affix.WeaponRange,
            Affix.SupportedByStun
        ],
        ignored=[
            'Adds \d+ to \d+ Chaos Damage'
        ]
    )
    parse_explicit_mods(
        item, 'Two Hand Mace', stats,
        parsers=[
            # Prefix
            Affix.SocketedGemLevel,
            Affix.SocketedMeleeGemLevel,
            Affix.IncreasedWeaponEleDamage,
            Affix.LifeLeech,
            Affix.IncreasedPhysDamage,
            Affix.ManaLeech,
            Affix.AddedPhysDamageLocal,
            # Suffix
            Affix.ChaosResist,
            Affix.ColdResist,
            Affix.GlobalCritMulti,
            Affix.FireResist,
            Affix.Accuracy,
            Affix.LifeGainOnHit,
            Affix.LifeGainOnKill,
            Affix.LightRadius,
            Affix.IncreasedAccuracy,
            Affix.LightningResist,
            Affix.ManaGainOnKill,
            Affix.Strength,
            Affix.StunDuration,
            Affix.StunThreshold
        ],
        ignored = [
            # part of base stats
            '\d+% increased Attack Speed',
            '\d+% increased Critical Strike Chance',
            '\d+% reduced Attribute Requirements',
            'Adds \d+ to \d+ (Cold|Fire|Lightning|Chaos) Damage'
        ],
        banned=[
            # Essence
            'Minions deal \d+% increased Damage',
            '\+\d to Level of Socketed (Fire|Cold|Lightning) Gems',
            '\d+% increased Spell Damage',
        ]
    )
    return stats


def parse_bow(item):
    stats = CaseInsensitiveCounter()
    stats['CullingStrike'] = False
    stats['AddedArrow'] = False
    parse_sockets(item, stats)
    parse_corrupted(item, stats)
    parse_weapon_properties(item, stats)
    parse_requirements(item, stats)
    parse_implicit_mods(
        item, 'Bow', stats,
        parsers=[
            Affix.IncreasedWeaponEleDamage,
            Affix.MoveSpeed,
            # Corrupted
            Affix.AddedArrow,
            Affix.Pierce,
            Affix.LifeLeechCold,
            Affix.CullingStrike,
            Affix.LifeLeechFire,
            Affix.ChanceToFlee,
            Affix.MaxPowerCharges,
            Affix.LifeLeechLightning,
            Affix.SupportedByFork,
        ],
        ignored=[
            '\d+% increased Critical Strike Chance',
            'Adds \d+ to \d+ Chaos Damage'
        ]
    )
    parse_explicit_mods(
        item, 'Bow', stats,
        parsers=[
            # Prefix
            Affix.SocketedGemLevel,
            Affix.SocketedBowGemLevel,
            Affix.IncreasedWeaponEleDamage,
            Affix.LifeLeech,
            Affix.IncreasedPhysDamage,
            Affix.ManaLeech,
            Affix.AddedPhysDamageLocal,
            # Suffix
            Affix.ChaosResist,
            Affix.ColdResist,
            Affix.GlobalCritMulti,
            Affix.Dexterity,
            Affix.FireResist,
            Affix.Accuracy,
            Affix.LifeGainOnHit,
            Affix.LifeGainOnKill,
            Affix.LightRadius,
            Affix.IncreasedAccuracy,
            Affix.LightningResist,
            Affix.ManaGainOnKill,
            Affix.ProjectileSpeed,
            Affix.StunDuration
        ],
        ignored=[
            # part of base stats
            '\d+% increased Attack Speed',
            '\d+% increased Critical Strike Chance',
            '\d+% reduced Attribute Requirements',
            'Adds \d+ to \d+ (Cold|Fire|Lightning|Chaos) Damage',
        ],
        banned=[
            # Signature Mod
            'Causes Bleeding on Hit',
            # Essence
            '\d+% increased Spell Damage',
            '\d+% increased Cast Speed',
            '\d+% chance to Cast Level 20 Fire Burst on Hit',
            'Minions deal \d+% increased Damage',
            '\+\d to Level of Socketed (Cold|Fire|Lightning) Gems',
            'Your Hits inflict Decay, dealing 750 Chaos Damage per second for 10 seconds',
        ]
    )
    return stats


def parse_claw(item):
    stats = CaseInsensitiveCounter()
    stats['CullingStrike'] = False
    parse_sockets(item, stats)
    parse_corrupted(item, stats)
    parse_weapon_properties(item, stats)
    parse_requirements(item, stats)
    parse_implicit_mods(
        item, 'Claw', stats,
        parsers=[
            Affix.LifeGainOnHit,
            Affix.ManaGainOnHit,
            Affix.LifeAndManaGainOnHit,
            Affix.LifeLeech,
            # Corrupted
            Affix.BlockChanceWhileDualWielding,
            Affix.LifeLeechCold,
            Affix.CullingStrike,
            Affix.LifeLeechFire,
            Affix.ChanceToFlee,
            Affix.LifeLeechLightning,
            Affix.WeaponRange,
            Affix.SupportedByLifeLeech,
            Affix.SupportedByMeleeSplash
        ],
        ignored=[
            'Adds \d+ to \d+ Chaos Damage'
        ]
    )
    parse_explicit_mods(
        item, 'Claw', stats,
        parsers=[
            # Prefix
            Affix.SocketedGemLevel,
            Affix.SocketedMeleeGemLevel,
            Affix.Mana,
            Affix.IncreasedWeaponEleDamage,
            Affix.LifeLeech,
            Affix.IncreasedPhysDamage,
            Affix.ManaLeech,
            Affix.AddedPhysDamageLocal,
            # Suffix
            Affix.ChaosResist,
            Affix.ColdResist,
            Affix.GlobalCritMulti,
            Affix.Dexterity,
            Affix.FireResist,
            Affix.Accuracy,
            Affix.Intelligence,
            Affix.LifeGainOnHit,
            Affix.LifeGainOnKill,
            Affix.LightRadius,
            Affix.IncreasedAccuracy,
            Affix.LightningResist,
            Affix.ManaGainOnKill,
            Affix.ManaRegen,
            Affix.StunDuration
        ],
        ignored=[
            # part of base stats
            '\d+% increased Attack Speed',
            '\d+% increased Critical Strike Chance',
            '\d+% reduced Attribute Requirements',
            'Adds \d+ to \d+ (Cold|Fire|Lightning|Chaos) Damage'
        ],
        banned=[
            # Master-crafting / Signature Mods
            'Hits can\'t be Evaded',
            # Essence
            'Your Hits inflict Decay, dealing 750 Chaos Damage per second for 10 seconds',
        ]
    )
    return stats


def parse_sceptre(item):
    stats = CaseInsensitiveCounter()
    parse_sockets(item, stats)
    parse_corrupted(item, stats)
    parse_weapon_properties(item, stats)
    parse_requirements(item, stats)
    parse_implicit_mods(
        item, 'Sceptre', stats,
        parsers=[
            Affix.IncreasedEleDamage,
            Affix.PenetrateEleResist,
            # Corrupted
            Affix.LifeLeechCold,
            Affix.PhysToCold,
            Affix.PhysToFire,
            Affix.SupportedByFasterCasting,
            Affix.LifeLeechFire,
            Affix.ChanceToFlee,
            Affix.PhysToLightning,
            Affix.LifeLeechLightning,
            Affix.SupportedByMeleeSplash,
            Affix.SupportedByWED
        ],
        ignored=[
            'Adds \d+ to \d+ Chaos Damage'
        ]
    )
    parse_explicit_mods(
        item, 'Sceptre', stats,
        parsers=[
            # Prefix
            Affix.SocketedGemLevel,
            Affix.SocketedColdGemLevel,
            Affix.SocketedFireGemLevel,
            Affix.SocketedLightningGemLevel,
            Affix.SocketedMeleeGemLevel,
            Affix.Mana,
            Affix.IncreasedWeaponEleDamage,
            Affix.LifeLeech,
            Affix.IncreasedPhysDamage,
            Affix.ManaLeech,
            Affix.AddedPhysDamageLocal,
            Affix.AddedSpellColdDamage,
            Affix.AddedSpellFireDamage,
            Affix.AddedSpellLightningDamage,
            Affix.SpellDamage,
            # Suffix
            Affix.ChaosResist,
            Affix.IncreasedColdDamage,
            Affix.ColdResist,
            Affix.GlobalCritMulti,
            Affix.IncreasedFireDamage,
            Affix.FireResist,
            Affix.Accuracy,
            Affix.CastSpeed,
            Affix.Intelligence,
            Affix.LifeGainOnHit,
            Affix.LifeGainOnKill,
            Affix.LightRadius,
            Affix.IncreasedAccuracy,
            Affix.IncreasedLightningDamage,
            Affix.LightningResist,
            Affix.ManaGainOnKill,
            Affix.ManaRegen,
            Affix.SpellCrit,
            Affix.Strength,
            Affix.StunDuration,
            Affix.StunThreshold
        ],
        ignored=[
            # part of base stats
            '\d+% increased Attack Speed',
            '\d+% increased Critical Strike Chance',
            '\d+% reduced Attribute Requirements',
            'Adds \d+ to \d+ (Cold|Fire|Lightning|Chaos) Damage'
        ],
        banned=[
            # Signature mods
            'Hits can\'t be Evaded',
            # Essence
            '10% chance to Cast Level 20 Fire Burst on Hit',
            'Minions deal \d+% increased Damage',
            'Your Hits inflict Decay, dealing 750 Chaos Damage per second for 10 seconds',
        ]
    )
    return stats


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


def parse_armour_properties(item, stats):
    stats['Quality'] = read_quality(item)
    stats['Armour'] = read_int_property('Armour', item)
    stats['Evasion'] = read_int_property('Evasion Rating', item)
    stats['EnergyShield'] = read_int_property('Energy Shield', item)


def parse_shield_properties(item, stats):
    stats['Quality'] = read_quality(item)
    stats['Armour'] = read_int_property('Armour', item)
    stats['Evasion'] = read_int_property('Evasion Rating', item)
    stats['EnergyShield'] = read_int_property('Energy Shield', item)
    stats['Block'] = read_percent_property('Chance to Block', item)


def parse_weapon_properties(item, stats):
    stats['Quality'] = read_quality(item)
    stats['PhysDamage'] = read_range_property('Physical Damage', item)
    stats['EleDamage'] = read_range_property('Elemental Damage', item)
    stats['ChaosDamage'] = read_range_property('Chaos Damage', item)
    stats['AttacksPerSecond'] = read_float_property('Attacks per Second', item)
    stats['CritChance'] = read_percent_property('Critical Strike Chance', item, scale=100)


def parse_requirements(item, stats, level_only=False, ignore_others=False):
    stats['ReqLevel'] = 0

    if not level_only:
        stats['ReqStr'] = 0
        stats['ReqDex'] = 0
        stats['ReqInt'] = 0

    if 'requirements' not in item:
        return

    for requirement in item['requirements']:
        if requirement['name'][:3] not in {'Lev', 'Str', 'Dex', 'Int'}:
            raise ItemParserException('Unknown requirement: ' + requirement['name'])
        if level_only and requirement['name'][:3] != 'Lev':
            if ignore_others:
                continue
            raise ItemParserException(
                'Expected only level requirement but found {} on {} item'.format(
                    requirement['name'], itemtype.get_name(item['type'])
                ))
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


def read_float_property(property_name, item, default_value=0):
    values = read_property(property_name, item)
    if values is None or len(values) == 0:
        return default_value
    return float(values[0][0])


def read_percent_property(property_name, item, default_value=0, scale=1):
    values = read_property(property_name, item)
    if values is None or len(values) == 0:
        return default_value
    return int(float(values[0][0][:-1]) * scale)


def read_range_property(property_name, item, default_value=0):
    """
    Reads a property that can either be an integer or a range A-B.
    Returns twice the average, to avoid rounding issues.
    """
    values = read_property(property_name, item)
    if values is None or len(values) == 0:
        return default_value
    numbers = values[0][0].split('-')
    if len(numbers) == 1:
        return int(numbers[0]) * 2  # must be x2 because this is X-X range
    elif len(numbers) == 2:
        return int(numbers[0]) + int(numbers[1])
    else:
        raise ItemParserException("Invalid {} range: {}".format(property_name, values[0][0]))


def read_quality(item):
    for property in item['properties']:
        if property['name'] == 'Quality':
            return int(property['values'][0][0][1:-1])
    return 0


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
    stats = PARSERS[item_type](item)
    return stats


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
    'Assassin\'s Mark': 10,
    'Haste': 11,
    'Temporal Chains': 12,
    'Vitality': 13,
    'Determination': 14,
    'Discipline': 15,
    'Grace': 16,
    'Hatred': 17,
    'Elemental Weakness': 18,
    'Anger': 19,
    'Vulnerability': 20,
    'Projectile Weakness': 21,
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
