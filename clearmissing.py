#!/usr/bin/python
import csv
import os
from btsrpcapi import *
import config

def updatemissedblocks() :
 rpc = btsrpcapi(config.url, config.user, config.passwd)
 f   = open('/home/coin/pytshares/missedblocksnew.csv', 'wb')
 w   = csv.writer(f, delimiter                                = ':')
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
 updatemissedblocks()
