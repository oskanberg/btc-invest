#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import time
import datetime
import json
import urllib2

INITIAL_TIME        = 1359643500
INITIAL_VALUE       = 145.85
INITIAL_CONVERSION  = 0.63018
INITIAL_BTC         = 7.13449122

def print_title(title):
    print ''.join(['_' for i in range(35)])
    print title
    print ''.join(['-' for i in range(35)])

while True:
    btc_data = urllib2.urlopen('http://blockchain.info/ticker')
    current_value = float(json.load(btc_data)['USD']['15m'] * INITIAL_BTC)
    value_delta = (current_value / INITIAL_VALUE) * 100 - 100
    conversion_data = urllib2.urlopen('http://rate-exchange.appspot.com/currency?from=USD&to=GBP')
    usd_in_gbp = float(json.load(conversion_data)['rate'])
    conversion_delta = (usd_in_gbp / INITIAL_CONVERSION) * 100 - 100
    
    os.system(['clear', 'cls'][os.name == 'nt'])
    print 'Updated: %s' % datetime.datetime.now()
    print_title('USD')
    print 'Original value\t: %f USD'    % INITIAL_VALUE
    print 'Current value\t: %f USD'     % current_value
    print 'Delta\t\t: %f%%'             % value_delta
    
    print_title('GBP')
    print 'Orig. USD-GBP\t: %f'     % INITIAL_CONVERSION
    print 'Current USD-GBP\t: %f'   % usd_in_gbp
    print 'Delta\t\t: %f%%'         % conversion_delta
    print 'Converted\t: %f GBP'     % (current_value * usd_in_gbp)
    time.sleep(30)
    
