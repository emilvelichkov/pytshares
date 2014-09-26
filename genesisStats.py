#!/usr/bin/python3

import json
from pprint import pprint
from datetime import datetime
from prettytable import PrettyTable
import statistics
from numpy import *
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from numpy.random import randn
from matplotlib.ticker import FuncFormatter

# The supply in the genesis_btsx.json is BIPS  (1billion with a precision of 10e6)  
# dividing by 5x10e5 adjusts the BIPS to 2 billion BTSX supply.
correctionTerm = 500000.0
supply         = 2e9
n              = 10
nBins          = 5000

with open('genesis.json', 'rt') as f:
 stakes = [ i[1]/correctionTerm for i in json.load(f)['balances']]
sortedStakes = sorted( stakes )
maxValue     = np.ceil(np.log10(sortedStakes[-1]))

print("-"*80)
print("top %d addresses collective percentage"%n)
print("-"*80)
for i in range ( 1, 10 ) :
    myNum = sum(sortedStakes[ -i: ])
    print( "top {0:>4,} addresses collectively own {1:>15,.0f} BTSX ({2:>6.2f}%)".format(i,myNum,myNum/supply*100))

print("-"*80)
print("top %d addresses individual percentage"%n)
print("-"*80)
for i in range ( 1, n ) :
    myNum = sortedStakes[-i]
    print( "top {0:>4,} addresse individually owns {1:>15,.0f} BTSX ({2:>6.2f}%)".format(i,myNum,myNum/supply*100))

print("-"*80)
print("address/amount distribution")
print("-"*80)
listOfAmounts = []
for i in range( 1, int(maxValue+1)):
 listOfAmounts.append(1*pow(10,i))
 listOfAmounts.append(3*pow(10,i))
 listOfAmounts.append(5*pow(10,i))
 listOfAmounts.append(7*pow(10,i))
 listOfAmounts.append(9*pow(10,i))

for i in listOfAmounts :
 num = len([t for t in sortedStakes if t>i])
 if num<=0 : break
 print( "address with >{0:>15,} BTSX : {1:>8,}".format(i, num) )

n, bins = np.histogram((stakes), nBins)
plt.figure()
plt.autoscale(tight=1,axis='both',enable=1)
plt.grid(which='both')
plt.xlabel('address index')
plt.ylabel('stake/address')
plt.semilogy( sort( stakes ) )
plt.savefig('stakeperaddressindex.png')
#plt.show()

plt.figure()
plt.autoscale(tight=1,axis='both',enable=1)
plt.grid(which='both')
plt.xlabel('stake/address')
plt.ylabel('histogram')
plt.semilogx(bins[1:nBins],n[1:nBins])
plt.savefig('histogram.png')
#plt.show()

plt.figure()
plt.autoscale(tight=1,axis='both',enable=1)
plt.grid(which='both')
plt.xlabel('stake/address')
plt.ylabel('cumulative distribution')
plt.semilogx(bins[1:nBins],cumsum(n)[1:nBins])
plt.savefig('cdf.png')
#plt.show()
