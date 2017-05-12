UNKNOWN=0
RING=1
AMULET=2
BODY=3
HELMET=4
GLOVES=5
BOOTS=6
BELT=7
SHIELD=8
WAND=9
STAFF=10
DAGGER=11
ONE_HAND_SWORD=12
TWO_HAND_SWORD=13
ONE_HAND_AXE=14
TWO_HAND_AXE=15
ONE_HAND_MACE=16
TWO_HAND_MACE=17
BOW=18
QUIVER=19
CLAW=20
SCEPTRE=21

RING_TYPES = {
    'Breach Ring', 'Coral Ring', 'Iron Ring', 'Paua Ring', 'Unset Ring', 'Sapphire Ring', 'Topaz Ring', 'Ruby Ring',
    'Diamond Ring', 'Gold Ring', 'Moonstone Ring', 'Two-Stone Ring', 'Amethyst Ring', 'Prismatic Ring', 'Opal Ring',
    'Steel Ring',
}
AMULET_TYPES = {
    'Coral Amulet', 'Paua Amulet', 'Amber Amulet', 'Jade Amulet', 'Lapis Amulet', 'Gold Amulet', 'Agate Amulet',
    'Citrine Amulet', 'Turquoise Amulet', 'Onyx Amulet', 'Marble Amulet', 'Blue Pearl Amulet',
}
BODY_TYPES = {
    'Plate Vest', 'Chestplate', 'Copper Plate', 'War Plate', 'Full Plate', 'Arena Plate', 'Lordly Plate',
    'Bronze Plate', 'Battle Plate', 'Sun Plate', 'Colosseum Plate', 'Majestic Plate', 'Golden Plate',
    'Crusader Plate', 'Astral Plate', 'Gladiator Plate', 'Glorious Plate',
    'Shabby Jerkin', 'Strapped Leather', 'Buckskin Tunic', 'Wild Leather', 'Full Leather', 'Sun Leather',
    'Thief\'s Garb', 'Eelskin Tunic', 'Frontier Leather', 'Glorious Leather', 'Coronal Leather', 'Cutthroat\'s Garb',
    'Sharkskin Tunic', 'Destiny Leather', 'Exquisite Leather', 'Zodiac Leather', 'Assassin\'s Garb',
    'Simple Robe', 'Silken Vest', 'Scholar\'s Robe', 'Silken Garb', 'Mage\'s Vestment', 'Silk Robe',
    'Cabalist Regalia', 'Sage\'s Robe', 'Silken Wrap', 'Conjurer\'s Vestment', 'Spidersilk Robe',
    'Destroyer Regalia', 'Savant\'s Robe', 'Necromancer Silks', 'Occultist\'s Vestment', 'Widowsilk Robe',
    'Vaal Regalia',
    'Scale Vest', 'Light Brigandine', 'Scale Doublet', 'Infantry Brigandine', 'Full Scale Armour',
    'Soldier\'s Brigandine', 'Field Lamellar', 'Wyrmscale Doublet', 'Hussar Brigandine', 'Full Wyrmscale',
    'Commander\'s Brigandine', 'Battle Lamellar', 'Dragonscale Doublet', 'Desert Brigandine', 'Full Dragonscale',
    'General\'s Brigandine', 'Triumphant Lamellar',
    'Chainmail Vest', 'Chainmail Tunic', 'Ringmail Coat', 'Chainmail Doublet', 'Full Ringmail', 'Full Chainmail',
    'Holy Chainmail', 'Latticed Ringmail', 'Crusader Chainmail', 'Ornate Ringmail', 'Chain Hauberk',
    'Devout Chainmail', 'Loricated Ringmail', 'Conquest Chainmail', 'Elegant Ringmail', 'Saint\'s Hauberk',
    'Saintly Chainmail',
    'Padded Vest', 'Oiled Vest', 'Padded Jacket', 'Oiled Coat', 'Scarlet Raiment', 'Waxed Garb', 'Bone Armour',
    'Quilted Jacket', 'Sleek Coat', 'Crimson Raiment', 'Lacquered Garb', 'Crypt Armour', 'Sentinel Jacket',
    'Varnished Coat', 'Blood Raiment', 'Sadist Garb', 'Carnal Armour',
    'Sacrificial Garb'
}
HELMET_TYPES = {
    'Iron Hat', 'Cone Helmet', 'Barbute Helmet', 'Close Helmet', 'Gladiator Helmet', 'Reaver Helmet', 'Siege Helmet',
    'Samite Helmet', 'Ezomyte Burgonet', 'Royal Burgonet', 'Eternal Burgonet',
    'Leather Cap', 'Tricorne', 'Leather Hood', 'Wolf Pelt', 'Hunter Hood', 'Noble Tricorne', 'Ursine Pelt',
    'Silken Hood', 'Sinner Tricorne', 'Lion Pelt',
    'Vine Circlet', 'Iron Circlet', 'Torture Cage', 'Tribal Circlet', 'Bone Circlet', 'Lunaris Circlet',
    'Steel Circlet', 'Necromancer Circlet', 'Solaris Circlet', 'Mind Cage', 'Hubris Circlet',
    'Battered Helm', 'Sallet', 'Visored Sallet', 'Gilded Sallet', 'Secutor Helm', 'Fencer Helm', 'Lacquered Helmet',
    'Fluted Bascinet', 'Pig-Faced Bascinet', 'Nightmare Bascinet',
    'Rusted Coif', 'Soldier Helmet', 'Great Helmet', 'Crusader Helmet', 'Aventail Helmet', 'Zealot Helmet',
    'Great Crown', 'Magistrate Crown', 'Prophet Crown', 'Praetor Crown', 'Bone Helmet',
    'Scare Mask', 'Plague Mask', 'Iron Mask', 'Festival Mask', 'Golden Mask', 'Raven Mask', 'Callous Mask',
    'Regicide Mask', 'Harlequin Mask', 'Vaal Mask', 'Deicide Mask'
}
GLOVES_TYPES = {
    'Iron Gauntlets', 'Plated Gauntlets', 'Bronze Gauntlets', 'Steel Gauntlets', 'Antique Gauntlets',
    'Ancient Gauntlets', 'Goliath Gauntlets', 'Vaal Gauntlets', 'Titan Gauntlets', 'Spiked Gloves',
    'Rawhide Gloves', 'Goathide Gloves', 'Deerskin Gloves', 'Nubuck Gloves', 'Eelskin Gloves', 'Sharkskin Gloves',
    'Shagreen Gloves', 'Stealth Gloves', 'Slink Gloves', 'Gripped Gloves',
    'Wool Gloves', 'Velvet Gloves', 'Silk Gloves', 'Embroidered Gloves', 'Satin Gloves', 'Samite Gloves',
    'Conjurer Gloves', 'Arcanist Gloves', 'Sorcerer Gloves', 'Fingerless Silk Gloves',
    'Fishscale Gauntlets', 'Ironscale Gauntlets', 'Bronzescale Gauntlets', 'Steelscale Gauntlets',
    'Serpentscale Gauntlets', 'Wyrmscale Gauntlets', 'Hydrascale Gauntlets', 'Dragonscale Gauntlets',
    'Chain Gloves', 'Ringmail Gloves', 'Mesh Gloves', 'Riveted Gloves', 'Zealot Gloves', 'Soldier Gloves',
    'Legion Gloves', 'Crusader Gloves',
    'Wrapped Mitts', 'Strapped Mitts', 'Clasped Mitts', 'Trapper Mitts', 'Ambush Mitts', 'Carnal Mitts',
    'Assassin\'s Mitts', 'Murder Mitts'
}
BOOTS_TYPES = {
    'Iron Greaves', 'Steel Greaves', 'Plated Greaves', 'Reinforced Greaves', 'Antique Greaves', 'Ancient Greaves',
    'Goliath Greaves', 'Vaal Greaves', 'Titan Greaves',
    'Rawhide Boots', 'Goathide Boots', 'Deerskin Boots', 'Nubuck Boots', 'Eelskin Boots', 'Sharkskin Boots',
    'Shagreen Boots', 'Stealth Boots', 'Slink Boots',
    'Wool Shoes', 'Velvet Slippers', 'Silk Slippers', 'Scholar Boots', 'Satin Slippers', 'Samite Slippers',
    'Conjurer Boots', 'Arcanist Slippers', 'Sorcerer Boots',
    'Leatherscale Boots', 'Ironscale Boots', 'Bronzescale Boots', 'Steelscale Boots', 'Serpentscale Boots',
    'Wyrmscale Boots', 'Hydrascale Boots', 'Dragonscale Boots',
    'Chain Boots', 'Ringmail Boots', 'Mesh Boots', 'Riveted Boots', 'Zealot Boots', 'Soldier Boots', 'Legion Boots',
    'Crusader Boots',
    'Wrapped Boots', 'Strapped Boots', 'Clasped Boots', 'Shackled Boots', 'Trapper Boots', 'Ambush Boots',
    'Carnal Boots', 'Assassin\'s Boots', 'Murder Boots',
    'Two-Toned Boots',
}
BELT_TYPES = {
    'Chain Belt', 'Rustic Sash', 'Heavy Belt', 'Leather Belt', 'Cloth Belt', 'Studded Belt', 'Vanguard Belt',
    'Crystal Belt'
}
SHIELD_TYPES = {
    'Splintered Tower Shield', 'Corroded Tower Shield', 'Rawhide Tower Shield', 'Cedar Tower Shield',
    'Copper Tower Shield', 'Reinforced Tower Shield', 'Painted Tower Shield', 'Buckskin Tower Shield',
    'Mahogany Tower Shield', 'Bronze Tower Shield', 'Girded Tower Shield', 'Crested Tower Shield',
    'Shagreen Tower Shield', 'Ebony Tower Shield', 'Ezomyte Tower Shield', 'Colossal Tower Shield',
    'Pinnacle Tower Shield',
    'Goathide Buckler', 'Pine Buckler', 'Painted Buckler', 'Hammered Buckler', 'War Buckler', 'Gilded Buckler',
    'Oak Buckler', 'Enameled Buckler', 'Corrugated Buckler', 'Battle Buckler', 'Golden Buckler',
    'Ironwood Buckler', 'Lacquered Buckler', 'Vaal Buckler', 'Crusader Buckler', 'Imperial Buckler',
    'Twig Spirit Shield', 'Yew Spirit Shield', 'Bone Spirit Shield', 'Tarnished Spirit Shield',
    'Jingling Spirit Shield', 'Brass Spirit Shield', 'Walnut Spirit Shield', 'Ivory Spirit Shield',
    'Ancient Spirit Shield', 'Chiming Spirit Shield', 'Thorium Spirit Shield', 'Lacewood Spirit Shield',
    'Fossilised Spirit Shield', 'Vaal Spirit Shield', 'Harmonic Spirit Shield', 'Titanium Spirit Shield',
    'Rotted Round Shield', 'Fir Round Shield', 'Studded Round Shield', 'Scarlet Round Shield', 'Splendid Round Shield',
    'Maple Round Shield', 'Spiked Round Shield', 'Crimson Round Shield', 'Baroque Round Shield', 'Teak Round Shield',
    'Spiny Round Shield', 'Cardinal Round Shield', 'Elegant Round Shield',
    'Plank Kite Shield', 'Linden Kite Shield', 'Reinforced Kite Shield', 'Layered Kite Shield',
    'Ceremonial Kite Shield', 'Etched Kite Shield', 'Steel Kite Shield', 'Laminated Kite Shield',
    'Angelic Kite Shield', 'Branded Kite Shield', 'Champion Kite Shield', 'Mosaic Kite Shield',
    'Archon Kite Shield',
    'Spiked Bundle', 'Driftwood Spiked Shield', 'Alloyed Spiked Shield', 'Burnished Spiked Shield',
    'Ornate Spiked Shield', 'Redwood Spiked Shield', 'Compound Spiked Shield', 'Polished Spiked Shield',
    'Sovereign Spiked Shield', 'Alder Spiked Shield', 'Ezomyte Spiked Shield', 'Mirrored Spiked Shield',
    'Supreme Spiked Shield'
}
WAND_TYPES = {
    'Driftwood Wand', 'Goat\'s Horn', 'Carved Wand', 'Quartz Wand', 'Spiraled Wand', 'Sage Wand', 'Pagan Wand',
    'Faun\'s Horn', 'Engraved Wand', 'Crystal Wand', 'Serpent Wand', 'Omen Wand', 'Heathen Wand', 'Demon\'s Horn',
    'Imbued Wand', 'Opal Wand', 'Tornado Wand', 'Prophecy Wand', 'Profane Wand'
}
STAFF_TYPES = {
    'Gnarled Branch', 'Primitive Staff', 'Long Staff', 'Iron Staff', 'Coiled Staff', 'Royal Staff', 'Vile Staff',
    'Crescent Staff', 'Woodful Staff', 'Quarterstaff', 'Military Staff', 'Serpentine Staff', 'Highborn Staff',
    'Foul Staff', 'Moon Staff', 'Primordial Staff', 'Lathi', 'Ezomyte Staff', 'Maelström Staff', 'Imperial Staff',
    'Judgement Staff', 'Eclipse Staff'
}
DAGGER_TYPES = {
    'Glass Shank', 'Skinning Knife', 'Carving Knife', 'Stiletto', 'Boot Knife', 'Copper Kris', 'Skean',
    'Imp Dagger', 'Flaying Knife', 'Prong Dagger', 'Butcher Knife', 'Poignard', 'Boot Blade', 'Golden Kris',
    'Royal Skean', 'Fiend Dagger', 'Trisula', 'Gutting Knife', 'Slaughter Knife', 'Ambusher', 'Ezomyte Dagger',
    'Platinum Kris', 'Imperial Skean', 'Demon Dagger', 'Sai'
}
ONE_HAND_SWORD_TYPES = {
    'Rusted Sword', 'Copper Sword', 'Sabre', 'Broad Sword', 'War Sword', 'Ancient Sword', 'Elegant Sword',
    'Dusk Blade', 'Hook Sword', 'Variscite Blade', 'Cutlass', 'Baselard', 'Battle Sword', 'Elder Sword',
    'Graceful Sword', 'Twilight Blade', 'Grappler', 'Gemstone Sword', 'Corsair Sword', 'Gladius', 'Legion Sword',
    'Vaal Blade', 'Eternal Sword', 'Midnight Blade', 'Tiger Hook',
    'Rusted Spike', 'Whalebone Rapier', 'Battered Foil', 'Basket Rapier', 'Jagged Foil', 'Antique Rapier',
    'Elegant Foil', 'Thorn Rapier', 'Smallsword', 'Wyrmbone Rapier', 'Burnished Foil', 'Estoc', 'Serrated Foil',
    'Primeval Rapier', 'Fancy Foil', 'Apex Rapier', 'Courtesan Sword', 'Dragonbone Rapier', 'Tempered Foil',
    'Pecoraro', 'Spiraled Foil', 'Vaal Rapier', 'Jewelled Foil', 'Harpy Rapier', 'Dragoon Sword'
}
TWO_HAND_SWORD_TYPES = {
    'Corroded Blade', 'Longsword', 'Bastard Sword', 'Two-Handed Sword', 'Etched Greatsword', 'Ornate Sword',
    'Spectral Sword', 'Curved Blade', 'Butcher Sword', 'Footman Sword', 'Highland Blade', 'Engraved Greatsword',
    'Tiger Sword', 'Wraith Sword', 'Lithe Blade', 'Headman\'s Sword', 'Reaver Sword', 'Ezomyte Blade',
    'Vaal Greatsword', 'Lion Sword', 'Infernal Sword', 'Exquisite Blade',
}
ONE_HAND_AXE_TYPES = {
    'Rusted Hatchet', 'Jade Hatchet', 'Boarding Axe', 'Cleaver', 'Broad Axe', 'Arming Axe', 'Decorative Axe',
    'Spectral Axe', 'Etched Hatchet', 'Jasper Axe', 'Tomahawk', 'Wrist Chopper', 'War Axe', 'Chest Splitter',
    'Ceremonial Axe', 'Wraith Axe', 'Engraved Hatchet', 'Karui Axe', 'Siege Axe', 'Reaver Axe', 'Butcher Axe',
    'Vaal Hatchet', 'Royal Axe', 'Infernal Axe', 'Runic Hatchet',
}
TWO_HAND_AXE_TYPES = {
    'Stone Axe', 'Jade Chopper', 'Woodsplitter', 'Poleaxe', 'Double Axe', 'Gilded Axe', 'Shadow Axe',
    'Dagger Axe', 'Jasper Chopper', 'Timber Axe', 'Headsman Axe', 'Labrys', 'Noble Axe', 'Abyssal Axe',
    'Karui Chopper', 'Talon Axe', 'Sundering Axe', 'Ezomyte Axe', 'Vaal Axe', 'Despot Axe', 'Void Axe',
    'Fleshripper',
}
ONE_HAND_MACE_TYPES = {
    'Driftwood Club', 'Tribal Club', 'Spiked Club', 'Stone Hammer', 'War Hammer', 'Bladed Mace', 'Ceremonial Mace',
    'Dream Mace', 'Wyrm Mace', 'Petrified Club', 'Barbed Club', 'Rock Breaker', 'Battle Hammer', 'Flanged Mace',
    'Ornate Mace', 'Phantom Mace', 'Dragon Mace', 'Ancestral Club', 'Tenderizer', 'Gavel', 'Legion Hammer',
    'Pernarch', 'Auric Mace', 'Nightmare Mace', 'Behemoth Mace',
}
TWO_HAND_MACE_TYPES = {
    'Driftwood Maul', 'Tribal Maul', 'Mallet', 'Sledgehammer', 'Jagged Maul', 'Brass Maul', 'Fright Maul',
    'Morning Star', 'Totemic Maul', 'Great Mallet', 'Steelhead', 'Spiny Maul', 'Plated Maul', 'Dread Maul',
    'Solar Maul', 'Karui Maul', 'Colossus Mallet', 'Piledriver', 'Meatgrinder', 'Imperial Maul', 'Terror Maul',
    'Coronal Maul'
}
BOW_TYPES = {
    'Crude Bow', 'Short Bow', 'Long Bow', 'Composite Bow', 'Recurve Bow', 'Bone Bow', 'Royal Bow', 'Death Bow',
    'Grove Bow', 'Reflex Bow', 'Decurve Bow', 'Compound Bow', 'Sniper Bow', 'Ivory Bow', 'Highborn Bow',
    'Decimation Bow', 'Thicket Bow', 'Steelwood Bow', 'Citadel Bow', 'Ranger Bow', 'Assassin Bow', 'Spine Bow',
    'Imperial Bow', 'Harbinger Bow', 'Maraketh Bow',
}
QUIVER_TYPES = {
    'Serrated Arrow Quiver', 'Two-Point Arrow Quiver', 'Sharktooth Arrow Quiver', 'Blunt Arrow Quiver',
    'Fire Arrow Quiver', 'Broadhead Arrow Quiver', 'Penetrating Arrow Quiver', 'Spike-Point Arrow Quiver'
}
CLAW_TYPES = {
    'Nailed Fist', 'Sharktooth Claw', 'Awl', 'Cat\'s Paw', 'Blinder', 'Timeworn Claw', 'Sparkling Claw',
    'Fright Claw', 'Double Claw', 'Thresher Claw', 'Gouger', 'Tiger\'s Paw', 'Gut Ripper', 'Prehistoric Claw',
    'Noble Claw', 'Eagle Claw', 'Twin Claw', 'Great White Claw', 'Throat Stabber', 'Hellion\'s Paw', 'Eye Gouger',
    'Vaal Claw', 'Imperial Claw', 'Terror Claw', 'Gemini Claw'
}
SCEPTRE_TYPES = {
    'Driftwood Sceptre', 'Darkwood Sceptre', 'Bronze Sceptre', 'Quartz Sceptre', 'Iron Sceptre', 'Ochre Sceptre',
    'Ritual Sceptre', 'Shadow Sceptre', 'Grinning Fetish', 'Horned Sceptre', 'Sekhem', 'Crystal Sceptre',
    'Lead Sceptre', 'Blood Sceptre', 'Royal Sceptre', 'Abyssal Sceptre', 'Stag Sceptre', 'Karui Sceptre',
    'Tyrant\'s Sekhem', 'Opal Sceptre', 'Platinum Sceptre', 'Vaal Sceptre', 'Carnal Sceptre', 'Void Sceptre',
    'Sambar Sceptre'
}

