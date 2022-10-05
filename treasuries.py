from packages import *
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 25 01:26:19 2022

@author: lorenzo
"""

from packages import *

# us-bond-rates
rates = ['^IRX','^FVX','^TNX','^TYX']

data = yahoo.download(rates,period='10y')['Adj Close'].fillna(method='ffill')


fig = plt.figure(figsize=(20,12))
ax1 = fig.add_subplot(111)
data.tail(200).plot(ax=ax1, lw=4.)
ax1.set_title('US Treasury-Rates', fontsize=50, fontweight='bold')
ax1.grid(True,color='k',linestyle='-.',linewidth=1)
ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize=40)
plt.xticks(size=30)
plt.yticks(size=30)
plt.savefig('us-rates.png',bbox_inches='tight')

