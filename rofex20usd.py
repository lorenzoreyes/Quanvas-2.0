import pandas as pd
import yfinance as yahoo
import matplotlib.pyplot as plt
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context
    #from pytickersymbols import PyTickerSymbols #https://pypi.org/project/pytickersymbols/

# obtain the sixth table of the page, with all data of the current Rofex20    
rofex = pd.read_html('https://www.rofex.com.ar/cem/CarteraVigenteROFEX20')[6] 

lista = list(rofex['Instrumento'].values)
lista = [i + '.BA' for i in lista]

data = yahoo.download(lista,period="1y",interval="60m")["Adj Close"].fillna(method="ffill")
cartera = pd.DataFrame((data * (rofex.Cantidad.values / 1000000)).T.sum(),columns=['Rofex20Vigente'],index=data.index)

time, duration = "1y", "60m"

stocks = ['AAPL.BA', 'BBD.BA', 'MELI.BA', 'KO.BA', 'INTC.BA', 'VALE.BA',
       'TSLA.BA', 'WFC.BA', 'XOM.BA', 'AMZN.BA', 'BABA.BA', 'T.BA', 'MSFT.BA',
       'GE.BA', 'WMT.BA', 'HMY.BA', 'PFE.BA', 'ERJ.BA', 'AUY.BA', 'X.BA']

cedears = yahoo.download(stocks, period=time, interval=duration)['Adj Close'].fillna(method='ffill')

ratios = [10,144,1,9,1,1,1,1,5,5,60,10,2,3,15,2,5,6,3,5]

cedears = cedears * ratios  # get stocks prices according to what you have to paid

topba = [s.replace('.BA', 'BA') for s in stocks]

cedears.columns = topba

forex = [i.replace('.BA','') for i in stocks]

df = yahoo.download(forex,period=time, interval=duration)['Adj Close'].fillna(method='ffill')
tc = cedears.div(df.tail(len(cedears)).values)
tc.columns = topba

mediaced = pd.DataFrame(index=tc.index)
mediaced['CableCedears'] = tc.T.median()

rofexusd = pd.DataFrame(cartera.iloc[:,0].values,columns=['rofexUSD'],index=cartera.index)
rofexusd['rofexUSD'] = rofexusd.rofexUSD / mediaced.CableCedears
rofexusd = rofexusd.fillna(method='ffill')

fig = plt.figure(figsize=(30,20))
ax1 = fig.add_subplot(111)
rofexusd.plot(ax=ax1, lw=5., legend=True)
plt.legend(fontsize=20)
ax1.grid(linewidth=2)
plt.title(f'rofexUSD ${round(rofexusd.iloc[-1,0],2)}', fontsize=30, fontweight='bold')
plt.xticks(size = 20)
plt.yticks(size = 20)
plt.show()
