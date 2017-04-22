
CREATE TABLE IF NOT EXISTS StashContents (
    StashId char(64) not null,
    ItemId char(64) primary key,
    Hash uuid not null,
    League smallint not null,
    Price smallint not null,
    Currency smallint not null,
    ItemType smallint not null,
    AddedTime timestamp with time zone not null,
    SoldTime timestamp with time zone not null,
    SeenTime timestamp with time zone not null,
    X smallint not null,
    Y smallint not null,
    W smallint not null,
    H smallint not null
);
CREATE INDEX StashContents_StashId ON StashContents (StashId);

CREATE TABLE IF NOT EXISTS Players (
    PlayerId bigint PRIMARY KEY,
    AccountName varchar(50) not null,
    League smallint not null,
    Predictions jsonb
);
CREATE UNIQUE INDEX IF NOT EXISTS players_accountname_league ON Players (AccountName, League);

CREATE TABLE IF NOT EXISTS BodyItems (
    ItemId char(64) primary key,
    Hash uuid not null,
    Sockets text not null,
    Corrupted bool not null,
    Quality smallint not null,

    ReqLevel smallint not null,
    ReqStr smallint not null,
    ReqDex smallint  not null,
    ReqInt smallint  not null,

    Armour smallint not null,
    Evasion smallint not null,
    EnergyShield smallint not null,

    AddedArmour smallint not null,
    IncreasedArmour smallint not null,
    AddedEvasion smallint not null,
    IncreasedEvasion smallint not null,
    AddedEnergyShield smallint not null,
    IncreasedEnergyShield smallint not null,

    AvoidIgnite smallint  not null,
    AvoidFreeze smallint  not null,
    AvoidShock smallint  not null,
    CannotBeKnockedBack bool  not null,
    ChaosResist smallint  not null,
    ColdResist smallint  not null,
    Dexterity smallint  not null,
    FireResist smallint  not null,
    GrantedSkillId smallint  not null,
    GrantedSkillLevel smallint  not null,
    Intelligence smallint  not null,
    Life smallint  not null,
    LifeRegen smallint not null,
    LightningResist smallint  not null,
    Mana smallint  not null,
    ManaMultiplier smallint not null,
    MaxResists smallint  not null,
    MoveSpeed smallint not null,
    PhysReflect smallint  not null,
    SocketedGemLevel smallint  not null,
    SocketedVaalGemLevel smallint  not null,
    SpellDamage smallint  not null,
    Strength smallint  not null,
    StunRecovery smallint not null
);

CREATE TABLE IF NOT EXISTS HelmetItems (
    ItemId char(64) primary key,
    Hash uuid not null,
    Sockets text not null,
    Corrupted bool not null,
    Quality smallint not null,

    ReqLevel smallint not null,
    ReqStr smallint not null,
    ReqDex smallint  not null,
    ReqInt smallint  not null,

    Armour smallint not null,
    Evasion smallint not null,
    EnergyShield smallint not null,

    AddedArmour smallint not null,
    IncreasedArmour smallint not null,
    AddedEvasion smallint not null,
    IncreasedEvasion smallint not null,
    AddedEnergyShield smallint not null,
    IncreasedEnergyShield smallint not null,

    Accuracy smallint  not null,
    ChaosResist smallint  not null,
    ColdResist smallint  not null,
    Dexterity smallint  not null,
    EnemiesCannotLeech bool  not null,
    FireResist smallint  not null,
    GrantedSkillId smallint not null,
    GrantedSkillLevel smallint not null,
    IncreasedAccuracy smallint not null,
    Intelligence smallint  not null,
    ItemRarity smallint not null,
    Life smallint  not null,
    LifeRegen smallint  not null,
    LightningResist smallint  not null,
    LightRadius smallint  not null,
    Mana smallint  not null,
    ManaShield smallint  not null,
    MinionDamage smallint  not null,
    PhysReflect smallint not null,
    SocketedMinionGemLevel smallint not null,
    SocketedVaalGemLevel smallint  not null,
    Strength smallint  not null,
    StunRecovery smallint  not null,
    SupportedByCastOnCrit smallint  not null,
    SupportedByCastOnStun smallint not null

);

CREATE TABLE IF NOT EXISTS BootsItems (
    ItemId char(64) primary key,
    Hash uuid not null,
    Sockets text not null,
    Corrupted bool not null,
    Quality smallint not null,

    ReqLevel smallint not null,
    ReqStr smallint not null,
    ReqDex smallint  not null,
    ReqInt smallint  not null,

    Armour smallint not null,
    Evasion smallint not null,
    EnergyShield smallint not null,

    AddedArmour smallint not null,
    IncreasedArmour smallint not null,
    AddedEvasion smallint not null,
    IncreasedEvasion smallint not null,
    AddedEnergyShield smallint not null,
    IncreasedEnergyShield smallint not null,

    CannotBeKnockedBack bool not null,
    ChaosResist smallint  not null,
    ColdResist smallint  not null,
    Dexterity smallint  not null,
    DodgeAttacks smallint  not null,
    FireResist smallint  not null,
    GrantedSkillId smallint  not null,
    GrantedSkillLevel smallint  not null,
    Intelligence smallint  not null,
    ItemRarity smallint  not null,
    Life smallint  not null,
    LifeRegen smallint  not null,
    LightningResist smallint  not null,
    Mana smallint  not null,
    MaxFrenzyCharges smallint not null,
    MoveSpeed smallint  not null,
    SocketedGemLevel smallint  not null,
    SocketedVaalGemLevel smallint  not null,
    Strength smallint  not null,
    StunRecovery smallint not null

);

