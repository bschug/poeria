import requests
from collections import defaultdict

import sys


def get_unique_prices(league):
    unique_prices = defaultdict(lambda: 0)
    get_unique_prices_from_url('http://poeninja.azureedge.net/api/Data/GetUniqueWeaponOverview', league, unique_prices)
    get_unique_prices_from_url('http://poeninja.azureedge.net/api/Data/GetUniqueArmourOverview', league, unique_prices)
    get_unique_prices_from_url('http://poeninja.azureedge.net/api/Data/GetUniqueAccessoryOverview', league, unique_prices)
    get_unique_prices_from_url('http://poeninja.azureedge.net/api/Data/GetUniqueFlaskOverview', league, unique_prices)
    return unique_prices

def get_unique_prices_from_url(url, league, unique_prices):
    response = requests.get(url, {'league': league}).json()
    for item in response['lines']:
        unique_prices[item['baseType']] = max(unique_prices[item['baseType']], item['chaosValue'])

def build_filter_code(unique_prices):
    worthless, mediocre, valuable, awesome = [], [], [], []
    for k, v in unique_prices.items():
        if v < 0.5:
            worthless.append(k)
        elif v < 2:
            mediocre.append(k)
        elif v < 15:
            valuable.append(k)
        else:
            awesome.append(k)

    code = """
# Top Tier Uniques (15c+)
Show
    Rarity Unique
    BaseType {}
    SetBackgroundColor 175 78 17
    SetTextColor 0 0 0
    SetBorderColor 0 0 0
    SetFontSize 45
    PlayAlertSound 6 300

# Decent Uniques (2c+)
Show
    Rarity Unique
    BaseType {}
    SetFontSize 45
    SetBackgroundColor 70 35 14 220
    SetBorderColor 0 0 0
    PlayAlertSound 6 300

# Mediocre Uniques (~1c)
Show
    Rarity Unique
    BaseType {}
    SetFontSize 38

# Worthless Uniques (< 2 alch)
Show
    Rarity Unique
    BaseType {}
    SetFontSize 24

# Draw pink border around unknown Uniques
Show
    Rarity Unique
    SetBorderColor 255 100 255
    """.format(
        ' '.join('"{}"'.format(x) for x in awesome),
        ' '.join('"{}"'.format(x) for x in valuable),
        ' '.join('"{}"'.format(x) for x in mediocre),
        ' '.join('"{}"'.format(x) for x in worthless),
    )
    return code

if __name__ == '__main__':
    league = sys.argv[1]
    print(build_filter_code(get_unique_prices(league)))
