#!/usr/bin/python

import logging
from bitstamp_api import api_client as bitstamp_api
from mtgox_api import public_api_client as mtgox_api
from networking import networking_kernel
from brains import daemon
from multiprocessing import Process

if __name__ == "__main__":
    log_format = '%(funcName)20s %(levelname)10s [%(asctime)s] :: %(message)s'
    logging.basicConfig(format=log_format, level=logging.DEBUG)
    bitstamp_api = bitstamp_api()
    mtgox_api    = mtgox_api()
    apis = {
        'bitstamp_api' : bitstamp_api,
        'mtgox_api'    : mtgox_api
    }
    kernel = networking_kernel(apis)
    logging.debug('Starting network kernel process ...')
    Process(target=kernel.update, args=()).start()
    logging.debug('Starting daemon ...')
    d = daemon(kernel)
    d.run()