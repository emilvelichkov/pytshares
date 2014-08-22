#!/usr/bin/python
from btsrpcapi import *
import config
import re

payouttarget = "xeroc"

if __name__ == "__main__":
 rpc = btsrpcapi(config.url, config.user, config.passwd)
 withdrawfee = 0.1 * 1e5;
 print rpc.getstatus()
 print rpc.walletopen("delegate")
 rpc.disableblockproduction("ALL")
 print rpc.unlock()
 r = json.loads(rpc.walletgetaccounts())
 accounts = r["result"]
 for account in accounts :
  if  not re.match(".*charity.*", account["name"]) :
   if account["delegate_info"] :
    if account["delegate_info"]["pay_balance"] > withdrawfee:
     payout = float(account["delegate_info"]["pay_balance"]) - withdrawfee
     print "%20s -- %20.5f -- %20.5f" % (account["name"], account["delegate_info"]["pay_balance"]/1.0e5, payout/1.0e5)
     #print rpc.withdrawdelegatepay(account["name"],payouttarget,payout/1.0e5) 
 print rpc.lock()
