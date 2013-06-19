#!/bin/false

from multiprocessing import Queue, Process
import datetime
import time
import os
import logging

TRADES_PAGE = '/var/www/trades.html'
LOG_PAGE = '/var/www/index.html'

class brain(object):
    
    def __init__(self, kernel):
        log_format = '<pre>%(funcName)20s %(levelname)10s [%(asctime)s] :: %(message)s</pre>'
        logging.basicConfig(
            level=logging.DEBUG,
            format=log_format,
            filename=LOG_PAGE,
            filemode='w'
        )
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

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
        price_disparity = mtgox_price - bitstamp_price
        if price_disparity > 0 :
            self.positive_disparity += 1
        else:
            self.negative_disparity += 1
        return (price_disparity, bitstamp_price)

    def record_trades(self, trade_list):
        with open(TRADES_PAGE, 'a+') as f:
            for trade in trade_list:
                f.write(str(trade))
    
    def run(self):
        while self.alive:
            price_disparity, bitstamp_price = self.evaluate_disparity()
            self.logger.info('price disparity: %f', price_disparity)
            if self.committed:
                if price_disparity <= 1:
                    self.logger.debug('price disparity too low - selling')
                    sale = self.kernel.get_api('bitstamp_api').ensure_sold_at_market_price(1)
                    self.record_trades(sale)
                    self.committed = False
                else:
                    self.logger.debug('committed, but suitable positive disparity')
            else:
                if price_disparity > 3:
                    self.logger.debug('large price disparity - committing')
                    api = self.kernel.get_api('bitstamp_api')
                    sale = api.buy_at_market_price_with_limit(1, bitstamp_price + (price_disparity - 1))
                    self.record_trades(sale)
                    self.committed = True
                else:
                    self.logger.debug('not committed and not committing')
            time.sleep(10)
