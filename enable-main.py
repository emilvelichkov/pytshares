#!/usr/bin/python
import csv
import os
from btsrpcapi import *
import config

rpc = btsrpcapi(config.backupurl, config.backupuser, config.backuppasswd)
rpc2  = btsrpcapi(config.url, config.user, config.passwd)

def enable( ) :
    print "enabling backup block production"
    print rpc2.getstatus()
    print rpc2.walletopen("delegate")
    rpc2.enableblockproduction("ALL")
    print rpc2.unlock(config.unlock)
    print rpc2.setnetwork(120,200)

    print "disabling main block production"
    print rpc.getstatus()
    print rpc.lock()
    rpc.disableblockproduction("ALL")

if __name__ == "__main__":
 enable(  )
