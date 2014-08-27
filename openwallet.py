#!/usr/bin/python
from btsrpcapi import *
import config

if __name__ == "__main__":
 rpc = btsrpcapi(config.url, config.user, config.passwd)
 rpc.walletopen(config.wallet)
