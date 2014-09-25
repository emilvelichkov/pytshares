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

json_data=open("genesis.json").read()
data = json.loads(json_data)

stakes = []
for b in data[ "balances" ] :
    stakes.append( float(b[ 1 ])/1.0e5 )

sumStakesMeas  = np.sum( stakes )
sumStakes      = 2*1e12
correctionTerm = (float( sumStakesMeas/sumStakes ))
print( "Correction term: 1/%7.2f" % (1/correctionTerm) )
stakes         = [ s * correctionTerm for s in stakes ]

sortedStakes = sorted( stakes )
cumulSum     = np.cumsum( sortedStakes )
maxValue     = np.ceil(np.log10(sortedStakes[-1]))
listOfAmounts = []
for i in range( 1, int(maxValue+1)):
 listOfAmounts.append(1*pow(10,i))
 listOfAmounts.append(3*pow(10,i))
 listOfAmounts.append(5*pow(10,i))
 listOfAmounts.append(7*pow(10,i))
 listOfAmounts.append(9*pow(10,i))

for i in listOfAmounts :
 nBelow = len(np.where( cumulSum < i )[ 0 ])
 nAbove = len( stakes ) - nBelow
 print( "address with >{0:>12,} : {1:>8,}".format(i, nAbove) )

nBins = 5000
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
