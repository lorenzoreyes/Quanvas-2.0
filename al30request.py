from packages import *

options = Options()
options.add_experimental_option("prefs",{'download.prompt_for_download': False})

pd.options.display.float_format = '{:,.2f}'.format

year = dt.date.today().year
quarter = str(dt.date.today() - dt.timedelta(90))

url = 'https://bolsar.info/Titulos_Publicos.php'
headers = {'User-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36'}

response = requests.get(url, headers)
soup =  BeautifulSoup(response.content, 'html.parser')
tables = soup.findAll('table')

bonds, letters = pd.read_html(str(tables[0]))[0], pd.read_html(str(tables[1]))
#page[2] = [i.replace('.','').replace(',','.') for i in page[2].to_list()]
bonds = bonds[['Especie','Último','Volumen','Monto']]
bonds.columns = ['Especie','Precio','Volumen','Monto']
bonds = bonds[~(bonds.Especie.apply(lambda x: ('Y' in x[-1])))]
# descarto empieza en B, CO, PBA, PMM, TO, TVPP y termina en D
discard = ['B', 'CO','CE','GE', 'N','PB', 'PM', 'TB','TC','TD', 'TO','T2','TV','R','S','Y']
for i in range(len(discard)):
    bonds = bonds[~(bonds.Especie.str.startswith(f'{discard[i]}'))]

bonds = bonds.drop_duplicates('Especie')
dollars = ['AL30','AL30D']

dollar = bonds[bonds.Especie.isin(dollars)]
bonds = bonds[bonds.Especie.isin(dollars)]



download = sorted(dollar.Especie.to_list())
chrome_options = Options()
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox") # linux only
chrome_options.add_argument("--headless")
chrome_options.add_argument("--start-maximized");
chrome_options.headless = True # also works
bot = webdriver.Chrome(options=chrome_options)

download = ['AL30','AL30D']
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

dolarizados = dollar[(dollar.Especie.apply(lambda x: ('D' in x[-1])))]['Especie'].to_list()
pesificados = dollar[~(dollar.Especie.apply(lambda x: ('D' in x[-1])))]['Especie'].to_list()

curva_dolares = pd.read_csv(dolarizados[0]+' - Cotizaciones historicas.csv')
curva_dolares = pd.DataFrame(curva_dolares.cierre.values,columns=[f'{dolarizados[0]}'],index=curva_dolares['fecha'])
curva_dolares = curva_dolares.loc['2021':]


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


writer = pd.ExcelWriter('al30.xlsx',engine='xlsxwriter')
curva_dolares.to_excel(writer,sheet_name='Bonos Dollar')
curva_pesos.to_excel(writer,sheet_name='Bonos Pesificados')
cable.fillna(method='bfill').to_excel(writer,sheet_name='cable bonos')
writer.close()
