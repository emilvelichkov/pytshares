#!/usr/bin/python
from btsrpcapi import *
import config

if __name__ == "__main__":
        rpc = btsrpcapi(config.url, config.user, config.passwd)
        print rpc.getstatus()
        print rpc.walletopen("delegate")
        print rpc.rpcexec({
            "method": "wallet_account_transaction_history",
            "params": [],
            "jsonrpc": "2.0",
            "id": 0
         })
