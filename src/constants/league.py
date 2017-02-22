UNKNOWN = 0
STANDARD = 1
HARDCORE = 2
BREACH = 3
BREACH_HC = 4

LEAGUE_ID = {
    'Standard': STANDARD,
    'Hardcore': HARDCORE,
    'Breach': BREACH,
    'Hardcore Breach': BREACH_HC
}


def get_id(league_name):
    return LEAGUE_ID.get(league_name, 0)


def get_name(league_id):
    return [k for k,v in LEAGUE_ID.items() if v == league_id]
