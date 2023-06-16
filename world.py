from packages import *

coins = ['EURUSD=X','GBPUSD=X','CHFUSD=X','CNYUSD=X','JPYUSD=X','BRLUSD=X','AUDUSD=X','CADUSD=X','NZDUSD=X']
coins += ['DX-Y.NYB', 'GC=F']
data = yahoo.download(coins, period='1y')['Adj Close'].fillna(method='ffill')

fig = plt.figure(figsize=(40,25))
ax1 = fig.add_subplot(111)
data[['DX-Y.NYB', 'GC=F']].pct_change().cumsum().plot(ax=ax1, lw=7.,c='k')
data.pct_change().cumsum().plot(ax=ax1, lw=4.)
ax1.set_title('Coins World', fontsize=50, fontweight='bold')
ax1.grid(True,color='k',linestyle='-.',linewidth=2)
ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize=40)
plt.xticks(size=30, rotation=45)
plt.yticks(size=40, rotation=45)
plt.savefig('coinsWWW.png',bbox_inches='tight')

commodities = pd.read_html('https://finance.yahoo.com/commodities')[0]
#tickets = dict(zip(commodities.Symbol.to_list(),commodities.Name.to_list()))
#tickets = commodities.sort_values('Symbol',ascending=True)
comm = yahoo.download(commodities['Symbol'].to_list(),period='1y')['Adj Close']
names = commodities.Name.to_list()
comm = comm[commodities.Symbol.to_list()]
comm.columns = commodities.Name.to_list()

# us market index
fig = plt.figure(figsize=(40,25))
ax1 = fig.add_subplot(111)
comm[names[:4]].pct_change().cumsum().plot(ax=ax1, lw=4.)
ax1.set_title('US Market Index', fontsize=150, fontweight='bold')
ax1.grid(True,color='k',linestyle='-.',linewidth=2)
ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize=45)
plt.xticks(size=50, rotation=45)
plt.yticks(size=60, rotation=45)
plt.savefig('usindex.png',bbox_inches='tight')

fig = plt.figure(figsize=(40,25))
ax1 = fig.add_subplot(111)
comm[names[4:8]].pct_change().cumsum().plot(ax=ax1, lw=4.)
ax1.set_title('US Bond Market', fontsize=150, fontweight='bold')
ax1.grid(True,color='k',linestyle='-.',linewidth=2)
ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize=45)
plt.xticks(size=50, rotation=45)
plt.yticks(size=60, rotation=45)
plt.savefig('usbonds.png',bbox_inches='tight')

fig = plt.figure(figsize=(40,25))
ax1 = fig.add_subplot(111)
comm[names[8:15]].pct_change().cumsum().plot(ax=ax1, lw=4.)
ax1.set_title('Metals', fontsize=150, fontweight='bold')
ax1.grid(True,color='k',linestyle='-.',linewidth=2)
ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize=45)
plt.xticks(size=50, rotation=45)
plt.yticks(size=60, rotation=45)
plt.savefig('metals.png',bbox_inches='tight')

fig = plt.figure(figsize=(40,25))
ax1 = fig.add_subplot(111)
comm[names[15:20]].pct_change().cumsum().plot(ax=ax1, lw=4.)
ax1.set_title('Oil & Gas', fontsize=150, fontweight='bold')
ax1.grid(True,color='k',linestyle='-.',linewidth=2)
ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize=45)
plt.xticks(size=50, rotation=45)
plt.yticks(size=60, rotation=45)
plt.savefig('oilngas.png',bbox_inches='tight')


fig = plt.figure(figsize=(40,25))
ax1 = fig.add_subplot(111)
comm[names[20:]].pct_change().cumsum().plot(ax=ax1, lw=4.)
ax1.set_title('Food Chain', fontsize=150, fontweight='bold')
ax1.grid(True,color='k',linestyle='-.',linewidth=2)
ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize=45)
plt.xticks(size=50, rotation=45)
plt.yticks(size=60, rotation=45)
plt.savefig('foodchain.png',bbox_inches='tight')
