import time
from simplejson import JSONDecodeError

import requests
import requests.exceptions


class PoEApi(object):
    def __init__(self, min_seconds_between_requests = 5):
        self.last_id = None
        self.last_request_time = 0
        self.min_seconds_between_requests = min_seconds_between_requests

    def public_stash_tabs(self, id=0):
        self.last_id = id
        url = 'http://api.pathofexile.com/public-stash-tabs?id={}'.format(id)
        while True:
            try:
                self.rate_limit()
                req = requests.get(url, timeout=5)
                response = req.json()
                assert 'next_change_id' in response, "Invalid Response: " + req.text
                return response
            except requests.exceptions.Timeout:
                print("Connection timed out, trying again.")
            except AssertionError:
                print("Invalid Response, trying again")
            except JSONDecodeError as ex:
                print("Invalid JSON: ", ex.msg)
                print("Trying again")

    def rate_limit(self):
        seconds_since_last_request = time.time() - self.last_request_time
        if seconds_since_last_request < self.min_seconds_between_requests:
            wait_time = self.min_seconds_between_requests - seconds_since_last_request
            print("too fast, waiting for", wait_time, "seconds")
            time.sleep(wait_time)
        self.last_request_time = time.time()
