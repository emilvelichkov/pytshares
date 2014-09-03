#!/usr/bin/python
from btsrpcapi import *
import config

#######################################
delegates = [ 
             "delegate.charity",
             "a.delegate.charity",
             "b.delegate.charity",
             "c.delegate.charity",
             "d.delegate.charity",
             "e.delegate.charity",
             "f.delegate.charity",
            ]
payee = "payouts.charity"
payrate = 100
########################################
#delegates = [ 
#             "delegate.xeroc",
#             "a.delegate.xeroc",
#             "b.delegate.xeroc",
#             "c.delegate.xeroc",
#             "d.delegate.xeroc",
#             "e.delegate.xeroc",
#             "f.delegate.xeroc",
#            ]
#payee = "delegate.xeroc"
#payrate = 80
########################################


if __name__ == "__main__":
 rpc = btsrpcapi(config.url, config.user, config.passwd)
 print rpc.walletopen("delegate")
 print rpc.unlock(config.unlock)
 for d in delegates :
     print rpc.updatereg( d, payee, {"version":"0.4.11"}, payrate)
