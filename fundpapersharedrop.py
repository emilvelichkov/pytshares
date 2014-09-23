#!/usr/bin/python
from btsrpcapi import *
import config
import csv
import string
a=string.lowercase

fund = [
  [1, "BTSX"],
  [10000, "FREE"]
  ]
csvfile = "papersharedrop/addresses"

if __name__ == "__main__":
 with open( csvfile, 'rb') as f:
  for i, row in enumerate(csv.reader(f, delimiter=';'), 1):
   for fu in fund :
    name="drop-"+a[i%26]*(i / 26+1)
    print "%f.1 %s xeroc %s" % (float(fu[0]), fu[1], name)
 #rpc = btsrpcapi(config.url, config.user, config.passwd)
 #print rpc.walletopen(config.wallet)
 #print rpc.unlock(config.unlock)
 #print rpc.lock()
