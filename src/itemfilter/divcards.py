import requests
from collections import defaultdict

import sys

def get_divcard_prices(league):
    prices = dict()
    url = "http://poeninja.azureedge.net/api/Data/GetDivinationCardsOverview"
    response = requests.get(url, {'league': league}).json()
    for item in response['lines']:
        prices[item['name']] = item['chaosValue']
    return prices


def build_filter_code(card_prices):
    worthless, mediocre, valuable, awesome = [], [], [], []
    for k, v in card_prices.items():
        if v <= 0.3:
            worthless.append(k)
        elif v < 2:
            mediocre.append(k)
        elif v < 15:
            valuable.append(k)
        else:
            awesome.append(k)

    code = """
# Strongly highlight very valuable cards (15c+)
Show
    Class "Divination Card"
    BaseType {}
    SetBackgroundColor 183 111 240
    SetTextColor 0 0 0
    SetFontSize 48
    SetBorderColor 0 0 0
    PlayAlertSound 6 300

# Highlight cards that are moderately valuable (2c+)
Show
    Class "Divination Card"
    BaseType {}
    SetBackgroundColor 64 40 84 220
    SetBorderColor 0 0 0
	SetTextColor 183 111 240
	SetFontSize 38
    PlayAlertSound 1 300

# Show cards normally that aren't very valuable (<=1c)
Show
    Class "Divination Card"
    BaseType {}
    SetTextColor 183 111 240
    PlayAlertSound 2 100

# Smaller font size for troll cards
Show
    Class "Divination Card"
    BaseType {}
    SetTextColor 183 111 240
    SetFontSize 24

# Draw pink border around all cards not recognized by the filter
# (They are constantly adding new cards, and I'm too lazy even to add the cards that are already there)
Show
    Class "Divination Card"
    SetBorderColor 255 100 255
	SetTextColor 183 111 240
    PlayAlertSound 1 300
    """.format(
        ' '.join('"{}"'.format(x) for x in awesome),
        ' '.join('"{}"'.format(x) for x in valuable),
        ' '.join('"{}"'.format(x) for x in mediocre),
        ' '.join('"{}"'.format(x) for x in worthless),
    )
    return code

if __name__ == '__main__':
    league = sys.argv[1]
    print(build_filter_code(get_divcard_prices(league)))
