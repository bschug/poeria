import json

import flask
import psycopg2

from .predictor import Predictor
from constants import league

app = flask.Flask(__name__)

predictor = Predictor()


@app.route('/api/v1/{account_name}/{league}')
def get_predictions(account_name, league):
    stash_id = get_stash_id(account_name, league)
    return json.dumps(predictor.predict(stash_id))


def get_stash_id(account_name, league_name):
    dbconn = psycopg2.connect("dbname='poeria' user='benjamin'")
    db = dbconn.cursor()
    db.execute('SELECT StashId FROM Players WHERE AccountName = %s AND League = %s',
               (account_name, league.get_id(league_name)))
    return db.fetchone()[0]


if __name__ == '__main__':
    app.run('localhost', 8080)
