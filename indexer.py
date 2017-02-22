from item import type as itemtype

class Indexer(object):
    def __init__(self, item_db, poeapi, first_id='0'):
        self.item_db = item_db
        self.poeapi = poeapi
        self.is_running = False
        self.next_change_id = first_id

    def run(self):
        self.is_running = True
        while self.is_running:
            self.process_next_stash_update()

    def process_next_stash_update(self):
        print("Requesting next...")
        stashes = self.get_next_stash_update()
        print("Received {} stashes".format(len(stashes)))
        deleted = 0
        for stash in stashes:
            deleted += self.item_db.update_stash(stash)
        self.item_db.commit()
        print("Sold: ", deleted)
        print("Total Items: ", self.item_db.count())

    def get_next_stash_update(self):
        """
        Fetches the next update set from the POE API and returns a list of stashes that changed.
        """
        response = self.poeapi.public_stash_tabs(self.next_change_id)
        self.next_change_id = response['next_change_id']
        print(self.next_change_id)
        return response['stashes']

    def process_stash(self, stash):
        self.item_db.add_items(stash['items'], stash['stash'])