ALL_TYPES = {
    RING: RING_TYPES,
    AMULET: AMULET_TYPES,
    BODY: BODY_TYPES,
    HELMET: HELMET_TYPES,
    GLOVES: GLOVES_TYPES,
    BOOTS: BOOTS_TYPES,
    BELT: BELT_TYPES,
    SHIELD: SHIELD_TYPES,
    WAND: WAND_TYPES,
    STAFF: STAFF_TYPES,
    DAGGER: DAGGER_TYPES,
    ONE_HAND_SWORD: ONE_HAND_SWORD_TYPES,
    TWO_HAND_SWORD: TWO_HAND_SWORD_TYPES,
    ONE_HAND_AXE: ONE_HAND_AXE_TYPES,
    TWO_HAND_AXE: TWO_HAND_AXE_TYPES,
    ONE_HAND_MACE: ONE_HAND_MACE_TYPES,
    TWO_HAND_MACE: TWO_HAND_MACE_TYPES,
    BOW: BOW_TYPES,
    QUIVER: QUIVER_TYPES,
    CLAW: CLAW_TYPES,
    SCEPTRE: SCEPTRE_TYPES
}

def get_item_type(item):
    item_basetype = item['typeLine']
    # Ignore 'Superior' prefix
    if item_basetype.startswith("Superior "):
        item_basetype = item_basetype[len("Superior "):]

    for type_id, basetypes in ALL_TYPES.items():
        if item_basetype in basetypes:
            return type_id
    # Ignore Talismans, Maps and Jewels
    if "Talisman" in item_basetype or " Map" in item_basetype or "Jewel" in item_basetype:
        return UNKNOWN
    # Ignore legacy quivers
    if item_basetype in {"Heavy Quiver", "Light Quiver", "Rugged Quiver", "Conductive Quiver", "Cured Quiver"}:
        return UNKNOWN
    if item_basetype == 'Fishing Rod':
        return UNKNOWN

    # Print warning for items we forgot
    print("WARNING: wtf is a ", item_basetype)
    return UNKNOWN


def get_name(itemtype):
    """Returns the name of the given itemtype."""
    if itemtype not in ALL_TYPES.keys():
        return 'INVALID'
    for k, v in globals().items():
        if v == itemtype:
            return k
    assert False, 'How can this be, itemtype was ' + itemtype
    return "ERROR WTF"


def from_name(name):
    """Returns itemtype id for the given name."""
    if name not in globals().keys:
        raise KeyError('Invalid itemtype: ' + name)
    itemtype = globals()[name]
    if type(itemtype) is not int:
        raise KeyError('Invalid itemtype: ' + name)
    return itemtype
