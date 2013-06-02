#!/bin/false

import time
import logging

class networking_kernel(object):

    def __init__(self, apis_dict):
        self.api_cache = {}
        self.apis = apis_dict
        for api_key in self.apis:
            self.api_cache[api_key] = { 
                'time' : 0,
                'float_value' : 999.99
            }

    def update_cache(self):
        for api_key in self.apis:
            self.api_cache[api_key]['float_value'] = self.apis[api_key].get_last_price()
            self.api_cache[api_key]['time'] = time.time()

    def get_cached_price(self, api_id):
        # Retrieve the cached version if we checked less than 10s ago
        if time.time() - self.api_cache[api_id]['time'] < 10:
            return self.api_cache[api_id]['float_value']
        else:
            self.update_cache()
            return self.api_cache[api_id]['float_value']

    def get_api(self, api_id):
        return self.apis[api_id]

    def update(self):
        while True:
            self.update_cache()
            time.sleep(10)