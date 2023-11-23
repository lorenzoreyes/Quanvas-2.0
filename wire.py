from packages import *

comafi = pd.read_html('https://www.comafi.com.ar/2254-CEDEAR-SHARES.note.aspx')[0]
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
listado = list(liquid.head(50).index.values)
listado = [i.replace('.BA','') for i in listado]
lista = []
for i in range(len(listado)):
    lista.append(comafi['Ticker en Mercado de Origen'][cells.index(f'{listado[i]}')])
freeRisk = '^GSPC'