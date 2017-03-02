import os
import xgboost as xgb
import joblib
import psycopg2
import pandas as pd

import constants.itemtype as itemtype

class Predictor(object):
    def __init__(self):
        self.models = dict()
        self.models[itemtype.RING] = joblib.load(model_filename('rings'))
        self.dbconn = psycopg2.connect("dbname='poeria' user='benjamin'")

    def predict(self, stash_tab):
        stash_items = self.load_stash_contents(stash_tab)
        result = {'worthless': [], 'valuable': []}
        for itemtype, features, sizes in stash_items:
            predictions = self.models[itemtype].predict(features)
            result['worthless'].extend(x for x, y in zip(sizes, predictions) if y == 0)
            result['valuable'].extend(x for x, y in zip(sizes, predictions) if y == 1)
        return result

    def load_stash_contents(self, stash_tab):
        db = self.dbconn.cursor()
        return [
            self.load_rings(stash_tab, db)
        ]

    def load_rings(self, stash_tab, db):
        db.execute("""
        SELECT X, Y, W, H,   -- 4
               Corrupted, Sockets, DoubledInBreach,  -- 7
               Strength, Dexterity, Intelligence,    -- 10
               Life, Mana, Evasion, EnergyShield,    -- 14
               Accuracy, CritChance, AttackSpeed, CastSpeed,   -- 18
               FireResist, ColdResist, LightningResist, ChaosResist,  -- 22
               AddedPhysAttackDamage, AddedFireAttackDamage, AddedColdAttackDamage,  --25
               AddedLightningAttackDamage, AddedChaosAttackDamage,  -- 27                                                  -- 32
               IncreasedEleDamage, IncreasedWeaponEleDamage, IncreasedFireDamage, IncreasedColdDamage, IncreasedLightningDamage,
               ItemRarity, LifeLeech, ManaLeech, LifeGainOnHit, LifeGainOnKill, LifeRegen, ManaGainOnKill, ManaRegen,   -- 40
               AvoidFreeze, GrantedSkillId, ManaGainOnHit, DamageToMana, LightRadius  --45
         WHERE r.ItemId = s.ItemId
           AND s.StashId = %s
           AND s.ItemType = %s
           AND s.SoldTime :: date < date '2000-01-01'
        """, (stash_tab, itemtype.RING))
        features = []
        sizes = []
        for row in db:
            sizes.append({'x':row[0], 'y':row[1], 'w':row[2], 'h':row[3]})
            features.append({
                'Corrupted': row[3],
                'HasSocket': len(row[6]),
                'HasWhiteSocket': 1 if row[6] == 'W' else 0,
                'DoubledInBreach': row[7],
                'Strength': row[8],
                'Dexterity': row[9],
                'Intelligence': row[10],
                'Life': row[11],
                'Mana': row[12],
                'Evasion': row[13],
                'EnergyShield': row[14],
                'Accuracy': row[15],
                'CritChance': row[16],
                'AttackSpeed': row[17],
                'CastSpeed': row[18],
                'TotalEleResist': row[19] + row[20] + row[21],
                'ChaosResist': row[22],
                'AddedPhysAttackDamage': row[23],
                'AddedFireAttackDamage': row[24],
                'AddedColdAttackDamage': row[25],
                'AddedLightningAttackDamage': row[26],
                'AddedChaosAttackDamage': row[27],
                'IncreasedEleDamage': row[28],
                'IncreasedWeaponEleDamage': row[29],
                'IncreasedFireDamage': row[30],
                'IncreasedColdDamage': row[31],
                'IncreasedLightningDamage': row[32],
                'ItemRarity': row[33],
                'LifeLeech': row[34],
                'ManaLeech': row[35],
                'LifeGainOnHit': row[36],
                'LifeGainOnKill': row[37],
                'LifeRegen': row[38],
                'ManaGainOnKill': row[39],
                'ManaRegen': row[40],
                'ManaGainOnHit': row[41],
                'DamageToMana': row[42],
                'LightRadius': row[43],
            })
        return itemtype.RING, pd.DataFrame(features, dtype=int), sizes


def model_filename(itemtype):
    basedir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    return os.path.join(basedir, 'models', itemtype + '.model')
