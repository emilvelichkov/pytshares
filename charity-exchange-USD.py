#!/usr/bin/python
from btsrpcapi import *
import config

accountname = "payouts.charity"
percentage  = 0.90

if __name__ == "__main__":
 rpc = btsrpcapi(config.url, config.user, config.passwd)
 print rpc.getstatus()
 print rpc.walletopen(config.wallet)
 print rpc.unlock(config.unlock)

 ## Get Price
 #price = float(json.loads(rpc.marketstatus("USD","BTSX"))[ "result" ][ "avg_price_1h" ])
 orders = rpc.orderbook( "USD", "BTSX", 1 )
 for o in json.loads( orders )[ "result" ] :
  if o[ 0 ][ "type" ] == "ask_order" :
   price = float(o[ 0 ][ "market_index" ][ "order_price" ][ "ratio" ]) * 10

 #prices = []
 #for o in json.loads(rpc.orderhistory("USD","BTSX",10))[ "result" ]:
 # prices.append(float(o[ "bid_price" ][ "ratio" ])*10)
 # prices.append(float(o[ "ask_price" ][ "ratio" ])*10)
 #price = sum( prices ) / len( prices );
 #print price

 ## getbalance
 balances = rpc.getbalance(accountname)
 for b in json.loads(balances)[ "result" ][ 0 ][ 1 ][ 0 ] :
   if b[ 0 ] == "BTSX" :
       balance = float(b[ 1 ])/1.0e5;

 ## put bid order 
 quant = balance * percentage
 print "wallet_market_submit_ask %s %f %s %f %s\n\n" %(accountname,  quant, "BTSX", price, "USD")
 print rpc.marketask(accountname, quant, "BTSX", price, "USD")
