#!/usr/bin/env python
# coding=utf8

import requests
import json
import sys
from datetime import datetime
import time
from pprint import pprint
import statistics
import re
from math import fabs
import numpy as num

## -----------------------------------------------------------------------
## Load Config
## -----------------------------------------------------------------------
config_data = open('config.json')
config = json.load(config_data)
config_data.close()

## -----------------------------------------------------------------------
## function about bts rpc
## -----------------------------------------------------------------------
headers = {'content-type': 'application/json',
   'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}
auth = (config["bts_rpc"]["username"], config["bts_rpc"]["password"])
url  = config["bts_rpc"]["url"]
asset_list_all = ["PTS", "PPC", "LTC", "BTC", "SLV", "GLD", "TRY", "SGD", "HKD", "RUB", "SEK", "NZD", "CNY", "MXN", "CAD", "CHF", "AUD", "GBP", "JPY", "EUR", "USD"] #  "WTI" missing as incompatible
delegate_list = config["delegate_list"]

if sys.argv[1] == "ALL":
 asset_list_publish = asset_list_all
else:
 asset_list_publish = sys.argv
 asset_list_publish.pop(0)

def publish_rule():
 #################
 # - if you haven't published a price in the past 20 minutes
 # - if REAL_PRICE < MEDIAN and YOUR_PRICE > MEDIAN publish price
 # - if REAL_PRICE > MEDIAN and YOUR_PRICE < MEDIAN and abs( YOUR_PRICE - REAL_PRICE ) / REAL_PRICE > 0.005 publish price
 # The goal is to force the price down rapidly and allow it to creep up slowly.
 # By publishing prices more often it helps market makers maintain the peg and
 # minimizes opportunity for shorts to sell USD below the peg that the market
 # makers then have to absorb.
 # If we can get updates flowing smoothly then we can gradually reduce the spread in the market maker bots.
 # *note: all prices in USD per BTSX
 # if you haven't published a price in the past 20 minutes, and the price change more than 0.5%
 #################
 # YOUR_PRICE = Your current published price.                    = myCurrentFeed[asset]
 # REAL_PRICE = Lowest of external feeds                         = realPrice[asset]
 # MEDIAN = current median price according to the blockchain.    = price_median_blockchain[asset]
 #################
 for asset in asset_list_publish :
  ## Define REAL_PRICE
  realPrice[asset] = statistics.median( price_in_btsx[asset] )
  ## Rules 
  if (datetime.utcnow()-oldtime[asset]).total_seconds() > config["maxAgeFeedInSeconds"] :
        print("Feeds for %s too old! Force updating!" % asset)
        return True
  elif realPrice[asset]     < price_median_blockchain[asset] and \
       myCurrentFeed[asset] > price_median_blockchain[asset]:
        print("External price move for %s: realPrice(%f) < feedmedian(%f) and newprice(%f) > feedmedian(%f) Force updating!"\
               % (asset,realPrice[asset],price_median_blockchain[asset],realPrice[asset],price_median_blockchain[asset]))
        return True
  elif fabs(myCurrentFeed[asset]-realPrice[asset])/realPrice[asset] > config["change_min"] and\
       (datetime.utcnow()-oldtime[asset]).total_seconds() > config["maxAgeFeedInSeconds"] > 20*60:
        print("New Feeds differs too much for %s %.2f > %.2f! Force updating!" \
               % (asset,fabs(myCurrentFeed[asset]-realPrice[asset]), config["change_min"]))
        return True
 ## default: False
 return False

def fetch_from_btc38():
  url="http://api.btc38.com/v1/ticker.php"
  availableAssets = [ "LTC", "BTSX", "PTS" ]
  try :
   params = { 'c': 'all', 'mk_type': 'btc' }
   response = requests.get(url=url, params=params, headers=headers)
   result = response.json()
  except: 
   print("%s" % (response.text))
  for coin in availableAssets :
   if "ticker" in result[coin.lower()] and result[coin.lower()]["ticker"]:
    price_in_btc[ coin ].append(float(result[coin.lower()]["ticker"]["last"]))
    volume_in_btc[ coin ].append(float(result[coin.lower()]["ticker"]["vol"]*result[coin.lower()]["ticker"]["last"]))

  availableAssets = [ "LTC", "BTSX", "BTC", "PPC", "PTS" ]
  try :
   params = { 'c': 'all', 'mk_type': 'cny' }
   response = requests.get(url=url, params=params, headers=headers)
   result = response.json()
  except: 
   print("%s" % (response.text))
  for coin in availableAssets :
   if "ticker" in result[coin.lower()] and result[coin.lower()]["ticker"]:
    price_in_cny[ coin ].append(float(result[coin.lower()]["ticker"]["last"]))
    volume_in_cny[ coin ].append(float(result[coin.lower()]["ticker"]["vol"])*float(result[coin.lower()]["ticker"]["last"]))

def fetch_from_bter():
  try :
   url="http://data.bter.com/api/1/tickers"
   response = requests.get(url=url, headers=headers)
   result = response.json()

   availableAssets = [ "LTC", "BTSX", "PTS", "PPC" ]
   for coin in availableAssets :
    price_in_btc[ coin ].append(float(result[coin.lower()+"_btc"]["last"]))
    volume_in_btc[ coin ].append(float(result[coin.lower()+"_btc"]["vol_btc"]))

   availableAssets = [ "BTC",  "LTC", "BTSX" ]
   for coin in availableAssets :
    price_in_usd[ coin ].append(float(result[coin.lower()+"_usd"]["last"]))
    volume_in_usd[ coin ].append(float(result[coin.lower()+"_usd"]["vol_usd"]))

   availableAssets = [ "BTSX", "BTC", "LTC", "BTSX", "PTS", "PPC" ]
   for coin in availableAssets :
    price_in_cny[ coin ].append(float(result[coin.lower()+"_cny"]["last"]))
    volume_in_cny[ coin ].append(float(result[coin.lower()+"_cny"]["vol_cny"]))
  except: 
    print("Warning: unknown error, try again after 1 seconds")
    time.sleep(15)
    fetch_from_bter()

def fetch_from_poloniex():
  try:
   url="https://poloniex.com/public?command=returnTicker"
   response = requests.get(url=url, headers=headers)
   result = response.json()
   availableAssets = [ "LTC", "BTSX", "PTS", "PPC" ]
   for coin in availableAssets :
    price_in_btc[ coin ].append(float(result["BTC_"+coin.upper()]["last"]))
    volume_in_btc[ coin ].append(float(result["BTC_"+coin.upper()]["baseVolume"]))
  except: 
   print("Warning: unknown error, try again after 1 seconds")
   time.sleep(15)
   fetch_from_poloniex()

def fetch_from_bitrex():
  availableAssets = [ "BTSX", "LTC", "BTSX", "PTS", "PPC" ]
  try:
   url="https://bittrex.com/api/v1.1/public/getmarketsummaries"
   response = requests.get(url=url, headers=headers)
   result = response.json()["result"]
   for coin in result :
    if( coin[ "MarketName" ] in ["BTC-"+a for a in availableAssets] ) :
     mObj    = re.match( 'BTC-(.*)', coin[ "MarketName" ] )
     altcoin = mObj.group(1)
     price_in_btc[ altcoin ].append(float(coin["Last"]))
     volume_in_btc[ altcoin ].append(float(coin["Volume"])*float(coin["Last"]))
  except:
    print("Warning: unknown error")
    fetch_from_bitrex()

def bitassetname(asset) :
 if asset == "XAU" : 
  return "GLD"
 elif asset == "XAG" : 
  return "SLV"
 else :
  return asset

def fetch_from_yahoo():
  try :
   availableAssets = ["XAG", "XAU", "TRY", "SGD", "HKD", "RUB", "SEK", "NZD", "CNY", "MXN", "CAD", "CHF", "AUD", "GBP", "JPY", "EUR", "USD"]
   yahooAssets = ",".join(["USD"+a+"=X" for a in availableAssets])
   ##########################
   url="http://download.finance.yahoo.com/d/quotes.csv"
   params = {'s':yahooAssets,'f':'l1','e':'.csv'}
   response = requests.get(url=url, headers=headers,params=params)
   yahooprices =  response.text.split( '\r\n' )
   for i,a in enumerate(availableAssets,1) :
    price_in_usd[ bitassetname(a.upper()) ].append(1/float(yahooprices[i-1])) # flipped market
   ##########################
   yahooAssets = ",".join([a+"CNY=X" for a in availableAssets])
   url="http://download.finance.yahoo.com/d/quotes.csv"
   params = {'s':yahooAssets,'f':'l1','e':'.csv'}
   response = requests.get(url=url, headers=headers,params=params)
   yahooprices =  response.text.split( '\r\n' )
   for i,a in enumerate(availableAssets,1) :
    price_in_cny[ bitassetname(a.upper()) ].append(float(yahooprices[i-1])) ## market is the other way round! (yahooAssets)
   ##########################
   yahooAssets = ",".join(["EUR"+a+"=X" for a in availableAssets])
   url="http://download.finance.yahoo.com/d/quotes.csv"
   params = {'s':yahooAssets,'f':'l1','e':'.csv'}
   response = requests.get(url=url, headers=headers,params=params)
   yahooprices =  response.text.split( '\r\n' )
   for i,a in enumerate(availableAssets,1) :
    price_in_eur[ bitassetname(a.upper()) ].append(float(yahooprices[i-1]))
   ##########################
  except:
   print("Warning: unknown error, try again after 1 seconds")
   time.sleep(15)
   fetch_from_yahoo()

 # def get_btc_to_fiat():
 #  try:
 #   url = "https://api.bitcoinaverage.com/ticker/USD/"
 #   response = requests.get(url=url, headers=headers)
 #   result = response.json()
 #   priceBTC = float(result["24h_avg"])
 #   for b in price_in_btsx["BTC"] :
 #    price_in_btsx["USD"].append(b*priceBTC)
 #    volume_in_btsx["USD"].append(0) # no weight
 #    price_in_usd["BTC"].append(b)
 #    volume_in_usd["BTC"].append()
 # 
 #   url = "https://api.bitcoinaverage.com/ticker/EUR/"
 #   response = requests.get(url=url, headers=headers)
 #   result = response.json()
 #   priceBTC = float(result["24h_avg"])
 #   for b in price_in_btsx["BTC"] :
 #    price_in_btsx["EUR"].append(b*priceBTC)
 #    volume_in_btsx["EUR"].append(0) # no weight
 #    price_in_eur["BTC"].append(b)
 #    volume_in_eur["BTC"].append()
 # 
 #   url = "https://api.bitcoinaverage.com/ticker/CNY/"
 #   response = requests.get(url=url, headers=headers)
 #   result = response.json()
 #   priceBTC = float(result["24h_avg"])
 #   for b in price_in_btsx["BTC"] :
 #    price_in_btsx["CNY"].append(b*priceBTC)
 #    volume_in_btsx["CNY"].append(0) # no weight
 #    price_in_cny["BTC"].append(b)
 #    volume_in_cny["BTC"].append()
 # 
 #  except:
 #    print("Warning: unknown error, try again after 1 seconds")
 #    time.sleep(15)
 #    get_btc_to_fiat()

def fetch_from_wallet():
 ##############################
 for asset in asset_list_publish :
  headers = {'content-type': 'application/json'}
  request = {
    "method": "blockchain_get_asset",
    "params": [asset],
    "jsonrpc": "2.0", "id": 1 }
  response = requests.post(url, data=json.dumps(request), headers=headers, auth=auth)
  result = response.json()
  assetprecision[asset] = float(result["result"]["precision"])
  ##############################
  #headers = {'content-type': 'application/json'}
  #request = {
  #  "method": "blockchain_market_order_book",
  #  "params": [asset, "BTSX", 100],
  #  "jsonrpc": "2.0", "id": 1 }
  #response = requests.post(url, data=json.dumps(request), headers=headers, auth=auth)
  #result = response.json()
  #realPrice[asset] = 0.0 # init offline markets
  #for os in result["result"] :
  # for o in os :
  #  if (o["type"]=="bid_order") :
  #   ratio = float(o["market_index"]["order_price"]["ratio"])
  #   realPrice[asset] = ratio * assetprecision[asset]/assetprecision["BTSX"]
  ##############################
  headers = {'content-type': 'application/json'}
  request = {
    "method": "blockchain_get_feeds_for_asset",
    "params": [asset],
    "jsonrpc": "2.0", "id": 1 }
  response = requests.post(url, data=json.dumps(request), headers=headers, auth=auth)
  result = response.json()
  price_median_blockchain[asset] = 0.0
  for feed in result["result"] :
   if feed["delegate_name"] == "MARKET":
    price_median_blockchain[asset] = float(feed["median_price"])
 ##############################
 for delegate in delegate_list:
  headers = {'content-type': 'application/json'}
  request = {
    "method": "blockchain_get_feeds_from_delegate",
    "params": [delegate],
    "jsonrpc": "2.0", "id": 1 }
  response = requests.post(url, data=json.dumps(request), headers=headers, auth=auth)
  result = response.json()
  for f in result[ "result" ] :
   myCurrentFeed[ f[ "asset_symbol" ] ] = f[ "price" ]
   oldtime[ f[ "asset_symbol" ] ] = datetime.strptime(f["last_update"],"%Y%m%dT%H%M%S")
 ##############################

def update_feed(assets,payee):
  for delegate in delegate_list:
        headers = {'content-type': 'application/json'}
        request = {
            "method": "wallet_publish_feeds",
            "params": [delegate, assets, payee],
            "jsonrpc": "2.0",
            "id": 1
            }
        while True:
          try:
            response = requests.post(url, data=json.dumps(request), headers=headers, auth=auth)
            result = response.json()
            print("Update:", delegate, assets, result)
          except:
            print("Warnning: Can't connect to rpc server, retry 5 seconds later")
            time.sleep(5)
            continue
          break

def get_weighted_mean():
 for asset in asset_list_publish :
  price_in_btsx[asset] = []
  volume_in_btsx[asset] = []
 ## BTC ################
 for asset in asset_list_publish :
  for i in price_in_btc[ asset ] :
   for idx in range(0, len(price_in_btc["BTSX"])) : # Price
    price_in_btsx[asset].append( float("%.8g" % float(price_in_btc["BTSX"][idx]/i)))
    volume_in_btsx[asset].append(float("%.8g" % float(volume_in_btc["BTSX"][idx]/i)))
 ## CNY ################
 for asset in asset_list_publish :
  for i in price_in_cny[ asset ] :
   for idx in range(0, len(price_in_cny["BTSX"])) : # Price
    price_in_btsx[asset].append( float("%.8g" % float(price_in_cny["BTSX"][idx]/i)))
    volume_in_btsx[asset].append(float("%.8g" % float(volume_in_cny["BTSX"][idx]/i)))
 ## USD ################
 for asset in asset_list_publish :
  for i in price_in_usd[ asset ] :
   for idx in range(0, len(price_in_usd["BTSX"])) : # Price
    price_in_btsx[asset].append( float("%.8g" % float(price_in_usd["BTSX"][idx]/i)))
    volume_in_btsx[asset].append(float("%.8g" % float(volume_in_usd["BTSX"][idx]/i)))
 
 for asset in asset_list_publish :
  ### Median
  #price_in_btsx_average[asset] = statistics.median(price_in_btsx[asset])
  ### Mean
  #price_in_btsx_average[asset] = statistics.mean(  price_in_btsx[asset]   )
  ### Weighted Mean
  volume     = [b for b in  volume_in_btsx[asset] ]
  assetprice = [a for a in  price_in_btsx[asset]  ]
  price_in_btsx_average[asset] = num.average(assetprice, weights=volume)

  ### Discount
  price_in_btsx_average[asset] = price_in_btsx_average[asset] / config["discount"]

if __name__ == "__main__":
 ## Initialization ###################################
 volume_in_cny         = {}
 volume_in_usd         = {}
 volume_in_btc         = {}
 volume_in_eur         = {}
 volume_in_btsx        = {}
 price_in_cny          = {}
 price_in_usd          = {}
 price_in_btc          = {}
 price_in_eur          = {}
 price_in_btsx         = {}
 price_in_btsx_average = {}
 volume                = {}
 myCurrentFeed              = {}
 price_median_blockchain   = {}
 realPrice             = {}
 assetprecision        = {}
 assetprecision["BTSX"] = 1e5
 oldtime               = {}

 for asset in asset_list_all + ["BTSX"]: 
  price_in_btsx[ asset ]       = []
  price_in_eur[ asset ]        = []
  price_in_usd[ asset ]        = []
  price_in_btc[ asset ]        = []
  price_in_cny[ asset ]        = []
  volume_in_eur[ asset ]       = []
  volume_in_usd[ asset ]       = []
  volume_in_btc[ asset ]       = []
  volume_in_cny[ asset ]       = []
  volume_in_btsx[ asset ]       = []
  price_in_btsx_average[asset] = 0.0
  myCurrentFeed[asset]              = 0.0
  price_median_blockchain[asset]   = 0.0
  realPrice[asset]             = 0.0
  oldtime[asset]               = datetime.utcnow()

 ## Get prices and stats #############################
 print( "="*80 )
 print("Loading old feeds")
 fetch_from_wallet()
 print("Loading Yahoo")
 fetch_from_yahoo()
 print("Loading BTC38")
 fetch_from_btc38()
 print("Loading BTer")
 fetch_from_bter()
 print("Loading Poloniex")
 fetch_from_poloniex()
 print("Loading bitrex")
 fetch_from_bitrex()
 # print("Load btc to fiat") ## has volume = 0 by my very definition
 # get_btc_to_fiat()
 print("Weighted Mean")
 get_weighted_mean()

 ## Discount!!
 asset_list_final = []
 for asset in asset_list_publish :
  if len(price_in_btsx[asset]) > 0 :
   if price_in_btsx_average[asset] > 0.0:
    asset_list_final.append([ asset, price_in_btsx_average[asset] ])
    print("{0}: new price: {1:>10.5f} (change my old: {2:+7.2f}%) (change to curr. median: {3:+7.2f}%) (my feed is {4!s})".format(\
               asset,price_in_btsx_average[asset],\
               (price_in_btsx_average[asset]-myCurrentFeed[asset])           *100,
               (price_in_btsx_average[asset]-price_median_blockchain[asset])*100,\
               str(datetime.utcnow()-oldtime[asset]) ))
 if publish_rule() :
  print("Update required! Forcing now!")
  update_feed(asset_list_final, config["payaccount"])
 else :
  print("no update required")
