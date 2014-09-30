#!/usr/bin/env python3
# coding=utf8 sw=1 expandtab ft=python

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

## ----------------------------------------------------------------------------
## When do we have to force publish?
## ----------------------------------------------------------------------------
def publish_rule():
 ##############################################################################
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
 ##############################################################################
 # YOUR_PRICE = Your current published price.                    = myCurrentFeed[asset]
 # REAL_PRICE = Lowest of external feeds                         = realPrice[asset]
 # MEDIAN = current median price according to the blockchain.    = price_median_blockchain[asset]
 ##############################################################################
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

## ----------------------------------------------------------------------------
## Fetch data
## ----------------------------------------------------------------------------
def fetch_from_btc38():
  url="http://api.btc38.com/v1/ticker.php"
  availableAssets = [ "LTC", "BTSX", "PTS" ]
  try :
   params = { 'c': 'all', 'mk_type': 'btc' }
   response = requests.get(url=url, params=params, headers=headers)
   result = response.json()
  except: 
   sys.exit("unknown error - btc38")
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
   sys.exit("unkown error - btc38")
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
    sys.exit("Warning: unknown error - BTer")

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
   sys.exit("Warning: unknown error - poloniex")

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
    sys.exit("Warning: unknown error - bittrex")

def fetch_from_yahoo():
  try :
   availableAssets = ["XAG", "XAU", "TRY", "SGD", "HKD", "RUB", "SEK", "NZD", "CNY", "MXN", "CAD", "CHF", "AUD", "GBP", "JPY", "EUR", "USD"]
   ## USD/X
   yahooAssets = ",".join(["USD"+a+"=X" for a in availableAssets])
   url="http://download.finance.yahoo.com/d/quotes.csv"
   params = {'s':yahooAssets,'f':'l1','e':'.csv'}
   response = requests.get(url=url, headers=headers,params=params)
   yahooprices =  response.text.split( '\r\n' )
   for i,a in enumerate(availableAssets,1) :
    price_in_usd[ bitassetname(a.upper()) ].append(1/float(yahooprices[i-1])) # flipped market
   ## CNY/X
   yahooAssets = ",".join([a+"CNY=X" for a in availableAssets])
   url="http://download.finance.yahoo.com/d/quotes.csv"
   params = {'s':yahooAssets,'f':'l1','e':'.csv'}
   response = requests.get(url=url, headers=headers,params=params)
   yahooprices =  response.text.split( '\r\n' )
   for i,a in enumerate(availableAssets,1) :
    price_in_cny[ bitassetname(a.upper()) ].append(float(yahooprices[i-1])) ## market is the other way round! (yahooAssets)
   ## EUR/X
   yahooAssets = ",".join(["EUR"+a+"=X" for a in availableAssets])
   url="http://download.finance.yahoo.com/d/quotes.csv"
   params = {'s':yahooAssets,'f':'l1','e':'.csv'}
   response = requests.get(url=url, headers=headers,params=params)
   yahooprices =  response.text.split( '\r\n' )
   for i,a in enumerate(availableAssets,1) :
    price_in_eur[ bitassetname(a.upper()) ].append(float(yahooprices[i-1]))
  except:
   sys.exit("Warning: unknown error - yahoo")

## ----------------------------------------------------------------------------
## GLD=XAU  SLV=XAG
## ----------------------------------------------------------------------------
def bitassetname(asset) :
 if asset == "XAU" : 
  return "GLD"
 elif asset == "XAG" : 
  return "SLV"
 else :
  return asset

## ----------------------------------------------------------------------------
## Fetch current feeds, assets and feeds of assets from wallet
## ----------------------------------------------------------------------------
def fetch_from_wallet():
 headers = {'content-type': 'application/json'}
 ## Try to connect to delegate
 request = { "method": "info", "params": [], "jsonrpc": "2.0", "id": 1 }
 try:
  response = requests.post(url, data=json.dumps(request), headers=headers, auth=auth)
  result = response.json()
 except:
  print("Cannot connect to delegate!!")
  sys.exit()
 ## asset definition - mainly for precision
 for asset in asset_list_publish :
  headers = {'content-type': 'application/json'}
  request = {
    "method": "blockchain_get_asset",
    "params": [asset],
    "jsonrpc": "2.0", "id": 1 }
  response = requests.post(url, data=json.dumps(request), headers=headers, auth=auth)
  result = response.json()
  assetprecision[asset] = float(result["result"]["precision"])
  ## feeds for asset
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
  time.sleep(.5) # Give time for the wallet to do more important tasks!
 ## feed from delegates
 for delegate in delegate_list:
  request = {
    "method": "blockchain_get_feeds_from_delegate",
    "params": [delegate],
    "jsonrpc": "2.0", "id": 1 }
  response = requests.post(url, data=json.dumps(request), headers=headers, auth=auth)
  result = response.json()
  for f in result[ "result" ] :
   myCurrentFeed[ f[ "asset_symbol" ] ] = f[ "price" ]
   oldtime[ f[ "asset_symbol" ] ] = datetime.strptime(f["last_update"],"%Y%m%dT%H%M%S")

