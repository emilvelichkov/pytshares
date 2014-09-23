#!/usr/bin/env python
# coding=utf8

import requests
import json
import sys

import datetime, threading, time
from pprint import pprint

headers = {'content-type': 'application/json',
   'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}

payaccount = "delegate.xeroc"

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
asset_list_all = ["PTS", "PPC", "LTC", "BTC", "WTI", "SLV", "GLD", "TRY", "SGD", "HKD", "RUB", "SEK", "NZD", "CNY", "MXN", "CAD", "CHF", "AUD", "GBP", "JPY", "EUR", "USD"]
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
   print "%s" % (response.text)
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
   print "%s" % (response.text)
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
    price_in_usd[ bitassetname(a.upper()) ].append(float(yahooprices[i-1]))
   ##########################
   yahooAssets = ",".join(["CNY"+a+"=X" for a in availableAssets])
   url="http://download.finance.yahoo.com/d/quotes.csv"
   params = {'s':yahooAssets,'f':'l1','e':'.csv'}
   response = requests.get(url=url, headers=headers,params=params)
   yahooprices =  response.text.split( '\r\n' )
   for i,a in enumerate(availableAssets,1) :
    if bitassetname(a.upper()) not in price_in_cny : price_in_cny[ bitassetname(a.upper()) ] = []
    price_in_cny[ bitassetname(a.upper()) ].append(1/float(yahooprices[i-1])) ## FIXME WTF!?!?!?!
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
   print "Warning: unknown error, try again after 1 seconds"
   time.sleep(1)
   get_rate_from_yahoo()

def fetch_from_bter():
  url="http://data.bter.com/api/1/tickers"
  try :
   response = requests.get(url=url, headers=headers)
   result = response.json()

   availableAssets = [ "BTSX", "LTC", "BTSX", "PTS", "PPC" ]
   for coin in availableAssets :
    if coin not in price_in_btc : price_in_btc[ coin ] = []
    price_in_btc[ coin ].append(float(result[coin.lower()+"_btc"]["last"]))

   availableAssets = [ "BTSX", "BTC", "LTC", "BTSX", "PTS", "PPC" ]
   for coin in availableAssets :
    if coin not in price_in_cny : price_in_cny[ coin ] = []
    price_in_cny[ coin ].append(float(result[coin.lower()+"_cny"]["last"]))
  except: 
    print "Warning: unknown error, try again after 1 seconds"
    time.sleep(1)
    fetch_from_bter()

def fetch_from_poloniex():
  try:
   url="https://poloniex.com/public?command=returnTicker"
   response = requests.get(url=url, headers=headers)
   result = response.json()
   availableAssets = [ "LTC", "BTSX", "PTS", "PPC" ]
   price_in_btsx["BTC"].append(float(result["BTC_BTSX"]["last"]))
   for coin in availableAssets :
    if coin not in price_in_btc : price_in_btc[ coin ] = []
    price_in_btc[ coin ].append(float(result["BTC_"+coin.upper()]["last"]))
  except: 
   print "Warning: unknown error, try again after 1 seconds"
   time.sleep(1)
   fetch_from_poloniex()

# def fetch_from_bitrex():
#   availableAssets = [ "BTSX", "LTC", "BTSX", "PTS", "PPC" ]
#   try:
#    url="https://bittrex.com/api/v1.1/public/getmarketsummaries"
#    response = requests.get(url=url, headers=headers)
#    result = response.json()["result"]
#    for coin in availableAssets :
#     if coin not in price_in_btc : price_in_btc[ coin ] = []
#     price_in_btc[ coin ].append(float(result["BTC-"+coin.upper()]["Last"]))
#   except:
#     print "Warning: unknown error"
#     return

def convert_all():
  for asset in price_in_cny :
   for i in price_in_cny[ asset ] :
    for j in price_in_cny[ "BTSX" ] :
     if asset not in price_in_btsx : price_in_btsx[ asset ] = []
     price_in_btsx[asset].append(float("%.3g" % float( j/i)))

  for asset in price_in_btc :
   for i in price_in_btc[ asset ] :
    for j in price_in_btc[ "BTSX" ] :
     if asset not in price_in_btsx : price_in_btsx[ asset ] = []
     price_in_btsx[asset].append(float("%.3g" % float(j/i)))

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



def update_feed(assets):
  for delegate in delegate_list:
        headers = {'content-type': 'application/json'}
        request = {
            "method": "wallet_publish_feeds",
            "params": [delegate, assets, payaccount],
            "jsonrpc": "2.0",
            "id": 1
            }
        while True:
          try:
            response = requests.post(url, data=json.dumps(request), headers=headers, auth=auth)
            result = response.json()
            print "Update:", delegate, assets, result
          except:
            print "Warnning: Can't connect to rpc server, retry 5 seconds later"
            time.sleep(5)
            continue
          break

price_in_cny = {}
price_in_usd = {}
price_in_btc = {}
price_in_eur = {}
price_in_btsx    = {}
price_in_btsx_average = {}

for asset in asset_list_all :
 price_in_btsx[asset] = []
 price_in_cny[asset]  = []
 price_in_usd[asset]  = []
 price_in_btc[asset]  = []
 price_in_eur[asset]  = []
 price_in_btsx_average[asset] = 0.0

print "Loading Yahoo"
fetch_from_yahoo()
print "Loading BTC38"
fetch_from_btc38()
print "Loading BTer"
fetch_from_bter()
print "Loading Poloniex"
fetch_from_poloniex()
# print "Loading bitrex"
# fetch_from_bitrex()
print "converting btc to USD/CNY/EUR"
convert_all()

# pprint( price_in_btc  )
# pprint( price_in_usd  )
# pprint( price_in_eur  )
# pprint( price_in_cny  )
# pprint( price_in_btsx )

asset_list_final = []
for asset in asset_list_publish:
 if len(price_in_btsx[asset]) > 0 :
  price_in_btsx_average[asset] = sum(price_in_btsx[asset])/len(price_in_btsx[asset])
  if price_in_btsx_average[asset] > 0.0:
    asset_list_final.append([ asset, price_in_btsx_average[asset] ])
update_feed(asset_list_final)
