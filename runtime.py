#!/usr/bin/python

import os
from bitstamp_api import api_client as bitstamp_api
from mtgox_api import public_api_client as mtgox_api
from networking import networking_kernel
import brains
from multiprocessing import Process
import getpass

if __name__ == "__main__":
    user = os.environ.get('BITSTAMP_USERNAME')
    password = os.environ.get('BITSTAMP_PASSWORD')
    
    if None in (user, password):
        user = getpass.getpass(prompt='User:')
        password = getpass.getpass()

    bitstamp_api = bitstamp_api(user=user, password=password)
    mtgox_api    = mtgox_api()
    apis = {
        'bitstamp_api' : bitstamp_api,
        'mtgox_api'    : mtgox_api
    }
    kernel = networking_kernel(apis)
    
    Process(target=kernel.update, args=()).start()
    
    d = brains.brain(kernel)
    d.run()