## ----------------------------------------------------------------------------
## Send the new feeds!
## ----------------------------------------------------------------------------
def update_feed(assets,payee):
 headers = {'content-type': 'application/json'}
 ## Try to connect to delegate
 request = { "method": "info", "params": [], "jsonrpc": "2.0", "id": 1 }
 try:
  response = requests.post(url, data=json.dumps(request), headers=headers, auth=auth)
  result = response.json()
 except:
  print("Cannot connect to delegate!!")
  sys.exit()

 # for each delegate update the list
 for delegate in delegate_list:
  request = {
   "method": "wallet_publish_feeds",
   "params": [delegate, assets, payee],
   "jsonrpc": "2.0",
   "id": 1
  }
  try:
   response = requests.post(url, data=json.dumps(request), headers=headers, auth=auth)
   result = response.json()
   print("Update:", delegate, assets, result)
  except:
   print("Cannot connect to delegate!!")
   sys.exit()

## ----------------------------------------------------------------------------
## calculate feed prices in BTSX for all assets given the exchange prices in USD,CNY,BTC
## ----------------------------------------------------------------------------
def get_btsxprice():
 for asset in asset_list_publish :
  price_in_btsx[asset] = []
  volume_in_btsx[asset] = []
 ## BTC
 for asset in asset_list_publish :
  for i in price_in_btc[ asset ] :
   for idx in range(0, len(price_in_btc["BTSX"])) : # Price
    price_in_btsx[asset].append( float("%.8g" % float(price_in_btc["BTSX"][idx]/i)))
    volume_in_btsx[asset].append(float("%.8g" % float(volume_in_btc["BTSX"][idx]/i)))
 ## CNY
 for asset in asset_list_publish :
  for i in price_in_cny[ asset ] :
   for idx in range(0, len(price_in_cny["BTSX"])) : # Price
    price_in_btsx[asset].append( float("%.8g" % float(price_in_cny["BTSX"][idx]/i)))
    volume_in_btsx[asset].append(float("%.8g" % float(volume_in_cny["BTSX"][idx]/i)))
 ## USD
 for asset in asset_list_publish :
  for i in price_in_usd[ asset ] :
   for idx in range(0, len(price_in_usd["BTSX"])) : # Price
    price_in_btsx[asset].append( float("%.8g" % float(price_in_usd["BTSX"][idx]/i)))
    volume_in_btsx[asset].append(float("%.8g" % float(volume_in_usd["BTSX"][idx]/i)))
 ## EUR
 for asset in asset_list_publish :
  for i in price_in_eur[ asset ] :
   for idx in range(0, len(price_in_eur["BTSX"])) : # Price
    price_in_btsx[asset].append( float("%.8g" % float(price_in_eur["BTSX"][idx]/i)))
    volume_in_btsx[asset].append(float("%.8g" % float(volume_in_eur["BTSX"][idx]/i)))
 
 for asset in asset_list_publish :
  ### Median
  #price_in_btsx_average[asset] = statistics.median(price_in_btsx[asset])
  ### Mean
  #price_in_btsx_average[asset] = statistics.mean(price_in_btsx[asset])
  ### Weighted Mean
  volume     = [b for b in  volume_in_btsx[asset] ]
  assetprice = [a for a in  price_in_btsx[asset]  ]
  price_in_btsx_average[asset] = num.average(assetprice, weights=volume)

  ### Discount
  price_in_btsx_average[asset] = price_in_btsx_average[asset] / config["discount"]


