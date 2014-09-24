#!/usr/bin/python
from btsrpcapi import *
import config
from pprint import pprint
from datetime import datetime
from prettytable import PrettyTable

if __name__ == "__main__":
 delegatefeeds = []
 currenttime = datetime.utcnow()
 rpc = btsrpcapi(config.url, config.user, config.passwd)
 print rpc.getstatus()
 delegates = json.loads(rpc.listdelegates( 1,150 ))
 for top,delegate in enumerate(delegates["result"],2) :
  feeds = (json.loads(rpc.getdelfeeds(delegate["name"]))["result"])
  numfeeds = len(feeds)
  validfeed = []
  for feed in feeds :
   feedtime = datetime.strptime(feed["last_update"],"%Y%m%dT%H%M%S")
   delta = (currenttime-feedtime)
   if delta.total_seconds()/60/60/24 < 1.0 :
    validfeed.append(feed["asset_symbol"])
  delegatefeeds.append({
                        "name" : str(delegate["name"]),
                        "numValidFeeds":len(validfeed),
                        "feeds": validfeed,
                        "top": top
                       })

 data_sorted = sorted(delegatefeeds, key=lambda item: item['numValidFeeds'])



 t = PrettyTable(["delegate","top","numFeeds"]) 
 t.align                   = 'l'                                                                                                                                                                                                    
 t.border                  = True

 for p in data_sorted : 
  t.add_row([p["name"], p["top"], p["numValidFeeds"]])

 print t.get_string(sortby="numFeeds", reversesort=True)
 print t.get_string(sortby="top", reversesort=False)
