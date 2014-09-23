#!/usr/bin/python
import csv
import os
from btsrpcapi import *
import config

rpc2  = btsrpcapi(config.backupurl, config.backupuser, config.backuppasswd)
rpc  = btsrpcapi(config.mainurl, config.mainuser, config.mainpasswd)

def enable( ) :
    print "enabling backup block production"
    print rpc2.getstatus()
    print rpc2.walletopen("delegate")
    rpc2.enableblockproduction("ALL")
    print rpc2.unlock(config.backupunlock)
    print rpc2.setnetwork(25,30)

    print "disabling main block production"
    print rpc.getstatus()
    print rpc.walletopen("delegate")
    print rpc.lock()
    rpc.disableblockproduction("ALL")

if __name__ == "__main__":
 enable(  )
