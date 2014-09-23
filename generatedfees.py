#!/usr/bin/python
import csv
import os
from btsrpcapi import *
import config

names1 = {'charity-delegate-1', 'charity-delegate-2', 'charity-delegate-3', 'charity-delegate-4',
          'charity-delegate-5', 'charity-delegate-6', 'charity-delegate-7', 'charity-delegate-8',
          'charity-delegate-9', 'delegate.charity', 'a.delegate.charity', 'b.delegate.charity',
          'c.delegate.charity', 'd.delegate.charity', 'e.delegate.charity', 'f.delegate.charity',
         }
names2 = {'xeroc-delegate-1', 'xeroc-delegate-2', 'xeroc-delegate-3', 'xeroc-delegate-4',
          'xeroc-delegate-5', 'xeroc-delegate-6', 'xeroc-delegate-7', 'xeroc-delegate-8',
          'xeroc-delegate-9', 'delegate.xeroc', 'a.delegate.xeroc', 'b.delegate.xeroc',
          'c.delegate.xeroc', 'd.delegate.xeroc', 'e.delegate.xeroc', 'f.delegate.xeroc',
         }

def getprice(altcoin) :
 url = "http://www.cryptocoincharts.info/v2/api/tradingPair/%s_btc" % altcoin
 request = requests.get(url);
 content = request.text
 j = json.loads(content)
 return j["price"]

def doit(names) :
 rpc = btsrpcapi(config.url, config.user, config.passwd)
 price = float(getprice("btsx"))
 paybalance = 0
 for name in names :
  a         = json.loads(rpc.getaccount(name))
  paybalance += int(a["result"]["delegate_info"]["pay_balance"])
 print "Paybalance: %.5f BTSX (%.2f BTC)" % (paybalance/1e5, paybalance/1e5*price)

if __name__ == "__main__":
 print "XeRoc-delegates\n---------------------"
 doit(names1)

 print "\nCharity-delegates\n-------------------"
 doit(names2)
