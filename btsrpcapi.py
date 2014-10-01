#!/usr/bin/python

import sys, getopt 
import requests
import json
from pprint import pprint
import time
import getpass

class btsrpcapi :
 def __init__(self, url, user, pwd) :
     self.auth    = (user,pwd)
     self.url     = url
     self.headers = {'content-type': 'application/json'}
   
 def rpcexec(self,payload) :
     response = requests.post(self.url, data=json.dumps(payload), headers=self.headers, auth=self.auth)
     r = json.loads(response.text)
     return json.dumps(r,indent=4) #["result"]
     
 def getstatus(self) :
     return self.rpcexec({
        "method": "get_info",
        "params": [],
        "jsonrpc": "2.0",
        "id": 0
     })

 def getbalance(self,name) :
     return self.rpcexec({
        "method": "wallet_account_balance",
        "params": [name],
        "jsonrpc": "2.0",
        "id": 0
     })

 def getassetbalance(self,name,asset) :
     balance = self.rpcexec({
        "method": "wallet_account_balance",
        "params": [name],
        "jsonrpc": "2.0",
        "id": 0
     })
     for b in json.loads(balance)[ "result" ][ 0 ][ 1 ]:
      if b[ 0 ] == asset : return float(b[ 1 ])
     return -1

 def getaccount(self,name) :
     return self.rpcexec({
        "method": "blockchain_get_account",
        "params": [name],
        "jsonrpc": "2.0",
        "id": 0
     })

 def walletcreate(self,name,pwd) :
     return self.rpcexec({
         "method": "wallet_create",
         "params": [name,pwd],
         "jsonrpc": "2.0",
         "id": 0
     })
     
 def walletopen(self,name) :
     return self.rpcexec({
         "method": "wallet_open",
         "params": [name],
         "jsonrpc": "2.0",
         "id": 0
     })

 def unlock(self,key) :
     return self.rpcexec({
         "method": "wallet_unlock",
         "params": ["99999999999", key],
         "jsonrpc": "2.0",
         "id": 0
     })

 def lock(self) :
     return self.rpcexec({
         "method": "wallet_lock",
         "params": [],
         "jsonrpc": "2.0",
         "id": 0
     })

 def importkey(self,key,name) :
     return self.rpcexec({
         "method": "wallet_import_private_key",
         "params": [key, name, "true", "false"],
         "jsonrpc": "2.0",
         "id": 0
     })


 def importkeyonly(self,key) :
     return self.rpcexec({
         "method": "wallet_import_private_key",
         "params": [key],
         "jsonrpc": "2.0",
         "id": 0
     })

 def createaccount(self,name) :
     return self.rpcexec({
         "method": "wallet_account_create",
         "params": [name],
         "jsonrpc": "2.0",
         "id": 0
     })

 def registername(self,name,payee,data,payrate) :
     return self.rpcexec({
         "method": "wallet_account_register",
         "params": [name, payee, data, payrate],
         "jsonrpc": "2.0",
         "id": 0
     })

 def enableblockproduction(self,name) :
     return self.rpcexec({
         "method": "wallet_delegate_set_block_production",
         "params": [name, "true"],
         "jsonrpc": "2.0",
         "id": 0
     })

 def disableblockproduction(self,name) :
     return self.rpcexec({
         "method": "wallet_delegate_set_block_production",
         "params": [name, "false"],
         "jsonrpc": "2.0",
         "id": 0
     })

 def approvedelegate(self,name) :
     return self.rpcexec({
         "method": "wallet_approve_delegate",
         "params": [name, "1"],
         "jsonrpc": "2.0",
         "id": 0
     })

 def unapprovedelegate(self,name) :
     return self.rpcexec({
         "method": "wallet_approve_delegate",
         "params": [name, "0"],
         "jsonrpc": "2.0",
         "id": 0
     })

 def disapprovedelegate(self,name) :
     return self.rpcexec({
         "method": "wallet_approve_delegate",
         "params": [name, "-1"],
         "jsonrpc": "2.0",
         "id": 0
     })

 def walletallgetaccounts(self) :
     return self.rpcexec({
         "method": "wallet_list_accounts",
         "params": [],
         "jsonrpc": "2.0",
         "id": 0
     })

 def walletgetaccounts(self) :
     return self.rpcexec({
         "method": "wallet_list_my_accounts",
         "params": [],
         "jsonrpc": "2.0",
         "id": 0
     })

 def walletdumpprivkey(self,key) :
     r = self.rpcexec({
         "method": "wallet_dump_private_key",
         "params": [key],
         "jsonrpc": "2.0",
         "id": 0
     })
     return json.loads(r)["result"]

 def setnetwork(self,d,m) :
     return self.rpcexec({
         "method": "network_set_advanced_node_parameters",
         "params": [{"desired_number_of_connections":d,
                     "maximum_number_of_connections":m}],
         "jsonrpc": "2.0",
         "id": 0
     })

 def withdrawdelegatepay(self,delegate,target,amount) :
     return self.rpcexec({
         "method": "wallet_delegate_withdraw_pay",
         "params": [delegate, target, amount, "auto pay day"],
         "jsonrpc": "2.0",
         "id": 0
     })
 def orderhistory(self,a,b,l) :
     return self.rpcexec({
         "method": "blockchain_market_order_history",
         "params": [a,b,1,l],
         "jsonrpc": "2.0",
         "id": 0
     })
 def orderbook(self,a,b,l) :
     return self.rpcexec({
         "method": "blockchain_market_order_book",
         "params": [a,b,l],
         "jsonrpc": "2.0",
         "id": 0
     })
 def marketbid(self,fromaccount,quant,qantsymbol,price,basesymol) :
     return self.rpcexec({
         "method": "wallet_market_submit_bid",
         "params": [fromaccount,quant,qantsymbol,price,basesymol],
         "jsonrpc": "2.0",
         "id": 0
     })
 def marketask(self,fromaccount,quant,qantsymbol,price,basesymol) :
     return self.rpcexec({
         "method": "wallet_market_submit_ask",
         "params": [fromaccount,quant,qantsymbol,price,basesymol],
         "jsonrpc": "2.0",
         "id": 0
     })

 def marketstatus(self,a,b) :
     return self.rpcexec({
         "method": "blockchain_market_status",
         "params": [a,b],
         "jsonrpc": "2.0",
         "id": 0
     })

 def updatereg(self,name,payee,data,payrate) :
     return self.rpcexec({
         "method": "wallet_account_update_registration",
         "params": [name, payee, data, payrate],
         "jsonrpc": "2.0",
         "id": 0
     })

 def listdelegates(self,first,limit) :
     return self.rpcexec({
         "method": "blockchain_list_delegates",
         "params": [first, limit],
         "jsonrpc": "2.0",
         "id": 0
     })

 def getdelfeeds(self,delname) :
     return self.rpcexec({
         "method": "blockchain_get_feeds_from_delegate",
         "params": [delname],
         "jsonrpc": "2.0",
         "id": 0
     })
