#!/usr/bin/python

from bitstamp_api import api_client as bitstamp_api

user = '55005'
password = 'PoIoP424242......'

api = bitstamp_api(user=user, password=password)

orders = api.open_orders()
print orders
assert len(orders) == 0

print api.buy_limit_order(1, 1)
orders = api.open_orders()
print orders
assert len(orders) == 1

api.cancel_order(orders[0]['id'])
orders = api.open_orders()
print orders
assert len(orders) == 0