CREATE TABLE IF NOT EXISTS GlovesItems (
    ItemId char(64) primary key,
    Hash uuid not null,
    Sockets text not null,
    Corrupted bool not null,
    Quality smallint not null,

    ReqLevel smallint not null,
    ReqStr smallint not null,
    ReqDex smallint  not null,
    ReqInt smallint  not null,

    Armour smallint not null,
    Evasion smallint not null,
    EnergyShield smallint not null,

    AddedArmour smallint not null,
    IncreasedArmour smallint not null,
    AddedEvasion smallint not null,
    IncreasedEvasion smallint not null,
    AddedEnergyShield smallint not null,
    IncreasedEnergyShield smallint not null,

    Accuracy smallint  not null,
    AddedColdAttackDamage smallint  not null,
    AddedFireAttackDamage smallint  not null,
    AddedLightningAttackDamage smallint  not null,
    AddedPhysAttackDamage smallint  not null,
    AttackSpeed smallint  not null,
    CastSpeed smallint  not null,
    ChaosResist smallint  not null,
    ColdResist smallint  not null,
    Dexterity smallint  not null,
    EleWeaknessOnHit smallint  not null,
    FireResist smallint  not null,
    GrantedSkillId smallint  not null,
    GrantedSkillLevel smallint  not null,
    Intelligence smallint  not null,
    ItemRarity smallint  not null,
    Life smallint  not null,
    LifeGainOnHit smallint  not null,
    LifeGainOnKill smallint  not null,
    LifeLeech smallint  not null,
    LifeRegen smallint  not null,
    LightningResist smallint  not null,
    Mana smallint  not null,
    ManaGainOnKill smallint  not null,
    ManaLeech smallint not null,
    MeleeDamage smallint not null,
    ProjectileAttackDamage smallint not null,
    SocketedGemLevel smallint  not null,
    SocketedVaalGemLevel smallint  not null,
    SpellDamage smallint not null,
    Strength smallint  not null,
    StunRecovery smallint  not null,
    SupportedByCastOnCrit smallint  not null,
    SupportedByCastOnStun smallint not null,
    TempChainsOnHit smallint  not null,
    VulnerabilityOnHit smallint not null
);

CREATE TABLE IF NOT EXISTS ShieldItems (
    ItemId char(64) primary key,
    Hash uuid not null,
    Sockets text not null,
    Corrupted bool not null,
    Quality smallint not null,

    Armour smallint not null,
    Evasion smallint not null,
    EnergyShield smallint not null,

    AddedArmour smallint not null,
    IncreasedArmour smallint not null,
    AddedEvasion smallint not null,
    IncreasedEvasion smallint not null,
    AddedEnergyShield smallint not null,
    IncreasedEnergyShield smallint not null,

    ReqLevel smallint not null,
    ReqStr smallint not null,
    ReqDex smallint  not null,
    ReqInt smallint  not null,
    Life smallint  not null,
    Mana smallint  not null,
    Strength smallint  not null,
    Dexterity smallint  not null,
    Intelligence smallint  not null,
    FireResist smallint  not null,
    ColdResist smallint  not null,
    LightningResist smallint  not null,
    ChaosResist smallint  not null,
    BlockChance smallint  not null,
    PhysReflect smallint  not null,
    StunRecovery smallint  not null,
    SocketedMeleeGemLevel smallint  not null,
    SocketedChaosGemLevel smallint  not null,
    SocketedFireGemLevel smallint  not null,
    SocketedColdGemLevel smallint  not null,
    SocketedLightningGemLevel smallint  not null,
    LifeRegen smallint  not null,
    ManaRegen smallint  not null,
    IncreasedSpellDamage smallint  not null,
    SpellCritChance smallint  not null,
    AvoidIgnite smallint  not null,
    GrantedSkillId smallint  not null,
    GrantedSkillLevel smallint  not null,
    SocketedGemLevel smallint  not null,
    SocketedVaalGemLevel smallint  not null,
    CastSpeed smallint  not null,
    ManaShield smallint  not null,
    PhysDamageReduction smallint  not null,
    SpellBlock smallint not null
);

