from blessings import Terminal

UNKNOWN = 0
STANDARD = 1
HARDCORE = 2
BREACH = 3
BREACH_HC = 4
LEGACY = 5
LEGACY_HC = 6

ALL_SOFTCORE_LEAGUES = [STANDARD, BREACH, LEGACY]

LEAGUE_ID = {
    'Standard': STANDARD,
    'Hardcore': HARDCORE,
    'Breach': BREACH,
    'Hardcore Breach': BREACH_HC,
    'Legacy': LEGACY,
    'Hardcore Legacy': LEGACY_HC
}


def get_id(league_name):
    league_id = LEAGUE_ID.get(league_name, UNKNOWN)
    if league_id == UNKNOWN:
        print(Terminal().bold_red("Unknown League: {}".format(league_name)))
    return league_id


def get_name(league_id):
    return [k for k,v in LEAGUE_ID.items() if v == league_id][0]
