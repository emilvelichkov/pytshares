#!/usr/bin/python
from datetime import datetime,timedelta
import sys

genesisTimeStamp = "20140719T031850"
genesisTime = datetime.strptime("20140719T031850","%Y%m%dT%H%M%S")
confirmationTime = timedelta( seconds=10 )

if __name__ == "__main__":
 blockNum = int(sys.argv[ 1 ])-1
 print(str(genesisTime+confirmationTime*blockNum)+" UTC")
