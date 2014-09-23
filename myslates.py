#!/usr/bin/python
from btsrpcapi import *
import config

trusted = [
"a.delegate.charity",
"alecmenconi",
"angel.bitdelegate",
"b.delegate.charity",
"bdnoble",
"bitsuperlab.gentso",
"clout-delegate1",
"d.dacsun",
"daslab",
"dele-puppy",
"delegate.baozi",
"delegate.charity",
"delegate.coinhoarder",
"delegate.jabbajabba",
"delegate.liondani",
"delegate.svk31",
"delegate1-galt",
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
"delegate.nathanhourt.com",
"bitcoiners",
"chinese",
"bts.coin",
]

if __name__ == "__main__":
 rpc = btsrpcapi(config.url, config.user, config.passwd)
 print rpc.walletopen(config.wallet)
 print rpc.unlock(config.unlock)
 for d in trusted :
  print rpc.approvedelegate(d)
