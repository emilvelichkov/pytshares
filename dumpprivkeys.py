#!/usr/bin/python

from btsrpcapi import *
import config
  
if __name__ == "__main__":
 rpc = btsrpcapi(config.url, config.user, config.passwd)
 print rpc.getstatus()
 print rpc.walletopen("delegat")
 rpc.unlock()
 r = json.loads(rpc.walletgetaccounts())
 accounts = r["result"]
 print "---------------------------------------------------------------------------------"
 for account in accounts :
  print "%20s - %s - %s" % (account["name"], account["owner_key"], walletdumpprivkey(account["owner_key"]))
 print "---------------------------------------------------------------------------------"
 print rpc.lock()
