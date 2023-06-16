import requests, re
import pandas as pd, datetime as dt
from bs4 import BeautifulSoup

pd.options.display.float_format = '{:,.2f}'.format

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
    #bonds = bonds[bonds[f'{bonds.columns[i]}'] !=0]
    
bonds['Spread'] = ((bonds['Venta'] - bonds['Compra']) / bonds['Venta']) * 100.0
#re.findall(r'\d+',bonds.Especie.to_list()[0])
#[re.findall(r'\d+',i) for i in bonds.Especie.to_list()]
# columnas especie, vence, spread [venta-compra/venta] precio, spread, vol, liquidez
dollars = list(filter(lambda x: 'D' in x[-1], bonds.Especie.to_list()))

#z = y[~(y.symbol.str.contains('BULL')) & ~(y.symbol.str.contains('BEAR'))]
#    z = z[z.symbol.apply(lambda x: ('USDT' in x[-4:]))]
#titles = list(set([i[:4] for i in debt.Especie.to_list()]))
#''.join([i for i in debt.Especie.to_list()if not i.isdigit()])
titles = sorted(list(set([re.split(r'(\d+)', i)[0] for i in bonds.Especie.to_list()])))

bonds.to_csv('bondsarg.csv')
print(bonds)