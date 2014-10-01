#!/usr/bin/python
from btsrpcapi import *
import config

trusted = [
"a.delegate.charity",
"alecmenconi",
"angel.bitdelegate",
"b.delegate.charity",
"bdnoble",
"bitcoiners",
"bitsuperlab.gentso",
"bts.coin",
"chinese",
"clout-delegate1",
"del.coinhoarder",
"dele-puppy",
"delegate.baozi",
"delegate.charity",
"delegate.jabbajabba",
"delegate.liondani",
"delegate.nathanhourt.com",
"delegate.svk31",
"delegate.xeldal",
"delegate1.john-galt",
"forum.lottocharity",
"happyshares",
"luckybit",
"maqifrnswa",
"mr.agsexplorer",
"riverhead-del-server-1",
"skyscraperfarms",
"spartako",
"testz",
"titan.crazybit",
]

untrusted = [ 
"anchor.crazybit",
"bitsharesx-delegate",
"cny.bts500",
"crazybit",
"d.dacsun",
"daslab",
"dc-delegate",
"delegate.adam",
"delegate.nathanhourt.com",
"delegate2.adam",
"delegated-proof-of-steak",
"do-you-even-dpos",
"dpos.crazybit",
"eur.bts500",
"titan.crazybit",
]

if __name__ == "__main__":
 rpc = btsrpcapi(config.url, config.user, config.passwd)
 print rpc.walletopen(config.wallet)


 # unapprove ALL
 r = json.loads(rpc.walletallgetaccounts())
 accounts = r["result"]
 for account in accounts :
  print rpc.unapprovedelegate(account["name"])

 print rpc.unlock(config.unlock)
 for d in trusted :
  print rpc.approvedelegate(d)
 for d in untrusted :
  print rpc.disapprovedelegate(d)

