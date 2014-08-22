#!/usr/bin/python
from btsrpcapi import *
import config
import re

payouttarget = "payouts.charity"

if __name__ == "__main__":
 withdrawfee = 0.1 * 1e5;
 print getstatus()
 print walletopen("delegate")
 disableblockproduction("ALL")
 print unlock(config.unlock)
 r = json.loads(walletgetaccounts())
 accounts = r["result"]
 for account in accounts :
  if  re.match(".*charity.*", account["name"]) :
   if account["delegate_info"] :
    if account["delegate_info"]["pay_balance"] > withdrawfee:
     payout = float(account["delegate_info"]["pay_balance"]) - withdrawfee
     print "%20s -- %20.5f -- %20.5f" % (account["name"], account["delegate_info"]["pay_balance"]/1.0e5, payout/1.0e5)
     print withdrawdelegatepay(account["name"],payouttarget,payout/1.0e5) 
 print lock()
