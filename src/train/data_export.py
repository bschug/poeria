from datetime import datetime
from functools import partial
from itertools import groupby
import dateutil.parser
import pytz
import os
import argparse

import psycopg2
import pandas as pd
import numpy as np

import constants
from constants import itemtype, currency, league
from indexer import itemdb


class DataExporter(object):
    def __init__(self, db, league=league.STANDARD, flavour='Both', league_end=None,
                 min_valuable_price=2, max_worthless_price=1, fresh_seconds=3*24*60*60):
        """
        :param db:      psycopg2 db instance
        :param league:  League ID for which to export data
        :param flavour: League flavour (Softcore, Hardcore, Both)
        :param league_end: datetime when the league has ended
        :param min_valuable_price: Items sold at this or more are valuable
        :param max_worthless_price: Unsold items listed at less than this are worthless
        :param fresh_seconds: Only items that were on offer for this long can be worthless
        """
        self.db = db
        self.league = league
        self.flavour = flavour
        self.league_end = league_end
        self.min_valuable_price = min_valuable_price
        self.max_worthless_price = max_worthless_price
        self.fresh_seconds = fresh_seconds
        self.exchange_rates = currency.get_exchange_rates(constants.league.get_name(league))

    def export(self, itype, filename):
        print()
        print("Exporting ", filename)
        items = self.get_data_from_db(itype)
        self.categorize(items)
        if is_weapon(itype):
            normalize_weapon_quality(items)
        if is_armour(itype):
            normalize_armour_quality(items)
        if can_have_six_sockets(itype):
            featurize_sockets(items)
        combine_resistances(items)
        apply_attribute_boni(items)
        remove_columns('ItemId', 'Hash', 'Sockets', 'GrantedSkillId', 'GrantedSkillLevel',
                       'AddedTime', 'SoldTime', 'SeenTime', 'Price', 'Currency')
        items.to_csv(filename)

    def get_data_from_db(self, itype):
        tablename = itemtype.get_name(itype) + 'Items'
        columns = ['s.Price', 's.Currency', 's.AddedTime', 's.SoldTime', 's.SeenTime'] + \
                  ['x.' + x for x in DB_COLUMNS[itype]]
        min_league = self.league + 1 if self.flavour == 'Hardcore' else self.league
        max_league = self.league if self.flavour == 'Softcore' else self.league + 1
        sql = 'SELECT ' + ', '.join(columns) + \
              '  FROM StashContents s, ' + tablename + ' x ' + \
              ' WHERE s.ItemId = x.ItemId ' + \
              '   AND s.League >= %(min_league)s ' + \
              '   AND s.League <= %(max_league)s '
        items = pd.read_sql(
            sql, self.db, params={'min_league': min_league, 'max_league': max_league})

        # Column names are all lowercase because postgres, so let's make them readable again.
        # Our columns list has the correct spelling, but is prefixed by "x." and "s."
        column_mapping = {x[2:].lower(): x[2:] for x in columns}
        items.columns = [column_mapping[x] for x in items.columns]

        print("Got data from db: ", items.columns)
        return items

    def categorize(self, items):
        print("categorizing...")
        items['valuable'] = items.apply(self.is_item_valuable, axis=1)
        items['worthless'] = items.apply(self.is_item_worthless, axis=1)
        print("{} valuable / {} worthless".format(items.valuable.sum(), items.worthless.sum()))

        # Remove all items where we can't tell if they're valuable or worthless
        items = items[items.valuable | items.worthless]

        # We don't need the worthless column anymore because an item can only be
        # valuable or worthless, never both, so it's implicitly covered by valuable now.
        del items['worthless']

    def is_item_valuable(self, item):
        """
        Checks if an item is valuable or not.
        May also return None if we can't tell.
        """
        if self.league_end is not None and item.SoldTime > self.league_end:
            return False

        sold = is_item_sold(item)
        price = self.convert_to_chaos(item.Price, item.Currency)

        # If item was sold at min price or higher, it's valuable
        if price >= self.min_valuable_price and sold:
            return True

        return False

    def is_item_worthless(self, item):
        price = self.convert_to_chaos(item.Price, item.Currency)
        fresh = (item.SeenTime - item.AddedTime).total_seconds() < self.fresh_seconds

        # If item was offered for a low price for more than the fresh time, assume it's worthless
        if price < self.max_worthless_price and not fresh:
            return True

        # If item is offered for a low price but the offer is younger than a day, ignore it

        # If item is sold for less than min price, ignore it
        # because we don't know if the buyer would have also bought it at a higher price

        return False

    def convert_to_chaos(self, price, currency):
        return price * self.exchange_rates[currency]


