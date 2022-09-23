from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
import yfinance as yahoo 
import pandas as pd, numpy as np
import ssl
import urllib.request
from apiBinance import *

client = Client(API_KEY,API_SECRET)


try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context
    #from pytickersymbols import PyTickerSymbols #https://pypi.org/project/pytickersymbols/


''' functions to get info about each market and their current stock tickets
 markets to operate: USA (Nasdaq & SP500), England, China, Japan, Canada, Brazil, Australia
 the handlers will result with a list of metrics that will be use by main script
 to build respective portfolio

 Steps 
 (1) call an endpoint to gather all proper tickers of that market
 (2) download the data
 (3) generate all the metrics
'''



def metrics(lista):
    df = yahoo.download(lista,period='1y',interval='60m')['Adj Close']
    df = df.sort_index(axis=0,ascending=True)
    df = df.fillna(method='ffill').dropna(axis=1)
    freeRisk = df.T.mean() # self-generated, as using Bitcoin as benchmark is a possibility but will bias the result
    pct = df.pct_change()
    mean = pd.DataFrame(pct.mean(),columns=['Mean'],index=pct.columns)
    riskpct = mean.mean()
    mean_rf = mean - riskpct.mean()
    std = pd.DataFrame(pct.std(),columns=['Std'],index=pct.columns)
    sharpe_ratio = pd.DataFrame(mean_rf['Mean']/(std['Std']), columns=['SharpeRatio'],index=pct.columns)
    orderedsharpe = sharpe_ratio.sort_values('SharpeRatio', axis=0, ascending=False)
    lista = list(orderedsharpe.head(50).index.values)
    df = yahoo.download(lista,period="1y",interval="60m")["Adj Close"].fillna(method="ffill")
    riskfree = df.T.mean().fillna(method='ffill')
    pct = df.pct_change().dropna() #(how='all')
    riskpct = riskfree.pct_change().dropna()
    mean = pd.DataFrame(pct.mean(),columns=['Mean'],index=pct.columns)
    mean_rf = mean - riskpct.mean()
    std = pd.DataFrame(pct.std(),columns=['Std'],index=pct.columns)
    numerator = pct.sub(riskpct,axis=0)
    downside_risk = ((numerator[numerator<0].fillna(0))**2).mean()
    noa = len(df.columns)
    weigths = np.random.random(noa)
    weigths /= np.sum(weigths)
    observations = len(df.index)
    mean_returns = df.pct_change().mean()
    cov = df.pct_change().cov()
    alpha = 0.1
    rf = riskpct.mean()
    num_portfolios = 1000
    Upbound = 0.15
    result = [df,riskfree,pct,riskpct,mean,mean_rf,std,numerator,downside_risk,noa,weigths\
        ,observations,mean_returns,cov,alpha,rf,num_portfolios,Upbound]
    return result

def GSPC():
    lista = pd.read_html("https://topforeignstocks.com/indices/components-of-the-sp-500-index/")[0]
    lista = list(lista.Ticker.values)
    freeRisk = '^GSPC'
    result = metrics(lista)
    return result
    

def Cedears():
    comafi = pd.read_html('https://www.comafi.com.ar/2254-CEDEAR-SHARES.note.aspx')[0]
    # sorteamos por orden alfabético
    comafi = comafi.sort_values('Símbolo BYMA',axis=0,ascending=True)
    comafi.index = range(len(comafi)) # update index order values
    cells = list(comafi['Símbolo BYMA'].values)
    # cells.index('AAPL') way to get index number where ticker is located
    cedears = [c + '.BA' for c in cells]
    volume = yahoo.download(cedears,period="80d")['Volume'].fillna(method='ffill')
    votal = pd.DataFrame(index=volume.index)
    votal['totav'] = volume.T.sum()
    percentage = volume.div(votal['totav'], axis=0)
    ordered = pd.DataFrame(percentage.sum().T,columns=['percentage'],index=percentage.columns)
    ordered = ordered / ordered.sum() # ensure you round to 100%
    orderedalph = ordered.sort_values('percentage',axis=0,ascending=False)    
    liquid = orderedalph.cumsum()    
    listado = list(liquid.head(50).index.values)
    listado = [i.replace('.BA','') for i in listado]
    lista = []
    for i in range(len(listado)):
        lista.append(comafi['Ticker en Mercado de Origen'][cells.index(f'{listado[i]}')])
    freeRisk = '^GSPC'
    result = metrics(lista)
    return result

def NIKKEI():
    lista = pd.read_html("https://topforeignstocks.com/indices/the-components-of-the-nikkei-225-index/")[0]
    lista['tickets'] = [t + '.T' for t in lista.Code.astype(str)]
    lista = list(lista.tickets.values)
    freeRisk = '^N225'
    result = metrics(lista)
    return result

def Shanghai():
    china = pd.read_html('https://tradingeconomics.com/china/stock-market')[1]
    lista = [i + '.SS' for i in list(china['Unnamed: 0'].astype(str))]
    freeRisk = "000001.SS"
    result = metrics(lista)
    return result

def BOVESPA():
    lista = pd.read_html("https://topforeignstocks.com/indices/components-of-the-bovespa-index/")[0]
    lista = list(lista.Ticker.values)
    freeRisk = '^BVSP'
    result = metrics(lista)
    return result

def CANADA():
    lista = pd.read_html("https://topforeignstocks.com/indices/the-components-of-the-sptsx-composite-index/")[0]
    lista = list(lista.Ticker.values)
    freeRisk = '^GSPTSE'
    result = metrics(result)
    return result

def FTSE():
    lista = pd.read_html("https://topforeignstocks.com/indices/components-of-the-ftse-100-index/")[0]
    lista = list(lista.Ticker.values)
    freeRisk = '^FTSE'
    result = metrics(lista)
    return result

def AUSTRALIA():
    australia = pd.read_html("https://topforeignstocks.com/indices/components-of-the-s-p-asx-all-australian-500-index/")[0]
    lista = list(australia['Ticker'].values)
    freeRisk = '^AXJO'
    result = metrics(lista)
    return result

def binance():
    x = pd.DataFrame(client.get_ticker())
    y =  x[x.symbol.str.contains('USDT')]
    z = y[~(y.symbol.str.contains('BULL')) & ~(y.symbol.str.contains('BEAR'))]
    z = z[~(z.symbol.str.contains('UP')) & ~(z.symbol.str.contains('DOWN'))]
    z = z[z.symbol.apply(lambda x: ('USDT' in x[-4:]))]
    z = z[z.lastPrice.astype(float)!=0]
    final = z[['symbol','lastPrice']]
    final = final.sort_values('symbol',ascending=True)
    final['lastPrice'] = final['lastPrice'].astype(float)
    lista = [i.replace('USDT','-USD') for i in final.symbol.to_list()]
    result = metrics(lista)
    return result

def Merval():
    panel = pd.read_html('https://iol.invertironline.com/Mercado/Cotizaciones')[0]
    #panel = pd.read_html('https://iol.invertironline.com/mercado/cotizaciones/argentina/acciones/panel-general')[0]
    lista = [i[0:4] + '.BA' for i in panel.Símbolo.to_list()]
    result = metrics(lista)
    return result
