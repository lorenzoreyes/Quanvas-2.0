from packages import *

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

def scrap(link):
  url = link 
  headers = {'User-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36'}
  response = requests.get(url, headers)
  soup =  BeautifulSoup(response.content, 'html.parser')
  tables = soup.findAll('table')
  data = pd.read_html(str(tables[0]))[0]
  data = data['Especie'].to_list()
  return data 

panel = scrap('https://bolsar.info/paneles.php?panel=2&titulo=Panel%20General')
lider = scrap('https://bolsar.info/lideres.php')

merval = [i + '.BA' for i in list(dict.fromkeys(panel + lider))]

data = yahoo.download(merval,period='1y',interval='60m')['Adj Close'].fillna(method='ffill')
returns = [str(round(i*100.0,2)) for i in data.pct_change().sum().to_list()]
returns = list(zip(data.columns.to_list(),returns))
returns = [' '.join(_) for _ in returns]

fig = plt.figure(figsize=(60,50))
ax1 = fig.add_subplot(111)
data.pct_change().cumsum().fillna(0).plot(ax=ax1, lw=5.,)
ax1.set_title('La Mercaluta', fontsize=90, fontweight='bold')
ax1.grid(True,color='k',linestyle='-.',linewidth=2)
ax1.legend(returns,loc='upper right', bbox_to_anchor=(1.1, 1),fontsize=24)
plt.xticks(size=60, rotation=45)
plt.yticks(size=70, rotation=45)
plt.savefig('LaMercaluta.png')

filtro = data.pct_change().sum().head(20).index.to_list()

data = data[filtro]

returns = [str(round(i*100.0,2)) for i in data.pct_change().sum().to_list()]
returns = list(zip(data.columns.to_list(),returns))
returns = [' '.join(_) for _ in returns]

fig = plt.figure(figsize=(30,15))
ax1 = fig.add_subplot(111)
data.pct_change().cumsum().fillna(0).plot(ax=ax1, lw=5.,)
ax1.set_title('La Mercaluta 20', fontsize=90, fontweight='bold')
ax1.grid(True,color='k',linestyle='-.',linewidth=2)
ax1.legend(returns,loc='upper right', bbox_to_anchor=(1.1, 1),fontsize=24)
plt.xticks(size=60, rotation=45)
plt.yticks(size=70, rotation=45)
plt.savefig('LaMercaluta20.png')

