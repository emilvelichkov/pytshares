#!/usr/bin/python
from datetime import datetime,timedelta
from btsrpcapi import *
import config
import sys

confirmationTime = timedelta( seconds=10 )

if __name__ == "__main__":
     rpc = btsrpcapi(config.url, config.user, config.passwd)
     print( rpc.getstatus(  ) )
     status = json.loads(rpc.getstatus())
     blockhead = status[ "result" ][ "blockchain_head_block_num" ]
     block = json.loads(rpc.rpcexec({
       "method": "blockchain_get_block",
       "params": [blockhead],
       "jsonrpc": "2.0",
       "id": 0
       }))
     nowtime = datetime.strptime(block[ "result" ][ "timestamp" ],"%Y%m%dT%H%M%S")
     blockNum = int(sys.argv[ 1 ])
     print("block %d to appear in <= %s" % (blockNum,str(confirmationTime*(blockNum-blockhead))))
     print("UTC time: %s" % str(nowtime+confirmationTime*(blockNum-blockhead)))
