import argparse

from indexer import Indexer
from itemdb import ItemDB
from poeapi import PoEApi


def main(args):
    next_change_id = load_next_change_id() if args.id is None else args.id
    db = ItemDB()
    api = PoEApi()
    indexer = Indexer(db, api, next_change_id)
    try:
        if args.max_updates > 0:
            for i in range(args.max_updates):
                indexer.process_next_stash_update()
        else:
            indexer.run()
    finally:
        store_next_change_id(indexer.next_change_id)


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--id')
    ap.add_argument('--max-updates', type=int, default=0, help='End program after this many updates')
    return ap.parse_args()


def store_next_change_id(next_change_id):
    with open('next_change_id.txt', 'w') as fp:
        fp.write(next_change_id)


def load_next_change_id():
    try:
        with open('next_change_id.txt', 'r') as fp:
            return fp.read()
    except:
        return '0'


if __name__ == '__main__':
    main(parse_args())