CREATE TABLE IF NOT EXISTS RingItems (
    ItemId char(64) primary key,
    Hash uuid not null,
    Corrupted bool not null,
    Sockets character not null,
    ReqLevel smallint NOT NULL DEFAULT 0,

    Accuracy smallint  NOT NULL DEFAULT 0,
    AddedChaosAttackDamage smallint  NOT NULL DEFAULT 0,
    AddedColdAttackDamage smallint  NOT NULL DEFAULT 0,
    AddedEnergyShield smallint  NOT NULL DEFAULT 0,
    AddedEvasion smallint NOT NULL DEFAULT 0,
    AddedFireAttackDamage smallint NOT NULL  DEFAULT 0,
    AddedLightningAttackDamage smallint  NOT NULL DEFAULT 0,
    AddedPhysAttackDamage smallint  NOT NULL DEFAULT 0,
    AttackSpeed smallint  NOT NULL DEFAULT 0,
    AvoidFreeze smallint  NOT NULL DEFAULT 0,
    CastSpeed smallint  NOT NULL DEFAULT 0,
    ChaosResist smallint NOT NULL  DEFAULT 0,
    ColdResist smallint NOT NULL  DEFAULT 0,
    DamageToMana smallint  NOT NULL DEFAULT 0,
    Dexterity smallint  NOT NULL DEFAULT 0,
    DoubledInBreach bool NOT NULL DEFAULT false,
    FireResist smallint  NOT NULL DEFAULT 0,
    GlobalCritChance smallint  NOT NULL DEFAULT 0,
    GrantedSkillId smallint  NOT NULL DEFAULT 0,
    GrantedSkillLevel smallint  NOT NULL DEFAULT 0,
    IncreasedAccuracy smallint NOT NULL DEFAULT 0,
    IncreasedColdDamage smallint  NOT NULL DEFAULT 0,
    IncreasedEleDamage smallint  NOT NULL DEFAULT 0,
    IncreasedFireDamage smallint NOT NULL  DEFAULT 0,
    IncreasedLightningDamage smallint  NOT NULL DEFAULT 0,
    IncreasedWeaponEleDamage smallint  NOT NULL DEFAULT 0,
    Intelligence smallint  NOT NULL DEFAULT 0,
    ItemRarity smallint  NOT NULL DEFAULT 0,
    Life smallint NOT NULL  DEFAULT 0,
    LifeGainOnHit smallint NOT NULL  DEFAULT 0,
    LifeGainOnKill smallint  NOT NULL DEFAULT 0,
    LifeLeech smallint NOT NULL  DEFAULT 0,
    LifeRegen smallint  NOT NULL DEFAULT 0,
    LightningResist smallint  NOT NULL DEFAULT 0,
    LightRadius smallint  NOT NULL DEFAULT 0,
    Mana smallint NOT NULL  DEFAULT 0,
    ManaGainOnHit smallint NOT NULL DEFAULT 0,
    ManaGainOnKill smallint  NOT NULL DEFAULT 0,
    ManaLeech smallint  NOT NULL DEFAULT 0,
    ManaRegen smallint  NOT NULL DEFAULT 0,
    SocketedGemLevel smallint NOT NULL DEFAULT 0,
    Strength smallint  NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS AmuletItems (
    ItemId char(64) PRIMARY KEY,
    Hash uuid not null,
    Corrupted bool not null,
    ReqLevel smallint  not null,

    Accuracy smallint  not null,
    AdditionalCurses smallint  not null,
    AddedColdAttackDamage smallint  not null,
    AddedEnergyShield smallint  not null,
    AddedFireAttackDamage smallint  not null,
    AddedLightningAttackDamage smallint  not null,
    AddedPhysAttackDamage smallint  not null,
    AttackSpeed smallint  not null,
    AvoidFreeze smallint  not null,
    AvoidIgnite smallint  not null,
    BlockChance smallint  not null,
    CastSpeed smallint  not null,
    ChaosResist smallint  not null,
    ColdResist smallint  not null,
    DamageToMana smallint  not null,
    Dexterity smallint  not null,
    FireResist smallint  not null,
    GlobalCritChance smallint  not null,
    GlobalCritMulti smallint  not null,
    GrantedSkillId smallint  not null,
    GrantedSkillLevel smallint not null,
    IncreasedArmour smallint  not null,
    IncreasedColdDamage smallint  not null,
    IncreasedEnergyShield smallint not null,
    IncreasedEvasion smallint  not null,
    IncreasedFireDamage smallint  not null,
    IncreasedLifeRegen smallint  not null,
    IncreasedLightningDamage smallint  not null,
    IncreasedSpellDamage smallint  not null,
    IncreasedWeaponEleDamage smallint  not null,
    Intelligence smallint  not null,
    ItemRarity smallint  not null,
    Life smallint  not null,
    LifeGainOnHit smallint  not null,
    LifeGainOnKill smallint  not null,
    LifeLeech smallint  not null,
    LifeLeechCold smallint  not null,
    LifeLeechFire smallint  not null,
    LifeLeechLightning smallint  not null,
    LifeRegen smallint  not null,
    LightningResist smallint  not null,
    Mana smallint  not null,
    ManaGainOnKill smallint  not null,
    ManaLeech smallint  not null,
    ManaRegen smallint  not null,
    MaxFrenzyCharges smallint  not null,
    MaxResists smallint not null,
    MinionDamage smallint  not null,
    MoveSpeed smallint  not null,
    PhysDamageReduction smallint  not null,
    SpellBlock smallint not null,
    SpellDamage smallint  not null,
    Strength smallint not null

);

CREATE TABLE IF NOT EXISTS BeltItems (
    ItemId char(64) primary key,
    Hash uuid not null,
    Corrupted bool not null,
    ReqLevel smallint  not null,

    AddedArmour smallint not null,
    AddedEnergyShield smallint  not null,
    AddedEvasion smallint not null,
    AdditionalTraps smallint not null,
    AvoidShock smallint not null,
    ChaosResist smallint  not null,
    ColdResist smallint  not null,
    FireResist smallint not null,
    FlaskChargeGain smallint not null,
    FlaskChargeUse smallint not null,
    FlaskDuration smallint not null,
    FlaskLife smallint not null,
    FlaskMana smallint not null,
    GrantedSkillId smallint not null,
    GrantedSkillLevel smallint not null,
    IncreasedAoE smallint not null,
    IncreasedPhysDamage smallint not null,
    IncreasedWeaponEleDamage smallint not null,
    Life smallint  not null,
    LifeRegen smallint not null,
    LightningResist smallint not null,
    MaxEnduranceCharges smallint not null,
    PhysReflect smallint not null,
    SkillDuration smallint not null,
    Strength smallint not null,
    StunDuration smallint not null,
    StunRecovery smallint not null,
    StunThreshold smallint not null
);

CREATE TABLE IF NOT EXISTS QuiverItems (
    ItemId char(64) primary key,
    Hash uuid not null,
    Corrupted bool not null,
    ReqLevel smallint not null,

    Accuracy smallint not null,
    AddedArrow smallint not null,
    AddedColdAttackDamage smallint not null,
    AddedFireAttackDamage smallint not null,
    AddedFireBowDamage smallint not null,
    AddedLightningAttackDamage smallint not null,
    AddedPhysAttackDamage smallint not null,
    AddedPhysBowDamage smallint not null,
    AttackSpeed smallint not null,
    ChaosResist smallint not null,
    ColdResist smallint not null,
    Dexterity smallint not null,
    FireResist smallint not null,
    GlobalCritChance smallint not null,
    GlobalCritMulti smallint not null,
    GrantedSkillId smallint not null,
    GrantedSkillLevel smallint not null,
    IncreasedAccuracy smallint not null,
    IncreasedWeaponEleDamage smallint not null,
    Life smallint not null,
    LifeGainOnKill smallint not null,
    LifeLeech smallint not null,
    LifeLeechCold smallint not null,
    LifeLeechFire smallint not null,
    LifeLeechLightning smallint not null,
    LightningResist smallint not null,
    ManaGainOnKill smallint not null,
    ManaLeech smallint not null,
    PhysToCold smallint not null,
    PhysToFire smallint not null,
    PhysToLightning smallint not null,
    Pierce smallint not null,
    ProjectileSpeed smallint not null,
    StunDuration smallint not null
);

CREATE TABLE IF NOT EXISTS WandItems (
    ItemId char(64) primary key,
    Hash uuid not null,
    Corrupted bool not null,
    Sockets text not null,
    Quality smallint not null,

    PhysDamage smallint not null,
    EleDamage smallint not null,
    ChaosDamage smallint not null,
    AttacksPerSecond smallint not null,
    CritChance smallint not null,

    ReqLevel smallint not null,
    ReqStr smallint not null,
    ReqDex smallint not null,
    ReqInt smallint not null,

    Accuracy smallint not null,
    AddedPhysDamageLocal smallint not null,
    AddedSpellColdDamage smallint not null,
    AddedSpellFireDamage smallint not null,
    AddedSpellLightningDamage smallint not null,
    CastSpeed smallint not null,
    ChanceToFlee smallint not null,
    ChaosResist smallint not null,
    ColdResist smallint not null,
    CullingStrike bool not null,
    FireResist smallint not null,
    GlobalCritMulti smallint not null,
    GrantedSkillId smallint not null,
    GrantedSkillLevel smallint not null,
    IncreasedAccuracy smallint not null,
    IncreasedColdDamage smallint not null,
    IncreasedFireDamage smallint not null,
    IncreasedLightningDamage smallint not null,
    IncreasedPhysDamage smallint not null,
    IncreasedWeaponEleDamage smallint not null,
    Intelligence smallint not null,
    LifeGainOnHit smallint not null,
    LifeGainOnKill smallint not null,
    LifeLeech smallint not null,
    LifeLeechCold smallint not null,
    LifeLeechFire smallint not null,
    LifeLeechLightning smallint not null,
    LightningResist smallint not null,
    LightRadius smallint not null,
    Mana smallint not null,
    ManaGainOnKill smallint not null,
    ManaLeech smallint not null,
    ManaRegen smallint not null,
    Pierce smallint not null,
    ProjectileSpeed smallint not null,
    SocketedGemLevel smallint not null,
    SocketedChaosGemLevel smallint not null,
    SocketedColdGemLevel smallint not null,
    SocketedFireGemLevel smallint not null,
    SocketedLightningGemLevel smallint not null,
    SpellCrit smallint not null,
    SpellDamage smallint not null,
    StunDuration smallint not null,
    SupportedByEleProlif smallint not null
);

CREATE TABLE IF NOT EXISTS StaffItems (
    ItemId char(64) primary key,
    Hash uuid not null,
    Corrupted bool not null,
    Sockets text not null,
    Quality smallint not null,

    PhysDamage smallint not null,
    EleDamage smallint not null,
    ChaosDamage smallint not null,
    AttacksPerSecond smallint not null,
    CritChance smallint not null,

    ReqLevel smallint not null,
    ReqStr smallint not null,
    ReqDex smallint not null,
    ReqInt smallint not null,

    Accuracy smallint not null,
    AddedPhysDamageLocal smallint not null,
    AddedSpellColdDamage smallint not null,
    AddedSpellFireDamage smallint not null,
    AddedSpellLightningDamage smallint not null,
    AttackSpeed smallint not null,
    BlockChance smallint not null,
    CastSpeed smallint not null,
    ChanceToFlee smallint not null,
    ChaosResist smallint not null,
    ColdResist smallint not null,
    FireResist smallint not null,
    GlobalCritChance smallint not null,
    GlobalCritMulti smallint not null,
    IncreasedAccuracy smallint not null,
    IncreasedColdDamage smallint not null,
    IncreasedFireDamage smallint not null,
    IncreasedLightningDamage smallint not null,
    IncreasedPhysDamage smallint not null,
    IncreasedWeaponEleDamage smallint not null,
    Intelligence smallint not null,
    LifeGainOnHit smallint not null,
    LifeGainOnKill smallint not null,
    LifeLeech smallint not null,
    LifeLeechCold smallint not null,
    LifeLeechFire smallint not null,
    LifeLeechLightning smallint not null,
    LightRadius smallint not null,
    LightningResist smallint not null,
    Mana smallint not null,
    ManaGainOnKill smallint not null,
    ManaLeech smallint not null,
    ManaRegen smallint not null,
    MaxPowerCharges smallint not null,
    SocketedChaosGemLevel smallint not null,
    SocketedColdGemLevel smallint not null,
    SocketedFireGemLevel smallint not null,
    SocketedLightningGemLevel smallint not null,
    SocketedGemLevel smallint not null,
    SocketedMana smallint not null,
    SocketedMeleeGemLevel smallint not null,
    SpellBlock smallint not null,
    SpellCrit smallint not null,
    SpellDamage smallint not null,
    Strength smallint not null,
    StunDuration smallint not null,
    StunThreshold smallint not null,
    SupportedByIncreasedAoE smallint not null,
    WeaponRange smallint not null
);

CREATE TABLE IF NOT EXISTS DaggerItems (
    ItemId char(64) primary key,
    Hash uuid not null,
    Corrupted bool not null,
    Sockets text not null,
    Quality smallint not null,

    PhysDamage smallint not null,
    EleDamage smallint not null,
    ChaosDamage smallint not null,
    AttacksPerSecond smallint not null,
    CritChance smallint not null,

    ReqLevel smallint not null,
    ReqStr smallint not null,
    ReqDex smallint not null,
    ReqInt smallint not null,

    Accuracy smallint not null,
    AddedPhysDamageLocal smallint not null,
    AddedSpellColdDamage smallint not null,
    AddedSpellFireDamage smallint not null,
    AddedSpellLightningDamage smallint not null,
    BlockChance smallint not null,
    BlockChanceWhileDualWielding smallint not null,
    ChanceToFlee smallint not null,
    ChaosResist smallint not null,
    ColdResist smallint not null,
    CullingStrike bool not null,
    Dexterity smallint not null,
    FireResist smallint not null,
    GlobalCritChance smallint not null,
    GlobalCritMulti smallint not null,
    LifeLeechCold smallint not null,
    LifeLeechFire smallint not null,
    LifeLeechLightning smallint not null,
    Mana smallint not null,
    ManaGainOnKill smallint not null,
    ManaLeech smallint not null,
    ManaRegen smallint not null,
    IncreasedAccuracy smallint not null,
    IncreasedPhysDamage smallint not null,
    IncreasedWeaponEleDamage smallint not null,
    Intelligence smallint not null,
    LifeGainOnHit smallint not null,
    LifeGainOnKill smallint not null,
    LifeLeech smallint not null,
    LightRadius smallint not null,
    LightningResist smallint not null,
    SocketedChaosGemLevel smallint not null,
    SocketedColdGemLevel smallint not null,
    SocketedFireGemLevel smallint not null,
    SocketedLightningGemLevel smallint not null,
    SocketedMeleeGemLevel smallint not null,
    SocketedGemLevel smallint not null,
    SpellDamage smallint not null,
    SpellCrit smallint not null,
    StunDuration smallint not null,
    SupportedByIncreasedCritDamage smallint not null,
    SupportedByMeleeSplash smallint not null,
    WeaponRange smallint not null
);

CREATE TABLE IF NOT EXISTS OneHandSwordItems (
    ItemId char(64) primary key,
    Hash uuid not null,
    Corrupted bool not null,
    Sockets text not null,
    Quality smallint not null,

    PhysDamage smallint not null,
    EleDamage smallint not null,
    ChaosDamage smallint not null,
    AttacksPerSecond smallint not null,
    CritChance smallint not null,

    ReqLevel smallint not null,
    ReqStr smallint not null,
    ReqDex smallint not null,
    ReqInt smallint not null,

    Accuracy smallint not null,
    AddedPhysDamageLocal smallint not null,
    Bleed smallint not null,
    BlockChanceWhileDualWielding smallint not null,
    ChanceToFlee smallint not null,
    ChaosResist smallint not null,
    ColdResist smallint not null,
    CullingStrike bool not null,
    Dexterity smallint not null,
    DodgeAttacks  smallint not null,
    FireResist smallint not null,
    GlobalCritMulti smallint not null,
    IncreasedAccuracy smallint not null,
    IncreasedPhysDamage smallint not null,
    IncreasedWeaponEleDamage smallint not null,
    LifeGainOnHit smallint not null,
    LifeGainOnKill smallint not null,
    LifeLeech smallint not null,
    LifeLeechCold smallint not null,
    LifeLeechFire smallint not null,
    LifeLeechLightning smallint not null,
    LightRadius smallint not null,
    LightningResist smallint not null,
    ManaGainOnKill smallint not null,
    ManaLeech smallint not null,
    Strength smallint not null,
    SocketedGemLevel smallint not null,
    SocketedMeleeGemLevel smallint not null,
    StunDuration smallint not null,
    StunThreshold smallint not null,
    SupportedByMeleeSplash smallint not null,
    SupportedByMultistrike smallint not null,
    WeaponRange smallint not null
);

CREATE TABLE IF NOT EXISTS TwoHandSwordItems (
    ItemId char(64) primary key,
    Hash uuid not null,
    Corrupted bool not null,
    Sockets text not null,
    Quality smallint not null,

    PhysDamage smallint not null,
    EleDamage smallint not null,
    ChaosDamage smallint not null,
    AttacksPerSecond smallint not null,
    CritChance smallint not null,

    ReqLevel smallint not null,
    ReqStr smallint not null,
    ReqDex smallint not null,
    ReqInt smallint not null,

    Accuracy smallint not null,
    AddedPhysDamageLocal smallint not null,
    ChanceToFlee smallint not null,
    ChaosResist smallint not null,
    ColdResist smallint not null,
    CullingStrike bool not null,
    Dexterity smallint not null,
    FireResist smallint not null,
    GlobalCritMulti smallint not null,
    IncreasedAccuracy smallint not null,
    IncreasedPhysDamage smallint not null,
    IncreasedWeaponEleDamage smallint not null,
    LifeGainOnHit smallint not null,
    LifeGainOnKill smallint not null,
    LifeLeech smallint not null,
    LifeLeechCold smallint not null,
    LifeLeechFire smallint not null,
    LifeLeechLightning smallint not null,
    LightRadius smallint not null,
    LightningResist smallint not null,
    ManaLeech smallint not null,
    ManaGainOnKill smallint not null,
    MaxPowerCharges smallint not null,
    SocketedGemLevel smallint not null,
    SocketedMeleeGemLevel smallint not null,
    Strength smallint not null,
    StunDuration smallint not null,
    StunThreshold smallint not null,
    SupportedByAdditionalAccuracy smallint not null,
    WeaponRange smallint not null
);

CREATE TABLE IF NOT EXISTS OneHandAxeItems (
    ItemId char(64) primary key,
    Hash uuid not null,
    Corrupted bool not null,
    Sockets text not null,
    Quality smallint not null,

    PhysDamage smallint not null,
    EleDamage smallint not null,
    ChaosDamage smallint not null,
    AttacksPerSecond smallint not null,
    CritChance smallint not null,

    ReqLevel smallint not null,
    ReqStr smallint not null,
    ReqDex smallint not null,
    ReqInt smallint not null,

    Accuracy smallint not null,
    AddedPhysDamageLocal smallint not null,
    ChanceToFlee smallint not null,
    ChaosResist smallint not null,
    ColdResist smallint not null,
    CullingStrike bool not null,
    Dexterity smallint not null,
    FireResist smallint not null,
    GlobalCritMulti smallint not null,
    GrantedSkillId smallint not null,
    GrantedSkillLevel smallint not null,
    IncreasedAccuracy smallint not null,
    IncreasedPhysDamage smallint not null,
    IncreasedWeaponEleDamage smallint not null,
    LifeGainOnHit smallint not null,
    LifeGainOnKill smallint not null,
    LifeLeech smallint not null,
    LifeLeechCold smallint not null,
    LifeLeechFire smallint not null,
    LifeLeechLightning smallint not null,
    LightRadius smallint not null,
    LightningResist smallint not null,
    ManaGainOnKill smallint not null,
    ManaLeech smallint not null,
    SocketedGemLevel smallint not null,
    SocketedMeleeGemLevel smallint not null,
    Strength smallint not null,
    StunDuration smallint not null,
    StunThreshold smallint not null,
    SupportedByMeleeSplash smallint not null,
    WeaponRange smallint not null
);

CREATE TABLE IF NOT EXISTS TwoHandAxeItems (
    ItemId char(64) primary key,
    Hash uuid not null,
    Corrupted bool not null,
    Sockets text not null,
    Quality smallint not null,

    PhysDamage smallint not null,
    EleDamage smallint not null,
    ChaosDamage smallint not null,
    AttacksPerSecond smallint not null,
    CritChance smallint not null,

    ReqLevel smallint not null,
    ReqStr smallint not null,
    ReqDex smallint not null,
    ReqInt smallint not null,

    Accuracy smallint not null,
    AddedPhysDamageLocal smallint not null,
    ChanceToFlee smallint not null,
    ChaosResist smallint not null,
    ColdResist smallint not null,
    CullingStrike bool not null,
    Dexterity smallint not null,
    FireResist smallint not null,
    GlobalCritMulti smallint not null,
    GrantedSkillId smallint not null,
    GrantedSkillLevel smallint not null,
    IncreasedAccuracy smallint not null,
    IncreasedPhysDamage smallint not null,
    IncreasedWeaponEleDamage smallint not null,
    LifeGainOnHit smallint not null,
    LifeGainOnKill smallint not null,
    LifeLeech smallint not null,
    LifeLeechCold smallint not null,
    LifeLeechFire smallint not null,
    LifeLeechLightning smallint not null,
    LightningResist smallint not null,
    LightRadius smallint not null,
    ManaGainOnKill smallint not null,
    ManaLeech smallint not null,
    MaxPowerCharges smallint not null,
    SocketedGemLevel smallint not null,
    SocketedMeleeGemLevel smallint not null,
    Strength smallint not null,
    StunDuration smallint not null,
    StunThreshold smallint not null,
    WeaponRange smallint not null
);

CREATE TABLE IF NOT EXISTS OneHandMaceItems (
    ItemId char(64) primary key,
    Hash uuid not null,
    Corrupted bool not null,
    Sockets text not null,
    Quality smallint not null,

    PhysDamage smallint not null,
    EleDamage smallint not null,
    ChaosDamage smallint not null,
    AttacksPerSecond smallint not null,
    CritChance smallint not null,

    ReqLevel smallint not null,
    ReqStr smallint not null,
    ReqDex smallint not null,
    ReqInt smallint not null,

    Accuracy smallint not null,
    AddedPhysDamageLocal smallint not null,
    ChanceToFlee smallint not null,
    ChaosResist smallint not null,
    ColdResist smallint not null,
    FireResist smallint not null,
    GlobalCritMulti smallint not null,
    IncreasedAccuracy smallint not null,
    IncreasedPhysDamage smallint not null,
    IncreasedWeaponEleDamage smallint not null,
    LifeGainOnHit smallint not null,
    LifeGainOnKill smallint not null,
    LifeLeech smallint not null,
    LifeLeechCold smallint not null,
    LifeLeechFire smallint not null,
    LifeLeechLightning smallint not null,
    LightningResist smallint not null,
    LightRadius smallint not null,
    ManaGainOnKill smallint not null,
    ManaLeech smallint not null,
    SocketedGemLevel smallint not null,
    SocketedMeleeGemLevel smallint not null,
    Strength smallint not null,
    StunDuration smallint not null,
    StunThreshold smallint not null,
    SupportedByAddedFireDamage smallint not null,
    SupportedByMeleeSplash smallint not null,
    SupportedByStun smallint not null,
    WeaponRange smallint not null
);

CREATE TABLE IF NOT EXISTS TwoHandMaceItems (
    ItemId char(64) primary key,
    Hash uuid not null,
    Corrupted bool not null,
    Sockets text not null,
    Quality smallint not null,

    PhysDamage smallint not null,
    EleDamage smallint not null,
    ChaosDamage smallint not null,
    AttacksPerSecond smallint not null,
    CritChance smallint not null,

    ReqLevel smallint not null,
    ReqStr smallint not null,
    ReqDex smallint not null,
    ReqInt smallint not null,

    Accuracy smallint not null,
    AddedPhysDamageLocal smallint not null,
    ChanceToFlee smallint not null,
    ChaosResist smallint not null,
    ColdResist smallint not null,
    FireResist smallint not null,
    GlobalCritMulti smallint not null,
    IncreasedAccuracy smallint not null,
    IncreasedAoE smallint not null,
    IncreasedPhysDamage smallint not null,
    IncreasedWeaponEleDamage smallint not null,
    LifeGainOnHit smallint not null,
    LifeGainOnKill smallint not null,
    LifeLeech smallint not null,
    LifeLeechCold smallint not null,
    LifeLeechFire smallint not null,
    LifeLeechLightning smallint not null,
    LightRadius smallint not null,
    LightningResist smallint not null,
    ManaGainOnKill smallint not null,
    ManaLeech smallint not null,
    MaxPowerCharges smallint not null,
    SocketedGemLevel smallint not null,
    SocketedMeleeGemLevel smallint not null,
    Strength smallint not null,
    StunDuration smallint not null,
    StunThreshold smallint not null,
    SupportedByStun smallint not null,
    WeaponRange smallint not null
);

CREATE TABLE IF NOT EXISTS BowItems (
    ItemId char(64) primary key,
    Hash uuid not null,
    Corrupted bool not null,
    Sockets text not null,
    Quality smallint not null,

    PhysDamage smallint not null,
    EleDamage smallint not null,
    ChaosDamage smallint not null,
    AttacksPerSecond smallint not null,
    CritChance smallint not null,

    ReqLevel smallint not null,
    ReqStr smallint not null,
    ReqDex smallint not null,
    ReqInt smallint not null,

    Accuracy smallint not null,
    AddedArrow bool not null,
    AddedPhysDamageLocal smallint not null,
    ChanceToFlee smallint not null,
    ChaosResist smallint not null,
    ColdResist smallint not null,
    CullingStrike bool not null,
    Dexterity smallint not null,
    FireResist smallint not null,
    GlobalCritMulti smallint not null,
    IncreasedAccuracy smallint not null,
    IncreasedPhysDamage smallint not null,
    IncreasedWeaponEleDamage smallint not null,
    LifeGainOnHit smallint not null,
    LifeGainOnKill smallint not null,
    LifeLeech smallint not null,
    LifeLeechCold smallint not null,
    LifeLeechFire smallint not null,
    LifeLeechLightning smallint not null,
    LightningResist smallint not null,
    LightRadius smallint not null,
    ManaGainOnKill smallint not null,
    ManaLeech smallint not null,
    MaxPowerCharges smallint not null,
    MoveSpeed smallint not null,
    Pierce smallint not null,
    ProjectileSpeed smallint not null,
    SocketedGemLevel smallint not null,
    SocketedBowGemLevel smallint not null,
    StunDuration smallint not null,
    SupportedByFork smallint not null
);

CREATE TABLE IF NOT EXISTS ClawItems (
    ItemId char(64) primary key,
    Hash uuid not null,
    Corrupted bool not null,
    Sockets text not null,
    Quality smallint not null,

    PhysDamage smallint not null,
    EleDamage smallint not null,
    ChaosDamage smallint not null,
    AttacksPerSecond smallint not null,
    CritChance smallint not null,

    ReqLevel smallint not null,
    ReqStr smallint not null,
    ReqDex smallint not null,
    ReqInt smallint not null,

    Accuracy smallint not null,
    AddedPhysDamageLocal smallint not null,
    BlockChanceWhileDualWielding smallint not null,
    ChanceToFlee smallint not null,
    ChaosResist smallint not null,
    ColdResist smallint not null,
    CullingStrike bool not null,
    Dexterity smallint not null,
    FireResist smallint not null,
    GlobalCritMulti smallint not null,
    IncreasedAccuracy smallint not null,
    IncreasedPhysDamage smallint not null,
    IncreasedWeaponEleDamage smallint not null,
    Intelligence smallint not null,
    LifeGainOnHit smallint not null,
    LifeGainOnKill smallint not null,
    LifeLeech smallint not null,
    LifeLeechCold smallint not null,
    LifeLeechFire smallint not null,
    LifeLeechLightning smallint not null,
    LightningResist smallint not null,
    LightRadius smallint not null,
    Mana smallint not null,
    ManaGainOnHit smallint not null,
    ManaGainOnKill smallint not null,
    ManaLeech smallint not null,
    ManaRegen smallint not null,
    SocketedGemLevel smallint not null,
    SocketedMeleeGemLevel smallint not null,
    StunDuration smallint not null,
    SupportedByLifeLeech smallint not null,
    SupportedByMeleeSplash smallint not null,
    WeaponRange smallint not null
);

CREATE TABLE IF NOT EXISTS SceptreItems (
    ItemId char(64) primary key,
    Hash uuid not null,
    Corrupted bool not null,
    Sockets text not null,
    Quality smallint not null,

    PhysDamage smallint not null,
    EleDamage smallint not null,
    ChaosDamage smallint not null,
    AttacksPerSecond smallint not null,
    CritChance smallint not null,

    ReqLevel smallint not null,
    ReqStr smallint not null,
    ReqDex smallint not null,
    ReqInt smallint not null,

    Accuracy smallint not null,
    AddedPhysDamageLocal smallint not null,
    AddedSpellColdDamage smallint not null,
    AddedSpellFireDamage smallint not null,
    AddedSpellLightningDamage smallint not null,
    CastSpeed smallint not null,
    ChanceToFlee smallint not null,
    ChaosResist smallint not null,
    ColdResist smallint not null,
    FireResist smallint not null,
    GlobalCritMulti smallint not null,
    IncreasedAccuracy smallint not null,
    IncreasedColdDamage smallint not null,
    IncreasedEleDamage smallint not null,
    IncreasedFireDamage smallint not null,
    IncreasedLightningDamage smallint not null,
    IncreasedPhysDamage smallint not null,
    IncreasedWeaponEleDamage smallint not null,
    Intelligence smallint not null,
    LifeGainOnHit smallint not null,
    LifeGainOnKill smallint not null,
    LifeLeech smallint not null,
    LifeLeechCold smallint not null,
    LifeLeechFire smallint not null,
    LifeLeechLightning smallint not null,
    LightningResist smallint not null,
    LightRadius smallint not null,
    Mana smallint not null,
    ManaGainOnKill smallint not null,
    ManaLeech smallint not null,
    ManaRegen smallint not null,
    PenetrateEleResist smallint not null,
    PhysToCold smallint not null,
    PhysToFire smallint not null,
    PhysToLightning smallint not null,
    SocketedGemLevel smallint not null,
    SocketedColdGemLevel smallint not null,
    SocketedFireGemLevel smallint not null,
    SocketedLightningGemLevel smallint not null,
    SocketedMeleeGemLevel smallint not null,
    SpellCrit smallint not null,
    SpellDamage smallint not null,
    Strength smallint not null,
    StunDuration smallint not null,
    StunThreshold smallint not null,
    SupportedByFasterCasting smallint not null,
    SupportedByMeleeSplash smallint not null,
    SupportedByWED smallint not null
)