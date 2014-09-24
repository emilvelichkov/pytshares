#!/usr/bin/python3
from btsrpcapi import *
import config
from pprint import pprint
from datetime import datetime
from prettytable import PrettyTable
import statistics

numDelegates = 110

if __name__ == "__main__":
 delegatefeeds = []
 feedprice = { }
 currenttime = datetime.utcnow()
 rpc = btsrpcapi(config.url, config.user, config.passwd)
 delegates = json.loads(rpc.listdelegates( 1,numDelegates ))
 for top,delegate in enumerate(delegates["result"],1) :
  feeds = (json.loads(rpc.getdelfeeds(delegate["name"]))["result"])
  numfeeds = len(feeds)
  validfeed = []
  for feed in feeds :
   feedtime = datetime.strptime(feed["last_update"],"%Y%m%dT%H%M%S")
   delta    = (currenttime-feedtime)
   if feed[ "asset_symbol" ] not in feedprice : feedprice[ feed["asset_symbol"] ] = [  ]
   feedprice[ feed["asset_symbol"] ].append(feed[ "price" ])
   if delta.total_seconds()/60/60/24 < 1.0 :
    validfeed.append(feed["asset_symbol"])
  delegatefeeds.append({
                        "name" : str(delegate["name"]),
                        "numValidFeeds":len(validfeed),
                        "feeds": feeds,
                        "top": top
                       })

 #data_sorted = sorted(delegatefeeds, key=lambda item: item['numValidFeeds'])
 t = PrettyTable(["asset", "mean", "std", "median"]) 
 t.align                   = 'l'                                                                                                                                                                                                    
 t.border                  = True
 t.float_format['mean']    = ".10"
 t.float_format['median']  = ".10"
 t.float_format['std']     = ".10"
 medianPrice = {}
 for a in feedprice :
  t.add_row([a, statistics.mean(feedprice[a]), statistics.stdev(feedprice[a]), statistics.median(feedprice[a])])
  medianPrice[ a ] = statistics.median(feedprice[a])
 print(t.get_string(sortby="std", reversesort=False))

 ## General Statistics ##############################
 t2 = PrettyTable(["delegate","top","numFeeds", "asset"]) 
 t2.align                   = 'l'                                                                                                                                                                                                    
 t2.border                  = True
 for p in delegatefeeds : 
  for a in p[ "feeds" ] : 
   assetstr = "%s (off by:%.3f%%)" % (a["asset_symbol"], 100*abs(a[ "price" ]-medianPrice[ a[ "asset_symbol" ]]))
   t2.add_row([p["name"], p["top"], p["numValidFeeds"], assetstr ])

 #print(t2.get_string(sortby="numFeeds", reversesort=True))
 print(t2.get_string(sortby="top", reversesort=False))
