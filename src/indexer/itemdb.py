import hashlib
from collections import defaultdict
import json
import re

import psycopg2
from psycopg2.extras import Json
from blessings import Terminal

from indexer.itemstats import ItemBannedException, ItemParserException
from . import itemstats
from constants import league
from constants import rarity
from constants import itemtype
from constants import currency

class ItemDB(object):
    def __init__(self, db_access_string="dbname='poeria' user='benjamin'"):
        self.dbconn = psycopg2.connect(db_access_string)
        self.db = self.dbconn.cursor()
        self.table_columns = dict()

    def update_stash(self, stash):
        raw_items = stash['items']
        if len(raw_items) == 0:
            return [], 0

        stash_id = stash['id']
        stash_price = get_price(stash['stash'])

        items = list(filter(is_priced_rare_item, [preprocess_item(x, stash_id, default_price=stash_price) for x in raw_items]))

        previous_stash_content = self.get_stash_content(stash_id)
        num_sold = self.mark_deleted_items_as_sold(previous_stash_content, stash_id, items)
        self.reset_seen_date_for_modified_items(previous_stash_content, stash_id, items)
        return items, num_sold

    def add_items(self, items):
        self.add_to_stash(items)

        items_by_type = defaultdict(lambda: [])
        for item in items:
            items_by_type[item['type']].append(item)

        self.add_body_items(items_by_type[itemtype.BODY])
        self.add_helmet_items(items_by_type[itemtype.HELMET])
        self.add_gloves_items(items_by_type[itemtype.GLOVES])
        self.add_boots_items(items_by_type[itemtype.BOOTS])
        self.add_belt_items(items_by_type[itemtype.BELT])
        self.add_shield_items(items_by_type[itemtype.SHIELD])
        self.add_ring_items(items_by_type[itemtype.RING])
        self.add_amulet_items(items_by_type[itemtype.AMULET])
        self.add_wand_items(items_by_type[itemtype.WAND])
        self.add_staff_items(items_by_type[itemtype.STAFF])
        self.add_dagger_items(items_by_type[itemtype.DAGGER])
        self.add_one_hand_sword_items(items_by_type[itemtype.ONE_HAND_SWORD])
        self.add_two_hand_sword_items(items_by_type[itemtype.TWO_HAND_SWORD])
        self.add_one_hand_axe_items(items_by_type[itemtype.ONE_HAND_AXE])
        self.add_two_hand_axe_items(items_by_type[itemtype.TWO_HAND_AXE])
        self.add_one_hand_mace_items(items_by_type[itemtype.ONE_HAND_MACE])
        self.add_two_hand_mace_items(items_by_type[itemtype.TWO_HAND_MACE])
        self.add_bow_items(items_by_type[itemtype.BOW])
        self.add_sceptre_items(items_by_type[itemtype.SCEPTRE])

    def mark_deleted_items_as_sold(self, previous_stash_content, stash_id, items):
        """
        Find all items that were removed since the last stash update and store there sold date.
        :return: number of items sold.
        """
        item_ids = {x['id'] for x in items}
        deleted_items = [x[0] for x in previous_stash_content if x[0] not in item_ids]
        self.mark_as_sold(deleted_items)
        return len(deleted_items)

    def reset_seen_date_for_modified_items(self, previous_stash_content, stash_id, items):
        """
        When players use currency on items, their id remains the same.
        We need to reset the seen time when this happens because the player essentially puts
        a new item up for sale, and the sale time should start counting at that point.
        """
        item_hashes = {x['stats']['Hash'] for x in items}
        modified_items = [x[0] for x in previous_stash_content if x[1] not in item_hashes]
        self.reset_seen_date(modified_items)

    def get_stash_content(self, stash_id):
        """
        Returns stash content as a list of (item_id, hash) tuples.
        """
        self.db.execute("""
            SELECT ItemId, Hash
              FROM StashContents
             WHERE StashId=%s
               AND SoldTime::date < date '2000-01-01';
            """, (stash_id,))
        return self.db.fetchall()

    def mark_as_sold(self, item_ids):
        """
        Marks all item in the list as sold by storing the current date as the sold date.
        """
        if len(item_ids) == 0:
            return

        self.db.execute("""
            UPDATE StashContents
               SET SoldTime = current_timestamp
             WHERE {}
            """.format(
                " OR ".join("ItemId = '{}'".format(x) for x in item_ids)
            )
        )

    def reset_seen_date(self, item_ids):
        """
        Resets seen date for all items in the list to current time.
        """
        if len(item_ids) == 0:
            return

        self.db.execute("""
            UPDATE StashContents
               SET SeenTime = current_timestamp
             WHERE {}
        """.format(
            " OR ".join("ItemId = '{}'".format(x) for x in item_ids)
        ))

    def commit(self):
        self.dbconn.commit()

    def count(self, item_type=None):
        if item_type is None:
            self.db.execute('select count(*) from StashContents')
        return self.db.fetchone()[0]

    def add_to_stash(self, items):
        if len(items) == 0:
            return

        values = ["('{stash_id}', '{id}', {type}, '{price[0]}', '{price[1]}', current_timestamp, date '1999-01-01', current_timestamp, {league_id}, '{stats[Hash]}', {x}, {y}, {w}, {h})".format(**x) for x in items]
        query = """
            INSERT INTO StashContents (StashId, ItemId, ItemType, Price, Currency, AddedTime, SoldTime, SeenTime, League, Hash, X, Y, W, H)
            VALUES {}
            ON CONFLICT (ItemId) DO UPDATE SET
                (StashId, SeenTime, Price, Currency) =
                (excluded.StashId, current_timestamp, excluded.Price, excluded.Currency);""".format(
            ",".join(values)
        )
        self.db.execute(query)

    def store_item_values(self, table, items):
        """
        Stores items in an item-specific table.
        Each item in the list must have all columns from the column list as keys.
        Items that are already in the database, but with a different hash, will overwrite the ones in the db.
        """
        if len(items) == 0:
            return

        columns = self.get_table_columns(table)

        # Ensure all stats on the item have a corresponding column in the db
        for item in items:
            for stat in item['stats'].keys():
                assert stat in columns, '{} table has no column for {} (value: {})\n{}'.format(
                    table, stat, item['stats'][stat], item)

        # Remove all items that have changed
        for item in items:
            self.db.execute("DELETE FROM {} WHERE ItemId=%s AND Hash<>%s".format(table),
                            (item['id'], item['stats']['Hash']))

        values_string = ','.join('({})'.format(self.make_item_values_sql(columns, x['stats'])) for x in items)

        query = "INSERT INTO {table} ({columns}) VALUES {values} ON CONFLICT DO NOTHING".format(
            table=table,
            columns=','.join(columns),
            values=values_string
        )
        self.db.execute(query)

    def get_table_columns(self, tablename):
        columns = self.table_columns.get(tablename)
        if columns is not None:
            return columns

        self.db.execute("""
                        SELECT column_name FROM information_schema.columns
                         WHERE table_schema = 'public'
                           AND table_name = %s
                        """,
                        (tablename.lower(),))
        self.table_columns[tablename] = [x[0] for x in self.db.fetchone()]
        assert self.table_columns[tablename] is not None, "Failed to fetch columns for {}".format(tablename)
        return self.table_columns[tablename]

    def add_body_items(self, items):
        self.store_item_values('BodyItems', items)

    def add_helmet_items(self, items):
        self.store_item_values('HelmetItems', items)

    def add_gloves_items(self, items):
        self.store_item_values('GlovesItems', items)

    def add_boots_items(self, items):
        self.store_item_values('BootsItems', items)

    def add_belt_items(self, items):
        self.store_item_values('BeltItems', items)

    def add_quiver_items(self, items):
        self.store_item_values('QuiverItems', items)

    def add_shield_items(self, items):
        self.store_item_values('ShieldItems', items)

    def add_ring_items(self, items):
        self.store_item_values('RingItems', items)

    def add_amulet_items(self, items):
        self.store_item_values('AmuletItems', items)

    def add_wand_items(self, items):
        self.store_item_values('WandItems', items)

    def add_staff_items(self, items):
        self.store_item_values('StaffItems', items)

    def add_dagger_items(self, items):
        self.store_item_values('DaggerItems', items)

    def add_one_hand_sword_items(self, items):
        self.store_item_values('OneHandSwordItems', items)

    def add_two_hand_sword_items(self, items):
        self.store_item_values('TwoHandSwordItems', items)

    def add_one_hand_axe_items(self, items):
        self.store_item_values('OneHandAxeItems', items)

    def add_two_hand_axe_items(self, items):
        self.store_item_values('TwoHandAxeItems', items)

    def add_one_hand_mace_items(self, items):
        self.store_item_values('OneHandMaceItems', items)

    def add_two_hand_mace_items(self, items):
        self.store_item_values('TwoHandMaceItems', items)

    def add_bow_items(self, items):
        self.store_item_values('BowItems', items)

    def add_claw_items(self, items):
        self.store_item_values('ClawItems', items)

    def add_sceptre_items(self, items):
        self.store_item_values('SceptreItems', items)

    def make_item_values_sql(self, columns, item):
        """
        Returns a list of the item values, in the order specified by [columns].
        All values are properly encoded and escaped.
        The output of this can directly be used as part of a SQL query.
        Brackets are not included, so that you can append other elements if necessary.

        :param columns: List of columns / item keys
        :param item:    Dictionary of column name to value
        """
        placeholders = ','.join(['%s'] * len(columns))
        return self.db.mogrify(placeholders, tuple([item[x] for x in columns])).decode('ascii')

    def update_gg_tab(self, stash, predictions):
        """
        Tabs named 'GG' are processed by the indexer for prediction.
        Our AHK script will create an overlay for that stash tab.
        If a player has multiple GG tabs, the last updated one is active.
        This method stores item sizes & positions and updates the active stash id
        for a stash tab named GG.
        """
        if len(stash['items']) == 0:
            return

        league_id = league.get_id(stash['items'][0]['league'])
        print("Updating GG Tab of", stash['accountName'])

        self.db.execute("""
            INSERT INTO Players (AccountName, League, Predictions)
            VALUES (%s, %s, %s)
            ON CONFLICT (AccountName, League) DO UPDATE SET Predictions = EXCLUDED.Predictions
        """, (stash['accountName'], league_id, Json(predictions)))

    def get_stats(self):
        self.db.execute("""
            SELECT ItemType, COUNT(*) FROM StashContents
            GROUP BY ItemType
        """)
        total = self.db.fetchall()
        total = {itemtype.get_name(k): v for k, v in total}

        self.db.execute("""
            SELECT ItemType, COUNT(*) FROM StashContents
            WHERE SoldTime::date > date '2000-01-01'
            GROUP BY ItemType
        """)
        sold = self.db.fetchall()
        sold = {itemtype.get_name(k): v for k, v in sold}

        self.db.execute("""
            SELECT ItemType, COUNT(*) FROM StashContents
            WHERE SoldTime::date > date '2007-01-01'
              AND (Price > 1 AND (Currency = 4 OR Currency >= 11)
                   OR Currency = 6)
            GROUP BY ItemType
        """)
        valuable_sold = self.db.fetchall()
        valuable_sold = {itemtype.get_name(k): v for k, v in valuable_sold}

        return {
            'total': total,
            'sold': sold,
            'valuable_sold': valuable_sold
        }

