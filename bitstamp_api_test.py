#!/usr/bin/python
import getpass
from bitstamp_api import api_client as bitstamp_api
import logging

class APITest(object):

    def __init__(self):
        user = getpass.getpass(prompt='User:')
        password = getpass.getpass()
        self.api =  bitstamp_api(user=user, password=password)

    def test_get_highest_bid(self):
        highest = self.api.get_highest_bid()
        assert highest > 50, "NOPE"

    def test_ensure_sold_at_market_price(self):
        self.api.ensure_sold_at_market_price(0.01)

    def test__watch_market_sell_orders(self):
        self.api._watch_market_sell_orders([{'id':123}])

    def test_buy_and_sell(self):
        print '#############', self.api.buy_at_market_price_with_limit(0.01, 125)
        print '#############', self.api.ensure_sold_at_market_price(0.01)


log_format = '%(funcName)20s %(levelname)10s [%(asctime)s] :: %(message)s'
logging.basicConfig(format=log_format, level=logging.DEBUG)
test = APITest()
test.test_buy_and_sell()