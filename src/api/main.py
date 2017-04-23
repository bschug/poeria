import json
import sys
import os
from indexer.itemdb import ItemDB

from flask import Flask
app = Flask(__name__)

db_credentials = os.environ['DB_CREDENTIALS']


@app.route('/api/v1/stats')
def stats():
    itemdb = ItemDB(db_credentials)
    stats = itemdb.get_stats()
    return json.dumps(stats)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)