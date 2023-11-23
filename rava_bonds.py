from packages import *
options = Options()
options.add_experimental_option("prefs",{'download.prompt_for_download': False})
pd.options.display.float_format = '{:,.2f}'.format
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
excel['MEP'] = excel['Precio P'] / excel['Precio D']


download = sorted(excel['Bono D'].to_list() + excel['Bono P'].to_list())

chrome_options = Options()
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox") # linux only
chrome_options.add_argument("--start-maximized");
chrome_options.headless = True # also works
bot = webdriver.Chrome(options=chrome_options)

for i in range(len(download)):
    bot.get(f'https://www.rava.com/perfil/{download[i]}')
    time.sleep(1)
    with open(f'{download[i]}.html', 'w+') as f:
        f.write(bot.page_source)
    button = bot.find_element(by='xpath',value='//*[@id="Coti-hist-c"]/div/div[3]/button')
    time.sleep(1)
    button
    bot.execute_script("arguments[0].click();", button)
    print("Bond obtained...\t {}.\t Download data and cashflow.".format(download[i]))
    time.sleep(1)

dolarizados = excel['Bono D'].to_list()
pesificados = excel['Bono P'].to_list()

curva_dolares = pd.read_csv(dolarizados[0]+' - Cotizaciones historicas.csv')
curva_dolares = pd.DataFrame(curva_dolares.cierre.values,columns=[f'{dolarizados[0]}'],index=curva_dolares['fecha'])
curva_dolares = curva_dolares.loc['2021':]

for i in range(1,len(dolarizados)):
    dolarizados[i] = pd.read_csv(dolarizados[i]+' - Cotizaciones historicas.csv')
    dolarizados[i] = pd.DataFrame(dolarizados[i].cierre.values,columns=[dolarizados[i].especie[0]],index=dolarizados[i]['fecha'])
    dolarizados[i] = dolarizados[i].loc['2021':]
    curva_dolares[f'{dolarizados[i].columns[0]}'] = dolarizados[i].tail(len(curva_dolares))

curva_dolares.fillna(method='bfill')

columnas = []
for i in range(len(curva_dolares.columns)):
  columnas.append(str(curva_dolares.columns[i]) + ' $' + str(round(curva_dolares.fillna(method='ffill').iloc[-1,i],3)))

fig = plt.figure(figsize=(30,20))
ax1 = fig.add_subplot(111)
curva_dolares.fillna(method='ffill').plot(ax=ax1, lw=4.)
ax1.set_title('Bonos D', fontsize=50, fontweight='bold')
ax1.grid(True,color='k',linestyle='-.',linewidth=2)
ax1.legend(columnas,loc='best', bbox_to_anchor=(1, 0.75),fontsize=40)
plt.xticks(size=30, rotation=45)
plt.yticks(size=40, rotation=45)
plt.savefig('bonosDolar.png',bbox_inches='tight')

curva_pesos = pd.read_csv(pesificados[0]+' - Cotizaciones historicas.csv')
curva_pesos = pd.DataFrame(curva_pesos.cierre.values,columns=[f'{pesificados[0]}'],index=curva_pesos['fecha'])
curva_pesos = curva_pesos.loc['2021':]

for i in range(1,len(pesificados)):
    pesificados[i] = pd.read_csv(pesificados[i]+' - Cotizaciones historicas.csv')
    pesificados[i] = pd.DataFrame(pesificados[i].cierre.values,columns=[pesificados[i].especie[0]],index=pesificados[i]['fecha'])
    pesificados[i] = pesificados[i].loc['2021':]
    curva_pesos[f'{pesificados[i].columns[0]}'] = pesificados[i].tail(len(curva_pesos))

curva_pesos = curva_pesos.fillna(method='bfill')

columnas = []
for i in range(len(curva_pesos.columns)):
  columnas.append(str(curva_pesos.columns[i]) + ' $' + str(round(curva_pesos.fillna(method='ffill').iloc[-1,i],2)))


fig = plt.figure(figsize=(30,20))
ax1 = fig.add_subplot(111)
curva_pesos.plot(ax=ax1, lw=4.)
ax1.set_title('Bonos P', fontsize=50, fontweight='bold')
ax1.grid(True,color='k',linestyle='-.',linewidth=2)
ax1.legend(columnas,loc='best', bbox_to_anchor=(1, 0.75),fontsize=40)
plt.xticks(size=30, rotation=45)
plt.yticks(size=40, rotation=45)
plt.savefig('bonosPesos.png',bbox_inches='tight')

cable = curva_pesos.tail(len(curva_dolares)).divide(curva_dolares.values)

columnas = []
for i in range(len(cable.columns)):
  columnas.append(str(cable.columns[i]) + ' $' + str(round(cable.fillna(method='ffill').iloc[-1,i],3)))


fig = plt.figure(figsize=(30,20))
ax1 = fig.add_subplot(111)
cable.loc['2022-03':].plot(ax=ax1, lw=4.)
ax1.set_title('Bonos Cable', fontsize=50, fontweight='bold')
ax1.grid(True,color='k',linestyle='-.',linewidth=2)
ax1.legend(columnas,loc='best', bbox_to_anchor=(1, 0.75),fontsize=40)
plt.xticks(size=30, rotation=45)
plt.yticks(size=40, rotation=45)
plt.savefig('cableBonos.png',bbox_inches='tight')
