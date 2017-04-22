import argparse
import cProfile
import pstats
import sys

from .indexer import Indexer, load_next_change_id
from .itemdb import ItemDB
from .poeapi import PoEApi


def main(args):
    if args.profile:
        pr = cProfile.Profile()
        pr.enable()

    next_change_id = load_next_change_id() if args.id is None else args.id
    db = ItemDB(args.db)
    api = PoEApi()
    indexer = Indexer(db, api, next_change_id)

    if args.max_updates > 0:
        for i in range(args.max_updates):
            indexer.process_next_stash_update()
    else:
        indexer.run()

    if args.profile:
        pr.disable()
        ps = pstats.Stats(pr, stream=sys.stdout).sort_stats('cumulative')
        ps.print_stats()


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--id')
    ap.add_argument('--max-updates', type=int, default=0, help='End program after this many updates')
    ap.add_argument('--profile', default=False, action='store_true')
    ap.add_argument('--db', default="dbname='poeria' user='benjamin'", help='Database credentials')
    return ap.parse_args()


if __name__ == '__main__':
    main(parse_args())
