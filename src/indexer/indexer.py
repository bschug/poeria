import time


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
        start_time = time.time()
        stashes = self.get_next_stash_update()
        print("Received {} stashes after {:.1f} seconds".format(
            len(stashes), time.time() - start_time))

        start_time = time.time()
        total_num_deleted = 0
        total_added = []
        for stash in stashes:
            added, num_deleted = self.item_db.update_stash(stash)
            total_added.extend(added)
            total_num_deleted += num_deleted
        self.item_db.add_items(total_added)
        self.item_db.commit()
        print("Processed {} items in {:.2f} seconds".format(
            len(total_added), time.time() - start_time))
        print("Sold: ", num_deleted)
        print("Total Items: ", self.item_db.count())

    def get_next_stash_update(self):
        """
        Fetches the next update set from the POE API and returns a list of stashes that changed.
        """
        response = self.poeapi.public_stash_tabs(self.next_change_id)
        self.next_change_id = response['next_change_id']
        print(self.next_change_id)
        store_next_change_id(self.next_change_id)
        return response['stashes']



def store_next_change_id(next_change_id):
    with open('next_change_id.txt', 'w') as fp:
        fp.write(next_change_id)


def load_next_change_id():
    try:
        with open('next_change_id.txt', 'r') as fp:
            return fp.read()
    except:
        return '0'