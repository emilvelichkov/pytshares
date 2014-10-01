#!/usr/bin/python
from btsrpcapi import *
import config
import sys

if __name__ == "__main__":
     rpc = btsrpcapi(config.url, config.user, config.passwd)
     tx = sys.argv[1] 
     print rpc.rpcexec({
       "method": "wallet_account_list_public_keys",
       "params": [tx],
       "jsonrpc": "2.0",
       "id": 0
       })
