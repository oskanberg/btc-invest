##
# Based on kmadac's client:
# https://github.com/kmadac/bitstamp-python-client
##

from multiprocessing import Lock
import requests
import logging
import time

class public_api_client(object):
    
    def __init__(self, proxydict=None):
        self.proxydict = proxydict
        self.lock      = Lock()
    
    def retry_on_HTTPError(called_function):
        def http_handler(self, *args):
            while True:
                try:
                    return called_function(self, *args)
                except requests.exceptions.HTTPError, e:
                    logging.warning('HTTP error %s, retrying in 5s' % e)
                except requests.exceptions.ConnectionError, e:
                    logging.warning('Connection error %s, retrying in 5s' % e)
                finally:
                    time.sleep(5)
        return http_handler
    
    def queue(called_function):
        def queued(self, *args):
            logging.debug('Queueing %s' % called_function)
            with self.lock:
                time.sleep(2)
            logging.debug('Calling %s' % called_function)
            return called_function(self, *args)
        return queued

    # does not make api call so does not need to be queued
    def get_last_price(self):
        return float(self.ticker()['return']['last_all']['value_int']) / 100000.0
        
    @retry_on_HTTPError
    @queue
    def ticker(self):
        '''
        Return dictionary
        '''
        r = requests.get('http://data.mtgox.com/api/1/BTCUSD/ticker', proxies=self.proxydict)
        if r.status_code == 200:
            return r.json()
        else:
            r.raise_for_status()
