#!/usr/bin/python
from btsrpcapi import *
import config
from pprint import pprint

accountname = "m.xeroc"
amount = "ALL"  # BTSX
txfee = 0.1 # BTSX

if __name__ == "__main__":
 rpc = btsrpcapi(config.url, config.user, config.passwd)
 rpc.getstatus()
 rpc.walletopen(config.wallet)
 rpc.unlock(config.unlock)

 ## Get Balance
 if amount == "ALL" : 
  amount = rpc.getassetbalance( accountname, 0 ) / 1e5 - txfee

 ## Get Price
 #price = float(json.loads(rpc.marketstatus("USD","BTSX"))[ "result" ][ "avg_price_1h" ])
 orders = rpc.orderbook( "USD", "BTSX", 1e6)
 offers = []
 for os in json.loads( orders )[ "result" ] :
  for o in os :
   if o[ "type" ] == "bid_order" :
    price = float(o[ "market_index" ][ "order_price" ][ "ratio" ]) * 10
    volume = float(o[ "state" ][ "balance" ]) * 10 / 1e5
    offers.append( [ price, volume ])
 offers_sorted = sorted(offers, reverse=1, key=lambda o:o[1])

 mySum = 0.0
 for i in offers_sorted :
  mySum+=i[ 1 ]
  quant = min( [  i[ 1 ]  , amount ] )
  price = i[ 0 ]
  print "wallet_market_submit_ask %s %f %s %f %s" %(accountname,  quant, "BTSX", price, "USD")
  print rpc.marketask(accountname, quant, "BTSX", price, "USD")
  amount = amount - quant - txfee
  if amount <= 0.0 :
   break
