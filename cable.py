from packages import *

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context
'''
context = ssl._create_unverified_context()
urllib.request.urlopen("https://no-valid-cert", context=context)

pd.options.display.float_format = '{:,.2f}'.format
'''
comafi = pd.read_html('https://www.comafi.com.ar/custodiaglobal/2483-Programas-Cedear.cedearnote.note.aspx#shares')[0]
# sorteamos por orden alfabético
comafi = comafi.sort_values('Id  de  mercado',axis=0,ascending=True)
comafi.index = range(len(comafi)) # update index order values
cells = list(comafi['Id  de  mercado'].values)
# cells.index('AAPL') way to get index number where ticker is located
cedears = [c + '.BA' for c in cells]

volume = yahoo.download(cedears,period="1y")['Volume'].fillna(method='ffill')
votal = pd.DataFrame(index=volume.index)
votal['totav'] = volume.T.sum()
percentage = volume.div(votal['totav'], axis=0)
ordered = pd.DataFrame(percentage.sum().T,columns=['percentage'],index=percentage.columns)
ordered = ordered / ordered.sum() # ensure you round to 100%
orderedalph = ordered.sort_values('percentage',axis=0,ascending=False)
liquid = orderedalph.cumsum()
listado = list(liquid.head(20).index.values)

filtro = [i.replace('.BA','') for i in listado]
comafi = comafi[comafi['Id  de  mercado'].isin(filtro)]

comafi = comafi.sort_values('Id  de  mercado',axis=0,ascending=True)
comafi.index = range(len(comafi)) # update index order values
cells = list(comafi['Id  de  mercado'].values)
# cells.index('AAPL') way to get index number where ticker is located
cedears = [c + '.BA' for c in cells]


data = yahoo.download(cedears,period='2y',interval='60m')['Adj Close'].fillna(method='ffill')

foreign = comafi['Ticker  en  mercado  de  origen'].to_list()
foreign = yahoo.download(foreign,period='2y',interval='60m')['Adj Close'].fillna(method='ffill')

ratios = [float(int(j[0]) / int(j[1])) for j in [i.split('/') for i in  comafi['Ratio  Cedear  /  valor  sub-yacente'].str.replace(':','/').to_list()]]

data['fechas'],foreign['fechas'] =  [i[:10] for i in data.index.astype(str).to_list()],[i[:10] for i in foreign.index.astype(str).to_list()]
data['fechas'],foreign['fechas'] =  [i[:10] for i in data.fechas.astype(str).to_list()],[i[:10] for i in foreign.fechas.astype(str).to_list()]

cable = pd.merge(data,foreign,on='fechas')

cable.index = cable['fechas']

del cable['fechas']
fuera = cable.iloc[:,20:]
cable = cable.iloc[:,:20]

for i in range(20):
    cable[f'{cable.columns[i]}'] *= ratios[i] 
    cable[f'{cable.columns[i]}'] /= fuera[f'{fuera.columns[i]}']
    
cable = cable.loc[:, ~(cable > 400.0).any()]
cable = cable.loc[:, ~(cable < 110.0).any()]
cable = cable.dropna(axis=1) 

precios = [str(round(i,2)) for i in cable.iloc[-1,:].to_list()]
columnas = []
for i in range(len(cable.columns)):
    columnas.append(str(cable.columns[i]) + ' $' + precios[i])

cable.columns = columnas

fig = plt.figure(figsize=(40,25))
ax1 = fig.add_subplot(111)
cable.plot(ax=ax1, lw=4.)
ax1.set_title('CEDEAR$ RAte', fontsize=150, fontweight='bold')
ax1.grid(True,color='k',linestyle='-.',linewidth=2)
ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize=50)
plt.xticks(size=50, rotation=45)
plt.yticks(size=60, rotation=45)
plt.savefig('cedeARSrate.png',bbox_inches='tight')
