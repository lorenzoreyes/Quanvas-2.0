from packages import *
mpl.rcParams['font.family'] = 'serif'
plt.style.use('fivethirtyeight')

today = dt.date.today()

os.system("curl https://www.bcra.gob.ar/Pdfs/PublicacionesEstadisticas/series.xlsm > seriese.xlsx")
os.system("python al30.py")
bonos = pd.read_excel('al30.xlsx',sheet_name='cable bonos')
bonos.index = bonos['fecha']
del bonos['fecha']
bonos.index = [dt.datetime.strptime(str(i), "%Y-%m-%d") for i in bonos.index.to_list()]
    
basem = pd.read_excel('seriese.xlsx', sheet_name='BASE MONETARIA')
reservas = pd.read_excel('seriese.xlsx', sheet_name='RESERVAS')
depositos = pd.read_excel('seriese.xlsx', sheet_name='DEPOSITOS')
prestamos = pd.read_excel('seriese.xlsx', sheet_name='PRESTAMOS')
tasas = pd.read_excel('seriese.xlsx', sheet_name='TASAS DE MERCADO')
instrumentos = pd.read_excel('seriese.xlsx', sheet_name='INSTRUMENTOS DEL BCRA')

basem = basem.loc[8:]
basem.index = basem['C60']
monetaria = pd.DataFrame(basem.iloc[:,24].values,columns=['billete_publico'],index=basem.iloc[:,0].values)
#interval = [monetaria.loc['2020':].],max(monetaria.loc['2020':].index)]
monetaria = monetaria.loc['2020':].dropna()

# Take every monetary aggregate
monetaria['billete_privado'] = basem.iloc[:,25].loc['2020':].dropna()#loc[interval[0]:interval[1]].values
monetaria['circulante'] = monetaria['billete_publico'] + monetaria['billete_privado']
monetaria['cta_cte_bcra'] = basem.iloc[:,27].loc['2020':].dropna().values#loc[interval[0]:interval[1]].values
monetaria['total_base'] = monetaria['billete_privado'] + monetaria['billete_publico'] + monetaria['cta_cte_bcra']

instrumentos = instrumentos[instrumentos.iloc[:,0].notna()]
instrumentos = instrumentos.iloc[8:,:]
instrumentos.index = instrumentos.iloc[:,0]
instrumentos = instrumentos.loc['2020':]#loc[interval[0]:interval[1]]
herramientas = pd.DataFrame(instrumentos.iloc[:,1].values,columns=['pases'],index=instrumentos.iloc[:,0].values)
herramientas['leliqs'] = instrumentos.iloc[:,4].values
herramientas['legar'] = instrumentos.iloc[:,5].values

reservas = reservas[reservas.iloc[:,0].notna()]
reservas = reservas.iloc[4:,:]
reservas.index = reservas.iloc[:,0]
reservas = reservas.loc['2020':]#.dropna(axis=1)#loc[interval[0]:interval[1]]
reservorio = pd.DataFrame(reservas.iloc[:,3].values,columns=['stock_reservas'],index=reservas.iloc[:,0].values)
reservorio['tc_oficial'] = reservas.iloc[:,-2].values
indice = []
for i in range(len(reservorio.index)):
  indice.append(dt.datetime.strptime(str(reservorio.index.values[i])[0:10],'%Y-%m-%d'))
reservorio.index = indice

# Reformat sheets into moentario main dataframe
# we use pd.concat to keep the most quantity of days until now, to have the most fresh data
monetaria = pd.DataFrame.join(monetaria,herramientas,how='outer').sort_index().fillna(method='ffill')
monetaria = pd.DataFrame.join(monetaria,reservorio['stock_reservas'],how='outer').sort_index().fillna(method='ffill')
monetaria = monetaria[~monetaria.index.duplicated(keep='first')]

# Sheet Depositos
depositos = depositos.iloc[8:,:]
depositos.index = depositos.iloc[:,0]
depositos = depositos.loc['2020':]

depositado = pd.DataFrame(depositos.iloc[:,1].values,columns=['cta_ctes_publico'],index=depositos.index)
depositado['cta_ctes_privado'] = depositos.iloc[:,10].values
depositado['caja_ahorro'] = depositos.iloc[:,11].values
depositado['plazos_tres'] = (depositos.iloc[:,12].values + depositos.iloc[:,13].values + depositos.iloc[:,14].values)
depositado['total_depositos_publico'] = depositos.iloc[:,11].values
depositado['total_depositos_privado'] = depositos.iloc[:,18].values
depositado['M2'] = depositos.iloc[:,-2].values

monetaria = pd.DataFrame.join(monetaria,depositado[['cta_ctes_publico','cta_ctes_privado']],how='outer').sort_index().fillna(method='ffill')
monetaria['M1_circulante_y_ctasctespublicas'] = monetaria['circulante'] + monetaria['cta_ctes_publico']
monetaria = pd.DataFrame.join(monetaria,depositado[['caja_ahorro','plazos_tres','total_depositos_publico','total_depositos_privado','M2']],how='outer').sort_index().fillna(method='ffill')
monetaria = monetaria[~monetaria.index.duplicated(keep='first')]

