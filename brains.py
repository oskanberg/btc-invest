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
        return price_disparity

    def buy_at_price(self, price):
        self.committed = True
        self.buy_in_price = price + self.trade_duty
        logging.debug('Bought in at %f' % self.buy_in_price)
        return True

    def sell_at_price(self, price):
        margin = (price - (price * self.trade_duty)) - self.buy_in_price
        self.profit += margin
        self.committed = False
        return True

    def ensure_sold_at_market_price(self, amount):
        '''
        Make sure amount is sold: adjust price if market changes
        @return the price that it sold at
        '''
        logging.debug('Ordering amount: %f at market price' % amount)
        open_orders = self._open_market_level_sell_orders(amount)
        self._watch_market_sell_orders(open_orders)

    def _watch_market_sell_orders(self, open_orders):
        '''
        Check that the orders are closed. If not, reopen them at market levels.
        '''
        api = self.kernel.get_api('bitstamp_api')
        actual_open_orders = api.open_orders()

        amount_to_reopen = 0.0
        actual_ids = [ order['id'] for order in actual_open_orders ]
        for order in open_orders:
            if order['id'] in actual_ids:
                logging.debug('Order %s still open. Closing.' % order['id'] )
                amount_to_reopen += float(order['amount'])
            else:
                logging.debug('Order %s has been closed.' % order['id'] )
        self.ensure_sold_at_market_price(amount_to_reopen)

    def _open_market_level_sell_orders(self, amount):
        '''
        Recursively buy the best asks until amount is ordered
        @return the open ask_orders (dict)
        '''
        api = self.kernel.get_api('bitstamp_api')
        order_book = api.order_book(group=True)
        ask_orders = [(float(order[0]), float(order[1])) for order in order_book['asks']]
        ask_orders.sort()
        lowest_ask = min([order[0] for order in ask_orders])
        assert ask_orders[0][0] == lowest_ask, 'sorting failed?'

        ask_price = ask_orders[0]
        ask_amount = ask_orders[1]
        if ask_amount > amount:
            logging.debug('Bid for %f at %f' % (amount, ask_price))
            order = [api.sell_limit_order(amount, ask_price)]
            return order
        else:
            logging.debug('Bid for %f at %f' % (amount, ask_price))
            order = [api.sell_limit_order(ask_amount, ask_price)]
            return order.append(self._open_market_level_sell_orders(amount - ask_amount))

    def buy_at_market_price_with_limit(self, amount, limit):
        '''
        Buy at the market price, but no more than limit
        @return the price that it sold at, None if failed
        '''
        

    def _open_market_level_buy_orders(self, amount):
        '''
        Recursively buy the best asks until amount is ordered
        @return the open ask_orders (dict)
        '''
        api = self.kernel.get_api('bitstamp_api')
        order_book = api.order_book(group=True)
        ask_orders = [(float(order[0]), float(order[1])) for order in order_book['asks']]
        ask_orders.sort()
        lowest_ask = min([order[0] for order in ask_orders])
        assert ask_orders[0][0] == lowest_ask, 'sorting failed?'

        ask_price = ask_orders[0]
        ask_amount = ask_orders[1]
        if ask_amount > amount:
            logging.debug('Bid for %f at %f' % (amount, ask_price))
            order = [api.sell_limit_order(amount, ask_price)]
            return order
        else:
            logging.debug('Bid for %f at %f' % (amount, ask_price))
            order = [api.sell_limit_order(ask_amount, ask_price)]
            return order.append(self._open_market_level_sell_orders(amount - ask_amount))



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
