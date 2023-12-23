from packages import *
import requests, re, json
import pandas as pd, datetime as dt
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings("ignore")
pd.options.display.float_format = '{:,.2f}'.format

data = pd.read_excel('resultados_por_info_completa.xlsx',sheet_name='resultados_por_lotes_finales')
data = data.dropna()

data = data[['Ticker','Precio Compra','Cantidad','Tipo']]
info = data[data['Tipo']=='Cedears'][['Cantidad','Ticker']]
bono = data[data['Tipo']!='Cedears'][['Cantidad','Ticker']]
# adjust the ratios
comafi = pd.read_html('comafi.html')[0]
comafi = comafi[['Programa  de  CEDEAR','Id  de  mercado','Ticker  en  mercado  de  origen','Ratio  Cedear  /  valor  sub-yacente','Frecuencia  de  pago  de  dividendo']]
comafi.columns = ['Cedear','Byma','Ticker','Ratio','Dividendo']
comafi['Ratin'] = [int(i.split(':')[0]) for i in comafi['Ratio']]
comafi['Ratiout'] = [int(i.split(':')[1]) for i in comafi['Ratio']]
del comafi['Ratio']

info = yahoo.download([i+'D.BA' for i in info['Ticker']],start='2023-12-19',end=None,interval='60m').fillna(method='ffill')['Adj Close']

# Bonos
year = dt.date.today().year 

#url = input('Provide web-page link to perform scrapping\n\n\t\t')
url = 'https://www.rava.com/cotizaciones/bonos'
headers = {'User-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36'}

response = requests.get(url, headers)
soup =  BeautifulSoup(response.content, 'html.parser')
jason = soup.findAll('bonos-p')

text = str(jason).replace('null','0')
text = (' '.join(text.split('[{')[1:])).split('}]')[0]
 
text = text.split(',')
keys = list(set([i.split(':')[0] for i in text]))
keys = [i.split(':')[0] for i in text[:39]]
dicts = {key: [] for key in keys}

items = [i.split(':')[1] for i in text]
items = [items[i:i+39] for i in range(0, len(items), 39)]

df = pd.DataFrame(columns=keys)

for item in items:
    df.loc[len(df)] = item
    
df.columns = [i.replace('"','') for i in df.columns]
df = df[['simbolo','ultimo']]
df['simbolo'] = [i.replace('"','') for i in df['simbolo'].to_list()]

# merge
df = df[df['simbolo'].isin([i+'D' for i in bono['Ticker']])]
df['ultimo'] = df['ultimo'].astype(float) / 100.0
data['Hoy'] = df.iloc[:,-1].to_list() + info.iloc[-1,:].to_list()
data['Nocional'] = (data['Precio Compra'] * data['Cantidad']).sum()
data['Noc Hoy'] = (data['Hoy'] * data['Cantidad']).sum()
del data['Tipo']
data['PnL'] = (data['Hoy'] - data['Precio Compra']) / data['Precio Compra']
#data['Weights'] = (data['Precio Compra'] * data['Cantidad']) / (data['Precio Compra'] * data['Cantidad']).sum()
#data['WeightsHoy'] = (data['Hoy'] * data['Cantidad']) / (data['Hoy'] * data['Cantidad']).sum()
print(data)