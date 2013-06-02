#!/bin/false

##
# Based on kmadac's client:
# https://github.com/kmadac/bitstamp-python-client
##

from multiprocessing import Lock
import requests
import logging
import time

class api_client(object):
    
    def __init__(self, proxydict=None, user=None, password=None):
        self.proxydict = proxydict
        self.lock      = Lock()
        self.params = {'user': user, 'password': password}

    def retry_on_HTTPError(called_function):
        def http_handler(self, *args, **kwargs):
            while True:
                try:
                    return called_function(self, *args, **kwargs)
                except requests.exceptions.HTTPError, e:
                    logging.warning('HTTP error %s, retrying in 5s' % e)
                except requests.exceptions.ConnectionError, e:
                    logging.warning('Connection error %s, retrying in 5s' % e)
                finally:
                    time.sleep(5)
        return http_handler
    

    # A lot of functions are not process safe, and the apis
    # have rate limits
    def queue(called_function):
        def queued(self, *args, **kwargs):
            logging.debug('Queueing %s' % called_function)
            with self.lock:
                time.sleep(2)
                logging.debug('Calling %s' % called_function)
                ret = called_function(self, *args, **kwargs)
            return ret
        return queued

    # does not make api call so does not need to be queued
    def get_last_price(self):
        return float(self.ticker()['last'])
        
    @retry_on_HTTPError
    @queue
    def ticker(self):
        '''
        Return dictionary
        '''
        r = requests.get('https://www.bitstamp.net/api/ticker/', proxies=self.proxydict)
        if r.status_code == 200:
            return r.json()
        else:
            r.raise_for_status()

    @retry_on_HTTPError
    @queue
    def order_book(self, group=True):
        '''
        Returns JSON dictionary with 'bids' and 'asks'.
        Each is a list of open orders and each order is represented as a list of price and amount.
        '''
        params = {'group': group}

        r = requests.get('https://www.bitstamp.net/api/order_book/', params=params, proxies=self.proxydict)
        if r.status_code == 200:
            return r.json()
        else:
            r.raise_for_status()

    @retry_on_HTTPError
    @queue
    def transactions(self, timedelta_secs=86400):
        '''
        Returns transactions for the last 'timedelta' seconds
        '''
        params = {'timedelta': timedelta_secs}

        r = requests.get('https://www.bitstamp.net/api/transactions/', params=params, proxies=self.proxydict)
        if r.status_code == 200:
            return r.json()
        else:
            r.raise_for_status()

    @retry_on_HTTPError
    @queue
    def bitinstant_reserves(self):
        '''
        Returns simple dictionary {'usd': 'Bitinstant USD reserves'}
        '''
        r = requests.get('https://www.bitstamp.net/api/bitinstant/', proxies=self.proxydict)
        if r.status_code == 200:
            return r.json()
        else:
            r.raise_for_status()

    @retry_on_HTTPError
    @queue
    def conversion_rate_usd_eur(self):
        '''
        Returns simple dictionary
        {'buy': 'buy conversion rate', 'sell': 'sell conversion rate'}
        '''
        r = requests.get('https://www.bitstamp.net/api/eur_usd/', proxies=self.proxydict)
        if r.status_code == 200:
            return r.json()
        else:
            r.raise_for_status()

    @retry_on_HTTPError
    @queue
    def account_balance(self):
        '''
        Returns dictionary:
        {u'btc_reserved': u'0',
         u'fee': u'0.5000',
         u'btc_available': u'2.30856098',
         u'usd_reserved': u'0',
         u'btc_balance': u'2.30856098',
         u'usd_balance': u'114.64',
         u'usd_available': u'114.64'}
        '''
        r = requests.post('https://www.bitstamp.net/api/balance/', data=self.params, proxies=self.proxydict)
        if r.status_code == 200:
            if 'error' in r.json():
                return False, r.json()['error']
            else:
                return r.json()
        else:
            r.raise_for_status()

    @retry_on_HTTPError
    @queue
    def user_transactions(self, timedelta_secs=86400):
        '''
        Returns descending list of transactions. Every transaction (dictionary) contains
        {u'usd': u'-39.25',
         u'datetime': u'2013-03-26 18:49:13',
         u'fee': u'0.20', u'btc': u'0.50000000',
         u'type': 2,
         u'id': 213642}
        '''
        self.params['timedelta'] = timedelta_secs

        r = requests.post('https://www.bitstamp.net/api/user_transactions/', data=self.params, proxies=self.proxydict)
        if r.status_code == 200:
            if 'error' in r.json():
                return False, r.json()['error']
            else:
                return r.json()
        else:
            r.raise_for_status()

    @retry_on_HTTPError
    @queue
    def open_orders(self):
        '''
        Returns JSON list of open orders. Each order is represented as dictionary:
        '''
        r = requests.post('https://www.bitstamp.net/api/open_orders/', data=self.params, proxies=self.proxydict)
        if r.status_code == 200:
            if 'error' in r.json():
                return False, r.json()['error']
            else:
                return r.json()
        else:
            r.raise_for_status()

    @retry_on_HTTPError
    @queue
    def cancel_order(self, order_id):
        '''
        Cancel the order specified by order_id
        Returns True if order was successfully canceled,
        otherwise tuple (False, msg) like (False, u'Order not found')
        '''
        self.params['id'] = order_id
        r = requests.post('https://www.bitstamp.net/api/cancel_order/', data=self.params, proxies=self.proxydict)
        if r.status_code == 200:
            if r.text == u'true':
                return True
            else:
                return False, r.json()['error']
        else:
            r.raise_for_status()

    @retry_on_HTTPError
    @queue
    def buy_limit_order(self, amount, price):
        '''
        Order to buy amount of bitcoins for specified price
        '''
        self.params['amount'] = amount
        self.params['price'] = price

        r = requests.post('https://www.bitstamp.net/api/buy/', data=self.params, proxies=self.proxydict)
        if r.status_code == 200:
            if 'error' in r.json():
                return False, r.json()['error']
            else:
                return r.json()
        else:
            r.raise_for_status()

    @retry_on_HTTPError
    @queue
    def sell_limit_order(self, amount, price):
        '''
        Order to buy amount of bitcoins for specified price
        '''
        self.params['amount'] = amount
        self.params['price'] = price

        r = requests.post('https://www.bitstamp.net/api/sell/', data=self.params, proxies=self.proxydict)
        if r.status_code == 200:
            if 'error' in r.json():
                return False, r.json()['error']
            else:
                return r.json()
        else:
            r.raise_for_status()

    @retry_on_HTTPError
    @queue
    def bitcoin_withdrawal(self, amount, address):
        '''
        Send bitcoins to another bitcoin wallet specified by address
        '''
        self.params['amount'] = amount
        self.params['address'] = address

        r = requests.post('https://www.bitstamp.net/api/bitcoin_withdrawal/', data=self.params, proxies=self.proxydict)
        if r.status_code == 200:
            if r.text == u'true':
                return True
            else:
                return False, r.json()['error']
        else:
            r.raise_for_status()

    @retry_on_HTTPError
    @queue
    def bitcoin_deposit_address(self):
        '''
        Returns bitcoin deposit address as unicode string
        '''
        r = requests.post('https://www.bitstamp.net/api/bitcoin_deposit_address/', data=self.params,
                          proxies=self.proxydict)
        if r.status_code == 200:
            if 'error' in r.json():
                return False, r.json()['error']
            else:
                return r.text
        else:
            r.raise_for_status()

    @retry_on_HTTPError
    @queue
    def withdrawal_requests(self):
        '''
        Returns list of withdrawal requests. Each request is represented as dictionary
        '''
        r = requests.post('https://www.bitstamp.net/api/withdrawal_requests/', data=self.params,
                          proxies=self.proxydict)
        if r.status_code == 200:
            if 'error' in r.json():
                return False, r.json()['error']
            else:
                return r.json()
        else:
            r.raise_for_status()