def is_weapon(itype):
    return itype in [
        itemtype.WAND, itemtype.STAFF, itemtype.DAGGER, itemtype.ONE_HAND_SWORD,
        itemtype.TWO_HAND_SWORD, itemtype.ONE_HAND_AXE, itemtype.TWO_HAND_AXE,
        itemtype.ONE_HAND_MACE, itemtype.TWO_HAND_MACE, itemtype.BOW, itemtype.CLAW,
        itemtype.SCEPTRE
    ]


def is_armour(itype):
    return itype in [
        itemtype.BODY, itemtype.HELMET, itemtype.GLOVES, itemtype.BOOTS, itemtype.SHIELD
    ]


def can_have_six_sockets(itype):
    return itype in [
        itemtype.BODY, itemtype.TWO_HAND_AXE, itemtype.TWO_HAND_MACE,
        itemtype.TWO_HAND_SWORD, itemtype.STAFF, itemtype.BOW
    ]


def is_item_sold(item):
    return item.SoldTime >= item.SeenTime


def normalize_armour_quality(items):
    """
    Normalizes all defenses to 20% quality.
    Quality is an Increased multiplier, so it applies to the base value, before factoring
    in other multipliers and flat boni.
    Therefore, we need to compute the base value first and then add the missing quality.
    We also add 0.5 to the result to round to the nearest integer instead of the next lower one.
    :param items:
    :return:
    """
    print("normalizing quality...")
    armour_multi = (items.IncreasedArmour + items.Quality + 100) / 100
    base_armour = (items.Armour - items.AddedArmour) / armour_multi
    items.Armour = (base_armour * (items.IncreasedArmour + 120) / 100 + items.AddedArmour + 0.5).astype(np.int16)
    del items['IncreasedArmour']
    del items['AddedArmour']

    evasion_multi = (items.IncreasedEvasion + items.Quality + 100) / 100
    base_evasion = (items.Evasion - items.AddedEvasion) / evasion_multi
    items.Evasion = (base_evasion * (items.IncreasedEvasion + 120) / 100 + items.AddedEvasion + 0.5).astype(np.int16)
    del items['IncreasedEvasion']
    del items['AddedEvasion']

    shield_multi = (items.IncreasedEnergyShield + items.Quality + 100) / 100
    base_shield = (items.EnergyShield - items.AddedEnergyShield) / shield_multi
    items.EnergyShield = (base_shield * (items.IncreasedEnergyShield + 120) / 100 + items.AddedEnergyShield + 0.5).astype(np.int16)
    del items['IncreasedEnergyShield']
    del items['AddedEnergyShield']

    del items['Quality']
    return items


def normalize_weapon_quality(items):
    """
    Normalize quality for weapons (affecting phys damage).
    See normalize_armour_quality for details.
    :param items:
    :return:
    """
    print("normalizing quality...")
    damage_multi = (items.IncreasedPhysDamage + items.Quality + 100) / 100
    base_damage = (items.PhysDamage - items.AddedPhysDamageLocal) / damage_multi
    items.PhysDamage = (base_damage * (items.IncreasedPhysDamage + 120) / 100 + items.AddedPhysDamageLocal).astype(np.int16)
    del items['IncreasedPhysDamage']
    del items['AddedPhysDamageLocal']
    return items


def combine_resistances(items):
    """
    Replaces individual ele resists with TotalEleResist.
    """
    print("combining resistances...")
    items['TotalEleResist'] = items.FireResist + items.ColdResist + items.LightningResist
    items = remove_columns('FireResist', 'ColdResist', 'LightningResist')(items)
    return items


def apply_attribute_boni(items):
    """
    Combine the implicit bonus life from strength with any existing life bonus.
    """
    print("applying attribute boni...")
    items.Life += items.Strength / 2
    items.Mana += items.Intelligence / 2
    items.Accuracy += items.Dexterity * 2
    return items