def get_price(text):
    """
    Parses a stash tab name or item note and returns the price, or None if it contains no price.
    """
    if text is None:
        return None

    match = re.match('(~b/o|~price) (\d+\.?\d?) ([a-z]+)', text)
    if match is None:
        return None

    currency_id = currency.get_id(match.group(3))
    if currency_id == currency.UNKNOWN:
        return None

    value = float(match.group(2))
    if value > 10000:
        return None

    return value, currency_id


def preprocess_item(item, stash_id, default_price=None):
    try:
        if item['frameType'] != rarity.RARE:
            return None

        item['type'] = itemtype.get_item_type(item)
        if item['type'] == itemtype.UNKNOWN:
            return None

        item['league_id'] = league.get_id(item['league'])

        item['stash_id'] = stash_id
        item_price = get_price(item.get('note', None))
        item['price'] = item_price if item_price is not None else default_price

        item['stats'] = itemstats.parse_stats(item, item['type'])
        item['stats']['ItemId'] = item['id']
        item['stats']['Hash'] = hash_item(item['stats'])
        return item

    except ItemBannedException as ex:
        #print("Skipping {ex.item_type} with {ex.mod_text}".format(ex=ex))
        pass

    except ItemParserException as ex:
        print(Terminal().bold_yellow(ex.msg))

    except Exception as ex:
        print(Terminal().bold_red("Exception while preprocessing item: ", json.dumps(item)))
        raise ex


def is_priced_rare_item(item):
    if item is None:
        return False
    if item['price'] is None:
        return False
    if item['frameType'] != rarity.RARE:
        return False
    return True


def hash_item(item):
    h = hashlib.md5()
    h.update(json.dumps(item, sort_keys=True).encode('utf-8'))
    return h.hexdigest()

