#!/usr/bin/python

from api import public_api_client

import datetime
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
        print 'crisis_daemon:\t\tbaseline_price = %f' % self.baseline_price
    
    def update_tracker(self):
        latest_trade = self.public_api_client.get_last_price()
        if self.trades_record:
            if latest_trade != self.trades_record[-1]:
                self.trades_record.append(latest_trade)
            else:
                print 'crisis_daemon:\t\tLast trade price has not changed.'
        else:
            self.trades_record.append(latest_trade)
    
    def evaluate_risk_level(self):
        # last five minutes
        trades = self.public_api_client.transactions(300)
        # TODO
        

    def run(self):
        while self.alive:
            self.evaluate_risk_level()
            time.sleep(5)


if __name__ == "__main__":
    public_client = public_api_client()
    crisis_d = crisis_daemon(public_client)
    crisis_d.run()
