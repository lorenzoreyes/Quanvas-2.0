from packages import *

url = 'https://www.comafi.com.ar/custodiaglobal/2483-Programas-Cedear.cedearnote.note.aspx#shares'
header = {
  "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
  "X-Requested-With": "XMLHttpRequest"
}

req = requests.get(url, headers=header)
comafi = pd.read_html('comafi.html')[0]
comafi = comafi[['Programa  de  CEDEAR','Id  de  mercado','Ticker  en  mercado  de  origen','Ratio  Cedear  /  valor  sub-yacente','Frecuencia  de  pago  de  dividendo']]
comafi.columns = ['Cedear','Byma','Ticker','Ratio','Dividendo']
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
local = local.tail(len(abroad))
cable = local.divide(abroad.values,axis='index')
cable = cable.dropna(axis=1)
comafi = comafi[comafi['Byma'].isin(cable.columns)]
comafi = comafi.dropna()

fig = plt.figure(figsize=(30,18))
ax1 = fig.add_subplot(111)
cable[(cable>=250.0)].dropna(axis=1).plot(ax=ax1, lw=3.,legend=False)
ax1.set_title('Argentina Cedears', fontsize=60, fontweight='bold')
ax1.grid(linewidth=2)
plt.xticks(size = 20)
plt.yticks(size = 20)

# now filter the best by liquidity
volume = yahoo.download(comafi['Byma'].to_list(),period='80d')['Volume'].fillna(method='ffill')
volume = volume.dropna(axis=1)
votal = pd.DataFrame(index=volume.index)
votal['totav'] = volume.T.sum()
percentage = volume.div(votal['totav'], axis=0)
ordered = pd.DataFrame(percentage.sum().T,columns=['percentage'],index=percentage.columns)
ordered = ordered / ordered.sum() # ensure you round to 100%
orderedalph = ordered.sort_values('percentage',axis=0,ascending=False)
liquid = orderedalph.cumsum()
recorte = comafi[comafi['Byma'].isin(liquid.index)]['Ticker'].to_list()
ticker_symbols = recorte
stocks = [yahoo.Ticker(i) for i in ticker_symbols]
infos = [s.info for s in stocks]

dicts = [{"ticker_symbol":ticker_symbols[i]} for i in range(len(ticker_symbols))]

for i in range(len(dicts)):
    dicts[i]['current_price'] = infos[i]['currentPrice']
    dicts[i]['dividend_yield'] = infos[i].get('dividendYield',0)
    dicts[i]['expected_dividend'] = dicts[i]['current_price'] * dicts[i]['dividend_yield']
    dicts[i]['exDividendDate'] = infos[i].get('exDividendDate','Never')
    value = dicts[i]['exDividendDate']
    dicts[i]['exDividendDate'] = value.upper() if isinstance(value, str) else dt.datetime.fromtimestamp(value).strftime('%Y-%m-%d')  

dividends = pd.DataFrame([i['ticker_symbol'] for i in dicts],columns=['Ticker'])
dividends['price'] = [i['current_price'] for i in dicts]    
dividends['dividend_yield'] = [i['dividend_yield'] for i in dicts]
dividends['expected_dividend'] = [i['expected_dividend'] for i in dicts]
dividends['exDividendDate'] = [i['exDividendDate'] for i in dicts]
dividends['divperdol'] = dividends['expected_dividend']/dividends['price']