monetaria['M3'] = (monetaria['M2'] + monetaria['billete_publico'] + monetaria['billete_privado'] + monetaria['total_depositos_privado']) / monetaria['stock_reservas']
monetaria['Dolarizar'] = (monetaria['M2'] + monetaria['billete_publico'] + monetaria['billete_privado'] + monetaria['total_depositos_privado'] + monetaria['leliqs']) / monetaria['stock_reservas']
monetaria = pd.DataFrame.join(monetaria,reservorio['tc_oficial'],how='outer').sort_index().fillna(method='ffill')
monetaria['solidario'] = monetaria['tc_oficial'] * 1.30 * 1.35
aapl = yahoo.download("AAPL AAPL.BA",start='2020-01-01',interval="1d")['Adj Close'].fillna(method="ffill")

aapl = aapl.rename(columns={'AAPL.BA':'AAPLBA'})
aapl['Cable Apple'] = (aapl.AAPLBA / aapl.AAPL) * 10
aapl.index = pd.to_datetime(aapl.index)
aapl.index = aapl.index.tz_localize(None)

monetaria = pd.DataFrame.join(monetaria, aapl['Cable Apple'],how='outer').sort_index().fillna(method='ffill')
monetaria = monetaria.fillna(method='ffill')
monetaria['FX Fundamental'] = (monetaria['pases'] + monetaria['leliqs'] + monetaria['legar'] + monetaria['total_base']) / monetaria['stock_reservas']
monetaria['Monetarista Blue'] = monetaria['solidario'] * (1 + (-monetaria['total_base'].pct_change().cumsum() + monetaria['Cable Apple'].pct_change().cumsum()))
monetaria['Brecha'] = (monetaria['Cable Apple'] / monetaria['tc_oficial']) - 1.0
monetaria = monetaria.fillna(method='ffill')
monetaria = round(monetaria,4)

# translate columns to english
'''monetaria = monetaria.rename(columns={'billete_publico':'public_coin','billete_privado':'private_coin','circulante':'supply',\
                                      'cta_cte_bcra':'bcra_current_account','pases':'bank_passes','stock_reservas':'reserves_stock',\
                                          'cta_ctes_publico':'public_current_accounts','cta_ctes_privado':'private_current_accounts','M1_circulante_y_ctasctespublicas':'M1',\
                                              'caja_ahorro':'saving_accounts','plazo_tres':'fixed_term','total_depositos_publico':'total_public_deposits','total_depositos_privado':'total_private_deposits',\
                                                  'M2':'M2','M3':'M3','tc_oficial':'Official_Exchange_Rate','solidario':'SOLIDARITY','FX Fundamental':'Fundamental Forex','Monetarista Blue':'Monetary Vision',\
                                                      'Brecha':'GAP'})
'''
monetaria = pd.DataFrame.join(monetaria,bonos,how='outer').sort_index().fillna(method='ffill')

toplot = monetaria.iloc[:,-8:].copy()
del toplot['Brecha']

precios = [' $'+ str(round(i,2)) for i in toplot.iloc[-1,:].to_list()]
columnas = [toplot.columns[i] + precios[i] for i in range(len(precios))]
toplot.columns = columnas

# Final plots
fig = plt.figure(figsize=(25,12))
ax1 = fig.add_subplot(111)
toplot.plot(ax=ax1, lw=3.)
ax1.set_title('Argentina Forex', fontsize=60, fontweight='bold')
ax1.grid(linewidth=2)
ax1.legend(fontsize=30)
plt.xticks(size = 20)
plt.yticks(size = 20)
plt.savefig('ArgentinaFX.png',dpi=50)

# Final plots
#fecha = (str(0) + str(dt.date.today().month)) if dt.date.today().month < 10 else str(dt.date.today().month)
fecha = str(dt.date.today() - dt.timedelta(265))
fig = plt.figure(figsize=(25,12))
ax1 = fig.add_subplot(111)
toplot.loc[f'{fecha}':].plot(ax=ax1, lw=3.)
ax1.set_title('Argentina Forex', fontsize=60, fontweight='bold')
ax1.grid(linewidth=2)
ax1.legend(fontsize=30)
plt.xticks(size = 20)
plt.yticks(size = 20)
plt.savefig('year.png',dpi=50)


figb = plt.figure(figsize=(25,12))
ax1 = figb.add_subplot(111)
monetaria['Brecha'].plot(ax=ax1, lw=2.)
ax1.set_title('GAP CCL AAPLBA vs. Official', fontsize=40, fontweight='bold')
ax1.grid(linewidth=2)
ax1.legend(fontsize=20)
plt.xticks(size = 30)
plt.yticks(size = 30)
plt.savefig('gap.png',dpi=50)

# save the excel
writer = pd.ExcelWriter(f'Central Bank Report {today}.xlsx',engine='xlsxwriter')
monetaria.to_excel(writer,sheet_name=f'report {today}',index=True)
writer.close()