def featurize_sockets(items):
    """
    Replaces the Sockets column with more ML-friendly columns like 5linked, 6linked and
    NumOffColorSockets.
    """
    print("featurizing sockets...")

    def count_links(sockets):
        return max(len(x) for x in sockets.split(' '))

    def count_off_color(sockets, str, dex, int):
        counts = {x: len(y) for x, y in groupby(sockets) if x != ' '}
        return counts['S'] if str > 0 else 0 + \
               counts['D'] if dex > 0 else 0 + \
               counts['I'] if int > 0 else 0 + \
               counts['G']

    link_count = items.Sockets.apply(count_links)
    items['5Linked'] = link_count >= 5
    items['6Linked'] = link_count >= 6
    items['NumOffColorSockets'] = \
        items.apply(lambda x: count_off_color(x.Sockets, x.ReqStr, x.ReqDex, x.ReqDex))

    del items['Sockets']
    return items


def remove_columns(*columns):
    print("removing redundant columns...")
    def _remove_columns(items, *columns):
        for column in columns:
            del items[column]
        return items
    return lambda x: _remove_columns(x, *columns)


DB_COLUMNS = {
    itemtype.BODY: itemdb.BODY_COLUMNS,
    itemtype.HELMET: itemdb.HELMET_COLUMNS,
    itemtype.GLOVES: itemdb.GLOVES_COLUMNS,
    itemtype.BOOTS: itemdb.BOOTS_COLUMNS,
    itemtype.BELT: itemdb.BELT_COLUMNS,
    itemtype.QUIVER: itemdb.QUIVER_COLUMNS,
    itemtype.RING: itemdb.RING_COLUMNS,
    itemtype.AMULET: itemdb.AMULET_COLUMNS,
    itemtype.WAND: itemdb.WAND_COLUMNS,
    itemtype.STAFF: itemdb.STAFF_COLUMNS,
    itemtype.DAGGER: itemdb.DAGGER_COLUMNS,
    itemtype.ONE_HAND_SWORD: itemdb.ONE_HAND_SWORD_COLUMNS,
    itemtype.TWO_HAND_SWORD: itemdb.TWO_HAND_SWORD_COLUMNS,
    itemtype.ONE_HAND_AXE: itemdb.ONE_HAND_AXE_COLUMNS,
    itemtype.TWO_HAND_AXE: itemdb.TWO_HAND_AXE_COLUMNS,
    itemtype.ONE_HAND_MACE: itemdb.ONE_HAND_MACE_COLUMNS,
    itemtype.TWO_HAND_MACE: itemdb.TWO_HAND_MACE_COLUMNS,
    itemtype.BOW: itemdb.BOW_COLUMNS,
    itemtype.CLAW: itemdb.CLAW_COLUMNS,
    itemtype.SCEPTRE: itemdb.SCEPTRE_COLUMNS,
}


def main(args):
    print("args: ", args)

    db = psycopg2.connect(args.db)
    exporter = DataExporter(db, league=args.league, flavour=args.flavour, league_end=args.league_end)

    args.itemtype = args.itemtype.upper()
    if args.itemtype == 'ALL':
        for itype in itemtype.ALL_TYPES:
            outfile = os.path.join(args.outdir, itemtype.get_name(itype) + '.csv')
            exporter.export(itype, outfile)
    else:
        itype = itemtype.from_name(args.itemtype)
        outfile = os.path.join(args.outdir, itemtype.get_name(itype) + '.csv')
        exporter.export(itype, outfile)


def parse_args():
    class CustomParser(argparse.Action):
        def __init__(self, option_strings, dest, parser=None, **kwargs):
            if parser is None:
                raise ValueError('CustomParser requires parser function')
            self.parser = parser
            super(CustomParser, self).__init__(option_strings, dest, **kwargs)

        def __call__(self, parser, namespace, values, option_string=None):
            if self.nargs is not None and self.nargs > 1:
                setattr(namespace, self.dest, [self.parser(x) for x in values])
            else:
                setattr(namespace, self.dest, self.parser(values))

    ap = argparse.ArgumentParser()
    ap.add_argument('itemtype', help='Item type to export, or ALL',
                    action=CustomParser, parser=str.upper)
    ap.add_argument('--db', required=True, help='db credentials')
    ap.add_argument('--league', default=league.STANDARD,
                    choices=[league.get_name(x) for x in league.ALL_SOFTCORE_LEAGUES],
                    action=CustomParser, parser=league.get_id)
    ap.add_argument('--flavour', choices=['Softcore', 'Hardcore', 'Both'], default='Both')
    ap.add_argument('--league-end', default=None, help='Date when the league ended',
                    action=CustomParser, parser=dateutil.parser.parse)
    ap.add_argument('--outdir', default=os.getcwd())
    return ap.parse_args()


if __name__ == '__main__':
    main(parse_args())
