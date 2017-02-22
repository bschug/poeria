UNKNOWN = 0
ALT = 1
FUSE = 2
ALCH = 3
CHAOS = 4
GCP = 5
EXA = 6
CHROM = 7
JEW = 8
CHANCE = 9
CHISEL = 10
SCOUR = 11
BLESSED = 12
REGRET = 13
REGAL = 14
DIVINE = 15
VAAL = 16

CURRENCY_ID = {
    'alt': ALT,
    'fuse': FUSE,
    'alch': ALCH,
    'chaos': CHAOS,
    'gcp': GCP,
    'exa': EXA,
    'chrom': CHROM,
    'jew': JEW,
    'chance': CHANCE,
    'chisel': CHISEL,
    'scour': SCOUR,
    'blessed': BLESSED,
    'regret': REGRET,
    'regal': REGAL,
    'divine': DIVINE,
    'vaal': VAAL
}


def get_id(currency_name):
    return CURRENCY_ID.get(currency_name, UNKNOWN)
