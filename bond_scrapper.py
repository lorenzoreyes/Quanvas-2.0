import requests, re
import pandas as pd, datetime as dt
from bs4 import BeautifulSoup

pd.options.display.float_format = '{:,.2f}'.format
'''
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
'''
year = dt.date.today().year 

#url = input('Provide web-page link to perform scrapping\n\n\t\t')
url = 'https://bolsar.info/Titulos_Publicos.php'
headers = {'User-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36'}

response = requests.get(url, headers)
soup =  BeautifulSoup(response.content, 'html.parser')
tables = soup.findAll('table')

bonds, letters = pd.read_html(str(tables[0])), pd.read_html(str(tables[1]))
bonds = bonds[0].drop_duplicates('Especie')
# remove if ends wit C, X or Z
bonds = bonds[~(bonds.Especie.apply(lambda x: ('C' in x[-1]))) & ~(bonds.Especie.apply(lambda x: ('X' in x[-1]))) & ~(bonds.Especie.apply(lambda x: ('Z' in x[-1])))]
bonds = bonds[['Especie','Compra','Venta','Último','Volumen','Monto']]
bonds['Vence'] = [re.findall(r'\d+',i) for i in bonds.Especie.to_list()]
bonds['Vence'] = [str(i)[2:-2].replace(',','').replace(' ','').replace("'","") for i in bonds.Vence.to_list()]
bonds['Vence'] = [int('20' + i) if len (i) > 1 else year for i in bonds.Vence.to_list()]

for i in range(1,len(bonds.columns)-1):
    bonds[f'{bonds.columns[i]}'] = [float(j.replace('.','').replace(',','.').replace('-','0')) for j in bonds[f'{bonds.columns[i]}'].to_list()]
    # remove null activity
    bonds = bonds[bonds[f'{bonds.columns[i]}'] !=0]
    
bonds['Spread'] = ((bonds['Venta'] - bonds['Compra']) / bonds['Venta']) * 100.0
# columnas especie, vence, spread [venta-compra/venta] precio, spread, vol, liquidez
dollars = list(filter(lambda x: 'D' in x[-1], bonds.Especie.to_list()))
pesos = [i[:-1] for i in dollars]

bonad = bonds[bonds['Especie'].isin(dollars)]
bonap = bonds[bonds['Especie'].isin(pesos)]
bonad = bonds[bonds['Especie'].isin([i+'D' for i in bonap['Especie'].to_list()])]
bonap = bonap[["Especie","Último"]]
bonap.columns = ['Bono P','Precio P']
bonap['Bono D'] = bonad['Especie'].to_list()
bonap['Precio D'] = bonad['Último'].to_list()
bonap['Precio D'] /= 100
bonap['MEP'] = bonap['Precio P'] / bonap['Precio D']
bonap = bonap[~((bonap.T == 0.00).any())]

titles = sorted(list(set([re.split(r'(\d+)', i)[0] for i in bonds.Especie.to_list()])))
bonds.index = range(len(bonds))

bonds.to_csv('bondsarg.csv')


print('\n\n',bonap)
