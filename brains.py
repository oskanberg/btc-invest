#!/usr/bin/python

from api import api_client

import datetime
import time
import os

ac = api_client()

while True:
    ticker = ac.ticker()
    os.system(['clear', 'cls'][os.name == 'nt'])
    print ' Updated: %s' % datetime.datetime.now()
    print '=====================================\n'
    for key in ticker.keys():
        print '%s:\t%s' % (key, ticker[key])
    time.sleep(10)

