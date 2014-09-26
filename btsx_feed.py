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

headers = {'content-type': 'application/json',
   'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}

payaccount = "delegate.xeroc"
maxAgeFeedInSeconds = 20 * 60 # 20 minutes

## Actually I think it may be beneficial to discount all feeds by 0.995 to give
## the market makers some breathing room and provide a buffer against down trends.
discount = 0.995
change_min = 0.5

## -----------------------------------------------------------------------
## Load Config
## -----------------------------------------------------------------------
config_data = open('config.json')
config = json.load(config_data)
config_data.close()

## -----------------------------------------------------------------------
## function about bts rpc
## -----------------------------------------------------------------------
auth = (config["bts_rpc"]["username"], config["bts_rpc"]["password"])
url  = config["bts_rpc"]["url"]
asset_list_all = ["PTS", "PPC", "LTC", "BTC", "SLV", "GLD", "TRY", "SGD", "HKD", "RUB", "SEK", "NZD", "CNY", "MXN", "CAD", "CHF", "AUD", "GBP", "JPY", "EUR", "USD"] #  "WTI" missing as incompatible
delegate_list = config["delegate_list"]

if sys.argv[1] == "ALL":
 asset_list_publish = asset_list_all
else:
 asset_list_publish = sys.argv
 asset_list_publish.pop(0)

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
    if coin not in price_in_btc : price_in_btc[ coin ] = []
    price_in_btc[ coin ].append(float(result[coin.lower()]["ticker"]["last"]))

  availableAssets = [ "LTC", "BTSX", "BTC", "PPC", "PTS" ]
  try :
   params = { 'c': 'all', 'mk_type': 'cny' }
   response = requests.get(url=url, params=params, headers=headers)
   result = response.json()
  except: 
   print("%s" % (response.text))
  for coin in availableAssets :
   if "ticker" in result[coin.lower()] and result[coin.lower()]["ticker"]:
    if coin not in price_in_cny : price_in_cny[ coin ] = []
    price_in_cny[ coin ].append(float(result[coin.lower()]["ticker"]["last"]))

def bitassetname(asset) :
 if asset == "XAU" : 
  return "GLD"
 elif asset == "XAG" : 
  return "SLV"
 else :
  return asset

def fetch_from_yahoo():
  availableAssets = ["XAG", "XAU", "TRY", "SGD", "HKD", "RUB", "SEK", "NZD", "CNY", "MXN", "CAD", "CHF", "AUD", "GBP", "JPY", "EUR", "USD"]
  yahooAssets = ",".join(["USD"+a+"=X" for a in availableAssets])
  try :
   ##########################
   url="http://download.finance.yahoo.com/d/quotes.csv"
   params = {'s':yahooAssets,'f':'l1','e':'.csv'}
   response = requests.get(url=url, headers=headers,params=params)
   yahooprices =  response.text.split( '\r\n' )
   for i,a in enumerate(availableAssets,1) :
    if bitassetname(a.upper()) not in price_in_usd : price_in_usd[ bitassetname(a.upper()) ] = []
    price_in_usd[ bitassetname(a.upper()) ].append(1/float(yahooprices[i-1])) # flipped market
   ##########################
   yahooAssets = ",".join([a+"CNY=X" for a in availableAssets])
   url="http://download.finance.yahoo.com/d/quotes.csv"
   params = {'s':yahooAssets,'f':'l1','e':'.csv'}
   response = requests.get(url=url, headers=headers,params=params)
   yahooprices =  response.text.split( '\r\n' )
   for i,a in enumerate(availableAssets,1) :
    if bitassetname(a.upper()) not in price_in_cny : price_in_cny[ bitassetname(a.upper()) ] = []
    price_in_cny[ bitassetname(a.upper()) ].append(float(yahooprices[i-1])) ## market is the other way round! (yahooAssets)
   ##########################
   yahooAssets = ",".join(["EUR"+a+"=X" for a in availableAssets])
   url="http://download.finance.yahoo.com/d/quotes.csv"
   params = {'s':yahooAssets,'f':'l1','e':'.csv'}
   response = requests.get(url=url, headers=headers,params=params)
   yahooprices =  response.text.split( '\r\n' )
   for i,a in enumerate(availableAssets,1) :
    if bitassetname(a.upper()) not in price_in_eur : price_in_eur[ bitassetname(a.upper()) ] = []
    price_in_eur[ bitassetname(a.upper()) ].append(float(yahooprices[i-1]))
   ##########################
  except:
   print("Warning: unknown error, try again after 1 seconds")
   time.sleep(1)
   fetch_from_yahoo()

def fetch_from_bter():
  url="http://data.bter.com/api/1/tickers"
  try :
   response = requests.get(url=url, headers=headers)
   result = response.json()

   availableAssets = [ "LTC", "BTSX", "PTS", "PPC" ]
   for coin in availableAssets :
    if coin not in price_in_btc : price_in_btc[ coin ] = []
    price_in_btc[ coin ].append(float(result[coin.lower()+"_btc"]["last"]))

   availableAssets = [ "BTC",  "LTC", "BTSX" ]
   for coin in availableAssets :
    if coin not in price_in_usd : price_in_usd[ coin ] = []
    price_in_usd[ coin ].append(float(result[coin.lower()+"_usd"]["last"]))

   availableAssets = [ "BTSX", "BTC", "LTC", "BTSX", "PTS", "PPC" ]
   for coin in availableAssets :
    if coin not in price_in_cny : price_in_cny[ coin ] = []
    price_in_cny[ coin ].append(float(result[coin.lower()+"_cny"]["last"]))
  except: 
    print("Warning: unknown error, try again after 1 seconds")
    time.sleep(1)
    fetch_from_bter()

def fetch_from_poloniex():
  try:
   url="https://poloniex.com/public?command=returnTicker"
   response = requests.get(url=url, headers=headers)
   result = response.json()
   availableAssets = [ "LTC", "BTSX", "PTS", "PPC" ]
   for coin in availableAssets :
    if coin not in price_in_btc : price_in_btc[ coin ] = []
    price_in_btc[ coin ].append(float(result["BTC_"+coin.upper()]["last"]))
  except: 
   print("Warning: unknown error, try again after 1 seconds")
   time.sleep(1)
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
     if altcoin not in price_in_btc : price_in_btc[ altcoin ] = []
     price_in_btc[ altcoin ].append(float(coin["Last"]))
  except:
    print("Warning: unknown error")
    fetch_from_bitrex()

def convert_all():
 for asset in price_in_cny :
  for i in price_in_cny[ asset ] :
   for j in price_in_cny[ "BTSX" ] :
    if asset not in price_in_btsx : price_in_btsx[ asset ] = []
    price_in_btsx[asset].append(float("%.5g" % float( j/i)))

 for asset in price_in_btc :
  for i in price_in_btc[ asset ] :
   for j in price_in_btc[ "BTSX" ] :
    if asset not in price_in_btsx : price_in_btsx[ asset ] = []
    price_in_btsx[asset].append(float("%.5g" % float(j/i)))

 for asset in price_in_usd :
  for i in price_in_usd[ asset ] :
   for j in price_in_usd[ "BTSX" ] :
    if asset not in price_in_btsx : price_in_btsx[ asset ] = []
    price_in_btsx[asset].append(float("%.5g" % float( j/i)))
 
def get_btc_to_fiat():
 try:
  url = "https://api.bitcoinaverage.com/ticker/USD/"
  response = requests.get(url=url, headers=headers)
  result = response.json()
  priceBTC = float(result["24h_avg"])
  for b in price_in_btsx["BTC"] :
   price_in_btsx["USD"].append(b*priceBTC)

  url = "https://api.bitcoinaverage.com/ticker/EUR/"
  response = requests.get(url=url, headers=headers)
  result = response.json()
  priceBTC = float(result["24h_avg"])
  for b in price_in_btsx["BTC"] :
   price_in_btsx["EUR"].append(b*priceBTC)

  url = "https://api.bitcoinaverage.com/ticker/CNY/"
  response = requests.get(url=url, headers=headers)
  result = response.json()
  priceBTC = float(result["24h_avg"])
  for b in price_in_btsx["BTC"] :
   price_in_btsx["CNY"].append(b*priceBTC)
 except:
   print("Warning: unknown error, try again after 1 seconds")
   time.sleep(1)
   get_btc_to_fiat()

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
  headers = {'content-type': 'application/json'}
  request = {
    "method": "blockchain_market_order_book",
    "params": [asset, "BTSX", 100],
    "jsonrpc": "2.0", "id": 1 }
  response = requests.post(url, data=json.dumps(request), headers=headers, auth=auth)
  result = response.json()
  #currprice[asset] = 0.0 # init offline markets
  #for os in result["result"] :
  # for o in os :
  #  if (o["type"]=="bid_order") :
  #   ratio = float(o["market_index"]["order_price"]["ratio"])
  #   currprice[asset] = ratio * assetprecision[asset]/assetprecision["BTSX"]
  ##############################
  headers = {'content-type': 'application/json'}
  request = {
    "method": "blockchain_get_feeds_for_asset",
    "params": [asset],
    "jsonrpc": "2.0", "id": 1 }
  response = requests.post(url, data=json.dumps(request), headers=headers, auth=auth)
  result = response.json()
  price_median_wallet[asset] = 0.0
  for feed in result["result"] :
   if feed["delegate_name"] == "MARKET":
    price_median_wallet[asset] = float(feed["median_price"])
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
   oldfeeds[ f[ "asset_symbol" ] ] = f[ "price" ]
   oldtime[ f[ "asset_symbol" ] ] = datetime.strptime(f["last_update"],"%Y%m%dT%H%M%S") # all feeds are published at the same time!
 ##############################

def publish_rule():
 #################
 # if REAL_PRICE < MEDIAN and YOUR_PRICE > MEDIAN publish price
 # if you haven't published a price in the past 20 minutes
 #  if REAL_PRICE > MEDIAN and YOUR_PRICE < MEDIAN and abs( YOUR_PRICE - REAL_PRICE ) / REAL_PRICE > 0.005 publish price
 # The goal is to force the price down rapidly and allow it to creep up slowly.
 # By publishing prices more often it helps market makers maintain the peg and minimizes opportunity for shorts to sell USD below the peg that the market makers then have to absorb.
 # If we can get updates flowing smoothly then we can gradually reduce the spread in the market maker bots.
 # *note: all prices in USD per BTSX
 # if you haven't published a price in the past 20 minutes, and the price change more than 0.5%
 #################
 # YOUR_PRICE = Your current published price.                    = oldfeeds[asset]
 # REAL_PRICE = Lowest of external feeds                         = currprice[asset]
 # MEDIAN = current median price according to the blockchain.    = price_median_wallet[asset]
 #################

 for asset in asset_list_publish :
  if (datetime.utcnow()-oldtime[asset]).total_seconds() > maxAgeFeedInSeconds :
   print("Feeds for %s too old! Force updating!" % asset)
   return True
  elif currprice[asset] < price_median_wallet[asset] and \
        oldfeeds[asset] > price_median_wallet[asset]:
   print("External price move for %s: currprice(%f) < feedmedian(%f) and newprice(%f) > feedmedian(%f) Force updating!"\
          % (asset,currprice[asset],price_median_wallet[asset],currprice[asset],price_median_wallet[asset]))
   return True
  elif fabs(oldfeeds[asset]-currprice[asset])/currprice[asset] > change_min and\
       (datetime.utcnow()-oldtime[asset]).total_seconds() > maxAgeFeedInSeconds > 20*60:
   print("New Feeds differs too much for %s %.2f > %.2f! Force updating!" \
          % (asset,fabs(oldfeeds[asset]-currprice[asset]), change_min))
   return True
 ## default: False
 return False

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

## Initialization ###################################
price_in_cny          = {}
price_in_usd          = {}
price_in_btc          = {}
price_in_eur          = {}
price_in_btsx         = {}
price_in_btsx_average = {}
oldfeeds              = {}
price_median_wallet   = {}
currprice             = {}
assetprecision        = {}
assetprecision["BTSX"] = 1e5
oldtime               = {}
for asset in asset_list_all : 
 price_in_btsx_average[asset] = 0.0
 oldfeeds[asset]              = 0.0
 price_median_wallet[asset]   = 0.0
 currprice[asset]             = 0.0
 oldtime[asset]               = datetime.utcnow()

## Get prices and stats #############################
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
print("converting btc to USD/CNY/EUR")
convert_all()
print("Load btc to fiat")
get_btc_to_fiat()

for asset in asset_list_all : 
 # REAL_PRICE = Lowest of external feeds
 currprice[asset] = min( price_in_btsx[asset] )

## Discount!!
asset_list_final = []
for asset in asset_list_publish :
 if len(price_in_btsx[asset]) > 0 :
  ### Median + Discount !!!
  price_in_btsx_average[asset] = statistics.median(price_in_btsx[asset])/discount
  if price_in_btsx_average[asset] > 0.0:
   asset_list_final.append([ asset, price_in_btsx_average[asset] ])
   print("{0}: new price: {1:>10.5f} (change my old: {2:+5.2f}%) (change to curr. median: {3:+5.2f}%) (my feed is {4!s})".format(\
              asset,price_in_btsx_average[asset],\
              (price_in_btsx_average[asset]-oldfeeds[asset])           *100,
              (price_in_btsx_average[asset]-price_median_wallet[asset])*100,\
              str(datetime.utcnow()-oldtime[asset]) ))
if publish_rule() :
 update_feed(asset_list_final, payaccount)
