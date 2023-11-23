import requests, re, json
import pandas as pd, datetime as dt
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings("ignore")

pd.options.display.float_format = '{:,.2f}'.format

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

dollars = list(filter(lambda x: 'D' in x[-1], df['simbolo'].to_list()))
pesos = [i[:-1] for i in dollars]

dolares = df[df['simbolo'].isin(dollars)]
pesificados = df[df['simbolo'].isin([i[:-1] for i in dolares['simbolo']])]
dolares = df[df['simbolo'].isin([i+'D' for i in pesificados['simbolo']])]

excel = pesificados
excel.columns = ['Bono P','Precio P']
excel['Precio P'] = excel['Precio P'].astype(float).to_list()
excel['Bono D'] = dolares['simbolo'].to_list()
excel['Precio D'] = dolares['ultimo'].astype(float).to_list()
#excel['Precio P'], excel['Precio D'] = excel['Precio P']/100.0, excel['Precio D']/100.0 
excel['MEP'] = excel['Precio P'] / excel['Precio D']
excel['Parity'] = excel['MEP'] / (excel['Precio D'] / 100.0)
#excel['Paridad'] = excel['MEP'] / (excel['Precio D']/100.0)
#excel['Nominal'] = excel['Precio P'] / (excel['Precio D']/100.0)
cheapest,expensive = excel[excel['MEP']==min(excel['MEP'])][['Bono P','MEP']], excel[excel['MEP']==max(excel['MEP'])][['Bono D','MEP']]
cheapest,expensive = cheapest.iloc[0].to_list(),expensive.iloc[0].to_list()

print("Data de Rava Bursatil\n\n",excel)
print('Dolar Pure\t%',
      round(((expensive[1]/cheapest[1])-1)*100.0,2),
      f'\nPesos\t{cheapest}\nDolares\t{expensive}')

import dataframe_image as dfi

dfi.export(excel,'myexcel.png')

url = 'https://criptoya.com/api/usdt/ars'
headers = {'User-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36'}

response = requests.get(url, headers)
cryptos = pd.DataFrame.from_dict(response.json()).T
cryptos = cryptos[['ask','bid']]

cryptos.T['satoshitango']

print('\n\nCryptos\n',cryptos)


