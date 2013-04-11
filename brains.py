#!/usr/bin/python

from api import public_api_client

import datetime
import logging
import time
import os

class crisis_daemon():
    
    def __init__(self, public_api_client, baseline_price=None):
        self.alive = True
        self.risk_level = 0.0
        self.public_api_client = public_api_client
        self.baseline_price = baseline_price
        if self.baseline_price == None:
            self.baseline_price = self.public_api_client.get_last_price()
        logging.info('Baseline price = %f' % self.baseline_price)
    
    def evaluate_risk_level(self):
        ticker = self.public_api_client.ticker()
        day_variance = float(ticker['high']) - float(ticker['low'])

        logging.info('Last 24h variance: %f' % day_variance)
        last_48h_trades = self.public_api_client.transactions(172800)
        prices = [trade['price'] for trade in last_48h_trades]
        logging.info('Last 48h minimum price: %f' % min(map(float, prices)))

    def run(self):
        while self.alive:
            self.evaluate_risk_level()
            time.sleep(5)


if __name__ == "__main__":
    logging.basicConfig(format='%(funcName)20s %(levelname)10s [%(asctime)s] :: %(message)s', level=logging.DEBUG)
    public_client = public_api_client()
    crisis_d = crisis_daemon(public_client)
    crisis_d.run()
