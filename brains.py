#!/bin/false

from multiprocessing import Queue, Process
import datetime
import logging
import time
import os

class daemon(object):
    
    def __init__(self, kernel):
        self.alive = True
        self.trade_duty = 0.004
        self.kernel = kernel
        self.buy_in_price = 0
        self.committed = False
        self.profit = 0.0
        self.positive_disparity = 0
        self.negative_disparity = 0
    
    def _multiprocess_call(self, queue, function, args):
        result = function(args)
        queue.put((args,result))

    def evaluate_disparity(self):
        queue = Queue()
        processes = []
        for api in ['bitstamp_api', 'mtgox_api']:
            api_call = Process(target=self._multiprocess_call,\
                args=(queue, self.kernel.get_cached_price, api))
            
            processes.append(api_call)
        for process in processes: process.start()
        for process in processes: process.join()
        for item in xrange(queue.qsize()):
            result = queue.get()
            if result[0] == 'mtgox_api':
                mtgox_price = float(result[1])
            elif result[0] == 'bitstamp_api':
                bitstamp_price = float(result[1])
        logging.info('Bitstamp price: %f' % bitstamp_price)
        logging.info('Mtgox price: %f' % mtgox_price)
        price_disparity = mtgox_price - bitstamp_price
        if price_disparity > 0 :
            self.positive_disparity += 1
        else:
            self.negative_disparity += 1
        logging.info('Disparity ratio: %f:%f' % (self.positive_disparity, self.negative_disparity))
        return (price_disparity, bitstamp_price)

    def record_trades(self, trade_list):
        with open('/tmp/trades', 'a+') as f:
            for trade in trades:
                f.write(trade)
    
    def run(self):
        while self.alive:
            price_disparity, bitstamp_price = self.evaluate_disparity()
            logging.info('Price disparity: %f' % price_disparity)
            if self.committed:
                if price_disparity > 1:
                    logging.debug('Funds committed but positive price disparity. Staying put.')
                else:
                    logging.debug('Selling; not significantly large price disparity.')
                    sale = self.kernel.get_api['bitstamp_api'].ensure_sold_at_market_price(1)
                    self.record_trades(sale)
            else:
                if price_disparity > 5:
                    api = self.kernel.get_api['bitstamp_api']
                    api.buy_at_market_price_with_limit(1, bitstamp_price + (price_disparity - 3))
                else:
                    logging.debug('Not buying in yet.')
            time.sleep(10)
