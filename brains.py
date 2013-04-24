
from multiprocessing import Queue, Process
import datetime
import logging
import time
import os

class daemon(object):
    
    def __init__(self, kernel):
        self.alive = True
        self.trade_duty = 0.02
        self.kernel = kernel
        self.buy_in_price = 0
        self.committed = False
        self.profit = 0.0
        self.positive_disparity = 0
        self.negative_disparity = 0
    
    def multiprocess_call(self, queue, function, args):
        result = function(args)
        queue.put((args,result))

    def evaluate_disparity(self):
        queue = Queue()
        processes = []
        for api in ['bitstamp_api', 'mtgox_api']:
            api_call = Process(target=self.multiprocess_call,\
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
        return price_disparity

    def buy_at_price(self, price):
        self.committed = True
        self.buy_in_price = price
        logging.debug('Bought in at %f' % self.buy_in_price)
        return True

    def sell_at_price(self, price):
        margin = (price - (price * self.trade_duty)) - self.buy_in_price
        self.profit += margin
        self.committed = False
        return True

    def run(self):
        while self.alive:
            price_disparity = self.evaluate_disparity()
            logging.info('Price disparity: %f' % price_disparity)
            if self.committed:
                if price_disparity > 1:
                    logging.debug('Funds committed but positive price disparity. Staying put.')
                else:
                    logging.debug('Selling; not significantly large price disparity.')
                    sell_price = self.kernel.get_cached_price('bitstamp_api')
                    self.sell_at_price(sell_price)
            else:
                if price_disparity > 5:
                    # Have to call the API again, probably more accurate
                    buy_in_price = self.kernel.get_cached_price('bitstamp_api')
                    self.buy_at_price(buy_in_price)
                else:
                    logging.debug('Not buying in yet.')
            logging.info('Profit so far: %f' % self.profit)
            time.sleep(10)
