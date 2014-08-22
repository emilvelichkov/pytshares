#!/usr/bin/python
import csv
import os
from btsrpcapi import *
import config

rpc = btsrpcapi(config.url, config.user, config.passwd)

def checkmissedblocks() :
 misschange = 0
 with open('/home/coin/pytshares/missedblocks.csv', 'rb') as csvfile:
  spamreader = csv.reader(csvfile, delimiter=':')
  for row in spamreader:
   name      = row[0]
   oldmissed = int(row[1])
   a         = json.loads(rpc.getaccount(name))
   newmissed = int(a["result"]["delegate_info"]["blocks_missed"])
   misschange += newmissed - oldmissed
  if misschange >= 3 :
   print rpc.getstatus()
   print rpc.walletopen("delegate")
   print rpc.unlock(config.unlock)
   print rpc.setnetwork(120,200)
   rpc.enableblockproduction("ALL")
   print "enabling backup block production"
 updatemissedblocks()

def updatemissedblocks() :
 f = open('/home/coin/pytshares/missedblocksnew.csv', 'wb')
 w = csv.writer(f, delimiter=':')
 with open('/home/coin/pytshares/missedblocks.csv', 'rb') as csvfile:
  spamreader = csv.reader(csvfile, delimiter=':')
  for row in spamreader:
   name      = row[0]
   a         = json.loads(rpc.getaccount(name))
   newmissed = int(a["result"]["delegate_info"]["blocks_missed"])
   w.writerow([name, newmissed])
 f.close()
 os.rename('/home/coin/pytshares/missedblocksnew.csv', '/home/coin/pytshares/missedblocks.csv')

if __name__ == "__main__":
 checkmissedblocks()
