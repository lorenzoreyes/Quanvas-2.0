from packages import *

client = Client(API_KEY,API_SECRET)


try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context


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
    #pct = df.pct_change() arithmetic returns
    pct = np.log(df) - np.log(df.shift(1)) # logarithmic returns
    mean = pd.DataFrame(pct.mean(),columns=['Mean'],index=pct.columns)
    riskpct = mean.mean()
    mean_rf = mean - riskpct.mean()
    std = pd.DataFrame(pct.std(),columns=['Std'],index=pct.columns)
    sharpe_ratio = pd.DataFrame(mean_rf['Mean']/(std['Std']), columns=['SharpeRatio'],index=pct.columns)
    orderedsharpe = sharpe_ratio.sort_values('SharpeRatio', axis=0, ascending=False)
    lista = list(orderedsharpe.head(40).index.values)
    df = yahoo.download(lista,period="1y",interval="60m")["Adj Close"].fillna(method="ffill")
    riskfree = df.T.mean().fillna(method='ffill')
    pct = np.log(df) - np.log(df.shift(1)) # logarithmic returns
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
    alpha = 0.05
    rf = riskpct.mean()
    num_portfolios = 1000
    Upbound = 0.085
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
    discardo = ['Irregular','-','Irreg','None','NONE']
    for i in range(len(discardo)):
        comafi = comafi[~(comafi['Frecuencia de Pago de Dividendo'].str.startswith(f'{discardo[i]}'))]
    comafi = comafi[['Programa de CEDEAR','Símbolo BYMA','Ticker en Mercado de Origen','Ratio CEDEARs/valor subyacente']]
    comafi.columns = ['Cedear','Byma','Ticker','Ratio']
    comafi['Ratin'] = [int(i.split(':')[0]) for i in comafi['Ratio']]
    comafi['Ratiout'] = [int(i.split(':')[1]) for i in comafi['Ratio']]
    del comafi['Ratio']
    # sorteamos por orden alfabético
    comafi['Byma'] = [c + '.BA' for c in comafi['Byma']]
    comafi = comafi.sort_values('Byma',axis=0,ascending=True)

    # data precio local filtramos liquidas
    local = yahoo.download(comafi['Byma'].to_list(),period="1y")['Adj Close'].fillna(method='ffill')
    local = local[comafi['Byma'].to_list()]
    local = local * comafi['Ratin'].to_list()
    # data precios de afuera y mezclamos
    abroad = yahoo.download(comafi['Ticker'].to_list(),period="1y")['Adj Close'].fillna(method='ffill')
    # ensure the same order
    abroad = abroad[comafi['Ticker'].to_list()]
    abroad = abroad * comafi['Ratiout'].to_list()

    # match length, mix & multiply it by its ratio
    abroad = abroad.tail(len(local))
    cable = local.divide(abroad.values,axis='index')
    cable = cable.dropna(axis=1)
    comafi = comafi[comafi['Byma'].isin(cable.columns)]
    freeRisk = '^GSPC'
    result = metrics(comafi['Ticker'].to_list())
    ratios = dict(zip(comafi['Ticker'],comafi['Ratin']))
    df = result[0]
    for i in range(len(df.columns)):
        df[df.columns[i]] = df[df.columns[i]] / ratios[df.columns[i]]
        
    result[0] = df
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
    z = z[~(z.symbol.str.contains('UP'))] # & ~(z.symbol.str.contains('DOWN'))]
    z = z[z.symbol.apply(lambda x: ('USDT' in x[-4:]))]
    # undesirable coins, paxg we later use it to hedge
    stable =['TUSDUSDT','USDCUSDT','BUSDUSDT','USTCUSDT','LUNA1USDT','LUNAUSDT','PAXGUSDT','REIUSDT','TRONUSDT','SHIBUSDT']
    z = z[~(z.symbol.isin(stable))]
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
