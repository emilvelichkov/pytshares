#!/usr/bin/python
import csv
import os
from btsrpcapi import *
import config

rpcLOCAL   = btsrpcapi(config.url, config.user, config.passwd)
rpcREMOTE  = btsrpcapi(config.backupurl, config.backupuser, config.backuppasswd)

def enable( ) :
    print "enabling remote block production"
    print rpcREMOTE.getstatus()
    print rpcREMOTE.walletopen("delegate")
    rpcREMOTE.enableblockproduction("ALL")
    print rpcREMOTE.unlock(config.backupunlock)
    print rpcREMOTE.setnetwork(120,200)

    print "disabling local block production"
    print rpcLOCAL.getstatus()
    print rpcLOCAL.walletopen("delegate")
    print rpcLOCAL.lock()
    rpcLOCAL.disableblockproduction("ALL")

if __name__ == "__main__":
 enable(  )
