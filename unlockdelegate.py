#!/usr/bin/python
from btsrpcapi import *
import config

if __name__ == "__main__":
 rpc = btsrpcapi(config.url, config.user, config.passwd)
 print rpc.getstatus()
 print rpc.walletopen("delegate")
 print rpc.unlock()
 print rpc.setnetwork(120,200)
 rpc.enableblockproduction("ALL")
