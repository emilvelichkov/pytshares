#!/usr/bin/python
import csv
import os
from btsrpcapi import *
import config

rpcLOCAL  = btsrpcapi(config.url, config.user, config.passwd)
rpcREMOTE = btsrpcapi(config.backupurl, config.backupuser, config.backuppasswd)

def checkmissedblocks() :
 misschange = 0
 with open(os.getenv("HOME") + '/pytshares/missedblocks.csv', 'rb') as csvfile:
  spamreader = csv.reader(csvfile, delimiter=':')
  for row in spamreader:
   name      = row[0]
   oldmissed = int(row[1])
   a         = json.loads(rpcLOCAL.getaccount(name))
   newmissed = int(a["result"]["delegate_info"]["blocks_missed"])
   misschange += newmissed - oldmissed
  if misschange >= 2 :
    print "disabling main block production"
    print "open"    + rpcREMOTE.walletopen("delegate")
    print "disable" + rpcREMOTE.disableblockproduction("ALL")
    print "lock"    + rpcREMOTE.lock()

    print "enabling backup block production"
    print "open"    + rpcLOCAL.walletopen("delegate")
    print "enable"  + rpcLOCAL.enableblockproduction("ALL")
    print "unclock" + rpcLOCAL.unlock(config.backupunlock)
    print "network" + rpcLOCAL.setnetwork(120,200)
 updatemissedblocks()

def updatemissedblocks() :
 f = open(os.getenv("HOME") + '/pytshares/missedblocksnew.csv', 'wb')
 w = csv.writer(f, delimiter=':')
 with open(os.getenv("HOME") + '/pytshares/missedblocks.csv', 'rb') as csvfile:
  spamreader = csv.reader(csvfile, delimiter=':')
  for row in spamreader:
   name      = row[0]
   a         = json.loads(rpcLOCAL.getaccount(name))
   newmissed = int(a["result"]["delegate_info"]["blocks_missed"])
   w.writerow([name, newmissed])
 f.close()
 os.rename(os.getenv("HOME") + '/pytshares/missedblocksnew.csv', os.getenv("HOME") + '/pytshares/missedblocks.csv')

if __name__ == "__main__":
 checkmissedblocks()
