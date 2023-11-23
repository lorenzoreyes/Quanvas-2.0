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
discard = ['B', 'CE','GE', 'N','PB', 'PM', 'TB','TC','TD', 'TO','T2','TV','TX','R','S','Y']
for i in range(len(discard)):
    bonds = bonds[~(bonds.Especie.str.startswith(f'{discard[i]}'))]

bonds = bonds.drop_duplicates('Especie')

discard = ['C','X','Y','Z']
for i in range(len(discard)):
    bonds = bonds[~(bonds.Especie.apply(lambda x: (discard[i] in x[-1])))]

# reformateo numeros
for i in range(1,len(bonds.columns)):
    # remuevo vacios
  bonds[f'{bonds.columns[i]}'] =  [i.replace('-','0') if len(i) < 2 else i for i in bonds[f'{bonds.columns[i]}'].astype(str).to_list()]
  bonds[f'{bonds.columns[i]}'] = [float(j.replace('.','').replace(',','.').replace('-','0')) for j in bonds[f'{bonds.columns[i]}'].to_list()]

bonds.index = range(len(bonds))
index = bonds[(bonds.Especie.apply(lambda x: ('D' in x[-1])))].index.to_list() + bonds[bonds.Especie.str.startswith('PR')].index.to_list() + bonds[bonds.Especie.str.startswith('T')].index.to_list()
ultimo = bonds.Precio.to_list().copy()
for i in index:
    ultimo[i] = ultimo[i]/100.0

bonds['Precio'] = ultimo

# arreglo decimales

#cer = ['TX']#,'PR13','DICP','PARP','CUAP']
#ceres = [' '.join(str(j) for j in [bonds[bonds.Especie.str.startswith(i)].Especie.to_list() for i in cer])]
#ceres = [i.replace('[','').replace(']',',').replace(' ','').replace("'","") for i in ceres][0][:-1].split(',')

#cer = bonds[bonds.Especie.isin(ceres)]
#cer = cer[~(cer.Especie.apply(lambda x: ('D' in x[-1])))]
#ceres = cer.Especie.to_list()

dollar = ['AL','AE','GD']
dollars = [' '.join(str(j) for j in [bonds[bonds.Especie.str.startswith(i)].Especie.to_list() for i in dollar])]
dollars = [i.replace('[','').replace(']',',').replace(' ','').replace("'","") for i in dollars][0][:-1].split(',')

dollar = bonds[bonds.Especie.isin(dollars)]

#download = sorted(cer.Especie.to_list() + dollar.Especie.to_list())
download = sorted(dollar.Especie.to_list())

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

dolarizados = dollar[(dollar.Especie.apply(lambda x: ('D' in x[-1])))]['Especie'].to_list()
pesificados = dollar[~(dollar.Especie.apply(lambda x: ('D' in x[-1])))]['Especie'].to_list()

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

'''
titulos, ceres = cer.Especie.to_list().copy(),cer.Especie.to_list().copy()

infla = pd.read_csv(titulos[0]+' - Cotizaciones historicas.csv')
infla = pd.DataFrame(infla.cierre.values,columns=[f'{titulos[0]}'],index=infla['fecha'])
infla = infla.loc['2021':]

for i in range(1,len(ceres)):
    ceres[i] = pd.read_csv(ceres[i]+' - Cotizaciones historicas.csv')
    ceres[i] = pd.DataFrame(ceres[i].cierre.values,columns=[ceres[i].especie[0]],index=ceres[i]['fecha'])
    ceres[i] = ceres[i].loc['2021':]
    infla[f'{ceres[i].columns[0]}'] =  ceres[i].tail(len(infla))

infla = infla.fillna(method='bfill')

columnas = []
for i in range(len(infla.columns)):
  columnas.append(str(infla.columns[i]) + ' $' + str(round(infla.fillna(method='ffill').iloc[-1,i],2)))


fig = plt.figure(figsize=(30,20))
ax1 = fig.add_subplot(111)
infla.plot(ax=ax1, lw=4.)
ax1.set_title('Bonos CER', fontsize=50, fontweight='bold')
ax1.grid(True,color='k',linestyle='-.',linewidth=2)
ax1.legend(columnas,loc='best', bbox_to_anchor=(1, 0.5),fontsize=20)
plt.xticks(size=30, rotation=45)
plt.yticks(size=40, rotation=45)
plt.savefig('bonosCER.png',bbox_inches='tight')

# flujos y calculo de duration y mod-d
# valoractual, face: valor tecnico + 2 cupones de un año, ytm cupon 2 pagos/ valor mercado, freq cant pagos año
flujos = []
for i in range(len(download)):
    try: 
        bond = pd.read_html(f'bonos/{download[i]}.html')[1]
        bond, bond.columns = bond[['Fecha','CupÃ³n']], ['Fechas','Cupon']
        bond['Fechas'] = [dt.datetime.strptime(i, "%d/%m/%Y") for i in bond.Fechas.to_list()]
        bond['Cupon'] = bond['Cupon'].astype(float) / 100.0
        value = bond.Cupon[0].astype(float)/-1
        bond = bond.drop(0)
        cyield = sum((bond['Cupon'] / 100.0) / value)
        bond['Disc_Cupon'] = bond['Cupon'] / (1 + cyield/2)  ** bond.index
        bond['PV/totalDCP'] = bond['Disc_Cupon'] * bond.index / bond['Disc_Cupon'].sum()
        bond['Duration'] = sum(bond['PV/totalDCP']) / 2
        bond['MOD_D'] = bond['Duration'] / (1 + (cyield/2))
        flujos.append(bond)
    except:
        flujos.append(f'bonos/{download[i]}.html NO CF')

duration = []
for i in range(1,22,2):
    #print(f'{download[i]} has a Duration of:\t',flujos[i]['Duration'][1])
    duration.append(flujos[i][['Fechas','Duration']].iloc[-1,:].to_list())
    
duration,duration.columns = pd.DataFrame.from_records(duration),['Fechas','Duration']
duration.index = duration['Fechas']    
del duration['Fechas']    
duration['Bono'] = [(download[i]) for i in range(1,22,2)]
duration = duration.sort_index(ascending=True)

fig = plt.figure(figsize=(30,20))
ax1 = fig.add_subplot(111)
duration.plot.scatter(ax=ax1,x='Duration',y='Bono',s=650)
ax1.set_title('Duration Bonos D', fontsize=50, fontweight='bold')
ax1.grid(True,color='k',linestyle='-.',linewidth=2)
plt.plot(duration.Bono,duration.Duration, '-o',linewidth=9)
plt.xticks(size=90, rotation=45)
plt.yticks(size=60, rotation=45)
plt.savefig("Duration.png",dpi=300)
'''
writer = pd.ExcelWriter('bonargs.xlsx',engine='xlsxwriter')
curva_dolares.to_excel(writer,sheet_name='Bonos Dollar')
curva_pesos.to_excel(writer,sheet_name='Bonos Pesificados')
cable.fillna(method='bfill').to_excel(writer,sheet_name='cable bonos')
#infla.to_excel(writer,sheet_name='Bonos CER')
writer.close()
