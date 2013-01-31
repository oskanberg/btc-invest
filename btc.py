#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import time
import datetime
import json
import urllib2

initial_time = 1359643500
initial_value = 145.85
btc = 7.12083752

while True:
    btc_data = urllib2.urlopen('http://blockchain.info/ticker')
    current_value = float(json.load(btc_data)['USD']['15m'] * btc)
    delta = (current_value / initial_value) * 100 - 100
    conversion_data = urllib2.urlopen('http://rate-exchange.appspot.com/currency?from=USD&to=GBP')
    usd_in_gbp = float(json.load(conversion_data)['rate'])
    os.system(['clear', 'cls'][os.name == 'nt'])
    print 'Updated: %s' % datetime.datetime.now()
    print ''.join(['_' for i in range(35)])
    print 'Original value\t: %f USD'   % initial_value
    print 'Current value\t: %f USD'    % current_value
    print 'Delta\t\t: %f%%'         % delta
    print 'Converted\t: %f GBP' % (current_value * usd_in_gbp)
    time.sleep(30)
