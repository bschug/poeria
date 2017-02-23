import os

import time

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

CURRENCY_SHORTNAMES = {
    'Orb of Alteration': 'alt',
    'Orb of Fusing': 'fuse',
    'Orb of Alchemy': 'alch',
    'Chaos Orb': 'chaos',
    'Gemcutter\'s Prism': 'gcp',
    'Exalted Orb': 'exa',
    'Chromatic Orb': 'chrom',
    'Jeweller\'s Orb': 'jew',
    'Orb of Chance': 'chance',
    'Cartographer\'s Chisel': 'chisel',
    'Orb of Scouring': 'scour',
    'Blessed Orb': 'blessed',
    'Orb of Regret': 'regret',
    'Regal Orb': 'regal',
    'Divine Orb': 'divine',
    'Vaal Orb': 'vaal'
}


def get_id(currency_name):
    """
    Returns the currency ID for the given short name.
    (Short name as used in price tags, e.g. exa for Exalted Orbs)
    """
    return CURRENCY_ID.get(currency_name, UNKNOWN)


def id_to_shortname(currency_id):
    """
    Returns the short name of the currency with the given id.
    """
    return [k for k,v in CURRENCY_ID.items() if v == currency_id][0]


def full_name_to_short(long_name):
    """
    Returns the shortname for a given currency, or None if there is no shortname for it.
    """
    return CURRENCY_SHORTNAMES.get(long_name, None)


def get_exchange_rates(league):
    """
    Returns up-to-date currency exchange rates.
    If cached data is less than one hour old, uses that.
    Otherwise fetches new data from poe.ninja.
    """
    cache_file = exchange_rate_cache_file(league)
    if os.path.exists(cache_file):
        cache_age = time.time() - os.path.getmtime(cache_file)
        if cache_age < 3600:
            return load_cached_exchange_rates(league)

    rates = load_exchange_rates_from_poe_ninja(league)
    store_exchange_rates(rates, league)
    return rates


def exchange_rate_cache_file(league):
    """
    Returns the path of the exchange rate cache file for a given league.
    """
    basedir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    return os.path.join(basedir, 'exchange_rates', league+'.csv')


def load_cached_exchange_rates(league):
    """
    Loads a CSV file with two columns (currency name, value in chaos)
    and returns it as a dictionary of currency id -> value in chaos
    """
    result = dict()
    with open(exchange_rate_cache_file(league), 'r') as fp:
        while True:
            try:
                cname, cvalue = fp.readline().split(',')
                result[CURRENCY_ID[cname]] = float(cvalue)
            except:
                break
    return result


def store_exchange_rates(rates, league):
    """
    Store exchange rates to CSV cache file.
    """
    cache_file = exchange_rate_cache_file(league)
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)
    with open(cache_file, 'w') as fp:
        for cid, value in rates.items():
            cname = id_to_shortname(cid)
            fp.write(cname)
            fp.write(',')
            fp.write(str(value))
            fp.write('\n')


def load_exchange_rates_from_poe_ninja(league):
    """
    Converts the JSON response from poe.ninja into a dictionary of currency id -> value in chaos.
    """
    import requests
    result = dict()
    response = requests.get('http://poe.ninja/api/Data/GetCurrencyOverview?league=' + league).json()
    for currency_data in response['lines']:
        shortname = full_name_to_short(currency_data['currencyTypeName'])
        if shortname is None:
            continue
        cid = get_id(shortname)
        result[cid] = currency_data['chaosEquivalent']

    # Manually add Chaos because as the reference currency, poe.ninja of course doesn't include it
    result[CHAOS] = 1
    return result
