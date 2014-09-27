#!/usr/bin/python
import csv
import os
from btsrpcapi import *
import config

rpc   = btsrpcapi(config.backupurl, config.backupuser, config.backuppasswd)
rpc2  = btsrpcapi(config.mainurl, config.mainuser, config.mainpasswd)

def enable( ) :
    print "checking connectivity"
    print rpc2.getstatus()
    print rpc.getstatus()

    print "enabling backup block production"
    print rpc2.walletopen("delegate")
    rpc2.enableblockproduction("ALL")
    print rpc2.unlock(config.mainunlock)
    print rpc2.setnetwork(25,30)

    print "disabling main block production"
    print rpc.walletopen("delegate")
    print rpc.lock()
    rpc.disableblockproduction("ALL")

if __name__ == "__main__":
 enable(  )
