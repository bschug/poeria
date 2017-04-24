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


@app.route('/api/v1/log')
def print_log_default():
    return print_log(0)


@app.route('/api/v1/log/<offset>')
def print_log(offset):
    offset = int(offset)
    current_size = os.stat('/home/bschug/log').st_size
    offset = min(max(0, current_size - 1024, offset), current_size)

    with open('/home/bschug/log', 'rb') as fp:
        fp.seek(offset)
        data = fp.read(current_size - offset).decode('utf-8')
        return json.dumps({'data': data, 'offset': current_size})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
