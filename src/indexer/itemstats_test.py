import unittest
from indexer.itemstats import parse_ring

class RingTests(unittest.TestCase):
    def setUp(self):
        self.item = {
            'identified': True,
            'corrupted': False,
            'sockets': []
        }

    def test_DoubledInBreach(self):
        stats = parse_ring(self.item)
        self.assertFalse(stats['DoubledInBreach'])

        self.item['implicitMods'] = ['Properties are doubled while in a Breach']
        stats = parse_ring(self.item)
        self.assertTrue(stats['DoubledInBreach'])

    def test_Life(self):
        self.item['implicitMods'] = ['+10 to maximum Life']
        self.item['explicitMods'] = ['+13 to maximum Life']
        stats = parse_ring(self.item)
        self.assertEqual(23, stats['Life'])

    def test_AddedPhysAttackDamage(self):
        self.item['implicitMods'] = ['Adds 2 to 5 Physical Damage to Attacks']
        self.item['explicitMods'] = ['Adds 4 to 9 Physical Damage to Attacks']
        stats = parse_ring(self.item)
        self.assertEqual(2+5+4+9, stats['AddedPhysAttackDamage'])

    def test_Mana(self):
        self.item['implicitMods'] = ['+20 to maximum Mana']
        self.item['explicitMods'] = ['+22 to maximum Mana']
        stats = parse_ring(self.item)
        self.assertEqual(42, stats['Mana'])

    def test_FireResist(self):
        self.item['implicitMods'] = ['+5% to Fire Resistance']
        self.item['explicitMods'] = ['+7% to Fire Resistance']
        stats = parse_ring(self.item)
        self.assertEqual(12, stats['FireResist'])

    def test_FireAndColdResist(self):
        self.item['implicitMods'] = ['+6% to Fire and Cold Resistances']
        self.assertEqual(6, parse_ring(self.item)['FireResist'])
        self.assertEqual(6, parse_ring(self.item)['ColdResist'])

    def test_FireAndLightningResist(self):
        self.item['implicitMods'] = ['+7% to Fire and Lightning Resistances']
        self.assertEqual(7, parse_ring(self.item)['FireResist'])
        self.assertEqual(7, parse_ring(self.item)['LightningResist'])

    def test_ColdAndLightningResist(self):
        self.item['implicitMods'] = ['+7% to Cold and Lightning Resistances']
        self.assertEqual(7, parse_ring(self.item)['ColdResist'])
        self.assertEqual(7, parse_ring(self.item)['LightningResist'])

    def test_AllResist(self):
        self.item['implicitMods'] = ['+8% to all Elemental Resistances']
        self.assertEqual(8, parse_ring(self.item)['FireResist'])
        self.assertEqual(8, parse_ring(self.item)['ColdResist'])
        self.assertEqual(8, parse_ring(self.item)['LightningResist'])

    def test_ItemRarity(self):
        self.item['implicitMods'] = ['5% increased Rarity of Items found']
        self.item['explicitMods'] = ['7% increased Rarity of Items found']
        self.assertEqual(12, parse_ring(self.item)['ItemRarity'])

    def test_GrantedSkill(self):
        self.item['implicitMods'] = ['Grants level 14 Conductivity Skill']
        self.assertEqual(14, parse_ring(self.item)['GrantedSkillLevel'])
        self.assertNotEqual(0, parse_ring(self.item)['GrantedSkillId'])

    def test_LifeLeech(self):
        self.item['explicitMods'] = ['0.25% of Physical Attack Damage Leeched as Life']
        self.assertEqual(25, parse_ring(self.item)['LifeLeech'])

        self.item['explicitMods'] = ['1% of Physical Attack Damage Leeched as Life']
        self.assertEqual(100, parse_ring(self.item)['LifeLeech'])

    def test_ManaLeech(self):
        self.item['explicitMods'] = ['0.25% of Physical Attack Damage Leeched as Mana']
        self.assertEqual(25, parse_ring(self.item)['ManaLeech'])

        self.item['explicitMods'] = ['1% of Physical Attack Damage Leeched as Mana']
        self.assertEqual(100, parse_ring(self.item)['ManaLeech'])

    def test_LifeRegen(self):
        self.item['explicitMods'] = ['3.2 Life Regenerated per second']
        self.assertEqual(32, parse_ring(self.item)['LifeRegen'])

        self.item['explicitMods'] = ['3 Life Regenerated per second']
        self.assertEqual(30, parse_ring(self.item)['LifeRegen'])