def print_stats() :
 print( "="*220)
 for asset in asset_list_publish :
    p = price_in_btsx_average[asset]
    ps = price_in_btsx[asset]
    bc = price_median_blockchain[asset]
    print("{0}|new: {1:>7.5f}BTSX (e:{2:>7.5f}/{3:>7.5f}) (bc:{4:>7.5f})  ".format(asset, p, statistics.mean(ps), statistics.median(ps), bc)+\
          "|  change: {0:+5.2f}%  ".format((p - myCurrentFeed[asset])*100)+\
          "|  change (to med.): {0:+7.2f}%  ".format((p - bc)*100)+\
          "|  exchange (median): {0:+5.2f}%  ".format((statistics.median(ps)-p)/p*100)+\
          "|  exchange (range): {0:+5.2f}% to {1:+7.2f}%  ".format((num.min(ps)-p)/p*100,(num.max(ps)-p)/p*100 )+\
          "|  last update: {0!s} ago".format(str(datetime.utcnow()-oldtime[asset]))  )

## ----------------------------------------------------------------------------
## Run Script
## ----------------------------------------------------------------------------
if __name__ == "__main__":
 ## Load Config ###############################################################
 config_data = open('config.json')
 config = json.load(config_data)
 config_data.close()
 ## rpc variables about bts rpc ###############################################
 headers = {'content-type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}
 auth    = (config["bts_rpc"]["username"], config["bts_rpc"]["password"])
 url     = config["bts_rpc"]["url"]
 asset_list_all = ["PTS", "PPC", "LTC", "BTC", "SLV", "GLD", "TRY", "SGD", "HKD", "RUB", "SEK", "NZD", "CNY", "MXN", "CAD", "CHF", "AUD", "GBP", "JPY", "EUR", "USD"] #  "WTI" missing as incompatible
 delegate_list  = config["delegate_list"]
 ## Call Parameters ###########################################################
 if len( sys.argv ) < 2 :
  sys.exit( "Usage: btsx_feed.py <space separated list of currencies>" )
 else :
  if sys.argv[1] == "ALL":
   asset_list_publish = asset_list_all
  else :
   asset_list_publish = sys.argv
   asset_list_publish.pop(0)

 ## Initialization
 volume_in_cny           = {}
 volume_in_usd           = {}
 volume_in_btc           = {}
 volume_in_eur           = {}
 volume_in_btsx          = {}
 price_in_cny            = {}
 price_in_usd            = {}
 price_in_btc            = {}
 price_in_eur            = {}
 price_in_btsx           = {}
 price_in_btsx_average   = {}
 volume                  = {}
 myCurrentFeed           = {}
 price_median_blockchain = {}
 realPrice               = {}
 assetprecision          = {}
 assetprecision["BTSX"]  = 1e5
 oldtime                 = {}

 for asset in asset_list_all + ["BTSX"]: 
  price_in_btsx[ asset ]         = []
  price_in_eur[ asset ]          = []
  price_in_usd[ asset ]          = []
  price_in_btc[ asset ]          = []
  price_in_cny[ asset ]          = []
  volume_in_eur[ asset ]         = []
  volume_in_usd[ asset ]         = []
  volume_in_btc[ asset ]         = []
  volume_in_cny[ asset ]         = []
  volume_in_btsx[ asset ]        = []
  price_in_btsx_average[asset]   = 0.0
  myCurrentFeed[asset]           = 0.0
  price_median_blockchain[asset] = 0.0
  realPrice[asset]               = 0.0
  oldtime[asset]                 = datetime.utcnow()

 ## Get prices and stats ######################################################
 print("Loading data: ", end="",flush=True)
 fetch_from_wallet()
 print("yahoo", end="",flush=True)
 fetch_from_yahoo()
 print(", BTC38", end="",flush=True)
 fetch_from_btc38()
 print(", BTer", end="",flush=True)
 fetch_from_bter()
 print(", Poloniex", end="",flush=True)
 fetch_from_poloniex()
 print(", bittrex", end="",flush=True)
 fetch_from_bitrex()
 print(" -- done. Calculating btsx feeds prices and checking publish rules.")

 ## Determine btsx price ######################################################
 get_btsxprice()

 ## Only publish given feeds ##################################################
 asset_list_final = []
 for asset in asset_list_publish :
  if len(price_in_btsx[asset]) > 0 :
   if price_in_btsx_average[asset] > 0.0:
    asset_list_final.append([ asset, price_in_btsx_average[asset] ])

 ## Print some stats ##########################################################
 print_stats()

 ## Check publish rules and publich feeds #####################################
 if publish_rule() :
  print("Update required! Forcing now!")
  update_feed(asset_list_final, config["payaccount"])
 else :
  print("no update required")
